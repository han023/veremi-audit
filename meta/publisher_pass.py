import json,os,re,threading,requests,urllib.parse,time
from concurrent.futures import ThreadPoolExecutor
requests.packages.urllib3.disable_warnings()
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
H={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/pdf,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9"}
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
lock=threading.Lock(); st={"ok":0,"fail":0}
def handle(r):
    fn=os.path.join("pdfs",slug(r))
    if os.path.exists(fn) and os.path.getsize(fn)>15000: return
    urls=[u for u in (r.get("pdf_url"),r.get("alt_url"),r.get("landing")) if u]
    doi=r.get("doi") or ""
    s=requests.Session(); s.headers.update(H)
    cands=[]
    for u in urls:
        if "mdpi.com" in u:
            art=re.sub(r'/pdf.*$','',u); cands.append(("mdpi",art,art+"/pdf"))
        elif "springeropen.com" in u or "biomedcentral" in u:
            cands.append(("spr",u.split("/track/")[0],u))
        elif "hindawi.com" in u or "downloads.hindawi" in u:
            m=re.search(r'/(\d{4})/(\d+)',u)
            if m: cands.append(("hin","https://onlinelibrary.wiley.com/doi/"+doi if doi else u,u))
        elif "sciencedirect.com" in u:
            cands.append(("els","https://www.sciencedirect.com/","" ))
        elif "iopscience" in u:
            cands.append(("iop",u.replace("/pdf",""),u))
        elif "degruyter" in u:
            cands.append(("dg",u.replace("/pdf",""),u))
        elif "stars.library" in u or "digitalcommons" in u or "repository" in u or "library" in u:
            cands.append(("repo",u,None))
    for kind,land,pdf in cands:
        try:
            lp=s.get(land,timeout=(10,40),verify=False)
            txt=lp.text if 'text' in lp.headers.get('content-type','') else ''
            targets=[]
            if pdf: targets.append(pdf)
            m=re.search(r'citation_pdf_url["\'][^>]*content=["\']([^"\']+)',txt) or re.search(r'content=["\']([^"\']+)["\'][^>]*citation_pdf_url',txt)
            if m: targets.insert(0,urllib.parse.urljoin(lp.url,m.group(1)))
            for a in re.findall(r'href=["\']([^"\']*(?:viewcontent\.cgi|\.pdf)[^"\']*)',txt)[:4]:
                targets.append(urllib.parse.urljoin(lp.url,a))
            for t in targets:
                try:
                    rr=s.get(t,timeout=(10,50),headers={**H,"Referer":lp.url},verify=False)
                    if rr.content[:4]==b'%PDF' and len(rr.content)>15000:
                        open(fn,'wb').write(rr.content); r["file"]=fn.replace("\\","/")
                        with lock: st["ok"]+=1
                        return
                except Exception: pass
        except Exception: pass
    with lock: st["fail"]+=1
todo=[r for r in recs if not r.get("file") and any(k in ((r.get("pdf_url") or "")+(r.get("alt_url") or "")+(r.get("landing") or "")) for k in ["mdpi.com","springeropen","biomedcentral","hindawi","iopscience","degruyter","stars.library","digitalcommons","repository","library"])]
print("publisher pass on",len(todo),flush=True)
with ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(handle,todo))
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("PUBPASS",st)
