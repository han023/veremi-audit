import os,re,json
T="workspace/text"
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
by={}
for r in recs: by.setdefault(slug(r),r)
def clean(s): return " ".join(s.split())
def grab(txt,pat,n=6,win=300):
    out=[]
    for m in re.finditer(pat,txt,re.I):
        seg=clean(txt[m.start():m.start()+win])
        seg=re.split(r'(?<=[.!?]) (?=[A-Z])',seg)
        s=" ".join(seg[:2])[:280]
        if len(s)>40 and s not in out: out.append(s)
        if len(out)>=n: break
    return out
NUM=r'(\d+(?:\.\d+)?)'
def numbers(txt,pat,n=8):
    out=[]
    for m in re.finditer(pat,txt,re.I):
        out.append(clean(m.group(0))[:120])
        if len(out)>=n: break
    return out
deep=[]
for fn in sorted(os.listdir(T)):
    pdf=fn[:-4]+".pdf"; r=by.get(pdf,{})
    txt=open(os.path.join(T,fn),encoding="utf-8",errors="ignore").read()
    d={
      "file":pdf,"year":r.get("year"),"cites":r.get("cites"),"title":r.get("title") or pdf,
      "venue":r.get("venue"),
      "assumptions": grab(txt,r'\b(?:we|it is|our (?:scheme|approach|protocol|system)|the (?:scheme|system|model))\s+assum\w+',5),
      "threat_model": grab(txt,r'(?:attack(?:er)?|threat|adversar\w+)\s+model',3,420),
      "limitations": grab(txt,r'(?:limitation|drawback|shortcoming|does not (?:consider|handle|address|detect)|cannot (?:detect|handle|prevent)|fails? to (?:detect|consider))',6),
      "future_work": grab(txt,r'(?:future work|in the future|future research|future direction|as future|further work|our future)',5,320),
      "baselines": grab(txt,r'(?:compared? (?:with|to|against)|comparison with|outperform\w*)\s+',5,200),
      "n_vehicles": numbers(txt,r'\b\d{2,5}\s*(?:vehicles|nodes|cars)\b'),
      "sim_time": numbers(txt,r'\bsimulation\s+time\s*(?:of|is|=|:)?\s*\d+\s*(?:s|sec|seconds|min|minutes|hours)?',4),
      "beacon_rate": numbers(txt,r'\b\d+(?:\.\d+)?\s*(?:hz|messages?\s*(?:per|/)\s*s(?:ec(?:ond)?)?|beacons?\s*(?:per|/)\s*s)',4),
      "attacker_frac": numbers(txt,r'\b\d{1,3}\s*%\s*(?:of\s*)?(?:attack|malicious|sybil|adversar)',5),
      "claimed_perf": numbers(txt,r'(?:detection rate|accuracy|precision|recall|f1[- ]?score|true positive rate|false positive rate|fpr|tpr)[^.]{0,40}?\b\d{2,3}(?:\.\d+)?\s*%',8),
      "area_km2": numbers(txt,r'\b\d+(?:\.\d+)?\s*(?:km2|km²|square kilometers?|km\s*x\s*\d)',3),
    }
    deep.append(d)
deep.sort(key=lambda x:(x["year"] or 0))
json.dump(deep,open("workspace/notes/deep_extract.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
# stats
import collections
def has(k): return sum(1 for d in deep if d[k])
print("papers:",len(deep))
for k in ["assumptions","threat_model","limitations","future_work","baselines","n_vehicles","beacon_rate","attacker_frac","claimed_perf","area_km2","sim_time"]:
    print(f"  {k:14s} present in {has(k):>3} papers")
