# Zenodo: the complete guide

Do this **before** submitting the paper. The paper's Availability section cites the
DOI, so the record has to exist first.

---

## Part 1 — What you are uploading

**One file:** `workspace/release/veremi-audit-artefact-2026-09-06.zip`
147 files · 0.96 MB compressed · 2.1 MB unpacked

### What is inside

| Part | Contents |
|---|---|
| `workspace/paper/` | LaTeX source, four figure scripts, three checkers, the compiled PDF |
| `workspace/sybilbench/` | loader, analysis, experiments 1–14, every result CSV |
| `workspace/verify/` | independent verifiers v1–v21, sklearn-free metrics, released splits |
| `workspace/synthesis/` | the audit ledger and the cascade write-up |
| `index.csv`, `references.bib` | the 331-record corpus index |
| `Dockerfile`, `requirements.txt` | one-command reproduction, pinned versions |
| `REPRODUCE.md`, `MANIFEST.md`, `DEPOSIT.md` | how to run it, per-file hashes, deposit notes |

### What is deliberately excluded, and why

- **The VeReMi archives.** 12 GB, not ours to redistribute, one download from their
  own records. `verify_datasets.py` fetches and MD5-checks them.
- **The 92 corpus papers and their extracted text.** Other people's work. The derived
  match matrix ships instead, so every corpus count stays reproducible without them.
- **The parquet cache.** 207 MB, rebuilt by `run_ingest.py`.

Say this in the description. A reviewer who finds no dataset should learn why in the
record, not by guessing.

---

## Part 2 — The order of operations

The archived code must be the code that produced the archived PDF. That forces this
sequence, and the DOI has to go in **before** the final compile.

```bash
# 1. verify what you have
python workspace/make_release.py --selftest          # expect six passes
python workspace/verify/v19_table_reproduction.py    # every table matches its file
```

**2.** On Zenodo, begin a new upload and **reserve the DOI** without publishing
(Part 3, step 5). You now have a DOI that does not yet resolve.

**3.** Put it in the paper:

```bash
# replace ZENODO-DOI-HERE in workspace/paper/body_new.tex with the reserved DOI
python workspace/paper/assemble.py
cd workspace/paper && ../tools/tectonic.exe -X compile veremi_audit.tex --outdir .
```

**4.** Refresh the hashes and rebuild so the archive carries that PDF:

```bash
python workspace/make_manifest.py
python workspace/make_release.py --selftest          # six passes again
```

**5.** Upload that archive to the reserved record and publish.

**After publishing, stop editing the paper.** Any later change makes the archived
code a different version from the one the PDF cites. If a change becomes necessary,
publish a *new version* of the record and cite that version's DOI in the revision.
Zenodo versions share a concept DOI, so the citation stays coherent.

---

## Part 3 — The form, field by field

Sign in at <https://zenodo.org> with GitHub or ORCID, then *New upload*.

**1. Files.** Drag the zip in. Wait for the upload to finish before continuing.

**2. Upload type:** `Software`.

**3. Title** — paste:
```
Code and data for "What VeReMi Measures: Structural Artefacts in VANET Misbehaviour Detection Benchmarks"
```

**4. Authors:** Hannan Muzammil, affiliation Hannsoft. Add your ORCID if you have
one; it links the record to you permanently.

**5. Reserve DOI.** In the *Basic information* block, click **Reserve DOI**. Do this
now, before the description, so you can stop and update the paper.

**6. Description** — paste:
```
Replication package for a measurement audit of the VeReMi and VeReMi Extension
misbehaviour-detection benchmarks.

Contents: the loader and its leakage controls, fourteen experiments, twenty-one
independent verifiers, every result table as CSV, the LaTeX source and compiled
paper, and a container that re-verifies the package in one command.

The package regenerates every number in the paper. Tables are emitted from the
result CSVs rather than typed, and a claim checker re-derives each printed value
from its source file. Both run inside the container build, so a failing build is a
failing artefact.

The source archives are not redistributed. VeReMi (10.5281/zenodo.20081895),
VeReMi Extension (10.5281/zenodo.20090854) and the preprocessed derivative
(10.5281/zenodo.14903687) must be fetched from their own records; the included
verify_datasets.py checks them by MD5. The 92 open-access papers behind the corpus
tables are likewise not redistributed, and a derived match matrix ships so those
counts remain reproducible without them.
```

**7. Licence:** `MIT`. Zenodo takes one field; the code is MIT and the result tables
are CC-BY-4.0, matching their CC-BY inputs. State that split in the description if
you want it explicit.

**8. Keywords:** `VANET`, `misbehaviour detection`, `Sybil attack`, `benchmarking`,
`reproducibility`, `VeReMi`, `V2X`

**9. Related identifiers** — add each row:

| Relation | Identifier |
|---|---|
| is supplement to | the paper's DOI, once it has one |
| is derived from | `10.5281/zenodo.20081895` |
| is derived from | `10.5281/zenodo.20090854` |
| is derived from | `10.5281/zenodo.14903687` |
| references | `10.1109/ICC40277.2020.9149132` |
| references | `10.1109/VNC69225.2026.11629123` |

**10. Version:** `v1.0.0`

**11. Language:** English. **Publication date:** today.

Then **Publish**.

---

## Part 4 — GitHub alongside, not instead

A repository is better for reading and forking. A bare GitHub URL is not archival:
repositories move and vanish, which is the failure our own corpus documents — three
papers give a repository link, all three to one archive that was restricted when we
sought access.

```bash
git init && git add . && git commit -m "VeReMi audit: replication package"
git remote add origin https://github.com/<you>/veremi-audit.git
git push -u origin main
git tag v1.0.0 && git push --tags
```

Then in Zenodo, open *GitHub* in your account settings, flip the switch for the
repository, and cut a GitHub **Release**. Zenodo archives each release automatically
and mints a DOI for it.

Cite the **Zenodo DOI** in the paper. Put the GitHub URL in the repository
description, not in Availability.

---

## Part 5 — Final checklist

- [ ] Zip rebuilt *after* the final PDF compile
- [ ] `ZENODO-DOI-HERE` no longer appears in the PDF
- [ ] `make_release.py --selftest` shows six passes
- [ ] `v19_table_reproduction.py` shows every table matching
- [ ] Description names the three source records
- [ ] Related identifiers added
- [ ] Version set to `v1.0.0`
- [ ] Licence chosen

A published Zenodo record cannot be unpublished, and files can only be replaced by
issuing a new version. That is why the checks come first.

---

## Part 6 — If the paper is double-blind

WiSec and VehicleSec review double-blind. The DOI resolves to a record carrying your
name, so citing it de-anonymises the submission.

For the review copy: remove the author block, and replace the Availability sentence
with a note that the artefact will be released on acceptance. Keep the real
Availability text in the camera-ready. T-ITS is single-blind, so this does not apply.
