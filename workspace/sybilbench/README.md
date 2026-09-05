# sybilbench — leakage-controlled tooling for the VeReMi Sybil archives

Built for the dataset audit (`../synthesis/08_dataset_audit.md`). Every component exists because a measured
artefact makes the naive approach wrong.

## Modules

| file | role |
|---|---|
| `loader.py` | Parses `<Family>_<density>.zip` → (public `view`, `truth`). Hashes pseudonyms to identity-free tokens (defeats Finding 1's `sender`-in-`senderPseudo` leakage); labels every vehicle from the *full* filename list so subsampling can never change a label; streams per window with float32 kinematics (full-archive row lists reached 14.6 GB). |
| `analysis.py` | `token_features` (per-identity behaviour), `pair_candidates` / `pair_features` (co-observed identity pairs), `label_pairs` (ground truth, evaluation only). |
| `run_ingest.py` | Parses all 8 Sybil archives to a parquet cache. `MAX_RECEIVERS=400` per window bounds memory; labels are unaffected. |
| `exp1_linkage.py` | Experiment 1: pairwise same-vehicle linkage with vehicle-disjoint splits and the geometry/timing ablation. |
| `pseudonym_layer.py` | Synthetic pseudonym-change policy (re-key every τ s), sequential (tracking) pair construction, and `gap_matched` negative resampling. |
| `exp2_pareto.py` | Experiment 2 (superseded): first Pareto attempt; kept to document the biases found. |
| `exp2b_pareto_controlled.py` | Experiment 2b: fixed cohort, a-priori features, concurrency filter. |
| `exp2c_pareto_final.py` | Experiment 2c: both heads trained with vehicle-disjoint splits (tracking underpowered — see Finding 11). |

## Reproduce

```bash
python workspace/sybilbench/run_ingest.py      # ~5 min, writes cache/*.parquet
python workspace/sybilbench/exp1_linkage.py    # ~3 min, writes exp1_results.csv
```

## Design rules

1. **The model never sees `truth`.** `Truth` is a separate object; `view` carries no `sender` and no raw
   pseudonym. Ground truth is used for labels, grouping and scoring only.
2. **Splits are vehicle-disjoint.** Random k-fold over pooled rows (as in the most-cited recent ML paper on
   this data) lets one vehicle appear in train and test.
3. **Always report the geometry-only ablation.** Timing alone reaches AUC ≈ 1.0 (Finding 9); a headline
   number without the ablation says nothing about physical detection.
4. **Deduplicate on `messageID` before any sender-level statistic.** One BSM is logged once per receiver
   (median 6.4 copies); grouping across receivers collapses cadence to ~1e-7 s and silently inflates
   pairwise timing features. This bug produced a wrong first version of Finding 9.
5. **Gap-match negatives in tracking experiments**, or the score partly measures *when* an identity
   reappeared rather than whether it is the same vehicle (worth ~0.10 AUC here).
6. **Hold the population fixed across policy settings.** Sweeping τ silently changes which vehicles re-key
   at all (36 % at τ=120 s vs 95 % at τ=15 s, and the survivors are 47 % longer-lived).
7. **Never select the scoring feature on the data you report.** Best-of-five selection inflated detection by
   **0.232 AUC**.
8. **Match evidence per identity when comparing policies.** Both heads rise with messages per identity at
   constant τ (Finding 12), so unmatched comparisons measure observation budget, not policy.
