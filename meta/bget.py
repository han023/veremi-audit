import sys,os,base64
from playwright.sync_api import sync_playwright
url,out=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    br=p.chromium.launch(headless=True)
    ctx=br.new_context(accept_downloads=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    pg=ctx.new_page(); ok=False
    try:
        with pg.expect_download(timeout=15000) as dl:
            try: pg.goto(url,timeout=60000,wait_until="commit")
            except Exception: pass
        dl.value.save_as(out); ok=True
    except Exception:
        try:
            b=pg.evaluate("""async () => { const r=await fetch(location.href,{credentials:'include'}); const b=new Uint8Array(await r.arrayBuffer());
              if(b[0]!==0x25||b[1]!==0x50) return null; let s=''; const C=8192; for(let i=0;i<b.length;i+=C) s+=String.fromCharCode.apply(null,b.subarray(i,i+C)); return btoa(s); }""")
            if b:
                open(out,'wb').write(base64.b64decode(b)); ok=True
        except Exception as e: print("ERR",e)
    br.close()
print("OK" if ok and os.path.exists(out) and open(out,'rb').read(4)==b'%PDF' else "FAIL", out, os.path.getsize(out) if os.path.exists(out) else 0)
