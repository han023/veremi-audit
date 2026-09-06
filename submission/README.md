# Submission record

The manuscript was submitted to **IEEE Transactions on Intelligent Transportation
Systems** as a Regular Paper, through the IEEE Author Portal at
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
