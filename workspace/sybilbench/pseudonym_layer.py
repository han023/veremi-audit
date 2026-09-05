"""
Synthetic pseudonym-change layer.

VeReMi benign vehicles keep one pseudonym for their whole presence (audit Finding 2: 1 847 senders ->
1 847 pseudonyms). That has two consequences the rest of this study has to fix:

  1. *Confound.* Because only attackers hold several identities, "these two identities are the same vehicle"
     is definitionally "this is an attacker" — so a linkage model can score well by detecting attackers
     instead of by linking. Giving benign vehicles multiple identities breaks the confound.
  2. *Missing axis.* Unlinkability, pseudonym lifetime and tracking resistance cannot be studied at all
     without pseudonym changes.

Pseudonym-change policy is a layer above mobility, so applying it in post-processing is faithful: we re-key a
vehicle's own message stream at a chosen lifetime, changing nothing physical. Lifetime tau then becomes the
controlled variable of the privacy/detection trade-off.

Attackers are left alone: their concurrency is the attack.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from sybilbench.loader import Truth


def apply_pseudonym_change(
    view: pd.DataFrame,
    truth: Truth,
    lifetime_s: float,
    *,
    salt: str = "psc",
    benign_only: bool = True,
) -> tuple[pd.DataFrame, Truth]:
    """Re-key each vehicle's stream every `lifetime_s` seconds.

    Returns a new (view, truth). The new tokens are unlinkable by construction — an attacker who wants to
    follow the vehicle must do it from kinematics, which is exactly the measurement we want.
    """
    v = view.copy()
    v["token"] = v["token"].astype(str)
    sender = v["token"].map(truth.token_to_sender)
    is_attacker = sender.map(lambda s: truth.sender_to_attack.get(s, 0) != 0 if pd.notna(s) else False)

    t0 = v.groupby("token", observed=True)["rcvTime"].transform("min")
    epoch = ((v["rcvTime"] - t0) // lifetime_s).astype("int64")

    if benign_only:
        epoch = epoch.where(~is_attacker, 0)  # attackers keep their identities

    new_token = [
        hashlib.blake2b(f"{salt}|{tok}|{e}".encode(), digest_size=8).hexdigest()
        for tok, e in zip(v["token"].to_numpy(), epoch.to_numpy())
    ]
    v["token"] = new_token

    new_truth = Truth(
        token_to_sender={
            nt: int(s)
            for nt, s in zip(new_token, sender.to_numpy())
            if pd.notna(s)
        },
        sender_to_attack=dict(truth.sender_to_attack),
    )
    return v, new_truth


def sequential_pairs(view: pd.DataFrame, truth: Truth, max_gap_s: float = 60.0,
                     max_pairs: int = 40_000, seed: int = 0) -> pd.DataFrame:
    """Candidate pairs for *tracking*: identity B appears after identity A ends, within `max_gap_s`.

    This is the pseudonym-linking attack: did the car that just vanished reappear under a new name?
    """
    rng = np.random.default_rng(seed)
    span = view.groupby("token", observed=True).agg(
        t0=("rcvTime", "min"), t1=("rcvTime", "max"),
        x0=("pos_x", "first"), y0=("pos_y", "first"),
        x1=("pos_x", "last"), y1=("pos_y", "last"),
        vx=("spd_x", "last"), vy=("spd_y", "last"),
    )
    span = span.sort_values("t0")
    toks = span.index.to_numpy()
    t0 = span["t0"].to_numpy()
    t1 = span["t1"].to_numpy()

    rows = []
    for i in range(len(toks)):
        # successors starting after i ends, within the gap budget
        lo = np.searchsorted(t0, t1[i])
        hi = np.searchsorted(t0, t1[i] + max_gap_s)
        cand = np.arange(lo, min(hi, len(toks)))
        if len(cand) == 0:
            continue
        if len(cand) > 25:
            cand = rng.choice(cand, 25, replace=False)
        for j in cand:
            if toks[i] == toks[j]:
                continue
            rows.append({"a": toks[i], "b": toks[j], "gap": float(t0[j] - t1[i])})
        if len(rows) > max_pairs * 2:
            break

    pairs = pd.DataFrame(rows)
    if len(pairs) > max_pairs:
        pairs = pairs.sample(max_pairs, random_state=seed).reset_index(drop=True)
    if pairs.empty:
        return pairs

    s = span.loc[pairs["a"]]
    e = span.loc[pairs["b"]]
    # dead-reckon A across the gap, then measure the miss distance to where B first appears
    pred_x = s["x1"].to_numpy() + s["vx"].to_numpy() * pairs["gap"].to_numpy()
    pred_y = s["y1"].to_numpy() + s["vy"].to_numpy() * pairs["gap"].to_numpy()
    pairs["miss"] = np.hypot(pred_x - e["x0"].to_numpy(), pred_y - e["y0"].to_numpy())
    pairs["jump"] = np.hypot(s["x1"].to_numpy() - e["x0"].to_numpy(), s["y1"].to_numpy() - e["y0"].to_numpy())
    pairs["spd_a"] = np.hypot(s["vx"].to_numpy(), s["vy"].to_numpy())
    pairs["spd_b"] = np.hypot(e["vx"].to_numpy(), e["vy"].to_numpy())
    pairs["spd_diff"] = np.abs(pairs["spd_a"] - pairs["spd_b"])
    pairs["implied_speed"] = pairs["jump"] / pairs["gap"].clip(lower=0.1)
    return pairs


def label_same_vehicle(pairs: pd.DataFrame, truth: Truth) -> pd.Series:
    sa = pairs["a"].map(truth.token_to_sender)
    sb = pairs["b"].map(truth.token_to_sender)
    return ((sa == sb) & sa.notna()).astype(int)


def gap_matched(pairs: pd.DataFrame, y: pd.Series, n_neg_per_pos: int = 20, seed: int = 0,
                bins: int = 12) -> tuple[pd.DataFrame, pd.Series]:
    """Resample negatives so their `gap` distribution matches the positives'.

    Without this, "tracking accuracy" partly measures *when* an identity reappeared rather than *whether it
    is the same car*: a re-keyed vehicle resumes immediately, so positives sit at small gaps by construction.
    Matching on gap forces the classifier to earn its score from geometry.
    """
    rng = np.random.default_rng(seed)
    pos = pairs[y == 1]
    neg = pairs[y == 0]
    if pos.empty or neg.empty:
        return pairs, y
    edges = np.quantile(pos["gap"], np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    keep_idx = list(pos.index)
    pos_bin = np.digitize(pos["gap"], edges)
    neg_bin = np.digitize(neg["gap"], edges)
    for b in np.unique(pos_bin):
        want = int((pos_bin == b).sum() * n_neg_per_pos)
        pool = neg.index[neg_bin == b]
        if len(pool) == 0:
            continue
        take = rng.choice(pool, min(want, len(pool)), replace=False)
        keep_idx.extend(take.tolist())
    out = pairs.loc[keep_idx].copy()
    return out, y.loc[keep_idx]


def apply_silent_period(view: pd.DataFrame, truth: Truth, lifetime_s: float, silence_s: float,
                        *, salt: str = "psc", benign_only: bool = False) -> tuple[pd.DataFrame, Truth]:
    """Re-key every `lifetime_s`, and stay silent for `silence_s` immediately after each change.

    Real pseudonym-change policies pair the change with a silence period (or a mix zone) precisely because
    a seamless hand-over is trivially linkable: the vehicle simply continues from where it stopped. Finding 12
    predicts that policies which cut *evidence per identity* hurt detection as much as tracking; silence is
    the interesting counter-case, because it removes continuity *between* identities without reducing the
    evidence *within* one, and concurrent (Sybil) linkage never needed that continuity.
    """
    v2, t2 = apply_pseudonym_change(view, truth, lifetime_s, salt=salt, benign_only=benign_only)
    if silence_s <= 0:
        return v2, t2
    t0 = v2.groupby("token", observed=True)["rcvTime"].transform("min")
    keep = (v2["rcvTime"] - t0) >= silence_s          # drop the first `silence_s` of each new identity
    v3 = v2[keep].copy()
    live = set(v3["token"].unique())
    t3 = Truth(
        token_to_sender={k: s for k, s in t2.token_to_sender.items() if k in live},
        sender_to_attack=dict(t2.sender_to_attack),
    )
    return v3, t3
