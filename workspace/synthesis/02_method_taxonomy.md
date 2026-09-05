# Method Taxonomy — Sybil Detection & Prevention in VANETs

Derived from the 92 full-text papers (`workspace/notes/paper_notes.csv` holds the per-paper tagging).
Counts are keyword-tagged mentions per era, so a paper appears in several rows.

| Family | 2006–12 | 2013–17 | 2018–21 | 2022–26 | Trend |
|---|---|---|---|---|---|
| Crypto / PKI / pseudonyms | 9 | 25 | 18 | 30 | steady backbone |
| RSU / infrastructure-assisted | 4 | 27 | 22 | 30 | steady backbone |
| Position / trajectory verification | 5 | 17 | 16 | 26 | steady |
| RSSI / PHY | 8 | 21 | 15 | 19 | flat, quality improving |
| Timestamp series | 5 | 14 | 13 | 21 | steady |
| Trust / reputation | 1 | 11 | 10 | 16 | steady |
| ML / DL | 0 | 4 | 13 | 27 | **dominant new wave** |
| Blockchain / DLT | 1 | 4 | 6 | 15 | **rising** |
| Fog / edge / cloud | 0 | 3 | 3 | 11 | **rising** |

---

## 1. Physical-layer / signal-based

**Principle.** One transmitter cannot occupy several positions; radio observables betray it.

| Sub-approach | Representative (corpus) | Signal used |
|---|---|---|
| RSS distribution statistics | Xiao 2006 | RSS over time window |
| RSSI-variation distinguishability | Bouassida 2007/09 | ΔRSSI between claimed neighbours |
| RSSI time-series similarity (model-free) | Voiceprint, Yao/Xiao 2017; Samhitha 2019 | DTW distance of RSSI series |
| Learned RSSI series | Taysi & Güven 2025 | LSTM / CNN over RSSI |
| Channel characterisation | Almesaeed 2025 | RSSI + azimuth/elevation angular spread, ray-traced |
| Physical measurement + traffic theory | Jin & Deng 2014/15 (PMSD) | beacon physical measurements + safety guard distance |

**Strengths.** No PKI, no infrastructure, works at initial deployment, attacker cannot forge physics cheaply.
**Weaknesses (stated by the papers themselves).** Multipath/shadowing wreck accuracy in urban canyons;
Guette & Ducourthial 2007 showed transmit-power tuning and directional antennas defeat naive variants;
needs an observation window, so detection is not instantaneous; needs RSSI-carrying datasets that barely exist.

---

## 2. Position / trajectory verification

**Principle.** Compare claimed positions/trajectories against a physically consistent story.

- *Verifiable multilateration / distance bounding* with 2–3 RSUs (Hubaux et al., background, used as baseline).
- *Trajectory-as-identity*: **Footprint** (Chang 2011) — an ordered set of RSU-signed, location-hidden tags;
  Sybil trajectories look implausibly similar. Successors: Baza 2020 (adds PoW), Khan 2026 (adds GPS to cut FPR
  ~68 % dense / 70 % sparse), Khatri 2024 (tags on a smart contract).
- *Timestamp series* (Park 2009): RSU-issued certificates; identical series ⇒ one vehicle.
- *Traffic-flow consistency*: Dutta 2013 (platoon dispersion, fuzzy clustering), Almutaz 2014,
  Ayaida 2019 (macroscopic fundamental diagram vs V2V-reported density).

**Strengths.** Strong against uncoordinated Sybils; preserves privacy if tags are signer-ambiguous;
traffic-flow variants need no crypto at all.
**Weaknesses.** RSU density assumption (sparse rural coverage breaks it); compromised RSU forges trajectories
(explicitly noted as the open problem in Footprint-derived papers); overlapping legitimate trajectories
(convoys, buses) create false positives — the exact issue Khan 2026 attacks.

---

## 3. Cryptography, PKI, pseudonyms, credentials

- **Pseudonym-pool hashing:** P2DAP / Threshold-P2DAP (Zhou 2007/2011) — coarse-grained hash groups let RSUs
  spot reuse; only the DMV can de-anonymize.
- **Group / short signatures:** Funderburg & Lee 2021 (hierarchical key management, short group signatures,
  relaxed backward secrecy); Man 2024 (batch verification, CRT + Schnorr, instant revocation).
- **Attribute-based credentials:** Akil 2023 — one-time registration, self-generated non-concurrent
  short-lived pseudonyms, no online authority. Structurally Sybil-free rather than Sybil-detecting.
- **Short-term pseudonyms per RSU jurisdiction:** Zhang 2025 (IoV, avoids bilinear pairing cost).
- **Lightweight symmetric / ID-based:** Shaik 2018, Prakash 2014, Pal 2024 (RC4A), Tadesse 2026 (multi-factor).

