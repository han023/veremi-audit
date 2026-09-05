import requests,urllib.parse,time,json
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"gapcheck/1.0 (mailto:{MAIL})"})
PROBES={
 "1. Sybil-specific comparative benchmark/reproduction":'sybil AND (vanet OR v2x OR vehicular) AND (benchmark OR "comparative evaluation" OR reproduc OR "head-to-head")',
 "2. evasion / adaptive attacker vs vehicular MBD":'(evasion OR "adaptive attacker" OR "adaptive adversary" OR "evade detection") AND (vanet OR v2x OR vehicular) AND (misbehavior OR "attack detection" OR ids)',
 "3. MBD latency/energy on embedded automotive hardware":'(misbehavior OR "attack detection" OR ids) AND (v2x OR vanet) AND (latency OR "real-time" OR energy) AND (embedded OR obu OR "raspberry pi" OR jetson OR hardware)',
 "4. detection limits / bounds for position falsification":'("position falsification" OR "location spoofing" OR sybil) AND (v2x OR vanet) AND ("theoretical bound" OR "fundamental limit" OR detectability OR identifiability)',
 "5. misbehavior detection surveys 2024-2026":'"misbehavior detection" AND (vehicular OR v2x) AND survey',
 "6. cross-dataset / generalization of vehicular IDS":'(vanet OR v2x OR vehicular) AND (misbehavior OR intrusion) AND (generalization OR "cross-dataset" OR "domain shift" OR transferability)',
 "7. VeReMi limitations / criticism":'veremi AND (limitation OR shortcoming OR critique OR realistic)',
 "8. Sybil attacks on platooning / CACC":'sybil AND (platoon OR cacc OR "cooperative adaptive cruise")',
 "9. attacker economics / cost model V2X security":'(v2x OR vanet OR vehicular) AND security AND ("cost model" OR "attacker cost" OR "economic analysis" OR game-theoretic)',
 "10. RSU-density / deployment sensitivity of detection":'(vanet OR v2x) AND (sybil OR misbehavior) AND ("rsu density" OR "infrastructure density" OR "sparse deployment" OR penetration rate)',
}
for name,q in PROBES.items():
    url=("https://api.openalex.org/works?per-page=8&sort=cited_by_count:desc"
         "&filter=title_and_abstract.search:"+urllib.parse.quote(q)+f"&mailto={MAIL}")
    try: j=S.get(url,timeout=60).json()
    except Exception as e:
        print(name,"ERR",e); continue
    print(f"\n=== {name}  [{(j.get('meta') or {}).get('count',0)} works]")
    for w in (j.get("results") or [])[:6]:
        v=((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        print(f"    {w.get('cited_by_count'):>4} {w.get('publication_year')} | {(w.get('title') or '')[:80]} | {v[:34]}")
    time.sleep(0.3)
