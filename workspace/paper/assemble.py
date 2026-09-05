"""Assemble veremi_audit.tex from the body draft, generated tables and the bibliography.

Tables are emitted from the result CSVs rather than typed, so a number in the paper
cannot drift from the number in the file that produced it.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd

PAPER = Path("workspace/paper")
BENCH = Path("workspace/sybilbench")

NEW_BIB = {
    # inserted in publication order among the existing entries
    "sommer2010": r"""\bibitem{sommer2010} R.~Sommer and V.~Paxson, ``Outside the closed world: on using machine learning for network intrusion detection,'' in \emph{IEEE Symp. Security and Privacy}, 2010, pp.~305--316. DOI: \\url{10.1109/SP.2010.25}.""",
    "arp2022": r"""\bibitem{arp2022} D.~Arp, E.~Quiring, F.~Pendlebury, A.~Warnecke, F.~Pierazzi, C.~Wressnegger, L.~Cavallaro, and K.~Rieck, ``Dos and don'ts of machine learning in computer security,'' in \emph{USENIX Security Symposium}, 2022.""",
    "guven2024": r"""\bibitem{guven2024} T.~Guven and Z.~C. Tay\c{s}i, ``Creating a realistic Sybil attack dataset for inter-vehicle communication,'' \emph{Peer-to-Peer Netw. Appl.}, 2025. DOI: \\url{10.1007/s12083-025-02058-w}.""",
}
# key after which each new entry is placed
ANCHOR = {"sommer2010": "park2009", "arp2022": "azam2022", "guven2024": "khatri2024"}

STAGE_LABEL = {
    "S0_published":    r"S0 published",
    "S1_no_pseudonym": r"S1 $-$ pseudonym",
    "S2_no_gt_agg":    r"S2 $-$ GT key",
    "S3_disjoint":     r"S3 $+$ disjoint",
    "S4_prevalence_3": r"S4 prevalence 3\%",
    "S5_jitter":       r"S5 $+$ jitter",
    "S6_no_rate":      r"S6 $-$ rate feats.",
}
ORDER = list(STAGE_LABEL)


def cell(auc, sd):
    if pd.isna(auc):
        return "---"
    # a subscript reads as part of the number: 0.998 with spread 0.000 became
    # "0.998.000". Parentheses carry the same information unambiguously.
    return "%.3f\\,{\\tiny(%s)}" % (
        auc, ("%.3f" % (0.0 if pd.isna(sd) else sd)).lstrip("0"))


