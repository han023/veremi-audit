# Research Questions (v2 — verified against the wider literature)

v1 ranked questions by how open they looked inside the Sybil corpus. v2 ranks them by **verified** openness
(see `06_gap_verification.md`), and separates *questions* from *innovations* (new mechanisms you could propose,
not just holes to fill).

**Novelty** ●●● first-of-kind after verification · ●●○ solid slice in an active area · ●○○ incremental.
**Effort** = weeks of full-time work. **Assets** = what you already have locally.

---

## Tier 1 — verified open, answerable with assets in hand

### RQ0 (NEW, now the recommended starting point). Are Sybil detection and location tracking the same measurement?
**Gaps G11 + G5 · Novelty ●●● (verified: 2 tangential works on the joint framing) · Effort 6–8 wks · Assets: verified on disk**
Every received VeReMi message carries `sender` (true vehicle) and `senderPseudo` (what a receiver actually
sees). So the same kinematic-linkage inference can be scored twice on the same traces: as Sybil detection
(linking an attacker's concurrent pseudonyms) and as a tracking attack (linking an honest driver's successive
pseudonyms). Sweep the linkage threshold, pseudonym lifetime, beacon rate and traffic density; plot the
Pareto front. Nobody has drawn it. See `05_new_paper_plan.md` for the full design.


### RQ1. Do published Sybil detectors actually beat each other on identical data?
**Gap G1 · Novelty ●●○ (●●● with RQ3/RQ4) · Effort 6–10 wks · FEASIBILITY (measured, round 6): the Extension has no RSSI and no RSU logs, but **VeReMi 2018 does carry populated RSSI** — so RSSI methods are testable there against position-falsification attacks, identity methods on the Extension, and only the RSU trajectory-tag family strictly needs regenerated traces (`07_feasibility.md`, `08_dataset_audit.md`).**
Re-implement six representatives — RSS-statistical (Xiao 2006), RSSI-DTW (Voiceprint 2017), timestamp-series
(Park 2009), trajectory (Footprint 2011), macroscopic traffic-flow (Ayaida 2019), ML ensemble (Azam 2022) —
and run them on `GridSybil`, `DataReplaySybil`, `DoSRandomSybil`, `DoSDisruptiveSybil` (both densities) plus
NextGen `trafficCongestionSybil`. Report per-message and per-vehicle ROC-AUC, FPR@95%TPR, latency, CPU.
*Note:* generic MBD benchmarking exists (VeReMi Extension), so state the contribution as **Sybil-family-specific
reproduction**, and pair it with RQ3/RQ4 so the paper is not "just a benchmark".
**Testable hypothesis:** 2011-era physics/trajectory schemes land within 5 AUC points of 2022–26 deep models.

### RQ2. How much reported accuracy is scenario leakage rather than learning?
**Gap G9 · Novelty ●●○ (reduced) · Effort 4–6 wks · PRIOR ART: *Evaluating Zero-Day Generalisation in VANET Detection* (2026) does leave-one-attack-out on VeReMi NextGen — re-scope to cross-*scenario* (map/density/beacon rate) for Sybil-specific detectors.**
Train on one map/density, test on another (LuST ↔ InTAS; 07:09 ↔ 14:16; urban ↔ highway; 1 Hz ↔ 10 Hz).
Corpus ML papers split within a single simulation run. Quantify the generalisation gap and recalibrate the
field's headline numbers. Position against the transfer-learning IoV-IDS literature, which does not cover
Sybil detectors.

### RQ3. What is the accuracy-vs-latency frontier under the 100 ms V2X deadline?
**Gap G6 · Novelty ●●● · Effort 3–5 wks**
Accuracy as a function of observation window (1 beacon → 10 s), and measured inference time on OBU-class
hardware (Raspberry Pi 4 / Jetson Nano). Nobody in this field publishes this curve, and window-based methods
(RSSI-DTW, trajectory, traffic-flow) are structurally disadvantaged — that result is the point.

### RQ4. Can an attack-utility-constrained adversary evade ML Sybil detectors?
**Gap G3 · Novelty ●●● · Effort 8–12 wks**
Three adversary upgrades in F2MD/Veins: (a) transmit-power randomisation and directional antennas — the 2007
Guette attack, still unanswered; (b) mobility-mimicking Sybils on plausible SUMO trajectories; (c) **gradient
evasion under a utility constraint** — the perturbed beacons must still produce the intended fake congestion.
(c) is the novel part: standard adversarial ML ignores whether the attack still *works*.
Prior art to cite (abstract read in round 3): **SixPack (2021)** — an insider fakes ABS activation in BSMs and rejoins the fake and real vehicle representations, evaluated *with F2MD on LuST/LuSTMini*, evading state-of-the-art detectors by inducing false positives. Delta: gradient-based, utility-constrained evasion of **ML** Sybil detectors, plus a defence (I3).

### RQ5. Does a Sybil detector survive when other misbehaviours are present?
**Gap G9/G1 · Novelty ●●○ · Effort 4 wks**
Mix Sybil traces with VeReMi's non-Sybil families (constant/random offset, data replay, DoS). Measure
cross-attack false-positive inflation; test whether one multi-class model beats specialised detectors.

---

## Tier 2 — verified open, needs new artefacts or theory

