"""
First analyses on the leakage-controlled view.

Two questions, both answered without ever showing a model the true `sender`:

  A. token-level detection — from the behaviour of a single identity, can we tell it belongs to an attacker?
  B. pairwise linkage     — given two identities, can we tell they are the same physical vehicle?

(B) is the one that matters: it is simultaneously the Sybil-detection primitive (link an attacker's
concurrent identities) and the tracking primitive (link an honest driver's successive identities). It is the
measurement behind the "linkability dilemma".
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd


def transmissions(view: pd.DataFrame) -> pd.DataFrame:
    """Collapse the receiver-centric view to one row per transmitted message.

    A single BSM is logged separately by every receiver that heard it (measured: median 6.4 copies, max 31).
    Grouping a token's rows across receivers therefore destroys its cadence — inter-arrival gaps collapse to
    ~1e-7 s — and inflates any pairwise timing feature. Always dedupe on `messageID` before reasoning about
    a *sender's* behaviour. Keep the raw view only for what one receiver actually observed.
    """
    return view.drop_duplicates("messageID").sort_values("rcvTime").reset_index(drop=True)


def rate_features(view: pd.DataFrame) -> pd.DataFrame:
    """Trivial per-identity rate statistics — the baseline any real detector must beat."""
    ded = transmissions(view)
    out = []
    for tok, g in ded.groupby("token", observed=True):
        t = g["rcvTime"].to_numpy()
        if len(t) < 2:
            continue
        dt = np.diff(t)
        out.append({"token": tok, "n_msgs": len(t), "interval_med": float(np.median(dt)),
                    "interval_std": float(np.std(dt)), "duration": float(t[-1] - t[0])})
    return pd.DataFrame(out)


def token_features(view: pd.DataFrame) -> pd.DataFrame:
    """Per-identity behavioural summary. No identity semantics, only observable behaviour."""
    g = view.sort_values("rcvTime").groupby("token")

    def _agg(d: pd.DataFrame) -> pd.Series:
        t = d["rcvTime"].to_numpy()
        dt = np.diff(t) if len(t) > 1 else np.array([np.nan])
        speed = np.hypot(d["spd_x"], d["spd_y"]).to_numpy()
        acl = np.hypot(d["acl_x"], d["acl_y"]).to_numpy()
        dx = d["pos_x"].to_numpy()
        dy = d["pos_y"].to_numpy()
        step = np.hypot(np.diff(dx), np.diff(dy)) if len(dx) > 1 else np.array([np.nan])
        # implied speed from consecutive positions vs claimed speed: a physical consistency residual
        implied = step / dt if len(step) == len(dt) and len(dt) > 0 else np.array([np.nan])
        resid = np.abs(implied - speed[1:]) if len(implied) == len(speed) - 1 else np.array([np.nan])
        return pd.Series(
            {
                "n_msgs": len(d),
                "duration": t[-1] - t[0] if len(t) > 1 else 0.0,
                "dt_mean": np.nanmean(dt),
                "dt_std": np.nanstd(dt),
                "speed_mean": np.nanmean(speed),
                "speed_std": np.nanstd(speed),
                "speed_max": np.nanmax(speed) if len(speed) else np.nan,
                "acl_mean": np.nanmean(acl),
                "acl_std": np.nanstd(acl),
                "step_mean": np.nanmean(step),
                "step_std": np.nanstd(step),
                "kin_resid_mean": np.nanmean(resid),
                "kin_resid_max": np.nanmax(resid) if len(resid) else np.nan,
                "pos_span_x": np.nanmax(dx) - np.nanmin(dx),
                "pos_span_y": np.nanmax(dy) - np.nanmin(dy),
                "posnoise_mean": np.nanmean(np.hypot(d["pos_noise_x"], d["pos_noise_y"])),
                "hednoise_mean": np.nanmean(np.hypot(d["hed_noise_x"], d["hed_noise_y"])),
                "n_receivers": d["receiver"].nunique(),
            }
        )

    return g.apply(_agg, include_groups=False).reset_index()


def pair_candidates(view: pd.DataFrame, max_pairs: int = 60_000, seed: int = 0) -> pd.DataFrame:
    """Sample token pairs that were seen by the same receiver, with overlapping presence.

    Restricting to co-observed pairs mirrors what a real receiver could attempt, and keeps the pair space
    tractable (all-pairs is quadratic in identities).
    """
    rng = np.random.default_rng(seed)
    span = view.groupby("token").agg(t0=("rcvTime", "min"), t1=("rcvTime", "max"))
    by_recv = view.groupby("receiver")["token"].unique()

    pairs = set()
    for _recv, toks in by_recv.items():
        toks = list(toks)
        if len(toks) < 2:
            continue
        if len(toks) > 60:  # subsample dense receivers to bound the pair count
            toks = list(rng.choice(toks, 60, replace=False))
        for a, b in itertools.combinations(sorted(toks), 2):
            pairs.add((a, b))
        if len(pairs) > max_pairs * 3:
            break

    pairs = list(pairs)
    if len(pairs) > max_pairs:
        idx = rng.choice(len(pairs), max_pairs, replace=False)
        pairs = [pairs[i] for i in idx]

    rows = []
    for a, b in pairs:
        sa, sb = span.loc[a], span.loc[b]
        overlap = min(sa.t1, sb.t1) - max(sa.t0, sb.t0)
        rows.append({"a": a, "b": b, "overlap": overlap})
    return pd.DataFrame(rows)


def pair_features(view: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Kinematic + timing relationship between two identities."""
    idx = {t: d for t, d in view.groupby("token")}
    out = []
    for r in pairs.itertuples(index=False):
        da, db = idx[r.a], idx[r.b]
        ta, tb = da["rcvTime"].to_numpy(), db["rcvTime"].to_numpy()
        # nearest-in-time matching, then geometry between the two claimed trajectories
        j = np.searchsorted(tb, ta).clip(0, len(tb) - 1)
        dt = np.abs(tb[j] - ta)
        m = dt < 1.0  # only compare near-simultaneous claims
        if m.sum() < 3:
            continue
        ax, ay = da["pos_x"].to_numpy()[m], da["pos_y"].to_numpy()[m]
        bx, by = db["pos_x"].to_numpy()[j[m]], db["pos_y"].to_numpy()[j[m]]
        dist = np.hypot(ax - bx, ay - by)
        sa = np.hypot(da["spd_x"], da["spd_y"]).to_numpy()[m]
        sb = np.hypot(db["spd_x"], db["spd_y"]).to_numpy()[j[m]]
        # cadence: do the two identities interleave on a shared clock?
        phase = np.abs(np.median(dt[m] % 1.0) - 0.5)
        out.append(
            {
                "a": r.a,
                "b": r.b,
                "overlap": r.overlap,
                "n_cmp": int(m.sum()),
                "dist_mean": float(np.mean(dist)),
                "dist_min": float(np.min(dist)),
                "dist_std": float(np.std(dist)),
                "spd_diff_mean": float(np.mean(np.abs(sa - sb))),
                "spd_corr": float(np.corrcoef(sa, sb)[0, 1]) if len(sa) > 2 and np.std(sa) > 0 and np.std(sb) > 0 else 0.0,
                "dt_median": float(np.median(dt[m])),
                "phase": float(phase),
            }
        )
    return pd.DataFrame(out)


