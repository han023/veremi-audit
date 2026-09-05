"""Build the IEEE Transactions variant from the assembled conference paper.

One script, idempotent, so the journal PDF can be rebuilt after any change to the
body without replaying a chain of edits.

T-ITS charges $175 per page past ten, so ten is a ceiling. Getting there needs the
journal class plus five cuts, each removing framing rather than evidence:

  1. the visual abstract, which duplicates Table XI;
  2. Table I, whose point the cascade makes on our own runs;
  3. the corpus reporting table, compressed to a paragraph citing the released CSV;
  4. the Discussion lists, compressed without dropping an item;
  5. Limitations, compressed with every threat still named.

Dropping Table I orphans one citation, which is removed so no entry is uncited.
"""
import re
from pathlib import Path

SRC = Path("workspace/paper/veremi_audit.tex")
DST = Path("workspace/paper/veremi_audit_journal.tex")

s = SRC.read_text(encoding="utf-8")
applied = []


def cut(old, new, label):
    global s
    assert old in s, "NOT FOUND: " + label
    s = s.replace(old, new, 1)
    applied.append(label)


# --- class and running head ------------------------------------------------------
cut(r"\documentclass[conference]{IEEEtran}",
    r"\documentclass[journal]{IEEEtran}", "journal class")
cut(r"\maketitle",
    "\\markboth{IEEE Transactions on Intelligent Transportation Systems}%\n"
    "{Muzammil: What VeReMi Measures}\n\\maketitle", "running head")

# T-ITS wants the affiliation as a title footnote rather than an author block,
# and Regular Papers carry a biography. The conference variant keeps its block.
a = s.index(r"\author{")
b = s.index("\n\n", a)
s = s[:a] + r"""\author{Hannan~Muzammil%
\thanks{Manuscript submitted for review. This work received no external funding.}%
\thanks{H. Muzammil is with Hannsoft (e-mail: abdullhannan0311@gmail.com;
web: https://www.hannsoft.org/).}%
\thanks{The replication package is archived at doi:10.5281/zenodo.22397725.}}
""" + s[b + 1:]
applied.append("author footnote")

cut(r"\end{document}",
    r"""\begin{IEEEbiographynophoto}{Hannan Muzammil}
is an independent researcher at Hannsoft. His work concerns measurement
and reproducibility in vehicular network security, with a focus on what
shared evaluation benchmarks encode. He maintains the replication package
accompanying this paper.
\end{IEEEbiographynophoto}

\end{document}""", "biography")

# --- 1. visual abstract ----------------------------------------------------------
a = s.index(r"\begin{figure}[t]")
b = s.index(r"\end{figure}", a) + len(r"\end{figure}")
assert "fig_abstract" in s[a:b], "first figure is not the visual abstract"
s = s[:a] + s[b:]
s = s.replace("Figure~\\ref{fig:abstract} summarises what follows.\n", "")
applied.append("visual abstract")

# --- 2. Table I and its paragraph ------------------------------------------------
a = s.index("Table~\\ref{tab:touch} lists representative recent work.")
b = s.index(r"\end{table}", s.index(r"\label{tab:touch}")) + len(r"\end{table}")
s = s[:a] + s[b:]
applied.append("Table I")

# the citation it carried is now orphaned
a = s.index(r"\bibitem{morton2024}")
b = s.index("\n\n", a) + 2
s = s[:a] + s[b:]
applied.append("orphaned citation")

# --- 3. corpus reporting section -------------------------------------------------
a = s.index(r"\section{Corpus Reporting Practice}")
b = s.index(r"\section{Structural Artefacts}")
s = s[:a] + r"""\section{Corpus Reporting Practice}

The corpus shows what the literature reports about itself.
Of 92 full texts, 22 state an explicit threat model.
Nine state a beacon rate and nine an attacker fraction.
Four mention a ROC curve, and two any interval or test.
Three give a repository link, all to one restricted archive.
Eleven papers since 2021 mention ns-2, dormant since 2011.
Every count and its pattern ship as a released table.

Both quantities we vary most are the ones least reported.
That is the gap this audit measures rather than asserts.

""" + s[b:]
applied.append("Section IV")

