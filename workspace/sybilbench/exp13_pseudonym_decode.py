"""Experiment 13 - how much of the sender does the pseudonym give away?

Section V-A shows the pseudonym contains the sender's digits. That is a statement
about string structure. This turns it into a decoder and measures what an adversary,
or a careless pipeline, actually recovers.

Two measurements, each against a control.

  DECODE. Given only a pseudonym, name the vehicle that emitted it. The decoder is
  deliberately trivial: find the sender identifiers whose digits appear inside the
  pseudonym, and take the longest. No training, no data beyond the identifier.

  LINK. Given two pseudonyms, decide whether one vehicle emitted both. Features are
  pseudonym-only: absolute numeric difference and longest common digit substring.

The control shuffles which pseudonym belongs to which vehicle, preserving both
populations exactly and destroying only the correspondence. A decoder that works on
real pseudonyms and collapses on shuffled ones has measured the leak, not the task.
"""
from __future__ import annotations

import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
from sybilbench import loader  # noqa: E402
from v2_metrics import bootstrap_ci, rank_auc  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]
MAX_PAIRS = 20_000
SEED = 0


def decode(pseudo: int, senders_by_len: list[tuple[str, int]]) -> int | None:
    """Longest sender identifier whose digits appear in the pseudonym."""
    p = str(pseudo)
    for s_str, s in senders_by_len:          # longest first
        if s_str in p:
            return s
    return None


def lcs_len(a: str, b: str) -> int:
    m = SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
    return m.size


def run(archive: str, rng: np.random.Generator) -> dict:
    with open(Path("workspace/sybilbench/cache") / f"{archive}.pseudomap.json",
              encoding="utf-8") as f:
        tok_pseudo = {k: int(v) for k, v in json.load(f)["token_to_pseudo"].items()}
    _view, truth = loader.load_cache(archive)

    toks = [t for t in tok_pseudo if t in truth.token_to_sender]
    pseudo = np.array([tok_pseudo[t] for t in toks])
    sender = np.array([truth.token_to_sender[t] for t in toks])

    senders = sorted(set(int(s) for s in sender))
    by_len = sorted(((str(s), s) for s in senders), key=lambda kv: -len(kv[0]))

    def decode_rate(pseudo_arr, sender_arr) -> tuple[float, float]:
        hit = miss = amb = 0
        for p, s in zip(pseudo_arr, sender_arr):
            got = decode(p, by_len)
            if got is None:
                amb += 1
            elif got == s:
                hit += 1
            else:
                miss += 1

        n = len(pseudo_arr)
        return hit / n, amb / n

    # control: same pseudonyms, same vehicles, correspondence destroyed
    shuffled = sender.copy()
    rng.shuffle(shuffled)

    real_acc, real_none = decode_rate(pseudo, sender)
    ctrl_acc, _ = decode_rate(pseudo, shuffled)

    # pairwise linkage from the identifier alone
    idx = rng.choice(len(toks), size=min(MAX_PAIRS * 2, len(toks) * 2 - 2), replace=True)
    a_i, b_i = idx[0::2], idx[1::2]
    keep = a_i != b_i
    a_i, b_i = a_i[keep], b_i[keep]
    ps_a, ps_b = pseudo[a_i], pseudo[b_i]
    y = (sender[a_i] == sender[b_i]).astype(int)

    diff = -np.abs(ps_a.astype(float) - ps_b.astype(float))
    lcs = np.array([lcs_len(str(x), str(z)) for x, z in zip(ps_a, ps_b)], dtype=float)

    # Control for the linkage arm. Permuting vehicles leaves the pseudonyms attached
    # to each other, so sibling pseudonyms still resemble one another and the null is
    # not null: it reached 0.82 on GridSybil. Permuting the pseudonyms instead keeps
    # both populations and the true partition, and breaks only the correspondence.
    perm = rng.permutation(len(pseudo))
    ps_a_c, ps_b_c = pseudo[perm][a_i], pseudo[perm][b_i]
    lcs_ctrl = np.array([lcs_len(str(x), str(z)) for x, z in zip(ps_a_c, ps_b_c)],
                        dtype=float)

    out = {
        "archive": archive,
        "identities": len(toks),
        "vehicles": len(senders),
        "decode_accuracy": round(real_acc, 4),
        "decode_accuracy_shuffled": round(ctrl_acc, 4),
        "decode_undecodable": round(real_none, 4),
        "chance_accuracy": round(1.0 / len(senders), 6),
        "pairs": int(len(y)),
        "positive_rate": round(float(y.mean()), 4),
    }
    if 0 < y.sum() < len(y):
        out["AUC_numeric_distance"] = round(rank_auc(y, diff), 4)
        out["AUC_common_substring"] = round(rank_auc(y, lcs), 4)
        lo, hi = bootstrap_ci(y, lcs, n_boot=1000, seed=3)
        out["AUC_common_substring_lo"] = round(lo, 4)
        out["AUC_common_substring_hi"] = round(hi, 4)
    if 0 < y.sum() < len(y):
        out["AUC_common_substring_shuffled"] = round(rank_auc(y, lcs_ctrl), 4)
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    rows = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        r = run(a, rng)
        rows.append(r)
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/sybilbench/exp13_pseudonym_decode.csv", index=False)
    print("\ndecode accuracy: %.3f real, %.3f shuffled, %.6f chance"
          % (df.decode_accuracy.mean(), df.decode_accuracy_shuffled.mean(),
             df.chance_accuracy.mean()))
    print("-> workspace/sybilbench/exp13_pseudonym_decode.csv")
