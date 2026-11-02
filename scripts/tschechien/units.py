import geopandas as gpd, pandas as pd, numpy as np, rasterio, re, json
from rasterio import features
g=gpd.read_parquet("cz_raw.parquet").reset_index(drop=True)
k=gpd.read_file("kraje.geojson").to_crs(32633); reg=k.union_all()
geo=gpd.read_parquet("geo50.parquet")[["hor_karto","geneze","hor_typ","geometry"]]
# Bodenflächen auf Region zuschneiden
g["geometry"]=g.geometry.intersection(reg); g=g[~g.geometry.is_empty & (g.area>1)].copy(); g=g.reset_index(drop=True)
g["km2"]=g.area/1e6; print("Fläche ČGS 1:50 000 in Region", round(g.km2.sum()), "km²")
# Gestein am repräsentativen Punkt
pts=gpd.GeoDataFrame(g[[]],geometry=g.representative_point(),crs=32633)
j=gpd.sjoin(pts,geo,how="left",predicate="within"); j=j[~j.index.duplicated()]
g["geo_txt"]=(j.hor_karto.fillna("")).values; g["geo_gen"]=j.geneze.fillna("").values
# Lücken mit 1:1 Mio. füllen
cov=g.union_all(); gap=reg.difference(cov)
m=gpd.read_file("pudy1mil.geojson").to_crs(32633)
m["geometry"]=m.geometry.intersection(gap); m=m[~m.geometry.is_empty].explode(index_parts=False); m=m[m.area>20000].reset_index(drop=True).copy()
print("Lücken", round(gap.area/1e6), "km², davon mit 1:1 Mio. gefüllt", round(m.area.sum()/1e6))
pm=gpd.GeoDataFrame(m[[]],geometry=m.representative_point(),crs=32633); jm=gpd.sjoin(pm,geo,how="left",predicate="within"); jm=jm[~jm.index.duplicated()]
m["geo_txt"]=jm.hor_karto.fillna("").values; m["geo_gen"]=jm.geneze.fillna("").values
# Höhe und Neigung (DMR4G, 100 m)
r=rasterio.open("dem100.tif"); dem=r.read(1).astype("float32"); dem[dem<=0]=np.nan
gy,gx=np.gradient(dem,100.0); slope=np.degrees(np.arctan(np.hypot(gx,gy)))
def zonal(gdf):
    ids=np.arange(1,len(gdf)+1)
    lab=features.rasterize(zip(gdf.geometry,ids),out_shape=dem.shape,transform=r.transform,fill=0,dtype="int32",all_touched=False)
    ok=(lab>0)&np.isfinite(dem)
    n=np.bincount(lab[ok],minlength=len(gdf)+1); sh=np.bincount(lab[ok],weights=dem[ok],minlength=len(gdf)+1)
    ss=np.bincount(lab[ok],weights=slope[ok],minlength=len(gdf)+1); s5=np.bincount(lab[ok],weights=(slope[ok]>=5).astype(float),minlength=len(gdf)+1)
    p=gdf.representative_point(); rr,cc=rasterio.transform.rowcol(r.transform,p.x.values,p.y.values); rr=np.clip(rr,0,dem.shape[0]-1); cc=np.clip(cc,0,dem.shape[1]-1)
    hp=dem[rr,cc]; sp=slope[rr,cc]
    h=np.where(n[1:]>0, sh[1:]/np.maximum(n[1:],1), hp); s=np.where(n[1:]>0, ss[1:]/np.maximum(n[1:],1), sp); f5=np.where(n[1:]>0, s5[1:]/np.maximum(n[1:],1), (sp>=5).astype(float))
    return h,s,f5
