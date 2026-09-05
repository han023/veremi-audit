# Research Gaps — Sybil Attacks in VANETs (v2, verified)

**v2 change:** every gap has been re-tested against the wider V2X / misbehaviour-detection literature via 36
OpenAlex probes, not just against the 92-paper Sybil corpus. Verification evidence and the claims that *died*
are in `06_gap_verification.md`. Status column:

- **OPEN** — verified open in the wider literature too. Safe to build a paper on.
- **NARROW** — the general area is active; only a specific slice is open. Publishable, but must cite the
  surrounding work and claim the slice precisely.
- **CLOSED** — was in v1, is not a gap. Kept here so the mistake is not repeated.

---

## OPEN gaps (build here)

### G1. No head-to-head, reproducible benchmark of *Sybil-specific* detectors — **OPEN**
**Corpus evidence.** 83 of 92 papers evaluate on private simulations; 4 mention code; 0 have reachable repos;
11 post-2020 papers still use NS-2 (dead since 2011); reported detection sits at 90–99.9 % regardless of
method or year; "comparisons against Footprint/P2DAP" use the authors' own re-implementations.
**External verification.** Benchmarking exists for *generic* misbehaviour detection (VeReMi, VeReMi Extension
215 cites, physical-layer plausibility checks 75 cites), but a controlled comparison of the Sybil detector
families — RSSI-DTW, timestamp-series, trajectory, traffic-flow, ML — does not exist (19 weak hits).
**Why it matters.** Nobody can say whether 20 years of work improved anything.
**Difficulty.** Medium — datasets and F2MD are already downloaded; the cost is re-implementing 5–6 schemes.

### G2. Reproducibility is effectively zero — **OPEN**
4/92 papers mention code. The single public artefact — the Istanbul RSSI Sybil dataset — is **owner-restricted
amid an authorship dispute**, its README stating the associated article was published without authorisation.
One corpus paper is retracted. Several "data available on request" statements. This is documentable, citable,
and nobody has audited it for this subfield.

### G3. Adversarial / gradient-based evasion of ML Sybil detectors — **OPEN**
**Corpus evidence.** 0 of 92 papers contain any adversarial-ML content (0 hits for adversarial examples,
0 for poisoning) despite 27 ML/DL papers in 2022–26.
**External verification.** Adversarial ML for V2X IDS exists broadly (125 works), and *SixPack* (2021) evades
MBD by abusing ABS — but no work attacks a **VeReMi-trained Sybil detector**, and none constrains the
perturbation by *attack utility* (the fake congestion must still happen). That combination is untaken.
**Why it matters.** A detector that reports 99 % against a naive attacker and collapses against an adaptive
one is worse than useless — it creates false assurance.

### G4. No detectability theory — **OPEN (strongest theoretical gap)**
No paper states what is *achievable*: given RSU density λ, vehicle density ρ, positioning error σ, beacon rate
*f*, observation window *T*, how separable are *k* Sybils from *k* real vehicles? Probe 4 (256 works) returns
only empirical classics. Consequence: an easy scenario and a good detector are indistinguishable in the
literature, which is precisely why accuracy numbers inflated for 20 years.

### G5. Sybil detection is not posed inside deployed PKI (SCMS / IEEE 1609.2) — **OPEN**
1 of 92 corpus papers mentions IEEE 1609.2; 1 mentions pseudonym certificates/linkage values. Externally, only
~10 works pair SCMS with misbehaviour detection, and exactly one — Akil 2023, in our corpus — treats
concurrent-pseudonym misuse. Yet SCMS *already* bounds pseudonyms, so the deployed question is "detect misuse
of a legitimate certificate batch and revoke fast", which almost nobody asks.

### G6. Latency and energy on automotive hardware are unmeasured — **OPEN**
3 of 92 papers mention embedded platforms; 7 mention the 100 ms budget; essentially none report inference cost
on OBU-class hardware, though they propose per-message deep nets, DTW windows, PoW puzzles, blockchain writes
and VDFs. Observation-window detectors need seconds-to-minutes — by which time the fake congestion has
already re-routed traffic.

### G7. No dataset has RSSI + identity + Sybil labels together — **OPEN (restated in round 6, measured)**
RSSI is the field's most-used signal (33 corpus papers). An earlier version of this gap said "the VeReMi
family has no RSSI" — **that was wrong**, and the measured truth is a stronger claim:

| Dataset | RSSI | identity | Sybil families |
|---|---|---|---|
| VeReMi 2018 | **yes** (populated, 1.3e-9…2.6e-5 W) | `sender` only, no pseudonyms | no (position falsification) |
| VeReMi Extension 2020 | no | `senderPseudo` (ID-leaking) | **yes** |
| Preprocessed CSV 2025 | no | **no identity column at all** | labels only |

So RSSI methods can be benchmarked on the 2018 set (no Sybil attacks) and identity methods on the Extension
(no RSSI) — **never both**. BurST-ADMA is not RSSI-centric; the Istanbul set is owner-restricted. Real
ITS-G5/802.11p traces exist publicly (Data in Brief 2019) for *calibration*, making a replacement feasible.
Full measurements: `08_dataset_audit.md` Finding 3.

