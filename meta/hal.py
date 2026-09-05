import json,re,requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"}
recs=json.load(open("meta/all.json",encoding="utf-8"))
def norm(t): return re.sub(r'[^a-z0-9]+',' ',(t or '').lower()).strip()
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
idx={norm(r["title"])[:60]:r for r in recs}
got=0
for q in ["sybil AND (vanet OR vehicular OR v2x)","sybil AND vehicule","sybil attack detection vehicular"]:
    d=requests.get("https://api.archives-ouvertes.fr/search/",params={"q":q,"fl":"title_s,fileMain_s,producedDateY_i,authFullName_s,doiId_s","rows":60,"wt":"json"},timeout=40).json()["response"]
    for x in d["docs"]:
        t=x.get("title_s"); t=t[0] if isinstance(t,list) else t
        f=x.get("fileMain_s")
        if not f or not t: continue
        if "sybil" not in norm(t): continue
        r=idx.get(norm(t)[:60])
        if r is None:
            r={"title":t.strip(),"doi":x.get("doiId_s",""),"year":x.get("producedDateY_i"),
               "venue":"HAL","authors":x.get("authFullName_s") or [],"cites":None,"oa_status":"green",
               "pdf_url":f,"landing":f,"abstract":"","sources":["hal"]}
            recs.append(r); idx[norm(t)[:60]]=r
        if r.get("file"): continue
        try:
            b=requests.get(f,headers=H,timeout=60).content
            if b[:4]==b'%PDF' and len(b)>15000:
                fn="pdfs/"+slug(r); open(fn,'wb').write(b); r["file"]=fn; r["pdf_url"]=r.get("pdf_url") or f
                got+=1; print("HAL OK",t[:60])
        except Exception as e: print("HAL ERR",type(e).__name__,t[:40])
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("HAL downloaded",got,"| corpus",len(recs))
