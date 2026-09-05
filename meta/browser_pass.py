import json,os,re,sys,base64
from playwright.sync_api import sync_playwright
recs=json.load(open("meta/all.json",encoding="utf-8"))
def slug(r):
    t=re.sub(r'[^A-Za-z0-9 ]+','',r["title"])[:90].strip().replace(' ','_')
    a=(r.get("authors") or ["anon"]); a=re.sub(r'[^A-Za-z]','',a[0].split()[-1]) if a else "anon"
    return f"{r.get('year') or 'nd'}_{a or 'anon'}_{t}.pdf"
todo=[r for r in recs if not r.get("file") and (r.get("pdf_url") or r.get("alt_url") or r.get("landing"))]
todo.sort(key=lambda r:-(r.get("cites") or 0))
LIM=int(sys.argv[1]) if len(sys.argv)>1 else 60
OFF=int(sys.argv[2]) if len(sys.argv)>2 else 0
todo=todo[OFF:OFF+LIM]
print("browser pass on",len(todo),flush=True)
ok=0
with sync_playwright() as p:
    br=p.chromium.launch(headless=True)
    ctx=br.new_context(accept_downloads=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    page=ctx.new_page()
    for r in todo:
        fn=os.path.join("pdfs",slug(r))
        if os.path.exists(fn) and os.path.getsize(fn)>15000: continue
        urls=[u for u in (r.get("pdf_url"),r.get("alt_url"),r.get("landing")) if u]
        got=False
        for u in urls:
            if got: break
            try:
                with page.expect_download(timeout=8000) as dl:
                    try: page.goto(u,timeout=45000,wait_until="commit")
                    except Exception: pass
                d=dl.value; d.save_as(fn)
                if os.path.getsize(fn)>15000 and open(fn,'rb').read(4)==b'%PDF': got=True
            except Exception:
                pass
            if got: break
            # inline pdf or html: try same-origin fetch of current url + citation_pdf_url
            try:
                cur=page.url
                b64=page.evaluate("""async () => {
                    const grab = async (u) => { const r = await fetch(u,{credentials:'include'}); const b=new Uint8Array(await r.arrayBuffer());
                        if (b[0]!==0x25||b[1]!==0x50) return null; let s=''; const C=8192;
                        for(let i=0;i<b.length;i+=C) s+=String.fromCharCode.apply(null,b.subarray(i,i+C)); return btoa(s); };
                    let out = await grab(location.href);
                    if (out) return out;
                    const m = document.querySelector('meta[name="citation_pdf_url"]');
                    if (m) { try { return await grab(m.content); } catch(e){} }
                    const a = [...document.querySelectorAll('a')].find(x=>/\.pdf|viewcontent|pdfdirect|\/pdf/i.test(x.href));
                    if (a) { try { return await grab(a.href); } catch(e){} }
                    return null; }""")
                if b64:
                    data=base64.b64decode(b64)
                    if data[:4]==b'%PDF' and len(data)>15000:
                        open(fn,'wb').write(data); got=True
            except Exception:
                pass
        if got:
            r["file"]=fn.replace("\\","/"); ok+=1
            print("OK",r.get("cites"),r["title"][:60],flush=True)
        else:
            print("--",r.get("cites"),r["title"][:55],flush=True)
    br.close()
json.dump(recs,open("meta/all.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("BROWSER PASS ok=",ok)
