import warnings; warnings.filterwarnings('ignore')
import json, glob, os, io, base64, numpy as np, pandas as pd, geopandas as gpd, pyogrio, rasterio, shapely
from rasterio import features
from rasterio.warp import reproject, transform_bounds
from rasterio.enums import Resampling
from PIL import Image
R=50; X0,Y0,X1,Y1=388300,5265100,610100,5515700; W=(X1-X0)//R; H=(Y1-Y0)//R
tr=rasterio.transform.from_origin(X0,Y1,R,R); CRS="EPSG:25832"
keys=json.load(open("keys.json")); KE={k.split("|")[0]:i+1 for i,k in enumerate(keys)}
# 1) Bodeneinheiten und Kreise (je Kreis-Datei der BK50, Geometrie auf 2 m vereinfacht: für 50-m-Raster ausreichend)
names={os.path.basename(f)[:-5]:os.path.basename(os.path.dirname(os.path.dirname(f)))[6:].replace("__Stadt"," (Stadtkreis)").replace("_"," ")
       for f in glob.glob("gpkg/*/data/*.gpkg")}
K=np.zeros((H,W),dtype="int32"); O=np.zeros((H,W),dtype="int16"); kn=[]; small=[]
for i,f in enumerate(sorted(glob.glob("parts/dBK50_*[!t].parquet"))):
    s_=os.path.basename(f)[:-8]; g=gpd.read_parquet(f,columns=["ke","geometry"])
    g["ki"]=g.ke.map(KE); assert g.ki.notna().all(), s_
    k=features.rasterize(((x,int(v)) for x,v in zip(g.geometry,g.ki)),out_shape=(H,W),transform=tr,fill=0,dtype="int32")
    new=(k>0)&(K==0); K[new]=k[new]; O[new]=i+1; kn.append((s_,names.get(s_,s_),s_.split("_")[1]))
    g["k"]=[keys[int(v)-1].split("|")[1] for v in g.ki]; small.append(g[g.k.isin(["16","2"])][["k","geometry"]])
    del g,k
np.save("O50.npy",O); json.dump(kn,open("kreisnamen.json","w"),ensure_ascii=False)
pd.concat(small).to_parquet("small_bw.parquet")
print("Raster Bodenfläche km²",round((K>0).sum()*R*R/1e6),"Kreise",len(kn),flush=True)
b=None
# 2) CORINE 5 ha 2021 -> Nutzungsklassen (clc_bw.py)
lu=np.load("clc50.npy")
lu[K==0]=0
np.save("lu50.npy",lu); np.save("K50.npy",K)
m=K>0
cnt=np.bincount(K[m].astype(np.int64)*16+lu[m],minlength=(len(keys)+1)*16).reshape(-1,16)*R*R/1e6
np.save("key_lu_km2.npy",cnt); print("Fläche",round(cnt.sum()),"ohne Nutzung",round(cnt[:,0].sum(),1))
# 3) Höhe und Neigung aus DGM200
src=rasterio.open("bkg/dgm200.utm32s.geotiff/dgm200/dgm200_utm32s.tif")
z=src.read(1).astype("float64"); z[z<-9000]=np.nan
gy,gx=np.gradient(z,src.res[0]); slope=np.degrees(np.arctan(np.hypot(gx,gy))).astype("float32")
dem=np.full((H,W),np.nan,dtype="float32"); sl=np.full((H,W),np.nan,dtype="float32")
reproject(z.astype("float32"),dem,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=CRS,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
reproject(slope,sl,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=CRS,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
m=(K>0)&np.isfinite(sl)&np.isfinite(dem); n=len(keys)+1
c=np.maximum(np.bincount(K[m],minlength=n),1)
st=pd.DataFrame({"key":keys,"h":(np.bincount(K[m],weights=dem[m],minlength=n)/c)[1:],
    "neig":(np.bincount(K[m],weights=sl[m],minlength=n)/c)[1:],"p5":(np.bincount(K[m],weights=sl[m]>=5,minlength=n)/c)[1:],
    "p10":(np.bincount(K[m],weights=sl[m]>=10,minlength=n)/c)[1:],"p2":(np.bincount(K[m],weights=sl[m]<2,minlength=n)/c)[1:],
    "npx":np.bincount(K[m],minlength=n)[1:]})
# Einheiten ohne Pixel: Wert am inneren Punkt der größten Fläche
miss=st.index[st.npx==0]
if len(miss):
    pp=[]
    for f in sorted(glob.glob("parts/dBK50_*[!t].parquet")):
        g=gpd.read_parquet(f,columns=["ke","geometry"]); g["ki"]=g.ke.map(KE); g=g[g.ki.isin(miss+1)]
        if len(g): g["a"]=g.area; pp.append(g)
    bb=pd.concat(pp).sort_values("a").drop_duplicates("ki",keep="last")
    p=bb.geometry.representative_point(); rr,cc=rasterio.transform.rowcol(tr,p.x.values,p.y.values)
    rr=np.clip(rr,0,H-1); cc=np.clip(cc,0,W-1)
    for ki,r_,c_ in zip(bb.ki,rr,cc):
        st.loc[ki-1,["h","neig"]]=[dem[r_,c_],sl[r_,c_]]; st.loc[ki-1,["p5","p10","p2"]]=[float(sl[r_,c_]>=5),float(sl[r_,c_]>=10),float(sl[r_,c_]<2)]
st.to_parquet("relief_bw.parquet"); print("ohne Pixel",len(miss),"Höhe mittel",round(np.nanmean(dem[K>0])),"max",round(np.nanmax(dem[K>0])))
# 5) Web-Raster
def to3857(arr,res,resamp,dtype,src_tr,nd=None):
    bb=transform_bounds(CRS,"EPSG:3857",X0,Y0,X1,Y1); w=int(np.ceil((bb[2]-bb[0])/res)); h=int(np.ceil((bb[3]-bb[1])/res))
    t=rasterio.transform.from_origin(bb[0],bb[3],res,res); dst=np.zeros((h,w),dtype=dtype)
    reproject(arr,dst,src_transform=src_tr,src_crs=CRS,dst_transform=t,dst_crs="EPSG:3857",resampling=resamp,src_nodata=nd,dst_nodata=nd)
    ll=transform_bounds("EPSG:3857","EPSG:4326",bb[0],bb[3]-h*res,bb[0]+w*res,bb[3]); return dst,[[ll[1],ll[0]],[ll[3],ll[2]]]
Ld,lb=to3857(lu,125,Resampling.nearest,"uint8",tr)
buf=io.BytesIO(); Image.fromarray(Ld,"L").save(buf,"PNG",optimize=True)
d0=np.where(np.isfinite(dem)&(K>0),dem,0)
Dd,db=to3857(np.round(d0).astype("uint16"),400,Resampling.average,"uint16",tr,0)
drgb=np.dstack([(Dd>>8).astype("uint8"),(Dd&255).astype("uint8"),np.zeros_like(Dd,dtype="uint8")])
b2=io.BytesIO(); Image.fromarray(drgb,"RGB").save(b2,"PNG",optimize=True)
json.dump({"keys":keys,"kl":base64.b64encode(buf.getvalue()).decode(),"klBounds":lb,"dem":base64.b64encode(b2.getvalue()).decode(),"demBounds":db},open("webraster.json","w"))
print("PNG",round(len(buf.getvalue())/1e6,2),round(len(b2.getvalue())/1e6,2))
