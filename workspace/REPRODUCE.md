# Reproducing every number in the paper

Run from the project root. Each command prints what it measured and writes one CSV.
`workspace/MANIFEST.md` pins the interpreter, library versions and file hashes.

## 0. Get the data

Three Zenodo artefacts, all CC-BY:

| Artefact | DOI | Used for |
|---|---|---|
| VeReMi Extension (Sybil families) | 10.5281/zenodo.20090854 | everything except the physical layer |
| VeReMi 2018 | 10.5281/zenodo.20081895 | the physical-layer section |
| Preprocessed derivative | 10.5281/zenodo.14903687 | the derivative subsection only |

```bash
python workspace/verify_datasets.py        # MD5 against the Zenodo records
```

Do not skip this. One archive we downloaded matched on size and failed on CRC.

## 1. Parse into cached views

```bash
python -u workspace/sybilbench/run_ingest.py
```

Writes `workspace/sybilbench/cache/<archive>.parquet` and `.truth.json`.
The view holds only receiver-observable fields. Ground truth is separate by construction.

## 2. Recover the raw pseudonyms

```bash
python -u workspace/verify/v3b_pseudomap_full.py
```

Writes `cache/<archive>.pseudomap.json`.

Required before the cascade. Without it the leakage arm would have to use the hashed
token, which carries no leakage at all -- the defect that invalidated our first attempt.

## 3. Structural claims, straight from the raw archives

These import none of the loader, so they check it rather than trusting it.

```bash
python -u workspace/verify/v1b_raw_refined.py       # ground-truth file census
python -u workspace/verify/v3c_identity_census.py   # identity counts from receiver logs
python -u workspace/verify/v7_dataset_usage.py      # what the 92 papers evaluate on
python -u workspace/verify/v9_derivative_audit.py   # the preprocessed derivative
python -u workspace/verify/v11_reporting_table.py   # corpus reporting table
python -u workspace/verify/v12_corpus_facts.py      # index size, ns-2 count, year span
python -u workspace/verify/v14_match_matrix.py --verify  # counts, without the texts
python -u workspace/sybilbench/exp13_pseudonym_decode.py # pseudonym decoding
python -u workspace/sybilbench/exp14_single_factor.py    # single-factor add-back
python -u workspace/verify/v15_nextgen_shortcuts.py     # NextGen replication
python -u workspace/verify/v16_nextgen_identifier.py    # NextGen identifier artefact
python -u workspace/verify/v17_master_census.py         # the machine-readable census
python -u workspace/verify/v18_information.py           # the leak in bits
python -u workspace/verify/v19_table_reproduction.py    # tables match their files
python -u workspace/verify/v20_release_splits.py        # publish the exact splits
python -u workspace/verify/v21_attacker_budget.py       # the 2 Hz attacker rate
```

`v3c` produces Table 4 in the paper: prevalence, identity counts, encoding rate,
benign rotation, duplication factor.

## 4. Metrics

```bash
python workspace/verify/v2_metrics.py               # self-test, must print PASS
```

Compares a sklearn-free ROC-AUC and average precision against scikit-learn and
scipy on random and heavily tied inputs. Every experiment calls both and aborts
on disagreement.

## 5. Experiments

```bash
python -u workspace/sybilbench/exp1_linkage.py        # timing vs geometry ablation, Fig. 1
python -u workspace/sybilbench/exp1b_rate_baseline.py # single-scalar baseline, Table 5
python -u workspace/sybilbench/exp9_cascade.py        # the seven-stage cascade
python -u workspace/sybilbench/exp9_cascade.py GridSybil_1416 --model=logistic
                                                      # any detector, own output file
python -u workspace/sybilbench/exp10_sensitivity.py GridSybil_0709   # Table 7
python -u workspace/verify/v4_timing_distributions.py # phase distributions and jitter
python -u workspace/verify/v5_pathloss_replicate.py 40 # physical layer
python -u workspace/verify/v6_prevalence_floor.py    # the prevalence floor
python -u workspace/verify/v8_nextgen_probe.py       # NextGen splits and aliases
python -u workspace/verify/v10_pseudonym_change.py   # rotation test, Section V-B
```

Wall-clock on one desktop: `exp9` takes roughly two hours across all eight
archives, dominated by the four denial-of-service archives with 47k-112k
identities each. Everything else finishes in minutes.

## 6. Build the paper

```bash
python workspace/paper/make_figure.py     # regenerate Fig. 1 from exp1_results.csv
python workspace/paper/assemble.py        # tables are emitted from the CSVs, not typed
python workspace/paper/check_sentences.py # sentence-length constraint
python workspace/paper/check_refs.py      # reference mix and citation integrity
cd workspace/paper && ../tools/tectonic.exe -X compile veremi_audit.tex --outdir .
```

