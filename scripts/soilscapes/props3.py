"""Eigenschaften v3: Legende (props.py) + amtliche LfU-Kennwerte + BAG500-Gestein + Hangneigung (DGM200).
Schreibt props3.json {units, match, critnames} und v3.parquet (Polygone mit neuer Klasse).
"""
import json, re, pandas as pd, numpy as np
from props import props_for, criteria
from bag500 import BAG, SAUER, KRISTALLIN, BASISCH

z = pd.read_csv("zuordnung.tsv", sep="\t", header=None, names=["leg","k","sure","why","text"], dtype=str).drop_duplicates("leg")
old = json.load(open("props.json"))

# ---- LfU-Kennwerte (je Legendeneinheit, getrennt Wald F / Nichtwald NF) ----
cols = ["key","go_ob","go_ub","ca_ob","ca_ub","bs","hu_ob","puffer"]
kw = pd.concat([pd.read_csv(f"ua/k{i}.csv", header=None, names=cols, dtype=str) for i in range(6)])
kw[["leg","fn"]] = kw.key.str.split("|", expand=True)
KW = {}
for _, r in kw.iterrows():
    d = {}
    for c in cols[1:]:
        v = r[c]
        if isinstance(v, str) and v not in ("", "n"): d[c] = float(v)
    if r.go_ob == "n": d["na"] = True
    KW.setdefault(r.leg, {})[r.fn] = d

# ---- BAG500 je Legendeneinheit ----
geo = pd.concat([pd.read_csv(f"ua/g{i}.csv", header=None, names=["leg","sauer","basisch","carb","dom"], dtype=str) for i in range(2)]).set_index("leg")

# ---- Neigung ----
sl_leg = pd.read_parquet("slope_leg.parquet"); sl_key = pd.read_parquet("slope_key.parquet")

def fmt(x, d=0):
    s = f"{x:.{d}f}".replace(".", ",")
    return s

def ka5_bs(v):
    return "sehr gering" if v < 5 else "gering" if v < 20 else "mittel" if v < 50 else "hoch" if v < 80 else "sehr hoch"

def ka5_humus(v):
    return ("sehr schwach humos" if v < 1 else "schwach humos" if v < 2 else "mittel humos" if v < 4 else "stark humos" if v < 8
            else "sehr stark humos" if v < 15 else "extrem humos (Anmoor)" if v < 30 else "Torf (organischer Boden)")

def ka5_grob(v):
    return "sehr schwach" if v < 2 else "schwach" if v < 10 else "mittel" if v < 25 else "stark" if v < 50 else "sehr stark" if v < 75 else "Grobbodenmaterial"

def ka5_carb(v):
    return "carbonatfrei" if v == 0 else "sehr carbonatarm" if v < 0.5 else "carbonatarm" if v < 2 else "carbonathaltig" if v < 10 else "carbonatreich" if v < 25 else "sehr carbonatreich"

PUF = {1:"extrem gering",2:"sehr gering",3:"gering",4:"mittel",5:"hoch",6:"sehr hoch",7:"extrem hoch"}

def pick(leg):
    """Wald-Wert bevorzugt (ungekalkt), sonst Nichtwald"""
    k = KW.get(leg, {})
    return k.get("F", {}), k.get("NF", {})

def x_for(leg, key=None):
    F, N = pick(leg)
    def g(c):
        return F.get(c, N.get(c))
    bs = F.get("bs", N.get("bs")); bs_src = "Wald" if "bs" in F else ("Acker/Grünland" if "bs" in N else None)
    gos = [v for v in [F.get("go_ob"), F.get("go_ub"), N.get("go_ob"), N.get("go_ub")] if v is not None]
    hu = max([v for v in [F.get("hu_ob"), N.get("hu_ob")] if v is not None], default=None)
    ca = min([v for v in [F.get("ca_ob"), N.get("ca_ob")] if v is not None], default=None)
    X = {"bs": bs, "bs_src": bs_src, "go": max(gos) if gos else None, "hu": hu, "ca": ca}
    if leg in geo.index:
        X["sauer"] = int(geo.loc[leg, "sauer"]); X["basisch"] = int(geo.loc[leg, "basisch"])
    s = sl_key.loc[key] if key is not None and key in sl_key.index else (sl_leg.loc[leg] if leg in sl_leg.index else None)
    if s is not None:
        X["neig"] = float(s.neig); X["p5"] = float(s.p5)
    return X

def lt(v, t): return v is not None and v < t
def ge(v, t): return v is not None and v >= t

