import numpy as np, pyogrio, rasterio, shapely, gc
from rasterio import features
R=50; X0,Y0,X1,Y1=388300,5265100,610100,5515700; W=(X1-X0)//R; H=(Y1-Y0)//R
tr=rasterio.transform.from_origin(X0,Y1,R,R)
CLC={}
for c in (111,112,121,122,123,124,131,132,133,141,142): CLC[c]=9
for c in (211,212,213): CLC[c]=1
for c in (221,222,223,241,242,243,244): CLC[c]=2
CLC[231]=3; CLC[321]=4; CLC[322]=5; CLC[323]=7; CLC[324]=7
for c in (311,312,313): CLC[c]=6
for c in (411,412): CLC[c]=8
for c in (331,332,333,334,335): CLC[c]=11
for c in (511,512,521,522,523): CLC[c]=10
lu=np.zeros((H,W),dtype="uint8"); n=0
for x in range(X0,X1,50000):
    bb=(x,Y0,min(x+50000,X1),Y1)
    d=pyogrio.read_dataframe("bkg/clc5_2021/CLC5ha_2021.gpkg",bbox=bb)
    box=shapely.box(*bb); g=shapely.intersection(shapely.simplify(d.geometry.values,10),box)
    c=d.CLC21.astype(int).map(CLC).values; unk=set(d.CLC21[np.isnan(c.astype(float))])
    if unk: print("unbekannt",unk)
    ok=~shapely.is_empty(g)
    lu=np.maximum(lu,features.rasterize(((gg,int(cc)) for gg,cc in zip(g[ok],c[ok])),out_shape=(H,W),transform=tr,fill=0,dtype="uint8"))
    n+=len(d); del d,g; gc.collect(); print(x,n,flush=True)
np.save("clc50.npy",lu); print({int(k):int(v) for k,v in zip(*np.unique(lu,return_counts=True))})