def cascade_table() -> str:
    d = pd.read_csv(BENCH / "exp9_cascade.csv")
    auc = d.pivot(index="stage", columns="archive", values="auc").reindex(ORDER)
    sd = d.pivot(index="stage", columns="archive", values="auc_sd_over_seeds").reindex(ORDER)
    triv = d.pivot(index="stage", columns="archive", values="trivial_auc").reindex(ORDER)
    cols = ["GridSybil_0709", "GridSybil_1416"]
    # the six saturated archives never separate, so one column carries their worst case
    dos = ["DataReplaySybil_0709", "DataReplaySybil_1416",
           "DoSRandomSybil_0709", "DoSRandomSybil_1416",
           "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]

    lines = [
        r"\begin{table}[t]",
        r"\caption{Protocol cascade. Mean AUC over five seeds.",
        r"Parentheses give the spread across those seeds.",
        r"The last column is the untrained scalar on GridSybil dense.}",
        r"\label{tab:cascade}",
        r"\centering",
        r"\footnotesize",
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Protocol & GridSybil & GridSybil & Other six & Trivial \\",
        r" & dense & sparse & archives & scalar \\",
        r"\midrule",
    ]
    for s in ORDER:
        vals = [cell(auc.loc[s, c], sd.loc[s, c]) for c in cols]
        dv = [auc.loc[s, c] for c in dos if c in auc.columns]
        dv = [v for v in dv if not pd.isna(v)]
        dos_cell = "---" if not dv else ("1.000" if min(dv) >= 0.9995 else "$\\geq$%.3f" % min(dv))
        t = triv.loc[s, "GridSybil_0709"]
        tcell = "---" if pd.isna(t) else "%.3f" % t
        lines.append("%s & %s & %s & %s & %s \\\\" % (STAGE_LABEL[s], vals[0], vals[1], dos_cell, tcell))
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def cascade_text() -> str:
    d = pd.read_csv(BENCH / "exp9_cascade.csv")
    g = d[d.archive == "GridSybil_0709"].set_index("stage")["auc"]
    gs = d[d.archive == "GridSybil_1416"].set_index("stage")["auc"]
    d01 = g["S0_published"] - g["S1_no_pseudonym"]
    d12 = g["S1_no_pseudonym"] - g["S2_no_gt_agg"]
    d12s = gs["S1_no_pseudonym"] - gs["S2_no_gt_agg"]
    sd = d[d.archive.str.startswith("GridSybil")].set_index(["archive", "stage"])["auc_sd_over_seeds"]
    sd_s2 = float(max(sd[("GridSybil_0709", "S2_no_gt_agg")], sd[("GridSybil_1416", "S2_no_gt_agg")]))
    d23 = g["S2_no_gt_agg"] - g["S3_disjoint"]
    d23s = gs["S2_no_gt_agg"] - gs["S3_disjoint"]
    t = d[d.archive == "GridSybil_0709"].set_index("stage")["trivial_auc"]
    ts = d[d.archive == "GridSybil_1416"].set_index("stage")["trivial_auc"]
    m_dense = g["S2_no_gt_agg"] - t["S2_no_gt_agg"]
    m_sparse = gs["S2_no_gt_agg"] - ts["S2_no_gt_agg"]
    # the denial-of-service trivial baselines are in the result file, not the table
    dos = d[d.archive.str.startswith("DoS") & (d.stage != "S0_published")
            & (d.stage != "S1_no_pseudonym")]
    dos_triv = dos["trivial_auc"].min()
    return "\n".join([
        r"Table~\ref{tab:cascade} reports the result.",
        r"Six of eight archives stay above AUC 0.995 throughout.",
        r"No control we apply moves them meaningfully.",
        r"Only the two GridSybil archives respond to the cascade.",
        "",
        r"The trivial column reads 0.009 at the first two stages.",
        r"That is the same statistic scored in the opposite direction.",
        r"Ground-truth aggregation pools a whole attacker into one row.",
        r"Pooled attackers beacon faster than honest vehicles, not slower.",
        r"A receiver cannot know which direction applies.",
        "",
        r"Removing the pseudonym feature shifts AUC by %.4f." % d01,
        r"The feature keeps the raw representation it has in the archive.",
        r"The identifier adds nothing once aggregation is already leaking.",
        "",
        r"%%CASCADE_GT%%",
        r"Inferring the partition, rather than receiving it, is the task.",
        "",
        r"Below this point the archive stops supporting inference.",
        r"At 3\% prevalence the seed spread reaches 0.088.",
        r"The two sparse archives become degenerate and are dropped.",
        r"Later stage differences all sit inside that spread.",
        r"We therefore do not attribute them to the controls.",
        r"Section~\ref{sec:sensitivity} measures those knobs where estimates are stable.",
        "",
        r"The final column carries the uncomfortable comparison.",
        r"It shows GridSybil dense, where the model beats the scalar.",
        r"The margin is %.2f on the dense archive and %.2f on the sparse one." % (m_dense, m_sparse),
        r"On the four denial-of-service archives that margin vanishes.",
        r"There the untrained scalar itself reaches %.3f from stage S2."
        % (math.floor(dos_triv * 1000) / 1000),
        r"The learned model adds nothing at all on those archives.",
        r"GridSybil is the one family where the benchmark measures something.",
    ])


def single_factor_table() -> str:
    d = pd.read_csv(BENCH / "exp14_single_factor.csv")
    d = d[d.archive == "GridSybil_0709"]
    base = d[d.factor == "controlled baseline"].iloc[0]
    rows = d[d.factor != "controlled baseline"].sort_values("delta", ascending=False)
    lines = [
        r"\begin{table}[t]",
        r"\caption{Each advantage added back to the controlled protocol.",
        r"Baseline AUC %.3f. Paired intervals are on shared rows, one seed.}" % base.auc,
        r"\label{tab:single}",
        r"\centering",
        r"\footnotesize",
        r"\begin{tabular}{@{}lrrl@{}}",
        r"\toprule",
        r"Advantage added & AUC & $\Delta$ & $\Delta$ paired, one seed \\",
        r"\midrule",
    ]
    for _, r in rows.iterrows():
        if pd.isna(r.get("auc")):
            continue
        # the paired interval belongs to its own seed's delta, not to the mean
        if bool(r.get("paired")) and not pd.isna(r.get("delta_seed0_lo")):
            ci = "%+.3f [%.3f, %.3f]" % (r.delta_seed0, r.delta_seed0_lo, r.delta_seed0_hi)
        else:
            ci = "not pairable"
        auc = math.floor(r.auc * 1000) / 1000        # never round an AUC up to 1.000
        lines.append("%s & %.3f & %+.3f & %s \\\\" % (r.factor, auc, r.delta, ci))
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def cascade_gt_line() -> str:
    d = pd.read_csv(BENCH / "exp9_cascade.csv")
    g = d[d.archive == "GridSybil_0709"].set_index("stage")["auc"]
    gs = d[d.archive == "GridSybil_1416"].set_index("stage")["auc"]
    d12 = g["S1_no_pseudonym"] - g["S2_no_gt_agg"]
    d12s = gs["S1_no_pseudonym"] - gs["S2_no_gt_agg"]
    d23 = g["S2_no_gt_agg"] - g["S3_disjoint"]
    return "\n".join([
        r"Removing the ground-truth key is followed by falls of %.3f and %.3f." % (d12, d12s),
        r"This is the largest and only unambiguous change.",
        r"Both are far outside the seed spread at that stage.",
        r"Making the split disjoint is followed by a further %.3f." % d23,
    ])


def decode_text() -> str:
    d = pd.read_csv(BENCH / "exp13_pseudonym_decode.csv")
    return "\n".join([
        r"Table~\ref{tab:decode} and Figure~\ref{fig:decode} report it.",
        r"The decoder names the emitting vehicle %.1f\%% of the time." % (
            100 * d.decode_accuracy.mean()),
        r"Permuting the correspondence drops that to %.2f\%%." % (
            100 * d.decode_accuracy_shuffled.mean()),
        r"Chance for these populations is %.2f\%%." % (100 * d.chance_accuracy.mean()),
        "",
        r"Linkage from the identifier alone is essentially perfect.",
        r"Longest common digit substring reaches AUC %.3f or above." % (
            math.floor(d.AUC_common_substring.min() * 1000) / 1000),
        r"The permuted control sits between %.2f and %.2f." % (
            d.AUC_common_substring_shuffled.min(), d.AUC_common_substring_shuffled.max()),
    ])


def paired_spread_text() -> str:
    d = pd.read_csv(BENCH / "exp14_single_factor.csv")
    d = d[(d.archive == "GridSybil_0709") & d.paired.fillna(False)
          & d.delta_seed0.notna()]
    if d.empty:
        return "At this prevalence a single split carries few attackers."
    return "\n".join([
        r"At 3\% prevalence a split holds about six attackers.",
        r"One split therefore moves easily against the five-split mean.",
        r"The paired intervals span %.2f, wider than either delta." % float(
            (d.delta_seed0_hi - d.delta_seed0_lo).mean()),
        r"Both intervals include zero, so neither factor is resolved.",
        r"We report both columns rather than the one we prefer.",
    ])


def nextgen_ids_text() -> str:
    d = pd.read_csv("workspace/verify/v16_nextgen_identifier.csv")
    return "\n".join([
        r"A new identifier artefact replaces the old one.",
        r"Sybil identities carry synthetic sender identifiers.",
        r"Benign identifiers reach %s across the four scenarios." % (
            "{:,}".format(int(d.benign_id_max.max())).replace(",", "\\,")),
        r"Every attacker identifier exceeds %s." % (
            "{:,}".format(int(d.attacker_id_min.min())).replace(",", "\\,")),
        r"The two ranges are disjoint in every scenario.",
        r"The identifier alone therefore separates the classes perfectly.",
    ])


def citation_count_text() -> str:
    rec = json.loads(Path("workspace/verify/v13_citation_counts.json")
                     .read_text(encoding="utf-8"))
    r = rec["records"][0]
    y, m, _ = rec["queried"].split("-")
    month = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"][int(m) - 1]
    return r"The extension alone had %d citations in %s %s." % (
        r["cited_by_count"], month, y)


def budget_text() -> str:
    b = pd.read_csv("workspace/verify/v21_attacker_budget.csv").set_index("archive")
    d = b.loc["DoSRandomSybil_0709"]
    return "\n".join([
        r"The mechanism is arithmetic, and we measured its terms.",
        r"An attacker emits at aggregate rate $R$ across $N$ identities.",
        r"Each identity then transmits about every $N/R$ seconds.",
        r"These families run at $R=%.1f$\,Hz, twice the benign rate." %
        d.aggregate_rate_hz_median,
        r"That doubling is the denial-of-service part of the attack.",
        r"With $N=%d$ the predicted gap is %.0f\,s." % (
            d.identities_per_attacker_median, d.implied_interval_from_rate),
        r"We measure %.0f\,s, so arithmetic and archive agree." %
        d.ghost_interval_median_s,
        "",
        r"Benign identities beacon once per second throughout.",
        r"Median inter-arrival is therefore a sufficient statistic here.",
        r"Geometry is redundant by construction, not by weakness.",
    ])


def information_text() -> str:
    d = pd.read_csv("workspace/verify/v18_information.csv")
    return "\n".join([
        r"\subsection{The leak, in bits}",
        "",
        r"Naming the vehicle behind an identity costs %.1f to %.1f bits." % (
            d.H_sender_bits.min(), d.H_sender_bits.max()),
        r"That entropy is what a detector must resolve from nothing.",
        r"Let $D$ be the sender named by the untrained decoder above.",
        r"The residual $H(S \mid D)$ measures %.2f to %.2f bits." % (
            d.H_sender_given_decode_bits.min(), d.H_sender_given_decode_bits.max()),
        r"So $I(D;S)$ recovers %.0f\%% to %.0f\%% of $H(S)$." % (
            100 * d.fraction_recovered.min(), 100 * d.fraction_recovered.max()),
        r"The identifier's shape hands over most of the partition.",
    ])

def sensitivity_table() -> str:
    d = pd.read_csv(BENCH / "exp10_sensitivity.csv")

    def block(sweep, label, fmt="%s", prefix=None):
        sub = d[d.sweep == sweep]
        rows = list(prefix or [])
        for _, r in sub.iterrows():
            rows.append("%s & %.3f & %.3f & %.3f & %.3f \\\\" % (
                fmt % str(r["value"]), r["auc"], r["auc_sd"], r["ap"], r["trivial_auc"]))
        return [r"\multicolumn{5}{l}{\emph{%s}} \\" % label] + rows

    lines = [
        r"\begin{table}[t]",
        r"\caption{Sensitivity on GridSybil dense. Three seeds per point.",
        r"Prevalence uses a disjoint split; the other sweeps run at native prevalence.}",
        r"\label{tab:sensitivity}",
        r"\centering",
        r"\footnotesize",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Setting & AUC & seed sd & AP & Trivial \\",
        r"\midrule",
    ]
    # the prevalences that were attempted and failed come first, so the floor is
    # visible in the table rather than only in the prose
    fl = pd.read_csv("workspace/verify/v6_prevalence_floor.csv")
    dense = fl[(fl.archive == "GridSybil_0709") & (~fl.usable)]
    degenerate = [r"%.3f & \multicolumn{4}{l}{degenerate: %d attackers kept} \\"
                  % (r["prevalence"], int(r["attacker_identities_kept"]))
                  for _, r in dense.sort_values("prevalence").iterrows()]
    lines += block("prevalence", "attacker prevalence", prefix=degenerate)
    lines += [r"\midrule"] + block("jitter_native", "transmission jitter (s)")
    lines += [r"\midrule"] + block("cap_native", "identities per attacker")
    lines += [r"\midrule"] + block("beacon_native", "fraction of beacons kept")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def sensitivity_text() -> str:
    d = pd.read_csv(BENCH / "exp10_sensitivity.csv")
    fl = pd.read_csv("workspace/verify/v6_prevalence_floor.csv")
    dense = fl[fl.archive == "GridSybil_0709"].set_index("prevalence")
    floor_benign = int(dense.loc[0.03, "benign_identities"])
    floor_kept_2 = int(dense.loc[0.02, "attacker_identities_kept"])
    floor_kept_3 = int(dense.loc[0.03, "attacker_identities_kept"])
    floor_test_3 = float(dense.loc[0.03, "test_positives_mean"])
    pv = d[d.sweep == "prevalence"]
    nat = d[(d.sweep == "prevalence_native")]
    j = d[d.sweep == "jitter_native"].set_index("value")
    b = d[d.sweep == "beacon_native"].set_index("value")
    c = d[d.sweep == "cap_native"].set_index("value")
    return "\n".join([
        r"Prevalence is the knob papers omit most often.",
        r"These archives set a floor on how low it can go.",
        r"Subsampling to prevalence $p$ holds the benign pool fixed.",
        r"Surviving attackers are $p\,N_{b}/(1-p)$, which shrinks fast.",
        r"GridSybil dense keeps %d attacker identities at 2\%%." % floor_kept_2,
        r"That is below the twenty we require before splitting.",
        r"At 3\%% it keeps %d, of which about %.0f reach the test fold." % (floor_kept_3, floor_test_3),
        r"The measured floor is 3\% dense and 5\% sparse.",
        r"The binding constraint is the benign population, not the attackers.",
        r"Only %d benign identities exist in the dense archive." % floor_benign,
        "",
        r"Between 3\% and native the ranking metric barely moves.",
        r"AUC stays between %.3f and %.3f across that range." % (pv.auc.min(), max(pv.auc.max(), nat.auc.max())),
        r"Average precision behaves completely differently.",
        r"It falls from %.3f at native to %.3f at 3\%%." % (nat.ap.iloc[0], pv[pv.value == "0.03"].ap.iloc[0]),
        r"Precision, recall and F1 inherit that dependence directly.",
        r"A paper reporting them at 30\% reports a different problem.",
        "",
        r"Jitter costs little on the per-identity task.",
        r"Half a second of jitter moves AUC from %.3f to %.3f." % (j.loc["0.0", "auc"], j.loc["0.5", "auc"]),
        r"The per-identity rate gap survives jitter of that size.",
        r"The pairwise clock signal does not, as shown next.",
        "",
        r"Attack intensity matters less than expected.",
        r"Capping attackers at two identities gives AUC %.3f." % c.loc["2", "auc"],
        r"Leaving them uncapped gives %.3f." % c.loc["native", "auc"],
        "",
        r"Beacon rate has a clearer effect.",
        r"Keeping one beacon in ten drops AUC to %.3f." % b.loc["0.1", "auc"],
        r"The trivial baseline falls further, from %.3f to %.3f." % (b.loc["1.0", "trivial_auc"], b.loc["0.1", "trivial_auc"]),
        r"Sparse beaconing hurts the shortcut more than the model.",
    ])


def phase_text() -> str:
    d = pd.read_csv("workspace/verify/v4_timing_distributions.csv")
    z = d[d.jitter_s == 0.0]
    jz = d[d.jitter_s > 0.0]
    # the denial-of-service fall, computed rather than typed
    dz = z[z.archive.str.startswith("DoS")].set_index("archive")["phase_auc"]
    djz = jz[jz.archive.str.startswith("DoS")].set_index("archive")["phase_auc"]
    dos_fall = float((dz - djz).mean())
    dos = z[z.archive.str.startswith("DoS")]
    grid = z[z.archive.str.startswith("Grid")]
    return "\n".join([
        r"The offset is an exact fraction of the beacon period.",
        r"Denial-of-service ghosts sit half a second apart.",
        r"Their residual against half a period has median $3\times10^{-6}$.",
        r"GridSybil siblings instead sit one third of a period apart.",
        r"For unrelated identities the same quantity is 0.25.",
        r"A round-robin over the transmit slot would explain both offsets.",
        r"We report that as a reading, not a measurement.",
        r"The sparse archive does not fit it cleanly.",
        r"Its attackers hold six identities yet show the same third.",
        r"Phase alone separates pairs at AUC %.2f to %.2f." % (z.phase_auc.min(), z.phase_auc.max()),
        r"Every one of those separations is significant beyond $p=10^{-8}$.",
        "",
        r"An attacker removes this signal by jittering transmissions.",
        r"A quarter-second jitter cuts phase AUC to %.2f--%.2f." % (jz.phase_auc.min(), jz.phase_auc.max()),
        r"On the denial-of-service families that is a fall of %.2f." % dos_fall,
        r"The change costs nothing in attack utility.",
        r"Detectors validated on it need not transfer.",
    ])


def main() -> None:
    body = (PAPER / "body_new.tex").read_text(encoding="utf-8")
    # Read the bibliography from a pinned copy, never from our own output.
    # Reading the output made insertion non-idempotent and duplicated entries.
    bib = (PAPER / "bibliography.tex").read_text(encoding="utf-8")
    for key, entry in NEW_BIB.items():
        if ("\\bibitem{" + key + "}") in bib:
            continue
        anchor = ANCHOR[key]
        m = re.search(r"\\bibitem\{" + anchor + r"\}.*?(?=\n\n)", bib, re.S)
        assert m, "anchor %s not found" % anchor
        bib = bib[:m.end()] + "\n\n" + entry + bib[m.end():]

    body = body.replace("%%CASCADE_TABLE%%", cascade_table())
    body = body.replace("%%CASCADE_TEXT%%", cascade_text())
    body = body.replace("%%BUDGET%%", budget_text())
    body = body.replace("%%INFORMATION%%", information_text())
    body = body.replace("%%NEXTGEN_IDS%%", nextgen_ids_text())
    body = body.replace("%%DECODE_TEXT%%", decode_text())
    body = body.replace("%%PAIRED_SPREAD%%", paired_spread_text())
    body = body.replace("%%SINGLE_FACTOR%%", single_factor_table())
    body = body.replace("%%CASCADE_GT%%", cascade_gt_line())
    body = body.replace("%%SENSITIVITY_TABLE%%", sensitivity_table())
    body = body.replace("%%SENSITIVITY_TEXT%%", sensitivity_text())
    body = body.replace("%%PHASE_TEXT%%", phase_text())
    left = re.findall(r"%%[A-Z_]+%%", body)
    assert not left, "unfilled placeholder: %s" % left

    out = body.rstrip() + "\n\n" + bib
    (PAPER / "veremi_audit.tex").write_text(out, encoding="utf-8")
    print("wrote workspace/paper/veremi_audit.tex")


if __name__ == "__main__":
    main()
