import json, gzip, base64, re, shutil, os
t=open("template_bw.html",encoding="utf-8").read()
css=re.sub(r"url\([^)]*\)","none",open("/home/claude/bk/package/dist/leaflet.css").read())
js=open("/home/claude/bk/package/dist/leaflet.js").read()
d=json.load(open("data_bw.json"))
gz=base64.b64encode(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(",",":")).encode(),9)).decode()
base=t.replace("/*LEAFLET_CSS*/",css).replace("/*LEAFLET_JS*/",js.replace("</script","<\\/script")).replace("/*DATAGZ*/",gz)
mark='<script>\n"use strict";\nlet D=null;'
assert base.count(mark)==1
web=base.replace(mark,'<script>const DETAIL_INDEX='+open("detail_index.json").read()+';</script>\n'+mark)
det=base.replace(mark,'<script>const DETAIL='+open("detail_tiles.json").read()+';</script>\n'+mark)
os.makedirs("site",exist_ok=True)
shutil.rmtree("site/detail",ignore_errors=True); shutil.copytree("detail","site/detail")
open("site/index.html","w",encoding="utf-8").write(web)
open("bodenkarte_bw.html","w",encoding="utf-8").write(web)
open("bodenkarte_bw_detail.html","w",encoding="utf-8").write(det)
print(round(len(web.encode())/1e6,2),"MB web;", round(len(det.encode())/1e6,2),"MB detail")