### RQ6. What is the detectability limit for k Sybils under given conditions?
**Gap G4 · Novelty ●●● (strongest theoretical gap) · Effort 8–12 wks, theory-heavy**
Model beacons as noisy observations of a marked point process; derive separability bounds as a function of
λ (RSU density), ρ (vehicle density), σ (positioning error), *f* (beacon rate), *T* (window). Validate
empirically on VeReMi scenarios. Output: a **scenario-difficulty index** so a reported 97 % becomes
interpretable. Verification found *no* bounds work in this space.

### RQ7. How should Sybil detection work *inside* SCMS / IEEE 1609.2?
**Gap G5 · Novelty ●●● · Effort 10–14 wks · needs crypto depth · NOTE: PUCA (2015) and ACPC (2018) already *prevent/revoke*; the open question is *detecting misuse* and measuring detect→report→revoke latency. RQ0 supplies the empirical half.**
Reframe: the deployed attacker holds a legitimate pseudonym batch and uses several certificates concurrently.
Questions: what concurrency is detectable from butterfly-key linkage structures without breaking unlinkability
for honest vehicles? What is end-to-end detect → misbehaviour-report → CRL-propagation latency, and is the
attack over before revocation lands? Only one prior work (Akil 2023) touches this framing.

### RQ8. Can one dataset carry RSSI, identity and Sybil labels at once?
**Gap G7 · Novelty ●●● (artefact) · Effort 8–12 wks · Motivation hardened in round 6: no public set has all three
(VeReMi 2018 = RSSI without Sybil; Extension = Sybil without RSSI; preprocessed CSV = neither).**
SUMO + Veins, 10 Hz beaconing, urban + highway, calibrated log-normal shadowing, ghost-vehicle ground truth,
multiple attacker densities — **calibrated against published real ITS-G5/802.11p measurement traces**, with a
small own measurement campaign if hardware allows. CC-BY on Zenodo + code. The field's most-used signal
currently has no usable public substrate.

### RQ9. Where is the privacy/detection Pareto front?
**Gap G11 · Novelty ●●○ · Effort 6–8 wks**
Sweep pseudonym lifetime and tag linkability for a Footprint-style scheme and an attribute-based-credential
scheme; plot detection TPR against *measured* tracking success of a linking adversary on the same traces.
The curve everyone has argued about since 2007 and nobody has drawn.

### RQ10. At what RSU density do infrastructure-based schemes stop working?
**Gap G10 · Novelty ●●○ · Effort 4 wks**
Sweep RSU density from urban-dense to rural-none; publish the breakdown threshold per family and show which
infrastructure-free family takes over. Directly useful to road operators; cheap once RQ1's harness exists.

---

## Tier 3 — narrow slices in active areas (cite the neighbours carefully)

### RQ11. Can Sybil identities corroborate a phantom object in collective perception?
**Gap G12 · Novelty ●●○ · Effort 10 wks**
CP-MBD is active (MISO-V 2021, CP-MBD survey 2025), so claim the slice: how many Sybil reporters are needed to
push a phantom object into a fused world model; can occlusion geometry and sensor-FoV consistency detect it;
what is the effect on AEB/ACC decisions. **Do not** claim first-of-kind on CP security.

### RQ12. Do colluding attackers driving physically together defeat trajectory schemes?
**Gap G13 · Novelty ●●○ · Effort 5 wks**
Two real vehicles can generate genuinely consistent joint trajectories, then mint Sybils from them. Test
Footprint/PoL/timestamp schemes against physically-colluding pairs.

### RQ13. What does each signal actually contribute? (modality ablation)
**Gap G1 · Novelty ●●○ · Effort 3 wks** — marginal value of RSSI vs kinematics vs certificate metadata vs
trajectory tags. Cheap after RQ1, and tells implementers what PKI hooks and sensors are worth paying for.

### RQ14. Does the field's evidence base support its claims? (systematic, quality-scored review)
**Gap G2/G14 · Novelty ●●○ · Effort 6–8 wks**
Only viable if Sybil-specific *and* methodologically novel: documented search protocol, inclusion/exclusion,
per-paper quality rubric (public data? public code? adaptive attacker? latency? standards? statistics?), and
the reproducibility audit. Generic MBD surveys (COMST 2023, TITS 2025) already exist — do not compete there.

---

## Innovations — mechanisms worth *proposing*, not just gaps to fill

| # | Idea | Closes | Novelty |
|---|---|---|---|
| **I1** | **Sybil-detectability index**: analytic scenario-difficulty score reported alongside accuracy | G4 | ●●● |
| **I2** | **SCMS-native concurrency detection**: linkage-structure-based proof that two pseudonyms share an enrolment, without unmasking honest vehicles | G5 | ●●● |
| **I3** | **Physics-constrained detectors**: kinematic + propagation constraints as differentiable penalties, so evasion must break the physics that makes the attack useful | G3 | ●●● |
| **I4** | **Attack-utility-constrained evasion**: adversarial search restricted to perturbations that preserve attacker payoff | G3 | ●●● |
| **I5** | **Damage-based metric**: report *damage prevented* (travel-time loss, spurious brake events) instead of only detection rate | G1/G8 | ●●○ |
| **I6** | **Modality ablation protocol**: standard recipe for reporting each signal's marginal contribution | G1 | ●●○ |

---

## The framing question for any paper here

> Has 20 years of Sybil-detection research produced a scheme that is simultaneously (i) accurate under an
> adaptive attacker, (ii) fast enough for a 100 ms safety deadline, (iii) privacy-preserving to a *measured*
> standard, (iv) affordable on production OBUs, and (v) reproducible from public code and data?

On the verified evidence: **no on all five simultaneously** — and (i), (ii), (iv), (v) have never even been
tested together for this attack class.
