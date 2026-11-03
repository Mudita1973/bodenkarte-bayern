import requests, numpy as np, io, json
from PIL import Image
from pyproj import Transformer
t=Transformer.from_crs(4326,3857,always_xy=True)
x0,y0=t.transform(7.48,47.50); x1,y1=t.transform(10.52,49.81)
R=150; W=int((x1-x0)/R); H=int((y1-y0)/R); print(W,H)
PAL=np.array([[125,15,50],[175,8,37],[236,89,106],[249,204,209],[204,236,249],[89,193,236],[0,120,173],[0,80,120]])
cls=np.full((H,W),255,np.uint8); n=4
for i in range(n):
    for j in range(n):
        c0,c1=W*i//n,W*(i+1)//n; r0,r1=H*j//n,H*(j+1)//n
        bx0=x0+c0*R; bx1=x0+c1*R; by1=y1-r0*R; by0=y1-r1*R
        u=("https://atlas.thuenen.de/geoserver/ows?service=WMS&version=1.1.1&request=GetMap&layers=geonode:pH_map_0_30&styles=&srs=EPSG:3857"
           f"&bbox={bx0},{by0},{bx1},{by1}&width={c1-c0}&height={r1-r0}&format=image/png&transparent=true")
        im=np.array(Image.open(io.BytesIO(requests.get(u,timeout=180).content)).convert("RGBA")).astype(int)
        rgb=im[...,:3]; a=im[...,3]
        d=((rgb[...,None,:]-PAL[None,None])**2).sum(-1); k=d.argmin(-1).astype(np.uint8); k[a<128]=255
        cls[r0:r1,c0:c1]=k; print(i,j,(a>=128).mean().round(3),flush=True)
np.save("th30_bw_cls.npy",cls); json.dump({"x0":x0,"y1":y1,"R":R,"W":W,"H":H},open("th30_bw_meta.json","w"))
print("fertig")
