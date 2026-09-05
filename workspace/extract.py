import os,re,json,sys
from pypdf import PdfReader
os.makedirs("workspace/text",exist_ok=True)
files=sorted(os.listdir("pdfs"))
out={}
for i,f in enumerate(files):
    tp="workspace/text/"+f[:-4]+".txt"
    if os.path.exists(tp) and os.path.getsize(tp)>500:
        out[f]=os.path.getsize(tp); continue
    try:
        rd=PdfReader("pdfs/"+f)
        t=[]
        for pg in rd.pages:
            try: t.append(pg.extract_text() or "")
            except Exception: pass
        txt="\n".join(t)
    except Exception as e:
        txt=""
        print("FAIL",f[:60],type(e).__name__,flush=True)
    open(tp,"w",encoding="utf-8").write(txt)
    out[f]=len(txt)
    if i%10==0: print(i,len(files),flush=True)
json.dump(out,open("workspace/text_sizes.json","w"),indent=1)
short=[k for k,v in out.items() if v<1000]
print("extracted",len(out),"| no/low text:",len(short))
for s in short: print("   ~",s[:70])
