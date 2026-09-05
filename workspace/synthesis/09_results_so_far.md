# Results So Far — paper-ready narrative

Every number here was measured in this project on md5-verified public data. Provenance for each is in
`08_dataset_audit.md` (Findings 1–15) and `workspace/sybilbench/*.csv`. Nothing below is quoted from another
paper unless named.

The material supports **two papers**. They share a codebase and can be written in either order, but Paper A
must exist for Paper B's numbers to be trusted.

---

# Paper A — "What VeReMi Measures: Structural Artefacts in the VANET Misbehaviour Benchmarks"

**Claim.** The benchmark the field trusts is easier than the problem it stands for, and in ways nobody has
reported. Several of its Sybil tasks are solvable without using any physical evidence.

**What the claim is NOT** (Finding 17, a tested negative). The paper does *not* argue that researchers exploit
a subtle protocol loophole. Running one pipeline under a reconstructed "naive" protocol (ground-truth
aggregation key, pseudonym as a feature, random k-fold, 30 % prevalence) against a controlled one gave a mean
AUC inflation of **−0.012** across eight archives — no systematic advantage. The supported claim is the
stronger and simpler one: **the task itself is trivially easy** (Findings 9, 10). Keeping this distinction is
what stops the paper overreaching.

## A1. The corpus cannot check itself (motivation)

From full-text extraction over 92 papers (`06_gap_verification.md` §4.1):

| Reported | Papers |
|---|---|
| Explicit threat/attacker model | 22 / 92 |
| Vehicle count | 34 / 92 |
| Beacon rate | **9 / 92** |
| Attacker fraction | **9 / 92** |
| Simulation area | **6 / 92** |
| ROC/AUC | 5 / 92 |
| Any significance test or CI | **2 / 92** |
| Code mentioned | 4 / 92 |
| Public code reachable today | **0 / 92** |
| Adversarial-ML content | **0 / 92** |

83 of 92 evaluate on private simulations; 11 papers published 2021 or later still use NS-2, whose development
ended in 2011. One corpus paper is retracted; the one public Sybil dataset with realistic RSSI is
owner-restricted amid an authorship dispute.

## A2. Identifier leakage (Finding 1)

Pseudonyms are constructed from the true sender id — `sender 15 → 10155, 20155`; `sender 5853 → 1058535,
2058535`. Share of (sender, pseudonym) pairs whose pseudonym contains the sender's digits:

| GridSybil | DataReplaySybil | DoSRandomSybil | DoSDisruptiveSybil |
|---|---|---|---|
| 87.1 % | 100 % | 100 % | 100 % |

Consequences: the Sybil grouping task is solvable by string arithmetic; any model given `senderPseudo`
numerically can shortcut; and the common practice of aggregating features **per `sender`** hands the model the
identity partition a real receiver must infer.

## A3. The privacy axis is absent (Finding 2)

`DataReplaySybil_0709` ground truth: 189 402 messages, 1 847 senders, **1 847 pseudonyms — strict 1:1**.
Benign vehicles never change pseudonyms, so unlinkability, pseudonym lifetime and tracking resistance cannot
be studied on the benchmark as shipped.

## A4. RSSI and identity are disjoint (Finding 3)

| Dataset | RSSI | identity | Sybil families |
|---|---|---|---|
| VeReMi 2018 | **yes** (1.3e-9 … 2.6e-5 W) | `sender` only | no |
| VeReMi Extension 2020 | no | `senderPseudo` (leaking) | **yes** |
| Preprocessed CSV 2025 | no | **none** | labels only |

**No public dataset carries signal strength, identity and Sybil labels together.** RSSI-based Sybil detection —
33 of 92 corpus papers — has no end-to-end substrate.

**And the RSSI that does exist is not usable (Finding 18).** Fitting path loss on benign links in VeReMi 2018:
corr(RSSI, log d) = **−0.64**, slope **−9.3 dB/decade**, implied exponent **n ≈ 0.93** against free space's 2 —
with 4–8 dB per-link scatter. RSS-based position verification implemented properly (receiver placed from its
own GPS fixes, residual against the fitted model, sender-disjoint splits) reaches **AUC 0.534 ± 0.012** on
`ConstantPosition`, the most blatant position lie in the set. The canonical physical-layer method cannot
detect it. So the largest detector family in the literature has **no public dataset on which it can be
validated at all** — which promotes the calibrated-dataset paper (RQ8) from convenience to necessity.

## A5. Prevalence and intensity are unrealistic (Findings 4–5)

