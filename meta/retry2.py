import json,os,re,threading,requests,urllib.parse
from concurrent.futures import ThreadPoolExecutor
requests.packages.urllib3.disable_warnings()
HDR={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/pdf,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9"}
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
M=re.compile(r'<meta[^>]+citation_pdf_url[^>]*>',re.I); C=re.compile(r'content=["\']([^"\']+)',re.I)
lock=threading.Lock(); st={"ok":0,"fail":0}
def go(r):
    fn=os.path.join("pdfs",slug(r))
    if os.path.exists(fn) and os.path.getsize(fn)>15000: return
    s=requests.Session(); s.headers.update(HDR)
    for u in [x for x in (r.get("alt_url"),r.get("pdf_url"),r.get("landing")) if x]:
        for verify in (True,False):
            try: resp=s.get(u,timeout=(10,40),allow_redirects=True,verify=verify)
            except Exception:
                continue
            d=resp.content
            if d[:4]==b'%PDF' and len(d)>15000:
                open(fn,'wb').write(d); r["file"]=fn.replace("\\","/")
                with lock: st["ok"]+=1
                return
            t=resp.text if 'text' in resp.headers.get('content-type','') else ''
            m=M.search(t)
            if m:
                c=C.search(m.group(0))
                if c:
                    p=urllib.parse.urljoin(resp.url,c.group(1))
                    try:
                        r2=s.get(p,timeout=(10,40),headers={**HDR,"Referer":resp.url},verify=verify)
                        if r2.content[:4]==b'%PDF' and len(r2.content)>15000:
                            open(fn,'wb').write(r2.content); r["file"]=fn.replace("\\","/")
                            with lock: st["ok"]+=1
                            return
                    except Exception: pass
            break
    # wayback
    for u in [x for x in (r.get("alt_url"),r.get("pdf_url")) if x]:
        try:
            j=requests.get("https://archive.org/wayback/available",params={"url":u},timeout=20).json()
            sn=((j.get("archived_snapshots") or {}).get("closest") or {}).get("url")
            if sn:
                rr=requests.get(sn,headers=HDR,timeout=(10,40))
                if rr.content[:4]==b'%PDF' and len(rr.content)>15000:
                    open(fn,'wb').write(rr.content); r["file"]=fn.replace("\\","/"); r["via"]="wayback"
                    with lock: st["ok"]+=1
                    return
        except Exception: pass
    with lock: st["fail"]+=1
todo=[r for r in recs if not r.get("file") and (r.get("alt_url") or r.get("pdf_url") or r.get("landing"))]
print("retry2 on",len(todo),flush=True)
with ThreadPoolExecutor(max_workers=8) as ex: list(ex.map(go,todo))
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("RETRY2",st)
