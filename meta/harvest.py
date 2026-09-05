import json, re, time, urllib.parse, sys
import requests

MAIL = "abdullhannan0311@gmail.com"
S = requests.Session()
S.headers.update({"User-Agent": f"sybil-vanet-research/1.0 (mailto:{MAIL})"})

def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', (t or '').lower()).strip()

records = {}   # key -> record

def add(rec):
    k = (rec.get("doi") or "").lower() or norm(rec["title"])[:90]
    if not k: return
    cur = records.get(k)
    if cur:
        for f in ("pdf_url","doi","year","venue","abstract","oa_status","cites"):
            if not cur.get(f) and rec.get(f): cur[f] = rec[f]
        cur["sources"] = sorted(set(cur["sources"]) | set(rec["sources"]))
    else:
        records[k] = rec

# ---------- OpenAlex ----------
OA_QUERIES = [
 'sybil AND (vanet OR vehicular)',
 '"sybil attack" AND "vehicular ad hoc network"',
 '"sybil attack" AND VANET',
 'sybil node detection vehicular network',
 '"sybil attack" AND (V2X OR "internet of vehicles")',
]
def inv2abs(inv):
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))[:1500]

for q in OA_QUERIES:
    cursor = "*"
    while cursor:
        url = ("https://api.openalex.org/works?per-page=200&cursor=" + urllib.parse.quote(cursor) +
               "&filter=title_and_abstract.search:" + urllib.parse.quote(q) +
               f"&mailto={MAIL}")
        r = S.get(url, timeout=60)
        if r.status_code != 200:
            print("OA err", r.status_code, q, file=sys.stderr); break
        j = r.json()
        for w in j.get("results", []):
            title = w.get("title") or ""
            nt = norm(title)
            if "sybil" not in nt: continue
            loc = w.get("best_oa_location") or {}
            pdf = loc.get("pdf_url") or (w.get("open_access") or {}).get("oa_url")
            if not pdf:
                for l in w.get("locations", []) or []:
                    if l.get("pdf_url"): pdf = l["pdf_url"]; break
            add({
              "title": title.strip(),
              "doi": (w.get("doi") or "").replace("https://doi.org/",""),
              "year": w.get("publication_year"),
              "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
              "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:12],
              "cites": w.get("cited_by_count"),
              "oa_status": (w.get("open_access") or {}).get("oa_status"),
              "pdf_url": pdf,
              "landing": (w.get("primary_location") or {}).get("landing_page_url"),
              "abstract": inv2abs(w.get("abstract_inverted_index")),
              "sources": ["openalex"],
            })
        cursor = (j.get("meta") or {}).get("next_cursor")
        if not j.get("results"): break
        time.sleep(0.2)
    print("after OA query:", q, len(records), file=sys.stderr)

json.dump(list(records.values()), open("meta/openalex.json","w",encoding="utf-8"), indent=1, ensure_ascii=False)
print("TOTAL", len(records))