Attacker share is **~30 %** in every archive (301/1004, 667/2221, 554/1847, 206/685) against a realistic
1–3 % — Söderhäll 2025 shows Sybils at 3 % of users already raise average travel time 20 %. Identities per
attacker range 2–7 (GridSybil) to 100 (DoS families), and papers rarely say which family they used.

## A6. The ready-made derivative cannot express the task (Finding 8)

`balanced_veremi_dataset.csv` (760 MB, CC-BY, 2.27 M rows) has **no identity column at all**, so Sybil
detection is impossible on it in principle. Its `ReceiverID` is malformed: two mega-receivers hold 95 % of rows
across 19 attack types while 30 093 "receivers" hold exactly one row each — receiver-disjoint CV therefore
**degenerates silently** (our run: accuracy 1.000, F1 0.000, AUC undefined). Identity-free per-message
kinematics reaches AUC 0.860, per-family recall 0.23–0.51 — far below the 94–99.9 % routinely published.

## A7. Six of eight archives fall to one scalar (Finding 10)

No training, no linkage, one number per identity:

| family | benign interval | attacker interval | AUC (interval) | AUC (msg count) |
|---|---|---|---|---|
| GridSybil | 1.0 s | 1.0 s | 0.58–0.66 | 0.60–0.63 |
| DataReplaySybil | 1.0 s | 1.0 s | 0.50 | **0.994** |
| DoSRandomSybil | 1.0 s | **50.0 s** | **1.000** | 0.998 |
| DoSDisruptiveSybil | 1.0 s | **50.0 s** | **1.000** | 0.998 |

Only GridSybil poses a non-trivial problem.

## A8. Timing, not physics (Finding 9)

Pairwise identity linkage, deduplicated transmissions, vehicle-disjoint splits:

| family | AUC geometry | AUC timing |
|---|---|---|
| GridSybil | 0.966–0.979 | 0.996–1.000 |
| DoSRandomSybil | 0.701–0.829 | 1.000 |
| DoSDisruptiveSybil | 0.632–0.716 | 0.999–1.000 |
| DataReplaySybil | *no concurrent pairs exist* | — |

Mechanism, measured: identities of one attacker are **phase-locked to a 0.5 s round-robin** — `dt mod 0.5 s`
median 7e-6 with 54.5 % under 0.01, versus 0.28 and 1.3 % for different vehicles. A real attacker removes this
by jittering, at no cost to attack utility.

## A9. Deliverables

A patch script producing a de-leaked, prevalence-controlled, pseudonym-change-layered variant; the eight
design rules in `sybilbench/README.md`; the `sybilbench` package; 12 result CSVs.

---

# Paper B — "The Linkability Dilemma: Sybil Detection and Location Privacy Consume the Same Evidence"

**Claim.** Detecting a Sybil and tracking a driver are the same inference. Every lever a pseudonym scheme can
pull is an *evidence* lever, and evidence is what both sides consume — so no policy setting favours one.

## B1. The dilemma, measured (Finding 11, replicated at two densities)

Fixed cohort, gap-matched negatives, geometry only, 3 seeds:

| τ | tracking (1416) | tracking (0709) | detection (1416) | detection (0709) |
|---|---|---|---|---|
| 15 s | 0.825 | 0.865 | 0.913* | 0.639 |
| 30 s | 0.850 | 0.893 | 0.947* | 0.677 |
| 60 s | 0.884 | 0.904 | 0.954* | 0.708 |
| 120 s | 0.988 | 0.994 | 0.974* | 0.747 |

\* trained detector; the 0709 column uses the single-feature detector, so compare columns within a scorer.

Both curves rise monotonically with τ at both densities, **r = 0.879**. **Tracking AUC never falls below
0.825**: even re-keying every 15 s, a *parameter-free* attacker — extrapolate last position by last velocity,
measure the miss distance — follows vehicles across pseudonym changes.

## B2. The mechanism is evidence per identity (Finding 12, replicated)

τ fixed at 30 s, identities truncated to N messages:

| N | tracking (1416 / 0709) | detection (1416 / 0709) |
|---|---|---|
| 5 | 0.747 / 0.757 | 0.578 / 0.588 |
| 10 | 0.779 / 0.772 | 0.639 / 0.661 |
| 20 | 0.811 / 0.819 | 0.674 / 0.699 |
| 40 | 0.832 / 0.838 | 0.680 / 0.683 |

