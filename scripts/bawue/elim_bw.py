import geopandas as gpd, numpy as np, shapely, pyogrio, time, sys
from collections import defaultdict
t0=time.time()
g=gpd.read_file(sys.argv[1]).explode(index_parts=False).reset_index(drop=True)
g=g[g.key.notna()]
g["k"]=g.key.str.split("|").str[1]
print("Teile",len(g))
TH=float(sys.argv[2])
for rnd in range(3):
    g=g.reset_index(drop=True)
    a=g.area.values
    small=np.where((a<TH)&(~g.k.isin(["2","16"])).values)[0]
    tree=shapely.STRtree(g.geometry.values); bnd=shapely.boundary(g.geometry.values)
    q=tree.query(g.geometry.values[small],predicate="intersects")
    cand=defaultdict(list)
    for s,n in zip(small[q[0]],q[1]):
        if s!=n: cand[s].append(n)
    leg=g.key.values.copy(); k=g.k.values.copy(); cnt=0
    for s,ns in cand.items():
        best=None;bl=0
        for n in ns:
            if g.key.values[n]==g.key.values[s]: continue
            l=shapely.length(shapely.intersection(bnd[s],bnd[n]))*(10 if a[n]>=TH else 1)
            if l>bl: bl=l;best=n
        if best is not None:
            leg[s]=g.key.values[best]; k[s]=g.k.values[best]; cnt+=1
    g["key"]=leg; g["k"]=k
    g=g.dissolve("key",aggfunc="first").reset_index().explode(index_parts=False)
    print(rnd,len(small),"klein,",cnt,"umgehängt ->",len(g),"Teile",round(time.time()-t0),"s")
pyogrio.write_dataframe(g[["key","k","geometry"]],sys.argv[3])
