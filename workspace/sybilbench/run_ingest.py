"""Parse every Sybil archive into the parquet cache. One-time cost; safe to re-run (skips cached).

MAX_RECEIVERS caps how many receiver logs are parsed per simulation window. Attacker labels are still taken
from the *full* filename list, so the cap changes sample size only, never a vehicle's label. 400 keeps a
whole family archive around ~100 MB in memory instead of tens of GB.
"""
import sys, time
sys.path.insert(0, "workspace")
from sybilbench import loader

MAX_RECEIVERS = 400

ARCHIVES = ["GridSybil_0709","GridSybil_1416","DataReplaySybil_0709","DataReplaySybil_1416",
            "DoSRandomSybil_0709","DoSRandomSybil_1416","DoSDisruptiveSybil_0709","DoSDisruptiveSybil_1416"]

if __name__ == "__main__":
    for a in ARCHIVES:
        if loader.cache_path(a).exists():
            print(f"skip {a} (cached)", flush=True); continue
        t0 = time.time()
        try:
            view, truth = loader.load_archive(a, max_receivers=MAX_RECEIVERS)
            loader.save_cache(a, view, truth)
            st = loader.identity_stats(view, truth)
            att = st[st.is_attacker]
            print(f"{a:26s} rows={len(view):8d} vehicles={len(st):5d} attackers={len(att):5d} "
                  f"ids/attacker med={att.identities.median():.0f} max={att.identities.max():.0f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        except Exception as e:
            print(f"{a:26s} FAILED {type(e).__name__}: {e}", flush=True)
    print("INGEST DONE", flush=True)
