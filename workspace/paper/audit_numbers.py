"""List every numeric literal in the paper body and flag those no check covers.

The paper claims every number traces to a released file. This tests that claim by
brute force: pull every number out of the body, then report which ones never appear
as a value the claim checker asserts.
"""
import re
import subprocess
import sys
from pathlib import Path

tex = Path("workspace/paper/veremi_audit.tex").read_text(encoding="utf-8")
body = tex[tex.index(r"\begin{document}"):tex.index(r"\begin{thebibliography}")]
body = re.sub(r"(?<!\\)%.*", " ", body)

# what the checker verifies: run it and capture the values it reports
res = subprocess.run([sys.executable, "workspace/paper/check_claims.py"],
                     capture_output=True, text=True)
checked_blob = res.stdout

# numeric literals, ignoring LaTeX sizing and reference machinery
skip_context = re.compile(r"(?:cite|ref|label|includegraphics|documentclass|"
                          r"cm\}|pt\}|vspace|multicolumn|section|bibitem)")
numbers = {}
for m in re.finditer(r"(?<![\w.])(\d{1,3}(?:\\,\d{3})+|\d+(?:\.\d+)?)(?![\w])", body):
    start = max(0, m.start() - 60)
    ctx = body[start:m.end() + 40].replace("\n", " ")
    if skip_context.search(body[max(0, m.start() - 25):m.start()]):
        continue
    numbers.setdefault(m.group(1), []).append(ctx.strip())

print("distinct numeric literals in the body: %d\n" % len(numbers))

unverified = []
for num, ctxs in sorted(numbers.items(), key=lambda kv: kv[0]):
    plain = num.replace("\\,", "")
    # a number is considered covered if the checker printed it, or it is trivially
    # structural (a stage index, a small count spelled in a table header, etc.)
    if plain in checked_blob or num in checked_blob:
        continue
    unverified.append((num, ctxs[0]))

print("not printed by the claim checker: %d" % len(unverified))
for num, ctx in unverified:
    print("  %-10s %s" % (num, ctx[:96]))
