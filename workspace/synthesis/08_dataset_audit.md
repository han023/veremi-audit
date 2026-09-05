# Dataset Audit — what the VeReMi-family Sybil benchmarks actually contain

**Status: original measurements, produced in this analysis.** Everything below was computed directly from the
md5-verified archives in `workspace/datasets/`. Scripts are inline in the session; each finding states the
exact file and the counts, so it is reproducible.

**Why this matters:** VeReMi and VeReMi Extension are the de-facto benchmarks for VANET misbehaviour
detection (Extension: 215 citations; 136 works since 2024). Papers report 94–99.9 % detection on them.
Four structural properties measured here suggest a substantial part of that performance is a property of the
*datasets*, not of the detectors. Verification found **no prior work reporting any of this**: probes for
identifier/label leakage in VANET datasets return **0 works**, and for VeReMi + pseudonym-change /
unlinkability **0 works**. No paper in the 92-paper corpus even mentions the `senderPseudo` field.

---

## Finding 1 — Pseudonyms encode the true sender identity (87–100 % of records)

Every received message (`type: 3`) carries `sender` (true vehicle, ground truth) and `senderPseudo` (what a
receiver would actually see). The pseudonym is **constructed from the sender id**:

| Archive | (sender, pseudonym) pairs | pseudonyms containing the sender's digits | examples |
|---|---|---|---|
| GridSybil_1416 | 497 | 433 (**87.1 %**) | 15 → 10155, 20155 · 21 → 10215 · 27 → 10275 |
| DoSDisruptiveSybil_0709 | 7 806 | 7 806 (**100 %**) | 10623 → 10106232 · 10659 → 10106592 |
| DataReplaySybil_0709 | 3 474 | 3 474 (**100 %**) | 15 → 20152, 30152, 40152, 50152 |
| DoSRandomSybil_1416 | 5 923 | 5 923 (**100 %**) | 5853 → 1058535, 2058535, 3058535 |

The construction is roughly `k·10ⁿ + sender·10 + suffix`. Consequences:

1. **The Sybil grouping task is solvable by string arithmetic.** Deciding "do these pseudonyms belong to one
   vehicle?" — the core of Sybil detection — can be answered from the identifier alone, with no kinematics.
2. **Any model given `senderPseudo` as a numeric feature can learn a shortcut.** Tree ensembles in particular
   will split on digit ranges.
3. **The subtler and more common trap: per-vehicle aggregation keyed on `sender`.** Several published
   pipelines build per-node movement matrices/eigenvalues and then classify the node. If the grouping key is
   `sender`, the model is handed the identity partition that a real receiver must *infer* — the hardest part
   of the problem is assumed away. (Azam 2022, the most-cited recent ML paper on this data, aggregates
   "movement pattern of the mobile nodes" per node before PCA/eigenvalue extraction.)

**Recommended control:** re-run any VeReMi-based result with (a) pseudonyms randomly re-mapped to
identity-free tokens, and (b) all aggregation keyed on `senderPseudo` only. The delta is the leakage.

## Finding 2 — Benign vehicles never change pseudonyms

Ground truth for `DataReplaySybil_0709`: **189 402 messages, 1 847 distinct senders, 1 847 distinct
pseudonyms — a strict 1:1 mapping, 0 senders with more than one pseudonym.** Median pseudonym usage span is
99 s, which is simply how long a vehicle is present in the window.

So the dataset contains **no pseudonym-change events for honest vehicles**. Therefore:
- Unlinkability, pseudonym lifetime, mix-zones and tracking-resistance **cannot be studied on this data as
  shipped** — the entire privacy axis of V2X is absent from the benchmark the community uses.
- Attackers, by contrast, *do* hold many identities (Finding 4), so "number of pseudonyms per vehicle" is
  itself a perfect label if ground-truth identity is available.
