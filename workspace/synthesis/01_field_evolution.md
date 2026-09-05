# Sybil Attacks in VANETs — How the Field Started, How It Changed, Where It Is Now

Written from the 92 full-text papers in `pdfs/` plus metadata for all 331 papers in `index.csv`.
Papers marked **[corpus]** are in the local collection; items marked **[background]** are foundational works
referenced repeatedly *inside* those papers but not held locally (they are not VANET-specific).

---

## 0. The one-paragraph version

The Sybil attack was defined for peer-to-peer systems in 2002 and imported into vehicular networks around
2004–2006, where it became the "root attack": one car pretending to be many cars can fake a traffic jam,
win a majority vote, or poison a reputation system. The first VANET-specific defences (2006–2009) were
**physical**: measure the radio signal and check whether the claimed positions can physically exist. When
those proved fragile, the field moved to **infrastructure-issued proofs** (2009–2015): roadside units stamp
a vehicle's passage, and a trajectory of such stamps becomes an unforgeable-but-anonymous identity. From
2016 the emphasis shifted to **statistical and learning-based** detection — RSSI time series, traffic-flow
models, then classical ML, then deep learning — and after 2020 to **cryptographic hardness and
architecture**: proofs of work/location, blockchain, verifiable delay functions, fog/edge offloading, 5G.
Along the way the *problem* barely changed, the *assumptions* changed enormously, and the *evaluation
quality* went backwards: today's papers report higher accuracies on weaker, less reproducible evidence
than the 2007–2013 papers did.

---

## 1. Pre-history (2002–2005): where the idea comes from

| Work | What it established |
|---|---|
| Douceur, *The Sybil Attack* (2002) **[background]** | Formal statement: without a trusted central identity authority, a single entity can present arbitrarily many identities; no purely local, resource-free scheme can prevent it. Cited by essentially every paper in this corpus — Park 2009, Feng 2016, Stępień 2021, Almesaeed 2025 all open with it. |
| Newsome et al., Sybil attack in sensor networks (2004) **[background]** | The defence taxonomy the VANET field inherited wholesale: *resource testing, radio-resource testing, registration, position verification, code attestation*. Kushwaha's 2014 survey **[corpus]** still uses these categories verbatim. |
| Golle, Greenstein, Raya, Hubaux (2004); Raya & Hubaux VANET security model (2005–07) **[background]** | Reframed the problem as *data consistency* rather than identity, and set the VANET adversary model (insider/outsider, malicious/rational, local/extended) that the corpus reuses. |

**Why VANETs made it urgent.** Safety applications are *voting machines*: congestion warnings, cooperative
awareness, and reputation systems all trust the count of independent reporters. Sybil identities are
therefore not one attack among many but the enabler of many — the phrase "root cause of many other attacks"
recurs from Park 2009 through Ayaida 2019.

---

## 2. Era 1 — Physical-layer detection, no PKI assumed (2006–2009)

The founding assumption: vehicles cannot be trusted to prove who they are, so let *physics* do it. A single
radio cannot be in five places at once.

| Year | Paper (corpus) | Idea | What it proved |
|---|---|---|---|
| 2006 | **Xiao, Yu, Gao — Detection and Localization of Sybil Nodes in VANETs** (252 cites, the most-cited paper in the corpus) | Signal-strength-based position verification, hardened by *statistical* analysis of the RSS distribution over time, plus traffic-pattern and roadside-base-station support | Naive single-shot RSS verification is inaccurate and spoofable; time-aggregated statistics fix much of it. Set the template: distributed, localized, no per-vehicle PKI. |
| 2007 | **Guette & Ducourthial — On the Sybil attack detection in VANET** (99) | Adversary-side quantification: how antenna type and transmit-power tuning change attack success | The first "negative result": an attacker who tunes power or uses directional antennas defeats RSS-based schemes. Every later RSSI paper cites this as the limit to beat. |
| 2007/09 | **Bouassida, Guette, Shawky, Ducourthial — Sybil Nodes Detection Based on RSS Variations** (74) | *Distinguishability degree* metric between nodes from RSSI variation; validated geometrically, in NS-2, **and with real measurements** | One of very few works in the entire corpus with real radio measurements rather than pure simulation. |
| 2007 | **Zhou, Roy Choudhury, Ning, Chakrabarty — Privacy-Preserving Detection of Sybil Attacks (P2DAP)** (87) | DMV issues pools of pseudonyms that hash into coarse-grained groups; RSUs detect same-group reuse and only a central authority can de-anonymize; Threshold-P2DAP extends it to colluders | Framed the tension that still defines the field: **detection wants linkability, privacy forbids it.** |
| 2009 | **Park, Aslam, Turgut, Zou — Defense based on roadside unit support** (124) | *Timestamp series*: RSUs (not vehicles) issue certificates; two messages carrying near-identical RSU timestamp series must come from one physical vehicle | Removed the requirement for a full vehicular PKI, and explicitly targeted the *initial deployment stage* (sparse RSUs, few equipped cars) — a deployment realism almost absent from later work. |

