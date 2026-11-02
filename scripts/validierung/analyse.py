import json, numpy as np, pandas as pd, geopandas as gpd, sys
sys.path.insert(0,"/home/claude/cz"); import pz_cz
rng=np.random.default_rng(1)
T=json.load(open("taxa.json")); grp_of={v["id"]:v["grp"] for v in T.values()}
O=json.load(open("obs.json"))
rows=[]
for name,lst in O.items():
    g="alle" if name=="Fungi" else T[name]["grp"]
    for oid,lat,lng,uid,date,tid,acc in lst: rows.append((oid,lat,lng,uid,date,tid,name,g))
df=pd.DataFrame(rows,columns=["oid","lat","lng","uid","date","tid","art","grp"])
pts=gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.lng,df.lat),crs=4326)
# --- Bayern: Einheit und LfU-Werte, Thünen-Raster
by=gpd.read_parquet("/home/claude/bk/raw.parquet")[["leg","geometry"]]
pb=gpd.sjoin(pts.to_crs(by.crs),by,predicate="within",how="inner").drop(columns="index_right")
U=json.load(open("/home/claude/bk/props5.json"))["units"]
def z(leg): u=U.get(leg); return u.get("z") if u else None
def lfu(zv,A):
    if not zv: return (None,None)
    bF,bN,cF,cN,nfk,kf,s,b,c=zv; bs=(bN if bN is not None else bF) if A else (bF if bF is not None else bN); ca=(cN if cN is not None else cF) if A else (cF if cF is not None else cN)
    sa=bs is not None and bs<20 and (ca is None or ca<0.5); ba=(ca is not None and ca>=0.5) or (bs is not None and bs>=80)
    return (sa,ba) if bs is not None or ca is not None else (None,None)
def bag(zv):
    if not zv or zv[6] is None: return (None,None)
    return (zv[6]>=50, (zv[7]+(zv[8] or 0))>=50)
for src,f in (("LfU Waldwert",lambda zv:lfu(zv,False)),("LfU Acker/Grünland",lambda zv:lfu(zv,True)),("Gestein BAG500",bag)):
    v=[f(z(l)) for l in pb.leg]; pb[src+"|s"]=[a for a,b in v]; pb[src+"|b"]=[b for a,b in v]
m=json.load(open("th30_meta.json")); cls=np.load("th30_cls.npy"); p3=pb.to_crs(3857)
c=((p3.geometry.x-m["x0"])/m["R"]).astype(int).values; r=((m["y1"]-p3.geometry.y)/m["R"]).astype(int).values
ok=(c>=0)&(c<m["W"])&(r>=0)&(r<m["H"]); k=np.full(len(pb),255); k[ok]=cls[r[ok],c[ok]]
pb["Thünen pH 0-30|s"]=np.where(k==255,None,k<=1); pb["Thünen pH 0-30|b"]=np.where(k==255,None,k>=5)
pb["land"]="BY"
# --- Westböhmen
czp=gpd.read_parquet("/home/claude/cz/cz_poly2.parquet")[["ukey","geometry"]]
u2=pd.read_parquet("/home/claude/cz/cz_units2.parquet"); zc={i:pz_cz.pz(r) for i,r in zip(u2.index,u2.itertuples())}
pc=gpd.sjoin(pts.to_crs(czp.crs),czp,predicate="within",how="inner").drop(columns="index_right")
pc["ČGS-Bodenkarte|s"]=[bool(zc[k][0]) for k in pc.ukey]; pc["ČGS-Bodenkarte|b"]=[bool(zc[k][1]) for k in pc.ukey]; pc["land"]="CZ"
def thin(d): # ein Fund je Beobachter, Art und 1-km-Zelle (gegen Häufung an beliebten Stellen)
    d=d.copy(); g=d.to_crs(3035); d["cell"]=(g.geometry.x//1000).astype(int).astype(str)+"_"+(g.geometry.y//1000).astype(int).astype(str)
    return d.drop_duplicates(["uid","tid","cell"])
res=[]
for land,d,srcs in (("Bayern",pb,["LfU Waldwert","LfU Acker/Grünland","Gestein BAG500","Thünen pH 0-30"]),("Westböhmen",pc,["ČGS-Bodenkarte"])):
    d=thin(d); base=d[d.grp=="alle"]
    for src in srcs:
        for g in ("sauer","ueberall","basisch"):
            G=d[d.grp==g]
            for side in ("s","b"):
                col=f"{src}|{side}"; gv=G[col].dropna().astype(bool).values; bv=base[col].dropna().astype(bool).values
                if len(gv)<10 or not len(bv): continue
                pg,p0=gv.mean(),bv.mean()
                bs=[rng.choice(gv,len(gv)).mean()/max(1e-9,rng.choice(bv,len(bv)).mean()) for _ in range(2000)]
                res.append(dict(land=land,quelle=src,gruppe=g,auf={"s":"sauer","b":"basisch"}[side],n=len(gv),anteil_gruppe=round(pg*100,1),anteil_alle=round(p0*100,1),faktor=round(pg/p0,2) if p0 else None,ki_lo=round(np.percentile(bs,2.5),2),ki_hi=round(np.percentile(bs,97.5),2)))
R=pd.DataFrame(res); R.to_csv("ergebnis.tsv",sep="\t",index=False); pd.set_option("display.width",200); print(R.to_string(index=False))
# je Art (Bayern, LfU Waldwert und Thünen; Westböhmen ČGS)
art=[]
for land,d,src in (("Bayern",pb,"LfU Waldwert"),("Bayern",pb,"Thünen pH 0-30"),("Westböhmen",pc,"ČGS-Bodenkarte")):
    d=thin(d); base=d[d.grp=="alle"]; b0s=base[src+"|s"].dropna().astype(bool).mean(); b0b=base[src+"|b"].dropna().astype(bool).mean()
    for a,G in d[d.grp!="alle"].groupby("art"):
        s=G[src+"|s"].dropna().astype(bool); b=G[src+"|b"].dropna().astype(bool)
        if len(s)>=25: art.append(dict(land=land,quelle=src,art=a,gruppe=G.grp.iloc[0],n=len(s),sauer_faktor=round(s.mean()/b0s,2),basisch_faktor=round(b.mean()/b0b,2) if b0b else None))
A=pd.DataFrame(art); A.to_csv("ergebnis_arten.tsv",sep="\t",index=False); print(A.to_string(index=False))
print("Funde nach Ausdünnung:",{k:len(thin(v)) for k,v in (("BY",pb),("CZ",pc))}, "davon Basis:",{k:int((thin(v).grp=="alle").sum()) for k,v in (("BY",pb),("CZ",pc))})
