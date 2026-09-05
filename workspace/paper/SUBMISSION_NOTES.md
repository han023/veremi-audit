# Submission notes — `veremi_audit.tex`

**Hannan Muzammil**, Hannsoft — <https://www.hannsoft.org/> — abdullhannan0311@gmail.com

Eleven pages, IEEEtran conference class, 37 references. Zero overfull boxes, zero
TeX errors, no `% TODO` markers.

The eleventh page is about 25 % full. It grew when the detector specification and
feature table were added, which a reviewer had every right to demand.

## Target venue

Checked 6 September 2026. Full detail in `workspace/SUBMISSION_GUIDE.md`.

**Submit to IEEE T-ITS.** It is the only strong venue open today, it already
publishes this literature, and the length fits. Both conference options closed
their 2026 cycles.

| Venue | Status | Length rule |
|---|---|---|
| **IEEE T-ITS** | **open, rolling** | ~10 pages, up to 6 more at $175 each |
| ACM WiSec 2027 | cycle 1 expected ~Nov 2026 | 10 pages excl. bibliography, 12 total |
| USENIX VehicleSec '27 | CFP not yet posted | shorter; would need real cuts |
| IEEE TIFS | open, rolling | wants a defence, not only an audit |

Two earlier statements in these notes were wrong and are corrected here.

**VehicleSec is not an NDSS event any more.** It moved to USENIX, and VehicleSec '26
ran 10–11 August 2026 in Baltimore. Any instruction to use `\documentclass{ndss}`
is obsolete; use the USENIX template if you target VehicleSec '27.

**ACM WiSec 2026 is closed.** Cycle 1 closed 18 November 2025, cycle 2 on 3 March
2026. WiSec stated its deadlines were firm with no extensions.

For T-ITS the class change is small, because the source is already IEEEtran:

```latex
\documentclass[conference]{IEEEtran}   % becomes
\documentclass[journal]{IEEEtran}
```

Recompile and re-run all three checkers afterwards. A reflow can move a float
without changing a number, and only the checkers will tell you which happened.

**If the venue is double-blind** (WiSec, VehicleSec), remove the author block *and*
the artefact DOI from Availability: the DOI resolves to a record carrying your name.
T-ITS is single-blind, so neither applies.

## Constraints applied

- **Sentence length:** every sentence is 12 words or fewer.
  636 checked, 0 over. Re-run `check_sentences.py` after any edit.
- **Reference mix:** 37 references, 26 established and 11 recent (2024+).
  That is 70 / 30, at the edge of the requested 70–80 / 20–30 split.
  Adding any further recent citation breaks it; add an established one alongside.
- **Originality:** all prose is written from our own measurements.
  Every number traces to a CSV, and `assemble.py` emits the tables from those CSVs
  rather than from typed values.

## Verification

Three checkers, all passing, all runnable from the project root.

| Script | Checks | Status |
|---|---|---|
| `check_sentences.py` | 12-word limit across the body | 636 sentences, 0 over |
| `check_refs.py` | reference mix, uncited entries, undefined citations | 37 refs, 30 % recent, clean |
| `check_claims.py` | every hand-typed number against its CSV | 292 claims, 0 failed |

`check_claims.py` also verifies Tables III, IV, V, VII and VIII cell by cell
against their source files, asserts that every reported point estimate lies inside
the interval printed beside it, checks that every float is referenced at least once,
scans for a bare percent sign that would comment out a line, scans for a value
slot left holding a period,
and confirms the cited dataset records and licences against the metadata captured
at download time.

## Claims and their evidence

| Paper claim | Source file |
|---|---|
| Census: prevalence, identities, encoding, duplication | `verify/v3c_identity_census.csv`, `verify/v3b_pseudomap.csv` |
| Ground truth lists up to 28x fewer identities | `verify/v1b_raw_refined.csv` vs `verify/v3b_pseudomap.csv` |
| Pseudonym `1` shared across senders, 147 672 messages | `verify/v1b_raw_refined.csv` |
| No benign rotation in the eight Sybil archives | `verify/v3c_identity_census.csv` |
| Single scalar, AUC 1.000 / 0.996 | `sybilbench/exp1b_rate_baseline_v2.csv` |
| Timing vs geometry ablation, Fig. 1 | `sybilbench/exp1_results.csv` |
| Phase offsets, jitter effect, significance | `verify/v4_timing_distributions.csv` |
| Cascade, ground-truth key associated with 0.060 | `sybilbench/exp9_cascade.csv` |
| Sensitivity sweeps | `sybilbench/exp10_sensitivity.csv` |
| Prevalence floor, 3 % dense and 5 % sparse | `verify/v6_prevalence_floor.csv` |
| Path loss, exponent 0.93, AUC 0.530 / 0.499 | `verify/v5_pathloss.csv` |
| No pseudonym rotation, and the test for it | `verify/v10_pseudonym_change.csv` |
| Detector, feature sets, linkage pair counts | `sybilbench/exp1_linkage.py`, `exp9_cascade.py` |
| Corpus reporting table | `verify/v11_reporting_table.csv` |
| Pseudonym decoding, 0.876 vs 0.003 | `sybilbench/exp13_pseudonym_decode.csv` |
| NextGen replication | `verify/v15_nextgen_shortcuts.csv` |
| NextGen identifier AUC 1.000 | `verify/v16_nextgen_identifier.csv` |
| Full census, 8 archives x 55 columns | `verify/v17_master_census.csv` |
| Single-factor add-back, order-free | `sybilbench/exp14_single_factor.csv` |
| Attacker rate 2 Hz, ghost gap 50 s | `verify/v21_attacker_budget.csv` |
| Index size, year span, ns-2 count | `verify/v12_corpus_facts.csv` |
| Extension citation count | `verify/v13_citation_counts.json` |

