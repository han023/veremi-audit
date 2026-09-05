# Where the code is, and where to deposit it

## Where it is now

Everything lives under `workspace/`. Nothing is in version control yet — this tree
is not a git repository.

| Path | What | Ships? |
|---|---|---|
| `workspace/sybilbench/` | loader, analysis, experiments 1–10 | yes |
| `workspace/verify/` | independent verifiers v1–v8, sklearn-free metrics | yes |
| `workspace/paper/` | LaTeX source, figure script, three checkers | yes |
| `workspace/synthesis/` | audit ledger, cascade write-up, gap analysis | yes |
| `index.csv`, `references.bib` | the 331-record corpus index | yes |
| `workspace/datasets/` | 12 GB of source archives | **no** |
| `workspace/sybilbench/cache/` | 207 MB parquet cache | **no** |

The two excluded directories are reproducible: `verify_datasets.py` checks the
Zenodo MD5s and `run_ingest.py` rebuilds the cache. Shipping them would add 12 GB
and redistribute someone else's data under our name.

## The archive

```bash
python workspace/make_release.py
```

Produces `workspace/release/veremi-audit-artefact-<date>.zip`. It contains no
dataset files, no parquet cache and no `__pycache__`.

Run it with `--selftest` before depositing:

```bash
python workspace/make_release.py --selftest
```

That unpacks the archive somewhere clean and runs the metric self-test, the corpus
counts, the paper assembly and all three checkers inside it. Two silent breakages
were caught this way: a flattened archive layout in which no script could resolve
its paths, and JSON evidence files that were never being packed.

## Where to deposit

**Zenodo is the right primary home.** It mints a DOI, has no size problem at this
scale, is where both VeReMi releases already live, and is accepted by every venue
on our target list. A Zenodo DOI is what the Availability section should cite.

1. Sign in at <https://zenodo.org> and choose *New upload*.
2. Upload the release zip.
3. Type: *Software*. Title: match the paper. Authors: as on the paper.
4. Licence: choose one that fits the inputs. The datasets we consume are CC-BY,
   so **CC-BY-4.0** for the data tables and **MIT** or **Apache-2.0** for the code
   is a clean pairing. State which applies to which in the record description.
5. Add related identifiers pointing at the datasets you consume:
   VeReMi `10.1007/978-3-030-01701-9_18`, VeReMi Extension
   `10.1109/ICC40277.2020.9149132`, VeReMi NextGen `10.5281/zenodo.19665762`.
6. Reserve the DOI **before** publishing, paste it into the paper's Availability
   section, recompile, then publish the record.

**GitHub alongside, not instead.** A repository is better for anyone who wants to
read or fork the code, but a bare GitHub URL is not archival — repositories move
and disappear, which is exactly the failure our own corpus documents (four papers
mention code, none of it reachable). Use Zenodo's GitHub integration so each
release is archived automatically and gets its own DOI.

**If the venue runs an artefact track** (WiSec and VehicleSec both do), submit the
same archive there. The evaluation asks for a reproduction path; `REPRODUCE.md`
already provides it, including expected wall-clock times.

## The freeze order

The archived code must be the code that produced the archived PDF, so the DOI has
to go in before the last compile and nothing may change after it.

1. `python workspace/make_release.py --selftest` -- expect six passes.
2. `python workspace/verify/v19_table_reproduction.py` -- every table matches its file.
3. Reserve the Zenodo DOI without publishing the record.
4. Replace `ZENODO-DOI-HERE` in `workspace/paper/body_new.tex` with it.
5. `python workspace/paper/assemble.py` then compile the final PDF.
6. `python workspace/make_manifest.py` so the hashes cover the final state.
7. `python workspace/make_release.py --selftest` once more.
8. Upload that archive to the reserved record and publish.

After step 8, do not edit the paper. Any change makes the archived code a
different version from the one the PDF cites, which is the thing this order exists
to prevent. If a change is unavoidable, publish a new version of the record and
cite that version's DOI.

## Container

```bash
docker build -t veremi-audit workspace
docker run --rm veremi-audit
```

The build fails if the shipped artefact does not verify, so a green build is
itself the check. The image excludes the source archives; mount them to rerun the
experiments rather than verify the outputs.

## One honest caveat to include in the record

Two things in the tree are not ours to redistribute and are excluded: the VeReMi
archives themselves, and anything from the Guven and Tay\c{s}i dataset, whose
repository carried an owner takedown and authorship-dispute notice when we sought
access. The record description should say the archives must be fetched from their
own Zenodo records.
