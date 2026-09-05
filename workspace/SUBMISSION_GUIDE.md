# Where to submit, and how

Checked 6 September 2026. Deadlines move; verify each on the venue's own site
before acting. Where a date has passed I say so rather than leaving it to be found.

---

## The short answer

**Submit to IEEE T-ITS now.** It is a journal with rolling submission, it already
publishes this literature, the paper is the right length, and it is the only strong
venue currently open. The two conference options both closed for their 2026 cycles.

---

## Venue status, as of today

| Venue | Status today | Fit |
|---|---|---|
| **IEEE T-ITS** | **open, rolling** | strong — publishes this literature, length fits |
| ACM WiSec 2027 | cycle 1 expected ~Nov 2026 | strong — measurement work in scope |
| USENIX VehicleSec '27 | CFP not yet posted | strong topic fit, tight length |
| IEEE TIFS | open, rolling | wants a defence, not only an audit |

### What changed since the earlier notes

**VehicleSec is no longer NDSS-colocated.** It moved to USENIX, and VehicleSec '26
ran 10–11 August 2026 in Baltimore. The earlier instruction in these notes to swap
in `\documentclass{ndss}` is obsolete. If you target VehicleSec '27, use the USENIX
template, not the NDSS one.

**ACM WiSec 2026 is closed.** Both cycles have passed: cycle 1 closed 18 November
2025, cycle 2 closed 3 March 2026. WiSec 2027 will most likely open a first cycle
around November 2026.

---

## Option 1 — IEEE T-ITS (recommended, open now)

**Why this one.** T-ITS publishes the exact literature this paper audits, including
several works in our own corpus. A measurement and evaluation-methodology paper is
in scope. Rolling submission means no waiting. Length is comfortable.

**Length.** Regular papers are "normally about 10 TRANSACTIONS pages or shorter",
with up to 6 additional pages permitted. Over-length charges are **$175 per extra
page** after acceptance. Our 11 pages in IEEEtran conference format will reflow when
converted to the T-ITS journal style, so check the page count after conversion and
budget for one or two over-length pages.

**Format.** IEEE journal template. Our source is already `IEEEtran`, so the change
is the document class options, not a rewrite:

```latex
% from
\documentclass[conference]{IEEEtran}
% to
\documentclass[journal]{IEEEtran}
```

Then recompile and re-check the page count. Expect tables to reflow; run the three
checkers afterwards because a reflow can break a float placement, not a number.

**Submission.** IEEE Author Portal. Have ready: the PDF, author and affiliation
details, ORCID, a conflict-of-interest declaration, and the artefact DOI.

**What reviewers will ask.** Prepare answers for:
- why a single detector family — §III-D states it, and the logistic cross-check in §VII-A answers it;
- whether the corpus is systematic — §III-A says plainly it is not, and why;
- whether NextGen invalidates the audit — §X answers it directly, both ways.

---

## Option 2 — ACM WiSec 2027 (opens ~November 2026)

**Length.** At most **10 pages** in double-column ACM format, `sigconf` option,
excluding bibliography and well-marked appendices, and **up to 12 pages in total**.

Our body runs to roughly nine and a half pages before the bibliography, so it should
fit. Confirm after conversion, because ACM `sigconf` sets differently from IEEEtran.

**Format.** ACM proceedings template, `sigconf` option, US Letter. This is a real
conversion, not a class swap: rewrite the `\author` block, and check every table
because column widths differ.

**Submission.** HotCRP. WiSec runs **artifact evaluation** after acceptance, which
this paper is unusually well placed for — the artefact already self-tests.

**Watch the dates.** WiSec 2026 stated that deadlines were firm and that there
would be no extensions. Assume the same for 2027.

---

## Option 3 — USENIX VehicleSec '27 (CFP not yet posted)

Best topical fit of the three: its audience is exactly the community that cites
VeReMi. The constraint is length — VehicleSec favours shorter papers, and at 11
pages this would need real cutting.

**If you go here, cut in this order:** the sensitivity table (§VIII) to an appendix,
then the corpus reporting table (§IV), then the dataset comparison (Table II). Keep
the cascade, the decode experiment and the NextGen section; they are the paper.

---

## Before you submit anywhere

1. **Deposit the artefact first.** The paper cites its DOI, so Zenodo comes before
   submission. See `ZENODO_RECORD.md`.
2. **Convert the template**, then recompile and re-run all three checkers. A reflow
   can break float placement even when no number changes.
3. **Check the page limit after conversion**, not before.
4. **Fill the author block** with your final affiliation and ORCID.
5. **Anonymise if required.** T-ITS is single-blind, so no change. WiSec and
   VehicleSec are double-blind: remove the author block, and remove the artefact URL
   from Availability, replacing it with a note that it will be provided on acceptance.

The double-blind point matters and is easy to miss. Our §Availability names a DOI
that resolves to a record carrying your name.

---

## What to say in the cover letter

Three sentences do the work:

> This paper audits the VeReMi benchmarks by measurement rather than by reading.
> It documents six structural artefacts, shows a single untrained scalar solves six
> of eight archives, and reports which of them persist into VeReMi NextGen.
> The complete replication package is deposited at [DOI] and verifies itself.

Do not oversell. The paper's credibility rests on what it declines to claim, and a
cover letter that overstates undercuts that.
