# Reading List — the 22 papers to actually read, in order

All files are in `../pdfs/`. Read in this order; it follows the argument of `01_field_evolution.md`.
Time estimate: ~15–20 hours for the whole list, or ~4 hours for the ★ core eight.

## Stage 1 — Foundations (read these eight first) ★

| # | Read | Why | File |
|---|---|---|---|
| 1 ★ | **Xiao, Yu, Gao 2006** — Detection and localization of Sybil nodes (252 cites) | The founding VANET paper. RSS statistics + position verification + RSU support. Everything descends from here. | `2006_Xiao_Detection_and_localization_of_sybil_nodes_in_VANETs.pdf` |
| 2 ★ | **Guette & Ducourthial 2007** — On the Sybil attack detection in VANET (99) | The attacker's side: power tuning and antennas break RSS methods. The limit nobody has closed. | `2007_Guette_On_the_Sybil_attack_detection_in_VANET.pdf` |
| 3 ★ | **Zhou et al. 2007** — Privacy-Preserving Detection (P2DAP) (87) | Where privacy-vs-detection becomes the field's central tension. | `2007_Zhou_PrivacyPreserving_Detection_of_Sybil_Attacks_in_Vehicular_Ad_Hoc_Networks.pdf` |
| 4 | **Bouassida et al. 2007/09** — RSSI variations, distinguishability degree (74) | Rare: geometry + simulation + **real measurements**. | `2007_Bouassida_Sybil_Nodes_Detection_Based_on_Received_Signal_Strength_Variations_within_VANET.pdf` |
| 5 ★ | **Park et al. 2009** — RSU-supported timestamp series (124) | Kills the PKI assumption; explicitly targets sparse early deployment. | `2009_Park_Defense_against_Sybil_attack_in_vehicular_ad_hoc_network_based_on_roadside_unit_support.pdf` |
| 6 ★ | **Chang et al. 2011** — Footprint (TPDS, 143) | The pivotal trajectory-as-identity paper; the baseline everyone (badly) re-implements. | `2011_Chang_Footprint_Detecting_Sybil_Attacks_in_Urban_Vehicular_Networks.pdf` |
| 7 | **El Zoghby et al. 2012** — Distributed data fusion, belief functions (15) | The evidence-theoretic branch; crypto-free confidence building. | `2012_Zoghby_Distributed_Data_Fusion_for_Detecting_Sybil_Attacks_in_VANETs.pdf` |
| 8 ★ | **Feng et al. 2016** — EBRS, multi-source Sybil (81) | Names the still-open problem: conspiring attackers with legitimate identities. | `2016_Feng_A_method_for_defensing_against_multisource_Sybil_attacks_in_VANET.pdf` |

## Stage 2 — The statistical / traffic-physics turn

| # | Read | Why | File |
|---|---|---|---|
| 9 ★ | **Yao/Xiao et al. 2017** — Voiceprint (DSN) | RSSI *time series* + DTW, model-free, distributed, with real experiments. The best physical-layer idea in the corpus. | `2017_Yuan_Voiceprint_A_Novel_Sybil_Attack_Detection_Method_Based_on_RSSI_for_VANETs.pdf` |
| 10 ★ | **Ayaida et al. 2019** — Macroscopic traffic model (Ad Hoc Networks, 54) | Detects Sybils by contradicting the traffic fundamental diagram. No crypto, no RSU. | `2019_Ayaida_A_Macroscopic_Traffic_Modelbased_Approach_for_Sybil_Attack_Detection_in_VANETs.pdf` |
| 11 | **Dutta & Chellappan 2013** — Fuzzy time-series clustering / platoon dispersion | The cyber-physical framing: real cars disperse, clones don't. | `2013_Dutta_A_Timeseries_Clustering_Approach_for_Sybil_Attack_Detection_in_Vehicular_Ad_hoc_Networks.pdf` |
| 12 | **Grover et al. 2015** — Multivariate verification (Open Comp. Sci., 14) | Implements three Sybil variants and measures network damage, not just detection. | `2015_Grover_Multivariate_verification_for_sybil_attack_detection_in_VANET.pdf` |
| 13 | **Almutaz et al. 2014** — Detecting Sybil attacks in vehicular networks (J. Trust Mgmt, 16) | Platoon-dispersion protocol, clean write-up of the physics argument. | `2014_Almutaz_Detecting_Sybil_attacks_in_vehicular_networks.pdf` |

## Stage 3 — Hardness, credentials, architecture

