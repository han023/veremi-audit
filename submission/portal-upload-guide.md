# What to upload, slot by slot

Portal: <https://ieee.atyponrex.com/journal/t-its> (IEEE Author Portal).
Not ScholarOne — that is only for final files of accepted papers.

Files are numbered in upload order.

---

## Required slots

### 1. Main Manuscript → `01-main-manuscript-latex.zip`

The slot takes **MS Word or LaTeX**, not PDF, and allows one bundled archive
holding "all LaTeX files, BibTeX files, figures, tables, all LaTeX classes and
packages". That is exactly this zip:

| In the archive | Why |
|---|---|
| `manuscript.tex` | The paper. References are inline `\bibitem`s, so there is no `.bib` file to include |
| `IEEEtran.cls` | V1.8b, the class the paper was compiled against. Bundled so the portal cannot typeset it against a different version and change the page count |
| `fig_ablation.pdf` | Fig. 1 |
| `fig_decode.pdf` | Fig. 2 |
| `fig_prevalence.pdf` | Fig. 3 |

Nothing else is in it — no supplementary material, no submission notes, no PDF of
the manuscript. That matches the slot's instruction.

**Verified:** unpacked into an empty directory and compiled with nothing else
present, it produces a 10-page PDF whose text is identical to the reference build.

### 2. Conflict of Interest → `02-conflict-of-interest.pdf`

One page. States that no author has a conflict to disclose, that the work had no
funding or sponsor, and that the author has no affiliation with the groups whose
datasets the paper audits.

The portal also requires the statement to appear **inside** the manuscript. It
does: the first author footnote on page 1 reads "This work received no external
funding, and the author declares no conflict of interest."

---

## Optional slots

### Supplementary Material for Review → `04-supplementary-replication-package.zip`

**Recommended, not required.** The complete replication package: experiments,
independent verifiers, every result CSV, the paper source, and a container that
re-verifies the whole thing in one command. Reviewers can check any number in the
paper without leaving the portal.

Two things to know before you attach it. It will be **published as Supplementary
Material**, which is fine — the code is MIT and the tables are CC-BY-4.0. And it
duplicates the Zenodo deposit, which the paper already cites. If you would rather
reviewers use the DOI, skip this slot; nothing in the paper depends on it.

### Cover letter / Comments → `03-cover-letter.pdf`

One page. Summarises the contribution, states the narrow stance of the paper, and
discloses that the public Zenodo archive contains a copy of the manuscript — noted
as a preprint posting rather than a prior publication, with an offer to add the
DOI and copyright notice on acceptance or to withdraw the copy if the journal
prefers.

Raising that yourself is better than having an editor find it.

### Leave these empty

| Slot | Why |
|---|---|
| Main Document — Tracked Changes | For revisions. This is an initial submission |
| Image | The figures are already in the main archive |
| Previously Published — Statement / Files | Nothing here was previously published. The Zenodo copy is a preprint, and the cover letter discloses it |
| LaTeX Supplementary File | Nothing supplementary is part of the TeX document |

---

## Not for upload

`00-manuscript-preview-do-not-upload.pdf` is the compiled paper, for you to read
before submitting. The portal builds its own PDF from the LaTeX archive, so do not
upload this one into the Main Manuscript slot — that slot wants source.

---

## The affiliation matching step

The portal asks you to match "Hannsoft" against Ringgold, its organization
registry, and it may offer unrelated suggestions before you search. Ignore them.

**Do not select an organization you have no affiliation with.** A wrong match is
published, indexed in IEEE Xplore, and propagates to every database downstream. An
unmatched affiliation is harmless; a false one is not.

What to do: type `Hannsoft` into **Find Organization**. It will not be found —
checked against ROR, which returns zero results, and a private company of this size
is very unlikely to be in Ringgold either. After the search comes back empty the
portal offers **"Organization is not listed"**. Select that. The affiliation card
is then marked as matched and the affiliation is recorded exactly as you entered
it, so it still publishes as "Hannsoft".

