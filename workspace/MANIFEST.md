# Manifest

Generated 2026-09-06.
SHA-256 of every file that produced a number in the paper.

## Environment

```
python           3.13.7
platform         Windows-10-10.0.19045-SP0
numpy            2.4.3
pandas           3.0.1
sklearn          1.9.0
scipy            1.18.0
matplotlib       3.11.1
pyarrow          25.0.1
```

## loader and analysis

```
2a06c316c597ead8  sybilbench/loader.py
9600dfcc38c3ea54  sybilbench/loader_veremi2018.py
572b4f24e39027a2  sybilbench/analysis.py
32cd805a3eb7882f  sybilbench/pseudonym_layer.py
```

## experiments

```
2b14b391c6573e8e  sybilbench/exp10_sensitivity.py
6730abe46356a3ec  sybilbench/exp13_pseudonym_decode.py
592bc55b587449d1  sybilbench/exp14_single_factor.py
bf2c86eb1db79f01  sybilbench/exp1_linkage.py
bb54e3b6e793bc50  sybilbench/exp1b_rate_baseline.py
0629874cb7659365  sybilbench/exp2_pareto.py
44dd0484df245b15  sybilbench/exp2b_pareto_controlled.py
7dacafb6040e9df5  sybilbench/exp2c_pareto_final.py
c6b04a9937941c7d  sybilbench/exp4_replicate.py
a9243971021905f8  sybilbench/exp6_rsu_vantage.py
a1fc4192d9dd911a  sybilbench/exp7_leakage_quantified.py
719bc8f14aad09ae  sybilbench/exp8_rssi_2018.py
ac573ad3e4ffd8e8  sybilbench/exp8b_position_verification.py
b4ef5f041f037421  sybilbench/exp9_cascade.py
```

## independent verification

```
9b3992e9249d666f  verify/v10_pseudonym_change.py
c416100ac9754ceb  verify/v11_reporting_table.py
29f3f4a9699fb047  verify/v12_corpus_facts.py
e2130df54aa5c359  verify/v14_match_matrix.py
14f20c6461f42daa  verify/v15_nextgen_shortcuts.py
81b3f19ecc542cc5  verify/v16_nextgen_identifier.py
b6134d8e721aec70  verify/v17_master_census.py
991999156abd0c84  verify/v18_information.py
3463ea99e2cb0a39  verify/v19_table_reproduction.py
4727a0010d155915  verify/v1_raw_structure.py
88ca5bef0cff5c8d  verify/v1b_raw_refined.py
7c1762af553adde1  verify/v20_release_splits.py
11f7028484868303  verify/v21_attacker_budget.py
c1126a86012114cd  verify/v2_metrics.py
dcce2e60aa2c28d8  verify/v3_pseudomap.py
95421130d32bb499  verify/v3b_pseudomap_full.py
7173c0b167f10658  verify/v3c_identity_census.py
acdf3e01f0502d3b  verify/v4_timing_distributions.py
2332d2a96ccf483c  verify/v5_pathloss_replicate.py
9d2f7851cb74aa7e  verify/v6_prevalence_floor.py
5be4c04d393add15  verify/v7_dataset_usage.py
cefc10704cb96962  verify/v8_nextgen_probe.py
599cc888235f8510  verify/v9_derivative_audit.py
```

## paper

```
dc204730b5a5cf1a  paper/assemble.py
fa01281acd29122f  paper/audit_numbers.py
8360eaa9d123101b  paper/bibliography.tex
19f441089f953928  paper/body_new.tex
727cff28c548ee21  paper/check_claims.py
37112bdb6db76bfe  paper/check_refs.py
bc0f69a2bf1d16ad  paper/check_sentences.py
f612d20e94d516ca  paper/fig_ablation.pdf
3ab0769674968b92  paper/fig_abstract.pdf
a31a53e9584b1ae7  paper/fig_decode.pdf
703ec678898a2f70  paper/fig_prevalence.pdf
d9fbd314d6411591  paper/find_corruption.py
a03c4116913fb881  paper/fix_criticals.py
f56ee469ac40a052  paper/make_fig_abstract.py
e5805bd4ff1564b1  paper/make_figure.py
9ecaa932f6b9a0db  paper/make_figures_2_3.py
64d52459ef5592c2  paper/make_journal.py
d8993c2392929715  paper/veremi_audit.pdf
f6d9359f55123865  paper/veremi_audit.tex
8bcee887a23f0c3b  paper/veremi_audit_journal.pdf
02073ac22108a703  paper/veremi_audit_journal.tex
```

