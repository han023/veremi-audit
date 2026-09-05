import json,os,re,sys,threading,queue,requests
from concurrent.futures import ThreadPoolExecutor
HDR={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
     "Accept":"application/pdf,text/html;q=0.9,*/*;q=0.8"}
recs=json.load(open("meta/all.json",encoding="utf-8"))
extra=json.load(open("meta/openaire_found.json",encoding="utf-8")) if os.path.exists("meta/openaire_found.json") else {}
for r in recs:
    if not r.get("pdf_url") and r["title"] in extra: r["pdf_url"]=extra[r["title"]]
os.makedirs("pdfs",exist_ok=True)
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
lock=threading.Lock(); stats={"ok":0,"skip":0,"fail":0}
def grab(r):
    u=r.get("pdf_url")
    if not u: return
    fn=os.path.join("pdfs",slug(r))
    if os.path.exists(fn) and os.path.getsize(fn)>15000:
        r["file"]=fn.replace("\\","/")
        with lock: stats["skip"]+=1
        return
    if u.startswith("http://arxiv.org/abs/") or u.startswith("https://arxiv.org/abs/"):
        u=u.replace("/abs/","/pdf/")
    try:
        s=requests.Session(); s.headers.update(HDR)
        resp=s.get(u,timeout=(10,30),allow_redirects=True)
        data=resp.content
        if data[:4]==b'%PDF' and len(data)>15000:
            open(fn,'wb').write(data); r["file"]=fn.replace("\\","/")
            with lock: stats["ok"]+=1; print("OK ",r["title"][:60],flush=True)
        else:
            r["dl_error"]=f"{resp.status_code} {resp.headers.get('content-type','')[:30]} {len(data)}b"
            with lock: stats["fail"]+=1; print("XX ",r["title"][:50],"|",r["dl_error"],"|",u[:70],flush=True)
    except Exception as e:
        r["dl_error"]=type(e).__name__
        with lock: stats["fail"]+=1; print("ER ",r["title"][:50],"|",type(e).__name__,"|",u[:70],flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    list(ex.map(grab,[r for r in recs if r.get("pdf_url")]))
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("RESULT",stats)