Full reproduction path: `workspace/REPRODUCE.md`.
The artefact self-tests: `python workspace/make_release.py --selftest`
unpacks it clean and runs the checkers inside it (271 of 277 checks; the
six skipped need the source archives, which are not redistributed).
Environment and file hashes: `workspace/MANIFEST.md`.

## What is deliberately not claimed

- **That the benchmark is trivial.** It substantially simplifies the deployment
  task, and GridSybil retains a genuinely harder residual problem.
- **That the VeReMi Extension lacks pseudonym change in general.** The claim is
  scoped to the eight Sybil archives examined. F2MD supports pseudonym change
  policies; they are simply not exercised in these archives, and `v10` tests the
  alternative explanation rather than assuming it away.
- **That a cascade increment is an independent causal effect.** Stages are nested,
  so a single-factor add-back measures each advantage against one fixed baseline
  instead. Both designs rank ground-truth aggregation first, which is what makes
  that conclusion order-independent. Where they differ, we name it as interaction.
- **That jitter caused the cascade's late drop.** It sits inside the seed spread.
  The jitter effect is reported where it was measured with a stable estimate.
- **That any author exploited a loophole.** The protocols we reconstruct were
  reasonable when written, and we say so.
- **That we are the first to test anything.** Priority claims are unprovable; we
  describe what we did instead, and every absence claim names our search.
- **That the attacker shares the benign transmit budget.** It does not: these
  families run at about 2 Hz, twice benign, which is what makes the ghost gap 50 s
  rather than 100 s. The relation is $N/R$, measured, not assumed.
- **That mutual information between pseudonym and sender is informative.** A unique
  identifier determines its owner, so that quantity is degenerate. We report
  $I(D;S)$ for a decoder that can be wrong instead.
- **That a citation count is stable.** The one count we give carries the month
  it was read, from a provenance record rather than memory.
- **That the ground-truth files contain fewer attackers.** They contain the same
  attacker vehicles. What they omit is the pseudonyms those attackers emitted.
- **That the average-precision gap shows inflation.** It is a prevalence artefact.
- **That RSSI methods are bad.** Only that no public data can validate them.
- **That realistic prevalence is reachable or unreachable.** We report the lowest
  stable evaluable prevalence, 3 % dense and 5 % sparse, and say nothing about
  what is realistic.
- **That the 3 % figure is a measured deployment prevalence.** It is the level at
  which measured impact already appears. Neither 3 % nor 30 % is a field figure.

Keeping these disclaimers is what makes the paper defensible under review.

## Corrections made during the audit

Recorded in full in `synthesis/10_verification_audit.md`. The load-bearing ones:

1. **The leakage test contained no leak.** Its pseudonym feature was derived from
   the salted hash, which had already destroyed the sender encoding. Replaced by
   the cascade with recovered raw pseudonyms. The invalid result is described as
   invalid in §VII-A rather than quietly dropped.
2. **The benign-rotation claim rested on invalid evidence.** The ground-truth file
   lists one pseudonym per vehicle for attackers too. Re-argued from receiver logs.
3. **A point estimate sat outside its own confidence interval.** The physical-layer
   AUC was a mean over five splits; the interval was a bootstrap over those splits
   pooled. Two different quantities. Replaced with `GroupKFold`, which yields one
   ranking with one matching interval, and the script now asserts containment.
4. Path loss was fitted on attacker links while the text said benign only.
5. Two wrong numbers in the ablation table.
6. Density labels were inverted in the figure.
7. The duplication factor 6.4 matched no measured archive.
8. A reported table had no script. Written as `exp1b_rate_baseline.py`.
9. A partial run overwrote the cascade CSV, reproducing defect 5 on this list. Restored from the release archive, and output
   filenames now carry the model and whether the run was complete.

### What the estimator fix revealed

Correcting defect 3 did not weaken the section. Fold-mean AUC is 0.530, close to the
0.534 first reported. But the pooled out-of-fold ranking, which is what a deployed
detector with one threshold actually needs, reaches **0.499 with an interval
containing 0.5**. Chance.

## Bibliography verification

Every entry was checked against its DOI registration record, not against our own
corpus scrape, which itself carried two of the errors. Sources: Crossref, dblp for
USENIX Security and the International Journal of Network Security, Zenodo for the
dataset record.

Twelve entries were wrong and are now fixed:

| Entry | Defect |
|---|---|
| `kamel2020` | **credited three people who are not authors** of VeReMi Extension |
| `sixpack2021` | author list was a TODO placeholder |
| `tits2025survey` | author list was a TODO placeholder; title was also short |
| `khatri2024` | author order wrong |
| `morton2024` | wrong middle initial, wrong year (2025, not 2024) |
| `soderhall2025` | second author missing |
| `akil2023`, `almazroi2024`, `hadri2026`, `sefati2025` | truncated to "et al." |
| `nextgen2026` | no authors; now cites the VNC 2026 paper |
| `ayaida2019` | fourth surname misspelled |

`kamel2020` was the serious one. VeReMi Extension is the dataset this paper audits,
so citing it with the wrong authors would have been the worst error in the document.

## Ethics statement

The paper carries one, which WiSec and VehicleSec both expect. It states that no
human subjects or personal data are involved, that naming papers in Table I locates
protocol choices rather than alleging misconduct, and that we take no position on
the authorship dispute affecting the Istanbul dataset. We never obtained that data,
and the claim checker verifies its absence from the tree.

## Before submitting

1. Swap in the venue class file and check the page limit.
2. Deposit the code and add the artefact URL to the Availability section.
3. Regenerate `MANIFEST.md` after the final code freeze.
4. Re-run all three checkers after any edit.
