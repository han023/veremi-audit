import requests,urllib.parse,time,re
MAIL="abdullhannan0311@gmail.com"
S=requests.Session(); S.headers.update({"User-Agent":f"gapcheck/1.0 (mailto:{MAIL})"})
def inv2abs(inv,limit=1100):
    if not inv: return ""
    pos={}
    for w,idxs in inv.items():
        for i in idxs: pos[i]=w
    return " ".join(pos[i] for i in sorted(pos))[:limit]
def probe(name,query,frm=None,n=6,sort="cited_by_count:desc"):
    f="title_and_abstract.search:"+urllib.parse.quote(query)
    if frm: f+=f",from_publication_date:{frm}-01-01"
    j=S.get(f"https://api.openalex.org/works?per-page=8&sort={sort}&filter={f}&mailto={MAIL}",timeout=60).json()
    print(f"\n=== {name} [{(j.get('meta') or {}).get('count',0)}]")
    for w in (j.get("results") or [])[:n]:
        v=((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        print(f"   {w.get('publication_year')} c={w.get('cited_by_count'):<4}| {(w.get('title') or '')[:76]} | {v[:28]}")
    time.sleep(0.3)
def deep(title_query,label):
    j=S.get("https://api.openalex.org/works",params={"search":title_query,"per-page":3,"mailto":MAIL},timeout=60).json()
    for w in (j.get("results") or [])[:1]:
        print(f"\n--- {label}\n    {w.get('title')} ({w.get('publication_year')}) cites={w.get('cited_by_count')}")
        print("    DOI:",w.get("doi"))
        a=inv2abs(w.get("abstract_inverted_index"))
        print("    ABSTRACT:",a[:900] if a else "(none)")
    time.sleep(0.3)
# corrected domain-constrained probes
probe("G4 detectability bounds (vehicular-constrained)",'(vanet OR v2x OR vehicular) AND (sybil OR "position falsification") AND (bound OR limit OR detectability OR identifiability OR "information-theoretic")')
probe("G5 SCMS concurrency (vehicular-constrained)",'(vanet OR v2x OR "c-its" OR vehicular) AND ("pseudonym certificate" OR scms OR "1609.2") AND (sybil OR concurrent OR misuse)')
# new works flagged by the recency sweep
deep("Mobility Discloses Genuinity Robust Machine Learning Sybil Attack Detection","NEW 2025 IoT-J Sybil detector")
deep("Evaluating Zero-Day Generalisation in VANET Detection","NEW 2026 zero-day generalisation")
deep("VeReMi-Graph temporal attributed graph dataset vehicular misbehaviour","NEW 2026 VeReMi-Graph dataset")
deep("SHAVA open-source Python framework interpretable intrusion detection vehicular","NEW 2026 SHAVA framework")
# what the neighbouring surveys claim as open
deep("Survey Machine Learning-Based Misbehavior Detection Systems 5G and Beyond Vehicular Networks","SURVEY COMST 2023")
deep("Advancing Intrusion Detection in V2X Networks Comprehensive Survey Machine Learning","SURVEY TITS 2025")
deep("Misbehavior Detection With Collective Perception in V2X Networks A Survey","SURVEY CP-MBD 2025")
deep("SixPack Abusing ABS to avoid Misbehavior detection in VANETs","PRIOR ART SixPack 2021")
deep("VeReMi Extension Dataset for Comparable Evaluation of Misbehavior Detection","VeReMi Extension paper")
