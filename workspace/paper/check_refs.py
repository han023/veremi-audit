"""Check the reference mix: established works versus recent ones."""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "workspace/paper/veremi_audit.tex"
text = open(path, encoding="utf-8").read()
bib = text.split(r"\begin{thebibliography}")[1]
entries = re.split(r"\\bibitem", bib)[1:]

recent = [e for e in entries if re.search(r"20(2[4-9]|3\d)", e)]
older = [e for e in entries if e not in recent]

n = len(entries)
print(f"references: {n}")
print(f"  recent (2024+):   {len(recent):2d}  ({100 * len(recent) / n:.0f}%)")
print(f"  established:      {len(older):2d}  ({100 * len(older) / n:.0f}%)")
print()
target = 20 <= 100 * len(recent) / n <= 30
print("within requested 20-30% recent:", "yes" if target else "NO")

keys = [re.match(r"\{([^}]+)\}", e).group(1) for e in entries if re.match(r"\{([^}]+)\}", e)]
cited = set(re.findall(r"\\cite\{([^}]+)\}", text))
cited = {k.strip() for group in cited for k in group.split(",")}
missing = [k for k in keys if k not in cited]
undefined = [k for k in cited if k not in keys]
print("uncited entries:", missing or "none")
print("undefined citations:", undefined or "none")