# --- 4. Discussion lists ---------------------------------------------------------
cut("""We propose the cascade itself as a pre-publication check.
Any detector evaluated on these archives can be run through it.
A result that survives S0 to S6 has passed our controls.
A result that collapses at S2 shows strong sensitivity to the partition.
The released script takes an archive and a model flag.
It reports the ladder for whatever detector is supplied.
A logistic regression run through it behaves the same way.
That removal is followed by 0.096 there and 0.064 here.
We tested two model families, which agree on that ordering.

We also propose seven reporting rules.
State the attacker fraction and beacon rate always.
Name the attack family and the density used.
Report an ablation separating timing from geometry.
Compare against a single-scalar baseline first.
Match evidence per identity when comparing policies.
Use identity-free tokens and disjoint splits by vehicle.
Publish the prevalence sweep, not one operating point.""",
    """We propose the cascade itself as a pre-publication check.
A result surviving S0 to S6 has passed our controls.
A result collapsing at S2 shows strong sensitivity to the partition.
The released script accepts any detector through a model flag.
A logistic regression behaves the same way, moving 0.096 against 0.064.
We tested two model families, which agree on that ordering.

Seven reporting rules follow from the measurements.
Always state the attacker fraction, beacon rate and density.
Name the attack family, and separate timing from geometry.
Compare against a single-scalar baseline before any model.
Match evidence per identity when comparing policies.
Use identity-free tokens and vehicle-disjoint splits.
Publish the prevalence sweep, not one operating point.""",
    "Discussion lists")

cut("""One diagnostic recurred each time.
Results were too strong for the available signal.
In the linkage experiment no pair feature passed AUC 0.65.
A forest on those same features still reported 1.000.
That gap indicated leakage, and leakage was present.""",
    """One diagnostic recurred each time: a result too strong for its signal.
No pair feature passed AUC 0.65, yet a forest on them reported 1.000.
That gap indicated leakage, and leakage was present.""",
    "diagnostic paragraph")

# --- 5. ethics and limitations ---------------------------------------------------
cut("""This work analyses published artefacts and published papers.
It involves no human subjects and no personal data.
The archives are simulated, so no vehicle or driver is real.

We name specific papers in Table~\\ref{tab:touch}.
We do so to locate protocol choices, not to allege misconduct.
Those choices were reasonable given what was documented.
Several are choices we made ourselves and later corrected.

We also describe a dataset withdrawn under an authorship dispute.
We report only its stated availability, which is a public fact.
We take no position on the dispute itself.
We did not obtain, mirror or redistribute that data.""",
    """This work analyses published artefacts and involves no human subjects.
The archives are simulated, so no vehicle or driver is real.
We name published work to locate protocol choices, alleging no misconduct.
One dataset we describe is withdrawn under an authorship dispute.
We report its stated availability, take no position, and never obtained it.""",
    "ethics")

cut("""Our audit covers the Sybil archives specifically.
Other attack families may behave differently.
Our controls use one detector family per experiment.
Stronger detectors could change absolute values.

Three threats deserve naming rather than listing.

Simulation realism bounds everything we report.
These archives model propagation and mobility, not radios.
A shortcut present in simulation need not survive on hardware.
Equally, hardware may add shortcuts a simulator never shows.

Jitter is applied afterwards to logged transmission times.
It therefore ignores medium access and collisions.
A real jittering attacker would interact with the channel.
Our jitter is an upper bound on how cheap the escape is.
We report it as one distribution, uniform, not as a model.

Observations are not independent within a vehicle.
Consecutive beacons from one sender are strongly correlated.
Our splits are vehicle-disjoint, which handles the worst of that.
Temporal dependence remains within folds.
Uncertainty estimates are therefore optimistic.

Two further limits are structural.""",
    """Our audit covers the Sybil archives specifically.
Other attack families may behave differently.

Simulation realism bounds everything we report.
These archives model propagation and mobility, not radios.
A shortcut seen in simulation need not survive on hardware.
Equally, hardware may add shortcuts a simulator never shows.

Jitter is applied afterwards to logged transmission times.
It ignores medium access, so it bounds how cheap the escape is.
We report one uniform distribution, not a channel model.

Observations are not independent within a vehicle.
Vehicle-disjoint splits handle the worst of that dependence.
Temporal dependence remains within folds.
Uncertainty estimates are therefore optimistic.

Two further limits are structural.""",
    "limitations")