| # | Read | Why | File |
|---|---|---|---|
| 14 ★ | **Baza et al. 2020** — Proofs of Work and Location (IEEE TDSC, 21) | Prices identities in CPU instead of detecting them. The bridge to modern designs. | `2020_Baza_Detecting_Sybil_Attacks_Using_Proofs_of_Work_and_Location_in_VANETs.pdf` |
| 15 | **Akil et al. 2023** — Non-interactive, Sybil-free authentication (VehicleSec) | Attribute-based credentials; structurally prevents concurrent pseudonyms. Cleanest answer to the 2007 tension. | `2023_Akil_NonInteractive_PrivacyPreserving_SybilFree_Authentication_Scheme_in_VANETs.pdf` |
| 16 | **Khatri et al. 2024** — Blockchain proof-of-location (Sensors, 12) | Smart contract as location ground truth + RSU puzzles. | `2024_Khatri_Sybil_AttackResistant_BlockchainBased_ProofofLocation_Mechanism_with_Privacy_Protection_in.pdf` |
| 17 | **Hadri et al. 2026** — Verifiable delay functions + fog/cloud (JCP) | Newest hardness primitive: sequential work resists parallel attackers. | `2026_Hadri_A_Novel_Approach_to_Sybil_Attack_Detection_in_VANETs_Using_Verifiable_Delay_Functions_and.pdf` |
| 18 | **Funderburg & Lee 2021** — Hierarchical key management, short group signatures (Sensors, 24) | The credential-management view of the same problem. | `2021_Funderburg_A_PrivacyPreserving_Key_Management_Scheme_with_Support_for_Sybil_Attack_Detection_in_VANET.pdf` |

## Stage 4 — The learning era and the new surfaces

| # | Read | Why | File |
|---|---|---|---|
| 19 ★ | **Azam et al. 2022** — Collaborative learning ensemble (Sensors, 65) | Most-cited recent paper; one of the few using VeReMi. Read it as the state of ML practice — and note the missing generalisation tests. | `2022_Azam_Collaborative_Learning_Based_Sybil_Attack_Detection_in_Vehicular_ADHOC_Networks_VANETS.pdf` |
| 20 | **Taysi & Güven 2025** — LSTM/CNN on RSSI time series | Voiceprint with a learned metric; also documents why existing datasets are inadequate. | `2025_Taysi_A_better_way_to_detect_sybil_attacks_in_vehiuclar_ad_hoc_networks.pdf` |
| 21 | **Almesaeed 2025** — Channel characterisation, angular spread | Best recent physical-layer advance: RSSI + azimuth/elevation spread from ray tracing. | `2025_Almesaeed_Realtime_Sybil_Attack_Detection_Based_on_Channel_Characterization_in_VANET.pdf` |
| 22 ★ | **Söderhäll & Papadimitratos 2025** — Sybil attacks on mobile crowdsensing for transportation | Moves the attack to app level (Waze-style navigation), targets high-betweenness roads, measures travel-time damage. The most realistic modern threat model in the corpus. | `2025_Sderhll_On_the_Impact_of_Sybilbased_Attacks_on_Mobile_Crowdsensing_for_Transportation.pdf` |

## Optional — context and contrast

- **Junaidi et al. 2022** — platoon management against Sybils (`2022_Junaidi_...`) — the platooning surface.
- **Khan et al. 2026** — robust framework, FPR reduction in sparse/dense regions (`2026_Khan_...`) — recent, arXiv.
- **Nishtha & Kumar 2025 (×2)** — Sybil impact across every routing-protocol family (`2025_Nishtha_...`).
- **Güven & Tayşi 2024/2025** — the Istanbul dataset papers (`2024_Guven_...`, `2025_Guven_...`). Read the
  requirements analysis (why existing datasets fail for RSSI), but note the artefact is now restricted and the
  authorship is disputed — see `../CODE_AND_DATASETS.md`.
- Skip the metaheuristic-hybrid tail (spider monkey / emperor penguin / elephant herding / frilled lizard /
  ship rescue optimisation). Read one — e.g. `2026_B_EFLOQDCNN_...` — to see the pattern, then stop; they add
  optimisers, not insight, and none is reproducible.

## Not obtainable (paywalled, no OA copy) — but you should know them

| Paper | Why it matters | DOI |
|---|---|---|
| Yu, Xu, Xiao 2013 — *Detecting Sybil attacks in VANETs* (JPDC, 182 cites) | Journal extension of the 2006 line | 10.1016/j.jpdc.2013.02.001 |
| Zhou et al. 2011 — *P2DAP* (IEEE JSAC, 160) | Journal version of #3 | 10.1109/jsac.2011.110308 |
| Yao et al. 2018 — *Multi-Channel RSSI* (IEEE TMC, 122) | Voiceprint's successor | 10.1109/TMC.2018.2833849 |
| Chen et al. 2009 — *Robust Detection in Urban VANETs* (98) | Motion-trajectory anomaly | — |
| Yao et al. 2019 — *Power Control Identification* (IEEE JSAC, 62) | Directly answers Guette 2007's attack | 10.1109/JSAC.2019.2933888 |

Request these via your library, ILL, or the authors (see `../README.md` for the full list).
