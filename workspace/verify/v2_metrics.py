"""V2 - metric implementations that do not depend on scikit-learn.

Reviewers asked for the AUC numbers to be checked against an independent
implementation. ROC-AUC here is the Mann-Whitney U statistic computed from
ranks; average precision is the step-wise sum used by the PR literature.
Ties get mid-ranks, which is where naive implementations usually disagree.

`selftest()` compares both against sklearn and against scipy's Mann-Whitney U
on random and adversarial (heavily tied) inputs.
"""
from __future__ import annotations

import numpy as np


def rank_auc(y: np.ndarray, s: np.ndarray) -> float:
    """ROC-AUC as normalised Mann-Whitney U. No sklearn."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    sorted_s = s[order]
    ranks = np.empty(len(s), dtype=float)
    i = 0
    while i < len(sorted_s):                      # mid-rank for tied blocks
        j = i
        while j + 1 < len(sorted_s) and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    r1 = ranks[y == 1].sum()
    u1 = r1 - n1 * (n1 + 1) / 2.0
    return float(u1 / (n1 * n0))


def step_ap(y: np.ndarray, s: np.ndarray) -> float:
    """Average precision, sum_n (R_n - R_{n-1}) * P_n. No sklearn."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    n_pos = int(y.sum())
    if n_pos == 0:
        return float("nan")
    order = np.argsort(-s, kind="mergesort")
    ys = y[order]
    ss = s[order]
    tp = np.cumsum(ys)
    k = np.arange(1, len(ys) + 1)
    precision = tp / k
    recall = tp / n_pos
    # collapse tied score blocks to their last index: a threshold cannot split a tie
    keep = np.ones(len(ss), dtype=bool)
    keep[:-1] = ss[:-1] != ss[1:]
    p, r = precision[keep], recall[keep]
    dr = np.diff(np.concatenate([[0.0], r]))
    return float((dr * p).sum())


def bootstrap_ci(y, s, stat=rank_auc, n_boot: int = 2000, seed: int = 0, alpha: float = 0.05):
    """Percentile bootstrap CI, resampling test rows with replacement."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    rng = np.random.default_rng(seed)
    n = len(y)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y[idx].sum() == 0 or y[idx].sum() == n:
            continue
        vals.append(stat(y[idx], s[idx]))
    if not vals:
        return (float("nan"), float("nan"))
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(lo), float(hi))


def delong_var_auc(y, s):
    """DeLong variance of AUC -> a parametric interval to sit beside the bootstrap."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    pos, neg = s[y == 1], s[y == 0]
    m, n = len(pos), len(neg)
    if m == 0 or n == 0:
        return float("nan"), (float("nan"), float("nan"))
    def midrank(x):
        order = np.argsort(x, kind="mergesort")
        xs = x[order]
        r = np.empty(len(x), dtype=float)
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[i]:
                j += 1
            r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
            i = j + 1
        return r
    both = np.concatenate([pos, neg])
    r_all = midrank(both)
    r_pos_alone = midrank(pos)
    r_neg_alone = midrank(neg)
    v01 = (r_all[:m] - r_pos_alone) / n
    v10 = 1.0 - (r_all[m:] - r_neg_alone) / m
    auc = v01.mean()
    var = v01.var(ddof=1) / m + v10.var(ddof=1) / n
    half = 1.959963985 * np.sqrt(max(var, 0.0))
    return float(auc), (float(max(0.0, auc - half)), float(min(1.0, auc + half)))


def selftest(seed: int = 0) -> None:
    from sklearn.metrics import average_precision_score, roc_auc_score
    from scipy.stats import mannwhitneyu
    rng = np.random.default_rng(seed)
    worst_auc = worst_ap = worst_mw = 0.0
    for trial in range(200):
        n = int(rng.integers(50, 800))
        y = (rng.random(n) < rng.uniform(0.02, 0.5)).astype(int)
        if y.sum() == 0 or y.sum() == n:
            continue
        if trial % 3 == 0:                      # heavily tied scores
            s = rng.integers(0, 4, n).astype(float)
        elif trial % 3 == 1:                    # continuous, signal present
            s = rng.normal(y * 0.8, 1.0)
        else:                                   # constant -> every score tied
            s = np.full(n, 0.5)
        worst_auc = max(worst_auc, abs(rank_auc(y, s) - roc_auc_score(y, s)))
        worst_ap = max(worst_ap, abs(step_ap(y, s) - average_precision_score(y, s)))
        u = mannwhitneyu(s[y == 1], s[y == 0], alternative="two-sided").statistic
        worst_mw = max(worst_mw, abs(u / (y.sum() * (n - y.sum())) - rank_auc(y, s)))
    print(f"max |ours - sklearn| AUC : {worst_auc:.3e}")
    print(f"max |ours - sklearn| AP  : {worst_ap:.3e}")
    print(f"max |ours - scipy MWU|   : {worst_mw:.3e}")
    assert worst_auc < 1e-12 and worst_ap < 1e-12 and worst_mw < 1e-12
    print("SELFTEST PASS - independent implementations agree to machine precision")


if __name__ == "__main__":
    selftest()
