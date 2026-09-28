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

# Publisher-mandated declarations are fixed wording: the CRediT roles, the competing
# interest sentence, the funding sentence and Elsevier's generative-AI template are
# all supplied by the publisher. Shortening them to satisfy a house style rule would
# misstate a required disclosure, so the limit stops at the first of them. Done here,
# before macros are stripped, while the section markers still exist.
for marker in ("section*{CRediT", "section*{Declaration", "section*{Funding"):
    if marker in body:
        body = body[:body.index(marker)]
        break

body = re.sub(r"\\markboth\{.*?\}\s*%?\s*\{.*?\}", " ", body, flags=re.S)
body = re.sub(r"\\author\{.*?\}\}", " ", body, flags=re.S)
# elsarticle keeps the title, authors, affiliation and keywords inside frontmatter.
# Flattened, "organization={Hannsoft}, addressline={Township}, ..." reads as one long
# sentence and so does a \sep-separated keyword list. Drop both; the abstract, which
# sits between them, is real prose and stays.
if "begin{frontmatter}" in body:
    a = body.index("begin{frontmatter}")
    b = body.index("begin{abstract}", a) - 1   # keep the backslash so the macro strips
    body = body[:a] + " " + body[b:]
body = re.sub(r"\\begin\{keyword\}.*?\\end\{keyword\}", " ", body, flags=re.S)
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
