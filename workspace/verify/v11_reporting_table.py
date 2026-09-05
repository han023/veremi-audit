"""V11 - regenerate the corpus reporting table from the extracted full texts.

Table III in the paper had no single script behind it. Six rows came from
`deep_extract.py`, which was not in the release; the other five were computed
during analysis and recorded only in prose. That is the same defect we corrected
for the single-scalar table and the preprocessed derivative, so it is corrected
the same way: one self-contained script, one CSV, one number per row.

The patterns for the first six rows are copied verbatim from `deep_extract.py` so
the counts reproduce rather than merely resemble. The rest are defined here.

A mention is not a guarantee. These are upper bounds on what papers report: a
paper matching the beacon-rate pattern has a beacon rate somewhere in its text,
which is the weakest claim consistent with the count, and the one we make.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

TEXT = Path("workspace/text")

# --- verbatim from deep_extract.py, so the six original rows reproduce ----------
ORIGINAL = {
    "Explicit threat model": r"(?:attack(?:er)?|threat|adversar\w+)\s+model",
    "Vehicle count": r"\b\d{2,5}\s*(?:vehicles|nodes|cars)\b",
    "Simulation time": r"\bsimulation\s+time\s*(?:of|is|=|:)?\s*\d+\s*(?:s|sec|seconds|min|minutes|hours)?",
    "Beacon rate": r"\b\d+(?:\.\d+)?\s*(?:hz|messages?\s*(?:per|/)\s*s(?:ec(?:ond)?)?|beacons?\s*(?:per|/)\s*s)",
    "Attacker fraction": r"\b\d{1,3}\s*%\s*(?:of\s*)?(?:attack|malicious|sybil|adversar)",
    "Simulation area": r"\b\d+(?:\.\d+)?\s*(?:km2|km²|square kilometers?|km\s*x\s*\d)",
}

# --- defined here ---------------------------------------------------------------
ADDED = {
    # the inclusive reading: a bare "ROC" counts. The strict variant finds two.
    "ROC or AUC": r"\b(?:roc|auc|auroc|auprc|area under)\b",
    "Any significance test or interval": (
        r"\b(?:confidence interval|standard deviation across|"
        r"p\s*[<=]\s*0?\.\d|statistically significant|t-test|wilcoxon|"
        r"mann[- ]whitney|chi[- ]squared|error bars?)\b"),
    "Code mentioned": r"\b(?:github\.com|gitlab\.com|bitbucket\.org|zenodo\.org/record|"
                      r"source code is available|code is available|our code)\b",
    "Adversarial machine learning content": (
        r"\b(?:adversarial (?:example|attack|perturbation|machine learning|training)|"
        r"evasion attack|poisoning attack|model extraction)\b"),
}

URL_RE = re.compile(r"https?://(?:github\.com|gitlab\.com|bitbucket\.org|zenodo\.org)/[^\s,)\]}]+", re.I)


def main() -> None:
    files = sorted(TEXT.glob("*.txt"))
    texts = {f.name: f.read_text(encoding="utf-8", errors="ignore") for f in files}
    n = len(texts)
    print("full texts: %d\n" % n)

    rows = []
    for label, pat in list(ORIGINAL.items()) + list(ADDED.items()):
        rx = re.compile(pat, re.I)
        hits = [name for name, t in texts.items() if rx.search(t)]
        rows.append({"item": label, "papers": len(hits), "of": n,
                     "share_pct": round(100 * len(hits) / n, 1)})
        print("%-38s %3d" % (label, len(hits)))

    # candidate code links, so the reachability row can be checked rather than asserted
    links: dict[str, list[str]] = {}
    for name, t in texts.items():
        found = sorted({u.rstrip(".") for u in URL_RE.findall(t)})
        if found:
            links[name] = found
    print("\npapers carrying a repository or archive URL: %d" % len(links))
    for name, us in sorted(links.items()):
        print("  %s" % name[:66])
        for u in us[:3]:
            print("      %s" % u[:96])

    Path("workspace/verify").mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv("workspace/verify/v11_reporting_table.csv", index=False)
    with open("workspace/verify/v11_code_links.json", "w", encoding="utf-8") as f:
        json.dump(links, f, indent=1)
    print("\n-> workspace/verify/v11_reporting_table.csv and v11_code_links.json")


if __name__ == "__main__":
    main()
