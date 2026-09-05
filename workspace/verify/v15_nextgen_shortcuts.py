"""V15 - do the same shortcuts exist in VeReMi NextGen?

Every finding in this paper so far comes from one dataset family. That is the
obvious external-validity objection: the shortcuts might be quirks of the
Extension rather than properties of how these benchmarks get built.

NextGen is the right test. It is independent of the Extension in scenario (InTAS,
not LuST), in generator version, and in attack family, and it was released to
address limitations of the earlier VeReMi work. If the shortcuts are absent there,
our findings are about one artefact. If they persist, they are about the practice.

Measured, per scenario, exactly as for the Extension:

  * does the alias encode the sender identifier
  * do benign vehicles hold more than one alias
  * attacker prevalence, at vehicle level and at identity level
  * the single-scalar baseline: median inter-arrival and message count
  * receiver duplication

Structure: outer zip -> Train|Test|Validation -> inner zip -> veh_<id>.json,
each a JSON array of received messages carrying an explicit `attacker` flag.
"""
from __future__ import annotations

import io
import json
import re
import statistics
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace/verify")
from v2_metrics import bootstrap_ci, rank_auc  # noqa: E402

DATA = Path("workspace/datasets/VeReMi_NextGen_sybil")
SPLIT = "Train"


def read_scenario(path: Path, split: str = SPLIT, max_files: int | None = None):
    """Yield (receiver, records) for each receiver log in one split."""
    with zipfile.ZipFile(path) as outer:
        inner = [n for n in outer.namelist()
                 if n.endswith(".zip") and ("/%s/" % split) in n]
        if not inner:
            return
        with outer.open(inner[0]) as fh, zipfile.ZipFile(io.BytesIO(fh.read())) as win:
            members = [m for m in win.namelist() if m.endswith(".json")]
            if max_files:
                members = members[:max_files]
            for m in members:
                try:
                    recs = json.loads(win.read(m))
                except json.JSONDecodeError:
                    continue
                yield Path(m).stem, recs


def digits(s) -> str:
    return re.sub(r"\D", "", str(s))


def analyse(path: Path, max_files: int | None = None) -> dict:
    alias_of = defaultdict(set)          # sender -> aliases
    attacker = {}                        # sender -> 0/1
    tx = defaultdict(list)               # alias -> send times
    copies = defaultdict(int)            # messageID -> receivers that logged it
    enc_hits = enc_total = 0
    n_records = 0

    for _recv, recs in read_scenario(path, max_files=max_files):
        for r in recs:
            s, a = r.get("sender_id"), r.get("sender_alias")
            if s is None or a is None:
                continue
            n_records += 1
            alias_of[s].add(a)
            attacker[s] = max(attacker.get(s, 0), int(r.get("attacker", 0)))
            st = r.get("sendTime")
            if st is not None:
                tx[a].append(float(st))
            mid = r.get("messageID")
            if mid is not None:
                copies[mid] += 1
            enc_total += 1
            enc_hits += digits(s) in digits(a)

    atk = {s for s, v in attacker.items() if v}
    ben = {s for s, v in attacker.items() if not v}
    ids_atk = [len(alias_of[s]) for s in atk]
    ids_ben = [len(alias_of[s]) for s in ben]

    # single-scalar baseline over identities, direction fixed a priori as before
    rows = []
    owner = {a: s for s, al in alias_of.items() for a in al}
    for a, times in tx.items():
        t = np.sort(np.asarray(times, dtype=float))
        if len(t) < 2:
            continue
        # NextGen stamps are integer nanoseconds; scale to seconds
        dt = np.diff(t) / 1e9
        rows.append((a, len(t), float(np.median(dt)), int(attacker.get(owner.get(a), 0))))
    f = pd.DataFrame(rows, columns=["alias", "n_msgs", "interval_med", "y"])

    out = {
        "scenario": path.stem,
        "records": n_records,
        "vehicles": len(attacker),
        "attacker_vehicles": len(atk),
        "prevalence_vehicles_pct": round(100 * len(atk) / max(1, len(attacker)), 2),
        "identities": sum(len(v) for v in alias_of.values()),
        "identities_attacker": sum(ids_atk),
        "prevalence_identities_pct": round(
            100 * sum(ids_atk) / max(1, sum(ids_atk) + sum(ids_ben)), 2),
        "encoding_pct": round(100 * enc_hits / max(1, enc_total), 2),
        "benign_alias_max": max(ids_ben) if ids_ben else 0,
        "benign_with_more_than_one": sum(1 for v in ids_ben if v > 1),
        "attacker_alias_med": statistics.median(ids_atk) if ids_atk else 0,
        "attacker_alias_max": max(ids_atk) if ids_atk else 0,
        "copies_median": statistics.median(copies.values()) if copies else 0,
        "identities_scored": len(f),
    }
    if len(f) > 40 and 0 < f.y.mean() < 1:
        y = f.y.to_numpy()
        out["AUC_interval"] = round(rank_auc(y, f.interval_med.to_numpy()), 4)
        out["AUC_msgcount"] = round(rank_auc(y, -f.n_msgs.to_numpy()), 4)
        lo, hi = bootstrap_ci(y, f.interval_med.to_numpy(), n_boot=1000)
        out["AUC_interval_lo"], out["AUC_interval_hi"] = round(lo, 4), round(hi, 4)
    return out


if __name__ == "__main__":
    mf = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rows = []
    for p in sorted(DATA.glob("*Sybil.zip")):
        r = analyse(p, max_files=mf)
        rows.append(r)
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v15_nextgen_shortcuts.csv", index=False)
    print("\n-> workspace/verify/v15_nextgen_shortcuts.csv")
