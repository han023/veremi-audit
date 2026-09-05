import json,os,re,csv
recs=json.load(open("meta/all.json",encoding="utf-8"))
# re-attach files present on disk
have={f for f in os.listdir("pdfs")} if os.path.isdir("pdfs") else set()
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"])
    a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
for r in recs:
    s=slug(r)
    r["file"]="pdfs/"+s if s in have else None
def veh(r):
    t=((r.get("title") or "")+" "+(r.get("abstract") or "")+" "+(r.get("venue") or "")).lower()
    return any(k in t for k in ["vanet","vehic","v2x","v2v","internet of vehicles","platoon","roadside","rsu","traffic","driving"])
recs=[r for r in recs if veh(r)]
recs.sort(key=lambda r:(-(r.get("year") or 0), -(r.get("cites") or 0)))
got=[r for r in recs if r.get("file")]; miss=[r for r in recs if not r.get("file")]

with open("index.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["have_pdf","year","cites","title","authors","venue","doi","oa_status","file","pdf_url","landing"])
    for r in recs:
        w.writerow(["YES" if r.get("file") else "", r.get("year"), r.get("cites"), r["title"],
                    "; ".join(r.get("authors") or []), r.get("venue") or "", r.get("doi") or "",
                    r.get("oa_status") or "", r.get("file") or "", r.get("pdf_url") or "", r.get("landing") or ""])

def bib(r,i):
    key=re.sub(r'\W','',((r.get("authors") or ["anon"])[0].split()[-1]))+str(r.get("year") or "")+str(i)
    au=" and ".join(r.get("authors") or [])
    return ("@article{%s,\n  title={%s},\n  author={%s},\n  journal={%s},\n  year={%s},\n  doi={%s},\n  note={%s}\n}\n"
            % (key, r["title"].replace('{','').replace('}',''), au, r.get("venue") or "", r.get("year") or "", r.get("doi") or "",
               ("local file: "+r["file"]) if r.get("file") else "paywalled"))
open("references.bib","w",encoding="utf-8").write("".join(bib(r,i) for i,r in enumerate(recs)))

L=["# Sybil Attacks in VANETs — Literature Corpus","",
   f"- Total papers found: **{len(recs)}**",
   f"- PDFs downloaded (open access): **{len(got)}**",
   f"- Not downloadable (paywalled / no OA copy): **{len(miss)}**","",
   "Sources: OpenAlex, Unpaywall, arXiv, OpenAIRE. Files in `pdfs/`, full table in `index.csv`, citations in `references.bib`.","",
   "## Downloaded",""]
for r in got:
    L.append(f"- **{r.get('year')}** · {r['title']}  \n  {', '.join((r.get('authors') or [])[:4])} · *{r.get('venue') or 'n/a'}* · cites {r.get('cites') or 0}  \n  `{r['file']}`")
L += ["","## Paywalled / no free copy found",""]
for r in miss:
    doi=f" · doi:{r['doi']}" if r.get("doi") else ""
    L.append(f"- **{r.get('year')}** · {r['title']} · *{r.get('venue') or 'n/a'}* · cites {r.get('cites') or 0}{doi}")
open("README.md","w",encoding="utf-8").write("\n".join(L))
print("papers",len(recs),"downloaded",len(got),"missing",len(miss))
