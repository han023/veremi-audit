"""Two critical corrections.

CRITICAL 1 -- the timing arithmetic did not match the measurement.

The paper derived a ghost interval of NT from a benign period T, giving 100 s for
N = 100. The measured value is 50 s. The derivation assumed the attacker transmits
at the benign rate; it does not. Measured (v21): the denial-of-service families run
at about 2 Hz, twice benign, which is the denial-of-service component of the attack.
The correct relation is N / R, and 100 / 2.009 = 49.8 s, which is what we see.

CRITICAL 2 -- the information-theoretic aside invited a wrong reading.

"Mutual information between pseudonym and sender is exactly the entropy" is true
here, because a pseudonym determines its owner so the conditional entropy is zero.
But it reads as a general claim, which is false, and the permutation we described
does not break that determinism, so it is not a null. The aside goes. What remains
is I(D; S) between the decoder output and the truth: a proper mutual information,
bounded by H(S), non-degenerate because the decoder can be wrong.
"""
from pathlib import Path

body = Path("workspace/paper/body_new.tex")
asm = Path("workspace/paper/assemble.py")
s = body.read_text(encoding="utf-8")
a = asm.read_text(encoding="utf-8")

# --- CRITICAL 1: body ------------------------------------------------------------
old = """The mechanism is arithmetic, not behaviour.
An attacker holding $N$ identities keeps one transmit budget.
Splitting a period $T$ across them gives each ghost interval $NT$.
Benign identities beacon at $T$, so the gap is the factor $N$.
With $T=1$\\,s and $N=100$ the two populations cannot overlap.
Median inter-arrival is then a sufficient statistic, and geometry is redundant."""
assert old in s, "timing derivation not found"
s = s.replace(old, "%%BUDGET%%")
body.write_text(s, encoding="utf-8")
print("critical 1: body derivation replaced with a placeholder")

# --- CRITICAL 2: generator -------------------------------------------------------
old2 = '''        "",
        r"One naive version of this statistic is worth avoiding.",
        r"Mutual information between pseudonym and sender is exactly the entropy.",
        r"It is also exactly the entropy under a permuted control.",
        r"A unique identifier determines its owner whoever that is.",
        r"That measures uniqueness, not structure, so we do not report it.",
'''
assert old2 in a, "MI aside not found in generator"
a = a.replace(old2, "")
print("critical 2: mutual-information aside removed")

# reframe the remaining statement as the mutual information it is
old3 = r'''        r"The identifier's shape therefore supplies %.0f\\%% to %.0f\\%% of them." % ('''
new3 = r'''        r"The identifier's shape supplies %.0f\\%% to %.0f\\%% of those bits." % ('''
assert old3 in a, "bits sentence not found"
a = a.replace(old3, new3)

old4 = r'''        r"After the decoder speaks, %.2f to %.2f bits remain." % ('''
new4 = r'''        r"After an untrained structural decoder, %.2f to %.2f bits remain." % ('''
assert old4 in a
a = a.replace(old4, new4)

# --- CRITICAL 1: generator -------------------------------------------------------
gen = '''def budget_text() -> str:
    b = pd.read_csv("workspace/verify/v21_attacker_budget.csv").set_index("archive")
    d = b.loc["DoSRandomSybil_0709"]
    return "\\n".join([
        r"The mechanism is arithmetic, and we measured its terms.",
        r"An attacker emits at aggregate rate $R$ across $N$ identities.",
        r"Each identity then transmits about every $N/R$ seconds.",
        r"These families run at $R=%.1f$\\,Hz, twice the benign rate." % d.aggregate_rate_hz_median,
        r"That doubling is the denial-of-service part of the attack.",
        r"With $N=%d$ the predicted gap is %.0f\\,s." % (
            d.identities_per_attacker_median, d.implied_interval_from_rate),
        r"We measure %.0f\\,s, so arithmetic and archive agree." % d.ghost_interval_median_s,
        "",
        r"Benign identities beacon once per second throughout.",
        r"Median inter-arrival is therefore a sufficient statistic here.",
        r"Geometry is redundant by construction, not by weakness.",
    ])


def sensitivity_table() -> str:'''
assert "def sensitivity_table() -> str:" in a
a = a.replace("def sensitivity_table() -> str:", gen, 1)
a = a.replace('    body = body.replace("%%INFORMATION%%", information_text())',
              '    body = body.replace("%%BUDGET%%", budget_text())\n'
              '    body = body.replace("%%INFORMATION%%", information_text())', 1)
asm.write_text(a, encoding="utf-8")
print("generators wired in")
