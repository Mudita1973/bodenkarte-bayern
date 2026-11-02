import json, gzip, base64, re, shutil, os
t=open("template_cz.html",encoding="utf-8").read()
css=re.sub(r"url\([^)]*\)","none",open("/home/claude/bk/package/dist/leaflet.css").read())
js=open("/home/claude/bk/package/dist/leaflet.js").read()
d=json.load(open("data_cz.json"))
gz=base64.b64encode(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(",",":")).encode(),9)).decode()
base=t.replace("/*LEAFLET_CSS*/",css).replace("/*LEAFLET_JS*/",js.replace("</script","<\\/script")).replace("/*DATAGZ*/",gz)
mark='<script>\n"use strict";\nlet D=null;'
assert base.count(mark)==1
lidx=json.load(open("lutiles_index.json"))
pre='<script>const LU_INDEX='+json.dumps(lidx,separators=(",",":"))+';</script>\n'
web=base.replace(mark,pre+'<script>const DETAIL_INDEX='+open("detail_index.json").read()+';</script>\n'+mark)
lut={k:base64.b64encode(open(f"lutiles/{k}.bin","rb").read()).decode() for k in lidx}
det=base.replace(mark,pre+'<script>const LUT='+json.dumps(lut,separators=(",",":"))+';</script>\n<script>const DETAIL='+open("detail_tiles.json").read()+';</script>\n'+mark)
os.makedirs("site",exist_ok=True)
for sub,src in (("detail","detail"),("lu","lutiles")):
    shutil.rmtree("site/"+sub,ignore_errors=True); shutil.copytree(src,"site/"+sub)
open("site/index.html","w",encoding="utf-8").write(web)
open("bodenkarte_westboehmen.html","w",encoding="utf-8").write(web)
open("bodenkarte_westboehmen_detail.html","w",encoding="utf-8").write(det)
print(round(len(web.encode())/1e6,2),"MB web;", round(len(det.encode())/1e6,2),"MB detail")
