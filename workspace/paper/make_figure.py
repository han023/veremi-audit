"""Figure 1 — timing evidence versus geometric evidence, per Sybil family.

Form: dumbbell. The paper's point is the *gap* between two evidence types per archive, and a dumbbell
encodes exactly that. A grouped bar chart would need a truncated y-axis (AUC lives in 0.5-1.0), which
misleads; dots carry no zero-baseline implication.

Colour: two categorical slots from the validated reference palette, blue #2a78d6 and orange #eb6834.
Checked with the skill's validator in light mode: all six checks PASS, worst-pair CVD Delta E 24.7.

Print figure, so no hover layer and no dark mode. Identity is carried by a legend plus direct value
labels, never by colour alone.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GEOMETRY = "#2a78d6"   # categorical slot 1
TIMING = "#eb6834"     # categorical slot 2
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#d8d7d2"

LABELS = {
    "GridSybil_0709": "GridSybil (dense)",
    "GridSybil_1416": "GridSybil (sparse)",
    "DoSRandomSybil_0709": "DoSRandomSybil (dense)",
    "DoSRandomSybil_1416": "DoSRandomSybil (sparse)",
    "DoSDisruptiveSybil_0709": "DoSDisruptiveSybil (dense)",
    "DoSDisruptiveSybil_1416": "DoSDisruptiveSybil (sparse)",
}

df = pd.read_csv("workspace/sybilbench/exp1_results.csv").dropna(subset=["auc_geometry_only"])
df = df[df["archive"].isin(LABELS)].copy()
df["label"] = df["archive"].map(LABELS)
df = df.sort_values("auc_geometry_only")

fig, ax = plt.subplots(figsize=(3.45, 2.5))          # IEEE single column
y = range(len(df))

# connector first, so the dots sit on top of it
for yi, (g, t) in enumerate(zip(df.auc_geometry_only, df.auc_timing_only)):
    ax.plot([g, t], [yi, yi], color=GRID, lw=2, solid_capstyle="round", zorder=1)

ax.scatter(df.auc_timing_only, y, s=42, color=TIMING, zorder=3,
           label="timing only", edgecolors="white", linewidths=0.8)
ax.scatter(df.auc_geometry_only, y, s=42, color=GEOMETRY, zorder=3,
           label="geometry only", edgecolors="white", linewidths=0.8)

# direct labels on the varying series; the timing series is pinned near 1.0 and needs none
for yi, g in zip(y, df.auc_geometry_only):
    ax.annotate(f"{g:.2f}", (g, yi), textcoords="offset points", xytext=(-6, 0),
                ha="right", va="center", fontsize=6.4, color=INK_SOFT)

# dashed rule marks chance (AUC 0.5); named in the caption rather than annotated in-plot,
# where it collided with the legend and added ink for one already-obvious value
ax.axvline(0.5, color=GRID, lw=1, ls=(0, (3, 3)), zorder=0)

ax.set_yticks(list(y))
ax.set_yticklabels(df.label, fontsize=7, color=INK)
ax.set_xlim(0.46, 1.045)
ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.tick_params(axis="x", labelsize=7, colors=INK_SOFT, length=0)
ax.tick_params(axis="y", length=0)
ax.set_xlabel("pairwise identity-linkage AUC", fontsize=7.4, color=INK)

ax.xaxis.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_visible(False)

ax.set_ylim(-1.15, len(df) - 0.4)   # room for the legend below the marks, not on top of them
leg = ax.legend(loc="upper left", bbox_to_anchor=(-0.02, 0.16), fontsize=6.8, ncol=2,
                frameon=False, handletextpad=0.35, borderpad=0.2, columnspacing=1.1)
for text in leg.get_texts():
    text.set_color(INK)

fig.tight_layout(pad=0.35)
fig.savefig("workspace/paper/fig_ablation.pdf", bbox_inches="tight")
fig.savefig("workspace/paper/fig_ablation.png", dpi=220, bbox_inches="tight")
print("wrote workspace/paper/fig_ablation.pdf and .png")
print(df[["label", "auc_geometry_only", "auc_timing_only"]].to_string(index=False))