The only thing a match affects is IEEE detecting an institutional open-access
agreement. Hannsoft has none, so nothing is lost.

---

## The Additional Information page

**Keywords** (optional, up to 2 more). The six from the manuscript are already
carried across. If you add any, add `V2X` and `evaluation methodology` — the first
widens discoverability, the second helps the editor route the paper to someone who
reviews evaluation protocol rather than detector design, which is what this paper
argues about.

**Methodologies** (1-2 required):

  - **Methods for security and privacy** — certain; this is a security paper.
  - **Data-based approaches (learning, deep learning, reinforcement learning)** —
    the objects under audit are learned detectors, and the findings are about how
    they are trained and evaluated.

If you would rather draw a statistics-minded reviewer than an ML one, swap the
second for *Data analytics and data science*. Do not pick *Modelling and
simulation*: the archives are simulator output, but this paper runs no simulation.

**Applications** (1-2 required):

  - **Vehicular Ad hoc Networks** — exact.
  - **Connected and Autonomous Vehicles** — the deployment setting the paper argues
    the benchmarks fail to represent.

**Submitted previously to this journal?** No, it wasn't submitted previously.

**Human subjects?** No. The manuscript says so in its Ethics section: the work
analyses published artefacts, involves no human subjects, and every vehicle in the
archives is simulated.

**Animal subjects?** None. Leave blank.

**Opposed reviewers?** Leave empty. The paper names published work and mentions a
dataset withdrawn under an authorship dispute, while taking no position on it.
Naming opposed reviewers would undercut that stance and reads as defensive. Let the
editor manage conflicts.

**Cover letter?** Yes — `03-cover-letter.pdf`, already attached.

**Previously published, in whole or in part?**
**No, this manuscript has never been previously presented or published.**

That is the correct answer even though the Zenodo archive contains a copy of the
PDF. A preprint is not a prior publication: the submission declaration you already
accepted says so explicitly ("with exception that articles are permitted to be
submitted to preprint servers"), and IEEE policy permits preprint posting. Choosing
"Yes" would ask you to describe how this submission differs from the earlier one,
which is unanswerable for an identical preprint.

The cover letter discloses the Zenodo copy anyway, which is the right belt-and-braces
move: you raise it, rather than an editor finding it.

**Code associated with the manuscript?** **Yes.** That is simply true. The upload
itself can wait — the page says code may be added "at submission, revision, or after
acceptance", so answering Yes does not commit you to doing it today.

Worth doing eventually, though. This paper argues that published results should be
reproducible, and a Code Ocean capsule puts an executable copy behind a tab on the
Xplore article page. The package already has a `Dockerfile` and a self-test, so the
capsule is mostly a repackaging job rather than new work.

**Data associated with the manuscript?** **Yes.** You do not need IEEE DataPort;
the field wants a DOI and title, and the deposit already exists:

```
DOI:   10.5281/zenodo.22397725
Title: Code and data for "What VeReMi Measures: Structural Artefacts in
       VANET Misbehaviour Detection Benchmarks"
```

The page also asks that the manuscript reference the data. It does — checked: that
DOI appears in the Availability section, and the three source-archive DOIs
(10.5281/zenodo.20081895, .20090854, .14903687) are cited too.

---

## Before you click submit

- [ ] Read `00-manuscript-preview-do-not-upload.pdf` end to end
- [ ] Degree name ("B.S.") and campus ("Lahore") correct in the biography
- [ ] Decide whether to add Hannsoft's city to the author footnote
- [ ] Zenodo record published and the DOI resolving
- [ ] Declarations ticked — see `SUBMIT_TO_IEEE.md` for what each one was checked against
- [ ] Abstract and keywords pasted from `SUBMIT_TO_IEEE.md`
- [ ] ORCID 0009-0000-7502-2755 entered, matching the paper

The manuscript is exactly 10 pages against a 10-page suggested length, so it
carries no overlength charge. An eleventh page costs $175, so if you edit anything,
recompile and recheck the page count before uploading.