### G8. Statistical rigour and experiment reporting — **OPEN (upgraded in round 4)**
5 of 92 papers report ROC/AUC; **2** report any significance test, confidence interval or seed variance.
Round 4's full-text extraction shows the problem is more basic than statistics — most papers do not describe
their own experiment: explicit threat model **22/92**, vehicle count 34/92, simulation time 18/92,
**beacon rate 9/92**, **attacker fraction 9/92**, **simulation area 6/92**. A result whose adversary,
message rate and attacker density are all unstated cannot be reproduced, compared, or even interpreted.
Documented instance of leakage: Azam 2022 (the most-cited recent ML paper here) uses PCA + SMOTE followed by
**random k-fold cross-validation over pooled simulation data**.

---

## NARROW gaps (publishable slice, but the area is active)

### G9. Cross-scenario generalisation of Sybil detectors — **NARROW**
Transfer-learning IDS work for IoV is common (101 works), but no one measures how Sybil detectors degrade
across maps, densities and beacon rates. Corpus ML papers split train/test inside one simulation run.

### G10. RSU-density thresholds where infrastructure schemes break — **NARROW**
144 works mention density; none publishes the breakdown point per scheme family. Park 2009 was the last paper
to make sparse deployment its central case.

### G11. Quantified privacy-vs-detection trade-off — **NARROW**
Privacy-preserving detection exists (DP-based collaborative IDS, LH-IDS 2024; 16 works), but nobody plots
detection TPR against *measured* adversarial tracking success for Sybil schemes. Privacy is argued, never measured.

### G12. Sybil-enabled corroboration in collective perception (CPM) — **NARROW**
CP misbehaviour detection is an active subfield (MISO-V 2021; CP-MBD survey 2025; simulation framework 2024),
so this is **not** virgin ground. The untaken slice: multiple Sybil identities *corroborating a phantom object*
to defeat consensus fusion, and occlusion-geometry checks as the defence (only 4 works pair Sybil with CP).

### G13. Colluding / insider Sybils with legitimate identities — **NARROW**
Named by Feng 2016 (EBRS) and partly handled by Threshold-P2DAP; colluding-Sybil effects studied in
platooning (2017). Still open for trajectory schemes: two attackers physically driving together can mint
plausible joint trajectories.

### G14. Literature quality control as a finding — **NARROW but usable**
331 indexed papers, 110 with zero citations, median 3, a retracted article, a live authorship dispute, four
2014 Footprint clones, two near-identical 2025 routing-impact papers. No existing survey in the corpus uses a
documented search protocol or quality rubric — but the *survey slot itself* is contested (see G-CLOSED-3).

---

## CLOSED — v1 claims that verification killed

| # | v1 claim | Why it is closed |
|---|---|---|
| C1 | "Sybil in cooperative perception is untouched — first-mover" | CP-MBD is an active subfield with its own 2025 survey. Only the narrow slice in G12 remains. |
| C2 | "Federated-learning Sybil poisoning is untouched" | FoolsGold (2018, 363 cites) + vehicular FL-MBD (2022–2026); 110 works. |
| C3 | "A survey would beat what exists" | IEEE COMST 2023 (158 cites) and IEEE TITS 2025 (71) own generic MBD surveying. Only a Sybil-specific, quality-scored review has room. |
| C4 | "Crowdsensing/navigation Sybil is a first-mover space" | Ghost Riders (ToN 2018), crowdsourced-mapping defences (2016), TITS 2020; 42 works. |
| C5 | "Platooning barely covered" | 19 works including a 2019 platoon Sybil defence and 2017 colluding-Sybil studies. |
| C6 | "Explainability is missing" | 108 works; XAI-ADS (2024), XAI for IDS (2023, 187 cites). |
| C7 | "Attacker economics unmodelled" | Security Games for Vehicular Networks (TMC 2010) and 77 further works. |
| C8 | "Post-quantum angle is open" | Post-Quantum Anonymous/Traceable/Linkable Authentication (TITS 2024); 76 works. |
| C9 | "No adaptive-attacker work exists" | SixPack (2021) evades MBD via ABS abuse; BoostSec (2023); 23 works. G3 survives only in its ML-evasion form. |

---

### G15. The field's own agenda says privacy is the top unsolved problem — **OPEN**
Thematic coding of stated future work (49 papers) and admitted limitations (52 papers) puts
**privacy preservation first among admitted limitations (13 papers)** and second among future-work items (7).
Meanwhile the linkability dial that governs it — P2DAP's hash-group granularity (2007), Footprint's temporal
linkability window (2011), Akil's epoch length (2023) — has never been measured at both ends on the same
traces. The field has named its own biggest gap for sixteen years without quantifying it.

## Gap → paper map (v2)

| Gaps | Paper it supports | Verified novelty |
|---|---|---|
| G1 + G3 + G4 + G8 | **Benchmark + difficulty index + utility-constrained evasion** | High on three axes |
| G5 | SCMS-native concurrency detection | Highest single-idea novelty |
| G7 | Open calibrated RSSI Sybil dataset | High, artefact-type |
| G6 + G9 + G10 | Deployment-feasibility study (latency, density thresholds, generalisation) | Medium-high |
| G11 + G12 + G13 | Follow-on papers once the benchmark exists | Medium |
