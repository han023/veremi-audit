# Submission record

## Status

| Venue | Submitted | Outcome |
|---|---|---|
| IEEE Trans. Intelligent Transportation Systems | 2026-09-06 | Desk rejected 2026-09-27, out of scope |
| Vehicular Communications (Elsevier) | 2026-10-06 | Desk rejected 2026-10-09, significance |
| IEEE Trans. Dependable and Secure Computing | prepared 2026-10-10 | not yet submitted |

## The reframe, 2026-10-10

Both rejections were a framing failure rather than two unlucky venue picks, so the
paper was reframed before being sent anywhere else. It now leads with the audit
method and treats VeReMi as the case study: new title, an abstract and
introduction that open on how security machine learning is evaluated, contributions
that put the cascade and the reporting rules first, and a new Section XI
subsection stating what transfers beyond this benchmark.

No measurement, table or figure changed. `check_claims.py` passes all 316
assertions on the reframed source, `check_sentences.py` reports none over twelve
words, and the journal build is 11 pages against TDSC's 12-page limit.

See [`SUBMIT-TO-TDSC.md`](SUBMIT-TO-TDSC.md), which also records what was verified
about the venue before choosing it: the traditional route is free, open access is
$2,800 and must not be selected, overlength beyond 12 pages is $220 per page, and
the submission URL must be taken from the journal page's own button because the
Computer Society moved its periodicals to the IEEE Author Portal.

### Why not ACM

ACM TOPS and ACM DTRAP are the venues most receptive to this kind of audit, and
McHugh's critique of the DARPA intrusion-detection evaluations — the closest
precedent for this paper — appeared in ACM TISSEC, now TOPS. They were ruled out on
cost. ACM became fully open access on 1 January 2026, so an APC applies unless the
corresponding author's institution is in ACM Open or the country qualifies for a
waiver. Pakistan is World Bank lower-middle-income, which earns a **50% discount,
not a waiver**; Hannsoft is not an ACM Open institution; and ACM states explicitly
that being an independent consultant without an affiliated institution is not by
itself a demonstration of financial hardship. That leaves a real bill, so ACM
fails the no-cost constraint.

Vehicular Communications returned it without review as **VEHCOM-D-26-01393**:

> The novelty and scientific contributions of this paper in terms of vehicular
> communications do not appear to be significant enough for further consideration
> by the journal.

No reviewer comments again. Read alongside the T-ITS letter, the two say the same
thing from different directions, and the qualifier "in terms of vehicular
communications" is the whole point. Neither editor disputed a measurement. Both
judged the paper as a contribution to their domain, and a critique of how a domain
evaluates itself does not advance that domain's methods.

The lesson for venue choice: a scope list says what a journal accepts, not what it
values. Both journals list security in scope. Neither values an evaluation audit.
This paper's peers are Sommer and Paxson, and Arp et al., and both of those
appeared at security venues rather than domain journals.

Submitted to Vehicular Communications as a Full Length Article through Editorial
Manager at <https://www.editorialmanager.com/vehcom/>, subscription route, no
article publishing charge. Classifications: security and privacy; vehicle to
vehicle and vehicle to infrastructure communications; artificial intelligence and
machine learning; protocol design, testing and verification. Deliberately not
"intelligent transportation systems", which is the framing T-ITS rejected.

The submitted source is `workspace/paper/veremi_audit_elsevier.tex`, built by
`make_elsevier.py`. Published timings for this journal are roughly 6 days to the
desk decision, 65 days to a post-review decision and 145 days to acceptance.

T-ITS returned it without review as **T-ITS-26-09-4944**. The editor's reason was
scope alone, quoted in full because it is useful to anyone choosing a venue for
this kind of work:

> The paper is related to the problem of security of communication networks. The
> paper is out of the scope of the journal as it does not have a strong focus on a
> transportation system/network. In particular, the dynamics of an underlying
> transportation system are not explicitly accounted for in algorithm
> design/analysis/validation.

No reviewer comments, and nothing about the methods or results was questioned. The
objection is structural and correct: the paper audits datasets and evaluation
protocol for a security problem, and it models no traffic dynamics. That is a
mismatch with the journal, not a defect in the work.

The manuscript was submitted as a Regular Paper through the IEEE Author Portal at
<https://ieee.atyponrex.com/journal/t-its>.

Two notes for anyone following the same route, because both cost time to work out:

- New T-ITS submissions go to the **Author Portal**, not ScholarOne.
  `mc.manuscriptcentral.com/t-its` handles only final files of accepted papers, and
  `publishingportal.ieee.org/app/publication-recommendations` is a venue
  recommender rather than a submission system.
- Regular Papers have a suggested length of **10 pages**, with up to 6 more allowed
  at **$175 per page**. `workspace/paper/make_journal.py` cuts the conference
  variant to exactly 10.

| File | What it holds |
|---|---|
| `portal-upload-guide.md` | Which file belongs in which portal slot, and why each optional slot was left empty |
| `submission-fields.md` | The form fields as submitted: abstract as plain text, keywords, methodologies, applications, and what each declaration was checked against |

The uploaded files themselves are build outputs under `workspace/release/`, which
is not tracked. Rebuild them with:

```bash
python workspace/paper/assemble.py
python workspace/paper/make_journal.py
python workspace/make_release.py --selftest
```

## What was checked before submitting

- The LaTeX archive compiles to 10 pages from an empty directory, with `IEEEtran.cls`
  bundled so the portal cannot typeset it against a different class version.
- The portal's generated reviewer PDF was diffed against the local build. The only
  differences are the line numbers and page footers the portal adds; no manuscript
  text changed, and all three figures render.
- No embedded raster image appears anywhere in the manuscript, so the Lena
  declaration holds by construction rather than by inspection.
