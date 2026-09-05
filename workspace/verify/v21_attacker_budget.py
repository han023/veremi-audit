"""V21 - what is the attacker's actual transmission budget?

The paper says benign vehicles beacon at 1 Hz, that an attacker holds about a
hundred identities, and that each ghost therefore transmits once per fifty seconds.
Those three statements are not consistent. Splitting a 1 Hz budget across a hundred
identities gives one transmission per hundred seconds, not fifty.

Either the measured 50 s is wrong, or the attacker's aggregate rate is not 1 Hz, or
fewer identities are live at once than the totals suggest. This measures all three
directly instead of choosing between them.

For each attacker vehicle we compute:
  * its aggregate transmission rate, over its own observed span
  * how many distinct identities it actually used
  * how many were live in the same second, which is what sets the per-ghost gap
"""
from __future__ import annotations

import sys
from collections import defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader  # noqa: E402

ARCHIVES = ["GridSybil_0709", "DataReplaySybil_0709",
            "DoSRandomSybil_0709", "DoSDisruptiveSybil_0709"]


def run(archive: str) -> dict:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    ded = ded.assign(sender=ded["token"].map(truth.token_to_sender))
    ded = ded[ded["sender"].notna()]

    agg_rate, n_ids, ghost_gap, live = [], [], [], []
    for s, g in ded.groupby("sender", observed=True):
        if truth.sender_to_attack.get(int(s), 0) == 0:
            continue
        t = np.sort(g["rcvTime"].to_numpy())
        span = t[-1] - t[0]
        if span <= 0 or len(t) < 10:
            continue
        agg_rate.append(len(t) / span)                 # transmissions per second
        ids = g["token"].nunique()
        n_ids.append(ids)
        # median gap between successive transmissions of one identity
        for _tok, gg in g.groupby("token", observed=True):
            tt = np.sort(gg["rcvTime"].to_numpy())
            if len(tt) > 2:
                ghost_gap.append(float(np.median(np.diff(tt))))
        # identities that appear within any one-second window, averaged
        sec = (g["rcvTime"] // 1).astype(np.int64)
        live.append(float(g.groupby(sec)["token"].nunique().mean()))

    if not agg_rate:
        return {"archive": archive, "note": "no attacker with enough data"}
    return {
        "archive": archive,
        "attacker_vehicles": len(agg_rate),
        "aggregate_rate_hz_median": round(float(np.median(agg_rate)), 3),
        "identities_per_attacker_median": int(np.median(n_ids)),
        "ghost_interval_median_s": round(float(np.median(ghost_gap)), 2),
        "identities_live_per_second": round(float(np.median(live)), 2),
        "implied_interval_if_1hz": round(float(np.median(n_ids)) / 1.0, 1),
        "implied_interval_from_rate": round(
            float(np.median(n_ids)) / float(np.median(agg_rate)), 1),
    }


if __name__ == "__main__":
    rows = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        r = run(a)
        rows.append(r)
        print(r, flush=True)
    pd.DataFrame(rows).to_csv("workspace/verify/v21_attacker_budget.csv", index=False)
    print("\n-> workspace/verify/v21_attacker_budget.csv")
