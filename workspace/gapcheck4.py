import requests,urllib.parse,time
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"gapcheck/1.0 (mailto:{MAIL})"})
def q(name,query,frm=2024):
    url=("https://api.openalex.org/works?per-page=10&sort=publication_date:desc"
         "&filter=title_and_abstract.search:"+urllib.parse.quote(query)+
         f",from_publication_date:{frm}-01-01&mailto={MAIL}")
    try: j=S.get(url,timeout=60).json()
    except Exception as e: print(name,"ERR",e); return
    print(f"\n=== {name}  [{(j.get('meta') or {}).get('count',0)} works since {frm}]")
    for w in (j.get("results") or [])[:7]:
        v=((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        print(f"    {w.get('publication_date')} c={w.get('cited_by_count'):<4}| {(w.get('title') or '')[:78]} | {v[:30]}")
    time.sleep(0.3)
# newest-first checks on the gaps the plan depends on
q("G1 Sybil benchmark/comparison","sybil AND (vanet OR v2x) AND (benchmark OR comparison OR evaluation OR reproduc)")
q("G3 adversarial evasion vehicular detection","(adversarial OR evasion) AND (v2x OR vanet OR vehicular) AND (misbehavior OR intrusion OR sybil)")
q("G4 detectability bounds/limits","(detectability OR identifiability OR 'fundamental limit' OR 'theoretical bound') AND (sybil OR 'position falsification' OR spoofing)")
q("G5 SCMS pseudonym concurrency","(scms OR 'pseudonym certificate' OR '1609.2' OR 'c-its') AND (sybil OR concurrency OR misuse OR revocation)")
q("G6 embedded latency MBD","(v2x OR vanet) AND (misbehavior OR sybil OR intrusion) AND (latency OR real-time) AND (embedded OR hardware OR obu)")
q("G7 RSSI Sybil dataset","(rssi OR 'signal strength') AND (sybil OR misbehavior) AND (dataset OR benchmark)")
q("VeReMi newest usage","veremi")
