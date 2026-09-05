"""V1 - reproduce the structural findings straight from the raw zips.

Deliberately does NOT import sybilbench. It re-reads the archives with the standard
library so a reviewer can check the findings without trusting our loader.

Reproduces, per archive:
  * pseudonym -> sender digit encoding rate      (paper Table `tab:leak`)
  * sender : pseudonym cardinality               (paper 'benign never rotate')
  * attacker prevalence, by vehicle and identity (paper '~30 %')
  * identities per attacker                      (paper '2-7 vs 100')
  * duplication factor, copies per messageID     (paper 'median 6.4')
"""
from __future__ import annotations

import json
import re
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path("workspace/datasets/VeReMi_Extension_sybil")
RECEIVER_RE = re.compile(r"traceJSON-(\d+)-(\d+)-A(\d+)-(\d+)-(\d+)\.json$")
GROUNDTRUTH_RE = re.compile(r"traceGroundTruthJSON-(\d+)\.json$")

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def encodes_sender(pseudo: int, sender: int) -> bool:
    """Does the pseudonym string literally contain the sender-id digits?"""
    return str(sender) in str(pseudo)


def scan(archive: str, max_windows: int | None = None) -> dict:
    path = DATA / f"{archive}.zip"
    # attacker label comes from the FILENAME (A<attackType>), over the *full* member list --
    # taking it from a parsed subset was the original label bug.
    sender_attack: dict[int, int] = {}
    pseudo_of_sender: dict[int, set] = defaultdict(set)
    sender_of_pseudo: dict[int, set] = defaultdict(set)
    enc_hits = enc_total = 0
    msg_copies: Counter = Counter()
    windows = 0

    with zipfile.ZipFile(path) as outer:
        inner_names = [n for n in outer.namelist() if n.lower().endswith(".zip")]
        inner_names.sort()
        for iname in inner_names:
            if max_windows is not None and windows >= max_windows:
                break
            windows += 1
            with outer.open(iname) as fh, zipfile.ZipFile(fh) as win:
                members = win.namelist()
                # pass 1: labels from every receiver filename in this window
                for m in members:
                    mm = RECEIVER_RE.search(m)
                    if mm:
                        sender_attack[int(mm.group(1))] = int(mm.group(3))
                # pass 2: read the receiver logs
                for m in members:
                    if not RECEIVER_RE.search(m):
                        continue
                    with win.open(m) as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                rec = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if rec.get("type") != 3:
                                continue
                            s = rec.get("sender")
                            p = rec.get("senderPseudo")
                            if s is None or p is None:
                                continue
                            pseudo_of_sender[s].add(p)
                            sender_of_pseudo[p].add(s)
                            enc_total += 1
                            enc_hits += encodes_sender(p, s)
                            mid = rec.get("messageID")
                            if mid is not None:
                                msg_copies[(iname, mid)] += 1
    return dict(archive=archive, windows=windows,
                sender_attack=sender_attack,
                pseudo_of_sender=pseudo_of_sender,
                sender_of_pseudo=sender_of_pseudo,
                enc_hits=enc_hits, enc_total=enc_total,
                msg_copies=msg_copies)


def report(r: dict) -> dict:
    sa = r["sender_attack"]
    pos = r["pseudo_of_sender"]
    observed = set(pos)                       # senders actually seen in the logs
    labelled = {s: a for s, a in sa.items()}  # every sender named by a filename

    atk_v = {s for s, a in labelled.items() if a != 0}
    ben_v = {s for s, a in labelled.items() if a == 0}
    atk_seen = {s for s in observed if labelled.get(s, 0) != 0}
    ben_seen = {s for s in observed if labelled.get(s, 0) == 0}

    ids_atk = [len(pos[s]) for s in atk_seen]
    ids_ben = [len(pos[s]) for s in ben_seen]
    n_ids_atk = sum(ids_atk)
    n_ids_ben = sum(ids_ben)

    copies = list(r["msg_copies"].values())
    # a pseudonym mapping to >1 true sender would break the 1:1 story
    multi_owner = sum(1 for v in r["sender_of_pseudo"].values() if len(v) > 1)

    return {
        "archive": r["archive"],
        "windows": r["windows"],
        "msgs_type3": r["enc_total"],
        "encoding_pct": round(100 * r["enc_hits"] / max(1, r["enc_total"]), 2),
        "vehicles_labelled": len(labelled),
        "attackers_labelled": len(atk_v),
        "prevalence_vehicles_pct": round(100 * len(atk_v) / max(1, len(labelled)), 2),
        "vehicles_observed": len(observed),
        "attackers_observed": len(atk_seen),
        "identities_total": n_ids_atk + n_ids_ben,
        "identities_attacker": n_ids_atk,
        "prevalence_identities_pct": round(100 * n_ids_atk / max(1, n_ids_atk + n_ids_ben), 2),
        "ids_per_benign_max": max(ids_ben) if ids_ben else 0,
        "ids_per_benign_mean": round(statistics.fmean(ids_ben), 3) if ids_ben else 0,
        "ids_per_attacker_min": min(ids_atk) if ids_atk else 0,
        "ids_per_attacker_med": statistics.median(ids_atk) if ids_atk else 0,
        "ids_per_attacker_max": max(ids_atk) if ids_atk else 0,
        "pseudonyms_with_multiple_owners": multi_owner,
        "dup_copies_median": statistics.median(copies) if copies else 0,
        "dup_copies_mean": round(statistics.fmean(copies), 3) if copies else 0,
        "unique_messages": len(copies),
    }


if __name__ == "__main__":
    import sys
    import pandas as pd
    mw = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = []
    for a in ARCHIVES:
        r = scan(a, max_windows=mw)
        row = report(r)
        rows.append(row)
        print(row, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v1_raw_structure.csv", index=False)
    print("\n-> workspace/verify/v1_raw_structure.csv")
