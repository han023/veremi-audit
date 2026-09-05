"""V7 - what these 92 papers actually evaluate on.

The paper opens by saying misbehaviour detection is evaluated "almost entirely" on
VeReMi. That is a quantitative claim and it needs a count, so this counts.

Mentions are counted per paper, case-insensitive, over the extracted full text.
A mention is not the same as an evaluation, so the simulator counts below are an
upper bound on "rolled their own" and the dataset counts are an upper bound on use.
Both are reported as what they are.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd

TEXT = Path("workspace/text")

PATTERNS = {
    "VeReMi (any)": r"veremi",
    "VeReMi Extension": r"veremi\s*[- ]?\s*extension",
    "VeReMi NextGen": r"veremi\s*[- ]?\s*nextgen",
    "F2MD": r"\bf2md\b",
    "NGSIM": r"\bngsim\b",
    "CRAWDAD": r"\bcrawdad\b",
    "BurST-ADMA": r"burst[- ]adma",
    "Istanbul RSSI set": r"(istanbul|beyo\W?glu|\bfatih\b).{0,80}(dataset|rssi)",
    "Kaggle": r"\bkaggle\b",
    "any named public dataset": r"veremi|\bf2md\b|\bngsim\b|\bcrawdad\b|burst[- ]adma|\bkaggle\b",
}
SIMULATORS = {
    "SUMO": r"\bsumo\b",
    "Veins": r"\bveins\b",
    "OMNeT++": r"omnet",
    "NS-2": r"\bns-?2\b",
    "NS-3": r"\bns-?3\b",
    "MATLAB": r"\bmatlab\b",
    "any simulator": r"\bsumo\b|\bveins\b|omnet|\bns-?2\b|\bns-?3\b|\bmatlab\b",
}


def load(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore").lower()


def main() -> None:
    files = sorted(TEXT.glob("*.txt"))
    texts = {f.name: load(f) for f in files}
    n = len(texts)
    print("papers with extracted full text: %d\n" % n)

    rows = []
    for label, pat in list(PATTERNS.items()) + list(SIMULATORS.items()):
        rx = re.compile(pat, re.S)
        hits = [name for name, t in texts.items() if rx.search(t)]
        rows.append({"item": label, "papers": len(hits),
                     "share_pct": round(100 * len(hits) / n, 1)})
        print("%-26s %3d  (%4.1f %%)" % (label, len(hits), 100 * len(hits) / n))

    # neither a named public dataset nor an obvious simulator mention
    named = re.compile(PATTERNS["any named public dataset"], re.S)
    sim = re.compile(SIMULATORS["any simulator"], re.S)
    only_sim = [k for k, t in texts.items() if sim.search(t) and not named.search(t)]
    neither = [k for k, t in texts.items() if not sim.search(t) and not named.search(t)]
    print("\nsimulator mentioned but no named public dataset: %d (%.1f %%)"
          % (len(only_sim), 100 * len(only_sim) / n))
    print("neither mentioned:                               %d (%.1f %%)"
          % (len(neither), 100 * len(neither) / n))

    rows.append({"item": "simulator only, no named dataset", "papers": len(only_sim),
                 "share_pct": round(100 * len(only_sim) / n, 1)})
    rows.append({"item": "neither", "papers": len(neither),
                 "share_pct": round(100 * len(neither) / n, 1)})
    rows.append({"item": "TOTAL full texts", "papers": n, "share_pct": 100.0})

    # which papers mention VeReMi at all
    vrx = re.compile(PATTERNS["VeReMi (any)"], re.S)
    print("\npapers mentioning VeReMi:")
    for name in sorted(k for k, t in texts.items() if vrx.search(t)):
        print("   " + name[:78])

    # year distribution of the VeReMi mentions
    years = Counter(name[:4] for name, t in texts.items() if vrx.search(t))
    print("\nby year:", dict(sorted(years.items())))

    pd.DataFrame(rows).to_csv("workspace/verify/v7_dataset_usage.csv", index=False)
    print("\n-> workspace/verify/v7_dataset_usage.csv")


if __name__ == "__main__":
    main()
