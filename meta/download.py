import json,os,re,sys,time,requests
MAIL="abdullhannan0311@gmail.com"
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                  "Accept":"application/pdf,text/html;q=0.9,*/*;q=0.8"})
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    y=r.get("year") or "nd"
    a=(r.get("authors") or ["anon"])[0].split()[-1] if r.get("authors") else "anon"
    a=re.sub(r'[^A-Za-z]','',a) or "anon"
    return f"{y}_{a}_{t}.pdf"
os.makedirs("pdfs",exist_ok=True)
ok=fail=skip=0; log=[]
for r in recs:
    u=r.get("pdf_url")
    if not u: continue
    fn=os.path.join("pdfs",slug(r))
    if os.path.exists(fn) and os.path.getsize(fn)>20000:
        r["file"]=fn; skip+=1; continue
    try:
        resp=S.get(u,timeout=40,allow_redirects=True,stream=True)
        data=resp.content
        if data[:4]==b'%PDF' and len(data)>15000:
            open(fn,'wb').write(data); r["file"]=fn; ok+=1
        else:
            ct=resp.headers.get("content-type","")
            r["dl_error"]=f"{resp.status_code} {ct[:40]} len={len(data)}"
            fail+=1; log.append((r["title"][:60],r["dl_error"],u[:80]))
    except Exception as e:
        r["dl_error"]=str(e)[:90]; fail+=1; log.append((r["title"][:60],str(e)[:60],u[:80]))
    time.sleep(0.2)
    if (ok+fail)%10==0: json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print(f"downloaded={ok} already={skip} failed={fail}")
for l in log[:40]: print(" FAIL |","|".join(map(str,l)))
