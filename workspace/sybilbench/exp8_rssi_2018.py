"""
Experiment 8 — can the physical-layer family be reproduced at all, on the only data that carries RSSI?

Finding 3: VeReMi 2018 has real received power but no Sybil families; the Extension has Sybil families but no
RSSI. So the largest detector family in the literature (33 of 92 corpus papers) can only be exercised here,
against 2018's position-falsification attacks. This experiment establishes what that substrate supports.

Detector: per-link RSSI statistics (mean, sd, min, max, range) — the summary Xiao 2006 computes over a window.
Evaluation: link-disjoint by sender, so a vehicle never appears in both train and test.
"""
import sys
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import GroupShuffleSplit
sys.path.insert(0, "workspace")
from sybilbench import loader_veremi2018 as L

N_ARCH = int(sys.argv[1]) if len(sys.argv) > 1 else 40

view, truth = L.load(max_archives=N_ARCH, max_receivers_per_archive=80)
print(f"rows={len(view)} senders={view['sender'].nunique()} receivers={view['receiver'].nunique()}", flush=True)
f = L.rssi_features(view)
y = L.label(f, truth).to_numpy()
print(f"link rows={len(f)} attacker links={int(y.sum())} ({y.mean():.3%})", flush=True)
fam = pd.Series(list(truth.sender_to_attack.values())).map(lambda a: L.ATTACK_NAMES.get(a, a)).value_counts()
print("attack families:", fam.to_dict(), flush=True)

if y.sum() < 20:
    print("too few attacker links — increase N_ARCH"); sys.exit(0)

FEATS = ["rssi_mean", "rssi_std", "rssi_min", "rssi_max", "rssi_range", "n", "duration"]
X = f[FEATS].to_numpy()
groups = f["sender"].to_numpy()

aucs, aps, singles = [], [], {c: [] for c in FEATS}
for seed in range(5):
    tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed).split(X, y, groups))
    if y[te].sum() < 3 or y[tr].sum() < 3:
        continue
    m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
    m.fit(X[tr], y[tr]); p = m.predict_proba(X[te])[:, 1]
    aucs.append(roc_auc_score(y[te], p)); aps.append(average_precision_score(y[te], p))
    for c in FEATS:
        v = f[c].to_numpy()[te]
        a = roc_auc_score(y[te], v)
        singles[c].append(max(a, 1 - a))
print(f"\nRSSI detector (sender-disjoint): AUC={np.mean(aucs):.4f}+/-{np.std(aucs):.4f}  AP={np.mean(aps):.4f}  (n={len(aucs)} seeds)")
print("single-feature AUCs:", {c: round(float(np.mean(v)), 3) for c, v in singles.items() if v})
pd.DataFrame({"auc": aucs, "ap": aps}).to_csv("workspace/sybilbench/exp8_rssi_2018.csv", index=False)
print("-> workspace/sybilbench/exp8_rssi_2018.csv")