**Strengths.** Prevention rather than detection; provable security arguments; compatible in principle with
SCMS-style deployments.
**Weaknesses.** Certificate-management burden and key escrow (raised by Zhang 2025); revocation latency;
signature flooding (Shaik 2018); most schemes assume tamper-proof devices; almost none are benchmarked
against the actual IEEE 1609.2 / ETSI TS 102 941 pseudonym machinery.

---

## 4. Trust / reputation / data fusion

- Belief functions & distributed fusion: El Zoghby 2012.
- Event-based reputation against *conspired* Sybils: Feng 2016 (EBRS), extended by Dutt 2019 (RSU/TA
  compromise), Chourey 2025 (direct + indirect trust).
- Cluster-local trust tables: Morton 2024 (TASER) — V2V-only, no infrastructure, directional antennas to cut FPR.

**Strengths.** Handles insiders using legitimate identities; degrades gracefully; infrastructure-free variants exist.
**Weaknesses.** Bootstrapping (cold start), whitewashing via pseudonym change — the direct conflict with
privacy; slow convergence relative to safety deadlines; almost never evaluated under adaptive attackers who
build reputation before defecting.

---

## 5. Machine learning / deep learning

| Style | Corpus examples |
|---|---|
| Classical ML ensembles | Azam 2022 (KNN+NB+RF+DT majority vote, VeReMi); Kakulla 2022 (SDTC, eigenvalue features) |
| Deep sequence models | Taysi 2025 (LSTM/CNN on RSSI); Helmi 2022 (DL on time/location/density) |
| Graph / spatio-temporal | Sefati 2025 (time-evolving graph + XGBoost) |
| Metaheuristic-optimised nets | Iwendi 2018 (spider monkey); Jose 2019 (SM+ECC); Velayudhan 2021/2025 (Emperor Penguin, Ship Rescue + Deep Kronecker); Suganyadevi 2025 (chaotic map + elephant herding + CNN); B. 2026 (EFLO_QDCNN) |
| Fuzzy / clustering | Dutta 2013; Ardakani 2022 (fuzzy cluster head + directional antenna); Bhanja 2023 (FLC for Sybil + DDoS) |

**Strengths.** Learns discriminative features nobody hand-designed; handles multi-modal inputs; the only
family that scales to "many attack types at once".
**Weaknesses (systemic in this corpus).**
- 83 of 92 papers use **no public dataset**; models are trained and tested on the authors' own simulation.
- Train/test splits from the *same* simulation run ⇒ leakage; no cross-scenario or cross-map generalisation test.
- Class imbalance handled ad hoc (one paper random-undersamples; most say nothing).
- No adversarial robustness evaluation anywhere in the corpus.
- Metaheuristic-hybrid papers rarely justify the optimiser, ablate it, or report variance across seeds.
- Inference cost vs the 10 Hz beacon rate / 100 ms latency budget is essentially never measured on real hardware.

---

## 6. Hardness-based & ledger-based (the newest family)

- **Proof of Work + Proof of Location:** Baza 2020 (TDSC) — per-tag puzzles make k parallel trajectories cost k× CPU.
- **Blockchain PoL:** Khatri 2024 — smart contract as location ground truth, RSU-issued puzzles, <10 % fake
  location registration.
- **Verifiable Delay Functions:** Hadri 2026 — sequential-work proofs immune to parallel hardware, fog/cloud
  hierarchy for verification.
- **Merkle structures + fog:** Almazroi 2024 (FC-LSR, 5G).

**Strengths.** Attacker-cost arguments instead of statistical thresholds; no dependence on radio conditions;
composes with privacy-preserving credentials.
**Weaknesses.** Energy and latency on automotive-grade ECUs are asserted, not measured; a well-funded attacker
buys hardware (PoW) — VDFs answer this partially; blockchain writes at V2X message rates are unaddressed at
realistic densities; hardware heterogeneity means honest low-end OBUs are penalised most.

---

## 7. Evaluation practice across the corpus (the meta-finding)

| Practice | Count (of 92 read papers) |
|---|---|
| Uses any named public dataset (VeReMi / Extension / F2MD / LuST / NGSIM…) | **9** |
| Mentions code availability at all | **4** |
| Public code that is actually reachable today | **0** (the one repo is access-restricted) |
| Uses NS-2 (development ended 2011) in a 2021+ paper | **11** |
| Uses SUMO (traffic) | 28 |
| Uses OMNeT++/Veins (802.11p stack) | 10 / 10 |
| Reports detection rate / accuracy | nearly all |
| Reports FPR/FNR | most |
| Reports ROC-AUC, confidence intervals, or significance tests | almost none |
| Reports detection latency in ms against safety deadlines | a handful |
| Reports compute/energy on automotive hardware | ~none |

Simulator use by era shows the field *slowly* modernising (NS-2 dominance 2013–17 → SUMO+OMNeT++/Veins
2022–26), but NS-2 persists in recent low-tier venues.

**Bottom line for anyone writing a new paper:** the methodological ceiling in this field is low enough that a
rigorous, reproducible, public-dataset, adversarially-tested evaluation is itself a publishable contribution.
