"""V12 - the corpus-level facts the paper states in prose.

Several numbers were stated without any file behind them: the index size, its year
span, its build date, how many records are signal-strength work, and how many
post-2020 papers still use ns-2. That last one is a specific accusation about the
field's tooling and had no script at all.

This measures them from `index.csv` and the extracted texts, and writes one CSV.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import unicodedata
from pathlib import Path

import pandas as pd

INDEX = Path("index.csv")
TEXT = Path("workspace/text")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def main() -> None:
    rows = list(csv.DictReader(INDEX.open(encoding="utf-8-sig")))
    years = [int(r["year"]) for r in rows if (r["year"] or "").strip().isdigit()]

    # signal-strength / physical-layer records, by the index's own topic tags
    rssi = [r for r in rows if "RSSI" in (r["topics"] or "") or "PHY" in (r["topics"] or "")]

    # ns-2 use in papers published from 2021 onward, over the full texts
    ns2 = re.compile(r"\bns-?2\b", re.I)
    ns3 = re.compile(r"\bns-?3\b", re.I)
    recent_ns2 = []
    for f in sorted(TEXT.glob("*.txt")):
        year = f.name[:4]
        if not year.isdigit() or int(year) < 2021:
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        # require ns-2 and not merely an ns-3 mention that the pattern clipped
        if ns2.search(t) and not (ns3.search(t) and not ns2.search(t)):
            recent_ns2.append(f.name)

    facts = {
        "index_records": len(rows),
        "index_year_min": min(years),
        "index_year_max": max(years),
        "index_built": dt.date.fromtimestamp(INDEX.stat().st_mtime).isoformat(),
        "full_texts": len(list(TEXT.glob("*.txt"))),
        "rssi_phy_records": len(rssi),
        "ns2_since_2021": len(recent_ns2),
    }
    for k, v in facts.items():
        print("%-22s %s" % (k, v))

    print("\npost-2020 papers mentioning ns-2:")
    for n in recent_ns2:
        print("  " + n[:74])

    pd.DataFrame([facts]).to_csv("workspace/verify/v12_corpus_facts.csv", index=False)
    pd.DataFrame({"file": recent_ns2}).to_csv("workspace/verify/v12_ns2_papers.csv", index=False)
    print("\n-> workspace/verify/v12_corpus_facts.csv and v12_ns2_papers.csv")


if __name__ == "__main__":
    main()