def label_pairs(pairs: pd.DataFrame, truth) -> pd.Series:
    """1 if both identities belong to the same physical vehicle (evaluation only)."""
    sa = pairs["a"].map(truth.token_to_sender)
    sb = pairs["b"].map(truth.token_to_sender)
    return ((sa == sb) & sa.notna()).astype(int)


def overlap_pairs(view: pd.DataFrame, max_pairs: int = 40_000, seed: int = 0,
                  min_overlap_s: float = 1.0) -> pd.DataFrame:
    """Candidate pairs built from *temporal overlap* instead of random co-observation sampling.

    `pair_candidates` subsamples dense receivers to 60 tokens to bound the quadratic pair space. That is fine
    for a vehicle receiver (tens of neighbours) but destroys an RSU view (~1400 identities): drawing 60 at
    random almost never catches two identities of the same attacker, and the positive class vanishes.

    Sorting identities by start time and pairing only those whose presence intervals actually overlap keeps
    the pair space linear-ish in practice while preserving every concurrent pair worth scoring.
    """
    rng = np.random.default_rng(seed)
    span = view.groupby("token", observed=True).agg(t0=("rcvTime", "min"), t1=("rcvTime", "max"))
    span = span.sort_values("t0")
    toks = span.index.to_numpy()
    t0 = span["t0"].to_numpy()
    t1 = span["t1"].to_numpy()

    rows = []
    for i in range(len(toks)):
        # everything starting before i ends can overlap i
        hi = np.searchsorted(t0, t1[i])
        for j in range(i + 1, min(hi, len(toks))):
            ov = min(t1[i], t1[j]) - max(t0[i], t0[j])
            if ov >= min_overlap_s:
                rows.append({"a": toks[i], "b": toks[j], "overlap": float(ov)})
        if len(rows) > max_pairs * 4:
            break

    pairs = pd.DataFrame(rows)
    if len(pairs) > max_pairs:
        pairs = pairs.sample(max_pairs, random_state=seed).reset_index(drop=True)
    return pairs
