# What VeReMi Measures

Replication package for a measurement audit of the VeReMi and VeReMi Extension
misbehaviour-detection benchmarks.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22397725.svg)](https://doi.org/10.5281/zenodo.22397725)

**Paper:** `workspace/paper/veremi_audit.pdf` (conference, 12 pp) · `veremi_audit_journal.pdf` (IEEE Transactions, 10 pp) · **Archive:** <https://doi.org/10.5281/zenodo.22397725>

---

## What this is

The VeReMi archives are the main shared benchmark for vehicular misbehaviour
detection. This audits them by measurement rather than by reading, and reports what
survives once the shortcuts are removed.

One untrained scalar solves six of the eight Sybil archives, reading message timing
alone and never a claimed position. Pseudonyms encode the true sender in 86.5–100%
of identity pairs, and an untrained decoder recovers the emitting vehicle 87.6% of
the time against 0.3% under a permuted control. Attacker prevalence is fixed at 30%
of vehicles in every archive. Running one detector through seven progressively
stricter protocols takes AUC from 0.998 to 0.843, and a single-factor add-back from
the controlled end agrees on which advantage dominates.

VeReMi NextGen repairs the identity leak. The message-rate shortcut survives it, and
a new identifier artefact replaces the old one.

## Reproducing it

```bash
docker build -t veremi-audit .
docker run --rm veremi-audit
```

The build fails if the artefact does not verify, so a green build is the check.
Without Docker:

```bash
pip install -r workspace/requirements.txt
python workspace/verify/v2_metrics.py              # metrics, self-tested
python workspace/verify/v14_match_matrix.py --verify
python workspace/paper/check_claims.py             # every printed number
```

Full route from raw archives to results: `workspace/REPRODUCE.md`.

## What is not here

The VeReMi archives themselves (12 GB, not ours to redistribute) and the 92
open-access papers behind the corpus tables. Both are fetched or checked by scripts
included here; a derived match matrix ships so the corpus counts stay reproducible
without the texts.

| Source | Record |
|---|---|
| VeReMi | [10.5281/zenodo.20081895](https://doi.org/10.5281/zenodo.20081895) |
| VeReMi Extension | [10.5281/zenodo.20090854](https://doi.org/10.5281/zenodo.20090854) |
| Preprocessed derivative | [10.5281/zenodo.14903687](https://doi.org/10.5281/zenodo.14903687) |

## Layout

```
workspace/paper/        LaTeX source, figures, three checkers, compiled PDF
workspace/sybilbench/   loader, analysis, experiments 1-14, result CSVs
workspace/verify/       independent verifiers v1-v21, sklearn-free metrics
workspace/synthesis/    the audit ledger and cascade write-up
index.csv               the 331-record corpus index
```

## Running the cascade on your own detector

```bash
python workspace/sybilbench/exp9_cascade.py GridSybil_0709 --model=logistic
```

Accepts `forest`, `boost`, `tree`, `logistic`. Output is named after the run, so a
different model writes its own file rather than overwriting the published one.

## Citing

```bibtex
@software{muzammil2026veremi,
  author    = {Muzammil, Hannan},
  title     = {Code and data for "What VeReMi Measures: Structural
               Artefacts in VANET Misbehaviour Detection Benchmarks"},
  year      = {2026},
  publisher = {Zenodo},
  version   = {v1.0.0},
  doi       = {10.5281/zenodo.22397725},
  url       = {https://doi.org/10.5281/zenodo.22397725}
}
```

## Licence

MIT for the code, CC-BY-4.0 for the result tables, matching their CC-BY inputs.
See [LICENSE](LICENSE).
