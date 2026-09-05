"""
Loader for the original VeReMi (2018) dataset — the only public set with real received power.

Audit Finding 3: the benchmark family splits its useful properties across incompatible releases.

    VeReMi 2018      RSSI present (1.3e-9 ... 2.6e-5 W)   no pseudonyms   no Sybil-specific families
    VeReMi Extension no RSSI                              pseudonyms      Sybil families
    preprocessed CSV no RSSI                              no identity     labels only

So RSSI-based detectors — 33 of the 92 corpus papers, the single largest family — can only be reproduced
here, against the 2018 position-falsification attacks rather than against Sybil attacks. That is a real
limitation to state, not to hide: it means no public data supports RSSI-based *Sybil* detection end to end.

Archive layout (measured):
    VeReMi_Dataset.zip
      └── veins_maat.uc1.<id>.<date>.tgz          (225 of them)
            └── work/.../securecomm2018/
                  ├── JSONlog-<veh>-<module>-A<atk>.json   receiver log
                  └── GroundTruthJSONlog.json              every message sent

Record types:
    type 2 -> receiver's own GPS      fields: noise, pos, rcvTime, spd, spd_noise, type
    type 3 -> received BSM            fields: RSSI, messageID, pos, pos_noise, rcvTime, sendTime, sender,
                                              spd, spd_noise, type
"""
from __future__ import annotations

import io
import json
import re
import tarfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ARCHIVE = Path("workspace/datasets/VeReMi_original/VeReMi_Dataset.zip")
CACHE = Path("workspace/sybilbench/cache")

RECEIVER_RE = re.compile(r"JSONlog-(\d+)-(\d+)-A(\d+)\.json$")

# VeReMi 2018 attack ids (from the SecureComm 2018 paper)
ATTACK_NAMES = {
    0: "Benign",
    1: "ConstantPosition",
    2: "ConstantPositionOffset",
    4: "RandomPosition",
    8: "RandomPositionOffset",
    16: "EventualStop",
}


@dataclass
class Truth2018:
    """Ground truth. Evaluation only — never a feature."""

    sender_to_attack: dict[int, int] = field(default_factory=dict)

    def is_attacker(self, sender: int) -> bool:
        return self.sender_to_attack.get(int(sender), 0) != 0


def _flatten(rec: dict) -> dict:
    out = {}
    for f in ("pos", "pos_noise", "spd", "spd_noise"):
        v = rec.get(f)
        if isinstance(v, (list, tuple)):
            out[f"{f}_x"] = v[0] if len(v) > 0 else np.nan
            out[f"{f}_y"] = v[1] if len(v) > 1 else np.nan
        else:
            out[f"{f}_x"] = np.nan
            out[f"{f}_y"] = np.nan
    return out


def load(max_archives: int | None = 8, max_receivers_per_archive: int | None = 60):
    """Parse the 2018 dataset into (view with RSSI, truth).

    `max_archives` bounds the work: the zip holds 225 simulation runs. Attacker labels come from the receiver
    filenames of every archive touched, so subsampling changes sample size, never a label.
    """
    if not ARCHIVE.exists():
        raise FileNotFoundError(ARCHIVE)

    frames: list[pd.DataFrame] = []
    truth = Truth2018()

    with zipfile.ZipFile(ARCHIVE) as z:
        tgzs = [n for n in z.namelist() if n.endswith(".tgz")]
        if max_archives is not None:
            tgzs = tgzs[:max_archives]

        for a_i, name in enumerate(tgzs):
            with tarfile.open(fileobj=io.BytesIO(z.read(name)), mode="r:gz") as t:
                members = [m for m in t.getmembers() if m.isfile() and "JSONlog" in m.name]
                receivers = [m for m in members if RECEIVER_RE.search(m.name.split("/")[-1])]

                # label every vehicle from the full filename list first
                for m in receivers:
                    veh, _mod, atk = (int(x) for x in RECEIVER_RE.search(m.name.split("/")[-1]).groups())
                    truth.sender_to_attack[veh] = atk

                use = receivers[:max_receivers_per_archive] if max_receivers_per_archive else receivers
                rows = []
                for m in use:
                    veh, _mod, atk = (int(x) for x in RECEIVER_RE.search(m.name.split("/")[-1]).groups())
                    for line in t.extractfile(m).read().decode("utf-8", "ignore").splitlines():
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        rtype = rec.get("type")
                        if rtype not in (2, 3):
                            continue
                        row = {
                            "archive": a_i,
                            "receiver": veh,
                            "type": rtype,
                            # type 2 is the receiver's OWN GPS fix: needed to place the receiver at
                            # reception time, without which claimed distance — and therefore RSS-based
                            # position verification (Xiao 2006) — cannot be computed at all.
                            "sender": rec.get("sender") if rtype == 3 else veh,
                            "messageID": rec.get("messageID"),
                            "rcvTime": rec.get("rcvTime"),
                            "sendTime": rec.get("sendTime"),
                            "RSSI": rec.get("RSSI"),
                        }
                        row.update(_flatten(rec))
                        rows.append(row)
                if rows:
                    frames.append(pd.DataFrame(rows))

    if not frames:
        return pd.DataFrame(), truth
    view = pd.concat(frames, ignore_index=True).sort_values("rcvTime").reset_index(drop=True)
    return view, truth