`assemble.py` reads every table value from the result CSVs, so a number in the
paper cannot drift from the file that produced it. It is idempotent: running it
twice gives the same document.

## Which file backs which claim

| Paper item | Produced by | Result file |
|---|---|---|
| Table 4, census | `v3c_identity_census.py`, `v3b_pseudomap_full.py` | `verify/v3c_identity_census.csv`, `verify/v3b_pseudomap.csv` |
| Ground-truth under-reporting | `v1b_raw_refined.py` vs `v3b_pseudomap_full.py` | `verify/v1b_raw_refined.csv` |
| Table 5, single scalar | `exp1b_rate_baseline.py` | `sybilbench/exp1b_rate_baseline_v2.csv` |
| Figure 1 and Table 3 | `exp1_linkage.py` | `sybilbench/exp1_results.csv` |
| Phase distributions, jitter | `v4_timing_distributions.py` | `verify/v4_timing_distributions.csv` |
| Table 6, cascade | `exp9_cascade.py` | `sybilbench/exp9_cascade.csv` |
| Table 7, sensitivity | `exp10_sensitivity.py` | `sybilbench/exp10_sensitivity.csv` |
| Path loss, Table IX | `v5_pathloss_replicate.py` | `verify/v5_pathloss.csv` |
| Prevalence floor | `v6_prevalence_floor.py` | `verify/v6_prevalence_floor.csv` |
| Corpus dataset usage | `v7_dataset_usage.py` | `verify/v7_dataset_usage.csv` |
| NextGen splits and aliases | `v8_nextgen_probe.py` | `verify/v8_nextgen_probe.csv` |
| Preprocessed derivative | `v9_derivative_audit.py` | `verify/v9_derivative_*.csv` |
| Pseudonym-rotation test | `v10_pseudonym_change.py` | `verify/v10_pseudonym_change.csv` |
| Corpus reporting table, Table III | `v11_reporting_table.py` | `verify/v11_reporting_table.csv` |
| Index size, year span, ns-2 count | `v12_corpus_facts.py` | `verify/v12_corpus_facts.csv` |
| Extension citation count | OpenAlex, read 2026-09-05 | `verify/v13_citation_counts.json` |
| Pseudonym decoding, Table VI, Fig. 2 | `exp13_pseudonym_decode.py` | `sybilbench/exp13_pseudonym_decode.csv` |
| Single-factor add-back, Table VIII | `exp14_single_factor.py` | `sybilbench/exp14_single_factor.csv` |
| NextGen replication, Table XI | `v15_nextgen_shortcuts.py` | `verify/v15_nextgen_shortcuts.csv` |
| NextGen identifier artefact | `v16_nextgen_identifier.py` | `verify/v16_nextgen_identifier.csv` |
| Full machine-readable census | `v17_master_census.py` | `verify/v17_master_census.csv` |
| Leak in bits | `v18_information.py` | `verify/v18_information.csv` |
| Table-by-table reproduction check | `v19_table_reproduction.py` | prints per table |
| Released train/test splits | `v20_release_splits.py` | `verify/v20_splits.csv` |
| Attacker transmission budget | `v21_attacker_budget.py` | `verify/v21_attacker_budget.csv` |

## What this archive does not contain

The 92 extracted full texts are other people's papers and are not redistributed.
`v7`, `v11` and `v12` read them, so those three cannot run from this archive.

Their outputs are still checkable. `v14_match_matrix.csv` ships one boolean per
paper per pattern, which is the derived evidence every corpus count is a sum over:

```bash
python -u workspace/verify/v14_match_matrix.py --verify
```

That recomputes Table III, the dataset-usage figures and the ns-2 count from the
matrix and compares them against the published CSVs. To rebuild the matrix itself,
fetch the open-access PDFs listed in `index.csv` and extract them to
`workspace/text/`, then run the same script without `--verify`.

## Running the cascade on your own detector

`exp9_cascade.py` takes `--model=forest|boost|tree|logistic`. Output is named after
the run: a different model, or a subset of archives, writes its own file rather than
overwriting `exp9_cascade.csv`. That file backs Table XI and a partial run truncated
it once, which is why the naming is defensive.

## Known non-determinism

Random forests are seeded, splits are seeded, and bootstraps are seeded.
Reported values are means over five seeds for the cascade and three for the sweeps.
Seed spread is reported beside every mean, because at 3 % prevalence it is large.
The physical-layer result uses GroupKFold, so its point estimate and its
interval describe the same out-of-fold ranking. The script asserts that.
