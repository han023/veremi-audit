"""Cut the journal variant to ten pages.

T-ITS charges $175 per page beyond ten, so ten is a ceiling. Removing the visual
abstract alone was not enough: the journal class sets looser than the conference
class and the paper still ran to eleven.

Two cuts, chosen because each removes framing rather than evidence:

  1. Table I, the representative-work table, with its paragraph. It says which
     control each cited work lacks. The cascade demonstrates the same thing on our
     own runs, so the table is a signpost rather than a result.

  2. Section IV, the corpus reporting practice table. It motivates the audit by
     showing what the literature omits. The section becomes one paragraph citing
     the released CSV, which holds every count.

No experiment, caveat, scope statement or number from the results survives being
cut here. Both removed items remain in the artefact.
"""
from pathlib import Path

p = Path("workspace/paper/veremi_audit_journal.tex")
s = p.read_text(encoding="utf-8")
before = len(s)

# --- 1. Table I and its paragraph -------------------------------------------------
start = s.index("Table~\\ref{tab:touch} lists representative recent work.")
end = s.index(r"\end{table}", s.index(r"\label{tab:touch}")) + len(r"\end{table}")
s = s[:start] + s[end:]
# the two sentences that follow it referred to the table's rows
s = s.replace("""Azam et al.\\ aggregate movement features per node, then apply random folds.
That is exactly the first protocol in our cascade.
""", """Azam et al.\\ aggregate movement features per node, then apply random folds.
That is exactly the first protocol in our cascade.
""")
print("cut 1: Table I and its paragraph")

# --- 2. Section IV compressed to a paragraph --------------------------------------
sec_start = s.index(r"\section{Corpus Reporting Practice}")
sec_end = s.index(r"\section{Structural Artefacts}")
replacement = r"""\section{Corpus Reporting Practice}

The corpus shows what the literature reports about itself.
Of 92 full texts, 22 state an explicit threat model.
Nine state a beacon rate and nine an attacker fraction.
Four mention a ROC curve, and two any interval or test.
Three give a repository link, all to one restricted archive.
Eleven papers since 2021 mention ns-2, dormant since 2011.
Every count and its pattern ship as a released table.

Both quantities we vary most are the ones least reported.
That is the gap this audit measures rather than asserts.

"""
s = s[:sec_start] + replacement + s[sec_end:]
print("cut 2: Section IV compressed, Table V removed")

p.write_text(s, encoding="utf-8")
print("\nchars: %d -> %d (%.1f%% smaller)" % (before, len(s), 100 * (before - len(s)) / before))
