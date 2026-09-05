"""Verify each claimed gap against the ADJACENT literature (not just the Sybil corpus)."""
import requests,urllib.parse,time,json,sys
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"gapcheck/1.0 (mailto:{MAIL})"})
PROBES={
 "A. adversarial ML vs V2X/VANET misbehavior detection":'(adversarial) AND (vehicular OR vanet OR v2x) AND ("misbehavior detection" OR "intrusion detection" OR "attack detection")',
 "B. adversarial examples vs Sybil detection (any domain)":'adversarial AND "sybil detection"',
 "C. collective/cooperative perception attacks":'("collective perception" OR "cooperative perception") AND (attack OR misbehavior OR spoofing OR security)',
 "D. Sybil in cooperative perception":'sybil AND ("collective perception" OR "cooperative perception")',
 "E. VeReMi benchmark / comparative evaluation":'veremi AND (benchmark OR comparison OR evaluation OR reproducib)',
 "F. federated learning poisoning in vehicular networks":'"federated learning" AND (vehicular OR v2x OR vanet) AND (poisoning OR sybil OR "malicious clients")',
 "G. SCMS / 1609.2 misbehavior reporting & revocation":'("misbehavior detection" OR "misbehaviour detection") AND (scms OR "1609.2" OR "security credential management" OR "pseudonym certificate")',
 "H. reproducibility / benchmark crisis in vehicular security":'(reproducib OR benchmark) AND (vehicular OR vanet OR v2x) AND security',
 "I. Sybil + LLM / foundation models":'sybil AND ("large language model" OR llm OR "foundation model")',
 "J. Sybil + digital twin":'sybil AND "digital twin"',
 "K. Sybil + post-quantum":'sybil AND ("post-quantum" OR "quantum-resistant" OR lattice-based)',
 "L. detection-theoretic bounds for Sybil":'sybil AND (bound OR "detection theory" OR "fundamental limit" OR identifiability)',
 "M. privacy-utility tradeoff quantified in VANET":'(vanet OR v2x) AND ("differential privacy" OR "privacy budget" OR "anonymity set") AND (detection OR misbehavior)',
 "N. graph neural networks for VANET misbehavior":'("graph neural" OR gnn) AND (vanet OR v2x OR vehicular) AND (misbehavior OR attack OR sybil)',
 "O. crowdsensing / navigation-app Sybil (Waze-type)":'sybil AND (crowdsensing OR "crowdsourced navigation" OR waze OR "navigation service")',
 "P. RSSI dataset for vehicular security":'(rssi OR "received signal strength") AND (vanet OR v2x OR vehicular) AND dataset',
 "Q. transformer / sequence models for V2X misbehavior":'(transformer OR lstm OR "sequence model") AND (v2x OR vanet) AND (misbehavior OR "attack detection")',
 "R. real-world V2X security testbed measurements":'(testbed OR "field trial" OR "real-world measurement") AND (v2x OR vanet) AND (security OR attack)',
}
out={}
for name,q in PROBES.items():
    url=("https://api.openalex.org/works?per-page=10&sort=cited_by_count:desc"
         "&filter=title_and_abstract.search:"+urllib.parse.quote(q)+f"&mailto={MAIL}")
    try:
        r=S.get(url,timeout=60); j=r.json()
    except Exception as e:
        print(name,"ERR",e); continue
    n=(j.get("meta") or {}).get("count",0)
    rows=[]
    for w in (j.get("results") or [])[:6]:
        rows.append((w.get("publication_year"),w.get("cited_by_count"),(w.get("title") or "")[:85],
                     ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""))
    out[name]={"count":n,"top":rows}
    print(f"\n=== {name}\n    matching works: {n}")
    for y,c,t,v in rows: print(f"    {c:>5} {y} | {t} | {v[:38]}")
    time.sleep(0.3)
json.dump(out,open("workspace/notes/gapcheck.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
