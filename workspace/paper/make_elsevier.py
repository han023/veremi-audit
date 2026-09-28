"""Build the Elsevier submission from the assembled paper.

Target: Vehicular Communications. Its guide rules out several things the IEEE
variants rely on, so this is a conversion rather than a class swap:

  - "A PDF is not an acceptable source file", so the .tex is what gets submitted
    and it has to compile on their side.
  - Sections must be numbered 1, 1.1, 1.1.1. IEEEtran gives I, II and A, B.
    elsarticle numbers this way by default, so the swap does it for free.
  - The title page needs a full postal address including the country.
  - A CRediT statement, a funding statement, a declaration of competing
    interests and a generative-AI declaration are all required, and none of them
    exist in the IEEE variants.

Content comes from the conference assembly, not the journal one. The journal cuts
existed only to reach T-ITS's ten-page limit before per-page charges; Elsevier sets
no such limit, so the fuller text goes in. Single-column preprint layout is the
Elsevier norm for submission and is easier to review than two columns.
"""
import re
from pathlib import Path

SRC = Path("workspace/paper/veremi_audit.tex")
DST = Path("workspace/paper/veremi_audit_elsevier.tex")

s = SRC.read_text(encoding="utf-8")
applied = []


def cut(old, new, label):
    global s
    assert old in s, "NOT FOUND: " + label
    s = s.replace(old, new, 1)
    applied.append(label)


# --- preamble ---------------------------------------------------------------------
head_end = s.index(r"\begin{document}")
s = r"""%% What VeReMi Measures --- structural artefacts in VANET misbehaviour benchmarks
%%
%% Submission source for Vehicular Communications (Elsevier).
%% Built by workspace/paper/make_elsevier.py from veremi_audit.tex. Do not edit by
%% hand: rerun the script instead, or the two will drift.
\documentclass[preprint,12pt]{elsarticle}

\usepackage{booktabs}
\usepackage{array}
\usepackage{graphicx}
\usepackage{url}
\usepackage{amsmath}
\usepackage[hidelinks]{hyperref}

%% elsarticle sets its own bibliography style; the manual list below is kept as-is.
\makeatletter
\def\ps@pprintTitle{%
  \let\@oddhead\@empty \let\@evenhead\@empty
  \def\@oddfoot{\centerline{\thepage}}\let\@evenfoot\@oddfoot}
\makeatother

""" + s[head_end:]
applied.append("preamble")

# --- front matter -----------------------------------------------------------------
title_start = s.index(r"\title{")
kw_end = s.index(r"\end{IEEEkeywords}") + len(r"\end{IEEEkeywords}")
block = s[title_start:kw_end]

m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", block, re.S)
abstract = m.group(1).strip()
m = re.search(r"\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}", block, re.S)
keywords = [k.strip().rstrip(".") for k in m.group(1).strip().split(",")]

front = r"""\begin{frontmatter}

%% no manual break: the IEEE title carried one to balance a two-column page,
%% which strands "VANET" on a line of its own in single column
\title{What VeReMi Measures: Structural Artefacts in VANET Misbehaviour Detection Benchmarks}

\author[hs]{Hannan Muzammil}
\ead{abdullhannan0311@gmail.com}
\ead[url]{https://www.hannsoft.org/}

\affiliation[hs]{organization={Hannsoft},
                 addressline={Township},
                 city={Lahore},
                 postcode={54700},
                 state={Punjab},
                 country={Pakistan}}

\begin{abstract}
%s
\end{abstract}

\begin{keyword}
%s
\end{keyword}

\end{frontmatter}""" % (abstract, "\n\\sep ".join(keywords))

s = s[:title_start] + front + s[kw_end:]
applied.append("front matter")

# \maketitle is part of frontmatter in elsarticle
s = s.replace("\n\\maketitle\n", "\n", 1)

# --- single column: starred floats and column widths ------------------------------
n = s.count(r"\begin{table*}")
s = s.replace(r"\begin{table*}", r"\begin{table}").replace(r"\end{table*}", r"\end{table}")
applied.append("%d starred table(s) unstarred" % n)

n = len(re.findall(r"width=\\columnwidth", s))
s = s.replace(r"width=\columnwidth", r"width=0.72\linewidth")
applied.append("%d figure width(s) rescaled" % n)

# --- statements Elsevier requires, placed before the reference list ---------------
DECLS = r"""\section*{CRediT authorship contribution statement}

\textbf{Hannan Muzammil:} Conceptualization, Methodology, Software, Formal
analysis, Investigation, Data curation, Validation, Visualization, Writing --
original draft, Writing -- review and editing.

\section*{Declaration of competing interest}

The author declares that he has no known competing financial interests or personal
relationships that could have appeared to influence the work reported in this
paper.

\section*{Funding}

This research did not receive any specific grant from funding agencies in the
public, commercial, or not-for-profit sectors.

\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}

During the preparation of this work the author used Claude (Anthropic) in order to
draft and edit text and to check the consistency of reported values. After using
this tool, the author reviewed and edited the content as needed and takes full
responsibility for the content of the published article.

\section*{Data availability}

The replication package, containing the analysis code, the independent verifiers
and every result table, is publicly archived at
\url{https://doi.org/10.5281/zenodo.22397725}.
The source archives are third-party deposits and are not redistributed.
Their own records are cited in the text.

"""
bib = s.index(r"\begin{thebibliography}")
s = s[:bib] + DECLS + s[bib:]
applied.append("CRediT, competing interest, funding, AI, data availability")

DST.write_text(s, encoding="utf-8")
print("wrote %s" % DST.name)
for a in applied:
    print("  " + a)
print("  sections: %d | tables: %d | figures: %d | references: %d"
      % (len(re.findall(r"\\section\{", s)), len(re.findall(r"\\begin\{table\}", s)),
         len(re.findall(r"\\begin\{figure\}", s)), s.count(r"\bibitem")))