**Era 1 in one line:** cheap, infrastructure-light, physics-grounded — and honest about its limits.

---

## 3. Era 2 — Infrastructure-issued trajectories and the privacy fight (2010–2015)

RSS alone lost. The field's answer: let the *road* certify the car, anonymously.

- **Chang, Qi, Zhu, Zhao, Shen — Footprint** (TPDS 2011, 143 cites) **[corpus]** is the pivotal paper. Each
  RSU issues a *location-hidden authorized message*; signer-ambiguous signatures hide which RSU signed;
  short-term linkability lets a receiver recognise a consistent trajectory without long-term tracking.
  Reported >98 % detection. It became the baseline everyone compares against — and the thing everyone
  re-implements badly (four separate corpus papers from 2014 are essentially Footprint restatements:
  Perumal, Suganya, D. Balamahalakshmi, Kumari).
- **Zhou et al., P2DAP journal version** (JSAC 2011, 160) and **Yu, Xu, Xiao — Detecting Sybil attacks in
  VANETs** (JPDC 2013, 182) are the two most-cited works of the era. *Neither has an open-access copy —
  see `README.md` "no free copy" list.*
- **Cyber-physical modelling arrives.** Dutta & Chellappan's fuzzy time-series clustering (2013) **[corpus]**
  and Almutaz's platoon-dispersion protocol (2013 thesis / 2014 J. Trust Management) **[corpus]** argue that
  *traffic physics* — real vehicles disperse over time, Sybil clones do not — is a free, hardware-less signal.
- **Grover et al., Multivariate verification** (Open Computer Science 2015) **[corpus]** implements three
  Sybil variants and measures their *network-performance* damage, not just detection: an early attempt at
  attack characterisation rather than defence-only papers.
- **El Zoghby, Cherfaoui, Ducourthial, Denœux — Distributed data fusion** (2012) **[corpus]** brings
  Dempster–Shafer belief functions: confidence about neighbours is built by fusing distributed opinions,
  explicitly aiming to avoid cryptography.
- **Feng et al., EBRS** (P2P Netw. Appl. 2016, 81 cites) **[corpus]** targets what earlier schemes ducked:
  *conspired* Sybil attacks launched with legitimate identities, using per-event reputation and trust values.

**Era 2 in one line:** RSU-anchored, privacy-aware, trajectory-based — and the first serious treatment of collusion.

**Also visible in this era: the literature's quality split begins.** From 2014 the yearly paper count jumps
(11 → 21 → 19 → 18) and a large share is low-tier restatement. Of the 331 indexed papers, **110 have zero
citations** and the median is 3.

---

## 4. Era 3 — Statistics, signal time-series, and the first ML wave (2016–2020)

Three parallel strands:

**(a) Physical layer, done properly.**
*Voiceprint* (Yao, Xiao et al., DSN 2017) **[corpus]** stops estimating position from RSSI — it treats the
RSSI series as a "vehicular speech" signal and compares series by **dynamic time warping**, so it needs no
radio-propagation model and no cooperation from neighbours. >90 % detection, <10 % FPR, with real-world
experiments. Its successors (Xiao's group: *Multi-Channel RSSI*, TMC 2018, 122 cites; *Power Control
Identification*, JSAC 2019, 62 cites — both paywalled, not in `pdfs/`) push the same idea into multi-channel
and power-control-aware settings. Samhitha et al. 2019 **[corpus]** is a re-implementation.

**(b) Traffic-flow models as the detector.**
Ayaida, Messai, Najeh, Ndjore — *A Macroscopic Traffic Model-based Approach* (Ad Hoc Networks 2019, 54)
**[corpus]** has each vehicle compare its *own measured speed* with the speed predicted from V2V-reported
neighbourhood density via the traffic-flow fundamental diagram. Sybil clones inflate density without
changing physical speed → contradiction. >90 % detection, no crypto, no RSU.

