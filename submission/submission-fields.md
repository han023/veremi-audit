# Submitting to IEEE Transactions on Intelligent Transportation Systems

Everything in this folder is what you upload. Nothing here needs editing except
the biography — see **Before you upload**, below.

**Submit here:** <https://ieee.atyponrex.com/journal/t-its> — the IEEE Author
Portal. Sign in with the same ORCID you put on the paper so the submission links
to your record.

Two other IEEE URLs are easy to confuse with it, and neither takes a new
submission:

| URL | What it actually is |
|---|---|
| `mc.manuscriptcentral.com/t-its` | ScholarOne. T-ITS uses it for **final files of already-accepted papers**, not for new submissions |
| `publishingportal.ieee.org/app/publication-recommendations` | The IEEE Publication Recommender. You paste a title and abstract and it suggests which IEEE journal fits. A venue-picking tool, not a submission system |

The Recommender is optional. If you want a second opinion on whether T-ITS is the
right venue, paste the title and abstract from this file into it before you submit.

---

## Before you upload — check two details in the biography

The biography now reads:

> Hannan Muzammil received the B.S. degree in computer science from the University
> of Management and Technology, Lahore, Pakistan, in 2025. He worked as a freelance
> developer before founding Hannsoft, where he is Chief Executive Officer. His
> interests include vehicular and Android application security, machine learning and
> deep learning, and research reproducibility.

Two things in it came from me, not from you, so confirm them:

1. **"B.S. degree"** — you said you graduated in computer science in 2025 without
   naming the degree. Change it if it was a B.Sc., BSCS or anything else.
2. **"Lahore"** — you said UMT Pakistan; I used UMT's main campus. Change it if you
   studied at another campus.

To edit: the `IEEEbiographynophoto` block at the end of `manuscript.tex`, or
`workspace/paper/make_journal.py` in the working tree if you want the change to
survive a rebuild. Recompile and re-upload.

One more thing I chose not to guess: IEEE author footnotes usually carry a city and
country for the affiliation. The footnote currently reads "H. Muzammil is with
Hannsoft" with no location, because I do not know where Hannsoft is registered. Add
it if you want the conventional form.

Page length is settled, and it is why the manuscript was cut to ten. T-ITS gives
Regular Papers a suggested length of **10 pages**, allows up to 6 more, and charges
**$175 per page over the suggested length** on acceptance. This manuscript is
exactly 10 pages, so it carries no overlength charge. Keep it there: adding half a
page of biography would cost $175.

---

## Files in this folder

| File | Role at submission |
|---|---|
| `manuscript.pdf` | **The PDF you upload.** 10 pages, IEEEtran journal class |
| `manuscript.tex` | LaTeX source. Upload with it, or hold until acceptance |
| `fig_ablation.pdf` | Fig. 1 — timing versus geometric evidence |
| `fig_decode.pdf` | Fig. 2 — pseudonym decoding against its control |
| `fig_prevalence.pdf` | Fig. 3 — metric behaviour across attacker prevalence |

The source compiles from this folder alone, with no other files:

```bash
tectonic -X compile manuscript.tex
```

That was verified: the PDF built from this folder is text-identical to the one
built in the project tree.

---

## The submission form, field by field

**Type:** Regular Paper (suggested length 10 pages; this manuscript is 10).

**Title:**
```
What VeReMi Measures: Structural Artefacts in VANET Misbehaviour Detection Benchmarks
```

**Running head / short title:**
```
Muzammil: What VeReMi Measures
```

**Abstract** (195 words, plain text, paste as-is):
```
One untrained scalar exceeds AUC 0.99 on six of eight VeReMi archives. That scalar
is raw message count, never a claimed position. These archives are the field's main
shared misbehaviour benchmark. Reported detection rates on them sit between 94% and
99.9%. We audit them by measurement: every claim is re-derived from source. We
examine the eight Sybil archives of the extension. Pseudonyms encode the true sender
in 86.5-100% of identity pairs. No benign vehicle in them emits a second pseudonym.
Attacker prevalence is 30.0% of vehicles in all eight. Attacker identities form
68-98% of the identity population. Ground-truth files list up to 28 times fewer
identities than receivers observe. We then run one detector through seven
progressively stricter protocols. Removing ground-truth aggregation is associated
with a 0.060 fall. We evaluate the pseudonym feature in its original
representation. The lowest stable evaluable prevalence is 3% dense, 5% sparse.
Ranking metrics barely move with prevalence; precision metrics collapse. We show
VeReMi 2018 cannot validate signal-strength position verification. Its measured
path-loss exponent is 0.93 against a free-space two. That detector then reaches AUC
0.530, barely above chance. We release code, controls and a reporting checklist for
future work.
```

**Keywords:** VANET, misbehaviour detection, Sybil attack, benchmarking,
reproducibility, VeReMi

**Author:**

| Field | Value |
|---|---|
| Given names | Hannan |
| Family name | Muzammil |
| Email | abdullhannan0311@gmail.com |
| Affiliation | Hannsoft |
| Country | Pakistan |
| ORCID | 0009-0000-7502-2755 |
| Corresponding author | Yes |

**Funding:** none. The paper states this in the first author footnote.

**Conflicts of interest:** none.

**Data availability / artefact:** the replication package is archived at
<https://doi.org/10.5281/zenodo.22397725> and mirrored at
<https://github.com/han023/veremi-audit>. The paper's Availability section cites
the DOI, not the repository, because a repository URL is not archival.