g["hoehe"],g["neig"],g["p5"]=zonal(g); m["hoehe"],m["neig"],m["p5"]=zonal(m)
# Gesteinsgruppen
ACID=re.compile(r"žul|granit|granodiorit|rul[ay]?\b|rula|pararul|ortorul|migmatit|svor|fylit|kvarcit|granulit|křemen[cn]|metagranit|porfyr|ryolit|rohovec|drob|břidlic|pískovc[eiů]? křem|pískovce křem|arkóz|kyselé horniny|minerálně chudé|anatexit|aplit|pegmatit|greisen",re.I)
BASIC=re.compile(r"amfibol(?!-biotit)|amfibolit|bazalt|čedič|diabas|gabr|serpentinit|dioritu?\b|andezit|eklogit|tefrit|bazick|ultrabaz|metabazit|spilit|pyroklast|tuf(?!it)|fonolit|lamprofyr",re.I)
CARB=re.compile(r"vápen|vápnit|slín|dolomit|opuk|travertin|mramor|krystalick[éý] vápen|spraš(?!ov)|karbonát|kalc",re.I)
LOESS=re.compile(r"spraš",re.I)
SAND=re.compile(r"písek|písk[uy]|písč(?!ito-hlinit)|navátý|štěrkopís|arenick|psamit",re.I)
SKEL=re.compile(r"suť|sutě|kamenit|balvan|blok|skelet|psefit|eluvi",re.I)
CLAY=re.compile(r"jíl(?!ovit[ýé] pís)|pelit|pelick|slín",re.I)
COVER=re.compile(r"nivní|deluvi|koluvi|hlín|sediment|polygenet|navátý|navážka|rašelin|slatin|hnilokal|antropogen",re.I)
def grp(sub, geotxt):
    t=sub if sub else geotxt
    if not t: return "?"
    if CARB.search(t): return "carb" if not LOESS.search(t) else "loess"
    if LOESS.search(t): return "loesslehm"
    if BASIC.search(t) and not ACID.search(t): return "basic"
    if ACID.search(t) and not COVER.search(t if sub else "") : return "acid"
    if SAND.search(t): return "sand"
    if CLAY.search(t): return "clay"
    if SKEL.search(t): return "skel"
    return "loam" if re.search(r"hlín|hlinit|sediment|polygenet|koluvi|deluvi|nivní",t,re.I) else "other"
g["sub"]=g.n_txt.fillna("").where(g.n_txt.notna(), g.sg_txt.fillna(""))
g["grp"]=[grp(s,t) for s,t in zip(g["sub"],g.geo_txt)]
g["grp_geo"]=[grp("",t) for t in g.geo_txt]
m["sub"]=""; m["grp"]=[grp("",t) for t in m.geo_txt]; m["grp_geo"]=m["grp"]
# Schlüssel: Kartiereinheit + Substrat (falls angegeben) sonst Gesteinsgruppe
g["ukey"]=g.index_kart_mapa.fillna("?")+" | "+np.where(g["sub"]!="", g["sub"], "Gestein: "+g.grp)
m["ukey"]="1M: "+m.leg_tksp.fillna("?")+" | Gestein: "+m.grp
g["src"]="50"; m["src"]="1M"
m["p1_jednot"]=m.leg_tksp; m["p1_wrb22_soilname"]=m.leg_wrb15; m["index_kart_mapa"]=None
cols=["ukey","src","index_kart_mapa","p1_jednot","p2_jednot","p3_jednot","sub","grp","grp_geo","geo_txt","geo_gen","p1_wrb22_soilname","p2_wrb22_soilname","hoehe","neig","p5","geometry"]
for c in cols:
    if c not in m: m[c]=None
allp=pd.concat([g[cols],m[cols]],ignore_index=True); allp=gpd.GeoDataFrame(allp,geometry="geometry",crs=32633); allp["km2"]=allp.area/1e6
allp.to_parquet("cz_poly.parquet")
print("Polygone",len(allp),"Einheiten",allp.ukey.nunique(), "Fläche", round(allp.km2.sum()))
print(allp.groupby("grp").km2.sum().round().sort_values(ascending=False))
