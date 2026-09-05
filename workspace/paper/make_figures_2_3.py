"""Figures 2 and 3.

Fig 2, pseudonym leakage: a slope chart. The claim is that a quantity collapses
when the correspondence is broken, so the reader needs the pair, not two bars.
Log scale, because the fall spans three orders and a linear axis would show a
line to the floor and nothing else.

Fig 3, prevalence sensitivity: two lines on one axis. Both are in AUC/AP units on
[0,1], so this is not a dual axis; it is two comparable series. The point is that
one is flat and the other is not.

Colour: categorical slots 1 and 2 from the validated palette, the same blue and
orange used in Figure 1, so a reader carries the mapping across figures.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

A = "#2a78d6"      # slot 1
B = "#eb6834"      # slot 2
INK = "#0b0b0b"
SOFT = "#52514e"
GRID = "#d8d7d2"

LABEL = {
    "GridSybil_0709": "GridSybil (dense)", "GridSybil_1416": "GridSybil (sparse)",
    "DataReplaySybil_0709": "DataReplay (dense)", "DataReplaySybil_1416": "DataReplay (sparse)",
    "DoSRandomSybil_0709": "DoSRandom (dense)", "DoSRandomSybil_1416": "DoSRandom (sparse)",
    "DoSDisruptiveSybil_0709": "DoSDisrupt. (dense)", "DoSDisruptiveSybil_1416": "DoSDisrupt. (sparse)",
}

# ------------------------------------------------------------------ Figure 2
d = pd.read_csv("workspace/sybilbench/exp13_pseudonym_decode.csv")
d["label"] = d["archive"].map(LABEL)
d = d.sort_values("decode_accuracy", ascending=False)

fig, ax = plt.subplots(figsize=(3.45, 2.5))
x = [0, 1]
for _, r in d.iterrows():
    ax.plot(x, [r.decode_accuracy, r.decode_accuracy_shuffled],
            color=A, lw=1.4, alpha=0.75, solid_capstyle="round", zorder=2)
ax.scatter([0] * len(d), d.decode_accuracy, s=30, color=A, zorder=3,
           edgecolors="white", linewidths=0.8)
ax.scatter([1] * len(d), d.decode_accuracy_shuffled, s=30, color=B, zorder=3,
           edgecolors="white", linewidths=0.8)
ax.axhline(d.chance_accuracy.mean(), color=GRID, lw=1, ls=(0, (3, 3)), zorder=1)
ax.annotate("chance", (1.06, d.chance_accuracy.mean()), fontsize=6.4, color=SOFT,
            va="center", annotation_clip=False)

ax.set_yscale("log")
ax.set_xlim(-0.28, 1.28)
ax.set_xticks(x)
ax.set_xticklabels(["real pseudonyms", "correspondence\npermuted"], fontsize=7.4, color=INK)
ax.set_ylabel("sender recovered (fraction)", fontsize=7.4, color=INK)
ax.tick_params(axis="y", labelsize=7, colors=SOFT, length=0)
ax.tick_params(axis="x", length=0)
ax.yaxis.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_visible(False)
ax.annotate("%.0f%%" % (100 * d.decode_accuracy.mean()), (0, d.decode_accuracy.mean()),
            textcoords="offset points", xytext=(-8, 0), ha="right", va="center",
            fontsize=7, color=INK)
ax.annotate("%.1f%%" % (100 * d.decode_accuracy_shuffled.mean()),
            (1, d.decode_accuracy_shuffled.mean()), textcoords="offset points",
            xytext=(9, 0), ha="left", va="center", fontsize=7, color=INK)
fig.tight_layout(pad=0.35)
fig.savefig("workspace/paper/fig_decode.pdf", bbox_inches="tight")
fig.savefig("workspace/paper/fig_decode.png", dpi=220, bbox_inches="tight")
print("wrote fig_decode: %.3f real, %.4f permuted" %
      (d.decode_accuracy.mean(), d.decode_accuracy_shuffled.mean()))

# ------------------------------------------------------------------ Figure 3
s = pd.read_csv("workspace/sybilbench/exp10_sensitivity.csv")
pv = s[s.sweep == "prevalence"].copy()
nat = s[s.sweep == "prevalence_native"]
pv["value"] = pv["value"].astype(float)
pv = pv.sort_values("value")
xs = list(pv.value) + [float(nat.prevalence_obs.iloc[0])]
auc = list(pv.auc) + [float(nat.auc.iloc[0])]
ap = list(pv.ap) + [float(nat.ap.iloc[0])]

fig, ax = plt.subplots(figsize=(3.45, 2.4))
ax.plot(xs, auc, color=A, lw=2, marker="o", ms=4.5, mec="white", mew=0.8, label="AUC", zorder=3)
ax.plot(xs, ap, color=B, lw=2, marker="o", ms=4.5, mec="white", mew=0.8,
        label="average precision", zorder=3)
ax.axhline(0.5, color=GRID, lw=1, ls=(0, (3, 3)), zorder=1)
ax.set_xscale("log")
# matplotlib's default log minor labels collide into mush at this range; set them
import matplotlib.ticker as mt
ax.xaxis.set_major_locator(mt.FixedLocator(xs))
ax.xaxis.set_major_formatter(mt.FuncFormatter(
    lambda v, _pos: "%.0f%%" % (100 * v)))
ax.xaxis.set_minor_locator(mt.NullLocator())
ax.set_xlabel("attacker prevalence among identities", fontsize=7.4, color=INK)
ax.set_ylim(0, 1.04)
ax.set_ylabel("score", fontsize=7.4, color=INK)
ax.tick_params(labelsize=7, colors=SOFT, length=0)
ax.yaxis.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_visible(False)
ax.annotate("AUC", (xs[-1], auc[-1]), textcoords="offset points", xytext=(-4, 7),
            ha="right", fontsize=7, color=A)
ax.annotate("average precision", (xs[0], ap[0]), textcoords="offset points", xytext=(4, -11),
            ha="left", fontsize=7, color=B)
fig.tight_layout(pad=0.35)
fig.savefig("workspace/paper/fig_prevalence.pdf", bbox_inches="tight")
fig.savefig("workspace/paper/fig_prevalence.png", dpi=220, bbox_inches="tight")
print("wrote fig_prevalence: AUC %.3f-%.3f, AP %.3f-%.3f" %
      (min(auc), max(auc), min(ap), max(ap)))
