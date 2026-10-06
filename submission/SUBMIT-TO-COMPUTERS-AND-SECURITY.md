> **Superseded, kept for the record.** The paper went to Vehicular Communications
> instead; see `SUBMIT-TO-VEHICULAR-COMMUNICATIONS.md`. Computers & Security was
> ruled out after reading their aims and scope, which carry a moratorium in force
> since early 2024 on submissions featuring AI or ML as significant components.
> This file is kept because that finding, and the impact-factor correction below,
> are worth knowing before anyone considers the venue again. Do not follow its
> steps.

# Submitting to Computers & Security (Elsevier)

Journal home: <https://www.sciencedirect.com/journal/computers-and-security>
Submit through Editorial Manager, reached from the journal's "Submit your article"
link. Sign in with your ORCID so the submission links to your record.

## Why this journal

It satisfies all three of your constraints at once, which nothing else on the
shortlist did.

| Constraint | How it is met |
|---|---|
| No cost | Hybrid journal. Elsevier's own wording: "No publication fee charged to authors under the subscription route." The $3,190 APC applies only if you *choose* open access. Do not choose it. |
| Visibility and profile | Impact factor around 8.0, Q1, and the longest-established journal in computer security. The highest impact factor of any free option found. |
| Speed | Initial screening in about 5 days, and no reformatting needed before submitting. |

Scope risk is nil. T-ITS rejected the paper with the words "the paper is related to
the problem of security of communication networks" — which is this journal's remit
stated for us. The work also sits in a line this readership knows: Sommer and
Paxson on machine learning in security evaluation, and Arp et al. on the pitfalls
that produce inflated numbers.

**Fallback if declined:** *Vehicular Communications* (Elsevier), also hybrid and
free under the subscription route, IF 6.5, Q1, published median of 65 days to a
post-review decision. Its scope is VANET specifically, so the fit is if anything
tighter, at a lower impact factor.

## Submit the manuscript as it is

Elsevier's "Your Paper Your Way" policy applies at initial submission: one file, in
any format or layout a referee can read. The IEEEtran two-column PDF is fine.
Formatting to Elsevier's `elsarticle` class is only needed after acceptance.

That is why this can go out today rather than after a reformatting pass.

## Files here

| File | Where it goes |
|---|---|
| `manuscript.pdf` | Manuscript. 10 pages, submitted as-is |
| `cover-letter-cose.pdf` | Cover letter |
| `declaration-of-interest.pdf` | Declaration of Interest |
| `highlights.txt` | Highlights, 5 bullets, each within the 85-character limit |

## Form answers

**Article type:** Research paper (full-length article).

**Title, abstract, keywords:** as in `../ieee_upload/submission-fields.md`. The
195-word abstract pastes unchanged.

**Author:** Hannan Muzammil, Hannsoft, Pakistan, ORCID 0009-0000-7502-2755,
corresponding author. Given name Hannan, family name Muzammil.

**Declaration of interest:** none. The statement is in the manuscript's first
author footnote and in `declaration-of-interest.pdf`.

**Funding:** none.

**Data availability:** Elsevier asks you to pick a statement. Choose the option
saying data is available in a public repository, and give:

```
The replication package is publicly archived at https://doi.org/10.5281/zenodo.22397725
```

**Declaration of generative AI:** Elsevier requires a statement if generative AI
was used in preparing the work. Answer honestly according to how you used it; the
policy concerns the writing of the manuscript, not software the research itself
employed.

**Preprint:** the Zenodo archive contains a copy of the manuscript. Elsevier
permits preprint posting, and the cover letter discloses it. Declare it if the
form asks.

**Previous submission:** the cover letter states plainly that T-ITS returned the
paper without review as out of scope, with no reviewer comments and no question
raised about the methods. Volunteering this is better than having it surface
later, and a scope rejection carries no stigma.

## Suggested reviewer expertise

Areas rather than names, and avoid anyone connected to the VeReMi releases or to
the papers the manuscript discusses:

- Machine learning evaluation and pitfalls in computer security
- Vehicular network and V2X security
- Benchmark and dataset auditing, reproducibility in empirical security

## Before submitting

- [ ] Choose the **subscription** route, not open access, or you will be billed $3,190
- [ ] `https://doi.org/10.5281/zenodo.22397725` resolves
- [ ] ORCID entered and matching the manuscript
- [ ] Highlights pasted, still within 85 characters each
- [ ] Abstract pasted as plain text with no LaTeX escapes

## After acceptance

Reformat to `elsarticle`, and post the accepted manuscript under Elsevier's green
open access terms so the work stays free to read. The Zenodo record already serves
that purpose.
