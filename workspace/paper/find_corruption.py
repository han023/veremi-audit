"""Find every place a number went missing from the prose.

Two blockers now have the same cause: a trim script carried numbers across a
rewrite by matching [\\d.]+ on the old text, which also matches a sentence-ending
period. Periods were substituted into value slots.

The signature is a lone period, or a doubled period, where a numeral belongs.
This scans the body for all of them at once instead of one report at a time.
"""
import re
from pathlib import Path

tex = Path("workspace/paper/veremi_audit.tex").read_text(encoding="utf-8")
body = tex[tex.index(r"\begin{document}"):tex.index(r"\begin{thebibliography}")]

PATTERNS = [
    (r"\bto \.\s*;", "'to .;' - a value slot holding a period"),
    (r"\bAUC \.", "'AUC .' - missing AUC value"),
    (r"and \.\.", "'and ..' - missing second value"),
    (r"\breaches \.", "missing value after 'reaches'"),
    (r"\bbetween \. ", "missing value after 'between'"),
    (r"\bis \.\s", "missing value after 'is'"),
    (r"\bof \.\s", "missing value after 'of'"),
    (r"\.\.", "doubled period"),
    (r"\b\d+\\%%", "doubled percent after a number"),
    (r"(?<!\\)%(?!\s*$)", "unescaped percent mid-line"),
    (r"\bnan\b", "a NaN reached the text"),
    (r"%\.\d[fd]", "an unfilled format specifier"),
    (r"%[ds]\b", "an unfilled format specifier"),
]

hits = 0
for line_no, line in enumerate(body.split("\n"), 1):
    if line.lstrip().startswith("%"):
        continue
    for pat, why in PATTERNS:
        if re.search(pat, line):
            hits += 1
            print("  L%-5d %-42s %s" % (line_no, why, line.strip()[:64]))
            break

print("\nsuspect lines: %d" % hits)
