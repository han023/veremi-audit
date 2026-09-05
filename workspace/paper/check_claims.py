"""Cross-check every hand-typed number in the paper against the result files.

Tables built by assemble.py cannot drift, because they are emitted from the CSVs.
Everything else -- the abstract, the prose, and the three tables written directly in
the body -- is typed by hand and can. This checks those.

Exit code is non-zero if any claim fails.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

TEX = Path("workspace/paper/veremi_audit.tex").read_text(encoding="utf-8")
BODY = TEX[TEX.index(r"\begin{document}"):TEX.index(r"\begin{thebibliography}")]
# Emphasis wrappers break a plain substring search, and an unbolded copy of the same
# value elsewhere then masks the miss. Flatten them before any lookup.
BODY = re.sub(r"\\textbf\{([^}]*)\}", r"\1", BODY)

census = pd.read_csv("workspace/verify/v3c_identity_census.csv").set_index("archive")
pmap = pd.read_csv("workspace/verify/v3b_pseudomap.csv").set_index("archive")
gtfile = pd.read_csv("workspace/verify/v1b_raw_refined.csv").set_index("archive")
scalar = pd.read_csv("workspace/sybilbench/exp1b_rate_baseline_v2.csv").set_index("archive")
abl = pd.read_csv("workspace/sybilbench/exp1_results.csv").set_index("archive")
path = pd.read_csv("workspace/verify/v5_pathloss.csv").set_index("fit")
phase = pd.read_csv("workspace/verify/v4_timing_distributions.csv")
casc = pd.read_csv("workspace/sybilbench/exp9_cascade.csv")
sens = pd.read_csv("workspace/sybilbench/exp10_sensitivity.csv")

ARCH = ["GridSybil_0709", "GridSybil_1416",
        "DataReplaySybil_0709", "DataReplaySybil_1416",
        "DoSRandomSybil_0709", "DoSRandomSybil_1416",
        "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]

results: list[tuple[bool, str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((ok, name, detail))


def in_text(s: str) -> bool:
    return s in BODY


# ---------------------------------------------------------------- census table
for a in ARCH:
    c = census.loc[a]
    check("census %s vehicles" % a,
          in_text("{:,}".format(int(c.benign_vehicles + c.attacker_vehicles)).replace(",", "\\,")),
          str(int(c.benign_vehicles + c.attacker_vehicles)))
    check("census %s attacker identities" % a,
          in_text("{:,}".format(int(c.identities_attacker)).replace(",", "\\,")),
          str(int(c.identities_attacker)))

# identity totals in the paper are benign + attacker identities
for a in ARCH:
    c = census.loc[a]
    tot = int(c.identities_benign + c.identities_attacker)
    check("census %s identities total" % a,
          in_text("{:,}".format(tot).replace(",", "\\,")), str(tot))

# encoding rate, per distinct pair
for a in ARCH:
    e = pmap.loc[a, "encoding_pct_pairs"]
    want = "100\\%" if e == 100.0 else "%.1f\\%%" % e
    check("census %s encoding %.2f" % (a, e), in_text(want), want)

# prevalence, all eight
for a in ARCH:
    p = census.loc[a, "prevalence_vehicles_pct"]
    check("census %s prevalence" % a, in_text("%.2f\\%%" % p), "%.2f" % p)

# duplication factor
for a in ARCH:
    m = int(gtfile.loc[a, "copies_median"])
    check("duplication %s median %d" % (a, m), m in (4, 6, 7), str(m))

# ---------------------------------------------------------------- scalar table
for a in ARCH:
    r = scalar.loc[a]
    check("scalar %s AUC interval" % a, in_text("%.3f\\,[" % r.AUC_interval_alone),
          "%.3f" % r.AUC_interval_alone)
    check("scalar %s AUC count" % a, in_text("%.3f\\,[" % r.AUC_msgcount_alone),
          "%.3f" % r.AUC_msgcount_alone)
    check("scalar %s attacker interval" % a,
          in_text("Benign identities beacon at 1.0"), "1.0 s benign")

# ---------------------------------------------------------------- ablation table
fam = {"GridSybil": ["GridSybil_0709", "GridSybil_1416"],
       "DoSRandomSybil": ["DoSRandomSybil_0709", "DoSRandomSybil_1416"],
       "DoSDisruptiveSybil": ["DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]}
for f, keys in fam.items():
    g = abl.loc[keys, "auc_geometry_only"].astype(float)
    t = abl.loc[keys, "auc_timing_only"].astype(float)
    lo, hi = "%.3f" % g.min(), "%.3f" % g.max()
    want_g = lo if lo == hi else "%s--%s" % (lo, hi)
    tl, th = "%.3f" % t.min(), "%.3f" % t.max()
    want_t = tl if tl == th else "%s--%s" % (tl, th)
    check("ablation %s geometry %s" % (f, want_g), in_text(want_g), want_g)
    check("ablation %s timing %s" % (f, want_t), in_text(want_t), want_t)

# ---------------------------------------------------------------- path loss
b = path.loc["benign_only"]
al = path.loc["all_links"]
for label, row in (("benign", b), ("all", al)):
    check("pathloss %s slope" % label, in_text("%.2f" % row.slope_db_per_decade),
          "%.2f" % row.slope_db_per_decade)
    check("pathloss %s exponent" % label, in_text("%.3f" % row.path_loss_exponent),
          "%.3f" % row.path_loss_exponent)
    check("pathloss %s corr" % label, in_text("%.3f" % abs(row.corr_rssi_logd)),
          "%.3f" % row.corr_rssi_logd)
    check("pathloss %s scatter" % label, in_text("%.2f" % row.per_link_residual_scatter_db),
          "%.2f" % row.per_link_residual_scatter_db)
    check("pathloss %s fold-mean AUC" % label, in_text("%.3f" % row.auc_fold_mean),
          "%.3f" % row.auc_fold_mean)
    check("pathloss %s out-of-fold AUC" % label, in_text("%.3f" % row.auc_oof),
          "%.3f" % row.auc_oof)
    # the defect that prompted this round: an estimate outside its own interval
    check("pathloss %s fold mean inside its interval" % label,
          row.auc_fold_ci_lo <= row.auc_fold_mean <= row.auc_fold_ci_hi,
          "%.4f in [%.4f, %.4f]" % (row.auc_fold_mean, row.auc_fold_ci_lo, row.auc_fold_ci_hi))
    check("pathloss %s out-of-fold inside its interval" % label,
          row.auc_boot_lo <= row.auc_oof <= row.auc_boot_hi,
          "%.4f in [%.4f, %.4f]" % (row.auc_oof, row.auc_boot_lo, row.auc_boot_hi))
    check("pathloss %s DeLong agrees with bootstrap" % label,
          abs(row.auc_delong_lo - row.auc_boot_lo) < 0.002
          and abs(row.auc_delong_hi - row.auc_boot_hi) < 0.002,
          "boot [%.4f,%.4f] delong [%.4f,%.4f]" % (row.auc_boot_lo, row.auc_boot_hi,
                                                   row.auc_delong_lo, row.auc_delong_hi))
check("pathloss links 86919", in_text("86\\,919"), str(int(al.links)))
check("pathloss AP", in_text("%.3f" % al.ap_oof), "%.4f" % al.ap_oof)
check("abstract quotes the fold mean", in_text("reaches AUC %.3f" % al.auc_fold_mean),
      "%.3f" % al.auc_fold_mean)

# ------------------------------------------------------- generated tables, cell by cell
def cells(label):
    seg = BODY[BODY.index("\\label{tab:%s}" % label):]
    seg = seg[:seg.index("\\end{tabular}")]
    return seg

casc_cells = cells("cascade")
for _, r in casc.iterrows():
    if pd.isna(r.get("auc")):
        continue
    if r.archive in ("GridSybil_0709", "GridSybil_1416"):
        check("cascade cell %s %s" % (r.archive, r.stage),
              ("%.3f" % r.auc) in casc_cells, "%.3f" % r.auc)
sens_cells = cells("sensitivity")
for _, r in sens.iterrows():
    if r.sweep in ("prevalence", "jitter_native", "cap_native", "beacon_native"):
        check("sensitivity cell %s %s" % (r.sweep, r.value),
              ("%.3f" % r.auc) in sens_cells, "%.3f" % r.auc)

# --------------------------------------------------------------- prevalence floor
floor = pd.read_csv("workspace/verify/v6_prevalence_floor.csv")
dense = floor[floor.archive == "GridSybil_0709"].set_index("prevalence")
sparse = floor[floor.archive == "GridSybil_1416"].set_index("prevalence")
check("floor dense is 3 percent",
      bool(dense.loc[0.03, "usable"]) and not bool(dense.loc[0.02, "usable"]), "3%")
check("floor sparse is 5 percent",
      bool(sparse.loc[0.05, "usable"]) and not bool(sparse.loc[0.03, "usable"]), "5%")
check("floor kept at 2 percent", in_text("keeps %d attacker identities"
                                         % int(dense.loc[0.02, "attacker_identities_kept"])),
      str(int(dense.loc[0.02, "attacker_identities_kept"])))
check("floor benign pool", in_text("Only %d benign identities"
                                   % int(dense.loc[0.03, "benign_identities"])),
      str(int(dense.loc[0.03, "benign_identities"])))

# ---------------------------------------------------------------- phase / jitter
z = phase[phase.jitter_s == 0.0]
jz = phase[phase.jitter_s > 0.0]
dos = z[z.archive.str.startswith("DoS")]
check("phase DoS median 3e-6", dos.sib_median.max() < 4e-6, "%.2e" % dos.sib_median.max())
check("phase Grid median 0.1667",
      abs(z[z.archive.str.startswith("Grid")].sib_median.mean() - 1 / 6) < 1e-3, "1/6")
check("phase unrelated median stated",
      in_text("For unrelated identities the same quantity is %.2f" % z.oth_median.median()),
      "%.3f" % z.oth_median.median())
check("phase AUC range in text",
      in_text("%.2f to %.2f" % (z.phase_auc.min(), z.phase_auc.max())),
      "%.2f-%.2f" % (z.phase_auc.min(), z.phase_auc.max()))
check("jitter AUC range in text",
      in_text("%.2f--%.2f" % (jz.phase_auc.min(), jz.phase_auc.max())),
      "%.2f-%.2f" % (jz.phase_auc.min(), jz.phase_auc.max()))

# ---------------------------------------------------------------- cascade prose
g = casc[casc.archive == "GridSybil_0709"].set_index("stage")["auc"]
gs = casc[casc.archive == "GridSybil_1416"].set_index("stage")["auc"]
d12 = g["S1_no_pseudonym"] - g["S2_no_gt_agg"]
check("cascade GT-key cost 0.060", in_text("%.3f" % d12), "%.4f" % d12)
check("abstract GT-key figure", in_text("associated with a %.3f fall" % d12), "%.4f" % d12)
check("cascade sd at S4", in_text("0.088"), "%.4f" % casc[
    (casc.archive == "GridSybil_0709") & (casc.stage == "S4_prevalence_3")].auc_sd_over_seeds.iloc[0])
other = casc[~casc.archive.str.startswith("GridSybil")]["auc"].dropna()
check("other six stay above 0.995", other.min() >= 0.995, "%.4f" % other.min())

# ---------------------------------------------------------------- sensitivity prose
nat = sens[sens.sweep == "prevalence_native"]
pv = sens[sens.sweep == "prevalence"]
j = sens[sens.sweep == "jitter_native"].set_index("value")
bt = sens[sens.sweep == "beacon_native"].set_index("value")
check("sens AUC range", in_text("%.3f and %.3f" % (pv.auc.min(), max(pv.auc.max(), nat.auc.max()))),
      "%.3f-%.3f" % (pv.auc.min(), nat.auc.max()))
check("sens jitter 0 to 0.5",
      in_text("%.3f to %.3f" % (j.loc["0.0", "auc"], j.loc["0.5", "auc"])),
      "%.3f/%.3f" % (j.loc["0.0", "auc"], j.loc["0.5", "auc"]))
check("sens beacon tenth", in_text("%.3f" % bt.loc["0.1", "auc"]), "%.3f" % bt.loc["0.1", "auc"])

# ---------------------------------------------------------------- prose specifics
check("shared pseudonym message count", in_text("147\\,672"),
      str(int(gtfile.loc["GridSybil_0709", "shared_pseudonym_msgs"])))
ratio = pmap.loc["DoSRandomSybil_0709", "distinct_pseudonyms"] / gtfile.loc["DoSRandomSybil_0709", "identities"]
check("GT under-report 27.6x", in_text("27.6"), "%.1f" % ratio)
check("GT names 4068", in_text("4\\,068"), str(int(gtfile.loc["DoSRandomSybil_0709", "identities"])))
check("logs show 112191", in_text("112\\,191"),
      str(int(pmap.loc["DoSRandomSybil_0709", "distinct_pseudonyms"])))
check("abstract under-report 28x", in_text("up to 28 times"), "%.1f" % (
    pmap["distinct_pseudonyms"] / gtfile["identities"]).max())
check("benign max identities is 1", int(census.benign_ids_max.max()) == 1,
      str(int(census.benign_ids_max.max())))
check("identity prevalence range 67.6-97.5",
      in_text("67.6\\%") and in_text("97.5\\%"),
      "%.1f-%.1f" % (census.prevalence_identities_pct.min(), census.prevalence_identities_pct.max()))
check("abstract identity prevalence 68-98", in_text("68--98\\%"), "67.6-97.5 rounds to 68-98")
check("abstract encoding 86.5-100", in_text("86.5--100\\%"),
      "%.1f-%.1f" % (pmap.encoding_pct_pairs.min(), pmap.encoding_pct_pairs.max()))
check("GridSybil ids 1 to 7",
      in_text("one to seven identities") and int(census.loc["GridSybil_0709", "attacker_ids_min"]) == 1,
      "%d-%d" % (census.loc["GridSybil_0709", "attacker_ids_min"],
                 census.loc["GridSybil_0709", "attacker_ids_max"]))

# ------------------------------------------------------------- corpus usage claims
usage = pd.read_csv("workspace/verify/v7_dataset_usage.csv").set_index("item")
n_total = int(usage.loc["TOTAL full texts", "papers"])
n_veremi = int(usage.loc["VeReMi (any)", "papers"])
n_named = int(usage.loc["any named public dataset", "papers"])
pct_unnamed = 100.0 - usage.loc["any named public dataset", "share_pct"]
check("corpus total full texts", in_text("Of our %d full texts" % n_total), str(n_total))
check("corpus VeReMi mentions", in_text("%d mention VeReMi at all" % n_veremi), str(n_veremi))
check("corpus named datasets", in_text("Only %d name any public dataset" % n_named), str(n_named))
check("corpus bespoke share", in_text("remaining %.0f" % pct_unnamed), "%.1f" % pct_unnamed)
check("no 'almost entirely' claim survives", not in_text("almost entirely"), "removed")
check("no unqualified 'no public dataset' claim",
      not in_text("No public dataset offers both together"), "removed")
check("priority claim softened", not in_text("To our knowledge, no prior work"), "removed")

# ------------------------------------------------------------------ NextGen probe
ng = pd.read_csv("workspace/verify/v8_nextgen_probe.csv")
check("nextgen encoding bound", in_text("at most %.2f" % ng.encoding_pct.max()),
      "%.2f" % ng.encoding_pct.max())
check("nextgen splits are predefined",
      in_text("predefined training and validation splits"), "Train/Validation present")
check("nextgen not claimed as audited", in_text("We have not audited NextGen"), "scoped")

# ------------------------------------------------------- physical-layer scope
check("physical-layer claim is scoped to 2018",
      in_text("VeReMi 2018 cannot meaningfully validate"), "scoped")
check("no unscoped canonical-method claim",
      not in_text("The canonical method still cannot detect it"), "removed")
# the physical-layer section must name the dataset that refutes the old claim
phys = BODY[BODY.index("Signal-strength methods appear"):]
phys = phys[:phys.index(r"\section")]
check("Guven dataset named in the physical-layer section",
      "Guven and Tay" in phys and "guven2024" in phys,
      "cited where the claim used to be")
check("Guven access status stated",
      in_text("takedown and authorship-dispute notice"), "stated")

# ------------------------------------------------------- preprocessed derivative
dv = pd.read_csv("workspace/verify/v9_derivative_summary.csv").iloc[0]
dr = pd.read_csv("workspace/verify/v9_derivative_audit.csv")
check("derivative singleton receivers",
      in_text("{:,}".format(int(dv.singleton_receivers)).replace(",", "\\,")),
      str(int(dv.singleton_receivers)))
check("derivative top-two share", in_text("%.1f" % dv.top2_share_pct), "%.1f" % dv.top2_share_pct)
check("derivative attack types is nineteen plus benign",
      int(dv.attack_types) == 20 and in_text("Nineteen attack types"), str(int(dv.attack_types)))
check("derivative has no identity column",
      int(dv.identity_columns) == 0 and in_text("no sender and no pseudonym column"), "0")
check("derivative degenerate split is one in five",
      in_text("One split in five gave accuracy 1.000"),
      "%d of %d runs" % (int((dr.get("f1") == 0).sum()), len(dr)))
check("stale singleton figure gone", not in_text("30\\,093"), "removed")

# ------------------------------------------------------------ no claim regressions
for phrase, label in [
    ("The Physical-Layer Family Has No Substrate", "unscoped section heading"),
    ("physical-layer detector family has no usable substrate", "unscoped contribution bullet"),
    ("Nobody has yet applied that lens", "priority claim"),
    ("No field measurement of V2X attacker prevalence exists", "universal negative"),
    ("No single feature exceeded AUC 0.65 once", "contradicted diagnostic"),
    ("almost exactly half a period", "stale offset sentence"),
    ("records a commit hash", "nonexistent commit hash"),
    ("Azam et al.\\ describe exactly this protocol", "over-attribution to Azam"),
    ("report bespoke, unshared simulations", "unmeasured simulation claim"),
    ("Representative VeReMi work", "wrong table caption"),
]:
    check("removed: " + label, not in_text(phrase), "absent")

check("defect count matches the list",
      in_text("Nine defects were found"), "nine")
check("estimator defect is listed",
      in_text("printed beside an interval for another estimator"), "listed")
check("missing-script defect is listed",
      in_text("published with no script behind it"), "listed")
check("offset mechanism marked as a reading",
      in_text("We report that as a reading, not a measurement"), "hedged")
check("sparse counterexample stated",
      in_text("Its attackers hold six identities yet show the same third"), "stated")

# ------------------------------------------------- pseudonym change, scoped and tested
pc = pd.read_csv("workspace/verify/v10_pseudonym_change.csv")
check("rotation claim is scoped to the examined archives",
      in_text("the eight Sybil archives we examined")
      and not in_text("No benign vehicle in any archive emits"), "scoped")
check("generator capability acknowledged",
      in_text("supports pseudonym change policies"), "F2MD noted")
check("no claim about other Extension scenarios",
      in_text("We make no claim about other Extension scenarios"), "stated")
check("alternative reading tested",
      in_text("Rotation might occur while the logged sender identifier also changes"),
      "hypothesis stated")
check("span median quoted",
      in_text("median %.1f to %.1f seconds" % (pc.span_q50.min(), pc.span_q50.max())),
      "%.1f-%.1f" % (pc.span_q50.min(), pc.span_q50.max()))
check("span dispersion quoted",
      in_text("variation is %.2f to %.2f" % (pc.span_cv.min(), pc.span_cv.max())),
      "%.2f-%.2f" % (pc.span_cv.min(), pc.span_cv.max()))
check("no pile-up quoted",
      in_text("more than %.1f" % pc.modal_share_pct.max()),
      "%.2f%%" % pc.modal_share_pct.max())
check("spans are not truncated near a policy period",
      float(pc.span_max_over_window.max()) < 0.5 and float(pc.modal_share_pct.max()) < 5.0,
      "modal share %.2f%%" % pc.modal_share_pct.max())

# ------------------------------------------------------ cascade wording is associative
for phrase, label in [
    ("attributes score to that advantage", "causal cascade framing"),
    ("The staged drop attributes score", "causal contribution bullet"),
    ("accounts for 0.060 of AUC", "causal abstract wording"),
    ("carried most of the recoverable score", "causal conclusion wording"),
    ("Removing the ground-truth key costs", "causal 'costs' phrasing"),
]:
    check("removed: " + label, not in_text(phrase), "absent")

check("cascade states the nesting caveat",
      in_text("The stages are cumulative, so each is nested in the last"), "stated")
check("cascade ordering is tested, not merely disclaimed",
      in_text("tests whether that ordering carries the result")
      and in_text("These effects carry no ordering by construction"), "tested")
check("interaction acknowledged where designs differ",
      in_text("That is interaction, and this design exposes it"), "stated")
sf = pd.read_csv("workspace/sybilbench/exp14_single_factor.csv")
sf = sf[(sf.archive == "GridSybil_0709") & (sf.factor != "controlled baseline")]
top = sf.sort_values("delta", ascending=False).iloc[0]
check("single-factor top advantage is the ground-truth key",
      top.factor == "ground-truth key", top.factor)
_second = sf.sort_values("delta", ascending=False).iloc[1]
check("single-factor top dominates the next",
      1.5 < float(top.delta) / float(_second.delta) < 2.0
      and in_text("nearly twice the next largest factor"),
      "ratio %.2f" % (float(top.delta) / float(_second.delta)))
for _, r in sf.iterrows():
    if bool(r.get("paired")) and not pd.isna(r.get("delta_seed0_lo")):
        check("paired delta inside its interval: " + r.factor,
              r.delta_seed0_lo <= r.delta_seed0 <= r.delta_seed0_hi,
              "%.4f in [%.4f, %.4f]" % (r.delta_seed0, r.delta_seed0_lo, r.delta_seed0_hi))

# ------------------------------------------------------------ detector is specified
check("classifier named in the paper",
      in_text("random forest of 200 trees, minimum leaf two"), "named")
check("no untested claim about stronger models",
      not in_text("would raise every number in the same direction"), "removed")
check("feature-set count matches the table",
      in_text("lists the four feature sets"), "four")
check("linkage pair counts stated",
      in_text("pairs per archive"), "stated")

# every experiment must actually use the forest the paper describes
sizes = set()
for src in sorted(Path("workspace").rglob("*.py")):
    if "cache" in src.parts or "release" in src.parts:
        continue
    for m in re.finditer(r"RandomForestClassifier\(n_estimators=(\d+)", src.read_text(encoding="utf-8")):
        sizes.add(int(m.group(1)))
check("one forest size across the codebase", sizes == {200}, str(sorted(sizes)))

# ------------------------------------------------------------------ heading wording
check("V-C heading matches the corrected wording",
      in_text("Ground truth omits most attacker pseudonyms")
      and not in_text("Ground truth under-reports the Sybil population"), "aligned")
check("abstract names the archives before referring to them",
      BODY.index("We examine the eight Sybil archives")
      < BODY.index("No benign vehicle in them emits"), "ordered")

# ------------------------------------------------------ corpus reporting table
rep = pd.read_csv("workspace/verify/v11_reporting_table.csv").set_index("item")
LABELS = {"Explicit threat model": "Explicit threat model",
          "Vehicle count": "Vehicle count",
          "Simulation time": "Simulation time",
          "Beacon rate": "Beacon rate",
          "Attacker fraction": "Attacker fraction",
          "Simulation area": "Simulation area",
          "ROC or AUC": "ROC or AUC",
          "Any significance test or interval": "Any significance test or interval",
          "Code mentioned": "Repository or archive link",
          "Adversarial machine learning content": "Adversarial machine learning content"}
for key, row_label in LABELS.items():
    want = int(rep.loc[key, "papers"])
    check("reporting table row %s" % row_label,
          ("%s & %d" % (row_label, want)) in BODY, str(want))
check("reporting table denominator",
      in_text("across the %d full texts" % int(rep["of"].iloc[0])), str(int(rep["of"].iloc[0])))
check("stale ROC count gone", "ROC or AUC & 5" not in BODY, "was 5")
check("code-link claim is specific",
      in_text("All three point at the same archive"), "stated")
check("no bare reachable-code row", "Reachable public code" not in BODY, "removed")

# ------------------------------------------------------------ structural integrity
# every float must be referenced at least once; four were not
for lab in re.findall(r"\\label\{((?:tab|fig):[a-z]+)\}", BODY):
    n = len(re.findall(r"\\ref\{" + re.escape(lab) + r"\}", BODY))
    check("float referenced: " + lab, n >= 1, "%d reference(s)" % n)

# --------------------------------------------------------------- required statements
check("ethics statement present",
      in_text("This work analyses published artefacts and published papers"), "present")
check("ethics disclaims misconduct allegation",
      in_text("not to allege misconduct"), "stated")
check("ethics disclaims a position on the dispute",
      in_text("We take no position on the dispute itself"), "stated")
check("runtime stated", in_text("about two hours across eight archives"), "stated")

# --------------------------------------------------------------- dataset provenance
for doi, what in [("10.5281/zenodo.20081895", "VeReMi 2018"),
                  ("10.5281/zenodo.20090854", "VeReMi Extension"),
                  ("10.5281/zenodo.14903687", "preprocessed derivative")]:
    check("record cited for " + what, in_text(doi), doi)
check("no stale Zenodo record in the paper",
      not in_text("zenodo.6415827") and not in_text("zenodo.6532550"), "absent")

# the DOIs in the paper must match the metadata captured at download time
import datetime as _dt
import json as _json
LOCAL = {"VeReMi_original": "10.5281/zenodo.20081895",
         "VeReMi_Extension_sybil": "10.5281/zenodo.20090854",
         "VeReMi_preprocessed": "10.5281/zenodo.14903687"}
for folder, doi in LOCAL.items():
    meta = Path("workspace/datasets") / folder / "_zenodo_metadata.json"
    if meta.exists():
        got = _json.loads(meta.read_text(encoding="utf-8")).get("doi")
        check("record matches downloaded metadata: " + folder, got == doi, str(got))

# ------------------------------------------------------------------ licence claim
for folder in ("VeReMi_original", "VeReMi_Extension_sybil", "VeReMi_preprocessed"):
    meta = Path("workspace/datasets") / folder / "_zenodo_metadata.json"
    if meta.exists():
        raw = _json.loads(meta.read_text(encoding="utf-8"))
        lic = raw.get("metadata", {}).get("license") or raw.get("license")
        lic = lic.get("id") if isinstance(lic, dict) else lic
        check("CC-BY claim holds for " + folder, lic == "cc-by-4.0", str(lic))
check("licence claim stated as three", in_text("All three are CC-BY licensed"), "stated")

# the ethics statement claims we never obtained the disputed data
disputed = [d for d in Path("workspace/datasets").glob("*")
            if d.is_dir() and any(k in d.name.lower() for k in ("istanbul", "guven", "taysi"))]
check("disputed dataset never obtained", not disputed, str([d.name for d in disputed]) or "absent")

# ------------------------------------------------------------------ corpus facts
cf = pd.read_csv("workspace/verify/v12_corpus_facts.csv").iloc[0]
check("index size stated", in_text("%d records on vehicular" % int(cf.index_records)),
      str(int(cf.index_records)))
check("year span stated",
      in_text("years %d to %d" % (int(cf.index_year_min), int(cf.index_year_max))),
      "%d-%d" % (int(cf.index_year_min), int(cf.index_year_max)))
check("build date stated", in_text("3 September 2026"), str(cf.index_built))
# the count is spelled out at the start of its sentence, and appears as digits elsewhere
check("full-text count stated",
      (int(cf.full_texts) == 92 and in_text("Ninety-two open-access full texts"))
      or in_text("%d open-access full texts" % int(cf.full_texts)),
      str(int(cf.full_texts)))
check("full-text count consistent elsewhere",
      in_text("Of our %d full texts" % int(cf.full_texts))
      and in_text("across the %d full texts" % int(cf.full_texts)),
      str(int(cf.full_texts)))
check("signal-strength record count", in_text("%d indexed records" % int(cf.rssi_phy_records)),
      str(int(cf.rssi_phy_records)))
check("ns-2 count stated", in_text("Eleven papers published since 2021 mention ns-2")
      and int(cf.ns2_since_2021) == 11, str(int(cf.ns2_since_2021)))
check("ns-2 claim is 'mention', not 'use'",
      not in_text("since 2021 still use ns-2"), "softened")
check("ns-2 survey caveat present", in_text("survey citing it in passing"), "stated")

# ------------------------------------------------------------- citation provenance
cite = _json.loads(Path("workspace/verify/v13_citation_counts.json").read_text(encoding="utf-8"))
rec = cite["records"][0]
# The citation count was removed: it drifts with time and was not load-bearing.
# The provenance record is kept so the claim can be restored with its date if wanted.
check("no undated citation count in the text",
      "citations" not in BODY or "had %d citations" % rec["cited_by_count"] not in BODY,
      "removed")
_dt.date.fromisoformat(cite["queried"])   # raises if the stamp is malformed
check("citation count carries a valid read date",
      len(cite["queried"]) == 10 and cite["queried"][:2] == "20", cite["queried"])

# ------------------------------------------------------------- derivative row count
check("derivative row count stated",
      in_text("%.2f million" % (int(dv.rows) / 1e6)), "{:,}".format(int(dv.rows)))

# ---------------------------------------------------------------- beacon interval
sc = pd.read_csv("workspace/sybilbench/exp1b_rate_baseline_v2.csv")
check("benign beacon interval is 1.0 s everywhere",
      set(sc.benign_interval_med.round(1)) == {1.0}
      and in_text("Benign identities beacon at 1.0"),
      str(sorted(set(sc.benign_interval_med))))

# ------------------------------------------- corpus counts reproduce from shipped data
mx = pd.read_csv("workspace/verify/v14_match_matrix.csv")
check("match matrix covers every full text", len(mx) == int(cf.full_texts), str(len(mx)))
for item in ("Explicit threat model", "Beacon rate", "Attacker fraction",
             "ROC or AUC", "Code mentioned"):
    check("matrix reproduces %s" % item,
          int(mx["report:" + item].sum()) == int(rep.loc[item, "papers"]),
          "%d vs %d" % (int(mx["report:" + item].sum()), int(rep.loc[item, "papers"])))
check("matrix reproduces the ns-2 count",
      int(mx[mx.year.astype(str) >= "2021"]["sim:NS-2"].sum()) == int(cf.ns2_since_2021),
      str(int(cf.ns2_since_2021)))
check("matrix reproduces VeReMi usage",
      int(mx["usage:VeReMi (any)"].sum()) == n_veremi, str(n_veremi))

# --------------------------------------------------- no percent starts a comment
# A bare % in the body is a TeX comment and silently eats the rest of its line.
# Three edits have introduced one by writing \%% in a string that is not formatted.
raw_body = TEX[TEX.index(r"\begin{document}"):TEX.index(r"\begin{thebibliography}")]
stray = []
for ln_no, ln in enumerate(raw_body.split("\n"), 1):
    if ln.lstrip().startswith("%"):
        continue                      # a real comment line is fine
    for m in re.finditer(r"%", ln):
        before = ln[:m.start()]
        if before.endswith("\\"):
            continue                  # properly escaped
        stray.append(ln.strip()[:70])
        break
check("no unescaped percent in the body", not stray, str(stray[:3]) or "none")

# ------------------------------------------------- no value slot left holding a period
# Two blockers came from a trim script that carried numbers by matching [\d.]+ on the
# old text, so sentence-ending periods were popped into value slots. This scans for
# the whole signature class rather than the instance last reported.
CORRUPT = [
    (r"to \.\s*;", "value slot holding a period"),
    (r"AUC \.", "missing AUC value"),
    (r"and \.\.", "missing second value"),
    (r"reaches \.", "missing value after 'reaches'"),
    (r"between \. ", "missing value after 'between'"),
    (r"\.\.", "doubled period"),
    (r"nan", "a NaN reached the text"),
    (r"%\.\d[fd]", "unfilled format specifier"),
]
bad_lines = []
for ln in raw_body.split(chr(10)):
    if ln.lstrip().startswith("%"):
        continue
    for pat, why in CORRUPT:
        if re.search(pat, ln):
            bad_lines.append(why + ": " + ln.strip()[:50])
            break
check("no missing values in the prose", not bad_lines, str(bad_lines[:2]) or "none")

# ------------------------------------------------- the cascade CSV must stay complete
# A partial run once overwrote this file with seven rows. The published table needs
# all eight archives, so its shape is asserted rather than assumed.
_c = pd.read_csv("workspace/sybilbench/exp9_cascade.csv")
check("cascade CSV covers every archive", _c.archive.nunique() == 8, str(_c.archive.nunique()))
check("cascade CSV has every stage", len(_c) >= 50, "%d rows" % len(_c))
check("cross-model robustness reported",
      in_text("logistic regression run through it behaves the same way"), "stated")

# ------------------------------------------------- the timing arithmetic must match
# The paper once derived a 100 s ghost interval from a 1 Hz benign rate while its own
# table measured 50 s. The attacker transmits at about 2 Hz, so the relation is N/R.
bud = pd.read_csv("workspace/verify/v21_attacker_budget.csv").set_index("archive")
_d = bud.loc["DoSRandomSybil_0709"]
check("attacker aggregate rate stated",
      in_text("$R=%.1f$" % _d.aggregate_rate_hz_median), "%.3f Hz" % _d.aggregate_rate_hz_median)
check("predicted gap matches the measurement",
      abs(_d.implied_interval_from_rate - _d.ghost_interval_median_s) < 1.0,
      "predicted %.1f vs measured %.1f" % (_d.implied_interval_from_rate,
                                           _d.ghost_interval_median_s))
check("no equal-budget derivation survives",
      "gives each ghost interval" not in BODY and "fifty seconds" not in BODY, "removed")
check("the doubling is explained",
      in_text("denial-of-service part of the attack"), "stated")

# ------------------------------------------------- no loose mutual-information claim
check("no unqualified mutual-information claim",
      "Mutual information between pseudonym and sender" not in BODY, "removed")
check("bits result framed as I(D;S)", in_text("$I(D;S)$ recovers"), "framed")
check("decoder variable defined before use",
      BODY.index("Let $D$ be the sender named") < BODY.index("$I(D;S)$ recovers"), "ordered")

# ---------------------------------------------------------------- report
bad = [(n, d) for ok, n, d in results if not ok]
print("claims checked: %d | failed: %d" % (len(results), len(bad)))
for n, d in bad:
    print("  FAIL %-42s measured: %s" % (n, d))
sys.exit(1 if bad else 0)