**(c) Machine learning enters — and datasets appear.**
The corpus shows ML/DL going 4 → 13 → 27 mentions across eras. Crucially, the *evaluation substrate* also
appeared here, from outside the Sybil literature:
- **VeReMi** (van der Heijden et al., 2018) — first public misbehaviour-detection dataset for VANETs (LuST
  traffic, position-falsification attacks incl. Sybil-adjacent variants). 3.6 GB, CC-BY.
- **F2MD** (Kamel et al.) — the misbehaviour-detection simulation framework that generates it.
- **VeReMi Extension** (2020) — 19.9 GB, adds *explicit Sybil families*: `GridSybil`, `DataReplaySybil`,
  `DoSRandomSybil`, `DoSDisruptiveSybil`.
Both are now in `workspace/datasets/`. **Only 9 of the 92 read papers use any named public dataset at all.**

Also here: **Baza, Nabil, Mahmoud et al. — Proofs of Work and Location** (IEEE TDSC 2020) **[corpus]**, which
makes trajectory forgery *computationally* expensive: an RSU issues a time-stamped anonymous location tag,
and the vehicle must solve a PoW puzzle per tag, so maintaining k parallel fake trajectories costs k× CPU.
This is the bridge from Era 2's cryptographic proofs to Era 4's hardness-based designs.

---

## 5. Era 4 — Deep learning, blockchain, fog, and new attack surfaces (2021–2026)

Volume peaks here: 2024 is the biggest year in the index (40 papers), 2025 second (35).

**Deep learning becomes the default.**
- Azam et al., *Collaborative Learning Based Sybil Attack Detection* (Sensors 2022, 65 cites) **[corpus]** —
  majority-vote ensemble of KNN / naive Bayes / random forest / decision tree on **VeReMi**. The most-cited
  recent paper, and one of the few using a public dataset.
- Taysi & Güven (2025) **[corpus]** — LSTM and CNN over **RSSI time series** (93.45 % / 94.28 % sensitivity),
  i.e. Voiceprint's idea with a learned similarity function instead of DTW.
- Sefati et al. (2025) **[corpus]** — VANET as a *time-evolving graph*; spatio-temporal beacon features
  (displacement, speed variation, directional change, beacon frequency, trust, behavioural similarity) +
  similarity clustering + XGBoost.
- Almesaeed & Al-Sherbaz (2025) **[corpus]** — adds **angular spread** (azimuth + elevation) from ray-traced
  channel statistics to RSSI: the sharpest physical-layer advance in the recent corpus.
- A large tail of *metaheuristic + deep net* hybrids: spider-monkey + ECC (2019), Emperor Penguin routing
  (2021), Elephant Herding + chaotic-map CNN (2025), Adaptive Ship Rescue Optimisation + Deep Kronecker
  Network (2025), Exponential Frilled Lizard Optimisation + Quantum Dilated CNN (2026). These report
  90–99 % on unnamed private simulations and are, as a group, the weakest evidence in the corpus.

**Cryptographic hardness and architecture.**
- Akil et al., *Non-Interactive Privacy-Preserving Sybil-Free Authentication* (VehicleSec 2023) **[corpus]** —
  attribute-based credentials + short-lived pseudonyms; vehicles self-generate pseudonyms after a single
  registration, with no online authority, and *cannot* hold concurrent valid pseudonyms. This is the
  cleanest modern answer to the 2007 privacy-vs-detection tension.
- Khatri, Nam, Lee (Sensors 2024) **[corpus]** — blockchain smart contract as the proof-of-location ledger,
  RSU-generated puzzles bounding identities per CPU.
- Hadri et al. (J. Cybersecurity & Privacy 2026) **[corpus]** — **verifiable delay functions**: inherently
  non-parallelisable sequential work, so extra CPUs don't buy extra identities; hierarchical fog/cloud layers
  do the checking. Claims 97.8 % detection, <2.3 % FPR.
- Funderburg & Lee (Sensors 2021), Man et al. (2024), Zhang et al. (Scientific Reports 2025) **[corpus]** —
  group signatures, batch verification, short-term pseudonyms per RSU jurisdiction for the **Internet of
  Vehicles / 5G** setting.
- Almazroi et al., *FC-LSR* (IEEE Access 2024) **[corpus]** — fog computing + Merkle Patricia trie for
  5G-enabled vehicular networks.

**The attack surface widens.**
- **Platooning:** Junaidi et al. (Sensors 2022) **[corpus]** secure platoon join/leave/merge against fake
  virtual members.
