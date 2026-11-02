import json, numpy as np, pandas as pd
md=json.load(open("mapdata2.json")); pr=json.load(open("props5.json")); wr=json.load(open("webraster.json"))
keys=wr["keys"]; kix={k:i for i,k in enumerate(keys)}
lu=np.load("key_lu_km2.npy")
z=pd.read_csv("zuordnung.tsv",sep="\t",header=None,names=["leg","k","sure","why","text"],dtype=str).drop_duplicates("leg").set_index("leg")
v=pd.read_parquet("v3.parquet"); v["key_old"]=v.leg+"|"+pd.read_parquet("v2.parquet").k2; v["hk"]=v.hoehe*v.km2
agg=v.groupby("key_old").agg(km2=("km2","sum"),hk=("hk","sum"),k2=("k2",lambda s:s.value_counts().index[0]),why2=("why2","first"))
K=[]
for i,key in enumerate(keys):
    leg=key.split("|")[0]; r=agg.loc[key]
    k=r.k2; sure=z.loc[leg,"sure"]=="True"; why=r.why2 or z.loc[leg,"why"]
    if r.why2: sure=False
    if "Bodenkomplex" in z.loc[leg,"text"]: sure=False
    crit=pr["match"][key]
    bits={c:sum((1<<j) for j,(n,ok) in enumerate(lst) if ok) for c,lst in crit.items()}
    K.append({"leg":leg,"k":k,"s":int(sure),"w":why,"a":round(float(r.km2),1),"h":int(round(r.hk/r.km2)),"lu":[int(round(x*100)) for x in lu[i+1]],"m":bits})
feat=[kix[f] for f in md["feat"]]
small=json.load(open("smallmarks2.json"))
data={"tr":md["tr"],"bin":md["bin"],"feat":feat,"keys":K,"units":pr["units"],"crit":pr["critnames"],"small":small,
      "lu":{"png":wr["kl"],"b":wr["klBounds"]},"dem":{"png":wr["dem"],"b":wr["demBounds"]}}
s=json.dumps(data,ensure_ascii=False,separators=(",",":"))
open("data4.json","w").write(s); print(len(s)/1e6,"MB",len(K),"Schlüssel")
import collections; c=collections.Counter()
for k in K: c[k["k"]]+=k["a"]
print({a:round(b) for a,b in sorted(c.items())})
