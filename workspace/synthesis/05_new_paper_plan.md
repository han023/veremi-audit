# Paper Plan (v4 — after four verification rounds, deep reading, and a dataset audit)

**What changed in v4.** Round 5 stopped searching and started *measuring the data*. The audit
(`08_dataset_audit.md`) found four unreported structural properties of the VeReMi-family benchmarks —
identifier leakage (87–100 %), no pseudonym changes for honest vehicles, no RSSI field, and ~30 % attacker
prevalence — none of which appears in any prior work (probes for VANET dataset identifier leakage and for
VeReMi + pseudonym change both return **0 works**). That makes the dataset audit itself the strongest and
fastest paper, and it changes the Linkability paper's method (a synthetic pseudonym-change layer is now
required, and becomes its swept parameter).

Evidence chain: `06_gap_verification.md` (4 rounds of probes + deep reading) · `07_feasibility.md` (schema,
buildability) · `08_dataset_audit.md` (original measurements).

---

# ★ RECOMMENDED FIRST — Paper 0: *"What VeReMi Measures: Structural Artefacts in the VANET Misbehaviour Benchmarks"*

**Type:** dataset audit / reproducibility paper · **Venue:** VehicleSec, ACM WiSec, IEEE TITS, or a
data-track (Scientific Data / Data in Brief) · **Effort:** 4–6 weeks · **Risk:** low — the core findings are
already measured and reproducible from `08_dataset_audit.md`.

**Thesis.** The benchmark the field trusts contains shortcuts that make its central task easier than the real
one, and omits the axis (pseudonym change) on which V2X privacy depends. Reported 94–99.9 % detection is, in
part, a property of the data.

### Contributions (all already evidenced)
1. **Identifier leakage**: pseudonyms embed the true sender id in 87–100 % of records; the Sybil grouping
   task is solvable by string arithmetic, and per-`sender` aggregation hands models the identity partition a
   real receiver must infer.
2. **No pseudonym change for benign vehicles** (1 847 senders : 1 847 pseudonyms) — the privacy axis is absent.
3. **No RSSI field** — a third of the literature cannot be benchmarked on the standard dataset.
4. **~30 % attacker prevalence** vs the 3 % regime that already causes +20 % travel time (Söderhäll 2025).
5. **Family variance**: 2–7 identities per attacker in GridSybil vs 100 in the DoS-Sybil families; papers
   rarely say which they used.
6. **Quantified impact**: re-run 2–3 representative detectors with and without the leakage controls
   (pseudonym re-mapping; pseudonym-only aggregation; prevalence sweep) and report how much performance was
   dataset artefact. *This is the experiment that turns the audit into a result.*
7. **Fixes**: a released patch script producing a de-leaked, prevalence-controlled, pseudonym-change-layered
   variant of the benchmark.

### Why it is the best first move
- The findings exist **now**, measured on md5-verified data — the remaining work is one controlled experiment
  plus writing.
- It is a prerequisite for every other paper in this plan: any benchmark or detector result built on VeReMi
  without these controls is contestable.
- Verified unreported: 0 prior works on either artefact.
- It is the kind of paper the whole subfield must cite.

**Main risk:** a reviewer says "the pseudonym format is a known simulator convention, not a claim". Answer in
the paper: the point is not that the convention is wrong, but that the *field consumes these files as ML
features and per-node aggregations*, and nobody has measured the resulting inflation. Finding 6 makes the
distinction cleanly — the physics is realistic, the identifiers are not.

---

# Paper 1 (second, or merge into Paper 0): *"The Linkability Dilemma: Sybil Detection and Location Privacy Are the Same Measurement"*

**Thesis.** Detecting a Sybil attacker means proving several pseudonyms belong to one vehicle. Tracking an
honest driver means exactly the same inference. The field has spent 20 years optimising one side and 20 years
optimising the other, and **nobody has plotted the curve that connects them**. This paper does, on public data.

**Type:** measurement/security paper · **Venue:** VehicleSec (NDSS) → IEEE TIFS / PETS / IEEE TITS
**Closes:** G11 (privacy–detection trade-off) + G5 (deployed pseudonym model) + parts of G1/G8
**Answers:** RQ9, RQ7 (empirical half), RQ1 (subset) · **Effort:** 6–8 weeks · **Risk:** low