Both heads rise with evidence at constant τ, near-identically at both densities. τ matters because it rations
evidence — the coupling is generic, not a quirk of these traces. **Corollary for the field: compare at matched
messages-per-identity, not matched τ.**

## B3. The exchange rate depends on the detector (Finding 11)

| τ segment | vs trained detector | vs single-feature detector |
|---|---|---|
| 120 → 60 s | 5.41× | 4.15× |
| 60 → 30 s | 4.46× | 1.10× |
| 30 → 15 s | **0.75× (net loss)** | 3.11× |

Pseudonym-lifetime policy cannot be set independently of the detector deployed with it.

## B4. Silence: right lever, not free (Findings 13–15)

*Mechanistically* (evidence held constant, 5 seeds, GridSybil_1416): silence 20 s cuts tracking
**−0.0411 (se 0.0040, significant)** while detection moves **+0.0080 (n.s.)**. The continuity gap costs the
tracker and not the detector — because concurrent linkage never needed continuity.

*In deployment* (τ fixed at 30 s, silence on top), silence consumes airtime and messages per identity collapse
26 → 9:

| density | S | Δ tracking | Δ detection | exchange |
|---|---|---|---|---|
| 1416 | 20 s | −0.060 | −0.058 | **1.04×** |
| 0709 | 20 s | −0.049 | −0.029 | 1.71× |

## B5. The three-way tension (Finding 15) — the paper's thesis

A pseudonym policy cannot simultaneously (1) hold **benign** evidence constant, (2) hold **attacker** evidence
constant, and (3) break continuity — because the policy applies to everyone. Compensating silence with longer
τ satisfies (1) and (3) but violates (2), and *raised* detection +0.033 at the sparse density. Silence at
fixed τ satisfies (2) and (3) but violates (1), and detection fell with the evidence.

**Escape requires an asymmetric mechanism** — one that removes evidence for the tracker while preserving it
for the detector.

## B6. Infrastructure is not the escape (Finding 16)

An emulated RSU (static observer, 300 m radius, whole window) versus a single vehicle, identical traces:

| density | Δ tracking | Δ detection | evidence gain | detection/tracking gain |
|---|---|---|---|---|
| 1416 | +0.185 (z = 15.5) | +0.108 (z = 7.8) | 2.3× | 0.58 — tracking favoured |
| 0709 | +0.017 (n.s.) | +0.045 (z = 6.7) | 1.7× | 2.72 — detection favoured |

The RSU raises **both** heads, and the direction of the imbalance flips between densities — no stable
asymmetry. What is stable is that it sees 1.7–2.3× more messages per identity, exactly Finding 12's
mechanism. One well-placed RSU also nearly matches the pooled omniscient view (0.799/0.689 vs 0.808/0.703).
Infrastructure is a better-placed observer, not a different kind of one.

**Two escape candidates remain untested**, and both avoid behavioural evidence entirely: cryptographic
concurrency proofs (RQ7 / SCMS certificate linkage) and aggregate-level detection that never resolves
individual identities.

---

# Methodological appendix — three self-corrections

Worth its own section; it is the reason the numbers above should be believed.

| # | Bug | Effect | How it was caught |
|---|---|---|---|
| 1 | Attacker labels taken from the parsed subset of receiver files | Benign vehicles appeared with up to 6 identities | Contradicted Finding 2's 1:1 mapping |
| 2 | Duplicate observations — one BSM logged per receiver (median 6.4 copies) | Cadence collapsed to ~1e-7 s; every timing feature inflated; a whole family's result was spurious | **No single feature exceeded AUC 0.65 while a forest reported 1.000** |
| 3 | Population drift, test-set feature selection, succession leaking into detection | +0.018, **+0.232**, and a family-dependent bias | Trend held while the measured population changed 47 % |

The recurring tell: **a result too strong for the amount of signal in the features.** Any headline in this
space should be re-derived under a fixed cohort, a-priori features and disjoint splits before it is believed.

---

# What remains

| Item | Status |
|---|---|
| Experiment 6 — RSU vantage (the asymmetry test) | **done — Finding 16: no escape** |
| Experiment 7 — leakage quantified (Paper A's headline number) | coded, not yet run |
| VeReMi-2018 RSSI loader | coded, not yet smoke-tested |
| Paper A leakage-controlled re-evaluation of 2–3 published detectors | designed, not run |
| Mix zones with spatial cloaking (vs plain silence) | not started |
| GridSybil density replicate of Findings 13/15 at other archives | partially done (0709) |
| RSSI-family benchmark on VeReMi 2018 | unlocked by Finding 3, not started |