def criteria3(F, h, X):
    C = criteria(F, h)
    C["6"] += [("Basensättigung ≥ 20 % (LfU-Kennwert, nicht sehr sauer)", ge(X["bs"], 20)),
               ("Oberboden carbonatfrei bis sehr carbonatarm (< 0,5 %)", lt(X["ca"], 0.5))]
    C["7"] += [("Basensättigung ≥ 50 % (LfU-Kennwert, basenreich)", ge(X["bs"], 50))]
    C["8"] += [("Basensättigung ≥ 20 % (LfU-Kennwert, schwach sauer)", ge(X["bs"], 20))]
    C["13"] += [("Basensättigung < 50 % (LfU-Kennwert, basenarm)", lt(X["bs"], 50)),
                ("Grobboden ≥ 10 Vol.-% (LfU-Kennwert, skeletthaltig)", ge(X["go"], 10)),
                ("saures Silikatgestein oder Sandstein ≥ 50 % (BAG500)", ge(X.get("sauer"), 50)),
                ("Hanglage: ≥ 50 % der Fläche mit ≥ 5° Neigung (DGM200)", ge(X.get("p5"), 0.5))]
    C["14"] += [("Basensättigung < 20 % (LfU-Kennwert, sehr sauer)", lt(X["bs"], 20))]
    C["15"] += [("Basensättigung < 20 % (LfU-Kennwert, sehr sauer)", lt(X["bs"], 20))]
    C["16"] += [("Basensättigung < 20 % (LfU-Kennwert, sehr sauer)", lt(X["bs"], 20)),
                ("Humus im Oberboden ≥ 15 % (LfU-Kennwert, Anmoor oder Torf)", ge(X["hu"], 15)),
                ("saures Silikatgestein ≥ 50 % (BAG500)", ge(X.get("sauer"), 50))]
    C["2"] += [("saures Silikatgestein ≥ 50 % (BAG500)", ge(X.get("sauer"), 50))]
    C["19"] += [("Plateaulage: mittlere Neigung < 3° (DGM200)", lt(X.get("neig"), 3)),
                ("Humus im Oberboden ≥ 15 % (LfU-Kennwert)", ge(X["hu"], 15))]
    return C

REGEL_KW = ("Amtliche Bodenkennwerte des LfU (UmweltAtlas Bayern, Dienst boden_kennwerte_ftz), "
            "je ÜBK25-Legendeneinheit getrennt für Wald und Nichtwald; Mittelwert über die Leitprofile der Einheit. "
            "Unter Acker und Grünland ist die Basensättigung durch Kalkung meist erhöht, daher zählt der Waldwert, wo vorhanden.")

def kennwerte_props(leg):
    F, N = pick(leg)
    out = {}
    if (F.get("na") or N.get("na")) and not any(k in F or k in N for k in ("bs","go_ob","hu_ob")):
        return {"hinweis": "Für diese Einheit (Siedlung, Abbau, Sonderfläche) gibt das LfU keine Kennwerte an."}
    def both(c, f, d=0, unit=" %"):
        parts = []
        if c in F: parts.append(("Wald", F[c]))
        if c in N: parts.append(("Acker/Grünland", N[c]))
        return parts
    rows = []
    for c, name, d, cls in [("bs", "Basensättigung (effektiv)", 0, ka5_bs), ("go_ob", "Grobboden Oberboden", 0, ka5_grob),
                            ("go_ub", "Grobboden Unterboden", 0, ka5_grob), ("ca_ob", "Carbonat Oberboden", 1, ka5_carb),
                            ("ca_ub", "Carbonat Unterboden", 1, ka5_carb), ("hu_ob", "Humus Oberboden", 1, ka5_humus)]:
        p = both(c, None)
        if p:
            unit = " Vol.-%" if c.startswith("go") else " Masse-%"
            rows.append({"n": name, "v": "; ".join(f"{fmt(v, d)}{unit} ({cls(v)}, {w})" for w, v in p)})
    if "puffer" in F:
        v = F["puffer"]; rows.append({"n": "Säurepuffervermögen (Wald)", "v": f"Stufe {fmt(v,1)} von 7 ({PUF.get(int(round(v)), '')})"})
    out["rows"] = rows
    return out

def gestein_prop(leg):
    if leg not in geo.index:
        return {"wert": "keine Angabe", "status": "fehlt", "regel": ""}
    r = geo.loc[leg]
    doms = []
    for part in r.dom.split(";"):
        g, p = part.split(":"); doms.append(f"{p} % {BAG.get(g, g)} ({g})")
    s, b = int(r.sauer), int(r.basisch)
    wert = f"{s} % saures Silikatgestein oder Sandstein" + (f", {b} % basisches Gestein" if b else "")
    return {"wert": wert, "status": "amtlich", "beleg": "; ".join(doms),
            "regel": "Bodenausgangsgesteinskarte BAG500 des LfU (UmweltAtlas, Layer bag500_kw), flächengewichtet über die ÜBK25-Flächen dieser Einheit (Flächenschwerpunkt). Sauer = Gruppen 55 Gneis, 56 Granit, 59 Phyllit/Schiefer/Quarzit, 61c und 61d Sandstein. Maßstab 1:500.000, daher nur Übersicht."}

