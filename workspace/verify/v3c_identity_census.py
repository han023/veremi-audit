"""V3c - identity census from the receiver logs, with attacker labels.

Finding 2 was originally argued from a ground-truth file: 1847 senders, 1847
pseudonyms, therefore benign vehicles never rotate. That inference does not hold.
The ground-truth files list one pseudonym per vehicle for attackers too, so the
1:1 mapping there is a property of how ground truth is logged, not of benign
behaviour.

The load-bearing evidence has to come from what receivers actually saw. This
scans the receiver logs, attaches the attacker label from the filename, and
reports the identity count per vehicle separately for benign and attacker.
"""
from __future__ import annotations

import io
import re
import statistics
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd

DATA = Path("workspace/datasets/VeReMi_Extension_sybil")
RECEIVER_RE = re.compile(r"traceJSON-(\d+)-(\d+)-A(\d+)-(\d+)-(\d+)\.json$")
PAIR_RE = re.compile(rb'"sender":\s*(\d+),\s*"senderPseudo":\s*(\d+)')
ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def scan(archive: str) -> dict:
    t0 = time.time()
    label: dict[int, int] = {}
    ids: dict[int, set] = {}
    msgs: Counter = Counter()
    with zipfile.ZipFile(DATA / (archive + ".zip")) as outer:
        for iname in sorted(n for n in outer.namelist() if n.lower().endswith(".zip")):
            with outer.open(iname) as fh, zipfile.ZipFile(io.BytesIO(fh.read())) as win:
                members = win.namelist()
                for m in members:
                    mm = RECEIVER_RE.search(m)
                    if mm:
                        label[int(mm.group(1))] = int(mm.group(3))
                for m in members:
                    if not RECEIVER_RE.search(m):
                        continue
                    for s, p in PAIR_RE.findall(win.read(m)):
                        s, p = int(s), int(p)
                        ids.setdefault(s, set()).add(p)
                        msgs[s] += 1

    known = {s for s in ids if s in label}
    unknown = set(ids) - known
    atk = sorted(len(ids[s]) for s in known if label[s] != 0)
    ben = sorted(len(ids[s]) for s in known if label[s] == 0)

    def pct(v, q):
        return v[min(len(v) - 1, int(q * len(v)))] if v else 0

    return {
        "archive": archive,
        "senders_seen": len(ids),
        "senders_unlabelled": len(unknown),
        "benign_vehicles": len(ben),
        "attacker_vehicles": len(atk),
        "prevalence_vehicles_pct": round(100 * len(atk) / max(1, len(atk) + len(ben)), 2),
        "identities_benign": sum(ben),
        "identities_attacker": sum(atk),
        "prevalence_identities_pct": round(100 * sum(atk) / max(1, sum(atk) + sum(ben)), 2),
        "benign_ids_min": min(ben) if ben else 0,
        "benign_ids_max": max(ben) if ben else 0,
        "benign_ids_mean": round(statistics.fmean(ben), 4) if ben else 0,
        "benign_with_more_than_one": sum(1 for v in ben if v > 1),
        "attacker_ids_min": min(atk) if atk else 0,
        "attacker_ids_p25": pct(atk, 0.25),
        "attacker_ids_med": statistics.median(atk) if atk else 0,
        "attacker_ids_p75": pct(atk, 0.75),
        "attacker_ids_max": max(atk) if atk else 0,
        "secs": round(time.time() - t0, 1),
    }


if __name__ == "__main__":
    rows = []
    for a in (sys.argv[1:] or ARCHIVES):
        r = scan(a)
        rows.append(r)
        print(r, flush=True)
        pd.DataFrame(rows).to_csv("workspace/verify/v3c_identity_census.csv", index=False)
    print("\n-> workspace/verify/v3c_identity_census.csv")
