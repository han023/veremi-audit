import json,os,re,sys
recs=json.load(open("meta/all.json",encoding="utf-8"))
s2=json.load(open("meta/s2_found.json",encoding="utf-8")) if os.path.exists("meta/s2_found.json") else {}
oaf=json.load(open("meta/openaire_found.json",encoding="utf-8")) if os.path.exists("meta/openaire_found.json") else {}
man=json.load(open("meta/manual.json",encoding="utf-8")) if os.path.exists("meta/manual.json") else {}
have=set(os.listdir("pdfs"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
n=0
for r in recs:
    if slug(r) in have: r["file"]="pdfs/"+slug(r); continue
    r["file"]=None
    alt = man.get(r["title"]) or s2.get((r.get("doi") or "").lower()) or oaf.get(r["title"])
    if alt and alt!=r.get("pdf_url"):
        r["alt_url"]=alt; n+=1
print("records with new alt url:",n)
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
