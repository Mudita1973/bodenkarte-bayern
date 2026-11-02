import json, glob, numpy as np, geopandas as gpd, shapely, os, collections
from shapely.geometry import Polygon
L=[];G=[]
for f in glob.glob("zab3/z*.json"):
    j=json.load(open(f))
    for rings in j["f"]:
        if len(rings[0])<4: continue
        try: p=Polygon(rings[0],[r for r in rings[1:] if len(r)>=4])
        except Exception: continue
        L.append(j["l"]); G.append(p)
g=gpd.GeoDataFrame({"l":L},geometry=G,crs=32633)
g["geometry"]=shapely.make_valid(g.geometry.values)
g=g[~g.geometry.is_empty]
reg=gpd.read_file("kraje.geojson").to_crs(32633).union_all().buffer(800)
g=g[g.intersects(reg)].to_crs(32632)
print("Flächen",len(g))
T=4000; b=g.total_bounds
ix0,iy0,ix1,iy1=int(b[0]//T),int(b[1]//T),int(b[2]//T),int(b[3]//T)
tiles=[]
for ix in range(ix0,ix1+1):
    for iy in range(iy0,iy1+1): tiles.append((ix,iy,shapely.box(ix*T,iy*T,(ix+1)*T,(iy+1)*T)))
tg=gpd.GeoDataFrame({"ix":[t[0] for t in tiles],"iy":[t[1] for t in tiles]},geometry=[t[2] for t in tiles],crs=32632)
reg32=gpd.GeoSeries([reg],crs=32633).to_crs(32632).iloc[0]
tg=tg[tg.intersects(reg32)]
j=gpd.sjoin(g,tg,predicate="intersects")
# Gebäude (ZABAGED-Layer 99): je Kachel puffern (6 m), vereinigen, zurücknehmen (-4 m) -> bebaute Fläche
BG=[]
for f in sorted(glob.glob("zab99/z*.json")):
    for rings in json.load(open(f))["f"]:
        if len(rings[0])>=4:
            try: BG.append(Polygon(rings[0]))
            except Exception: pass
bg=gpd.GeoDataFrame(geometry=BG,crs=32633); bg=bg[bg.geometry.is_valid|True]
bg=bg[bg.intersects(reg)].to_crs(32632); print("Gebäude",len(bg))
jb=gpd.sjoin(bg,tg,predicate="intersects"); BUILT={}
for (ix,iy),grp in jb.groupby(["ix","iy"]):
    x0,y0=ix*T,iy*T
    u=shapely.union_all(shapely.buffer(grp.geometry.values,6,quad_segs=2))
    u=shapely.buffer(u,-4,quad_segs=2)
    u=shapely.simplify(shapely.clip_by_rect(u,x0,y0,x0+T,y0+T),1.5)
    if u is not None and not u.is_empty: BUILT[(ix,iy)]=u
print("Kacheln mit Gebäuden",len(BUILT))
def zz(n): return (n<<1)^(n>>63) if n<0 else n<<1
def vi(buf,n):
    while True:
        b=n&0x7f; n>>=7
        if n: buf.append(b|0x80)
        else: buf.append(b); return
idx=[]; tot=0
for (ix,iy),grp in j.groupby(["ix","iy"]):
    x0,y0=ix*T,iy*T
    cl=shapely.clip_by_rect(grp.geometry.values,x0,y0,x0+T,y0+T)
    buf=bytearray(); feats=[]
    for l,geom in zip(grp.l.values,cl):
        if geom is None or geom.is_empty: continue
        polys=[p for p in getattr(geom,"geoms",[geom]) if p.geom_type=="Polygon" and p.area>=50]
        if not polys: continue
        fb=bytearray(); vi(fb,int(l)); np_=0; pb=bytearray()
        for p in polys:
            rings=[p.exterior]+list(p.interiors); rb=bytearray(); nr=0
            for r in rings:
                c=np.round(np.asarray(r.coords)[:-1]-[x0,y0]).astype(np.int64)
                keep=np.ones(len(c),bool); keep[1:]=np.any(c[1:]!=c[:-1],axis=1); c=c[keep]
                if len(c)<3: continue
                d=np.diff(np.vstack([[0,0],c]),axis=0)
                vi(rb,len(c))
                for dx,dy in d: vi(rb,zz(int(dx))); vi(rb,zz(int(dy)))
                nr+=1
            if nr: vi(pb,nr); pb+=rb; np_+=1
        if np_: vi(fb,np_); fb+=pb; feats.append(fb)
    bu=BUILT.get((ix,iy))
    if bu is not None:
        polys=[p for p in getattr(bu,"geoms",[bu]) if p.geom_type=="Polygon" and p.area>=150]
        if polys:
            fb=bytearray(); vi(fb,99); np_=0; pb=bytearray()
            for p in polys:
                rb=bytearray(); nr=0
                for r in [p.exterior]+list(p.interiors):
                    c=np.round(np.asarray(r.coords)[:-1]-[x0,y0]).astype(np.int64)
                    keep=np.ones(len(c),bool); keep[1:]=np.any(c[1:]!=c[:-1],axis=1); c=c[keep]
                    if len(c)<3: continue
                    d=np.diff(np.vstack([[0,0],c]),axis=0); vi(rb,len(c))
                    for dx,dy in d: vi(rb,zz(int(dx))); vi(rb,zz(int(dy)))
                    nr+=1
                if nr: vi(pb,nr); pb+=rb; np_+=1
            if np_: vi(fb,np_); fb+=pb; feats.append(fb)
    if not feats: continue
    vi(buf,len(feats))
    for fb in feats: buf+=fb
    open(f"lutiles3/{ix}_{iy}.bin","wb").write(bytes(buf)); idx.append(f"{ix}_{iy}"); tot+=len(buf)
json.dump(idx,open("lutiles3_index.json","w"))
print("Kacheln",len(idx),"MB",round(tot/1e6,2),"max KB",max(os.path.getsize("lutiles3/"+k+".bin") for k in idx)//1000)
