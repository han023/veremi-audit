# Gap Verification — testing my own claims against the adjacent literature

A gap that only looks open because you searched too narrowly is not a gap. The first pass
(`03_research_gaps.md` v1) was derived from the 92-paper Sybil-VANET corpus alone. This file re-tests every
claim against the **wider misbehaviour-detection (MBD) / V2X security literature** via OpenAlex, and against a
keyword audit of the full text of all 92 corpus papers.

Method: 36 OpenAlex title+abstract probes (`workspace/gapcheck*.py`, raw results in `notes/gapcheck.json`),
plus 27 regex probes over `workspace/text/` (`notes/keyword_audit.json`).

---

## Part 1 — Keyword audit of the 92 corpus papers

| Probe | Papers | Probe | Papers |
|---|---|---|---|
| adversarial ML | **0** | latency stated in ms | 27 |
| model poisoning | **0** | 100 ms deadline discussed | 7 |
| federated learning | 2 | real-world testbed/measurement | 11 |
| IEEE 1609.2 | **1** | ROC / AUC | 5 |
| pseudonym certificate / linkage value | **1** | significance testing / CI | **2** |
| ETSI / SCMS / C-ITS | 11 | energy on embedded hardware | 3 |
| C-V2X / 5G sidelink | 4 | differential privacy | **1** |
| collective perception (CPM) | **1** | k-anonymity | 6 |
| VeReMi | 5 | 10 Hz beaconing | 7 |
| graph neural network | 2 | transformer / LLM | 1 |

Interpretation: the corpus is standards-blind, statistically weak, and has *literally zero* adversarial-ML
content. Those parts of the v1 analysis survive.

---

## Part 2 — Claims that DIED or were WEAKENED (v1 was wrong or overstated)

| v1 claim | Reality | Evidence |
|---|---|---|
| "Sybil in cooperative perception — **zero** work, first-mover paper" | **Wrong.** CPM misbehaviour detection is an active subfield (15+ works): MISO-V (2021), object-based shared-perception MBD (2019), CP-MBD under privacy (2022), a CP-MBD **survey** (2025), CP-MBD simulation framework (2024). | probe B/C |
| "Federated-learning Sybil poisoning is untouched" | **Wrong.** FoolsGold *Mitigating Sybils in Federated Learning Poisoning* (2018, 363 cites) plus vehicular FL-MBD (Ad Hoc Networks 2023), privacy-preserving FL MBD (TNSM 2022), decentralised FL IoV (2026). 110 works. | probe F |
| "Crowdsensing / navigation-app Sybil is a first-mover space" | **Overstated.** *Ghost Riders: Sybil Attacks on Crowdsourced Mobile Mapping Services* (IEEE/ACM ToN 2018, 54), *Defending against Sybil Devices in Crowdsourced Mapping* (2016, 96), TITS 2020 self-supervised detection (59). 42 works. | probe O |
| "Platooning barely covered" | **Overstated for the literature** (true only of my corpus): *Defending against Sybil Attacks in Vehicular Platoons* (2019), colluding-Sybil message falsification (2017), Sybil impact on cooperative driving (2017). 19 works. | probe 8 |
| "Attacker economics unmodelled" | **Weakened.** *Security Games for Vehicular Networks* (TMC 2010, 86), game-theoretic IDS frameworks (FGCS 2017, 83), 77 works. Sybil-specific pricing is still thin, but this is not virgin ground. | probe 9 |
| "Post-quantum angle is open" | **Weakened.** *Post-Quantum Anonymous, Traceable and Linkable Authentication* (TITS 2024), 76 works. | probe K |
| "Explainability is missing" | **Wrong.** XAI for vehicular IDS is busy: *XAI for Intrusion Detection and Mitigation* (2023, 187), XAI-ADS (IEEE Access 2024, 68), black-box XAI evaluation for V2X anomaly detection (Sensors 2024). 108 works. | probe E |
| "A pure survey would beat what exists" | **Wrong for generic MBD.** *ML-Based Misbehavior Detection Systems for 5G and Beyond Vehicular Networks* (**IEEE COMST 2023, 158 cites**) and *Advancing Intrusion Detection in V2X Networks* (**TITS 2025, 71**) own that space. A new survey must be Sybil-specific **and** methodologically novel (quality scoring, reproducibility audit) or it is dead on arrival. | probe 5 |
| "No adaptive-attacker work at all" | **Weakened.** *SixPack: Abusing ABS to avoid Misbehavior detection in VANETs* (2021) is exactly an evasion attack — non-ML, exploits a plausibility-check blind spot. Also BoostSec (2023), Q-learning adaptive trust threshold (2025). 23 works. | probe 2 |
| "VeReMi is the only dataset" | **Incomplete.** BurST-ADMA (Australian MBD dataset, 2022), VeReMi NextGen (2026), *A Comparative Review of Security Threats Datasets for Vehicular Networks* (2021), ITS-G5 DSRC full-stack traces (Data in Brief 2019), 802.11p BSM measurement sets (2018). | probe 7/P |