## results

```
aad4df3e1b2f520c  sybilbench/exp10_sensitivity.csv
cd84661e9359f5ec  sybilbench/exp13_pseudonym_decode.csv
85be5d521fc81ff2  sybilbench/exp14_single_factor.csv
22114ff68513dcc2  sybilbench/exp1_results.csv
1bd1f8b94a4a940c  sybilbench/exp1b_rate_baseline.csv
10e9a2944d861f97  sybilbench/exp1b_rate_baseline_v2.csv
3a449284da592528  sybilbench/exp2_pareto.csv
cd30b28c6a3de0df  sybilbench/exp2b_pareto_controlled.csv
5716e7fea77f83e1  sybilbench/exp2c_pareto_final.csv
183fb7d4ec47728c  sybilbench/exp3_silence.csv
204e9bed4673cc9d  sybilbench/exp3b_silence_matched.csv
cdd2489ffdf23f93  sybilbench/exp4_evidence.csv
36db66409a02885d  sybilbench/exp4_pareto.csv
58802704bfef0370  sybilbench/exp4_silence.csv
199c2c9fbae84da9  sybilbench/exp5_silence_deployment.csv
cf286bda283dcdd7  sybilbench/exp6_rsu_vantage_GridSybil_0709.csv
e00e5a7c3d9ca6e7  sybilbench/exp6_rsu_vantage_GridSybil_1416.csv
97d45ec6c86fbfe4  sybilbench/exp7_leakage_quantified.csv
2146d09da9796f97  sybilbench/exp7_leakage_quantified_norate.csv
d0a51f8dbe6c8c4c  sybilbench/exp8_rssi_2018.csv
a9a02388647c1940  sybilbench/exp8b_position_verification.csv
06f12da24f32dfa1  sybilbench/exp9_cascade.csv
36ba8354afd7aaa4  sybilbench/exp9_cascade_logistic_partial.csv
c726e3817be6b17d  sybilbench/pareto_final.csv
9ecbb270d6ffc5ea  verify/master_archive_table.csv
91e43b39b7dcbe85  verify/v10_pseudonym_change.csv
ca91e4c512b0acb2  verify/v11_reporting_table.csv
236254783deac1ed  verify/v12_corpus_facts.csv
d92dfdfe7803d8ef  verify/v12_ns2_papers.csv
7f8cc04dd24d2cd4  verify/v14_match_matrix.csv
c74c7a30dcb14eea  verify/v15_nextgen_shortcuts.csv
42a37a3988a7e4de  verify/v16_nextgen_identifier.csv
cce39ed932fcf5f4  verify/v17_master_census.csv
c617b6eb7596bdc3  verify/v18_information.csv
e21c4db5eae9e799  verify/v1_raw_structure.csv
9311873593baccdb  verify/v1b_raw_refined.csv
f0c11ae98739f275  verify/v20_splits.csv
0e692f1f9d41eddc  verify/v21_attacker_budget.csv
84cdf35c05f0e0d5  verify/v3b_pseudomap.csv
8eb01a7972712070  verify/v3c_identity_census.csv
d3ea5bcfad8222bb  verify/v4_timing_distributions.csv
91cd0bd4350588c4  verify/v5_pathloss.csv
431ba9fd5b07ec79  verify/v6_prevalence_floor.csv
639bc8011c1738f0  verify/v7_dataset_usage.csv
b440342c29a56fa5  verify/v8_nextgen_probe.csv
a55e312f80f11734  verify/v9_derivative_audit.csv
bc6d33a53b2bf6e5  verify/v9_derivative_summary.csv
```
