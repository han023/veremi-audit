# Zenodo: every remaining field, filled in

Companion to `ZENODO_RECORD.md`, which covers files, title, description and the
publish order. This covers the rest of the form. Field semantics checked against
Zenodo's own documentation on 6 September 2026.

Sections you can skip are marked **leave empty** with the reason. Leaving a field
empty is a decision, and an empty field is better than a plausible-looking guess.

---

## Publication date — **required**

```
2026-09-06
```

Zenodo: *"a required field. By default, it is set to the date the draft was created.
If your upload was previously published elsewhere (e.g. a journal article), please
use the date of the first publication."*

This artefact has not been published anywhere before, so the deposit date is
correct. Use the date you actually publish the record, not today's if you deposit
later. Format is `YYYY-MM-DD`; EDTF forms like `2026-09` are accepted but there is
no reason to be imprecise here.

---

## Licence and copyright

**Licence field:**
```
MIT License
```

Pick it from the SPDX list rather than typing it.

**There is no separate copyright-holder field on Zenodo.** Copyright is asserted by
authorship plus the licence, so nothing further is needed. If you want it stated
explicitly, add a `LICENSE` file to the archive containing:

```
Copyright (c) 2026 Hannan Muzammil

Code: MIT License.
Result tables and derived data: CC-BY-4.0, matching the CC-BY licensing of the
VeReMi source archives from which they are derived.
```

**Why MIT and not CC-BY-4.0 for the whole record.** The upload is mostly software,
and Zenodo takes one licence. The inputs are CC-BY, so the derived tables carry
CC-BY; the description already says so. If you prefer the reverse emphasis, choose
CC-BY-4.0 and note that the code is MIT. Either is defensible; do not leave it unset.

---

## Funding — **leave empty**

Not required. Zenodo: *"provide information about the awards or grants which funded
the research output."*

This work was unfunded. Declaring a funder you do not have is a false statement in a
permanent record, and an empty funding section is unremarkable.

---

## Alternate identifiers — **leave empty for now**

This is for identifiers of *this same record* held elsewhere — an arXiv ID, a
handle, an existing DOI for the same artefact. You have none yet.

Add one later if you post the paper to arXiv:

| Scheme | Identifier | Relation |
|---|---|---|
| arXiv | `arXiv:XXXX.XXXXX` | *is identical to* — only if it is the same object |

Do **not** put the paper's journal DOI here. A paper is a different object from its
replication package; that belongs in *Related works*.

---

## Related works — six entries

This is the field that makes the record findable from the datasets it audits, and
it is the one most people leave blank. Fill it.

| Relation | Scheme | Identifier | Why |
|---|---|---|---|
| is supplement to | DOI | *paper DOI, once assigned* | ties artefact to article |
| is derived from | DOI | `10.5281/zenodo.20081895` | VeReMi 2018 |
| is derived from | DOI | `10.5281/zenodo.20090854` | VeReMi Extension |
| is derived from | DOI | `10.5281/zenodo.14903687` | preprocessed derivative |
| references | DOI | `10.1109/ICC40277.2020.9149132` | the Extension paper |
| references | DOI | `10.1109/VNC69225.2026.11629123` | VeReMi NextGen |

Add the first row after the paper is accepted, as a new version of the record.

**Resource type** for each: `Dataset` for the three Zenodo records, `Publication /
Conference paper` for the two papers.

---

## References — optional, and worth filling

Free-text citations of works the record builds on. Distinct from *Related works*,
which is machine-readable links; this is the human-readable list.

Paste these three:

```
Kamel, J., Wolf, M., van der Heijden, R. W., Kaiser, A., Urien, P., & Kargl, F. (2020). VeReMi Extension: A Dataset for Comparable Evaluation of Misbehavior Detection in VANETs. IEEE ICC. https://doi.org/10.1109/ICC40277.2020.9149132
```
```
van der Heijden, R. W., Lukaseder, T., & Kargl, F. (2018). VeReMi: A Dataset for Comparable Evaluation of Misbehavior Detection in VANETs. SecureComm. https://doi.org/10.1007/978-3-030-01701-9_18
```
```
Hermann, A., Remmers, J.-N., Eisermann, D., Erb, B., & Kargl, F. (2026). VeReMi NextGen: A Dataset for Evaluating Misbehavior Detection Systems in VANETs. IEEE VNC. https://doi.org/10.1109/VNC69225.2026.11629123
```

The full 37-item bibliography is inside the archive as `references.bib`; there is no
need to paste it here.

---

## Software section

Shown because the resource type is *Software*.

**Repository URL:**
```
https://github.com/<your-username>/veremi-audit
```
Leave empty until the repository exists. Do not enter a URL you have not created.

**Programming language:**
```
Python
```

**Development status:**
```
Inactive
```

Zenodo offers Concept, WIP, Suspended, Abandoned, Active, Inactive, Unsupported.
`Inactive` is the honest label for a frozen replication package: complete, not
abandoned, not under active development. Choose `Active` only if you intend to keep
maintaining it.

---

## Publishing information — **leave empty**

These fields (journal, volume, issue, pages, imprint, thesis) describe a *published
article*. This record is software, and the article is a separate object linked
through *Related works*.

Filling them would claim the archive is the journal publication. It is not.

---

## Conference — **leave empty**

For records that *are* conference contributions: name, dates, place, session.

The paper is not yet accepted anywhere, and even once it is, the conference belongs
on the paper's record, not the artefact's. Revisit only if you deposit the paper
itself on Zenodo.

---

## Domain specific fields — **leave empty**

Zenodo shows extra schemas for certain communities. None matches vehicular network
security, and forcing an unrelated schema adds noise.

---

## Recommended information, the rest

**Contributors:** leave empty. Single author, already in Creators.

**Subjects / keywords:**
```
VANET
misbehaviour detection
Sybil attack
benchmarking
reproducibility
VeReMi
V2X
```

**Languages:** `English`

**Dates:** leave empty. This is for additional dates — collected, valid, submitted.
The publication date already covers it.

**Version:**
```
v1.0.0
```

**Publisher:**
```
Zenodo
```
This is the default and is correct: Zenodo is publishing the record.

---

## Summary table

| Field | Value |
|---|---|
| Resource type | Software |
| Publication date | date you publish, `YYYY-MM-DD` |
| Licence | MIT License |
| Version | v1.0.0 |
| Publisher | Zenodo |
| Language | English |
| Funding | empty — unfunded |
| Alternate identifiers | empty until arXiv |
| Related works | six entries above |
| References | three entries above |
| Software: language | Python |
| Software: status | Inactive |
| Software: repository | empty until GitHub exists |
| Publishing information | empty — this is not the article |
| Conference | empty — not a conference contribution |
| Domain specific | empty — no matching schema |
