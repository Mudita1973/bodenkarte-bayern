import json, glob, numpy as np, pandas as pd, geopandas as gpd
rng=np.random.default_rng(1)
T=json.load(open("taxa.json")); O=json.load(open("obs_bw.json"))
rows=[]
for name,lst in O.items():
    g="alle" if name=="Fungi" else T[name]["grp"]
    for oid,lat,lng,uid,date,tid,acc in lst: rows.append((oid,lat,lng,uid,date,tid,name,g))
df=pd.DataFrame(rows,columns=["oid","lat","lng","uid","date","tid","art","grp"])
pts=gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.lng,df.lat),crs=4326).to_crs(25832)
P=json.load(open("/home/claude/bw/props_bw.json"))["units"]
hits=[]
for f in sorted(glob.glob("/home/claude/bw/parts/dBK50_*[!t].parquet")):
    g=gpd.read_parquet(f,columns=["ke","geometry"]).set_crs(25832,allow_override=True)
    h=gpd.sjoin(pts,g,predicate="within",how="inner"); hits.append(h.drop(columns="index_right"))
pb=pd.concat(hits).drop_duplicates("oid"); pb["ke"]=pb.ke.str.strip()
zc=np.array([P[k]["zc"] if k in P else [None]*5 for k in pb.ke],dtype=object)
for j,src in ((0,"BK50 Wald"),(2,"BK50 Acker/Grünland")):
    pb[src+"|s"]=[None if v is None else bool(v) for v in zc[:,j]]; pb[src+"|b"]=[None if v is None else bool(v) for v in zc[:,j+1]]
# strengere Variante: nur Stufen 2 und 3 (unter pH 4) als sauer
import re
def strict(k):
    a=P.get(k); 
    if not a: return None
    b=[x for x in a["p"]["saeure"]["belege"] if x["art"].startswith("unter Wald")]
    if not b: return None
    raw=b[0]["beleg"].split()[-1].split("/")[0]; main=re.findall(r"6a|6b|[2-8]",re.sub(r"\(.*?\)","",raw))
    return bool(main) and all(m in ("2","3") for m in main) and not a["zc"][1]
pb["BK50 Wald, nur unter pH 4|s"]=[strict(k) for k in pb.ke]; pb["BK50 Wald, nur unter pH 4|b"]=pb["BK50 Wald|b"]
try:
    m=json.load(open("th30_bw_meta.json")); cls=np.load("th30_bw_cls.npy"); p3=pb.to_crs(3857)
    c=((p3.geometry.x-m["x0"])/m["R"]).astype(int).values; r=((m["y1"]-p3.geometry.y)/m["R"]).astype(int).values
    ok=(c>=0)&(c<m["W"])&(r>=0)&(r<m["H"]); k=np.full(len(pb),255); k[ok]=cls[r[ok],c[ok]]
    pb["Thünen pH 0-30|s"]=np.where(k==255,None,k<=1); pb["Thünen pH 0-30|b"]=np.where(k==255,None,k>=5); TH=True
except Exception as e: print("Thünen fehlt",e); TH=False
def thin(d):
    d=d.copy(); g=d.to_crs(3035); d["cell"]=(g.geometry.x//1000).astype(int).astype(str)+"_"+(g.geometry.y//1000).astype(int).astype(str)
    return d.drop_duplicates(["uid","tid","cell"])
d=thin(pb); base=d[d.grp=="alle"]; res=[]
srcs=["BK50 Wald","BK50 Wald, nur unter pH 4","BK50 Acker/Grünland"]+(["Thünen pH 0-30"] if TH else [])
for src in srcs:
    for g in ("sauer","ueberall","basisch"):
        G=d[d.grp==g]
        for side in ("s","b"):
            col=f"{src}|{side}"; gv=G[col].dropna().astype(bool).values; bv=base[col].dropna().astype(bool).values
            if len(gv)<10 or not len(bv): continue
            pg,p0=gv.mean(),bv.mean()
            bs=[rng.choice(gv,len(gv)).mean()/max(1e-9,rng.choice(bv,len(bv)).mean()) for _ in range(2000)]
            res.append(dict(quelle=src,gruppe=g,auf={"s":"sauer","b":"basisch"}[side],n=len(gv),anteil_gruppe=round(pg*100,1),anteil_alle=round(p0*100,1),
                            faktor=round(pg/p0,2) if p0 else None,ki_lo=round(np.percentile(bs,2.5),2),ki_hi=round(np.percentile(bs,97.5),2)))
R=pd.DataFrame(res); R.to_csv("ergebnis_bw.tsv",sep="\t",index=False); pd.set_option("display.width",220); print(R.to_string(index=False))
art=[]; b0s=base["BK50 Wald|s"].dropna().astype(bool).mean(); b0b=base["BK50 Wald|b"].dropna().astype(bool).mean()
for a,G in d[d.grp!="alle"].groupby("art"):
    s=G["BK50 Wald|s"].dropna().astype(bool); b=G["BK50 Wald|b"].dropna().astype(bool)
    if len(s)>=25: art.append(dict(art=a,gruppe=G.grp.iloc[0],n=len(s),sauer_faktor=round(s.mean()/b0s,2),basisch_faktor=round(b.mean()/b0b,2)))
A=pd.DataFrame(art); A.to_csv("ergebnis_arten_bw.tsv",sep="\t",index=False); print(A.to_string(index=False))
print("Funde in BW:",len(pb),"nach Ausdünnung:",len(d),"davon Basis (alle Pilze):",int((d.grp=="alle").sum()))