def rssi_features(view: pd.DataFrame) -> pd.DataFrame:
    """Per-sender RSSI statistics — the substrate for the physical-layer detector family.

    Xiao 2006 uses the *distribution* of received signal strength over a window; Voiceprint 2017 uses the RSSI
    *time series* compared by DTW. Both need the columns produced here. Deduplicate per (receiver, sender):
    RSSI is a property of a link, so pooling across receivers would average away the very variation these
    methods exploit.
    """
    v = view[view["RSSI"].notna() & (view["RSSI"] > 0)].copy()
    v["rssi_dbm"] = 10 * np.log10(v["RSSI"] * 1000.0)  # W -> dBm
    # keyed on archive too: vehicle ids repeat across simulation runs
    g = v.groupby(["archive", "receiver", "sender"], observed=True)
    out = g.agg(
        n=("rssi_dbm", "size"),
        rssi_mean=("rssi_dbm", "mean"),
        rssi_std=("rssi_dbm", "std"),
        rssi_min=("rssi_dbm", "min"),
        rssi_max=("rssi_dbm", "max"),
        duration=("rcvTime", lambda t: t.max() - t.min()),
    ).reset_index()
    out["rssi_range"] = out["rssi_max"] - out["rssi_min"]
    return out.fillna(0.0)


def label(df: pd.DataFrame, truth: Truth2018) -> pd.Series:
    return df["sender"].map(lambda s: 1 if truth.is_attacker(s) else 0)


def position_verification_features(view: pd.DataFrame) -> pd.DataFrame:
    """RSS-based position verification, per link — the actual Xiao 2006 / Bouassida 2007 measurement.

    Raw RSSI statistics cannot expose a position lie: received power reflects the *true* geometry, so it stays
    honest while the claimed coordinates do not. The signal is the **residual** between the distance a receiver
    would infer from power and the distance the sender claims.

    Steps: place the receiver at reception time from its own type-2 GPS fixes; compute claimed distance to the
    sender's claimed position; fit a log-distance path-loss model over all links; per link, summarise the
    residual between measured RSSI and the RSSI that claimed distance predicts.
    """
    # NOTE: vehicle ids are reused across the 225 independent simulation runs — measured: 95 of 102 receiver
    # ids appear in more than one archive. Grouping on `receiver` alone therefore matches a reception in one
    # simulation against a GPS fix from another, and the resulting "distances" are meaningless: doing so
    # degrades corr(RSSI, log d) from -0.64 to -0.28 and flattens the path-loss slope from -9.1 to
    # -3.7 dB/decade. Always key on (archive, receiver).
    rx = view[view["type"] == 2][["archive", "receiver", "rcvTime", "pos_x", "pos_y"]].sort_values(
        ["archive", "receiver", "rcvTime"]
    )
    tx = view[(view["type"] == 3) & view["RSSI"].notna() & (view["RSSI"] > 0)].copy()
    if rx.empty or tx.empty:
        return pd.DataFrame()

    # nearest own-GPS fix for each reception, within the same simulation run
    out = []
    for (a, r), g in tx.groupby(["archive", "receiver"], observed=True):
        own = rx[(rx["archive"] == a) & (rx["receiver"] == r)]
        if own.empty:
            continue
        idx = np.searchsorted(own["rcvTime"].to_numpy(), g["rcvTime"].to_numpy()).clip(0, len(own) - 1)
        g = g.copy()
        g["rx_x"] = own["pos_x"].to_numpy()[idx]
        g["rx_y"] = own["pos_y"].to_numpy()[idx]
        out.append(g)
    if not out:
        return pd.DataFrame()
    t = pd.concat(out, ignore_index=True)

    t["claimed_dist"] = np.hypot(t["pos_x"] - t["rx_x"], t["pos_y"] - t["rx_y"]).clip(lower=1.0)
    t["rssi_dbm"] = 10 * np.log10(t["RSSI"] * 1000.0)
    t["log_d"] = np.log10(t["claimed_dist"])

    # fit rssi ~ a + b*log10(d) globally; b is -10n for path-loss exponent n
    A = np.vstack([np.ones(len(t)), t["log_d"].to_numpy()]).T
    coef, *_ = np.linalg.lstsq(A, t["rssi_dbm"].to_numpy(), rcond=None)
    t["rssi_pred"] = A @ coef
    t["residual"] = t["rssi_dbm"] - t["rssi_pred"]

    g = t.groupby(["archive", "receiver", "sender"], observed=True)
    feats = g.agg(
        n=("residual", "size"),
        resid_mean=("residual", "mean"),
        resid_absmean=("residual", lambda v: float(np.mean(np.abs(v)))),
        resid_std=("residual", "std"),
        resid_max=("residual", lambda v: float(np.max(np.abs(v)))),
        dist_mean=("claimed_dist", "mean"),
        dist_std=("claimed_dist", "std"),
        rssi_mean=("rssi_dbm", "mean"),
        rssi_std=("rssi_dbm", "std"),
    ).reset_index()
    feats.attrs["path_loss_fit"] = {"intercept_dbm": float(coef[0]), "slope_db_per_decade": float(coef[1])}
    return feats.fillna(0.0)


if __name__ == "__main__":
    view, truth = load(max_archives=4)
    print(f"rows={len(view)} senders={view['sender'].nunique()} receivers={view['receiver'].nunique()}")
    print("columns:", list(view.columns))
    print(f"RSSI present in {view['RSSI'].notna().mean():.1%} of rows")
    f = rssi_features(view)
    y = label(f, truth)
    print(f"link-level rows={len(f)} attacker share={y.mean():.3f}")
    print(f.head().to_string())
    print("\nattack families present:",
          {ATTACK_NAMES.get(a, a): n for a, n in
           pd.Series(list(truth.sender_to_attack.values())).value_counts().items()})
