"""Download Sybil-relevant VeReMi-family datasets from Zenodo. Resumable: re-run after any failure."""
import os,sys,time,json,requests
H={"User-Agent":"research-corpus/1.0"}
JOBS=[
 ("VeReMi_original","20081895",lambda k: k.endswith((".zip",".md",".txt"))),
 ("VeReMi_preprocessed","14903687",lambda k: True),
 ("VeReMi_Extension_sybil","20090854",lambda k: "sybil" in k.lower()),
 ("VeReMi_NextGen_sybil","19665762",lambda k: "sybil" in k.lower() or "groundTruth" in k),
]
def fetch(url,path,size):
    for attempt in range(8):
        done=os.path.getsize(path) if os.path.exists(path) else 0
        if done==size: return True
        if done>size: os.remove(path); done=0
        hdr=dict(H)
        if done: hdr["Range"]=f"bytes={done}-"
        try:
            with requests.get(url,stream=True,timeout=(20,120),headers=hdr) as r:
                if done and r.status_code!=206:   # server ignored Range -> restart clean
                    done=0; mode="wb"
                elif done: mode="ab"
                else: mode="wb"
                r.raise_for_status()
                with open(path,mode) as f:
                    for chunk in r.iter_content(1<<20):
                        f.write(chunk)
        except Exception as e:
            got=os.path.getsize(path) if os.path.exists(path) else 0
            print(f"    retry {attempt+1}: {type(e).__name__} at {got/1e6:.0f}/{size/1e6:.0f} MB",flush=True)
            time.sleep(5*(attempt+1))
    return os.path.exists(path) and os.path.getsize(path)==size
for name,rid,filt in JOBS:
    d=os.path.join("workspace/datasets",name); os.makedirs(d,exist_ok=True)
    rec=requests.get(f"https://zenodo.org/api/records/{rid}",timeout=60,headers=H).json()
    json.dump(rec["metadata"],open(os.path.join(d,"_zenodo_metadata.json"),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
    files=[f for f in rec["files"] if filt(f["key"])]
    print(f"== {name}: {len(files)} files {sum(f['size'] for f in files)/1e9:.2f} GB",flush=True)
    for f in files:
        p=os.path.join(d,f["key"])
        if os.path.exists(p) and os.path.getsize(p)==f["size"]:
            print("  have",f["key"],flush=True); continue
        ok=fetch(f["links"]["self"],p,f["size"])
        print(("  OK   " if ok else "  FAIL ")+f["key"],f"{os.path.getsize(p)/1e6:.0f} MB",flush=True)
print("DATASETS DONE",flush=True)
