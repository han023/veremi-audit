# Submission record

## Status

| Venue | Submitted | Outcome |
|---|---|---|
| IEEE Trans. Intelligent Transportation Systems | 2026-09-06 | Desk rejected 2026-09-27, out of scope |
| Vehicular Communications (Elsevier) | 2026-10-06 | Under review |

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
