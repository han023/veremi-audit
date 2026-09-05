import json,os,re,sys,threading,requests,urllib.parse
from concurrent.futures import ThreadPoolExecutor
requests.packages.urllib3.disable_warnings()
HDR={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/pdf,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9",
 "Accept-Encoding":"gzip, deflate, br","Connection":"keep-alive","Upgrade-Insecure-Requests":"1"}
recs=json.load(open("meta/all.json",encoding="utf-8"))
extra=json.load(open("meta/openaire_found.json",encoding="utf-8")) if os.path.exists("meta/openaire_found.json") else {}
for r in recs:
    if not r.get("file") and r["title"] in extra and not r.get("pdf_url"): r["pdf_url"]=extra[r["title"]]
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
lock=threading.Lock(); stats={"ok":0,"fail":0}
PDFMETA=re.compile(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',re.I)
PDFMETA2=re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',re.I)
def try_get(s,u,ref=None,verify=True):
    h=dict(HDR)
    if ref: h["Referer"]=ref
    return s.get(u,headers=h,timeout=(10,45),allow_redirects=True,verify=verify)
def save(fn,data):
    open(fn,'wb').write(data); return True
def attempt(r):
    u=r.get("pdf_url") or r.get("landing")
    if not u: return
    fn=os.path.join("pdfs",slug(r))
    if os.path.exists(fn) and os.path.getsize(fn)>15000:
        r["file"]=fn.replace("\\","/"); return
    s=requests.Session()
    cands=[u]
    if "doi.org" not in u and r.get("doi"): cands.append("https://doi.org/"+r["doi"])
    if r.get("landing"): cands.append(r["landing"])
    tried=set()
    for c in list(cands):
        if c in tried: continue
        tried.add(c)
        for verify in (True,False):
            try:
                resp=try_get(s,c,ref=c.split("/pdf")[0],verify=verify)
            except Exception as e:
                if verify: continue
                resp=None
            if resp is None: break
            d=resp.content
            if d[:4]==b'%PDF' and len(d)>15000:
                save(fn,d); r["file"]=fn.replace("\\","/")
                with lock: stats["ok"]+=1; print("OK ",r["title"][:55],flush=True)
                return
            # HTML -> look for citation_pdf_url
            txt=resp.text if 'text' in resp.headers.get('content-type','') else ''
            m=PDFMETA.search(txt) or PDFMETA2.search(txt)
            if m:
                p=urllib.parse.urljoin(resp.url,m.group(1))
                if p not in tried:
                    tried.add(p)
                    try:
                        r2=try_get(s,p,ref=resp.url,verify=verify)
                        if r2.content[:4]==b'%PDF' and len(r2.content)>15000:
                            save(fn,r2.content); r["file"]=fn.replace("\\","/")
                            with lock: stats["ok"]+=1; print("OK*",r["title"][:55],flush=True)
                            return
                    except Exception: pass
            break
    # wayback fallback on original pdf url
    if r.get("pdf_url"):
        try:
            j=requests.get("https://archive.org/wayback/available",params={"url":r["pdf_url"]},timeout=25).json()
            snap=((j.get("archived_snapshots") or {}).get("closest") or {}).get("url")
            if snap:
                rr=try_get(requests.Session(),snap)
                if rr.content[:4]==b'%PDF' and len(rr.content)>15000:
                    save(fn,rr.content); r["file"]=fn.replace("\\","/"); r["via"]="wayback"
                    with lock: stats["ok"]+=1; print("OKw",r["title"][:55],flush=True)
                    return
        except Exception: pass
    with lock: stats["fail"]+=1
todo=[r for r in recs if not r.get("file") and (r.get("pdf_url") or r.get("landing"))]
print("retrying",len(todo),flush=True)
with ThreadPoolExecutor(max_workers=8) as ex: list(ex.map(attempt,todo))
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("RETRY RESULT",stats)