**Prior publication:** none. This work has not been published or submitted
elsewhere.

---

## The submission declarations

The portal asks you to tick these. Where a statement is checkable against the
manuscript, here is what was checked.

**Sole submission, not published or submitted elsewhere.** True, with one thing to
be aware of rather than to worry about. The replication package on Zenodo and
GitHub contains the manuscript PDF, so the paper is publicly posted. The
declaration explicitly permits preprint posting, and IEEE policy allows it. Two
consequences: say so if the portal offers a preprint field, and after acceptance
IEEE asks you to add the DOI and copyright notice to the posted version. If you
would rather not post it at all, remove the two PDFs from the archive and deposit
only code and data.

**All co-authors agree.** Single-author paper. Trivially satisfied.

**Contact details may be shared with IEEE partners.** Your call, nothing to check.

**Prepared per the journal's style and format.** Checked: IEEEtran journal class,
10 pages against a 10-page suggested length, 195-word abstract against a 200-word
cap, IEEE keywords block, author footnotes with affiliation and ORCID, an
IEEEbiographynophoto, and 36 references in IEEE style with no uncited entry and no
undefined citation.

**The three peer-review policy statements.** You have to read these yourself. What
the manuscript does: it is submitted to one venue only; it quotes no source text
and cites 36 works for every attributed claim; and the electronic-posting point is
the Zenodo/GitHub copy discussed above.

**No Lena image.** Verified mechanically, not by eye. Every figure is vector output
from matplotlib, and the manuscript PDF contains **zero embedded raster images** of
any kind. There is no photograph in the paper, so the Lena image cannot be in it.

**All listed authors meet the IEEE authorship criteria.** Single author, who did
the work, wrote the paper and approves the final version. All three criteria met.

---

## Cover letter

Paste into the cover-letter box, or attach as its own file.

```
Dear Editor,

Please consider the enclosed manuscript, "What VeReMi Measures: Structural
Artefacts in VANET Misbehaviour Detection Benchmarks", for publication as a
Regular Paper in IEEE Transactions on Intelligent Transportation Systems.

The VeReMi archives are the main shared benchmark for vehicular misbehaviour
detection, and reported detection rates on them now sit between 94% and 99.9%.
This paper asks what those numbers are measuring. Rather than proposing another
detector, it audits the benchmarks themselves by measurement, re-deriving every
claim from the raw archives.

The central findings are that a single untrained statistic, raw message count,
exceeds AUC 0.99 on six of the eight Sybil archives without training, linkage or
any physical reasoning; that pseudonyms encode the true sender in 86.5 to 100% of
identity pairs; and that attacker prevalence is fixed at 30% of vehicles in every
archive, roughly an order of magnitude above the deployment range the literature
motivates. Running one detector through seven progressively stricter evaluation
protocols moves AUC from 0.998 to 0.843, and an order-free single-factor analysis
agrees on which advantage dominates. We also show that VeReMi 2018 cannot validate
the signal-strength position-verification family at all: its measured path-loss
exponent is 0.93 against a free-space two, and the detector reaches AUC 0.530.

We extend the measurements to VeReMi NextGen. The identity leak is genuinely
repaired there; the message-rate shortcut is not.

The paper is deliberately narrow in stance. It does not allege that any prior
result was obtained improperly, and several of the protocol choices it examines are
choices we made ourselves before correcting them. Its claim is that these
benchmarks substantially simplify the intended deployment task, and that this is
measurable.

The complete replication package is archived at doi:10.5281/zenodo.22397725. It
regenerates every number in the paper: tables are emitted from result files rather
than typed, and a claim checker re-derives each printed value from its source, both
inside a container build so a failing build is a failing artefact.

The manuscript is original, is not under consideration elsewhere, and has no
funding or competing interests to declare.

Thank you for your consideration.

Hannan Muzammil
Hannsoft
ORCID 0009-0000-7502-2755
abdullhannan0311@gmail.com
```

---

## Suggested reviewer expertise

The portal may ask. Areas that fit, rather than named people:

- VANET / V2X misbehaviour and Sybil detection
- Benchmark and dataset auditing, evaluation methodology
- Reproducibility and evaluation pitfalls in security machine learning
- Vehicular network simulation (VEINS, SUMO, F2MD)

Do **not** suggest authors of the VeReMi releases or of papers the manuscript
discusses; the editor will read that as a conflict.

---

## Pre-flight checklist

- [ ] Degree name and campus confirmed in the biography
- [ ] Still exactly 10 pages after any biography edit (11 costs $175)
- [ ] `manuscript.pdf` opens, is 10 pages, figures render
- [ ] Submitting at ieee.atyponrex.com/journal/t-its, not ScholarOne
- [ ] ORCID entered in the portal, matching the paper
- [ ] Abstract pasted as plain text, no LaTeX escapes left
- [ ] Zenodo record published and resolving before submission
- [ ] Cover letter attached or pasted

The Zenodo record must resolve before you submit, because the paper cites it.

---

## After submission

Do not edit the paper further. Any change makes the archived code a different
version from the one the PDF cites. If a revision becomes necessary, publish a new
Zenodo version and cite that version's DOI in the revision. Zenodo versions share a
concept DOI, so the citation stays coherent.

IEEE will ask for the copyright form on acceptance, and for source files if you
only uploaded the PDF. Both are in this folder. **Final files for an accepted paper
go to ScholarOne** at `mc.manuscriptcentral.com/t-its` — that is the one stage where
that URL is the right one.
