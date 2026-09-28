# Submitting to Vehicular Communications (Elsevier)

Journal: <https://www.sciencedirect.com/journal/vehicular-communications>
Submit through Editorial Manager via the journal's "Submit your article" link.
Sign in with your ORCID so the submission links to your record.

## Why here, and not Computers & Security

C&S was the earlier plan and it was wrong. Their aims and scope carry this:

> **AI and ML:** As of early 2024, we have instituted a moratorium on consideration
> of submissions that feature AI or ML as significant components.

This paper runs random forests and logistic regression through a seven-stage
cascade and reports AUC throughout. Whether that counts as "featuring ML" is
arguable, but at desk screening ambiguity resolves against the author, and a second
scope rejection costs weeks. C&S also excludes cryptology "including blockchains",
which our related work touches.

Vehicular Communications lists **"Security issues and countermeasures"** in scope,
with no AI/ML moratorium and no cryptology exclusion. It is free under the
subscription route, Q1, impact factor 5.7, CiteScore 14.4. The published figures
also correct an earlier overestimate: C&S is 6.8, not the ~8.0 that third-party
aggregators report, so the gap that would have justified the risk is small.

## The source, not a PDF

The guide is explicit: **"A PDF is not an acceptable source file."** So the
manuscript is submitted as LaTeX. Double-column is allowed for LaTeX but Elsevier's
single-column `preprint` layout is the norm for review, and that is what this uses.

The manuscript was converted from IEEEtran to `elsarticle`, which is not a class
swap. What changed, and why:

| Change | Reason |
|---|---|
| `elsarticle`, single column | Elsevier's submission format |
| Sections numbered 1, 1.1, 1.1.1 | Required. IEEEtran gives I, II and A, B |
| Full postal address on the title page | Required, including country |
| CRediT statement | Required |
| Funding statement | Required, using Elsevier's own "no funding" wording |
| Declaration of competing interest | Required as a section, not only a footnote |
| Generative AI declaration | Required when AI tools were used in preparation |
| Data availability section | Points at the Zenodo DOI |
| Fuller text restored | The T-ITS cuts existed only to reach ten pages before per-page charges. Elsevier sets no page limit, so Table 1, the full corpus section and the uncompressed discussion are back |

32 pages in this layout is normal and not a problem: Elsevier judges length by
words, and the manuscript is about 8,100.

**Verified:** unpacked into an empty directory with only the four figures beside
it, `manuscript.tex` compiles to a PDF identical to the reference build.

## Files here

| File | Where it goes |
|---|---|
| `manuscript.tex` | Manuscript, file type **Manuscript** |
| `fig_abstract.pdf` | Figure 1 |
| `fig_decode.pdf` | Figure 2 |
| `fig_ablation.pdf` | Figure 3 |
| `fig_prevalence.pdf` | Figure 4 |
| `highlights.docx` | **Highlights**. Editable, as required, with "highlights" in the filename |
| `cover-letter.pdf` | Cover Letter |
| `manuscript-preview.pdf` | For you to read. **Do not upload** — the system builds its own PDF from the source |

## One file you must generate yourself

**Declaration of competing interests.** The guide says the declarations tool
"should always be completed", and the resulting **Word file (.doc/.docx)** is what
gets uploaded. It has to come from Elsevier's tool, so I cannot produce it.

Go to <https://declarations.elsevier.com/>, select **"I have nothing to declare"**,
download the Word file, and upload it. Do not convert it to PDF.

The manuscript already carries the matching statement as its own section, which the
guide also requires.

## Form answers

**Article type:** Full Length Article.

**Title:**
```
What VeReMi Measures: Structural Artefacts in VANET Misbehaviour Detection Benchmarks
```

**Abstract:** 195 words, within the 250 limit. Paste from
`../ieee_upload/submission-fields.md`; it is unchanged.

**Keywords:** exactly these six. The journal allows 1 to 7, so do **not** add the
two extras suggested for the IEEE submission, which would make eight.
```
VANET; misbehaviour detection; Sybil attack; benchmarking; reproducibility; VeReMi
```

**Author:** Hannan Muzammil, given name Hannan, family name Muzammil.
Hannsoft, Township, Lahore 54700, Punjab, Pakistan.
abdullhannan0311@gmail.com, ORCID 0009-0000-7502-2755, corresponding author.

**Funding:** none. The manuscript uses Elsevier's recommended sentence.

**Data availability:** choose the option for data in a public repository and give:
```
https://doi.org/10.5281/zenodo.22397725
```

**Generative AI:** declared in the manuscript, in the section before the
references, using Elsevier's template.

**Preprint:** the Zenodo archive holds a copy of the manuscript. Elsevier states
that preprint sharing "will not count as prior publication". The cover letter
discloses it.

**Previous submission:** the cover letter states that T-ITS returned the paper
without review as out of scope, with no reviewer comments. Say so if asked.

**SSRN preprint offer:** the submission flow may offer to post your manuscript to
SSRN. Declining costs nothing, since the Zenodo record already serves that purpose.
Accepting is also harmless and adds a second DOI.

## Before submitting

- [ ] Competing-interests Word file generated from Elsevier's tool and uploaded
- [ ] Open access question answered **subscription**, not open access
- [ ] Six keywords, not eight
- [ ] `https://doi.org/10.5281/zenodo.22397725` resolves
- [ ] Read `manuscript-preview.pdf` through once, then do not upload it
