"""Build the IEEE Transactions variant, without the visual abstract.

T-ITS charges $175 for every page past ten, so ten is a hard ceiling here rather
than a target. Two changes get us there:

  * journal class instead of conference;
  * the visual abstract removed, as the author asked. It duplicates Table XI and
    the cascade text, so it is the cheapest float to lose.

The conference version is left untouched at veremi_audit.tex. This writes a
separate file so both survive.
"""
import re
from pathlib import Path

SRC = Path("workspace/paper/veremi_audit.tex")
DST = Path("workspace/paper/veremi_audit_journal.tex")

s = SRC.read_text(encoding="utf-8")

# --- journal class ---------------------------------------------------------------
s = s.replace(r"\documentclass[conference]{IEEEtran}",
              r"\documentclass[journal]{IEEEtran}")

# --- drop the visual abstract and its reference ----------------------------------
start = s.index(r"\begin{figure}[t]")
end = s.index(r"\end{figure}", start) + len(r"\end{figure}")
block = s[start:end]
assert "fig_abstract" in block, "first figure is not the visual abstract"
s = s[:start] + s[end:]
s = s.replace("Figure~\\ref{fig:abstract} summarises what follows.\n", "")

# the journal class wants a running head and a short title
s = s.replace(r"\maketitle",
              "\\markboth{IEEE Transactions on Intelligent Transportation Systems}%\n"
              "{Muzammil: What VeReMi Measures}\n\\maketitle")

DST.write_text(s, encoding="utf-8")
left = len(re.findall(r"\\begin\{figure\}", s))
print("wrote %s" % DST.name)
print("  class: journal | figures remaining: %d" % left)
print("  visual abstract removed, its reference removed")
