import os,re,json,csv
T="workspace/text"
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
by_file={}
for r in recs:
    by_file.setdefault(slug(r),r)
URL=re.compile(r'(https?://[^\s<>")\]]+|www\.[^\s<>")\]]+|github\.com/[\w.\-/]+)',re.I)
CODE=re.compile(r'github|gitlab|bitbucket|sourceforge|zenodo|codeocean|code ocean|figshare|ieee-dataport|dataport|kaggle|colab|/code|source code|our code|code is available|implementation is available',re.I)
DATA={
 "VeReMi":r'veremi',
 "VeReMi Extension":r'veremi[- ]extension',
 "NGSIM":r'\bngsim\b|next generation simulation',
 "LuST (Luxembourg)":r'\blust\b|luxembourg sumo',
 "TAPASCologne":r'tapas[- ]?cologne|cologne trace',
 "CRAWDAD":r'crawdad',
 "Kaggle dataset":r'kaggle',
 "IEEE DataPort":r'dataport',
 "Mobility trace (San Francisco cabs)":r'cabspotting|san francisco.{0,20}taxi',
 "F2MD":r'\bf2md\b|framework for misbehavior detection',
 "CICIDS/NSL-KDD (generic IDS sets)":r'nsl-?kdd|cicids|kdd ?cup|unsw-?nb15',
}
SIM={
 "NS-2":r'\bns-?2\b',"NS-3":r'\bns-?3\b',"OMNeT++":r'omnet',"SUMO":r'\bsumo\b',
 "Veins":r'\bveins\b',"MATLAB":r'matlab',"GloMoSim":r'glomosim',"OPNET":r'opnet',
 "VanetMobiSim":r'vanetmobisim',"Python/sklearn/TF":r'scikit-learn|tensorflow|pytorch|keras',
}
METH={
 "RSSI/PHY":r'rssi|received signal strength|signal strength|channel state|doppler|angle of arrival',
 "Position/trajectory":r'trajector|position verif|location verif|footprint|mobility pattern|driving pattern',
 "Crypto/PKI/pseudonym":r'pseudonym|public key|certificat|digital signature|ecdsa|elliptic curve|zero[- ]knowledge',
 "ML/DL":r'machine learning|deep learn|neural network|\bsvm\b|k-?nn|random forest|clustering|classifier|federated learning|reinforcement learning',
 "Blockchain":r'blockchain|smart contract|distributed ledger|proof of',
 "Trust/reputation":r'trust value|reputation|belief|dempster',
 "RSU-assisted":r'road ?side unit|\brsu\b',
 "Timestamp series":r'timestamp series|time ?stamp',
 "Fog/edge/cloud":r'fog comput|edge comput|cloud comput',
}
rows=[]
for fn in sorted(os.listdir(T)):
    txt=open(os.path.join(T,fn),encoding="utf-8",errors="ignore").read()
    low=txt.lower()
    pdf=fn[:-4]+".pdf"
    r=by_file.get(pdf,{})
    urls=set()
    for m in URL.finditer(txt):
        u=m.group(0).rstrip('.,;')
        if CODE.search(u): urls.add(u)
    code_ctx=[]
    for m in re.finditer(r'[^.]{0,120}(source code|code is available|our code|implementation is available|github|gitlab|zenodo|code ocean|figshare)[^.]{0,160}',txt,re.I):
        s=" ".join(m.group(0).split())
        if len(s)>25: code_ctx.append(s[:260])
    ds=[k for k,p in DATA.items() if re.search(p,low)]
    sims=[k for k,p in SIM.items() if re.search(p,low)]
    meths=[k for k,p in METH.items() if re.search(p,low)]
    rows.append({"file":pdf,"year":r.get("year"),"cites":r.get("cites"),"title":r.get("title") or pdf,
                 "venue":r.get("venue"),"doi":r.get("doi"),
                 "code_urls":" | ".join(sorted(urls))[:600],
                 "code_mentions":" ;; ".join(code_ctx[:3])[:700],
                 "datasets":", ".join(ds),"simulators":", ".join(sims),"methods":", ".join(meths),
                 "chars":len(txt)})
rows.sort(key=lambda r:(r["year"] or 0))
with open("workspace/notes/paper_notes.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(rows,open("workspace/notes/paper_notes.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("papers mined:",len(rows))
print("with code URL:",sum(1 for r in rows if r["code_urls"]))
print("with code mention:",sum(1 for r in rows if r["code_mentions"]))
from collections import Counter
c=Counter()
for r in rows:
    for d in r["datasets"].split(", "):
        if d: c[d]+=1
print("datasets:",c.most_common())
s=Counter()
for r in rows:
    for x in r["simulators"].split(", "):
        if x: s[x]+=1
print("simulators:",s.most_common())
