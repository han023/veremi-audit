"""Experiment 8b — RSS-based position verification (Xiao 2006 style) on VeReMi 2018."""
import sys
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import GroupShuffleSplit
sys.path.insert(0, "workspace")
from sybilbench import loader_veremi2018 as L

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
view, truth = L.load(max_archives=N, max_receivers_per_archive=80)
print(f"rows={len(view)} (type2={int((view['type']==2).sum())} type3={int((view['type']==3).sum())})", flush=True)

f = L.position_verification_features(view)
if f.empty:
    print("no features"); sys.exit(0)
print("path-loss fit:", f.attrs.get("path_loss_fit"), flush=True)
y = L.label(f, truth).to_numpy()
print(f"link rows={len(f)} attacker links={int(y.sum())} ({y.mean():.3%})", flush=True)

FEATS = ["resid_mean", "resid_absmean", "resid_std", "resid_max", "dist_mean", "dist_std",
         "rssi_mean", "rssi_std", "n"]
X = f[FEATS].to_numpy(); groups = f["sender"].to_numpy()
aucs, aps, singles = [], [], {c: [] for c in FEATS}
for seed in range(5):
    tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed).split(X, y, groups))
    if y[te].sum() < 3 or y[tr].sum() < 3: continue
    m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
    m.fit(X[tr], y[tr]); p = m.predict_proba(X[te])[:, 1]
    aucs.append(roc_auc_score(y[te], p)); aps.append(average_precision_score(y[te], p))
    for c in FEATS:
        a = roc_auc_score(y[te], f[c].to_numpy()[te]); singles[c].append(max(a, 1-a))
print(f"\nposition-verification detector (sender-disjoint): AUC={np.mean(aucs):.4f}+/-{np.std(aucs):.4f} AP={np.mean(aps):.4f} (n={len(aucs)})")
print("single-feature AUCs:", {c: round(float(np.mean(v)),3) for c,v in singles.items() if v})
pd.DataFrame({"auc":aucs,"ap":aps}).to_csv("workspace/sybilbench/exp8b_position_verification.csv", index=False)
