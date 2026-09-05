"""V8 - a first look at VeReMi NextGen, enough to place our audit against it.

We do not audit NextGen in this paper. This measures only what the paper asserts
about it, so that assertion is traceable rather than remembered:

  * whether the release ships predefined splits
  * whether the alias encodes the sender identifier, which is the artefact that
    dominates the extension

The alias check runs on the ground-truth files. For the extension we learned that
ground-truth files under-report the identity population, so the alias-per-sender
count from this source is NOT reported as evidence about pseudonym change. Only
the encoding rate is, because that is a property of each alias in isolation.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

DATA = Path("workspace/datasets/VeReMi_NextGen_sybil")


def probe(path: Path) -> dict:
    records = json.loads(path.read_text(encoding="utf-8"))
    aliases = defaultdict(set)
    encoded = total = 0
    for r in records:
        s, a = r.get("sender_id"), r.get("sender_alias")
        if not s or not a:
            continue
        total += 1
        aliases[s].add(a)
        # sender_id looks like "veh_1386"; does the alias contain those digits?
        if str(s).split("_")[-1] in str(a):
            encoded += 1
    return {
        "file": path.name,
        "records": len(records),
        "senders": len(aliases),
        "aliases": sum(len(v) for v in aliases.values()),
        "encoding_pct": round(100 * encoded / max(1, total), 2),
    }


if __name__ == "__main__":
    gts = sorted(DATA.glob("*_groundTruth.json"))
    splits = sorted({p.name.split("_")[3] for p in gts if len(p.name.split("_")) > 3})
    print("ground-truth files: %d" % len(gts))
    print("split names present: %s" % ", ".join(splits))

    rows = [probe(p) for p in gts]
    for r in rows:
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v8_nextgen_probe.csv", index=False)
    print("\nencoding rate across files: %.2f%% to %.2f%%"
          % (df.encoding_pct.min(), df.encoding_pct.max()))
    print("-> workspace/verify/v8_nextgen_probe.csv")
