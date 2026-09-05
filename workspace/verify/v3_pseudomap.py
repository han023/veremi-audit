"""V3 - recover the raw pseudonym behind every hashed token.

Needed because exp7's 'naive' arm derived its leakage feature from the hashed
token, which by construction carries no leakage. Reproducing the leak honestly
requires the real senderPseudo value.

Reads only the ground-truth files (one per window), which list every message
actually sent with both `sender` and `senderPseudo`. Hashes each pseudonym with
the loader's own salt so the mapping lines up with the cached view.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

DATA = Path("workspace/datasets/VeReMi_Extension_sybil")
OUT = Path("workspace/sybilbench/cache")
GT_RE = re.compile(r"traceGroundTruthJSON-(\d+)\.json$")
SALT = "sybilbench-v1"
ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def token(archive: str, pseudo) -> str:
    return hashlib.blake2b(f"{SALT}|{archive}|{pseudo}".encode(), digest_size=8).hexdigest()


def build(archive: str) -> dict:
    pairs: dict[str, int] = {}
    sender_of: dict[str, int] = {}
    with zipfile.ZipFile(DATA / f"{archive}.zip") as outer:
        for iname in sorted(n for n in outer.namelist() if n.lower().endswith(".zip")):
            with outer.open(iname) as fh, zipfile.ZipFile(io.BytesIO(fh.read())) as win:
                for m in win.namelist():
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
                            p, s = rec.get("senderPseudo"), rec.get("sender")
                            if p is None:
                                continue
                            t = token(archive, p)
                            pairs[t] = p
                            if s is not None:
                                sender_of[t] = s
    return {"pseudo": pairs, "sender": sender_of}


if __name__ == "__main__":
    targets = sys.argv[1:] or ARCHIVES
    for a in targets:
        m = build(a)
        path = OUT / f"{a}.pseudomap.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"token_to_pseudo": m["pseudo"]}, f)
        # sanity: does the recovered pseudonym really encode the sender?
        hits = sum(1 for t, p in m["pseudo"].items() if t in m["sender"] and str(m["sender"][t]) in str(p))
        n = len(m["pseudo"])
        print(f"{a}: {n} tokens mapped, encoding {100*hits/max(1,n):.2f}% -> {path.name}", flush=True)
