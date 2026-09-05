import json,re,time,sys,urllib.parse,requests
S=requests.Session(); S.headers.update({"User-Agent":"sybil-vanet-research/1.0 (mailto:abdullhannan0311@gmail.com)"})
recs=json.load(open("meta/all.json",encoding="utf-8"))
def norm(t): return re.sub(r'[^a-z0-9]+',' ',(t or '').lower()).strip()
todo=[r for r in recs if not r.get("pdf_url")]
print("openaire lookup for",len(todo),file=sys.stderr)
found=0
INST=re.compile(r'<instance[^>]*>(.*?)</instance>',re.S)
for i,r in enumerate(todo):
    title=re.sub(r'[^\w\s]',' ',r["title"])[:180]
    try:
        x=S.get("https://api.openaire.eu/search/publications",params={"title":title,"size":3},timeout=40).text
    except Exception: continue
    # only trust result whose title matches
    if norm(r["title"])[:40] not in norm(x): continue
    urls=[]
    for blk in INST.findall(x):
        if 'classid="OPEN"' not in blk: continue
        for u in re.findall(r'<url>([^<]+)</url>',blk):
            u=u.strip()
            if 'doi.org' in u or 'dblp' in u: continue
            urls.append(u)
    pdfs=[u for u in urls if u.lower().endswith('.pdf')] or urls
    if pdfs:
        r["pdf_url"]=pdfs[0]; r["oa_host"]="openaire"; found+=1
        print("  +",r["title"][:55],"->",pdfs[0][:70],file=sys.stderr)
    if i%25==0:
        json.dump({r["title"]:r["pdf_url"] for r in recs if r.get("oa_host")=="openaire"},open("meta/openaire_found.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
        print(i,"found",found,file=sys.stderr)
    time.sleep(0.5)
json.dump({r["title"]:r["pdf_url"] for r in recs if r.get("oa_host")=="openaire"},open("meta/openaire_found.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("OPENAIRE new candidates:",found)
