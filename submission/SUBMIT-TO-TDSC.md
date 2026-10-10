# Submitting to IEEE Transactions on Dependable and Secure Computing

**Status:** prepared, not yet submitted.

## Why here, after two desk rejections

T-ITS and Vehicular Communications both returned the paper without review, and
both gave the same reason from different directions. T-ITS: "it does not have a
strong focus on a transportation system/network." VEHCOM: the contribution "in
terms of vehicular communications" is not significant enough. Neither disputed a
measurement.

The mistake was mine and it was a framing mistake, not a venue-shopping problem.
A paper that audits how a field evaluates itself is not a contribution to that
field's methods, so a domain journal has nothing to weigh it against. The paper's
own models — Sommer and Paxson, Arp et al. — are security-venue papers. It should
have gone to a security venue from the start.

TDSC is the right class of venue:

| Constraint | How it is met |
|---|---|
| No cost | Hybrid journal. The traditional route carries no charge. Open access is $2,800 and must not be selected |
| Page limit | Regular papers run to **12 formatted pages including references and the biography**. Our build is **11**, so no overlength charge |
| Scope | Dependability and security, with evaluation, measurement and benchmarking named among its evaluation topics |
| Precedent | TDSC publishes dataset and evaluation work for security, e.g. Landauer et al., "Maintainable Log Datasets for Evaluation of Intrusion Detection Systems," TDSC 2023, doi:10.1109/TDSC.2022.3201582 |

Overlength beyond 12 pages is a **Mandatory Overlength Page Charge of $220 per
page**, assessed on the final layout rather than at submission. The 11-page build
leaves one page of margin for copy-editing reflow.

## What changed in the paper

The framing, and only the framing. No measurement, table or figure moved, and
`check_claims.py` still passes all 316 assertions.

| Was | Now |
|---|---|
| Title: "What VeReMi Measures: Structural Artefacts in VANET Misbehaviour Detection Benchmarks" | "Auditing a Security Benchmark by Measurement: Structural Artefacts in VANET Misbehaviour Detection" |
| Abstract opened on the AUC headline | Opens on how security ML is evaluated, then reaches the case |
| Keywords led with VANET | Lead with benchmarking, evaluation methodology, security machine learning |
| Introduction opened on Sybil attacks in vehicular networks | Opens on benchmarks carrying a field's claims, states the gap, states the method, then introduces the case |
| Contributions led with the six artefacts | Lead with the cascade and the seven reporting rules, which are benchmark-neutral |
| Nothing said the method outlives VeReMi | New Section XI subsection, "What transfers beyond this benchmark" |

The abstract is **190 words**, inside the Computer Society's 100–200 range.

## Before you submit: confirm the submission route

The Computer Society historically used ScholarOne at
`mc.manuscriptcentral.com/cs-ieee`, and migrated its periodicals to the **IEEE
Author Portal** around the end of December 2024, with the portal still writing
into the ScholarOne review database. Both URLs refuse automated requests, so
**take the link from the journal's own "Submit a manuscript" button** rather than
typing one in:

<https://www.computer.org/csdl/journal/tq>

This is the same trap as T-ITS, where the society page sent new submissions to the
Author Portal while `mc.manuscriptcentral.com/t-its` handled only final files of
accepted papers. Do not assume; click through from the journal page.

## Form answers

**Paper type:** Regular Paper.

**Title**
```
Auditing a Security Benchmark by Measurement: Structural Artefacts in VANET Misbehaviour Detection
```

**Abstract:** 190 words. Paste as plain text from the manuscript's abstract
environment; there are no LaTeX escapes except the percent signs.

**Keywords:** benchmarking; evaluation methodology; security machine learning;
misbehaviour detection; VANET; reproducibility; VeReMi.

**Author:** Hannan Muzammil, given name Hannan, family name Muzammil. Hannsoft,
Township, Lahore 54700, Punjab, Pakistan. abdullhannan0311@gmail.com,
ORCID 0009-0000-7502-2755, corresponding author.

**Funding:** none. Stated in the first author footnote.

**Competing interests:** none. Stated in the first author footnote.

**Data availability:** <https://doi.org/10.5281/zenodo.22397725>.

**Open access:** choose the **traditional** route. Selecting open access commits
you to $2,800.

**Previous submission:** disclose both. T-ITS and Vehicular Communications each
returned it without review on scope and significance, with no reviewer comments
and no question raised about the methods. Two scope rejections carry no stigma and
volunteering them is better than having them surface later.

**Suggested reviewer expertise:** machine learning evaluation and pitfalls in
computer security; benchmark and dataset auditing; reproducibility in empirical
security; vehicular and V2X security. Avoid anyone connected to the VeReMi
releases or to papers the manuscript discusses.

## Files to upload

Rebuild first:

```bash
python workspace/paper/assemble.py
python workspace/paper/make_journal.py
cd workspace/paper && ../tools/tectonic.exe -X compile veremi_audit_journal.tex --outdir .
```

| File | Slot |
|---|---|
| `veremi_audit_journal.pdf` | Manuscript, 11 pages |
| `veremi_audit_journal.tex` + `IEEEtran.cls` + the three figure PDFs | LaTeX source archive, if the portal asks for source |

## Checks that passed on this build

- `check_claims.py`: 316 assertions, 0 failed
- `check_sentences.py`: 688 sentences, 0 over 12 words
- `check_refs.py`: 37 references, 30% from 2024 or later, no uncited or undefined
  entries, no mangled control sequences, no malformed DOIs
- 11 pages, inside the 12-page limit including references and biography
- Running heads alternate correctly: journal name on even pages, author and short
  title on odd

## Before submitting

- [ ] Submission URL taken from the journal page's own button, not typed
- [ ] **Traditional** route selected, not open access
- [ ] Abstract pasted as plain text, still 190 words
- [ ] Both previous submissions disclosed
- [ ] `https://doi.org/10.5281/zenodo.22397725` resolves