- A study of the privacy/detection trade-off must **layer a synthetic pseudonym-change policy** over the
  benign traces (split each benign vehicle's trace at a chosen lifetime and re-key it). This is legitimate —
  pseudonym-change policy is a layer above mobility — and it turns the missing feature into a controlled,
  sweepable parameter.

## Finding 3 (CORRECTED) — RSSI and identity are disjoint across the benchmark family

An earlier draft of this audit said "the VeReMi family has no RSSI". That was wrong, and the correction is a
stronger finding. Measured field sets:

| Dataset | received power | pseudonyms | Sybil-specific attack families |
|---|---|---|---|
| **VeReMi (2018)** | **`RSSI` present and populated** — real values, 1.3e-9 … 2.6e-5 W (median 9.4e-9) | **no** — `sender` only | **no** (position-falsification types A1…A16) |
| **VeReMi Extension (2020)** | **absent** | yes (`senderPseudo`, but ID-leaking — Finding 1) | yes (GridSybil, DataReplaySybil, DoSRandomSybil, DoSDisruptiveSybil) |
| **Preprocessed VeReMi CSV (2025)** | absent | **no identity column at all** | labels only (Finding 8) |

**No public dataset offers signal strength, identity, and Sybil labels at the same time.** RSSI-based Sybil
detection — the single largest family in the literature (33 of 92 corpus papers) — therefore has *no* dataset
that supports it end to end. You can benchmark RSSI methods on VeReMi 2018 (which has no Sybil attacks) or
identity methods on the Extension (which has no RSSI), never both. This is the precise, defensible version of
the "no RSSI substrate" complaint, and it is the strongest single motivation for a new dataset.

## Finding 4 — Attacker density is ~30 %, an order of magnitude above realistic

Attacker share of receiver logs (from the `A<n>` filename labels):

| Archive | attack id | attacker logs / total | share |
|---|---|---|---|
| GridSybil_1416 | A16 | 301 / 1 004 | 30.0 % |
| DoSDisruptiveSybil_0709 | A19 | 667 / 2 221 | 30.0 % |
| DataReplaySybil_0709 | A17 | 554 / 1 847 | 30.0 % |
| DoSRandomSybil_1416 | A18 | 206 / 685 | 30.1 % |

For comparison, Söderhäll & Papadimitratos (2025) show that Sybils at **3 % of participants already raise
average travel time by 20 %** — i.e. the realistic, damaging regime is ten times sparser than the benchmark's.
Detection at 30 % attacker prevalence is a much easier statistical problem (abundant positives, dense
corroboration) than detection at 1–3 %. Reported accuracies are therefore not transferable to deployment,
and **class-prevalence sensitivity is never reported** in the corpus.

## Finding 5 — Attack intensity varies enormously between families

Identities per attacker, observed from receiver logs (min / median / max):

| Archive | identities per attacker |
|---|---|
| GridSybil_1416 | 2 / 3 / 7 |
| DataReplaySybil_0709 | 3 / 39 / 100 |
| DoSRandomSybil_1416 | 5 / 100 / 100 |
| DoSDisruptiveSybil_0709 | 6 / 100 / 100 |

A detector tuned on 100-identity floods will look excellent and say nothing about the 2–7-identity case,
which is the stealthy and realistic one. **Papers rarely state which family they evaluate on** — and, per
`06_gap_verification.md` §4.1, only 9 of 92 state the attacker fraction at all.

## Finding 6 — Sybil trajectories are individually plausible (a correction)

An initial aggregate measurement suggested all identities of an attacker shared one position (spread 0 m).
**That was my measurement bug**, not a property of the data. Record-level inspection of GridSybil
(receiver `traceJSON-9-7-A0-50404-14.json`, attacker `sender 15`) shows the attacker alternating pseudonyms
every 0.5 s, each with a **distinct, smoothly evolving trajectory** roughly 250 m apart:

```
 rcvTime  senderPseudo     pos_x     pos_y    spd_x   spd_y
50404.62         10155   1370.89   1273.31     0.75   -1.69
50405.12         20155   1323.75   1023.23    -0.90   -1.48
50405.62         10155   1372.01   1270.61     1.60   -3.61
50406.12         20155   1322.21   1020.31    -1.02   -1.65
```

So the kinematic task is genuinely non-trivial: ghosts have believable motion. The triviality comes from the
*identifier*, not the physics — which is exactly why Finding 1 matters.

## Finding 7 — Integrity: one archive was silently corrupt

`DataReplaySybil_1416.zip` matched its manifest size exactly but failed CRC and MD5
(`81b9dbe6697e…` vs Zenodo's `ab049e792479…`). Size checks are insufficient; the pipeline now verifies Zenodo
MD5 (`workspace/verify_datasets.py`) and the fetcher re-downloads mismatches automatically.

---

## What follows from this audit

| Finding | Consequence for the field | Consequence for our plan |
|---|---|---|
| 1. Identifier leakage | Published VeReMi results may be inflated by an unreported shortcut | A leakage-controlled re-evaluation is a paper in itself |
| 2. No pseudonym change | The privacy axis is absent from the standard benchmark | The linkability study needs a synthetic pseudonym-change layer — cheap, and it becomes the swept parameter |
| 3. RSSI ⟂ identity | RSSI-based Sybil detection has no end-to-end dataset; the two benchmarks are complementary but disjoint | RSSI methods → VeReMi 2018; identity methods → Extension; both → regenerate |
| 4. 30 % attackers | Results do not transfer to the 1–3 % regime that matters | Prevalence sweeps must be part of any evaluation |
| 5. Family variance | "Sybil detection" numbers are not comparable across papers | Always report per-family, and include the 2–7-identity case |
| 6. Plausible ghost motion | The kinematic problem is real | Kinematic linkage remains a meaningful detector |
| 7. Silent corruption | Anyone re-downloading may be working on bad data | MD5 verification is now standard in the pipeline |


## Finding 8 — The ready-to-use preprocessed derivative cannot express the task, and its grouping column is malformed

`balanced_veremi_dataset.csv` (Zenodo 14903687, 760 MB, CC-BY, 2.27 M rows) is the most convenient public
VeReMi derivative — the fastest path from download to classifier, and therefore the one most likely to be
used uncritically. Measured properties:

- **19 columns, none of them an identity**: `rcvTime, pos_{0,1}, pos_noise_{0,1}, spd_{0,1}, spd_noise_{0,1},
  acl_{0,1}, acl_noise_{0,1}, hed_{0,1}, hed_noise_{0,1}, ReceiverID, AttackerType`. There is no `sender` and
  no `senderPseudo`. **Sybil detection is therefore impossible in principle on this file** — you cannot detect
  "one vehicle claiming many identities" from rows that contain no identity. A model trained here performs
  single-message plausibility classification and is often reported as Sybil detection.
- **`ReceiverID` is malformed**: 30 095 distinct values over 600 k sampled rows, but two of them
  (`Receiver_3`: 490 708 rows; `Receiver_2`: 79 199 rows) hold 95 % of the data and span 19 attack types,
  while the other 30 093 hold **exactly one row each** and map to exactly one attack type. Consequences:
  group-aware (receiver-disjoint) cross-validation **degenerates** — in our run the test fold contained no
  Sybil rows at all (accuracy 1.000, F1 0.000, AUC undefined) — so grouped validation silently fails, and
  random splits mix rows freely.
- **Labels are 20 perfectly balanced classes** (~30 k each: 4 Sybil families, 15 other attacks, Benign),
  which corresponds to no deployment prevalence whatsoever (compare Finding 4's 30 %, and the realistic 1–3 %).

### Empirical anchor (our measurement)

Binary Sybil-family vs everything else, single-message kinematics only, RandomForest (60 trees), 600 k rows:

| Setup | accuracy | F1 | ROC-AUC |
|---|---|---|---|
| all features, random split | 0.874 | 0.548 | 0.860 |
| without `rcvTime`, random split | 0.870 | 0.532 | 0.846 |
| receiver-disjoint split | *degenerate — no positives in test fold* | | |

Per-family recall (no `rcvTime`, random split): GridSybil **0.510**, DoSDisruptiveSybil **0.440**,
DataReplaySybil **0.301**, DoSRandomSybil **0.228**; benign false-positive rate **0.000**.

**Interpretation.** Identity-free, per-message kinematics recovers Sybil families at recall 0.23–0.51 — far
below the 94–99.9 % routinely reported. Either published results use information this file does not contain
(i.e. identity, via `sender`-keyed aggregation — Finding 1), or they evaluate a different, easier task. Both
readings are damaging, and both are testable with the controls proposed in this audit.

## Finding 9 (REVISED after self-audit) — Sybil identities are separable by transmission timing, not by physics

> **Correction notice.** The first version of this finding reported timing-only AUC ≈ 1.0 across all eight
> archives from an experiment containing **two bugs**. Both are described below, because the way they inflated
> the result is itself instructive. The corrected numbers preserve the qualitative conclusion but change the
> magnitudes, remove one family entirely, and reveal a simpler mechanism.

### The two bugs

**Bug 1 — duplicate observations.** Every transmitted BSM is logged separately by each receiver that heard it
(measured: median **6.4** copies per `messageID`, max 31). Grouping a token's rows across receivers collapses
its inter-arrival gaps to ~1e-7 s and inflates every pairwise timing feature. Fix: `analysis.transmissions()`
deduplicates on `messageID` before any sender-level reasoning.

**Bug 2 — one-sided group split.** Pairs were grouped for splitting by the vehicle of endpoint `a` only, so
the vehicle behind endpoint `b` could straddle train and test. Fix: split *vehicles* first, then keep only
pairs whose **both** endpoints fall on the same side.

The tell that something was wrong: no single feature exceeded AUC 0.65, yet a 200-tree forest on four of
those same features reported AUC 1.000. That gap is only explicable by leakage, and it was.

### Corrected results

Pairwise identity linkage, deduplicated transmissions, strict vehicle-disjoint splits, RandomForest(200).
`workspace/sybilbench/exp1_results.csv`.

| Archive | pairs | pos. rate | AUC all | **AUC geometry** | **AUC timing** | AP geometry |
|---|---|---|---|---|---|---|
| GridSybil_0709 | 25 971 | 0.027 | 0.994 | **0.979** | 0.996 | 0.884 |
| GridSybil_1416 | 29 218 | 0.060 | 0.998 | **0.966** | 1.000 | 0.855 |
| DataReplaySybil_0709 | — | — | *no positive pairs survive* | | | |
| DataReplaySybil_1416 | — | — | *no positive pairs survive* | | | |
| DoSRandomSybil_0709 | 1 717 | 0.058 | 1.000 | **0.748** | 1.000 | 0.286 |
| DoSRandomSybil_1416 | 1 847 | 0.097 | 1.000 | **0.829** | 1.000 | 0.696 |
| DoSDisruptiveSybil_0709 | 1 588 | 0.064 | 1.000 | **0.716** | 1.000 | 0.523 |
| DoSDisruptiveSybil_1416 | 1 733 | 0.105 | 1.000 | **0.632** | 1.000 | 0.441 |

Seed stability (5 seeds): DoSDisruptiveSybil_0709 all = 1.0000 ± 0.0000, timing = 1.0000 ± 0.0000,
geometry = 0.776 ± 0.054; GridSybil_1416 all = 0.996 ± 0.002, geometry = 0.976 ± 0.008.

### The mechanism, measured directly

The attacker cycles its identities on a fixed round-robin, so any two identities of one attacker are separated
by an exact multiple of 0.5 s:

| pair type | median `dt` | median `dt mod 0.5 s` | fraction with `dt mod 0.5 < 0.01` |
|---|---|---|---|
| same vehicle (Sybil siblings) | 0.5000 | **0.000007** | **54.5 %** |
| different vehicles | 0.4892 | 0.280 | 1.3 % |

The identities are **phase-locked**. That is a property of the attacker implementation, not of Sybil attacks.

### What survives, and what changed

- **Survives:** timing separates Sybil siblings near-perfectly on the DoS families (AUC 1.000 ± 0.000), while
  geometry — the physically meaningful signal — is much weaker (0.63–0.83).
- **Survives:** GridSybil is the one genuinely geometric family (geometry AUC 0.976 ± 0.008, AP 0.86–0.88).
- **Changed:** DataReplaySybil **drops out**: after deduplication it yields *no* concurrent identity pairs at
  all. Its Sybil identities are used **sequentially**, not simultaneously — so pairwise concurrent linkage is
  the wrong primitive for it. The earlier "AUC 1.000 on DataReplay" was entirely the duplicate-observation bug.
- **Changed:** geometry-only numbers rose slightly (0.70→0.75, 0.63 stays low) once the split was tightened,
  and the DoS pair counts fell 3× because duplicates had been inflating them.
- **Unchanged conclusion:** a headline number on these archives can be obtained without physical evidence, and
  a real attacker removes the signal by jittering transmission times at no cost to attack utility.

## Finding 10 — Six of eight archives are solved by one scalar, with no linkage and no ML

Deduplicated per-identity statistics, evaluated directly as a classifier (no training):

| Archive | benign interval | attacker interval | **AUC, median interval alone** | **AUC, message count alone** |
|---|---|---|---|---|
| GridSybil_0709 | 1.0 s | 1.0 s | 0.658 | 0.631 |
| GridSybil_1416 | 1.0 s | 1.0 s | 0.575 | 0.603 |
| DataReplaySybil_0709 | 1.0 s | 1.0 s | 0.503 | **0.995** |
| DataReplaySybil_1416 | 1.0 s | 1.0 s | 0.501 | **0.994** |
| DoSRandomSybil_0709 | 1.0 s | **50.0 s** | **1.000** | 0.998 |
| DoSRandomSybil_1416 | 1.0 s | **50.0 s** | **1.000** | 0.998 |
| DoSDisruptiveSybil_0709 | 1.0 s | **50.0 s** | **1.000** | 0.998 |
| DoSDisruptiveSybil_1416 | 1.0 s | **50.0 s** | **1.000** | 0.998 |

Benign identities beacon at exactly 1 Hz. In the DoS families the attacker spreads a fixed transmit budget
over ~100 identities, so each ghost transmits once per 50 s — **a 50× rate difference that separates the
classes perfectly with a single number**. In DataReplaySybil the interval matches benign, but ghosts are
short-lived, so raw message count reaches AUC 0.994. Only GridSybil resists both (0.58–0.66).

**Implication.** Any detector reported on the DoS or DataReplay families must be compared against this
one-scalar baseline; without that comparison, a 99 % result demonstrates nothing. GridSybil is the only
family in the Sybil set where the benchmark poses a non-trivial problem.

## Finding 11 (REVISED after second self-audit) — Privacy and detection move together; whether short pseudonym lifetimes are a net loss depends on detector strength

> **Correction notice.** The first version of this finding claimed a clean "knee at 30–60 s" where the
> privacy/security exchange rate flips. Auditing that experiment found **three biases**, and the corrected
> result is weaker and more conditional. The exchange-rate flip is real only against a *strong* detector.

### Three biases found in the first attempt

| # | Bias | Size |
|---|---|---|
| **B1** | **Population drift.** At τ = 120 s only 36 % of benign vehicles re-key at all, and those that do are 47 % longer-lived (median 148.5 s vs 101 s at τ = 15 s). Longer-lived vehicles are easier to track, so the trend could have been composition rather than policy. | +0.018 AUC |
| **B2** | **Test-set feature selection.** Detection reported the best of five features in both directions, chosen on the data it scored. | **+0.232 AUC** |
| **B3** | **Succession leaking into detection.** Under "all vehicles re-key", an attacker's own ghost is re-keyed too, so its consecutive epochs form a *sequential* positive pair — a tracking signal scored as detection. | removed by an overlap filter |

Controls applied: a **fixed cohort** of 169 benign vehicles with presence ≥ 130 s (so every cohort vehicle
re-keys at every τ, holding the population constant); **no feature selection**; **concurrency required** for
detection pairs; gap-matched negatives for tracking; geometry-only features; 3 seeds.

### Corrected result (GridSybil_1416)

Tracking is scored **parameter-free** (one a-priori feature, `miss` = dead-reckoning error, direction fixed,
no fitting) because after cohort restriction and gap-matching only ~50 positives remain — too few to train and
split. Detection is scored with a **trained model under vehicle-disjoint splits** because it has 13–19× more
positives. The asymmetry is deliberate and conservative for the privacy claim: a *parameter-free* attacker is
a lower bound on what a real adversary achieves.

| τ | tracking AUC (privacy loss) | positives | detection AUC (security) | positives |
|---|---|---|---|---|
| 15 s | 0.825 ± 0.023 | 52 | 0.913 ± 0.007 | 651 |
| 30 s | 0.850 ± 0.023 | 45 | 0.947 ± 0.026 | 821 |
| 60 s | 0.884 ± 0.020 | 55 | 0.954 ± 0.009 | 857 |
| 120 s | 0.988 ± 0.004 | 50 | 0.974 ± 0.007 | 970 |

**What survives:** both curves rise monotonically with τ — **Pearson r = 0.879**. Every setting that makes
drivers harder to follow makes Sybils harder to catch. The dilemma is real and now measured under controls.

**What survives, and matters most:** **tracking AUC never falls below 0.825.** Even re-keying every 15 s, a
*parameter-free* attacker — extrapolate last position by last velocity, measure the miss distance — follows
vehicles across pseudonym changes. Pseudonym rotation alone does not deliver unlinkability at any lifetime
tested.

### The knee is conditional, not universal

Marginal privacy gained per unit detection lost:

| τ segment | vs **trained** detector | vs **single-feature** detector |
|---|---|---|
| 120 → 60 s | 5.41× | 4.15× |
| 60 → 30 s | 4.46× | 1.10× |
| 30 → 15 s | **0.75×** (net loss) | 3.11× (still favourable) |

So the earlier "flip below 30 s" claim is **only true against a capable detector**. A strong detector loses a
lot of accuracy below 30 s (0.947 → 0.913), making the trade uneconomic; a weak detector has little left to
lose, so shortening remains cheap. **Pseudonym-lifetime policy therefore cannot be set independently of the
detector deployed alongside it** — which is a sharper and more useful statement than a fixed knee.

### Limitations

- One family (GridSybil), one density: the DoS families offer no concurrent geometry worth measuring
  (Finding 9) and DataReplay yields no concurrent pairs at all.
- The tracking head is **underpowered** (~50 positives). A trained tracking model could not be estimated
  reliably: with vehicle-disjoint splits it returned NaN at τ = 120 s and a single valid seed at τ = 30 s.
  Reported tracking numbers are therefore parameter-free lower bounds, not best-case attacks.
- Fixed-clock re-keying only. Real policies re-key in mix zones, silent periods or density triggers, all of
  which should push the privacy side up. Measuring those is the next step.

### Methodological note

Two rounds of self-audit overturned two headline claims (Finding 9's mechanism and magnitudes; Finding 11's
knee). Both times the tell was the same: **a result too strong for the amount of signal in the features.**
No single feature exceeded AUC 0.65 while a forest reported 1.000 (Finding 9); a trend held across τ while the
population under measurement changed by 47 % (Finding 11). Any headline in this space should be re-derived
under a fixed cohort, a-priori features, and disjoint splits before it is believed.

## Finding 12 — The coupling is mediated by evidence per identity, not by pseudonym policy as such

Third self-audit. Finding 11 showed tracking and detection AUC both rising with pseudonym lifetime τ
(r = 0.879). The obvious alternative explanation was never tested: **τ also controls how many messages
accumulate under each identity**, and more observations make *any* linkage easier. If that is the mechanism,
the "trade-off" is an information-quantity effect wearing a privacy-policy label.

### Messages per identity are set by τ

| τ | benign msgs/identity (median) | attacker msgs/identity | identities in window |
|---|---|---|---|
| 15 s | 15 | 14 | 11 097 |
| 30 s | 29 | 24 | 6 135 |
| 60 s | 48 | 35 | 3 577 |
| 120 s | 63 | 52 | 2 249 |

### Holding τ fixed and varying evidence directly

τ fixed at 30 s; every identity truncated to its first N messages; both heads re-scored:

| N msgs/identity | tracking AUC | detection AUC |
|---|---|---|
| 5 | 0.747 | 0.578 |
| 10 | 0.779 | 0.639 |
| 20 | 0.811 | 0.674 |
| 40 | 0.832 | 0.680 |
| all | 0.829 | 0.686 |

**Both heads rise with evidence per identity at constant τ** — tracking +0.082, detection +0.108 from N = 5 to
N = 40. Comparable in size to the movement attributed to τ in Finding 11 (tracking +0.163 across the whole
τ range, of which roughly half is accounted for here).

### What this means

1. **The dilemma is real but its mechanism is generic.** Pseudonym lifetime matters because it rations the
   evidence collected under one identity, and that same evidence serves the tracking attack and the Sybil
   detector equally. The coupling is not a quirk of these traces; it follows from both tasks consuming the
   same input.
2. **It is a stronger statement than the original.** Any policy that reduces evidence per identity — shorter
   lifetimes, silence periods, mix zones, transmission suppression — should degrade detection by a comparable
   amount. That is a falsifiable prediction, and the natural next experiment.
3. **It fixes the reporting standard.** Comparisons should be made at **matched messages-per-identity**, not
   at matched τ. Two schemes evaluated at different pseudonym lifetimes are, silently, evaluated at different
   evidence budgets — which is the same class of error as comparing detectors across different attacker
   prevalences (Finding 4) or different attack families (Finding 5).

### Status of Finding 11 after this check

- **Unchanged:** both curves move together; tracking AUC never falls below 0.825; the exchange rate depends
  on detector strength.
- **Reinterpreted:** τ is not acting through "unlinkability" in any privacy-theoretic sense; it acts through
  observation count. Claims of the form "shorter pseudonym lifetime protects drivers" should be restated as
  "less evidence per identity protects drivers — and equally protects attackers".

## Finding 13 — Silence decouples the dilemma; shortening pseudonym lifetime does not

Finding 12 says the privacy/security coupling runs through *evidence accumulated per identity*. That predicts
a way out: a policy that removes **continuity between** identities without removing **evidence within** one
should cost tracking but not detection — because concurrent (Sybil) linkage never needed the continuity.

Silence periods are exactly that policy, and the prediction holds.

### First attempt failed, and the failure was informative

Naively dropping the first S seconds of each new identity reduced messages per identity from 26 to 18, and
both heads fell together (tracking −0.030, detection −0.019 at S = 10 s) — precisely Finding 12's prediction
for an evidence cut. The test was confounded, not the theory.

### Evidence-matched test

Silence S paired with τ_effective = 30 + S, holding messages per identity at 25–26. Five seeds:

| policy | tracking AUC | detection AUC |
|---|---|---|
| no silence (τ = 30 s) | 0.8072 ± 0.0077 | 0.6828 ± 0.0125 |
| silence 20 s (τ_eff = 50 s) | **0.7661 ± 0.0046** | 0.6909 ± 0.0078 |
| **difference** | **−0.0411 (se 0.0040) — significant** | +0.0080 (se 0.0066) — not significant |

Tracking falls by ten standard errors; detection does not move.

### Why this matters

- **Shortening pseudonym lifetime is the wrong lever.** It rations evidence, so it degrades detection roughly
  as much as it protects drivers (Finding 11: exchange rate 0.75× against a trained detector below 30 s).
- **Silence is the right lever.** It breaks the hand-over an attacker needs to follow a vehicle, while leaving
  intact the concurrent co-observation a Sybil detector needs. Privacy is bought at no measurable security
  cost.
- This is a concrete, testable design recommendation, and it explains why the pseudonym-privacy literature
  converged on mix zones and silent periods rather than on ever-shorter lifetimes — but here the reason is
  *measured*, and measured jointly with the detection side that literature does not evaluate.

### Honest magnitude

Silence helps; it does not solve. Tracking AUC falls only from 0.807 to 0.766 — a parameter-free attacker
still follows vehicles across a 20 s silence. Combined with Finding 11 (tracking never below 0.825 across
every τ tested without silence), the overall picture is that **kinematic linkability in this mobility regime is
hard to defeat by pseudonym scheduling alone**, whichever lever is pulled.

### Limitations

Single family and density (GridSybil_1416); silence modelled as a transmission gap, not as a mix zone with
spatial cloaking; detection scored with a single a-priori feature for comparability across policies (the
trained detector sits ~0.27 AUC higher, Finding 11), so the *absolute* detection level here is a floor, not an
estimate of the best achievable.

## Finding 14 — Replication at a second density: two of three findings hold, the third is confounded

Everything above was measured on `GridSybil_1416`. Re-running the identical protocol on `GridSybil_0709`
(sparser traffic; cohort 179 benign vehicles vs 169) tests whether these are properties of the problem or of
one simulation window.

### A. The Pareto replicates (Finding 11) ✓

| τ | tracking (1416) | tracking (0709) | detection (1416)* | detection (0709)* |
|---|---|---|---|---|
| 15 s | 0.825 | **0.865** | 0.667 | **0.639** |
| 30 s | 0.850 | **0.893** | 0.675 | **0.677** |
| 60 s | 0.884 | **0.904** | 0.706 | **0.708** |
| 120 s | 0.988 | **0.994** | 0.731 | **0.747** |

\* single-feature detector, so comparable across both columns.

Both curves rise monotonically with τ at both densities. Tracking is *higher* at the sparser density
(0.865 vs 0.825 at τ = 15 s), which is the expected direction: fewer candidate vehicles means less ambiguity
when matching a re-keyed identity. The headline stands — **tracking AUC never falls below 0.825 at either
density**, and the two heads move together.

### B. The evidence mechanism replicates (Finding 12) ✓

τ fixed at 30 s, identities truncated to N messages:

| N | tracking (1416) | tracking (0709) | detection (1416) | detection (0709) |
|---|---|---|---|---|
| 5 | 0.747 | 0.757 | 0.578 | 0.588 |
| 10 | 0.779 | 0.772 | 0.639 | 0.661 |
| 20 | 0.811 | 0.819 | 0.674 | 0.699 |
| 40 | 0.832 | 0.838 | 0.680 | 0.683 |

Near-identical at both densities (tracking +0.080 vs +0.082; detection +0.095 vs +0.108 from N = 5 to 40).
Evidence per identity, not density, drives both heads.

### C. The silence result does NOT replicate cleanly (Finding 13) ✗ — and the reason is a residual confound

| | tracking Δ | detection Δ |
|---|---|---|
| GridSybil_1416 | **−0.0411** (se 0.0040, significant) | +0.0080 (se 0.0066, n.s.) |
| GridSybil_0709 | **−0.0150** (se ≈ 0.0044, significant but 2.7× smaller) | **+0.0325** (se ≈ 0.0085, significant *increase*) |

The privacy benefit survives but shrinks; the "no detection cost" claim does not.

**The confound I missed.** To hold benign evidence constant, silence S was paired with τ_eff = 30 + S. But the
policy applies to attackers too, so their identities also live 50 s instead of 30 s — **more evidence per
ghost, which makes Sybil detection easier**. Detection therefore has two opposing pressures: silence removes
continuity (no effect on concurrent linkage) while the longer τ_eff adds evidence (helps detection). At the
dense window these roughly cancelled (+0.008, n.s.); at the sparse window the evidence effect dominates
(+0.033).

So Finding 13's mechanism claim is intact — silence does not *itself* cost detection — but the experiment as
run cannot demonstrate "free privacy", because the evidence-matching device changes attacker identity lifetime
as a side effect. The clean test needs silence applied at **fixed τ for everyone**, with the benign evidence
difference accepted and reported rather than compensated. That is the next experiment.

### Status summary

| Finding | Claim | Replication |
|---|---|---|
| 11 | Privacy and detection move together with τ; tracking never below 0.825 | ✓ holds at both densities |
| 12 | Coupling is mediated by evidence per identity | ✓ near-identical at both densities |
| 13 | Silence buys privacy at no detection cost | ✗ privacy benefit shrinks 2.7×; "no cost" is confounded by τ_eff |

## Finding 15 — Silence is not free in deployment: every privacy lever also arms the attacker

Finding 14 showed the evidence-matched silence test was confounded (τ_eff = 30 + S gives attackers
longer-lived identities). The clean deployment question is different: apply silence **at fixed τ for
everyone** and accept — and report — the evidence it removes.

τ = 30 s for all vehicles, silence S added on top, 5 seeds, both densities:

| density | S | msgs/identity | tracking AUC | detection AUC | Δ tracking | Δ detection | exchange |
|---|---|---|---|---|---|---|---|
| 1416 | 0 s | 26 | 0.807 ± 0.008 | 0.675 ± 0.007 | — | — | — |
| 1416 | 10 s | 18 | 0.774 ± 0.006 | 0.659 ± 0.008 | −0.033 | −0.016 | 2.06× |
| 1416 | 20 s | **9** | 0.747 ± 0.008 | 0.617 ± 0.012 | −0.060 | −0.058 | **1.04×** |
| 0709 | 0 s | 25 | 0.808 ± 0.004 | 0.681 ± 0.009 | — | — | — |
| 0709 | 10 s | 18 | 0.776 ± 0.004 | 0.672 ± 0.008 | −0.032 | −0.009 | 3.51× |
| 0709 | 20 s | **9** | 0.759 ± 0.015 | 0.652 ± 0.006 | −0.049 | −0.029 | 1.71× |

Silence consumes airtime, so messages per identity collapse from ~26 to **9** at S = 20 s — and by Finding 12,
that cuts both heads. At the dense window the exchange rate falls to **1.04×**: privacy and security are
given up in equal measure, no better than shortening τ.

### The three-way tension

Putting Findings 12–15 together, a pseudonym policy cannot simultaneously:

1. hold **benign** evidence per identity constant,
2. hold **attacker** evidence per identity constant, and
3. add silence (or otherwise break continuity),

because the policy applies to everyone. Compensating for silence by lengthening τ (Finding 13's design)
satisfies (1) and (3) but violates (2) — it hands each Sybil ghost a longer life and *raises* detection at the
sparse density (+0.033). Applying silence at fixed τ satisfies (2) and (3) but violates (1) — evidence
collapses for benign vehicles and detection falls with it.

**This is the deep form of the linkability dilemma.** It is not that privacy and detection happen to be
correlated in these traces; it is that every lever a pseudonym scheme can pull is an *evidence* lever, and
evidence is exactly what both the tracker and the detector consume. A defence that rations evidence rations
it for both sides.

### What would escape it

Only an asymmetric mechanism — one that removes evidence for the tracker while preserving it for the
detector. Candidates worth testing: infrastructure-side detection where the RSU sees what individual vehicles
cannot (Footprint's premise); cryptographic concurrency proofs that need no behavioural evidence at all
(the SCMS/certificate-concurrency direction, `04_research_questions.md` RQ7); or detection at aggregate rather
than identity level. None is tested here, and each is a paper.

### Status of the experimental programme

| Finding | Claim | Evidence |
|---|---|---|
| 9 | Sybil identities separable by transmission timing, not physics | 8 archives; corrected after 2 bugs |
| 10 | 6 of 8 archives solved by one scalar (rate/count), no ML | AUC 1.000 / 0.994 |
| 11 | Privacy and detection move together with τ; tracking never < 0.825 | r = 0.879; replicated at 2 densities |
| 12 | Coupling is mediated by evidence per identity | replicated, near-identical at 2 densities |
| 13 | Continuity gap alone does not cost detection | holds mechanistically; confounded as a policy claim |
| 14 | Replication: 11 ✓, 12 ✓, 13 ✗ | GridSybil_0709 |
| 15 | Silence is not free in deployment; exchange → 1.04× | 2 densities, 5 seeds |

## Finding 16 — Infrastructure vantage does not escape the dilemma; it is another evidence accumulator

Finding 15 left one escape route: an **asymmetric mechanism** that grants detection power without granting
equal tracking power. Roadside units are the classic candidate (Footprint's premise). VeReMi has no RSUs, so
one is emulated — a static observer receiving every transmission whose claimed position falls within 300 m,
for the whole window, sited at the busiest 300 m cells. Three vantages, identical traces, τ = 30 s, 3 seeds:

| density | vantage | msgs/identity | tracking AUC | detection AUC |
|---|---|---|---|---|
| 1416 | one vehicle (n=36) | 12.3 | 0.614 | 0.581 |
| 1416 | one RSU (n=12) | 28.6 | **0.799** | **0.689** |
| 1416 | pooled global | 26.0 | 0.808 | 0.703 |
| 0709 | one vehicle (n=36) | 8.5 | 0.790 | 0.673 |
| 0709 | one RSU (n=15) | 14.6 | **0.807** | **0.718** |
| 0709 | pooled global | 25.0 | 0.811 | 0.699 |

### The RSU improves both heads

| density | Δ tracking (rsu − vehicle) | Δ detection | evidence gain | **detection gain / tracking gain** |
|---|---|---|---|---|
| 1416 | +0.185 (z = 15.5) | +0.108 (z = 7.8) | 2.3× | **0.58** — tracking favoured |
| 0709 | +0.017 (z = 1.2, n.s.) | +0.045 (z = 6.7) | 1.7× | **2.72** — detection favoured |

**The direction of the imbalance flips between densities**, so there is no stable asymmetry. What is stable is
that the RSU sees 1.7–2.3× more messages per identity than a vehicle does, and *both* heads rise with it —
exactly Finding 12's prediction. An RSU is not a different kind of observer; it is a better-placed one.

### Secondary observations

- **A single vehicle is a weak observer**, and how weak depends on density: 0.614/0.581 at the dense window
  against 0.790/0.673 at the sparse one. Dense traffic gives a vehicle more neighbours but far more ambiguity.
- **One well-placed RSU ≈ the pooled omniscient view** (0.799/0.689 vs 0.808/0.703 at 1416; 0.807/0.718 vs
  0.811/0.699 at 0709). Infrastructure buys most of what global observation would.
- Both readings support deploying RSUs for detection — they just also hand an observer the same tracking power,
  which is the point.

### Verdict on the escape route

Infrastructure is **not** an escape from the linkability dilemma. Of the three candidates named in Finding 15,
one is now tested and closed. The remaining two are untested and both avoid behavioural evidence entirely:
cryptographic concurrency proofs (RQ7 / SCMS certificate linkage) and aggregate-level detection that never
resolves individual identities.

### Method note — a bug this run exposed

The script wrote a fixed output filename, so invoking it once per archive **silently overwrote** the first
archive's rows; only the log preserved them. Fixed to per-archive filenames
(`exp6_rsu_vantage_<archive>.csv`) and the 1416 run repeated. Two earlier bugs in this experiment are recorded
in `EXP6_STATUS.md`: a candidate sampler that emptied the positive class at RSU scale, and a first comparison
that pitted a *pooled global* view against a single RSU rather than one observer against one observer.

## Finding 17 (NEGATIVE) — The documented shortcuts do not, by themselves, inflate AUC

Findings 1 and 4 establish that the archives contain identifier leakage and unrealistic prevalence.
The natural next claim — *"and that is why published numbers are so high"* — was tested directly and
**is not supported**.

One pipeline, two protocols, 8 archives, 3 seeds (`exp7_leakage_quantified.py`):

- **naive**: features aggregated on the ground-truth `sender` key, raw pseudonym offered as a numeric feature,
  random k-fold CV, native ~30 % attacker prevalence — reconstructed from common practice in the corpus.
- **controlled**: aggregation on observable identity only, hashed tokens, vehicle-disjoint splits, prevalence
  subsampled to 3 %.

Rate and count features are dropped from **both** arms, because Finding 10 shows they alone solve six of
eight archives; leaving them in means both arms ride the same shortcut and the comparison measures nothing.

| archive | naive AUC | controlled AUC | AUC inflation |
|---|---|---|---|
| GridSybil_0709 | 0.936 | 0.795 | **+0.142** |
| GridSybil_1416 | 0.787 | 0.885 | −0.098 |
| DataReplaySybil_0709 | 0.922 | 0.973 | −0.051 |
| DataReplaySybil_1416 | 0.817 | 0.950 | −0.134 |
| DoSRandomSybil_0709 | 1.000 | 0.999 | +0.001 |
| DoSRandomSybil_1416 | 0.999 | 0.997 | +0.002 |
| DoSDisruptiveSybil_0709 | 0.976 | 0.919 | +0.057 |
| DoSDisruptiveSybil_1416 | 0.916 | 0.931 | −0.015 |
| **mean** | | | **−0.012** |

**Mean AUC inflation is −0.012** — the controlled protocol is, on average, very slightly *better*. Only one
archive shows a substantial gap in the predicted direction (GridSybil_0709, +0.142); two show a substantial
gap in the opposite direction.

### Average precision moves, but the comparison is invalid

Mean AP inflation is +0.143, reaching +0.35 to +0.44 on three archives. That difference is **dominated by a
confound**: AP depends on class prevalence, and the controlled arm deliberately sets prevalence to 3 % against
the naive arm's 30 %. A lower AP at lower prevalence is arithmetic, not evidence of leakage. Reporting the AP
gap as "inflation" would be exactly the kind of unmatched comparison this project criticises elsewhere
(Findings 4, 12), so it is not claimed.

### What this means for the argument

The audit's supported claim is **"the benchmark is trivially solvable"**, not **"published protocols inflate
results"**:

- **Strongly supported** — Finding 10: a single scalar (per-identity message interval or count) reaches
  AUC 1.000 / 0.994 on six of eight archives, with no training and no linkage. Finding 9: timing separates
  Sybil siblings at AUC ≈ 1.0 while geometry reaches only 0.63–0.83 on the DoS families.
- **Not supported** — that the specific naive protocol adds much *on top of* that easiness. Once the trivial
  rate shortcut is removed from both arms, ground-truth aggregation and the pseudonym feature buy little
  in AUC terms.

That distinction matters for how Paper A is written. The problem with these benchmarks is that the task itself
is too easy, not that researchers are exploiting a subtle protocol loophole. A paper claiming the latter would
overreach; the evidence supports the former, and it is the more damaging finding anyway.

### Isolating identity leakage properly

The clean experiment holds prevalence fixed and varies only one factor at a time (aggregation key; pseudonym
feature present/absent; random vs vehicle-disjoint split). Not run. Given the mean AUC result above, the
expected effect is small.

## Finding 18 — VeReMi 2018's RSSI is too weakly distance-dependent to support RSS position verification

Finding 3 established that VeReMi 2018 is the only public set carrying received power, so the physical-layer
detector family — 33 of the 92 corpus papers — can only be exercised there. This tests whether it actually can.

### The RSSI is only weakly informative about distance

Fitting a log-distance path-loss model on **benign** links (claimed position = true position, so distance is
honest), 20 archives, 141 608 receptions:

| quantity | measured | reference |
|---|---|---|
| corr(RSSI, log₁₀ d) | **−0.64** | — |
| slope | **−9.3 dB/decade** | free space −20; urban −30 to −40 |
| implied path-loss exponent | **n ≈ 0.93** | free space n = 2, urban n = 3–4 |
| per-link scatter | 3.6–8.5 dB sd | — |

Mean RSSI by distance is monotone out to ~800 m (−31.5, −40.6, −45.6, −51.6, −52.0, −54.2 dBm) but the decay
is far shallower than physics. With ~9 dB of signal per decade of distance against 4–8 dB of per-link scatter,
a *tenfold* position lie produces a residual comparable to the noise floor.

### Consequence: the classic detector does not work here

RSS-based position verification (Xiao 2006, Bouassida 2007) implemented properly — receiver placed from its
own type-2 GPS fixes, claimed distance computed, residual against the fitted path-loss model summarised per
link, sender-disjoint splits, 5 seeds, 86 919 links with 5.5 % attacker prevalence:

**AUC = 0.534 ± 0.012, AP = 0.055.** Single features: residual mean 0.530, residual sd 0.537, residual max
0.538 — all near chance. Raw RSSI statistics without the position comparison do no better (AUC 0.597).

The attack under test is `ConstantPosition`, the most blatant position lie in the dataset. If the canonical
physical-layer method cannot detect *that* here, the substrate cannot validate the family.

### Corrected conclusion for Finding 3

The situation is worse than "RSSI and Sybil labels live in different datasets". It is:

1. VeReMi Extension has Sybil families but **no RSSI**;
2. VeReMi 2018 has RSSI but **no Sybil families**; and
3. the RSSI it does have is **too weakly distance-dependent to run the classic RSS method at all**.

So the largest detector family in this literature has **no public dataset on which it can be validated** —
which makes the calibrated-dataset paper (RQ8) the highest-value artefact contribution in the programme,
not merely a convenience.

### Method note — a bug found and fixed mid-experiment

VeReMi 2018 is 225 independent simulation runs, and **vehicle ids are reused across them** (measured: 95 of
102 receiver ids appear in more than one archive). The first implementation grouped on `receiver` alone,
matching receptions in one simulation against GPS fixes from another. Effect of the fix:

| | grouped on `receiver` | grouped on `(archive, receiver)` |
|---|---|---|
| corr(RSSI, log d) | −0.28 | **−0.64** |
| slope | −3.7 dB/decade | **−9.3 dB/decade** |
| distance bins | non-monotone (RSSI *rose* beyond 800 m) | monotone to 800 m |

The tell was physical implausibility: received power increasing with distance. Detection AUC was 0.554 before
the fix and 0.534 after — the conclusion is unchanged, but the earlier number was reached for the wrong reason.