---

## Part 3 — Claims that SURVIVED verification (these are the real gaps)

| Gap | Verification | Strength |
|---|---|---|
| **V1. No head-to-head, reproducible benchmark of *Sybil-specific* detectors** | Probe 1 returns 19 works; none is a controlled re-implementation + comparison of Sybil schemes. VeReMi-family benchmarking exists for *generic* MBD, not for the Sybil detector families (RSSI-DTW, timestamp-series, trajectory, traffic-flow). | **Strong** |
| **V2. Adversarial / gradient-based evasion of ML Sybil detectors** | 0 corpus papers; probe A returns 10 works, none of which attack a VeReMi-trained Sybil model. SixPack (2021) is the closest and is non-ML, single-mechanism. | **Strong** |
| **V3. Detectability limits / theoretical bounds** | Probe 4 (256 works) returns only the classic empirical papers — no bounds, no identifiability analysis, no scenario-difficulty normalisation anywhere. | **Strong** |
| **V4. Concurrent-pseudonym (certificate-misuse) detection inside SCMS / IEEE 1609.2** | Probe F returns **one** relevant work — Akil et al. 2023, which is in our corpus. Probe G: SCMS+MBD is 10 works (EmuLab SCMS 2018, C-ITS MBD feasibility 2018, pseudonym-certificate + MBD experimentation 2021). The Sybil-as-certificate-concurrency framing is essentially untaken. | **Strong** |
| **V5. Latency / energy of Sybil detection on automotive-grade hardware** | 3 of 92 corpus papers mention embedded platforms; probe 3 returns 25 mostly-unrelated works. No accuracy-vs-latency frontier exists for this problem. | **Strong** |
| **V6. Public, RSSI-realistic, Sybil-labelled dataset** | The only one (Istanbul) is owner-restricted amid an authorship dispute; VeReMi-family inherits F2MD's simplified RSSI, 1 Hz beacons, small maps; BurST-ADMA is not RSSI-focused. Real ITS-G5/802.11p measurement traces exist (Data in Brief 2019) — usable for *calibration*, which makes this tractable. | **Strong** |
| **V7. Sybil-enabled corroboration attacks in CPM** (narrowed) | CP-MBD is active, but probe D finds only 4 works pairing Sybil with collective perception, none studying *multi-identity corroboration of a phantom object* and occlusion-geometry defences. | **Medium** (must cite the CP-MBD field) |
| **V8. Cross-scenario generalisation of Sybil detectors** (narrowed) | Transfer-learning IDS work exists (101 works) but is about IoV intrusion datasets, not Sybil detectors across maps/densities/beacon rates. | **Medium** |
| **V9. RSU-density thresholds where infrastructure schemes fail** | 144 works mention density, none publishes the breakdown threshold per scheme family. | **Medium** |
| **V10. Quantified privacy-vs-detection trade-off curve** | 16 works (DP-based collaborative IDS, LH-IDS 2024) address privacy-preserving *detection*, none plots detection TPR against measured tracking success for Sybil schemes. | **Medium** |

---

## Part 4 — Innovation openings (ideas that follow from the verified gaps)

These are the "what could actually be new" items, not just gaps.

