import os,re,json
T="workspace/text"
recs=json.load(open("meta/all.json",encoding="utf-8"))
notes={r["file"]:r for r in json.load(open("workspace/notes/paper_notes.json",encoding="utf-8"))}
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
by={}
for r in recs: by.setdefault(slug(r),r)
def clean(s): return " ".join(s.split())
def sents(txt,pat,n=3,win=260):
    out=[]
    for m in re.finditer(pat,txt,re.I):
        s=clean(txt[max(0,m.start()-90):m.start()+win])
        if len(s)>60: out.append(s)
        if len(out)>=n: break
    return out
cards=[]
for fn in sorted(os.listdir(T)):
    pdf=fn[:-4]+".pdf"; r=by.get(pdf,{}); nt=notes.get(pdf,{})
    txt=open(os.path.join(T,fn),encoding="utf-8",errors="ignore").read()
    body=txt[:60000]
    abstract=(r.get("abstract") or "")[:900]
    if not abstract:
        m=re.search(r'abstract[:\s—-]*(.{200,1200})',body,re.I|re.S)
        abstract=clean(m.group(1)) if m else clean(body[:700])
    card={
      "file":pdf,"year":r.get("year"),"cites":r.get("cites"),"venue":r.get("venue"),
      "title":r.get("title") or pdf,"doi":r.get("doi"),
      "abstract":clean(abstract)[:900],
      "contribution":sents(body,r'we propose|we present|this paper proposes|we introduce|our contribution|in this paper, we',2),
      "evaluation":sents(body,r'simulation results|experimental results|accuracy of|detection rate|false positive|precision and recall|f1[- ]score',2),
      "limits":sents(body,r'future work|limitation|however, our|does not consider|in future|open (?:issue|problem)',2),
      "datasets":nt.get("datasets",""),"simulators":nt.get("simulators",""),"methods":nt.get("methods",""),
    }
    cards.append(card)
cards.sort(key=lambda c:(c["year"] or 0, -(c["cites"] or 0)))
json.dump(cards,open("workspace/notes/cards.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
with open("workspace/notes/cards.md","w",encoding="utf-8") as f:
    for c in cards:
        f.write(f"## {c['year']} — {c['title']}\n")
        f.write(f"*{c['venue'] or 'n/a'}* · {c['cites'] or 0} cites · doi:{c['doi'] or '—'} · `{c['file']}`\n\n")
        f.write(f"**Abstract.** {c['abstract']}\n\n")
        if c["contribution"]: f.write("**Claim.** "+" // ".join(c["contribution"])+"\n\n")
        if c["evaluation"]: f.write("**Eval.** "+" // ".join(c["evaluation"])+"\n\n")
        if c["limits"]: f.write("**Limits/future.** "+" // ".join(c["limits"])+"\n\n")
        f.write(f"**Tech.** methods: {c['methods']} | sim: {c['simulators']} | data: {c['datasets'] or '—'}\n\n---\n\n")
print("cards:",len(cards),"chars:",os.path.getsize("workspace/notes/cards.md"))
