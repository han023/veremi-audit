import json,os,re,base64,shutil
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
# key fragment -> source file
MAP={
 "1424-8220/22/18/6934":".playwright-mcp/sensors-22-06934-v2.pdf",
 "1424-8220/21/4/1063":".playwright-mcp/sensors-21-01063-v2.pdf",
 "1424-8220/22/22/9000":".playwright-mcp/sensors-22-09000-v2.pdf",
 "1424-8220/24/24/8140":".playwright-mcp/sensors-24-08140.pdf",
 "1424-8220/21/10/3538":".playwright-mcp/sensors-21-03538-v2.pdf",
 "2624-800X/6/2/59":".playwright-mcp/jcp-06-00059.pdf",
 "comp-2015-0006":".playwright-mcp/10-1515-comp-2015-0006.pdf",
 "2196-064X-1-4":"springer_2196064X14.b64",
 "1742-6596/1427/1/012009":"iop_marsybil.b64",
}
def load(src):
    if src.endswith(".b64"):
        t=open(src,encoding="utf-8").read().strip().strip('"')
        return base64.b64decode(t)
    return open(src,'rb').read()
done=0
for r in recs:
    blob=(r.get("pdf_url") or "")+" "+(r.get("alt_url") or "")+" "+(r.get("landing") or "")+" "+(r.get("doi") or "")
    for frag,src in MAP.items():
        if frag.lower() in blob.lower() and os.path.exists(src):
            data=load(src)
            if data[:4]==b'%PDF':
                fn="pdfs/"+slug(r); open(fn,'wb').write(data); r["file"]=fn; done+=1
                print("imported:",r["title"][:60])
            break
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("imported",done)
