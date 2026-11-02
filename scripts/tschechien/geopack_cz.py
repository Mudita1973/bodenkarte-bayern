import json, base64, collections, os, shutil, pandas as pd
u=pd.read_parquet("cz_units2.parquet")
keys=[f"{r.leg}|{r.k}" for r in u.itertuples()]; kix={k:i for i,k in enumerate(keys)}
json.dump(keys,open("keys.json","w"))
def zz(n): return (n<<1)^(n>>63)
def varint(buf,n):
    n=zz(n)
    while True:
        b=n&0x7f; n>>=7
        if n: buf.append(b|0x80)
        else: buf.append(b); break
def topo(fn,merge=False):
    t=json.load(open(fn)); obj=list(t["objects"].values())[0]
    buf=bytearray(); arcs=t["arcs"]; varint(buf,len(arcs))
    for a in arcs:
        varint(buf,len(a))
        for x,y in a: varint(buf,x); varint(buf,y)
    geoms=[g for g in obj["geometries"] if g.get("type")]
    if merge:
        # Flächen gleicher Einheit je 20-km-Zelle bündeln: viel weniger Kartenobjekte, Ausschnitt-Prüfung bleibt wirksam
        sc,tr_=t["transform"]["scale"],t["transform"]["translate"]; grp={}
        for g in geoms:
            for p in (g["arcs"] if g["type"]=="MultiPolygon" else [g["arcs"]]):
                i=p[0][0]; x,y=arcs[i if i>=0 else ~i][0]; cx=int((x*sc[0]+tr_[0])//0.27); cy=int((y*sc[1]+tr_[1])//0.18)
                grp.setdefault((g["properties"]["key"],cx,cy),[]).append(p)
        geoms=[{"type":"MultiPolygon","arcs":v,"properties":{"key":k[0]}} for k,v in grp.items()]
    varint(buf,len(geoms)); feats=[]
    for g in geoms:
        polys=g["arcs"] if g["type"]=="MultiPolygon" else [g["arcs"]]
        varint(buf,len(polys))
        for p in polys:
            varint(buf,len(p))
            for ring in p:
                varint(buf,len(ring))
                for i in ring: varint(buf,i)
        feats.append(kix[g["properties"]["key"]])
    return {"tr":t["transform"],"bin":base64.b64encode(bytes(buf)).decode(),"feat":feats}
ov=topo("ms/ov.topojson"); json.dump(ov,open("ov.json","w"),separators=(",",":"))
gen=topo("ms/gen.topojson",merge=True); json.dump(gen,open("gen.json","w"),separators=(",",":"))
print("ov",len(ov["feat"]),"gen",len(gen["feat"]), os.path.getsize("gen.json")/1e6,"MB")
# Detailkacheln
g=json.load(open("ms/detail.geojson")); TL=0.1; TW=0.15
def venc(out,v):
    v=(v<<1) if v>=0 else ((-v<<1)-1)
    while True:
        b=v&0x7f; v>>=7
        if v: out.append(b|0x80)
        else: out.append(b); break
tiles=collections.defaultdict(list)
for f in g["features"]:
    key=f["properties"]["key"]; geom=f["geometry"]
    if geom is None: continue
    polys=geom["coordinates"] if geom["type"]=="MultiPolygon" else [geom["coordinates"]]
    for rings in polys:
        xs=[p[0] for p in rings[0]]; ys=[p[1] for p in rings[0]]
        tiles[(int(((min(ys)+max(ys))/2)//TL), int(((min(xs)+max(xs))/2)//TW))].append((kix[key],rings,(min(ys),min(xs),max(ys),max(xs))))
index=[]; blobs=[]; reg=[]
for (ty,tx),items in sorted(tiles.items()):
    reg.append(f"{ty//5}_{tx//5}"); out=bytearray(); venc(out,len(items)); bb=[90,180,-90,-180]
    for ki,rings,b in items:
        venc(out,ki); venc(out,len(rings)); bb=[min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3])]
        for r in rings:
            r=r[:-1]; venc(out,len(r)); px=py=0
            for x,y in r:
                qx=round(x*1e5); qy=round(y*1e5); venc(out,qy-py); venc(out,qx-px); py,px=qy,qx
    blobs.append(base64.b64encode(bytes(out)).decode()); index.append([round(v,4) for v in bb])
names=sorted(set(reg)); rid=[names.index(r) for r in reg]
open("detail_tiles.json","w").write(json.dumps({"i":index,"r":rid,"b":blobs},separators=(",",":")))
shutil.rmtree("detail",ignore_errors=True); os.makedirs("detail")
for n,name in enumerate(names):
    ts=[t for t,r in enumerate(rid) if r==n]
    open(f"detail/r{n:02d}.json","w").write(json.dumps({"t":ts,"b":[blobs[t] for t in ts]},separators=(",",":")))
json.dump({"i":index,"r":rid,"n":len(names)},open("detail_index.json","w"),separators=(",",":"))
print(len(names),"Regionen, max",max(os.path.getsize(f"detail/r{n:02d}.json") for n in range(len(names)))/1e6,"MB, Kacheln",len(index), os.path.getsize("detail_tiles.json")/1e6,"MB")
