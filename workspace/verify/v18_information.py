"""V18 - how many bits of the sender does the pseudonym's structure supply?

A first attempt computed I(P; S) directly and got exactly H(S) on every archive --
and exactly H(S) on the permuted control as well. That is not a leak measurement.
A pseudonym is unique, so it determines its owner in-sample whatever the owner is;
H(S | P) is zero by construction. Naive mutual information here measures identifier
uniqueness, not the structure we care about.

The quantity that does mean something is how many bits a *structural* decoder
recovers, because such a decoder can be wrong. Let D be the sender named by the
untrained digit decoder of Experiment 13. Then

    bits recovered = H(S) - H(S | D)

is the reduction in uncertainty about the true sender obtained from the identifier's
form alone. The permuted control keeps both populations and destroys only the
correspondence, so the decoder is left guessing and recovers close to nothing.

H(S) is the number of bits needed to name the emitting vehicle from nothing. The
ratio therefore reads as: the identifier's shape hands over this fraction of the
partition a detector is supposed to infer.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/sybilbench")
from sybilbench import loader  # noqa: E402
from exp13_pseudonym_decode import decode  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def entropy(counts) -> float:
    n = sum(counts)
    if n == 0:
        return 0.0
    p = np.array([c / n for c in counts if c > 0])
    return float(-(p * np.log2(p)).sum())


def conditional_entropy(pairs) -> float:
    """H(S | D) over the empirical joint of decoder output and truth."""
    by_d: dict[object, Counter] = defaultdict(Counter)
    for d, s in pairs:
        by_d[d][s] += 1
    n = len(pairs)
    return sum((sum(c.values()) / n) * entropy(list(c.values())) for c in by_d.values())


def run(archive: str, rng) -> dict:
    with open(Path("workspace/sybilbench/cache") / f"{archive}.pseudomap.json",
              encoding="utf-8") as f:
        tok_pseudo = {k: int(v) for k, v in json.load(f)["token_to_pseudo"].items()}
    _v, truth = loader.load_cache(archive)
    toks = [t for t in tok_pseudo if t in truth.token_to_sender]
    pseudo = [tok_pseudo[t] for t in toks]
    sender = [truth.token_to_sender[t] for t in toks]

    by_len = sorted(((str(s), s) for s in sorted(set(sender))), key=lambda kv: -len(kv[0]))
    decoded = [decode(p, by_len) for p in pseudo]

    h_s = entropy(list(Counter(sender).values()))
    h_given_d = conditional_entropy(list(zip(decoded, sender)))
    recovered = h_s - h_given_d

    permuted = list(sender)
    rng.shuffle(permuted)
    h_given_d_ctrl = conditional_entropy(list(zip(decoded, permuted)))
    recovered_ctrl = h_s - h_given_d_ctrl

    return {
        "archive": archive,
        "identities": len(toks),
        "H_sender_bits": round(h_s, 3),
        "H_sender_given_decode_bits": round(h_given_d, 3),
        "bits_recovered": round(recovered, 3),
        "fraction_recovered": round(recovered / h_s, 4) if h_s else 0.0,
        "bits_recovered_permuted": round(recovered_ctrl, 3),
        "fraction_permuted": round(recovered_ctrl / h_s, 4) if h_s else 0.0,
    }


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rows = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        r = run(a, rng)
        rows.append(r)
        print(r, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("workspace/verify/v18_information.csv", index=False)
    print("\nH(S) spans %.2f to %.2f bits" % (df.H_sender_bits.min(), df.H_sender_bits.max()))
    print("decoder recovers %.1f%% to %.1f%% of it; permuted control %.1f%% to %.1f%%"
          % (100 * df.fraction_recovered.min(), 100 * df.fraction_recovered.max(),
             100 * df.fraction_permuted.min(), 100 * df.fraction_permuted.max()))
    print("-> workspace/verify/v18_information.csv")
