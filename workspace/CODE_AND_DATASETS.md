# Code and Datasets Found in the Corpus

Result of scanning the full text of all 92 papers for code links, repositories, and data-availability
statements (`workspace/mine.py`, results in `workspace/notes/paper_notes.csv`).

## Headline finding

| | count |
|---|---|
| Papers read | 92 |
| Papers mentioning code at all | **4** |
| Papers with a working public code repository | **0** (the one that existed is now access-restricted) |
| Papers using any *named public dataset* | **9** |
| Papers whose data statement is "available from the author on request" | 4 |
| Papers whose data statement is "not applicable" despite reporting experiments | 2 |

This is the single strongest empirical gap in the field (see `synthesis/03_research_gaps.md`, G2).

---

## 1. Code mentioned in corpus papers

### 1.1 Güven & Tayşi — Istanbul VANET Sybil dataset + simulation source — **RESTRICTED**
- Papers: *Creating A Realistic Sybil Attack Dataset For Inter-vehicle Communication* (Research Square 2024,
  doi 10.21203/rs.3.rs-5417476/v1) and the journal version in *Peer-to-Peer Networking and Applications* 18:234
  (2025, doi 10.1007/s12083-025-02058-w); used again in Tayşi 2025 (DÜMF Müh. Derg.).
- Repo: `github.com/VANET-Istanbul-Sybil-Attack-Dataset/dataset-src` — cloned to `workspace/code/dataset-src`
  (94 KB: `README.md` + `DATA_LICENSE.md` only).
- **Status: data and code withdrawn.** The repository README states the owner did not authorise publication of
  the associated article, is pursuing its removal from the journal, and that all data and code access is
  restricted; the six `.xz` dataset dumps (~93 GB) are described as subject to copyright-infringement claims.
- **Implication for us:** do not attempt to obtain or use this dataset. Cite the situation as evidence for the
  reproducibility gap (G2) and as the motivation for building an open replacement (`05_new_paper_plan.md`,
  Option C). Treat the two Güven papers as *disputed* in any review we write.

### 1.2 Man et al. 2024 — cites `github.com/mschoenebeck/bls12-381`
Third-party pairing library used for batch verification; not the authors' own artefact.

### 1.3 Everything else
No repositories. Typical statements: *"datasets used and/or analysed during the current study available from
the corresponding author on reasonable request"* (Suganyadevi 2025), *"Dataset available on request from the
authors"* (Khatri 2024), *"simulation scripts and processed datasets … from the corresponding author"*
(Hadri 2026).

---

## 2. Datasets actually used by corpus papers

| Dataset | Papers using it | Public? |
|---|---|---|
| VeReMi | 5 | yes, CC-BY |
| VeReMi Extension | 4 | yes, CC-BY |
| F2MD (framework, generates data) | 4 | yes, open source |
| LuST (Luxembourg SUMO scenario) | 2 | yes, open source |
| Generic IDS sets (NSL-KDD / CICIDS-family) | 2 | yes — but **not vehicular**; using them for VANET Sybil detection is a methodological red flag worth calling out |
| Istanbul RSSI Sybil dataset | 3 | **no longer** (see 1.1) |

---

## 3. What is downloaded locally

### `workspace/datasets/` (Zenodo, all CC-BY 4.0) — **download in progress**

| Folder | Zenodo record | Content | Size | Status |
|---|---|---|---|---|
| `VeReMi_original/` | 20081895 (doi 10.5281/zenodo.20081895) | van der Heijden et al. 2018 misbehaviour-detection dataset, LuST traffic, 225 simulations | 3.62 GB | downloading |
| `VeReMi_preprocessed/` | 14903687 | `balanced_veremi_dataset.csv` — class-balanced, ML-ready | 0.76 GB | queued |
| `VeReMi_Extension_sybil/` | 20090854 | **Sybil-specific subsets only**: `GridSybil_0709/1416`, `DataReplaySybil_0709/1416`, `DoSRandomSybil_0709/1416`, `DoSDisruptiveSybil_0709/1416` (0709 = low density, 1416 = high density) | 3.82 GB | queued |
| `VeReMi_NextGen_sybil/` | 19665762 | `InTAS_{urban,highway}_{2,7}_trafficCongestionSybil` + ground-truth JSONs | ~4.0 GB | queued |

Each folder carries `_zenodo_metadata.json` (title, authors, license, DOI) for citation.

**Resuming.** Zenodo throttles and drops long transfers; the first attempt died with a `ConnectionError`
mid-file. `workspace/get_datasets.py` is resumable — it sends an HTTP `Range` header, appends to the partial
file, retries 8× with backoff, and skips any file whose size already matches Zenodo's manifest. So:

```bash
python workspace/get_datasets.py      # safe to re-run as often as needed
```

Progress log: `workspace/datasets/download.log`. Verify completeness by comparing each file's size against
`_zenodo_metadata.json`; a short file means the run was interrupted, so just re-run.

Full non-Sybil subsets were deliberately skipped (VeReMi Extension is 19.9 GB total, NextGen 36.2 GB) —
widen the `JOBS` filters in the script to fetch them, if disk allows (~46 GB free at time of writing).

### `workspace/code/`

| Folder | Source | Use |
|---|---|---|
| `F2MD/` | `github.com/josephkamel/F2MD` | Framework For Misbehavior Detection — the OMNeT++/Veins/SUMO pipeline that generated VeReMi Extension. This is the tool to extend for new Sybil scenarios and adaptive attackers (RQ4, RQ6). |
| `LuSTScenario/` | `github.com/lcodeca/LuSTScenario` | Luxembourg SUMO Traffic scenario, 24 h realistic mobility — the traffic substrate behind VeReMi. 452 MB. |
| `dataset-src/` | Istanbul repo | Restricted; kept only as evidence of the takedown notice. |

---

## 4. Recommended additional artefacts (not downloaded, links only)

| Artefact | Why | Where |
|---|---|---|
| VeReMi Extension full 19.9 GB | needed if extending beyond Sybil to cross-attack studies (RQ5) | Zenodo 20090854 |
| VeReMi NextGen full 36.2 GB | newest, InTAS maps, more attack families | Zenodo 19665762 |
| Veins + OMNeT++ + SUMO toolchain | to run F2MD and generate new data | veins.car2x.org |
| ETSI TS 102 941 / IEEE 1609.2 specs | for the standards-aware work (RQ7) | ETSI / IEEE (free ETSI download) |
| InTAS scenario | NextGen's traffic base | github.com/silaslobo/InTAS |

## 5. Practical notes

- VeReMi-family data is JSON-lines per vehicle (`traceGroundTruthJSON-*` and per-receiver logs); the
  preprocessed CSV is the fastest way to prototype a classifier before committing to the full pipeline.
- The `0709` / `1416` suffixes are simulation start times = traffic-density regimes; using both is how you get
  the cross-density generalisation test in RQ2.
- Attack labels live in the ground-truth files, not the receiver logs — build the join carefully or you
  inherit exactly the label-leakage problem the corpus suffers from.
