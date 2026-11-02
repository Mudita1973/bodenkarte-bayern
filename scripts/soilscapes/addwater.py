"""Ergänzt props3.json um Bodenwasser-Kennwerte (LfU, boden_kennwerte_ftz 53/55/57/59) und Pilz-Kennzahlen je Einheit -> props5.json"""
import json, pandas as pd
P=json.load(open("props3.json"))
W={}
for row in open("ua/wasser.txt").read().split(";"):
    k,*v=row.split(","); fn=k[-1]; leg=k[:-1]
    vals=[(int(x,36) if x else None) for x in v]; vals=[None if (x is not None and x<0) else x for x in vals]
    W.setdefault(leg,{})["F" if fn=="F" else "N"]=dict(zip(["fk","nfk","lk","kf"],vals))
cols=["key","go_ob","go_ub","ca_ob","ca_ub","bs","hu_ob","puffer"]
kw=pd.concat([pd.read_csv(f"ua/k{i}.csv",header=None,names=cols,dtype=str) for i in range(6)])
KW={}
for _,r in kw.iterrows():
    leg,fn=r.key.split("|"); d={}
    for c in ("ca_ob","bs"):
        if isinstance(r[c],str) and r[c] not in ("","n"): d[c]=float(r[c])
    KW.setdefault(leg,{})[fn]=d
geo=pd.concat([pd.read_csv(f"ua/g{i}.csv",header=None,names=["leg","sauer","basisch","carb","dom"],dtype=str) for i in range(2)]).set_index("leg")
def f(x,d=0): return f"{x:.{d}f}".replace(".",",")
def cl_nfk(v): return "sehr gering" if v<50 else "gering" if v<90 else "mittel" if v<140 else "hoch" if v<200 else "sehr hoch"
def cl_kf(v): return "sehr gering" if v<1 else "gering" if v<10 else "mittel" if v<40 else "hoch" if v<100 else "sehr hoch" if v<300 else "äußerst hoch"
def pick(d,key):
    for fn in ("F","N","NF"):
        if fn in d and d[fn].get(key) is not None: return d[fn][key]
    return None
n=0
for leg,u in P["units"].items():
    p=u["p"]; w=W.get(leg,{}); kwd=KW.get(leg,{})
    if w and p.get("kennwerte") and p["kennwerte"].get("rows") is not None:
        rows=p["kennwerte"]["rows"]
        def both(key,unit,cls,d=0):
            parts=[]
            for fn,lab in (("F","Wald"),("N","Acker/Grünland")):
                v=w.get(fn,{}).get(key)
                if v is not None: parts.append(f"{f(v,d)} {unit}"+(f" ({cls(v)}, {lab})" if cls else f" ({lab})"))
            return "; ".join(parts)
        for key,name,unit,cls in (("nfk","Nutzbare Feldkapazität (bis 1 m)","mm",cl_nfk),("fk","Feldkapazität (bis 1 m)","mm",None),("lk","Luftkapazität (bis 1 m)","mm",None),("kf","Wasserdurchlässigkeit gesättigt (kf)","cm/Tag",cl_kf)):
            t=both(key,unit,cls)
            if t: rows.append({"n":name,"v":t}); n+=1
    bs=pick(kwd,"bs"); ca=pick(kwd,"ca_ob"); nfk=pick(w,"nfk") if w else None; kf=pick(w,"kf") if w else None
    s=b=None
    if leg in geo.index: s=int(geo.loc[leg,"sauer"]); b=int(geo.loc[leg,"basisch"])
    u["z"]=[bs,ca,nfk,kf,s,b]
P["water_rule"]=("Bodenwasser-Kennwerte des LfU (UmweltAtlas Bayern, Dienst boden_kennwerte_ftz, Layer 53, 55, 57 und 59) je ÜBK25-Legendeneinheit, "
 "getrennt für Wald und Nichtwald, gemittelt über die Teilkennungen der Einheit. Einstufung der nutzbaren Feldkapazität und der Wasserdurchlässigkeit nach Bodenkundlicher Kartieranleitung (KA5).")
json.dump(P,open("props5.json","w"),ensure_ascii=False)
print("Zeilen ergänzt:",n,"Einheiten mit Wasserdaten:",sum(1 for l in P["units"] if l in W),"von",len(P["units"]))
import collections
c=collections.Counter()
for u in P["units"].values():
    bs,ca,nfk,kf,s,b=u["z"]; c["bs"]+=bs is not None; c["nfk"]+=nfk is not None
print(c)
print(P["units"]["574a"]["p"]["kennwerte"]["rows"][-4:], P["units"]["574a"]["z"])
