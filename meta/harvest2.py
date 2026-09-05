import json, re, time, urllib.parse, sys, xml.etree.ElementTree as ET
import requests
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"sybil-vanet-research/1.0 (mailto:{MAIL})"})
def norm(t): return re.sub(r'[^a-z0-9]+',' ',(t or '').lower()).strip()

recs = json.load(open("meta/openalex.json",encoding="utf-8"))
idx = {}
for r in recs:
    k=(r.get("doi") or "").lower() or norm(r["title"])[:90]
    idx[k]=r
    idx.setdefault(norm(r["title"])[:90], r)

def add(rec):
    k=(rec.get("doi") or "").lower() or norm(rec["title"])[:90]
    cur = idx.get(k) or idx.get(norm(rec["title"])[:90])
    if cur:
        for f in ("pdf_url","doi","year","venue","abstract","cites","landing"):
            if not cur.get(f) and rec.get(f): cur[f]=rec[f]
        cur["sources"]=sorted(set(cur.get("sources",[]))|set(rec["sources"]))
    else:
        recs.append(rec); idx[k]=rec; idx[norm(rec["title"])[:90]]=rec

# ---- Semantic Scholar ----
S2="https://api.semanticscholar.org/graph/v1/paper/search"
fields="title,year,abstract,venue,externalIds,openAccessPdf,citationCount,authors"
for q in ["sybil attack VANET","sybil attack vehicular ad hoc network",
          "sybil node detection vehicular network","sybil attack internet of vehicles",
          "sybil attack V2X security"]:
    for off in range(0,300,100):
        for attempt in range(6):
            r=S.get(S2,params={"query":q,"fields":fields,"limit":100,"offset":off},timeout=60)
            if r.status_code==200: break
            time.sleep(12)
        else:
            print("S2 fail",q,off,file=sys.stderr); break
        d=r.json(); data=d.get("data") or []
        for p in data:
            t=p.get("title") or ""
            if "sybil" not in norm(t): continue
            oap=p.get("openAccessPdf") or {}
            add({"title":t.strip(),"doi":(p.get("externalIds") or {}).get("DOI",""),
                 "year":p.get("year"),"venue":p.get("venue"),
                 "authors":[a["name"] for a in (p.get("authors") or [])][:12],
                 "cites":p.get("citationCount"),"oa_status":None,
                 "pdf_url":oap.get("url"),"landing":None,
                 "abstract":(p.get("abstract") or "")[:1500],"sources":["s2"],
                 "arxiv":(p.get("externalIds") or {}).get("ArXiv")})
        if len(data)<100: break
        time.sleep(2)
    print("after s2",q,len(recs),file=sys.stderr)

# ---- arXiv ----
for q in ['all:"sybil attack" AND all:vehicular','all:sybil AND all:VANET','all:sybil AND all:"internet of vehicles"']:
    r=S.get("http://export.arxiv.org/api/query",params={"search_query":q,"max_results":200},timeout=60)
    root=ET.fromstring(r.text); ns={"a":"http://www.w3.org/2005/Atom"}
    for e in root.findall("a:entry",ns):
        t=" ".join((e.findtext("a:title",'',ns) or "").split())
        if "sybil" not in norm(t): continue
        aid=e.findtext("a:id",'',ns)
        add({"title":t,"doi":"","year":int((e.findtext("a:published",'',ns) or "0000")[:4]),
             "venue":"arXiv preprint","authors":[a.findtext("a:name",'',ns) for a in e.findall("a:author",ns)][:12],
             "cites":None,"oa_status":"green","pdf_url":aid.replace("/abs/","/pdf/"),
             "landing":aid,"abstract":" ".join((e.findtext("a:summary",'',ns) or "").split())[:1500],
             "sources":["arxiv"]})
    time.sleep(3)
    print("after arxiv",q,len(recs),file=sys.stderr)

json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("TOTAL",len(recs),"| with pdf_url:",sum(1 for r in recs if r.get("pdf_url")))
