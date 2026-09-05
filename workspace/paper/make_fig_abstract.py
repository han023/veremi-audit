"""Figure 0 - the visual abstract.

Form: a two-lane schematic, not a chart. The claim is a contrast between two
protocols run over the same data, and what a reader needs is the pairing plus the
two end values. A bar chart of two numbers would carry less and imply a magnitude
comparison that is not the point.

The numbers are read from the result CSVs, not typed, so the figure cannot drift
from the tables. Colour uses categorical slots 1 and 2 from the validated palette,
the same blue and orange as Figures 1 to 3, so the reader carries the mapping.

Identity is never colour alone: each lane is labelled, and each value is printed.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrow, FancyBboxPatch

A = "#2a78d6"      # slot 1, the published protocol
B = "#eb6834"      # slot 2, the deployable one
INK = "#0b0b0b"
SOFT = "#52514e"
PALE_A = "#dbe8f8"
PALE_B = "#fbe3d8"

casc = pd.read_csv("workspace/sybilbench/exp9_cascade.csv")
g = casc[casc.archive == "GridSybil_0709"].set_index("stage")["auc"]
published, controlled = float(g["S0_published"]), float(g["S6_no_rate"])

scalar = pd.read_csv("workspace/sybilbench/exp1b_rate_baseline_v2.csv")
# The count and the value must share a threshold, and the claim says ONE scalar,
# so this counts message count alone rather than the better of two per archive.
# Message count clears 0.99 on six. 0.993 would drop DataReplaySybil sparse at
# 0.9929, leaving five, so the count and the printed threshold would disagree.
THRESHOLD = 0.99
# the log reports the same scalar the caption counts, so the two cannot drift
best_scalar = float(scalar.AUC_msgcount_alone.max())
n_solved = int((scalar.AUC_msgcount_alone >= THRESHOLD).sum())

path = pd.read_csv("workspace/verify/v5_pathloss.csv").set_index("fit")
oof = float(path.loc["all_links", "auc_oof"])

fig, ax = plt.subplots(figsize=(3.45, 2.25))
ax.set_xlim(0, 10)
ax.set_ylim(-0.1, 5.2)
ax.axis("off")


def lane(y, colour, pale, title, line1, line2, value):
    # the box has to hold two short lines; one long line overran into the number
    ax.add_patch(FancyBboxPatch((0.45, y - 0.62), 6.15, 1.24,
                                boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=0, facecolor=pale, zorder=1))
    ax.text(0.72, y + 0.34, title, fontsize=6.6, color=colour, va="center",
            fontweight="bold", zorder=3)
    ax.text(0.72, y - 0.06, line1, fontsize=5.5, color=SOFT, va="center", zorder=3)
    ax.text(0.72, y - 0.40, line2, fontsize=5.5, color=SOFT, va="center", zorder=3)
    ax.add_patch(FancyArrow(6.75, y, 0.55, 0, width=0.035, head_width=0.2,
                            head_length=0.22, length_includes_head=True,
                            color=colour, zorder=3))
    ax.text(7.55, y, "%.3f" % value, fontsize=12.5, color=colour, va="center",
            ha="left", fontweight="bold", zorder=3)


ax.text(0.45, 4.78, "the same eight VeReMi archives", fontsize=7.2, color=INK,
        fontweight="bold")

lane(3.62, A, PALE_A, "as published",
     "ground-truth key   |   raw pseudonym",
     "random folds   |   30% attackers", published)
lane(2.02, B, PALE_B, "as a receiver would see it",
     "observed identities   |   disjoint split",
     "3% attackers   |   jitter", controlled)

ax.text(7.55, 4.62, "AUC", fontsize=6.4, color=SOFT, ha="left")

ax.plot([0.45, 9.3], [1.12, 1.12], color="#d8d7d2", lw=0.8)
ax.text(0.45, 0.68,
        "Message count alone reaches AUC %.2f or better on %d of the eight."
        % (THRESHOLD, n_solved),
        fontsize=6.4, color=INK)
ax.text(0.45, 0.20,
        "Signal-strength position verification reaches %.3f, which is chance." % oof,
        fontsize=6.4, color=INK)

fig.tight_layout(pad=0.15)
fig.savefig("workspace/paper/fig_abstract.pdf", bbox_inches="tight")
fig.savefig("workspace/paper/fig_abstract.png", dpi=240, bbox_inches="tight")
print("wrote fig_abstract: published %.3f, controlled %.3f, "
      "msgcount max %.3f, >=%.2f on %d, phy %.3f"
      % (published, controlled, best_scalar, THRESHOLD, n_solved, oof))