### Round-4 grounding (from deep reading, not inference)
- **The dial is not invented — it is the field's own.** P2DAP (2007) tunes pseudonym **hash-group
  granularity** and evaluates privacy with *N-anonymity*; Footprint (2011) tunes a **temporal linkability
  window** ("two authorized messages signed by the same RSU within the same period are recognizable") and
  argues privacy qualitatively in §5.2; Akil (2023) tunes **epoch length** with unlinkable credentials and
  concedes vehicles "could still be tracked". Three landmark schemes, one dial, zero measurements of both ends.
- **The field agrees this is the gap:** privacy is the #1 admitted limitation across the 92 papers (13
  papers) and #2 stated future-work theme (7).
- **Damage anchor for the introduction:** Söderhäll 2025 measures Sybils at **3 % of users raising average
  travel time 20 %** — the concrete harm number this literature otherwise lacks.
- **A precedent metric exists for the privacy axis** (P2DAP's N-anonymity), so the measurement is defensible
  rather than ad hoc.

### Why this one, specifically
1. **Verified empty intersection.** Pseudonym-linking/tracking: 250 works. Sybil detection: 331 papers indexed
   here. Their quantified *joint* trade-off: **2 works**, both tangential. Concurrent-pseudonym detection
   framing: 4 works, none framing it this way.
2. **Data is on disk and md5-verified.** `DataReplaySybil_0709/1416`, `DoSDisruptiveSybil_0709/1416` plus the
   preprocessed CSV — no simulation, no crypto implementation, no waiting for the rest of the download.
3. **Ground truth is free.** `sender` (true vehicle) vs `senderPseudo` (what receivers see) gives labels for
   *both* tasks from the same traces.
4. **Small build.** One linkage engine, two evaluation heads. Not six re-implementations.
5. **It reframes the field**, which is what gets cited: every Sybil paper's "privacy preserved" claim becomes
   a measurable quantity instead of an assertion.

### Core method
- **Synthetic pseudonym-change layer (required — see `08_dataset_audit.md` Finding 2).** Benign vehicles in
  VeReMi never change pseudonyms, so split each benign trace at a chosen pseudonym lifetime τ_p and re-key it.
  This is a policy layer above mobility, and it makes τ_p the paper's controlled variable.
- **Identifier hygiene (required — Finding 1).** Re-map all pseudonyms to identity-free tokens before any
  experiment; group only by `senderPseudo`. Otherwise both heads are solvable by string arithmetic.
- **Linkage engine.** Given a stream of BSMs with pseudonyms only, score pseudonym pairs by kinematic
  continuity (position/speed/heading extrapolation over the pseudonym-change gap, with `*_noise` as the error
  model). Tunable operating point = linkage threshold τ.
- **Head A — Sybil detection.** A vehicle emitting concurrent, mutually-consistent pseudonyms is a Sybil.
  Measure TPR/FPR against the attacker labels (`A<n>` in filenames, ground-truth file).
- **Head B — tracking risk.** Apply the same linkage to *honest* vehicles and measure re-identification: mean
  trajectory-continuity length, fraction of pseudonym changes successfully linked, anonymity-set size.
- **Output — the Pareto front.** Sybil-detection TPR on one axis, honest-vehicle tracking success on the
  other, swept over τ, pseudonym lifetime, beacon rate, and traffic density (0709 vs 1416).
- **Design guidance.** The curve yields the first evidence-based answer to "how short must a pseudonym's life
  be before Sybil detection stops working — and how long before drivers are trackable?"

### Structure
1. Introduction — the dilemma, stated as one measurement.
2. Background — pseudonym schemes (SCMS/1609.2, PUCA, ACPC) and Sybil detection; why the two literatures never met.
3. Threat & privacy model — insider with a legitimate pseudonym batch; passive global/local tracker.
4. Linkage engine and operating points.
5. Head A: detection results across Sybil families and densities.
6. Head B: tracking results on honest vehicles.
7. The Pareto front + sensitivity (pseudonym lifetime, beacon rate, density, positioning noise).
8. Implications for SCMS parameter choice; what a misbehaviour authority can and cannot ask for.
9. Limitations (simulated traces, no RSSI, single mobility model) → motivates Papers 2 and 3.
10. Artefacts: code + configs + the Pareto data.

### Hypotheses (publishable whichever way they fall)
- **H1** There is no τ at which Sybil detection is strong and tracking is weak — the tasks are near-identical.
- **H2** Detection degrades faster than privacy improves as pseudonym lifetime shortens (asymmetric trade-off).
- **H3** Traffic density moves both curves together: dense traffic hides honest vehicles *and* Sybils.

### Staging
| Weeks | Deliverable |
|---|---|
| 1 | Loader for VeReMi Extension (nested zips, type-3 records, label parsing from filenames + GT) |
| 2 | Linkage engine v1 (kinematic extrapolation + noise model), sanity check against ground truth |
| 3 | Head A: Sybil detection metrics across the four verified archives |
| 4 | Head B: tracking metrics on benign vehicles |
| 5 | Pareto sweeps (τ, pseudonym lifetime, density) + statistics with seed variance and CIs |
| 6–8 | Write-up, artefact release, SCMS-parameter discussion |

**Fallback if H1 is trivially true:** the paper becomes "how much of published Sybil-detection performance is
privacy loss in disguise" — an audit of the corpus's privacy claims against measured linkability. Still novel.

---

# Paper 2 — *"Sybil Detectors Under Adaptive Adversaries: a Reproducible Benchmark"* (the v2 plan, re-scoped)

**Effort 3–4 months.** Reuses Paper 1's loader. Re-scoped for feasibility:
- **Four families, not six** — traffic-flow (Ayaida), kinematic plausibility, ML ensemble (Azam-style),
  pseudonym-linkage (Paper 1's engine). RSSI and RSU-trajectory families **require regenerating traces with a
  patched F2MD/Veins** (`07_feasibility.md` §3) — schedule that only if the reviewers or the story demand it.
- Adds the **difficulty index (I1 — now framed as *generalising* Ayaida 2019's scheme-specific analytical
  detection-rate-vs-density model across detector families, and citing it)**, **attack-utility-constrained
  evasion (I4)**, latency on OBU-class hardware (RQ3), and damage-based metrics (I5, anchored on Söderhäll's
  3 %→20 % result).
- **First baseline to implement: Ayaida 2019** — flag when `|V_measured − V_est(density from CAMs)| > V_th`,
  confirm with a neighbour. No RSSI, no crypto, no RSU: fully reproducible on VeReMi.
- **Leakage control is a contribution in itself:** Azam 2022 uses random k-fold CV over pooled simulation
  data; scenario-disjoint splits will move the numbers.
- Prior art to differentiate against, explicitly: **SixPack (2021)** — non-ML evasion of F2MD detectors on
  LuST — and **Evaluating Zero-Day Generalisation** (2026) — leave-one-attack-out on VeReMi NextGen.

# Paper 3 — *"An Open, Calibrated, RSSI-Realistic Sybil Dataset"*

**Effort 2–3 months.** Motivated by a documentable fact: the only realistic RSSI Sybil dataset (Istanbul) is
owner-restricted amid an authorship dispute, and VeReMi provably lacks an RSSI field. Regenerate with patched
F2MD/Veins at 10 Hz, calibrate shadowing against published ITS-G5/802.11p measurement traces, release CC-BY.
Position against BurST-ADMA, VeReMi NextGen and **VeReMi-Graph v1.0 (2026)**.

# Paper 4 — *"Sybil as Certificate Concurrency"* (highest single-idea novelty, needs crypto depth)

Verified: 9 works in the SCMS/pseudonym-concurrency space, none detecting misuse. Paper 1 supplies the
empirical half; this adds the linkage-structure design and the detect → report → revoke latency question.

---

## Sequencing

```
Paper 1  Linkability Dilemma  (6–8 wks, data ready, framing verified empty)
   ├── loader + linkage engine feed Paper 2's benchmark
   ├── measured privacy curve feeds Paper 4's SCMS design
   └── documented RSSI absence justifies Paper 3
```

## If a review paper is wanted instead
Sybil-specific, quality-scored, reproducibility-auditing only (RQ14). Do **not** write a general misbehaviour
survey — IEEE COMST 2023 (158 cites) and IEEE TITS 2025 own it. ~70 % is already drafted across
`01_`, `02_`, `03_`, `06_`.

## Assets
| Need | File |
|---|---|
| History / related work | `01_field_evolution.md` |
| Taxonomy + practice audit | `02_method_taxonomy.md` |
| Gaps, verified | `03_research_gaps.md` |
| RQs + innovations | `04_research_questions.md` |
| Proof gaps are real; killed claims | `06_gap_verification.md` |
| **Data schema, what is buildable, integrity workflow** | `07_feasibility.md` |
| Per-paper evidence | `notes/cards.md`, `notes/paper_notes.csv` |
| Citations | `../references.bib` |
