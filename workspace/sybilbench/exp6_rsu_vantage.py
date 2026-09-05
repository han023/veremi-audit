"""
Experiment 6 — does an infrastructure vantage point escape the evidence tension?

Findings 12/15 say every pseudonym-policy lever rations *evidence*, and both the tracker and the detector
consume it, so no policy setting favours one over the other. The proposed escape is an **asymmetric
mechanism**: an observer that gains detection power without granting equal tracking power.

Roadside units are the classic candidate (Footprint's premise) — a static observer at an intersection sees
every identity that passes for the whole simulation, whereas a vehicle sees a neighbour only while co-present.

VeReMi has no RSUs, so one is emulated: a fixed point that receives every transmission whose claimed position
falls within radius R, over the entire window. Two vantages are then compared on identical traces:

    vehicle vantage : pairs co-observed by one moving receiver   (what has been measured so far)
    RSU vantage     : pairs co-observed at one static point      (long dwell, wide coverage)

Hypothesis (from Finding 12): the RSU raises BOTH heads, because it simply accumulates more evidence —
i.e. no asymmetry, and the dilemma survives. The alternative — detection rising faster than tracking — would
be the first measured escape.

Caveat stated up front: reception is modelled on *claimed* position, which is what a receiver logs. For a
Sybil ghost the claimed position is fabricated, so the emulated RSU hears ghosts wherever they claim to be.
That is favourable to the RSU (it sees the whole fake formation), so this is an optimistic bound on the
infrastructure advantage.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader, pseudonym_layer as P  # noqa: E402

SEEDS = [0, 1, 2]
RADIUS_M = 300.0
N_RSU = 6
N_VEHICLE_OBSERVERS = 12


def pick_rsu_sites(ded: pd.DataFrame, n: int, radius: float) -> list[tuple[float, float]]:
    """Place RSUs at the busiest locations — a proxy for intersections."""
    cell = radius
    gx = (ded["pos_x"] // cell).astype("int64")
    gy = (ded["pos_y"] // cell).astype("int64")
    counts = pd.DataFrame({"gx": gx, "gy": gy}).value_counts().head(n * 3)
    sites, used = [], set()
    for (cx, cy), _n in counts.items():
        if any(abs(cx - ux) <= 1 and abs(cy - uy) <= 1 for ux, uy in used):
            continue  # keep RSUs from overlapping
        used.add((cx, cy))
        sites.append(((cx + 0.5) * cell, (cy + 0.5) * cell))
        if len(sites) >= n:
            break
    return sites


def rsu_view(ded: pd.DataFrame, site: tuple[float, float], radius: float, rsu_id: int) -> pd.DataFrame:
    d = np.hypot(ded["pos_x"] - site[0], ded["pos_y"] - site[1])
    v = ded[d <= radius].copy()
    v["receiver"] = rsu_id          # the RSU is the single receiver for this view
    return v


def score(view: pd.DataFrame, truth, seed: int) -> dict:
    out = {}
    n = view.groupby("token", observed=True).size()
    out["msgs_per_id"] = float(n.median()) if len(n) else np.nan
    out["identities"] = int(len(n))

    # detection: concurrent identity pairs
    # overlap-driven candidates: a random 60-token subsample of an RSU's ~1400 identities never catches
    # two ghosts of one attacker, which silently empties the positive class.
    cd = analysis.overlap_pairs(view, max_pairs=20_000, seed=seed)
    out["detection_auc"], out["detection_pos"] = np.nan, 0
    if not cd.empty:
        if True:
            ft = analysis.pair_features(view, cd)
            if not ft.empty:
                y = analysis.label_pairs(ft, truth)
                if y.sum() >= 20 and y.nunique() > 1:
                    out["detection_auc"] = float(roc_auc_score(y, ft["spd_corr"].fillna(0)))
                    out["detection_pos"] = int(y.sum())

    # tracking: successive identity pairs (needs a pseudonym-change layer to exist at all)
    pr = P.sequential_pairs(view, truth, max_gap_s=120, max_pairs=30_000, seed=seed)
    out["tracking_auc"], out["tracking_pos"] = np.nan, 0
    if not pr.empty:
        y = P.label_same_vehicle(pr, truth)
        pm, ym = P.gap_matched(pr, y, n_neg_per_pos=20, seed=seed)
        if ym.sum() >= 20 and ym.nunique() > 1:
            out["tracking_auc"] = float(roc_auc_score(ym, -pm["miss"].fillna(1e9)))
            out["tracking_pos"] = int(ym.sum())
    return out


def run(archive: str, tau: int = 30) -> pd.DataFrame:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)

    sites = pick_rsu_sites(v2, N_RSU, RADIUS_M)
    print(f"{archive}: {len(sites)} RSU sites, radius {RADIUS_M:.0f} m, tau={tau}s", flush=True)

    # Like-for-like: an RSU is ONE static observer, so a vehicle must be ONE mobile observer.
    # Scoring the pooled view would silently make the vehicle condition a global omniscient observer.
    busiest = (v2.groupby("receiver", observed=True).size().sort_values(ascending=False)
               .head(N_VEHICLE_OBSERVERS).index.tolist())

    rows = []
    for seed in SEEDS:
        # vehicle vantage: each observer sees only what it received
        for rid in busiest:
            vv = v2[v2["receiver"] == rid]
            if vv.empty:
                continue
            r = score(vv, t2, seed)
            r.update({"archive": archive, "vantage": "vehicle", "seed": seed, "site": int(rid)})
            rows.append(r)

        # global pooled view: an upper bound no single observer can reach
        r = score(v2, t2, seed)
        r.update({"archive": archive, "vantage": "global", "seed": seed})
        rows.append(r)

        # RSU vantage: one static observer per site, scored separately then averaged
        for i, site in enumerate(sites):
            rv = rsu_view(v2, site, RADIUS_M, rsu_id=10_000 + i)
            if rv.empty:
                continue
            r = score(rv, t2, seed)
            r.update({"archive": archive, "vantage": "rsu", "seed": seed, "site": i})
            rows.append(r)

    df = pd.DataFrame(rows)
    summ = df.groupby("vantage").agg(
        identities=("identities", "mean"),
        msgs_per_id=("msgs_per_id", "mean"),
        tracking_auc=("tracking_auc", "mean"),
        tracking_sd=("tracking_auc", "std"),
        tracking_pos=("tracking_pos", "mean"),
        detection_auc=("detection_auc", "mean"),
        detection_sd=("detection_auc", "std"),
        detection_pos=("detection_pos", "mean"),
    ).round(4)
    print(summ.to_string(), flush=True)
    return df


if __name__ == "__main__":
    archives = sys.argv[1:] or ["GridSybil_1416"]
    out = pd.concat([run(a) for a in archives], ignore_index=True)
    # per-archive filename: a fixed name meant the second invocation silently overwrote the first run's rows
    tag = "_".join(archives)
    path = f"workspace/sybilbench/exp6_rsu_vantage_{tag}.csv"
    out.to_csv(path, index=False)
    print(f"\nEXP6 DONE -> {path}")
