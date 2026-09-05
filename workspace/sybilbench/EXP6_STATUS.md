# Pending runs — code ready, execution blocked in the authoring session

Three things are written, reviewed and ready; none has been executed because auto mode blocked Python
execution part-way through the session. Run them in a fresh session or with default permissions.

```bash
cd "F:/d app/research paper"

# 1. the asymmetry test (details below)
python -u workspace/sybilbench/exp6_rsu_vantage.py GridSybil_1416 >  workspace/sybilbench/exp6c.log 2>&1
python -u workspace/sybilbench/exp6_rsu_vantage.py GridSybil_0709 >> workspace/sybilbench/exp6c.log 2>&1

# 2. how much published performance is dataset artefact  (Paper A's headline number)
python -u workspace/sybilbench/exp7_leakage_quantified.py > workspace/sybilbench/exp7.log 2>&1

# 3. smoke-test the VeReMi-2018 loader, which is the only source of real RSSI
python -u workspace/sybilbench/loader_veremi2018.py
```

**Experiment 7** runs one pipeline under two protocols: *naive* (per-`sender` aggregation using ground-truth
identity, pseudonym offered as a feature, random k-fold, native ~30 % prevalence — reconstructed from common
practice in the corpus) versus *controlled* (aggregation on observable identity only, vehicle-disjoint splits,
prevalence subsampled to 3 %). The AUC/AP gap is the inflation attributable to the artefacts in Findings 1, 4
and 8. Writes `exp7_leakage_quantified.csv`.

**loader_veremi2018.py** parses the 2018 release (nested `.tgz` inside the zip) and exposes the `RSSI` field
plus `rssi_features()` at link level, which is what Xiao 2006 and Voiceprint 2017 need. Attacks there are
position falsification, not Sybil — that limitation is the point of Finding 3.

---

# Experiment 6 (RSU vantage) — the asymmetry test

Tests whether an **infrastructure vantage point** escapes the evidence tension of Findings 12/15: does a
static observer gain *detection* power without granting equal *tracking* power? If yes, it is the first
measured escape from the linkability dilemma. If it raises both equally, the dilemma survives.

VeReMi contains no RSUs, so one is emulated: a fixed point receiving every transmission whose claimed
position falls within 300 m, for the whole window. RSU sites are placed at the busiest 300 m cells
(intersection proxies), non-adjacent.

## Two methodological problems found and fixed while running it

**P1 — candidate sampler emptied the positive class.** `pair_candidates` caps dense receivers at 60 tokens to
bound the quadratic pair space. Fine for a vehicle (tens of neighbours); fatal for an RSU view of ~1 400
identities, where a random 60 almost never contains two ghosts of one attacker. First run returned
**detection_pos = 0** and an undefined AUC. Fixed by `analysis.overlap_pairs()`, which pairs identities whose
presence intervals actually overlap instead of subsampling tokens.

**P2 — the comparison was not like-for-like.** After the P1 fix, the "vehicle" condition scored the *pooled*
view (all receivers together), i.e. a global omniscient observer, against a single spatially-restricted RSU.
That comparison is meaningless. Fixed: each vehicle observer is now scored on **only what it received**
(12 busiest receivers, averaged), exactly as each RSU is scored on only what it heard, with the pooled view
kept separately as a labelled upper bound.

## Provisional numbers — do NOT cite

From the P1-fixed but P2-broken run (RSU-local vs global pooled, τ = 30 s, GridSybil_1416):

| vantage | identities | msgs/id | tracking AUC | detection AUC |
|---|---|---|---|---|
| RSU (local) | 1 406 | 28.6 | 0.799 ± 0.030 | 0.689 ± 0.010 |
| pooled global | 6 135 | 26.0 | 0.808 ± 0.005 | 0.703 ± 0.007 |

This says only that a spatially-restricted observer is slightly worse than an omniscient one on both heads —
unsurprising, and not the question. It is *suggestive* that no asymmetry appeared (detection did not rise
relative to tracking), but the correct test is the pending run.

## To finish

```bash
cd "F:/d app/research paper"
python -u workspace/sybilbench/exp6_rsu_vantage.py GridSybil_1416 > workspace/sybilbench/exp6c.log 2>&1
python -u workspace/sybilbench/exp6_rsu_vantage.py GridSybil_0709 >> workspace/sybilbench/exp6c.log 2>&1
```

Runtime ~10 min per archive. Output: `workspace/sybilbench/exp6_rsu_vantage.csv`, with `vantage` ∈
{`vehicle`, `rsu`, `global`}.

**What to read from it.** Compare `rsu` against `vehicle` (both single observers):

- detection rises **more** than tracking → asymmetry exists; infrastructure is a genuine escape, and the
  Footprint premise is vindicated in measurement.
- both rise by similar amounts → no escape; the RSU is just another evidence accumulator, and Finding 15's
  three-way tension stands as the general result.

The second outcome is what Finding 12 predicts.