def relief_prop(leg):
    if leg not in sl_leg.index:
        return {"wert": "keine Angabe", "status": "fehlt"}
    s = sl_leg.loc[leg]
    lage = "Hang- und Steillage" if s.p5 >= 0.5 else ("eben bis flach" if s.neig < 2 else "flach bis mäßig geneigt")
    return {"wert": f"{lage}: mittlere Neigung {fmt(s.neig,1)}°, {fmt(s.p5*100)} % der Fläche ≥ 5°, {fmt(s.p10*100)} % ≥ 10°",
            "status": "berechnet",
            "regel": "Aus dem Höhenmodell DGM200 (BKG, 200-m-Raster) berechnet und über alle Flächen der Einheit gemittelt. Das grobe Raster glättet steile Kleinformen: echte Hangneigungen sind meist steiler."}

if __name__ == "__main__":
    # Polygone mit neuer Klasse (Höhenregeln wie v2)
    v = pd.read_parquet("v2.parquet")
    newk = dict(zip(z.leg, z.k)); newwhy = dict(zip(z.leg, z.why))
    v["k"] = v.leg.map(newk)
    k2 = v.k.copy(); why2 = pd.Series("", index=v.index)
    m = (v.leg == "61a") & (v.hoehe < 700); k2[m] = "0"; why2[m] = "Einheit 61a, aber unter 700 m Höhe: laut Dokument liegt Klasse 16 meist oberhalb von etwa 700 bis 800 m"
    m = (v.leg == "75c") & (v.hoehe >= 800); k2[m] = "16"; why2[m] = "Gley und Anmoorgley auf Granit oder Gneis oberhalb von 800 m: nasse, anmoorige Hochlage auf saurem Kristallin, daher Klasse 16 (unsicher, Grundwasser- statt Staunässe)"
    v["k2"] = k2; v["why2"] = why2
    v.to_parquet("v3.parquet")
    v["key_old"] = v.leg + "|" + pd.read_parquet("v2.parquet").k2
    v["hk"] = v.hoehe * v.km2
    agg = v.groupby("key_old").agg(km2=("km2","sum"), hk=("hk","sum"), leg=("leg","first"), k2=("k2","first"))
    agg["h"] = agg.hk / agg.km2

    units = {}; flags = {}
    for _, r in z.iterrows():
        P, Fl = props_for(r.leg, r.text)
        if r.leg in old["units"]:
            P["moor"] = old["units"][r.leg]["p"]["moor"]   # amtliche ÜMBK25-Prüfung übernehmen
        P["gestein"] = gestein_prop(r.leg)
        P["relief"] = relief_prop(r.leg)
        kwp = kennwerte_props(r.leg)
        P["kennwerte"] = {"wert": "", "status": "amtlich" if kwp.get("rows") else "fehlt", "rows": kwp.get("rows", []),
                          "hinweis": kwp.get("hinweis", ""), "regel": REGEL_KW}
        # Säure: amtliche Basensättigung ergänzen
        X = x_for(r.leg)
        if X["bs"] is not None:
            bs = X["bs"]
            stufe = "sehr sauer (genähert < pH 4,5)" if bs < 20 else "sauer (genähert pH 4,5 bis 5,5)" if bs < 50 else "schwach sauer bis neutral (genähert ≥ pH 5,5)"
            P["saeure"]["belege"].insert(0, {"art": f"Basensättigung {fmt(bs)} % ({X['bs_src']}): {stufe}", "status": "amtlich",
                                             "beleg": "LfU-Bodenkennwert (UmweltAtlas)"})
            P["saeure"]["wert"] = f"Basensättigung {fmt(bs)} % ({X['bs_src']}) → {stufe}" + ("; " + P["saeure"]["wert"] if P["saeure"]["wert"] != "keine Angabe" else "")
            P["saeure"]["status"] = "amtlich"
            P["saeure"]["regel"] = ("Amtliche effektive Basensättigung des LfU (Waldwert bevorzugt, weil Acker und Grünland gekalkt werden). "
                                    "Die pH-Zuordnung ist eine Näherung über die übliche Beziehung von Basensättigung und pH in Waldböden; "
                                    "die Grenzen folgen dem Dokument (schwach sauer pH 5,5 bis 6,5, sauer 4,5 bis 5,5, sehr sauer < 4,5). "
                                    "Dazu Indizien aus Bodentyp und Gestein der Legende.")
        units[r.leg] = {"text": r.text.split(": ", 1)[1] if ": " in r.text else r.text, "p": P}
        flags[r.leg] = Fl
    match = {}; critnames = None
    for key, r in agg.iterrows():
        C = criteria3(flags[r.leg], r.h, x_for(r.leg, key))
        match[key] = {k: [[n, bool(ok)] for n, ok in crit] for k, crit in C.items()}
        if critnames is None: critnames = {k: [n for n, _ in crit] for k, crit in C.items()}
    json.dump({"units": units, "match": match, "critnames": critnames}, open("props3.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("Einheiten", len(units), "Schlüssel", len(match))
    print(v.groupby("k2").km2.sum().round(0).to_dict())
