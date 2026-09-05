"""
VeReMi / VeReMi-Extension loader with leakage controls built in.

Why the controls exist (see synthesis/08_dataset_audit.md):
  * Finding 1 — `senderPseudo` encodes the true `sender` id in 87-100 % of records, so any model that sees
    the raw pseudonym (or that groups rows by the ground-truth `sender`) can solve the Sybil-grouping task
    by string arithmetic instead of by kinematics.
  * Finding 2 — benign vehicles never change pseudonyms (strict 1:1 sender:pseudonym), so pseudonym-change
    dynamics have to be layered on synthetically if you want to study unlinkability.

The loader therefore returns two objects that are deliberately hard to mix up:

    view   : the *public view*  — what a receiver could actually observe. No `sender`, no raw pseudonym.
    truth  : the *ground truth* — pseudonym token -> true vehicle, plus attack labels. Evaluation only.

Anything that trains or tunes on `truth` is cheating, and the split makes that explicit rather than implicit.

Archive layout (measured):
    <Family>_<density>.zip
      └── VeReMi_<tstart>_<tend>_<date>.zip           (one per simulation window)
            ├── traceJSON-<veh>-<module>-A<atk>-<t>-<seed>.json   receiver log, one JSON object per line
            └── traceGroundTruthJSON-<seed>.json                  every message actually sent

Record types inside a receiver log:
    type 2 -> the receiver's own GPS fix   (no sender fields)
    type 3 -> a received BSM               (sender, senderPseudo, messageID, kinematics)
    type 4 -> ground-truth record          (only in the GroundTruth file)
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

DATASETS = Path("workspace/datasets")
CACHE = Path("workspace/sybilbench/cache")

# traceJSON-<vehicle>-<module>-A<attackType>-<startTime>-<seed>.json
RECEIVER_RE = re.compile(r"traceJSON-(\d+)-(\d+)-A(\d+)-(\d+)-(\d+)\.json$")
GROUNDTRUTH_RE = re.compile(r"traceGroundTruthJSON-(\d+)\.json$")

# VeReMi Extension attack ids -> family name (from the dataset's own numbering)
ATTACK_NAMES = {
    0: "Benign",
    16: "GridSybil",
    17: "DataReplaySybil",
    18: "DoSRandomSybil",
    19: "DoSDisruptiveSybil",
}

VEC_FIELDS = ["pos", "pos_noise", "spd", "spd_noise", "acl", "acl_noise", "hed", "hed_noise"]


@dataclass
class Truth:
    """Ground truth. Never feed any of this to a detector."""

    # token -> true vehicle id  (token is the leakage-safe pseudonym replacement)
    token_to_sender: dict[str, int] = field(default_factory=dict)
    # true vehicle id -> attack type id (0 = benign)
    sender_to_attack: dict[int, int] = field(default_factory=dict)

    def sybil_groups(self) -> dict[int, set[str]]:
        """True partition: vehicle -> the set of identity tokens it emitted."""
        out: dict[int, set[str]] = {}
        for token, sender in self.token_to_sender.items():
            out.setdefault(sender, set()).add(token)
        return out

    def is_attacker(self, token: str) -> bool:
        sender = self.token_to_sender.get(token)
        return bool(sender is not None and self.sender_to_attack.get(sender, 0) != 0)


def _token(archive: str, pseudo, salt: str) -> str:
    """Leakage-safe identity token.

    A raw VeReMi pseudonym leaks its owner (sender 15 -> 10155, 20155, ...). Hashing with a per-run salt
    destroys that structure while staying stable within a run, so linkage must come from kinematics.
    """
    h = hashlib.blake2b(f"{salt}|{archive}|{pseudo}".encode(), digest_size=8)
    return h.hexdigest()


def _flatten(rec: dict) -> dict:
    out = {}
    for f in VEC_FIELDS:
        v = rec.get(f)
        if isinstance(v, (list, tuple)):
            out[f"{f}_x"] = v[0] if len(v) > 0 else np.nan
            out[f"{f}_y"] = v[1] if len(v) > 1 else np.nan
        else:
            out[f"{f}_x"] = np.nan
            out[f"{f}_y"] = np.nan
    return out


def _iter_windows(archive_path: Path):
    """Yield (window_name, ZipFile) for each simulation window inside a family archive."""
    with zipfile.ZipFile(archive_path) as outer:
        for name in outer.namelist():
            if name.endswith(".zip"):
                yield name.split("/")[-1][:-4], zipfile.ZipFile(io.BytesIO(outer.read(name)))


def load_archive(
    archive: str,
    *,
    family_dir: str = "VeReMi_Extension_sybil",
    salt: str = "sybilbench-v1",
    max_windows: int | None = None,
    max_receivers: int | None = None,
) -> tuple[pd.DataFrame, Truth]:
    """Parse one family archive into (public view, ground truth).

    The returned frame contains only what a receiver could observe, plus bookkeeping columns
    (`archive`, `window`, `receiver`) that are metadata, not features.
    """
    path = DATASETS / family_dir / f"{archive}.zip"
    if not path.exists():
        raise FileNotFoundError(path)

    frames: list[pd.DataFrame] = []
    truth = Truth()

    for w_i, (window, zf) in enumerate(_iter_windows(path)):
        if max_windows is not None and w_i >= max_windows:
            break
        rows: list[dict] = []  # per-window, so peak memory stays bounded
        names = [n for n in zf.namelist() if n.endswith(".json")]

        # ground truth: which vehicle is an attacker, and of which family
        for n in names:
            if GROUNDTRUTH_RE.search(n):
                for line in zf.open(n).read().decode("utf-8", "ignore").splitlines():
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    s = rec.get("sender")
                    if s is not None:
                        truth.sender_to_attack.setdefault(int(s), 0)

        receivers = [n for n in names if RECEIVER_RE.search(n)]

        # Label every vehicle from the *full* filename list, not just the parsed subset.
        # Subsampling receivers must never change a vehicle's attacker label, or attackers whose own
        # log was skipped silently become "benign" and pollute the benign identity statistics.
        for n in receivers:
            m = RECEIVER_RE.search(n)
            veh, _module, atk, _t0, _seed = (int(x) for x in m.groups())
            truth.sender_to_attack[veh] = atk

        if max_receivers is not None:
            receivers = receivers[:max_receivers]

        for n in receivers:
            m = RECEIVER_RE.search(n)
            veh, module, atk, _t0, _seed = (int(x) for x in m.groups())

            for line in zf.open(n).read().decode("utf-8", "ignore").splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("type") != 3:
                    continue  # type 2 is the receiver's own GPS, not an observation of others

                pseudo = rec.get("senderPseudo")
                sender = rec.get("sender")
                token = _token(archive, pseudo, salt)
                if sender is not None:
                    truth.token_to_sender[token] = int(sender)

                row = {
                    "archive": archive,
                    "window": window,
                    "receiver": veh,
                    "token": token,               # leakage-safe identity a receiver can key on
                    "rcvTime": rec.get("rcvTime"),
                    "sendTime": rec.get("sendTime"),
                    "messageID": rec.get("messageID"),
                }
                row.update(_flatten(rec))
                rows.append(row)

        if rows:
            frames.append(_compact(pd.DataFrame(rows)))
        del rows

    if not frames:
        return pd.DataFrame(), truth
    view = pd.concat(frames, ignore_index=True)
    return view.sort_values(["rcvTime", "token"]).reset_index(drop=True), truth


def _compact(df: pd.DataFrame) -> pd.DataFrame:
    """Shrink a parsed window: float32 kinematics, categorical bookkeeping columns.

    A list-of-dicts frame for a whole archive is tens of GB; this keeps the peak bounded.
    """
    keep64 = {"rcvTime", "sendTime"}  # 0.5 s cadence analysis needs the precision
    for c in df.columns:
        if df[c].dtype == "float64" and c not in keep64:
            df[c] = df[c].astype("float32")
        elif df[c].dtype == "int64" and c != "messageID":
            df[c] = pd.to_numeric(df[c], downcast="integer")
    for c in ("archive", "window", "token"):
        if c in df.columns:
            df[c] = df[c].astype("category")
    return df


def attach_labels(view: pd.DataFrame, truth: Truth) -> pd.Series:
    """Per-row attacker label, for evaluation only."""
    senders = view["token"].map(truth.token_to_sender)
    return senders.map(lambda s: truth.sender_to_attack.get(s, 0) if pd.notna(s) else 0).astype(int)


def identity_stats(view: pd.DataFrame, truth: Truth) -> pd.DataFrame:
    """Per-vehicle summary: how many identities it emitted, and whether it is an attacker."""
    df = view.copy()
    df["sender"] = df["token"].map(truth.token_to_sender)
    g = df.groupby("sender").agg(
        identities=("token", "nunique"),
        messages=("token", "size"),
        t_first=("rcvTime", "min"),
        t_last=("rcvTime", "max"),
    )
    g["attack"] = [truth.sender_to_attack.get(int(s), 0) for s in g.index]
    g["family"] = g["attack"].map(lambda a: ATTACK_NAMES.get(a, f"A{a}"))
    g["is_attacker"] = g["attack"] != 0
    return g.reset_index()


def cache_path(archive: str) -> Path:
    return CACHE / f"{archive}.parquet"


def save_cache(archive: str, view: pd.DataFrame, truth: Truth) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    view.to_parquet(cache_path(archive), index=False)
    with open(CACHE / f"{archive}.truth.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "token_to_sender": truth.token_to_sender,
                "sender_to_attack": {str(k): v for k, v in truth.sender_to_attack.items()},
            },
            f,
        )


def load_cache(archive: str) -> tuple[pd.DataFrame, Truth]:
    view = pd.read_parquet(cache_path(archive))
    with open(CACHE / f"{archive}.truth.json", encoding="utf-8") as f:
        raw = json.load(f)
    truth = Truth(
        token_to_sender={k: int(v) for k, v in raw["token_to_sender"].items()},
        sender_to_attack={int(k): int(v) for k, v in raw["sender_to_attack"].items()},
    )
    return view, truth
