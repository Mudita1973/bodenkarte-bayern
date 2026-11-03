import geopandas as gpd, pandas as pd, glob, gc, sys, shapely, os
fs=sorted(glob.glob("gpkg/*/data/*.gpkg"))
for f in fs:
    out="parts/"+os.path.basename(f).replace(".gpkg",".parquet")
    if os.path.exists(out): continue
    g=gpd.read_file(f,layer="bod_ke")
    g["km2"]=g.area/1e6
    a=pd.DataFrame(g.drop(columns="geometry")); a.to_parquet(out.replace(".parquet","_att.parquet"))
    g=g[["ke","km2","geometry"]].copy(); g["geometry"]=shapely.simplify(g.geometry.values,2.0)
    g.to_parquet(out); print(os.path.basename(f),len(g),flush=True)
    del g,a; gc.collect()
