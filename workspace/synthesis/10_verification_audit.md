# Verification audit — every paper claim re-derived from raw data

Second-pass audit. Every number in `workspace/paper/veremi_audit.tex` was re-derived
from the raw archives by scripts that do **not** import the original loader, and every
metric was recomputed with a scikit-learn-free implementation.

Scripts live in `workspace/verify/`. Each is standalone and prints what it measured.

| Script | What it settles |
|---|---|
| `v1_raw_structure.py` | first raw pass (superseded by v1b; kept because it found the label defect) |
| `v1b_raw_refined.py` | ground-truth file census, per archive |
| `v2_metrics.py` | ROC-AUC and AP without sklearn, self-tested against sklearn and scipy |
| `v3_pseudomap.py` / `v3b_pseudomap_full.py` | recovers the raw pseudonym behind each hashed token |
| `v3c_identity_census.py` | identity counts per vehicle from receiver logs, labelled |
| `v4_timing_distributions.py` | the timing shortcut as a distribution, with intervals |
| `v5_pathloss_replicate.py` | physical-layer result, refitted correctly |

---

## A. Claims that survived

### A1. Pseudonyms encode the sender identity

Confirmed, and now measured over whole archives instead of a sample.
Two different rates matter and the paper conflated them.

| Archive | distinct (sender, pseudonym) pairs | encoding, per pair | encoding, per message |
|---|---|---|---|
| GridSybil dense | 8 840 | 86.50 % | 83.40 % |
| GridSybil sparse | 3 726 | 87.01 % | 88.05 % |
| DataReplaySybil dense | 72 140 | 100 % | 100 % |
| DataReplaySybil sparse | 27 421 | 100 % | 100 % |
| DoSRandomSybil dense | 112 191 | 100 % | 100 % |
| DoSRandomSybil sparse | 47 473 | 100 % | 100 % |
| DoSDisruptiveSybil dense | 112 187 | 100 % | 100 % |
| DoSDisruptiveSybil sparse | 47 466 | 100 % | 100 % |

The paper's "87.1 % over 497 pairs" was a sample. The full-archive figure is 86.5–87.0 %.
Claim holds; the table is replaced with the complete one.

### A2. Attacker prevalence is 30 %

Confirmed exactly, in all eight archives, from filename labels over the full member list.

| Archive | attacker vehicles | vehicles | prevalence |
|---|---|---|---|
| GridSybil dense | 1 219 | 4 064 | 30.00 % |
| GridSybil sparse | 507 | 1 688 | 30.04 % |
| DataReplaySybil dense | 1 221 | 4 067 | 30.02 % |
| DataReplaySybil sparse | 507 | 1 688 | 30.04 % |
| DoSRandomSybil dense | 1 221 | 4 067 | 30.02 % |
| DoSRandomSybil sparse | 507 | 1 688 | 30.04 % |
| DoSDisruptiveSybil dense | 1 221 | 4 067 | 30.02 % |
| DoSDisruptiveSybil sparse | 507 | 1 688 | 30.04 % |

The paper quoted "301/1004, 667/2221, 554/1847, 206/685", which were partial counts.
Replaced.

**Identity-level prevalence is a different and larger number**, and the paper never gave it:
67.6 %, 68.3 %, 96.1 %, 95.7 %, 97.5 %, 97.5 %, 97.5 %, 97.5 %. Most identities in six of
eight archives are attacker identities. Any per-identity classifier therefore trains on a
majority-attacker population.

### A3. Attack intensity spans two orders of magnitude

Confirmed and sharpened, from receiver logs.

| Family | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| GridSybil dense | 1 | 3 | 3 | 7 | 7 |
| GridSybil sparse | 1 | 3 | 6 | 7 | 7 |
| DataReplaySybil dense | 1 | 34 | 56 | 83 | 100 |
| DataReplaySybil sparse | 1 | 28 | 50 | 73 | 100 |
| DoSRandomSybil | 1 | 97–98 | 100 | 100 | 100 |
| DoSDisruptiveSybil | 1 | 97–98 | 100 | 100 | 100 |

The paper said "two to seven" for GridSybil. The true minimum is one, not two.

### A4. One scalar solves six of eight archives

Confirmed, and now with a released script (`exp1b_rate_baseline.py`) that did not exist
before, plus bootstrap intervals and an a-priori direction rather than a fitted one.

---

## B. Claims that needed correcting

### B1. The benign-rotation argument used invalid evidence

The paper argued that benign vehicles never rotate pseudonyms from one ground-truth file:
1 847 senders, 1 847 pseudonyms, strictly one to one.