**I1. Sybil-detectability index (scenario-difficulty normalisation).**
Derive an analytic index from RSU density λ, vehicle density ρ, positioning noise σ, beacon rate *f* and
observation window *T*, predicting the best achievable separation between *k* Sybils and *k* real vehicles;
validate it empirically on VeReMi-family scenarios. Impact: makes "97 % detection" interpretable for the first
time, and gives reviewers a tool. Closes V3, supports V1.

**I2. SCMS-native concurrency detection.**
Reframe Sybil detection as *pseudonym-certificate concurrency* detection: use butterfly-key linkage structures
to prove "these two pseudonyms came from one enrolment in overlapping time" without unmasking honest vehicles,
and quantify detect→report→revoke latency end-to-end. Closes V4; makes the work relevant to deployment rather
than to a 2011 threat model.

**I3. Physics-constrained detectors (adversarially robust by construction).**
Embed kinematic and propagation constraints as differentiable penalties inside the model so that evading the
detector forces the attacker to violate the physics that makes the attack useful. Test against I4's attacks.
Closes V2 with a defence, not just an attack.

**I4. Attack-utility-constrained evasion.**
Standard adversarial ML asks "can I flip the label"; here the right question is "can I flip the label *while
still creating the fake congestion*". Formalise the attacker's utility (travel-time gain, lane clearance) as a
constraint set and search inside it. Closes V2 rigorously and avoids the usual unrealistic-perturbation critique.

**I5. Damage-based evaluation metric.**
Replace/augment detection rate with *damage prevented* — delta in travel time, spurious brake events,
mis-routed vehicles — computed in SUMO. Söderhäll 2025 measures attack damage; nobody measures *defence* in
those units. A metric contribution that reframes the benchmark.

**I6. Modality-ablation study.**
Quantify the marginal value of each signal (RSSI, kinematics, certificate metadata, trajectory tags) for Sybil
detection. Cheap to run once the benchmark exists, and directly useful: it tells implementers what sensors and
what PKI hooks are actually worth the cost.

---

## Part 5 — What this means for paper choice

- A **plain benchmark** is now less defensible on its own (generic MBD benchmarking exists) — but a
  *Sybil-specific* benchmark **plus** difficulty normalisation (I1) **plus** attack-utility-constrained
  evasion (I4) is novel on three independent axes and uses assets already downloaded.
- A **plain survey** is dead (COMST 2023, TITS 2025). Only a Sybil-specific, quality-scored, reproducibility-
  auditing review has room.
- The **highest-novelty single idea** is I2 (SCMS-native concurrency detection), but it needs cryptographic
  depth and has no ready-made dataset — better as paper #2 or #3.

See `05_new_paper_plan.md` for the recommended plan built on this.

---

# Round 3 — recency sweep, neighbour abstracts, and a data-feasibility check

Rounds 1–2 sorted by citation count, which hides 2025–26 work; round 3 re-ran the load-bearing probes sorted
by **date**, read the abstracts of the neighbouring surveys and the closest prior art, and — new this round —
**opened the dataset to check the recommended paper is buildable** (`07_feasibility.md`).

## 3.1 New prior art found (adjusts, not kills, the plan)

| Work | Why it matters |
|---|---|
| **Evaluating Zero-Day Generalisation in VANET Detection** (2026, Annals of Math. & CS) | Leave-One-Attack-Out on **VeReMi NextGen** with RF/XGBoost/NB/LR/Extra-Trees. Partially overlaps RQ5 (cross-attack) and touches RQ2. Small venue, classical ML only, generic attacks — but it must be cited, and RQ2/RQ5 must be re-scoped to *cross-scenario* (map/density/beacon-rate) for *Sybil-specific* detector families. |
| **SixPack** (2021) — abstract read | Insider modifies BSMs to fake ABS activation, rejoins the fake and real vehicle representations, evaluated **with F2MD on LuST/LuSTMini**, evading state-of-the-art anomaly detectors by inducing false positives. This is the closest prior art to RQ4 and uses the same tooling. RQ4's delta must be explicit: *gradient-based, attack-utility-constrained* evasion of **ML Sybil detectors**, plus a defence. |
| **VeReMi-Graph v1.0** (Mendeley Data, 2026) | New temporal attributed-graph dataset for vehicular misbehaviour → relevant substrate for graph-based detectors, and a competitor/complement for any dataset paper. |
| **SHAVA** (SoftwareX 2026) | Open-source Python VANET IDS framework — but evaluated on **CICIDS-2017**, a non-vehicular dataset. Useful *evidence* for the corpus-quality argument (generic IDS datasets misused for V2X). |
| **PUCA** (Ad Hoc Networks 2015, 40 cites), **ACPC** (2018, 26), attribute-based credentials in C-ITS (2017, 24) | Pseudonym schemes that *structurally* limit concurrent identities, plus efficient revocation. They weaken any claim of novelty for "prevent concurrency"; the open question is **detecting misuse and measuring detect→report→revoke latency**, which they do not address. |
| **Machine Learning and Reputation Based Misbehavior Detection** (TVT 2020, 119) | A strong non-Sybil-specific baseline to include in any benchmark. |

