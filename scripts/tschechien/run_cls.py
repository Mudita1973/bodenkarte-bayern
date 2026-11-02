import geopandas as gpd, pandas as pd, numpy as np, collections, json
import importlib.util; spec=importlib.util.spec_from_file_location("c","classify_cz.py"); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
a=gpd.read_parquet("cz_poly.parquet")
a["grp"]=[c.grp(s,t) for s,t in zip(a["sub"].fillna(""),a.geo_txt.fillna(""))]
maj=a.groupby(["ukey","grp"]).km2.sum().reset_index().sort_values("km2").drop_duplicates("ukey",keep="last").set_index("ukey").grp
a["grp"]=a.ukey.map(maj)
m=a.src=="1M"
a.loc[m,"p2_jednot"]=[c.M1.get(x,(x,None))[1] for x in a.loc[m,"p1_jednot"]]
a.loc[m,"p1_jednot"]=[c.M1.get(x,(x,None))[0] for x in a.loc[m,"p1_jednot"]]
a["hk"]=a.hoehe*a.km2; a["nk"]=a.neig*a.km2; a["fk"]=a.p5*a.km2
agg=a.groupby("ukey").agg(src=("src","first"),code=("index_kart_mapa","first"),p1=("p1_jednot","first"),p2=("p2_jednot","first"),p3=("p3_jednot","first"),sub=("sub","first"),grp=("grp","first"),wrb=("p1_wrb22_soilname","first"),wrb2=("p2_wrb22_soilname","first"),km2=("km2","sum"),hk=("hk","sum"),nk=("nk","sum"),fk=("fk","sum"),n=("km2","size"))
res=[c.classify(dict(p1=r.p1,p2=r.p2,p3=r.p3,grp=r.grp,sub=r.sub,src=r.src,wrb=r.wrb)) for r in agg.itertuples()]
agg["k"]=[x[0] for x in res]; agg["why"]=[x[1] for x in res]; agg["sure"]=[x[2] for x in res]
agg["h"]=agg.hk/agg.km2; agg["neig"]=agg.nk/agg.km2; agg["p5"]=agg.fk/agg.km2
agg.to_parquet("cz_units.parquet"); a.to_parquet("cz_poly2.parquet")
print(agg.groupby("k").km2.sum().round().sort_values(ascending=False))
print("unsicher Anteil", round(agg[~agg.sure].km2.sum()/agg.km2.sum()*100,1),"%")
print(agg.groupby(["p1","k"]).km2.sum().round(1).sort_values(ascending=False).head(45).to_string())
