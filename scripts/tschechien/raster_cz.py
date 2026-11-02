import json, glob, numpy as np, rasterio, geopandas as gpd, pandas as pd, io, base64
from rasterio import features
from rasterio.warp import reproject, transform_bounds
from rasterio.enums import Resampling
from shapely.geometry import shape, Polygon, MultiPolygon
from PIL import Image
R=50; X0,Y0,X1,Y1=285000,5370000,545000,5600000; W=(X1-X0)//R; H=(Y1-Y0)//R
tr=rasterio.transform.from_origin(X0,Y1,R,R)
CLS={138:1,135:2,136:2,137:2,139:3,142:6,140:7,141:7,131:8,18:8,130:11,129:11,132:10}
for l in [114,115,116,117,118,119,121,122,123,124,125,126,127,134]: CLS[l]=9
ORDER=[1,3,2,6,7,11,8,9,10]
lu=np.zeros((H,W),dtype="uint8")
geoms={c:[] for c in ORDER}
for f in glob.glob("zab/z*.json"):
    j=json.load(open(f)); c=CLS[j["l"]]
    for rings in j["f"]:
        try:
            p=Polygon(rings[0],rings[1:]) if len(rings)>1 else Polygon(rings[0])
            geoms[c].append(p)
        except Exception: pass
for c in ORDER:
    if geoms[c]:
        m=features.rasterize(((g,1) for g in geoms[c]),out_shape=(H,W),transform=tr,fill=0,dtype="uint8")
        lu[m>0]=c
    print(c,len(geoms[c]),(lu==c).mean())
# Region und Schlüssel
keys=json.load(open("keys.json")); kix={k:i+1 for i,k in enumerate(keys)}
b=gpd.read_file("ms/base.shp").to_crs(32633)
K=features.rasterize(((g,kix[k]) for g,k in zip(b.geometry,b.key)),out_shape=(H,W),transform=tr,fill=0,dtype="int32")
lu2=lu.copy(); lu2[K==0]=0
m=K>0
cnt=np.bincount(K[m].astype(np.int64)*16+lu2[m],minlength=(len(keys)+1)*16).reshape(-1,16)*R*R/1e6
np.save("key_lu_km2.npy",cnt); print("Fläche",cnt.sum(),"ohne Nutzung",cnt[:,0].sum())
np.save("lu50.npy",lu2); np.save("K50.npy",K)
# Web-Raster (EPSG:3857, 125 m) für Nutzung, Höhe 400 m
def to3857(arr,res,resamp,dtype,src_tr,nd=None):
    bb=transform_bounds("EPSG:32633","EPSG:3857",X0,Y0,X1,Y1); w=int(np.ceil((bb[2]-bb[0])/res)); h=int(np.ceil((bb[3]-bb[1])/res))
    t=rasterio.transform.from_origin(bb[0],bb[3],res,res); dst=np.zeros((h,w),dtype=dtype)
    reproject(arr,dst,src_transform=src_tr,src_crs="EPSG:32633",dst_transform=t,dst_crs="EPSG:3857",resampling=resamp,src_nodata=nd,dst_nodata=nd)
    ll=transform_bounds("EPSG:3857","EPSG:4326",bb[0],bb[3]-h*res,bb[0]+w*res,bb[3]); return dst,[[ll[1],ll[0]],[ll[3],ll[2]]]
Ld,lb=to3857(lu2,125,Resampling.nearest,"uint8",tr)
buf=io.BytesIO(); Image.fromarray(Ld,"L").save(buf,"PNG",optimize=True)
r=rasterio.open("dem100.tif"); dem=r.read(1); dem=np.where((dem>0)&np.isfinite(dem),dem,0)
Dd,db=to3857(np.round(dem).astype("uint16"),400,Resampling.average,"uint16",r.transform,0)
drgb=np.dstack([(Dd>>8).astype("uint8"),(Dd&255).astype("uint8"),np.zeros_like(Dd,dtype="uint8")])
b2=io.BytesIO(); Image.fromarray(drgb,"RGB").save(b2,"PNG",optimize=True)
json.dump({"keys":keys,"kl":base64.b64encode(buf.getvalue()).decode(),"klBounds":lb,"dem":base64.b64encode(b2.getvalue()).decode(),"demBounds":db},open("webraster.json","w"))
print("PNG", len(buf.getvalue())/1e6, len(b2.getvalue())/1e6)
