import numpy as np, rasterio, pandas as pd, time
from rasterio.warp import reproject
from rasterio.enums import Resampling
t0=time.time()
src=rasterio.open("/mnt/user-data/uploads/07_Bodenkarten/_dgm200_tmp.tif")
z=src.read(1).astype("float64"); z[z<-9000]=np.nan
r=src.res[0]
gy,gx=np.gradient(z,r)
slope=np.degrees(np.arctan(np.hypot(gx,gy))).astype("float32")
ids=np.load("ids50.npy")
H,W=ids.shape
g=pd.read_parquet("v2.parquet")
import geopandas as gpd
raw=gpd.read_parquet("raw.parquet",columns=["geometry"])
xmin,ymin,xmax,ymax=raw.total_bounds; R=50
xmin=np.floor(xmin/R)*R; ymax=np.ceil(ymax/R)*R
tr=rasterio.transform.from_origin(xmin,ymax,R,R)
sl=np.full((H,W),np.nan,dtype="float32")
reproject(slope,sl,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=src.crs,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
np.save("slope50.npy",sl)
m=(ids>0)&np.isfinite(sl)
n=len(g)+1
c=np.bincount(ids[m],minlength=n)
s=np.bincount(ids[m],weights=sl[m],minlength=n)
s5=np.bincount(ids[m],weights=(sl[m]>=5),minlength=n)
s10=np.bincount(ids[m],weights=(sl[m]>=10),minlength=n)
s2=np.bincount(ids[m],weights=(sl[m]<2),minlength=n)
cc=np.maximum(c,1)
g["neig"]=np.where(c>0,s/cc,np.nan)[1:]
g["p5"]=np.where(c>0,s5/cc,np.nan)[1:]
g["p10"]=np.where(c>0,s10/cc,np.nan)[1:]
g["p2"]=np.where(c>0,s2/cc,np.nan)[1:]
g["npx"]=c[1:]
g[["fid","leg","k2","km2","neig","p5","p10","p2","npx"]].to_parquet("slope.parquet")
print(round(time.time()-t0),"s; Bayern Neigung: mittel",np.nanmean(sl[ids>0]).round(2),"P90",np.nanpercentile(sl[ids>0],90).round(1),"max",np.nanmax(sl).round(1))
g["w"]=g.km2
for k,d in g.dropna(subset=["neig"]).groupby("k2"):
    w=d.km2
    print(k, "neig", round((d.neig*w).sum()/w.sum(),1), "p5", round((d.p5*w).sum()/w.sum()*100), "% p10", round((d.p10*w).sum()/w.sum()*100),"% eben<2", round((d.p2*w).sum()/w.sum()*100),"%")
