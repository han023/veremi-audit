# Working Folder — Sybil Attacks in VANETs

Everything for the new paper lives here. Source corpus is one level up (`../pdfs`, `../index.csv`,
`../references.bib`).

## Map

| Path | What it is |
|---|---|
| `synthesis/01_field_evolution.md` | **Read this first.** How the field started (Douceur 2002 → Xiao 2006), the four eras, what changed and what never did. |
| `synthesis/02_method_taxonomy.md` | Six method families, representative papers, strengths/weaknesses, and the evaluation-practice audit. |
| `synthesis/03_research_gaps.md` | **v2, verified.** 8 OPEN gaps, 6 NARROW, 9 CLOSED (claims that verification killed). |
| `synthesis/04_research_questions.md` | **v2.** 14 research questions ranked by *verified* novelty, plus 6 proposable innovations (I1–I6). |
| `synthesis/05_new_paper_plan.md` | **v2.** The recommended paper (benchmark + difficulty index + adaptive adversaries) plus two follow-ons, with outlines, venues, staging and kill-switches. |
| `synthesis/06_gap_verification.md` | **Read before writing anything.** Every gap re-tested against the wider V2X/misbehaviour-detection literature (36 OpenAlex probes + 27 full-text probes): what survived, what died, and the innovation openings. |
| `synthesis/07_feasibility.md` | **What the data can actually support.** VeReMi record schema (measured), which detector families are buildable, and the md5 integrity workflow. |
| `synthesis/09_results_so_far.md` | **Paper-ready narrative.** Every measured number organised as two papers (the benchmark audit; the linkability dilemma), plus the methodological appendix on three self-corrections and what remains to run. |
| `sybilbench/` | The code: loader with leakage controls, pseudonym-change layer, six experiments, 12 result CSVs. See its own README for the eight design rules. |
| `synthesis/08_dataset_audit.md` | **Original measurements on the benchmark data**: identifier leakage 87–100 %, no pseudonym change, no RSSI, 30 % attacker prevalence, family variance, one corrupt archive. None of it previously reported. |
| `CODE_AND_DATASETS.md` | Every code link and dataset found in the 92 papers, what was downloaded, and the Istanbul-dataset takedown situation. |
| `notes/cards.md` | One card per paper (232 KB): abstract, claimed contribution, evaluation, stated limitations, methods/simulators/datasets. Chronological. |
| `notes/paper_notes.csv` | Machine-readable version: file, year, cites, venue, DOI, code URLs, code mentions, datasets, simulators, method tags. |
| `notes/cards.json` | Same as cards.md in JSON. |
| `notes/deep_extract.json` | Round-4 deep extraction from every full text: assumptions, threat models, evaluation parameters, claimed numbers, admitted limitations, stated future work, named baselines. |
| `notes/future_work_themes.json` | Thematic coding of what the 92 papers themselves declare unfinished. |
| `notes/keyword_audit.json`, `notes/gapcheck.json` | Raw probe results behind `06_gap_verification.md`. |
| `text/` | Plain-text extraction of all 92 PDFs — grep this instead of opening PDFs. |
| `datasets/` | VeReMi, VeReMi Extension (Sybil subsets), VeReMi NextGen (Sybil subsets), preprocessed VeReMi CSV. All CC-BY, with Zenodo metadata. **Download is resumable and may be incomplete — re-run `python workspace/get_datasets.py` until it prints `DATASETS DONE`.** |
| `code/F2MD` | Misbehaviour-detection framework (generates VeReMi-style data) — the tool to extend. |
| `code/LuSTScenario` | Luxembourg SUMO traffic scenario. |
| `code/dataset-src` | Istanbul Sybil dataset repo — **restricted by its owner**, kept as evidence only. |
| `*.py` | The pipeline: `extract.py` (PDF→text), `mine.py` (code/dataset/method mining), `cards.py` (per-paper cards), `get_datasets.py` (Zenodo downloader). |

## Where the project actually got to

The literature review (files 01–07) was the setup. The result is in `08_dataset_audit.md` and
`09_results_so_far.md`: **15 measured findings**, produced by running experiments on the benchmark rather than
reading about it, including two structural artefacts of VeReMi that no prior work reports, and a measured
account of why Sybil detection and location tracking cannot be separated. Three of my own headline claims were
overturned by self-audit along the way; the corrections are documented in place rather than quietly dropped.

## The three-line summary of the literature review

1. **The field's problem is evidential, not conceptual.** 20 years of schemes, 90–99 % accuracies, and no two
   numbers comparable: 83 of 92 papers evaluate on private simulations, 4 mention code, 0 have reachable
   repositories, 11 post-2020 papers still use NS-2.
2. **The attacker in the literature is weaker than the attacker in 2007.** Guette & Ducourthial showed
   power/antenna control breaks RSS-based detection; almost nothing since accounts for it, and no paper tests
   an adaptive or ML-evading adversary.
3. **The best opening move is a reproducible benchmark** on the VeReMi-family Sybil subsets already
   downloaded here — low risk, high value, and it becomes the substrate for an adaptive-attack paper and an
   open RSSI dataset afterwards.

## Reproducing / extending the pipeline

```bash
python workspace/extract.py       # PDFs -> workspace/text/
python workspace/mine.py          # -> notes/paper_notes.{csv,json}
python workspace/cards.py         # -> notes/cards.{md,json}
python workspace/get_datasets.py  # -> datasets/ (resumable; re-run until "DATASETS DONE")
```

Dependencies: `pypdf`, `requests` (already installed).