That inference does not hold. The ground-truth files list **one pseudonym per vehicle for
attackers too**, in seven of the eight archives. For DoSRandomSybil dense the ground-truth
file reports 4 068 identities while the receiver logs show 112 191. The 1:1 mapping is a
property of ground-truth logging, not of benign behaviour.

**The conclusion survives on better evidence.** Receiver logs, labelled from filenames:

| Archive | benign vehicles | benign identities | max per benign vehicle | benign with >1 |
|---|---|---|---|---|
| all eight | 1 181–2 846 | equal to vehicle count | **1** | **0** |

Not one benign vehicle in any archive emits a second pseudonym. Claim confirmed; argument replaced.

### B2. Ground-truth files under-report the Sybil population

New. Worth stating in its own right, because label pipelines read those files.

| Archive | identities in ground truth | identities in receiver logs | ratio |
|---|---|---|---|
| GridSybil dense | 7 606 | 7 648 | 1.0x |
| GridSybil sparse | 1 689 | 3 243 | 1.9x |
| DataReplaySybil dense | 4 068 | 72 140 | 17.7x |
| DoSRandomSybil dense | 4 068 | 112 191 | 27.6x |
| DoSDisruptiveSybil sparse | 1 689 | 47 466 | 28.1x |

Anyone deriving the Sybil partition from `traceGroundTruthJSON` alone finds no Sybils at all
in six archives. Our loader reads receiver logs, so our own results are unaffected.

### B3. A degenerate pseudonym value

New. In both GridSybil archives one pseudonym is shared by several senders, and its value is
the literal integer `1`. It carries 147 672 ground-truth messages in the dense archive, 19 %
of that file. This is the whole reason GridSybil encoding falls short of 100 %. Any pipeline
keying on `senderPseudo` silently merges those vehicles into a single identity.

### B4. Duplication factor

The paper says the median duplication factor is 6.4 copies. Measured per archive it is not a
single number, and 6.4 is not one of the values.

| Archive | receiver records | unique transmissions | median copies | mean copies |
|---|---|---|---|---|
| dense archives | 3.8–5.5 M | 0.51–0.75 M | 6–7 | 7.34–7.44 |
| sparse archives | 1.0–1.5 M | 0.21–0.32 M | 4 | 4.71–4.72 |

Corrected to a range with the method stated: copies are counted per `(window, messageID)`
across all receiver logs in the archive.

### B5. Two wrong numbers in the ablation table

Against `exp1_results.csv`:

* DoSRandomSybil geometry-only AUC is 0.748–0.829, not 0.701–0.829.
* DoSDisruptiveSybil timing-only AUC is 1.000 for both densities, not 0.999–1.000.

### B6. Density labels were inverted in the figure

`0709` is the 07:00–09:00 window and holds 4 064–4 068 vehicles. `1416` holds 1 688–1 691.
The figure labelled `0709` "low" and `1416` "high". Corrected to dense and sparse.

### B7. The timing mechanism was described as something the code does not compute

The paper states that sibling identities have "Δt mod 0.5" with median 7e-6. The implemented
feature is `|median(Δt mod 1.0) − 0.5|`. The underlying fact is real but is stated wrongly:
sibling identities interleave at almost exactly **half a beacon period**, so their nearest
send-time offset is 0.5 s to within about 1e-5 s. Rewritten to match the measurement.

---

## C. Defects found in our own experiments

### C1. The leakage test did not contain the leak (serious)

`exp7_leakage_quantified.py` built its "naive" arm's pseudonym feature like this:

```python
pseudo_num = v.groupby("sender")["token"].first().map(lambda t: int(t[:8], 16) % 10**7)
```

`token` is already a salted BLAKE2b hash. Hashing destroys the sender encoding, so the
feature was a random integer and carried no leakage whatsoever. The negative result —
"naive protocols do not inflate AUC" — was therefore obtained against a straw man.

Fixed by recovering the real pseudonyms (`v3b_pseudomap_full.py`) and rerunning the
comparison as a staged cascade (`exp9_cascade.py`). See section D.

### C2. Path loss was fitted on attacker links

`position_verification_features` fits the log-distance model over every link. Attacker links
carry falsified coordinates, so their claimed distances are wrong by construction and bias
the slope. The paper claims the fit uses benign links only. `v5_pathloss_replicate.py`
reports both fits.

### C3. Single-feature AUCs were orientation-selected

`exp8`/`exp8b` report `max(a, 1 - a)` per feature. That chooses each feature's sign using
the test labels and cannot fall below 0.5 even for pure noise. No number in the paper comes
from that line, so no published figure changes, but the diagnostic printout was misleading
during development. Replaced with a-priori directions and signed values, which top out at
0.539 (`resid_mean`) rather than the selected values.

