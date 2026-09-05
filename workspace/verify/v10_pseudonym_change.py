"""V10 - does pseudonym change occur in the eight Sybil archives?

Our census reports one pseudonym per benign vehicle, everywhere. The generator
behind these archives, F2MD, lists pseudonym change policies among its features,
so a reader may reasonably expect rotation to be present. This script tests the
claim properly instead of asserting it.

A 1:1 sender-to-pseudonym mapping can arise two ways:

  A. no pseudonym change happens, which is what we claim; or
  B. pseudonym change happens and the logged `sender` changes with it, in which
     case the mapping is 1:1 by construction and rotation is invisible to us.

B leaves a signature. If a new identifier were minted on every change, observed
lifetimes would be truncated at the policy period and would cluster near it.
Under A, a vehicle's observation span reflects how long it was in radio range,
which is governed by traffic and should be broad and irregular.

So this measures the distribution of per-sender observation spans and compares it
against the simulation window length. A tight cluster well below the window is
evidence for B; a broad spread is evidence for A.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]
QS = [0.05, 0.25, 0.50, 0.75, 0.95]


def run(archive: str) -> dict:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    ded = ded.assign(sender=ded["token"].map(truth.token_to_sender))
    ded = ded[ded["sender"].notna()]
    benign = ded[[truth.sender_to_attack.get(int(s), 0) == 0 for s in ded["sender"]]]

    # span per benign vehicle, within its own simulation window
    g = benign.groupby(["window", "sender"], observed=True)["rcvTime"]
    span = (g.max() - g.min()).to_numpy()
    span = span[span > 0]

    wl = benign.groupby("window")["rcvTime"].agg(lambda t: t.max() - t.min())
    window_len = float(wl.max())

    row = {"archive": archive,
           "benign_vehicles_scored": len(span),
           "window_length_s": round(window_len, 1),
           "span_mean_s": round(float(np.mean(span)), 1),
           "span_sd_s": round(float(np.std(span)), 1),
           "span_cv": round(float(np.std(span) / np.mean(span)), 3)}
    for q in QS:
        row["span_q%02d" % int(q * 100)] = round(float(np.quantile(span, q)), 1)
    # a fixed-period policy would pile spans onto one value
    vals, counts = np.unique(np.round(span, 0), return_counts=True)
    row["modal_span_s"] = float(vals[counts.argmax()])
    row["modal_share_pct"] = round(100 * counts.max() / len(span), 2)
    row["span_max_over_window"] = round(float(span.max() / window_len), 3)
    return row


if __name__ == "__main__":
    rows = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        r = run(a)
        rows.append(r)
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v10_pseudonym_change.csv", index=False)
    print("\nspan coefficient of variation: %.2f to %.2f"
          % (df.span_cv.min(), df.span_cv.max()))
    print("largest single-value pile-up: %.2f %% of vehicles" % df.modal_share_pct.max())
    print("longest span as a fraction of its window: %.2f" % df.span_max_over_window.max())
    print("\n-> workspace/verify/v10_pseudonym_change.csv")
