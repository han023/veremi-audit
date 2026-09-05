"""V3b - full pseudonym map, built from the receiver logs.

V3 read only the ground-truth files and came up short: DataReplaySybil replays
other vehicles' pseudonyms, so the identities a receiver actually sees are not
the identities the ground-truth file lists. That mismatch is itself worth
recording, and it means the leakage feature has to be recovered from the logs.

Parsing 5 M JSON objects per archive to read two integers is wasteful, so this
scans the raw bytes with a regex instead and only decodes what it matches.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path

DATA = Path("workspace/datasets/VeReMi_Extension_sybil")
OUT = Path("workspace/sybilbench/cache")
RECEIVER_RE = re.compile(r"traceJSON-(\d+)-(\d+)-A(\d+)-(\d+)-(\d+)\.json$")
PAIR_RE = re.compile(rb'"sender":\s*(\d+),\s*"senderPseudo":\s*(\d+)')
LOOSE_SENDER = re.compile(rb'"sender":\s*(\d+)')
LOOSE_PSEUDO = re.compile(rb'"senderPseudo":\s*(\d+)')
SALT = "sybilbench-v1"
ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def token(archive: str, pseudo: int) -> str:
    return hashlib.blake2b((SALT + "|" + archive + "|" + str(pseudo)).encode(),
                           digest_size=8).hexdigest()


def build(archive: str) -> dict:
    pairs: Counter = Counter()          # (sender, pseudo) -> messages
    t0 = time.time()
    with zipfile.ZipFile(DATA / (archive + ".zip")) as outer:
        for iname in sorted(n for n in outer.namelist() if n.lower().endswith(".zip")):
            with outer.open(iname) as fh, zipfile.ZipFile(io.BytesIO(fh.read())) as win:
                for m in win.namelist():
                    if not RECEIVER_RE.search(m):
                        continue
                    blob = win.read(m)
                    got = PAIR_RE.findall(blob)
                    if not got:
                        # field order differs in some windows; fall back to a paired scan
                        s = LOOSE_SENDER.findall(blob)
                        p = LOOSE_PSEUDO.findall(blob)
                        got = list(zip(s, p)) if len(s) == len(p) else []
                    for s, p in got:
                        pairs[(int(s), int(p))] += 1
    tok_to_pseudo = {}
    for (s, p) in pairs:
        tok_to_pseudo[token(archive, p)] = p
    owners: dict[int, set] = {}
    for (s, p) in pairs:
        owners.setdefault(p, set()).add(s)
    enc = sum(1 for (s, p) in pairs if str(s) in str(p))
    return {
        "archive": archive,
        "distinct_sender_pseudo_pairs": len(pairs),
        "distinct_pseudonyms": len(owners),
        "distinct_senders": len({s for s, _ in pairs}),
        "encoding_pct_pairs": round(100 * enc / max(1, len(pairs)), 2),
        "encoding_pct_messages": round(
            100 * sum(c for (s, p), c in pairs.items() if str(s) in str(p)) / max(1, sum(pairs.values())), 2),
        "messages": sum(pairs.values()),
        "pseudonyms_with_multiple_owners": sum(1 for v in owners.values() if len(v) > 1),
        "secs": round(time.time() - t0, 1),
        "_map": tok_to_pseudo,
    }


if __name__ == "__main__":
    import pandas as pd
    targets = sys.argv[1:] or ARCHIVES
    rows = []
    for a in targets:
        r = build(a)
        mp = r.pop("_map")
        with open(OUT / (a + ".pseudomap.json"), "w", encoding="utf-8") as f:
            json.dump({"token_to_pseudo": mp}, f)
        rows.append(r)
        print(r, flush=True)
        pd.DataFrame(rows).to_csv("workspace/verify/v3b_pseudomap.csv", index=False)
    print("\n-> workspace/verify/v3b_pseudomap.csv")
