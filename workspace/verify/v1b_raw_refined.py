"""V1b - refined raw scan. Fixes three defects found in the first pass.

1. Senders observed in a log but named by no filename were silently counted as
   benign. That is the same label bug we hit during development, re-entering
   through the back door. Unlabelled senders are now excluded and counted.
2. The encoding rate was measured per message. The paper's table counts distinct
   (sender, pseudonym) pairs. Both are now reported; they are different things.
3. Ground-truth files carry every message sent, so identity statistics come from
   there instead of from the receiver logs. Receiver logs are used only to measure
   duplication, which is what they alone can show.
"""
from __future__ import annotations

import io
import json
import re
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

DATA = Path("workspace/datasets/VeReMi_Extension_sybil")
RECEIVER_RE = re.compile(r"traceJSON-(\d+)-(\d+)-A(\d+)-(\d+)-(\d+)\.json$")
GT_RE = re.compile(r"traceGroundTruthJSON-(\d+)\.json$")
ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def scan(archive: str) -> dict:
    path = DATA / f"{archive}.zip"
    sender_attack: dict[int, int] = {}
    pseudo_of_sender: dict[int, set] = defaultdict(set)
    owners_of_pseudo: dict[int, set] = defaultdict(set)
    msgs_per_pseudo: Counter = Counter()
    enc_msgs_hit = enc_msgs_tot = 0
    gt_messages = 0
    windows = 0
    recv_records = 0
    copies_sample: Counter = Counter()

    with zipfile.ZipFile(path) as outer:
        inner = sorted(n for n in outer.namelist() if n.lower().endswith(".zip"))
        for iname in inner:
            windows += 1
            with outer.open(iname) as fh, zipfile.ZipFile(io.BytesIO(fh.read())) as win:
                members = win.namelist()
                for m in members:                       # labels from EVERY filename
                    mm = RECEIVER_RE.search(m)
                    if mm:
                        sender_attack[int(mm.group(1))] = int(mm.group(3))
                for m in members:                       # identity facts from ground truth
                    if not GT_RE.search(m):
                        continue
                    with win.open(m) as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                rec = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            s, p = rec.get("sender"), rec.get("senderPseudo")
                            if s is None or p is None:
                                continue
                            gt_messages += 1
                            pseudo_of_sender[s].add(p)
                            owners_of_pseudo[p].add(s)
                            msgs_per_pseudo[p] += 1
                            enc_msgs_tot += 1
                            enc_msgs_hit += str(s) in str(p)
                # duplication: how many receivers logged each transmission.
                # one receiver file is not enough; sample enough files to cover the window.
                sample = [m for m in members if RECEIVER_RE.search(m)]
                for m in sample:
                    with win.open(m) as f:
                        for line in f:
                            if b'"type": 3' not in line and b'"type":3' not in line:
                                continue
                            try:
                                rec = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if rec.get("type") != 3:
                                continue
                            recv_records += 1
                            mid = rec.get("messageID")
                            if mid is not None:
                                copies_sample[(iname, mid)] += 1

    labelled = sender_attack
    observed = set(pseudo_of_sender)
    unlabelled = observed - set(labelled)
    known = observed & set(labelled)
    atk = {s for s in known if labelled[s] != 0}
    ben = {s for s in known if labelled[s] == 0}

    pairs = [(s, p) for s in known for p in pseudo_of_sender[s]]
    enc_pairs_hit = sum(1 for s, p in pairs if str(s) in str(p))
    ids_atk = [len(pseudo_of_sender[s]) for s in atk]
    ids_ben = [len(pseudo_of_sender[s]) for s in ben]
    shared = {p: v for p, v in owners_of_pseudo.items() if len(v) > 1}
    copies = list(copies_sample.values())

    return {
        "archive": archive,
        "windows": windows,
        "vehicles": len(labelled),
        "attackers": len(atk),
        "benign": len(ben),
        "prevalence_vehicles_pct": round(100 * len({s for s in labelled if labelled[s] != 0}) / len(labelled), 2),
        "senders_unlabelled": len(unlabelled),
        "gt_messages": gt_messages,
        "identities": len(owners_of_pseudo),
        "identities_attacker": sum(ids_atk),
        "prevalence_identities_pct": round(100 * sum(ids_atk) / max(1, sum(ids_atk) + sum(ids_ben)), 2),
        "encoding_pct_messages": round(100 * enc_msgs_hit / max(1, enc_msgs_tot), 2),
        "encoding_pct_pairs": round(100 * enc_pairs_hit / max(1, len(pairs)), 2),
        "distinct_pairs": len(pairs),
        "ids_per_benign_max": max(ids_ben) if ids_ben else 0,
        "ids_per_attacker_min": min(ids_atk) if ids_atk else 0,
        "ids_per_attacker_med": statistics.median(ids_atk) if ids_atk else 0,
        "ids_per_attacker_max": max(ids_atk) if ids_atk else 0,
        "pseudonyms_shared_by_many": len(shared),
        "shared_pseudonym_values": sorted(shared)[:5],
        "shared_pseudonym_msgs": sum(msgs_per_pseudo[p] for p in shared),
        "recv_records": recv_records,
        "unique_transmissions": len(copies),
        "copies_median": statistics.median(copies) if copies else 0,
        "copies_mean": round(statistics.fmean(copies), 3) if copies else 0,
        "copies_ratio_records_over_unique": round(recv_records / max(1, len(copies)), 3),
    }


if __name__ == "__main__":
    rows = []
    for a in ARCHIVES:
        r = scan(a)
        rows.append(r)
        print(r, flush=True)
    pd.DataFrame(rows).to_csv("workspace/verify/v1b_raw_refined.csv", index=False)
    print("\n-> workspace/verify/v1b_raw_refined.csv")