## 3.2 Corrected probes (rounds 1–2 queries were too broad on two gaps)

- **G4 detectability bounds**, vehicular-constrained: 317 works, top results are the 2006–2011 classics.
  **No bounds, identifiability analysis or difficulty normalisation exists.** Gap confirmed, strongest theory gap.
- **G5 SCMS/pseudonym concurrency**, vehicular-constrained: **9 works** — PUCA (2015), ACPC (2018),
  ABC in C-ITS (2017), pseudonym-certificate management + MBD experimentation (2021). Detection-of-misuse
  framing remains open.

## 3.3 The joint framing that verification says is open

| Probe | Works | Reading |
|---|---|---|
| pseudonym linking / tracking attacks in VANET | **250** | Mature literature (Changing Pseudonyms 2007 · 251 cites; Pseudonym Changing at Social Spots TVT 2011 · 457; SLOW 2009 · 184) |
| pseudonym change strategies vs tracking | 163 | Mature |
| **joint Sybil-detection ∧ location-privacy trade-off, quantified** | **2** | Both tangential (a 2022 pseudonym-changing scheme; a 2015 thesis) — **open** |
| concurrent-pseudonym usage detection | 4 | All generic Sybil papers; none frames it as pseudonym-concurrency inference — **open** |
| VeReMi used for privacy/tracking analysis | 35 | Nearly all are privacy-*preserving* FL/IDS (protecting training data), not measuring tracking risk on the traces |

Two mature parent literatures, an empty intersection, and public labelled data that spans both — the best
shape a new paper can have.

## 3.4 Feasibility check (the round-3 finding that changed the plan)

Opening the archives (full detail in `07_feasibility.md`):

- **VeReMi Extension has no RSSI field.** The RSSI/PHY detector family — a third of the corpus, including
  Voiceprint and Xiao 2006 — **cannot be reproduced on this data** without regenerating traces from a patched
  F2MD/Veins. The v2 "six-family benchmark" is therefore not buildable as scoped.
- **Every received message carries `sender` (true vehicle) *and* `senderPseudo`.** Receivers see only the
  pseudonym; the true id is ground truth. So the pseudonym→vehicle mapping needed for both Sybil-linkage
  detection *and* tracking-risk measurement is already public and labelled.
- One "complete" archive failed CRC despite matching its size — integrity is now checked by **Zenodo MD5**
  (`workspace/verify_datasets.py`), not size.

**Net effect:** the benchmark paper gets harder and the linkability paper gets easier — and the latter is the
one whose framing verification shows to be empty. The recommendation in `05_new_paper_plan.md` changed
accordingly.

---

# Round 4 — deep reading of all 92 full texts

Rounds 1–3 read abstracts, snippets and metadata. Round 4 ran a structured extraction over every full text
(`workspace/deep_extract.py` → `notes/deep_extract.json`) pulling assumptions, threat models, evaluation
parameters, claimed numbers, admitted limitations and stated future work, then hand-read the methodology and
privacy sections of the papers that define the design space.

## 4.1 What the papers report about their own experiments (n = 92)

| Reported item | Papers | Comment |
|---|---|---|
| Explicit threat / attacker model | **22** | 76 % of papers never state the adversary they defend against |
| Number of vehicles/nodes | 34 | |
| Simulation time | 18 | |
| **Beacon / message rate** | **9** | Yet the standard is 1–10 Hz and detection windows depend on it |
| **Attacker fraction** | **9** | The single most important experimental variable |
| **Simulation area** | **6** | |
| Any quantified performance claim | 25 | The rest report bar charts or prose |

