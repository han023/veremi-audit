import os,re,json,hashlib,sys
from pypdf import PdfReader
APPLY = "--apply" in sys.argv
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
def norm(t): return re.sub(r'[^a-z0-9]+',' ',(t or '').lower()).strip()
have={f for f in os.listdir("pdfs")}
info={}
for r in recs:
    s=slug(r)
    if s not in have: continue
    p="pdfs/"+s
    if s in info: continue
    try:
        rd=PdfReader(p); txt=""
        for pg in rd.pages[:2]: txt+=" "+(pg.extract_text() or "")
    except Exception:
        txt=""
    info[s]={"text":norm(txt)[:4000],"md5":hashlib.md5(open(p,'rb').read()).hexdigest(),"rec":r}
def score(title,txt):
    w=[x for x in norm(title).split() if len(x)>3]
    if not w or not txt: return -1
    return sum(1 for x in w if x in txt)/len(w)
groups={}
for s,d in info.items(): groups.setdefault(d["md5"],[]).append(s)
delete=[]
for h,files in groups.items():
    if len(files)==1: continue
    txt=info[files[0]]["text"]
    scored=sorted(((score(info[f]["rec"]["title"],txt),f) for f in files),reverse=True)
    keep=scored[0][1]
    for sc,f in scored[1:]:
        delete.append((f,f"dup of {keep} (score {sc:.2f} vs {scored[0][0]:.2f})"))
for s,d in info.items():
    if any(s==f for f,_ in delete): continue
    sc=score(d["rec"]["title"],d["text"])
    if 0 <= sc < 0.4 and len(d["text"])>300:
        delete.append((s,f"content mismatch (score {sc:.2f})"))
print("files:",len(info),"| to delete:",len(delete))
for f,why in delete: print("  DEL",why,"|",f[:75])
scanned=[s for s,d in info.items() if len(d["text"])<300]
print("no text layer (scanned, kept unverified):",len(scanned))
for s in scanned: print("   ~",s[:75])
if APPLY:
    for f,_ in delete:
        try: os.remove("pdfs/"+f)
        except Exception as e: print("rm fail",f,e)
    print("deleted",len(delete))
