import os,re,json,hashlib
from pypdf import PdfReader
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
def norm(t): return re.sub(r'[^a-z0-9]+',' ',(t or '').lower()).strip()
bad=[]; dup={}
have={f for f in os.listdir("pdfs")}
n=0
for r in recs:
    s=slug(r)
    if s not in have: continue
    p="pdfs/"+s; n+=1
    try:
        rd=PdfReader(p)
        txt=""
        for pg in rd.pages[:2]:
            txt+=" "+(pg.extract_text() or "")
        txt=norm(txt)[:3000]
    except Exception as e:
        bad.append((s,"unreadable:"+type(e).__name__)); continue
    words=[w for w in norm(r["title"]).split() if len(w)>3]
    if not words: continue
    hit=sum(1 for w in words if w in txt)
    if hit/len(words) < 0.45:
        bad.append((s,f"title match {hit}/{len(words)}"))
    h=hashlib.md5(open(p,'rb').read()).hexdigest()
    dup.setdefault(h,[]).append(s)
print("checked",n)
print("--- suspicious ---")
for s,why in bad: print(" ",why,"|",s[:80])
print("--- duplicate content ---")
for h,v in dup.items():
    if len(v)>1: print("  ",len(v),"copies:", " || ".join(x[:60] for x in v))
