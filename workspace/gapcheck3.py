import requests,urllib.parse,time,json
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"gapcheck/1.0 (mailto:{MAIL})"})
def q(name,query,n=6):
    url=("https://api.openalex.org/works?per-page=8&sort=cited_by_count:desc"
         "&filter=title_and_abstract.search:"+urllib.parse.quote(query)+f"&mailto={MAIL}")
    try: j=S.get(url,timeout=60).json()
    except Exception as e: print(name,"ERR",e); return
    print(f"\n=== {name}  [{(j.get('meta') or {}).get('count',0)} works]")
    for w in (j.get("results") or [])[:n]:
        v=((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        print(f"    {w.get('cited_by_count'):>4} {w.get('publication_year')} | {(w.get('title') or '')[:82]} | {v[:32]}")
    time.sleep(0.3)
q("A. adversarial examples against VeReMi-trained models",'adversarial AND veremi')
q("B. misbehavior detection for collective perception (CPM)",'("collective perception" OR "cpm") AND ("misbehavior detection" OR "plausibility check" OR "phantom object" OR "ghost object")')
q("C. phantom/ghost object injection attacks",'("phantom vehicle" OR "ghost object" OR "phantom object" OR "object injection") AND (v2x OR autonomous OR perception)')
q("D. Sybil-VANET 2025-2026 newest",'sybil AND (vanet OR v2x OR "internet of vehicles")',8)
q("E. explainable AI for vehicular misbehavior detection",'(explainable OR interpretable OR xai) AND (v2x OR vanet) AND (misbehavior OR intrusion OR attack)')
q("F. certificate/pseudonym misuse detection concurrency",'("concurrent pseudonyms" OR "pseudonym misuse" OR "certificate misuse" OR "simultaneous identities") AND (v2x OR vanet OR c-its)')
q("G. ETSI CPM / CAM standard-compliant security evaluation",'(etsi OR "ts 103 324" OR "en 302 637") AND (security OR misbehavior OR attack) AND (evaluation OR compliance)')
q("H. RSSI/PHY fingerprinting for V2X identity",'(fingerprint OR "rf fingerprinting" OR "physical layer authentication") AND (v2x OR vanet OR vehicular)')
