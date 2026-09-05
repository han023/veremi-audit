# Feasibility — what the data actually supports

Round 3 checked something rounds 1–2 did not: **whether the recommended paper can be built from the data that
exists.** I opened the downloaded VeReMi Extension archives and read the record schema. This changed the plan.

---

## 1. VeReMi / VeReMi Extension record schema (measured, not assumed)

Archive layout: outer zip → per-time-window inner zips → one JSON file per receiving vehicle, plus one
ground-truth file per simulation.

```
DataReplaySybil_0709.zip
└── VeReMi_25200_28800_2022-9-13_21:7:46.zip
    ├── traceJSON-9-7-A0-25202-7.json          ← receiver log  (A0 = benign receiver)
    ├── traceJSON-15-13-A17-25207-7.json       ← receiver log  (A17 = attacker type 17)
    └── traceGroundTruthJSON-7.json            ← 189 402 records, all sent messages
```

**Record types inside a receiver log** (measured on `traceJSON-10341-10339-A0-28557-7.json`, 2 461 records):

| type | count | fields |
|---|---|---|
| 3 — received BSM | 2 288 | `rcvTime, sendTime, sender, senderPseudo, messageID, pos, pos_noise, spd, spd_noise, acl, acl_noise, hed, hed_noise` |
| 2 — own GPS | 173 | same minus `sender, senderPseudo, messageID, sendTime` |
| 4 — ground truth | (in GT file) | as type 3 |

Attacker labels come from the **filename** (`A0` benign, `A<n>` attack type) and from the ground-truth file.

### The two findings that matter

**(a) The Extension has NO RSSI field — but the original VeReMi (2018) does.** Measured: VeReMi 2018 type-3
records are `RSSI, messageID, pos, pos_noise, rcvTime, sendTime, sender, spd, spd_noise, type`, with RSSI
populated (1.3e-9 … 2.6e-5 W). The Extension dropped RSSI and added `senderPseudo`.
⇒ **RSSI methods can be benchmarked on VeReMi 2018** (which has no Sybil-specific families, only
position-falsification attacks), and **identity methods on the Extension** (which has no RSSI). No public set
has both plus Sybil labels — see `08_dataset_audit.md` Finding 3.

**(b) Every received message carries BOTH `sender` (true vehicle) and `senderPseudo` (pseudonym).**
A receiver in reality sees only `senderPseudo`; `sender` is ground truth. So VeReMi gives, for free, the
labelled mapping *pseudonym → physical vehicle* — which makes two things directly computable on public data:
- **Sybil detection as pseudonym-linkage**: infer which pseudonyms belong to one vehicle from kinematics.
- **Location-privacy loss**: the *same* linkage, applied to honest vehicles, is a tracking attack.
This is the basis of the newly recommended paper (see `05_new_paper_plan.md`).

## 2. What each detector family needs, and whether the data has it

| Family | Needs | On VeReMi Extension? |
|---|---|---|
| Traffic-flow / macroscopic (Ayaida 2019) | positions, speeds, neighbour density | **Yes** |
| Kinematic plausibility (position/speed/heading consistency) | pos, spd, acl, hed + noise | **Yes** |
| ML on beacon features (Azam 2022, Sefati 2025) | the above, labelled | **Yes** |
| Pseudonym-linkage / concurrency | senderPseudo + timing | **Yes** (and ground truth for it) |
| Timestamp-series (Park 2009) | RSU encounter certificates | **No** — no RSU logs; needs regeneration |
| Trajectory tags (Footprint 2011) | RSU-issued signed tags | **No** — needs regeneration |
| RSSI family (Xiao, Voiceprint, Almesaeed, Taysi) | received signal strength | **No** — see (a) |

**Consequence:** a "six-family benchmark" as scoped in v2 of the plan is **not buildable on VeReMi alone**.
It needs either scope reduction (4 families) or a simulation campaign to regenerate traces with RSSI and RSU
events. That is a real 4–6 week cost, and it is why the recommendation changed.

## 3. F2MD status

`workspace/code/F2MD` is a **shallow clone with empty submodules** (96 files; `veins-f2md`, `simulte-f2md`,
`inet` are submodule stubs). Regenerating data requires:

```bash
cd workspace/code/F2MD && git submodule update --init --recursive   # large
# then OMNeT++ 5.x + SUMO + Veins toolchain to build and run
```

Plan for that only if the RSSI/RSU families are needed (paper 2 or 3), not before.

## 4. Integrity: size checks are not enough

One completed file (`DataReplaySybil_1416.zip`, 163 MB) matched its manifest size but failed CRC — a leftover
of the earlier concurrent-download bug. It was deleted and re-fetched, and now verifies.

The pipeline now checks **Zenodo MD5** rather than size:

```bash
python workspace/verify_datasets.py            # report only
python workspace/verify_datasets.py --delete   # delete corrupt files so the fetcher re-gets them
bash   workspace/fetch_datasets.sh             # resumable, verifies md5 after each file, single-instance lock
```

`workspace/datasets/manifest.tsv` now carries `path · size · url · md5` for all 24 files.

At the time of writing: 9 of 24 files complete (7.2 / 12.4 GB); `VeReMi_Dataset.zip` (3.6 GB),
`DataReplaySybil_0709/1416`, `DoSDisruptiveSybil_0709/1416` and the preprocessed CSV are complete and
**md5-verified** — enough to start work immediately.

## 5. What is buildable *today*, without waiting

1. Pseudonym-linkage engine + Sybil detection + tracking evaluation (the recommended paper) — needs only
   `DataReplaySybil_*` and `DoSDisruptiveSybil_*`, both verified on disk.
2. Kinematic-plausibility and traffic-flow detectors — same data.
3. ML baselines — the preprocessed balanced CSV (760 MB, verified) is the fastest path to a first classifier.
4. Cross-density generalisation (0709 vs 1416) — both densities present.

Blocked until the download finishes: `GridSybil_*` (largest Sybil family), `DoSRandomSybil_*`,
and the NextGen `trafficCongestionSybil` scenarios used for cross-map generalisation.
