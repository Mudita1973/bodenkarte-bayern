import json, numpy as np, base64, collections, time
t0=time.time()
g=json.load(open("detail.geojson"))
wr=json.load(open("webraster.json")); kix={k:i for i,k in enumerate(wr["keys"])}
TL=0.1; TW=0.15
def venc(out, v):
    v = (v<<1) if v>=0 else ((-v<<1)-1)
    while True:
        b=v&0x7f; v>>=7
        if v: out.append(b|0x80)
        else: out.append(b); break
tiles=collections.defaultdict(list); nv=0
for f in g["features"]:
    key=f["properties"]["key"]; geom=f["geometry"]
    if geom is None: continue
    polys=geom["coordinates"] if geom["type"]=="MultiPolygon" else [geom["coordinates"]]
    for rings in polys:
        xs=[p[0] for p in rings[0]]; ys=[p[1] for p in rings[0]]
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
        t=(int(cy//TL), int(cx//TW))
        tiles[t].append((kix[key], rings, (min(ys),min(xs),max(ys),max(xs))))
        nv+=sum(len(r) for r in rings)
print("Teile",sum(len(v) for v in tiles.values()),"Kacheln",len(tiles),"Punkte",nv, round(time.time()-t0),"s")
index=[]; blobs=[]; reg=[]
for (ty,tx),items in sorted(tiles.items()):
    reg.append(f"{ty//5}_{tx//5}")
    out=bytearray(); venc(out,len(items))
    bb=[90,180,-90,-180]
    for ki,rings,b in items:
        venc(out,ki); venc(out,len(rings))
        bb=[min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3])]
        for r in rings:
            r=r[:-1]; venc(out,len(r)); px=py=0
            for x,y in r:
                qx=round(x*1e5); qy=round(y*1e5)
                venc(out,qy-py); venc(out,qx-px); py,px=qy,qx
    blobs.append(base64.b64encode(bytes(out)).decode())
    index.append([round(bb[0],4),round(bb[1],4),round(bb[2],4),round(bb[3],4)])
names=sorted(set(reg)); rid=[names.index(r) for r in reg]
js=json.dumps({"i":index,"r":rid,"b":blobs},separators=(",",":"))
open("detail_tiles.json","w").write(js); print(len(js)/1e6,"MB")
import os, shutil
shutil.rmtree("detail",ignore_errors=True); os.makedirs("detail")
for n,name in enumerate(names):
    ts=[t for t,r in enumerate(rid) if r==n]
    open(f"detail/r{n:02d}.json","w").write(json.dumps({"t":ts,"b":[blobs[t] for t in ts]},separators=(",",":")))
json.dump({"i":index,"r":rid,"n":len(names)},open("detail_index.json","w"),separators=(",",":"))
sz=[os.path.getsize(f"detail/r{n:02d}.json") for n in range(len(names))]
print(len(names),"Regionen, max",max(sz)/1e6,"MB, Index",os.path.getsize("detail_index.json")/1e3,"kB")
