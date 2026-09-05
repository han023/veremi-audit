"""V16 - the identifier artefact in VeReMi NextGen.

NextGen removes the artefact that dominates the Extension: its receiver-visible
alias does not encode the sender. That is a real improvement and we say so.

But the ground-truth `sender_id` acquires a different problem. Sybil identities are
minted with synthetic identifiers from a numeric range disjoint from the real
vehicles, so the identifier alone separates the classes.

That is not a leak a deployed receiver could exploit, because a receiver never sees
`sender_id`. It matters because published pipelines do key on the ground-truth
sender field: that is stage S0 of our own cascade, reconstructed from practice. Any
pipeline that touches it inherits a perfect shortcut.

Reported per scenario: the two ranges, the AUC of the raw identifier, and the AUC of
its digit length, which is the crudest possible decoder.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace/verify")
from v2_metrics import bootstrap_ci, rank_auc  # noqa: E402
from v15_nextgen_shortcuts import read_scenario  # noqa: E402

DATA = Path("workspace/datasets/VeReMi_NextGen_sybil")
MAX_FILES = 300          # bounds cost; the ranges are stable well before this


def analyse(path: Path, max_files: int = MAX_FILES) -> dict:
    attacker: dict[str, int] = {}
    alias_num: dict[str, int] = {}
    for _recv, recs in read_scenario(path, max_files=max_files):
        for r in recs:
            s = r.get("sender_id")
            if not s:
                continue
            attacker[s] = max(attacker.get(s, 0), int(r.get("attacker", 0)))
            a = r.get("sender_alias")
            if a is not None and s not in alias_num:
                alias_num[s] = int(re.sub(r"\D", "", str(a)) or 0)

    ids = [(int(re.sub(r"\D", "", s) or 0), v) for s, v in attacker.items()]
    num = np.array([i for i, _ in ids])
    y = np.array([v for _, v in ids])
    if len(set(y)) < 2:
        return {"scenario": path.stem, "note": "single class"}

    alias = np.array([alias_num.get(s, 0) for s in attacker])
    lo, hi = bootstrap_ci(y, num.astype(float), n_boot=1000)
    return {
        "scenario": path.stem,
        "identities": len(y),
        "attacker_share_pct": round(100 * float(y.mean()), 2),
        "benign_id_min": int(num[y == 0].min()), "benign_id_max": int(num[y == 0].max()),
        "attacker_id_min": int(num[y == 1].min()), "attacker_id_max": int(num[y == 1].max()),
        "ranges_disjoint": bool(num[y == 0].max() < num[y == 1].min()),
        "AUC_sender_id": round(rank_auc(y, num.astype(float)), 4),
        "AUC_sender_id_lo": round(lo, 4), "AUC_sender_id_hi": round(hi, 4),
        "AUC_id_digit_length": round(
            rank_auc(y, np.array([len(str(i)) for i in num], dtype=float)), 4),
        # the receiver-visible field, for contrast
        "AUC_alias": round(rank_auc(y, alias.astype(float)), 4),
    }


if __name__ == "__main__":
    rows = []
    for p in sorted(DATA.glob("*Sybil.zip")):
        r = analyse(p)
        rows.append(r)
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v16_nextgen_identifier.csv", index=False)
    if "AUC_sender_id" in df:
        print("\nground-truth identifier AUC: %.3f to %.3f"
              % (df.AUC_sender_id.min(), df.AUC_sender_id.max()))
        print("receiver-visible alias AUC:  %.3f to %.3f"
              % (df.AUC_alias.min(), df.AUC_alias.max()))
    print("-> workspace/verify/v16_nextgen_identifier.csv")
