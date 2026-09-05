import json,os,re,csv,hashlib
recs=json.load(open("meta/all.json",encoding="utf-8"))
have=set(os.listdir("pdfs"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
for r in recs:
    s=slug(r); r["file"]="pdfs/"+s if s in have else None
def veh(r):
    t=((r.get("title") or "")+" "+(r.get("abstract") or "")+" "+(r.get("venue") or "")).lower()
    return any(k in t for k in ["vanet","vehic","v2x","v2v","internet of vehicles","platoon","roadside","rsu","traffic","driving","crowdsens"])
recs=[r for r in recs if veh(r)]
# dedupe identical file contents
seen={}
for r in recs:
    if r.get("file") and os.path.exists(r["file"]):
        h=hashlib.md5(open(r["file"],'rb').read()).hexdigest()
        r["md5"]=h
        seen.setdefault(h,[]).append(r)
dupes=sum(len(v)-1 for v in seen.values() if len(v)>1)
CATS=[
 ("RSSI / signal-strength & PHY","rssi|signal strength|received signal|channel character|physical layer|power control|angle of arrival|doppler"),
 ("Position / trajectory verification","position verif|trajectory|localization|location verif|footprint|gps|geograph|movement|mobility pattern"),
 ("Cryptography, PKI & pseudonyms","pseudonym|certificat|public key|signature|authentication|key management|privacy-preserving|anonym|zero-knowledge"),
 ("Machine learning / deep learning","machine learning|deep learn|neural|svm|k-nearest|knn|random forest|classifier|federated|reinforcement|cnn|lstm|transformer|self-supervis"),
 ("Blockchain / distributed ledger","blockchain|ledger|smart contract|proof-of|consensus"),
 ("Trust / reputation","trust|reputation|belief|fuzzy"),
 ("RSU / infrastructure-assisted","roadside unit|rsu|infrastructure|fog|edge|cloud"),
 ("Surveys & reviews","survey|review|taxonomy|comparative study|comparison of"),
 ("Routing-protocol impact","routing|aodv|olsr|gpsr|dsr"),
 ("Datasets & simulation","dataset|simulation|veins|sumo|ns-2|ns2|ns-3|omnet"),
]
def cats(r):
    t=((r.get("title") or "")+" "+(r.get("abstract") or "")).lower()
    out=[n for n,pat in CATS if re.search(pat,t)]
    return out or ["Other / general Sybil defence"]
for r in recs: r["cats"]=cats(r)
recs.sort(key=lambda r:(-(r.get("cites") or 0), -(r.get("year") or 0)))
got=[r for r in recs if r.get("file")]; miss=[r for r in recs if not r.get("file")]
with open("index.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["have_pdf","year","cites","title","authors","venue","doi","topics","file","pdf_url","landing"])
    for r in recs:
        w.writerow(["YES" if r.get("file") else "","" if not r.get("year") else r["year"],r.get("cites") or "",
                    r["title"],"; ".join(r.get("authors") or []),r.get("venue") or "",r.get("doi") or "",
                    "; ".join(r["cats"]),r.get("file") or "",r.get("pdf_url") or "",r.get("landing") or ""])
def bibkey(r,i):
    a=re.sub(r'\W','',((r.get("authors") or ["anon"])[0].split()[-1])) or "anon"
    return f"{a}{r.get('year') or ''}_{i}"
with open("references.bib","w",encoding="utf-8") as f:
    for i,r in enumerate(recs):
        f.write("@article{%s,\n  title={{%s}},\n  author={%s},\n  journal={%s},\n  year={%s},\n  doi={%s},\n  note={%s}\n}\n\n"%(
            bibkey(r,i), r["title"], " and ".join(r.get("authors") or []), r.get("venue") or "",
            r.get("year") or "", r.get("doi") or "", ("PDF: "+r["file"]) if r.get("file") else "no open-access copy found"))
L=["# Sybil Attacks in VANETs — Literature Corpus","",
   f"Built {len(recs)} papers · **{len({r['file'] for r in got})} PDFs downloaded** · {len(miss)} without a free copy.","",
   "| file | what |","|---|---|","| `pdfs/` | downloaded PDFs (`YEAR_FirstAuthor_Title.pdf`) |",
   "| `index.csv` | full table: every paper, topics, DOI, link, whether the PDF is local |",
   "| `references.bib` | BibTeX for all of them |","| `meta/all.json` | raw metadata |","",
   "Sources searched: OpenAlex, Unpaywall, Semantic Scholar, arXiv, OpenAIRE, HAL, Internet Archive Wayback, publisher OA sites (MDPI, Springer Open, IOP, De Gruyter, Hindawi), author home pages.","",
   "## Topic breakdown",""]
from collections import Counter
c=Counter(); cg=Counter()
for r in recs:
    for k in r["cats"]:
        c[k]+=1
        if r.get("file"): cg[k]+=1
L+=["| topic | papers | PDFs held |","|---|---|---|"]
for k,v in c.most_common(): L.append(f"| {k} | {v} | {cg[k]} |")
L+=["","## Most-cited papers in the corpus",""]
for r in recs[:30]:
    mark="✅" if r.get("file") else "❌"
    L.append(f"- {mark} **{r.get('cites') or 0} cites** · {r.get('year')} · {r['title']}  \n  *{r.get('venue') or 'n/a'}*" + (f" · `{r['file']}`" if r.get("file") else (f" · doi:{r['doi']}" if r.get("doi") else "")))
L+=["","## Downloaded (full list)",""]
for r in sorted(got,key=lambda r:-(r.get("year") or 0)):
    L.append(f"- **{r.get('year')}** · {r['title']} — *{r.get('venue') or 'n/a'}* · {r.get('cites') or 0} cites · `{r['file']}`")
L+=["","## No free copy found — request or buy",""]
for r in sorted(miss,key=lambda r:-(r.get("cites") or 0)):
    d=f" · https://doi.org/{r['doi']}" if r.get("doi") else ""
    L.append(f"- **{r.get('year')}** · {r['title']} — *{r.get('venue') or 'n/a'}* · {r.get('cites') or 0} cites{d}")
open("README.md","w",encoding="utf-8").write("\n".join(L))
print(f"papers={len(recs)} unique_pdfs={len({r['file'] for r in got})} linked={len(got)} missing={len(miss)}")
