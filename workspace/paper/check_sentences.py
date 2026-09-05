"""Verify the 12-word-per-sentence constraint on the paper body.

Skips tables, comments, macros and the bibliography, then flags any sentence over the limit.
"""
import re
import sys

LIMIT = 12
path = sys.argv[1] if len(sys.argv) > 1 else "workspace/paper/veremi_audit.tex"
text = open(path, encoding="utf-8").read()

start = text.index(r"\begin{document}")
end = text.index(r"\begin{thebibliography}")
body = text[start:end]

body = re.sub(r"\\author\{.*?\}\}", " ", body, flags=re.S)
body = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", " ", body, flags=re.S)
# Escaped percent must go before comment stripping: otherwise the bare % left behind
# looks like a comment start and swallows the rest of the line, merging two sentences.
body = body.replace(r"\%", " percent ").replace(r"\&", " and ").replace(r"\_", "_")
body = re.sub(r"(?<!\\)%.*", " ", body)
body = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", body)

over, total = [], 0
for sentence in re.split(r"(?<=[.!?])\s+", body):
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", sentence)
    if not words:
        continue
    total += 1
    if len(words) > LIMIT:
        over.append((len(words), " ".join(words)[:95]))

print(f"sentences checked: {total} | over {LIMIT} words: {len(over)}")
for n, s in over:
    print(f"  {n}: {s}")
sys.exit(1 if over else 0)
