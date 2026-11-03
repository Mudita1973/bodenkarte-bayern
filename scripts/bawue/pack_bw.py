import json, collections, numpy as np, pandas as pd, geopandas as gpd, rasterio, shapely
from rasterio import features
from pyproj import Transformer
keys=json.load(open("keys.json"))
pr=json.load(open("props_bw.json")); u=pd.read_parquet("bw_units_cls.parquet")
lu=np.load("key_lu_km2.npy"); wr=json.load(open("webraster.json")); rel=pd.read_parquet("relief_bw.parquet").set_index("key")
# Flächen aus der Originalgeometrie (bw_units: km² je Einheit)
K=[]
for i,key in enumerate(keys):
    ke,k=key.split("|"); r=u.loc[ke]; assert r.k==k, key
    crit=pr["match"][key]
    bits={c:sum((1<<j) for j,(n,ok) in enumerate(lst) if ok) for c,lst in crit.items()}
    h=rel.loc[key].h
    K.append({"leg":ke,"k":k,"s":int(bool(r.sure)),"w":r.why,"a":round(float(r.km2),2 if r.km2<1 else 1),"h":int(round(h)) if h==h else 0,
              "lu":[int(round(x*100)) for x in lu[i+1]],"m":bits})
# Regeltexte nur einmal speichern
units=pr["units"]; REG=[]; RI={}
for x in units.values():
    x["p"]["bodentyp"].pop("detail",None)
    for p in x["p"].values():
        rg=p.get("regel")
        if isinstance(rg,str) and rg:
            if rg not in RI: RI[rg]=len(REG); REG.append(rg)
            p["regel"]=RI[rg]
for ke,x in units.items():
    v=u.loc[ke].nfk1m
    try: v=float(str(v).replace(",","."))
    except Exception: v=None
    if v is not None and v==v: x["nf"]=int(round(v))
print("Regeltexte",len(REG))
# Kreisstatistik
R=50; X0,Y1=388300,5515700
O=np.load("O50.npy"); Kr=np.load("K50.npy"); L=np.load("lu50.npy"); kn=json.load(open("kreisnamen.json"))
kcls=np.array(["-"]+[k.split("|")[1] for k in keys])
tr=rasterio.transform.from_origin(X0,Y1,R,R); px=R*R/1e6
FIXN={"Rems Murr Kreis":"Rems-Murr-Kreis","Main Tauber Kreis":"Main-Tauber-Kreis","Baden Baden":"Baden-Baden (Stadtkreis)","Neckar Odenwald Kreis":"Neckar-Odenwald-Kreis",
 "Rhein Neckar Kreis":"Rhein-Neckar-Kreis","Breisgau Hochschwarzwald":"Breisgau-Hochschwarzwald","Schwarzwald Baar Kreis":"Schwarzwald-Baar-Kreis","Alb Donau Kreis":"Alb-Donau-Kreis",
 "Stuttgart":"Stuttgart (Stadtkreis)","Mannheim":"Mannheim (Stadtkreis)","Ulm":"Ulm (Stadtkreis)","Heilbronn":"Heilbronn (Landkreis)","Karlsruhe":"Karlsruhe (Landkreis)"}
kreise=[]
for i,(code,name,ags) in enumerate(kn):
    name=FIXN.get(name,name)
    m=(O==i+1)&(Kr>0)
    if not m.any(): continue
    cl=kcls[Kr[m]]; gr=L[m]==3; c={}
    for k in np.unique(cl):
        if k=="W": continue
        s=cl==k; c[k]=[round(float(s.sum()*px),2),round(float((s&gr).sum()*px),2)]
    rr,cc=np.nonzero(O==i+1)
    x0,y1=tr*(cc.min(),rr.min()); x1,y0=tr*(cc.max()+1,rr.max()+1)
    kreise.append({"n":name,"ags":"08"+ags,"bb":[int(x0/1000),int(y0/1000),int(np.ceil(x1/1000)),int(np.ceil(y1/1000))],"t":round(float(m.sum()*px),1),"c":c})
kreise.sort(key=lambda k:k["n"])
print("Kreise",len(kreise),"Summe",round(sum(k["t"] for k in kreise)))
# kleine Vorkommen (Klassen 16 und 2)
sm=gpd.read_parquet("small_bw.parquet").set_crs(25832,allow_override=True)
sm["geometry"]=shapely.make_valid(sm.geometry.values)
sm=sm.dissolve(by="k").explode(index_parts=False).reset_index(); sm["km2"]=sm.area/1e6; sm=sm[sm.km2>=0.05]
pts=sm.representative_point().to_crs(4326)
small=[[k,round(p.y,4),round(p.x,4),round(a_,1)] for k,p,a_ in zip(sm.k,pts,sm.km2)]
print("kleine",collections.Counter(s[0] for s in small))
# Landesumriss aus dem 50-m-Raster
mask=(Kr>0).astype("uint8")
shp=[shapely.geometry.shape(g) for g,v in features.shapes(mask,mask=mask>0,transform=tr) if v==1]
reg=shapely.union_all(shp).buffer(60).buffer(-60).simplify(80)
reg=shapely.MultiPolygon([p for p in getattr(reg,"geoms",[reg]) if p.area>2e6])
region=[]
for pg in reg.geoms:
    for r in [pg.exterior]+[i for i in pg.interiors if shapely.Polygon(i).area>2e6]:
        region.append([int(round(v)) for xy in list(r.coords)[:-1] for v in xy])
print("Umriss Teile",len(region),"Punkte",sum(len(r) for r in region)//2)
ov=json.load(open("ov.json")); gen=json.load(open("gen.json"))
data={"tr":gen["tr"],"bin":gen["bin"],"feat":gen["feat"],"keys":K,"units":units,"reg":REG,"crit":pr["critnames"],"small":small,
      "lu":{"png":wr["kl"],"b":wr["klBounds"]},"dem":{"png":wr["dem"],"b":wr["demBounds"]},"kreise":kreise,"ov":ov,"region":region}
s=json.dumps(data,ensure_ascii=False,separators=(",",":")); open("data_bw.json","w").write(s)
import gzip; print(round(len(s)/1e6,2),"MB, gz",round(len(gzip.compress(s.encode(),6))/1e6,2),"MB",len(K))
c=collections.Counter()
for k in K: c[k["k"]]+=k["a"]
print({a:round(b) for a,b in sorted(c.items())})
