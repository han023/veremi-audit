"""V5 - independent replication of the physical-layer result.

Three defects in the original run, all fixed here.

  1. The log-distance path-loss model was fitted over every link, attackers
     included. Attacker links carry falsified positions, so their claimed
     distances are wrong by construction and drag the slope towards zero. The
     paper said the fit uses benign links; the code did not. Both fits are
     reported so the size of that mistake is visible.

  2. Single-feature AUCs were reported as max(a, 1 - a), which picks each
     feature's orientation using the test labels and cannot fall below 0.5 even
     for pure noise. Directions are now fixed a priori and the signed value is
     reported.

  3. THE POINT ESTIMATE AND ITS INTERVAL DESCRIBED DIFFERENT QUANTITIES. The
     reported AUC was the mean of five per-split values, while the interval was
     a bootstrap over the five test sets concatenated. Those five sets came from
     five independently trained models with independently scaled scores, so
     pooling them is not even a valid ranking, and the resulting interval need
     not contain the mean it was printed beside. It did not: 0.534 sat outside
     [0.517, 0.532].

     The fix is a single estimator. GroupKFold partitions the senders into five
     folds, so every link is scored exactly once by a model that never saw its
     sender. Those out-of-fold scores form one ranking, and the AUC of that
     ranking is the reported number. Its bootstrap and DeLong intervals are
     computed on the same ranking, so they describe the same quantity. Per-fold
     values are reported alongside as a dispersion check, not as the estimate.

Metrics come from the sklearn-free implementation in v2_metrics.py.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
from sybilbench import loader_veremi2018 as L  # noqa: E402
from v2_metrics import bootstrap_ci, delong_var_auc, rank_auc, step_ap  # noqa: E402

FEATS = ["resid_mean", "resid_absmean", "resid_std", "resid_max",
         "dist_mean", "dist_std", "rssi_mean", "rssi_std", "n"]
# a-priori direction: a position lie should inflate the residual and the claimed
# distance, and leave measured power unusually high for the distance claimed.
DIRECTION = {"resid_mean": +1, "resid_absmean": +1, "resid_std": +1, "resid_max": +1,
             "dist_mean": +1, "dist_std": +1, "rssi_mean": +1, "rssi_std": +1, "n": -1}
N_FOLDS = 5
T4 = 2.776445  # two-sided 95 % Student t, 4 degrees of freedom


def fit_pathloss(t: pd.DataFrame, mask=None):
    d = t if mask is None else t[mask]
    A = np.vstack([np.ones(len(d)), d["log_d"].to_numpy()]).T
    coef, *_ = np.linalg.lstsq(A, d["rssi_dbm"].to_numpy(), rcond=None)
    corr = float(np.corrcoef(d["log_d"], d["rssi_dbm"])[0, 1])
    return coef, corr


def build(n_archives: int):
    view, truth = L.load(max_archives=n_archives, max_receivers_per_archive=80)
    rx = view[view["type"] == 2][["archive", "receiver", "rcvTime", "pos_x", "pos_y"]].sort_values(
        ["archive", "receiver", "rcvTime"])
    tx = view[(view["type"] == 3) & view["RSSI"].notna() & (view["RSSI"] > 0)].copy()
    out = []
    for (a, r), g in tx.groupby(["archive", "receiver"], observed=True):
        own = rx[(rx["archive"] == a) & (rx["receiver"] == r)]
        if own.empty:
            continue
        idx = np.searchsorted(own["rcvTime"].to_numpy(), g["rcvTime"].to_numpy()).clip(0, len(own) - 1)
        g = g.copy()
        g["rx_x"] = own["pos_x"].to_numpy()[idx]
        g["rx_y"] = own["pos_y"].to_numpy()[idx]
        out.append(g)
    t = pd.concat(out, ignore_index=True)
    t["claimed_dist"] = np.hypot(t["pos_x"] - t["rx_x"], t["pos_y"] - t["rx_y"]).clip(lower=1.0)
    t["rssi_dbm"] = 10 * np.log10(t["RSSI"] * 1000.0)
    t["log_d"] = np.log10(t["claimed_dist"])
    t["is_attacker"] = t["sender"].map(
        lambda s: 1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0).astype(int)
    return t, truth


def summarise(coef, corr, tag: str) -> dict:
    return {"fit": tag, "intercept_dbm": round(float(coef[0]), 2),
            "slope_db_per_decade": round(float(coef[1]), 2),
            "path_loss_exponent": round(-float(coef[1]) / 10.0, 3),
            "corr_rssi_logd": round(corr, 4)}


def evaluate(t: pd.DataFrame, coef, seed: int = 0) -> dict:
    A = np.vstack([np.ones(len(t)), t["log_d"].to_numpy()]).T
    t = t.assign(residual=t["rssi_dbm"].to_numpy() - A @ coef)
    g = t.groupby(["archive", "receiver", "sender"], observed=True)
    f = g.agg(n=("residual", "size"),
              resid_mean=("residual", "mean"),
              resid_absmean=("residual", lambda v: float(np.mean(np.abs(v)))),
              resid_std=("residual", "std"),
              resid_max=("residual", lambda v: float(np.max(np.abs(v)))),
              dist_mean=("claimed_dist", "mean"),
              dist_std=("claimed_dist", "std"),
              rssi_mean=("rssi_dbm", "mean"),
              rssi_std=("rssi_dbm", "std"),
              y=("is_attacker", "max")).reset_index().fillna(0.0)
    X = f[FEATS].to_numpy()
    y = f["y"].to_numpy()
    groups = f["sender"].to_numpy()
    per_link_scatter = float(t.groupby(["archive", "receiver", "sender"])["residual"].std().median())

    # every link scored exactly once, by a model that never saw its sender
    oof = np.full(len(y), np.nan)
    fold_auc = []
    for tr, te in GroupKFold(n_splits=N_FOLDS).split(X, y, groups):
        assert not (set(groups[tr]) & set(groups[te])), "sender leaked across the split"
        m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2,
                                   n_jobs=-1, random_state=seed)
        m.fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
        if 0 < y[te].sum() < len(te):
            fold_auc.append(rank_auc(y[te], oof[te]))
    assert not np.isnan(oof).any(), "some link was never scored"

    auc = rank_auc(y, oof)
    ap = step_ap(y, oof)
    blo, bhi = bootstrap_ci(y, oof, n_boot=2000, seed=11)
    _, (dlo, dhi) = delong_var_auc(y, oof)

    singles = {c: round(rank_auc(y, DIRECTION[c] * f[c].to_numpy()), 4) for c in FEATS}
    return {"links": len(f), "attacker_links": int(y.sum()),
            "attacker_link_rate": round(float(y.mean()), 4),
            "auc_oof": round(auc, 4),
            "auc_boot_lo": round(blo, 4), "auc_boot_hi": round(bhi, 4),
            "auc_delong_lo": round(dlo, 4), "auc_delong_hi": round(dhi, 4),
            "auc_fold_mean": round(float(np.mean(fold_auc)), 4),
            "auc_fold_sd": round(float(np.std(fold_auc, ddof=1)), 4),
            # Student t interval across folds, for the fold-mean estimator. Folds
            # partition the senders, so the five values are not independent draws;
            # this is the usual approximation and is reported as such.
            "auc_fold_ci_lo": round(float(np.mean(fold_auc) - T4 * np.std(fold_auc, ddof=1) / np.sqrt(len(fold_auc))), 4),
            "auc_fold_ci_hi": round(float(np.mean(fold_auc) + T4 * np.std(fold_auc, ddof=1) / np.sqrt(len(fold_auc))), 4),
            "auc_fold_min": round(float(np.min(fold_auc)), 4),
            "auc_fold_max": round(float(np.max(fold_auc)), 4),
            "ap_oof": round(ap, 4),
            "per_link_residual_scatter_db": round(per_link_scatter, 2),
            "singles_apriori": singles}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    t, truth = build(n)
    print("link rows={} attacker rows={} ({:.2%})".format(
        len(t), int(t["is_attacker"].sum()), t["is_attacker"].mean()), flush=True)

    rows = []
    for tag, mask in (("all_links", None), ("benign_only", t["is_attacker"] == 0)):
        coef, corr = fit_pathloss(t, mask)
        info = summarise(coef, corr, tag)
        res = evaluate(t, coef)
        singles = res.pop("singles_apriori")
        info.update(res)
        rows.append(info)
        print(info, flush=True)
        print("  single-feature AUC, a-priori direction:", singles, flush=True)
        # the estimate and its interval must now describe the same ranking
        assert info["auc_boot_lo"] <= info["auc_oof"] <= info["auc_boot_hi"], \
            "point estimate outside its own bootstrap interval"
        assert info["auc_delong_lo"] <= info["auc_oof"] <= info["auc_delong_hi"], \
            "point estimate outside its own DeLong interval"
    pd.DataFrame(rows).to_csv("workspace/verify/v5_pathloss.csv", index=False)
    print("\n-> workspace/verify/v5_pathloss.csv")
