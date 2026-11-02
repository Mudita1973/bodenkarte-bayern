import json, numpy as np, pandas as pd, geopandas as gpd, collections
from rasterio import features
import rasterio
from pyproj import Transformer
keys=json.load(open("keys.json")); kix={k:i for i,k in enumerate(keys)}
pr=json.load(open("props_cz.json")); u=pd.read_parquet("cz_units2.parquet")
lu=np.load("key_lu_km2.npy"); wr=json.load(open("webraster.json"))
K=[]
for i,(key,r) in enumerate(zip(keys,u.itertuples())):
    assert key==f"{r.leg}|{r.k}"
    crit=pr["match"][r.leg]
    bits={c:sum((1<<j) for j,(n,ok) in enumerate(lst) if ok) for c,lst in crit.items()}
    K.append({"leg":r.leg,"k":r.k,"s":int(bool(r.sure)),"w":r.why,"a":round(float(r.km2),1),"h":int(round(r.h)) if r.h==r.h else 0,
              "lu":[int(round(x*100)) for x in lu[i+1]],"m":bits})
units={f"{r.leg}|{r.k}":pr["units"][r.leg] for r in u.itertuples()} if False else pr["units"]
# Kreisstatistik
R=50; X0,Y0,X1,Y1=285000,5370000,545000,5600000; W=(X1-X0)//R; H=(Y1-Y0)//R
tr=rasterio.transform.from_origin(X0,Y1,R,R)
ok=gpd.read_file("okresy.geojson").to_crs(32633).reset_index(drop=True)
O=features.rasterize(((g,i+1) for i,g in enumerate(ok.geometry)),out_shape=(H,W),transform=tr,fill=0,dtype="int32")
Kr=np.load("K50.npy"); L=np.load("lu50.npy")
kcls=np.array(["-"]+[k.split("|")[1] for k in keys])
t32=Transformer.from_crs(32633,32632,always_xy=True)
kreise=[]; px=R*R/1e6
for i,o in ok.iterrows():
    m=(O==i+1)&(Kr>0)
    if not m.any(): continue
    cl=kcls[Kr[m]]; gr=L[m]==3
    c={}
    for k in np.unique(cl):
        s=cl==k
        if k=="W": continue
        c[k]=[round(float(s.sum()*px),2),round(float((s&gr).sum()*px),2)]
    x0,y0,x1,y1=o.geometry.bounds; xs,ys=t32.transform([x0,x1,x0,x1],[y0,y0,y1,y1])
    kreise.append({"n":o.nazev,"ags":str(o.kod),"bb":[int(min(xs)/1000),int(min(ys)/1000),int(np.ceil(max(xs)/1000)),int(np.ceil(max(ys)/1000))],
                   "t":round(float(m.sum()*px),1),"c":c})
kreise.sort(key=lambda k:k["n"])
json.dump(kreise,open("kreise.json","w"),ensure_ascii=False)
print("Kreise",len(kreise),"Summe",round(sum(k["t"] for k in kreise)))
# kleine Vorkommen
a=gpd.read_parquet("cz_poly2.parquet"); a["k"]=a.ukey.map(pd.read_parquet("cz_units.parquet").k)
sm=a[a.k.isin(["16","2"])].dissolve(by="k").explode(index_parts=False).reset_index()
sm=sm.to_crs(32633); sm["km2"]=sm.area/1e6; sm=sm[sm.km2>=0.05]
pts=sm.representative_point().to_crs(4326)
small=[[k,round(p.y,4),round(p.x,4),round(a_,1)] for k,p,a_ in zip(sm.k,pts,sm.km2)]
print("kleine",collections.Counter(s[0] for s in small))
reg=gpd.read_file("kraje.geojson").to_crs(32632).union_all().simplify(80)
region=[]
for pg in getattr(reg,"geoms",[reg]):
    for r in [pg.exterior]+list(pg.interiors): region.append([int(round(v)) for xy in list(r.coords)[:-1] for v in xy])
print("Umriss Punkte",sum(len(r) for r in region)//2)
ov=json.load(open("ov.json")); gen=json.load(open("gen.json"))
data={"tr":gen["tr"],"bin":gen["bin"],"feat":gen["feat"],"keys":K,"units":units,"crit":pr["critnames"],"small":small,
      "lu":{"png":wr["kl"],"b":wr["klBounds"]},"dem":{"png":wr["dem"],"b":wr["demBounds"]},"kreise":kreise,"ov":ov,"region":region}
s=json.dumps(data,ensure_ascii=False,separators=(",",":")); open("data_cz.json","w").write(s)
print(round(len(s)/1e6,2),"MB",len(K))
c=collections.Counter()
for k in K: c[k["k"]]+=k["a"]
print({a:round(b) for a,b in sorted(c.items())})