- **Crowdsensing / navigation apps:** Söderhäll & Papadimitratos (PerCom Workshops 2025) **[corpus]** move
  the attack off the ad-hoc network entirely — Sybil accounts in a Waze-style navigation service, targeted at
  high *betweenness-centrality* roads, measured by the travel-time damage to honest users. A different
  threat model (server-side, app-level), and arguably the more realistic deployment of Sybil attacks today.
- **Routing-protocol impact studies:** Nishtha & Kumar (2025, ×2) **[corpus]** systematically show every
  category of VANET routing protocol (topology, position, geocast, cluster, broadcast) is disrupted by Sybil.

**Dataset work — and a cautionary tale.** Güven & Tayşi (2024 preprint / 2025 P2P Netw. Appl.) **[corpus]**
built the first large RSSI-realistic Sybil dataset (Istanbul, OpenStreetMap + calibrated SUMO flows +
log-normal shadowing, ~93 GB, 7 995 vehicles incl. 652 ghost vehicles) precisely because *no public dataset
carries realistic RSSI*. **As of this writing the repository is locked**: the stated dataset owner has
published a takedown/authorship-dispute notice and restricted all data and code (see
`workspace/CODE_AND_DATASETS.md`). The one genuinely reproducible artefact in the modern Sybil-VANET
literature is currently unavailable.

---

## 6. What actually changed, tracked as variables

| Dimension | 2006–2009 | 2010–2015 | 2016–2020 | 2021–2026 |
|---|---|---|---|---|
| Trust anchor | none (physics) | RSU-issued anonymous proofs | statistics + learned models | crypto hardness (PoW/PoL/VDF), blockchain, ABC |
| Identity model | claimed positions | pseudonym pools, group signatures | pseudonyms + behaviour | short-term pseudonyms, self-generated credentials |
| Attacker | naive, fixed power | + colluding, + stolen identities | + power-control aware | + app-level Sybils, platoon infiltration |
| Infrastructure | RSU optional | RSU essential | RSU + cloud | fog/edge/5G, smart contracts |
| Evaluation | analysis + NS-2 + some real measurements | NS-2/SUMO | SUMO/OMNeT++/Veins, first public datasets | same sims + occasional VeReMi; heavy private data |
| Reported performance | ~85–95 %, with stated failure modes | ~98 % | 90–97 % | 94–99.9 % |
| Reproducibility | low | low | low | **still ~zero: 4 of 92 papers mention code; 1 public repo, now restricted** |

**The uncomfortable trend:** claimed accuracy rises monotonically while evidence quality does not. Eleven
corpus papers published in 2021 or later still evaluate in **NS-2** — a simulator whose development stopped
in 2011 and which has no 802.11p/1609.4 stack by default. Papers keep comparing against re-implementations
of Footprint/P2DAP rather than released code, so the "baselines" are not the baselines.

---

## 7. The five ideas that actually survived

1. **Physical impossibility of co-location** (Xiao 2006 → Voiceprint 2017 → angular spread 2025): the only
   signal an attacker cannot forge by software alone.
2. **Anonymous infrastructure-stamped trajectories** (Park 2009 → Footprint 2011 → PoL 2020/2024): identity
   without identification.
3. **Traffic physics as a consistency check** (Dutta 2013, Almutaz 2014, Ayaida 2019): free, model-based,
   deployment-friendly.
4. **Making identities expensive** (P2DAP threshold → PoW/PoL 2020 → VDF 2026): accept that you cannot
   *detect* every Sybil, so *price* them.
5. **Privacy as a first-class constraint, not an afterthought** (P2DAP 2007 → Footprint 2011 → attribute-based
   credentials 2023): the field's most durable intellectual contribution.

## 8. What has *not* moved since 2006

- Nobody agrees on a benchmark, so no two numbers in this literature are comparable.
- Attacker models are still overwhelmingly naive (fixed power, no mobility mimicry, no learning).
- Almost nothing is evaluated against the actual deployed standards (IEEE 1609.2 / ETSI ITS SCMS pseudonym
  certificates, C-V2X Rel-16/17); the corpus is still 802.11p-shaped.
- Real-world radio measurement is rarer now than it was in 2007.
- Detection latency against the 100 ms safety-message deadline is almost never reported, even by papers
  proposing per-message deep networks or on-chain verification.

→ Continue to `03_research_gaps.md` for the itemised gaps and `04_research_questions.md` for the questions
they imply.
