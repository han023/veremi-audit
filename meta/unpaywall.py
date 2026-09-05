import json,time,sys,requests
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"sybil-vanet-research/1.0 (mailto:{MAIL})"})
recs=json.load(open("meta/all.json",encoding="utf-8"))
todo=[r for r in recs if not r.get("pdf_url") and r.get("doi")]
print("checking",len(todo),"paywalled DOIs on unpaywall",file=sys.stderr)
found=0
for i,r in enumerate(todo):
    try:
        j=S.get(f"https://api.unpaywall.org/v2/{r['doi']}",params={"email":MAIL},timeout=30).json()
    except Exception as e:
        continue
    r["oa_status"]=j.get("oa_status") or r.get("oa_status")
    locs=[l for l in (j.get("oa_locations") or []) if l.get("url_for_pdf")]
    if locs:
        r["pdf_url"]=locs[0]["url_for_pdf"]; r["oa_host"]=locs[0].get("host_type"); found+=1
    elif j.get("best_oa_location",{}) and (j.get("best_oa_location") or {}).get("url"):
        r["landing"]=r.get("landing") or j["best_oa_location"]["url"]
    if i%40==0: print(i,found,file=sys.stderr)
    time.sleep(0.12)
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("new OA pdfs found:",found,"| total with pdf:",sum(1 for r in recs if r.get("pdf_url")))
