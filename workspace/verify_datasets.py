"""Verify downloaded datasets against Zenodo MD5. Deletes corrupt files so the fetcher re-downloads them."""
import os,hashlib,sys
DELETE = "--delete" in sys.argv
ok=bad=miss=part=0
for line in open("workspace/datasets/manifest.tsv",encoding="utf-8"):
    p,s,u,md5=line.rstrip("\n").split("\t"); s=int(s)
    if not os.path.exists(p): miss+=1; continue
    g=os.path.getsize(p)
    if g!=s: part+=1; print(f"PARTIAL {os.path.basename(p)} {g/1e6:.0f}/{s/1e6:.0f} MB"); continue
    h=hashlib.md5()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(1<<22), b''): h.update(chunk)
    if h.hexdigest()==md5:
        ok+=1; print(f"OK      {os.path.basename(p)} {g/1e6:.0f} MB")
    else:
        bad+=1; print(f"CORRUPT {os.path.basename(p)} md5 {h.hexdigest()[:12]} != {md5[:12]}")
        if DELETE: os.remove(p); print(f"        deleted -> will re-download")
print(f"\nverified_ok={ok} corrupt={bad} partial={part} missing={miss}")