The paper's 0.597 for raw signal statistics is a forest score, not a selected single feature,
and is unaffected.

### C4. A reported table had no script

`exp1b_rate_baseline.csv` backs the paper's single-scalar table, and no script produced it.
Rewritten as `exp1b_rate_baseline.py`. The AUCs reproduce to within 0.001–0.005; the
identity counts do not, because the original counted a subset.

---

### B8. The phase mechanism is family-dependent

Measured per family (`v4_timing_distributions.py`), sibling identities do not all
sit half a beacon period apart. The denial-of-service families do, to within
$3\times10^{-6}$. GridSybil attackers hold three identities and sit one third of a
period apart, giving 0.1667 on the same statistic. The offset is the beacon period
divided by the identity count. The paper's single universal figure is replaced by
the per-family measurement.

### B9. Jitter was credited with a drop it did not cause

An early reading of the cascade attributed a 0.059 AUC drop to transmission jitter.
That drop sits inside a seed spread of 0.13, because the stage runs at 3 % prevalence
where the test fold holds about six attackers. Measured at native prevalence, where
the spread is 0.007, jitter costs 0.011 on the per-identity task. On the pairwise
task it is decisive: phase AUC falls from 0.88 to 0.57. Both numbers are now reported
in the places they apply.

### B10. The archives cannot be evaluated below 3 % prevalence

New, and a limit on any work using this data. Subsampling attackers to 2 % or less
leaves a vehicle-disjoint test fold with fewer than five attacker vehicles, so the
run is degenerate. The two sparse archives are already degenerate at 3 %. This is a
property of the archives, not of our splitter.

---

## E. Independent reproduction of the physical-layer result

`v5_pathloss_replicate.py` rebuilds the result from the 2018 archive without reusing
the original feature code path. The propagation measurements reproduce exactly.

| Quantity | Paper (first pass) | Replication |
|---|---|---|
| Links | 86 919 | 86 919 |
| Slope, dB/decade | −9.3 | −9.29 |
| Path-loss exponent | 0.93 | 0.929 |
| Correlation with log d | −0.64 | −0.633 |

### E1. The point estimate sat outside its own interval

The first pass reported AUC 0.534 with a bootstrap interval of [0.517, 0.532]. A
reviewer caught that the estimate lies outside its own interval, which cannot happen
if both describe the same quantity. They did not.

* **0.534** was the mean of five per-split AUCs.
* **[0.517, 0.532]** was a bootstrap over those five test sets *concatenated*.

Each split trained its own forest, and each forest scores on its own scale. Pooling
five such score vectors does not produce a coherent ranking, so the pooled AUC is a
different and lower quantity than the mean of the five. Printing one beside the other
was the error.

### E2. The fix, and what it revealed

`GroupKFold` now partitions senders into five folds, so every link is scored exactly
once by a model that never saw its sender. Two estimators are reported, each with the
interval for that same estimator, and the script asserts containment before writing.

| Estimator | All links | Benign fit |
|---|---|---|
| AUC, mean across folds | 0.530 [0.507, 0.553] | 0.524 [0.502, 0.547] |
| AUC, pooled out of fold | 0.499 [0.491, 0.507] | 0.493 [0.485, 0.501] |
| Average precision | 0.054 | 0.054 |

The fold-mean, 0.530, is close to the 0.534 originally reported, so the conclusion is
unchanged. The pooled out-of-fold value is more interesting: **0.499, with an interval
that contains 0.5**. Ranking within a fold is weak; ranking every link on one global
scale is indistinguishable from chance. A deployed detector needs the second, not the
first, which strengthens rather than weakens the section's claim.

Refitting on benign links only moves the exponent from 0.929 to 0.941 and the fold-mean
AUC from 0.530 to 0.524. The C2 defect is therefore real but immaterial.

### E3. The same defect elsewhere

`exp9_cascade.py` reports `auc` as a mean over five seeds while `auc_boot_lo/hi` is a
bootstrap on seed 0 alone. No paper table displays those columns, and no containment
violation occurs in the data, but the column names implied a pairing that does not
hold. They are renamed to say which split they describe.

## F. Metric implementations

`v2_metrics.py` implements ROC-AUC as a mid-rank Mann-Whitney statistic and average
precision as the step-wise sum, with no scikit-learn. Self-tested over 200 random
trials including constant scores and heavily tied scores, which is where naive
implementations diverge.

```
max |ours - sklearn| AUC : 2.220e-16
max |ours - sklearn| AP  : 1.110e-16
max |ours - scipy MWU|   : 0.000e+00
```

Every experiment now scores with both and aborts on any disagreement above 1e-9.

---

## D. What replaced the negative result

See `11_cascade_result.md`.