cut("""External validity now rests on two datasets, not one.
Section~\\ref{sec:generalise} tests the shortcuts on NextGen.
Both remain simulator output from one research lineage.""",
    """External validity rests on two datasets, not one.
Both remain simulator output from one research lineage.""",
    "external validity")

# --- 6. availability walkthrough -------------------------------------------------
cut("""The route from raw data to results has four steps.
First, verify archive checksums against the Zenodo records.
Second, parse archives into cached views and ground truth.
Third, recover pseudonyms so the leakage arm is honest.
Fourth, run the numbered experiments in any order.

Every result file names the script that produced it.""",
    """Every result file names the script that produced it.""",
    "availability walkthrough")

cut("""Scripts, controls and result tables are released with this paper.
They reproduce every number above from the raw archives.
The archive is deposited at \\url{10.5281/zenodo.22397725}.
A container image rebuilds and re-verifies it in one command.
The full eight-archive census ships as a machine-readable table.
Every statistic we measured is a column, not only those printed here.

Every result file names the script that produced it.
A manifest records a hash per file and the library versions.
Independent metric implementations are included and self-tested.""",
    """Scripts, controls and result tables reproduce every number above.
The archive is deposited at \\url{10.5281/zenodo.22397725}.
A container image rebuilds and re-verifies it in one command.
The eight-archive census ships as a machine-readable table.
Every measured statistic is a column there, not only printed ones.
Every result file names the script that produced it.
A manifest records hashes, library versions and self-tested metric code.""",
    "availability")

# --- 8. conclusion ----------------------------------------------------------------
cut("""One untrained count scalar exceeds AUC 0.99 on six archives.
Timing alone reaches near-perfect linkage accuracy.
Geometry, the physically motivated signal, performs far worse.""",
    """One untrained count scalar exceeds AUC 0.99 on six archives.
Geometry, the physically motivated signal, performs far worse.""",
    "conclusion findings")

cut("""Finally, VeReMi 2018 cannot validate the signal-strength family.
An accessible calibrated dataset is therefore a necessity.

Our code, controls and checklist accompany this paper.
We hope future results become comparable again.""",
    """VeReMi 2018 cannot validate the signal-strength family.
An accessible calibrated dataset is therefore a necessity.
Our code, controls and checklist accompany this paper.""",
    "conclusion close")

# --- 7. schema table kinematic rows ----------------------------------------------
cut(r"""\texttt{pos}, \texttt{pos\_noise} & claimed position, variance & yes \\
\texttt{spd}, \texttt{spd\_noise} & claimed speed, variance & yes \\
\texttt{acl}, \texttt{acl\_noise} & claimed acceleration & yes \\
\texttt{hed}, \texttt{hed\_noise} & claimed heading & yes \\""",
    r"""\texttt{pos}, \texttt{spd}, & claimed kinematics, each & yes \\
\texttt{acl}, \texttt{hed} & with its noise variance & \\""",
    "schema rows")

DST.write_text(s, encoding="utf-8")
print("wrote %s" % DST.name)
print("  applied: %s" % ", ".join(applied))
print("  figures: %d | references: %d"
      % (len(re.findall(r"\\begin\{figure\}", s)), s.count(r"\bibitem")))