This is the sharpest reproducibility evidence in the whole analysis: **most papers do not state the
parameters that would let anyone reproduce or even interpret their result.** It upgrades the evidence base of
G1/G2/G8 from "few use public data" to "most do not describe their own experiment".

## 4.2 What the field itself says is unfinished

Thematic coding of the *stated future work* (49 papers) and *admitted limitations* (52 papers):

| Theme | Stated as future work | Admitted as limitation |
|---|---|---|
| **Privacy preservation** | 7 | **13 (highest)** |
| Trust / reputation extension | 8 | 10 |
| Detection accuracy / FPR | 2 | 9 |
| RSU deployment / infrastructure | 5 | 8 |
| Energy / overhead | 7 | 6 |
| Latency / real-time | 4 | 6 |
| Dataset / benchmark | 0 | 4 |
| Colluding attackers | 1 | 2 |
| Real-world validation | 2 | 2 |

**Privacy is the field's own number-one admitted weakness** — and the recommended paper is precisely a
measurement of it. Note also that *no* paper lists "dataset/benchmark" as future work while four admit it as
a limitation: the field knows the substrate is missing and nobody volunteers to build it.

## 4.3 The linkability knob has existed since 2007 — unmeasured

Deep reading of the three landmark privacy-aware Sybil papers shows each defines the *same dial* and argues
privacy qualitatively:

| Paper | The knob | Privacy argument |
|---|---|---|
| **P2DAP** (Zhou 2007) | granularity of the coarse-grained pseudonym **hash groups** | *N-anonymity* (their rename of k-anonymity): "coarse-grained hash values are uniformly shared by multiple vehicles" |
| **Footprint** (Chang 2011) | **temporal linkability window** — RSU signatures are signer-ambiguous but "two authorized messages signed by the same RSU within the same given period are recognizable"; Sybil trajectories then form detectable "communities" | a qualitative §5.2 "Privacy Analysis" |
| **Akil 2023** | **epoch length** — pseudonyms fixed within an epoch, unlinkable across epochs (CL signatures + NIZKP) | unlinkability of anonymous credentials, with an acknowledgement that vehicles "could still be tracked" |

Three schemes, sixteen years, one dial — turned up for detection, turned down for privacy, **never measured
at both ends on the same traces**. That is the paper.

## 4.4 Corrections from deep reading

| Item | Correction |
|---|---|
| **I1 (difficulty index) novelty** | **Reduced from ●●● to ●●○.** Ayaida 2019 already derives *a mathematical model that evaluates the rate of Sybil attack detection according to traffic density*. It is scheme-specific, but it is a genuine precedent — I1 must be framed as generalising it across detector families, and must cite it. |
| **RQ2 (leakage)** | **Now evidenced, not hypothesised.** Azam 2022 uses PCA + SMOTE then **random k-fold cross-validation** over pooled simulation data — textbook scenario leakage, in the corpus's most-cited recent ML paper. |
| **Ayaida as a baseline** | Fully reproducible on VeReMi: compare own measured speed *V* against speed *V_est* from the traffic-flow fundamental diagram using CAM-derived neighbour density, flag if `|V − V_est| > V_th`, confirm with a neighbour. No RSSI, no crypto, no RSU. Best first baseline. |
| **Damage anchor for I5** | Söderhäll 2025 measures it concretely: **Sybils at 3 % of the user population raise average travel time by 20 %**, with targets chosen by betweenness centrality. The strongest "why it matters" number in the corpus. |
| **Baza 2020 detail** | PoW is required *between* consecutive RSUs, specifically to stop trajectory forgery when RSUs are sparse — relevant to G10 (density thresholds). |

## 4.5 Net effect on the plan

Nothing in round 4 breaks the recommendation — it strengthens it and sharpens the framing:
the dial to sweep is not invented, it is P2DAP's hash granularity / Footprint's linkability window /
Akil's epoch length; the privacy axis has a precedent metric (N-anonymity); the detection axis has a clean
reproducible baseline (Ayaida); and the damage axis has a citable anchor (3 % Sybils → +20 % travel time).
