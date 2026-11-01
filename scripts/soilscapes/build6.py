import json, gzip, base64, re, shutil, os
t=open("template7.html").read()
css=re.sub(r"url\([^)]*\)","none",open("package/dist/leaflet.css").read())
js=open("package/dist/leaflet.js").read()
d=json.load(open("data4.json")); d["kreise"]=json.load(open("kreise.json")); d["ov"]=json.load(open("ov.json"))
gz=base64.b64encode(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(",",":")).encode(),9)).decode()
base=t.replace("/*LEAFLET_CSS*/",css).replace("/*LEAFLET_JS*/",js.replace("</script","<\\/script")).replace("/*DATAGZ*/",gz)
mark='<script>\n"use strict";\nlet D=null;'
assert base.count(mark)==1
idx=open("detail_index.json").read()
web=base.replace(mark,'<script>const DETAIL_INDEX='+idx+';</script>\n'+mark)
det=base.replace(mark,'<script>const DETAIL='+open("detail_tiles.json").read()+';</script>\n'+mark)
os.makedirs("site",exist_ok=True); shutil.rmtree("site/detail",ignore_errors=True); shutil.copytree("detail","site/detail")
open("site/index.html","w").write(web)
open("bodenkarte_v7.html","w").write(web)          # Ordner: normale Datei (Detail nur online)
open("bodenkarte_v7_detail.html","w").write(det)   # Ordner: Detail eingebettet
print(round(len(web)/1e6,2),"MB web;", round(len(det)/1e6,2),"MB detail")
