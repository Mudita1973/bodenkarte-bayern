"""Pilz-Bodengruppen für Westböhmen aus der ČGS-Bodenkarte (keine gemessenen Kennwerte wie in Bayern)."""
import re, pandas as pd
def s(v): return v if isinstance(v,str) else ""
def pz(r):
    p1=s(r.p1); t=p1.split()[0] if p1 else ""; g=r.grp; wrb=s(r.wrb)
    calc=g in ("carb","loess") or bool(re.search(r"vápnit|karbonát",p1)) or t in ("rendzina","pararendzina")
    dyst=bool(re.search(r"dystrick|oligotrof",p1))
    sauer=(dyst or bool(re.search(r"podzol",p1)) or t in ("podzol","kryptopodzol","stagnoglej")) and not calc and "eutrofn" not in p1
    # basisches Gestein (oft nur aus der geologischen Karte) zählt nur, wenn die Bodenkarte nicht basenarm oder mittel basenhaltig sagt
    basisch=calc or bool(re.search(r"eutrofn",p1)) or t in ("černozem","černice") or (g=="basic" and not dyst and "mesobaz" not in p1 and "Dystric" not in wrb)
    wasser=(t in ("hnědozem","luvizem","černozem") or (t=="kambizem" and ("luvick" in p1 or "Aeolic" in wrb)) or (g in ("loess","loesslehm") and t in ("kambizem","pseudoglej","hnědozem","luvizem"))) \
        and not re.search(r"arenick|psefit|litick|rankerov",p1)
    return int(sauer),int(basisch),int(wasser)
if __name__=="__main__":
    u=pd.read_parquet("cz_units2.parquet"); r=[pz(x) for x in u.itertuples()]
    u["s"],u["b"],u["w"]=zip(*r); tot=u.km2.sum()
    for c,n in (("s","sauer"),("b","basisch"),("w","Wasserspeicher")): print(n, round(u[u[c]==1].km2.sum()), "km²", round(u[u[c]==1].km2.sum()/tot*100,1),"%")
    print("sauer und basisch zugleich:", round(u[(u.s==1)&(u.b==1)].km2.sum()))
