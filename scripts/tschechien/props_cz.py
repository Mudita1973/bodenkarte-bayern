import pandas as pd, numpy as np, json, re
u=pd.read_parquet("cz_units.parquet").sort_values("km2",ascending=False)
TYP={"kambizem":"Braunerde (Kambizem)","kryptopodzol":"Kryptopodsol (etwa Braunerde-Podsol)","podzol":"Podsol","pseudoglej":"Pseudogley","stagnoglej":"Stagnogley",
 "glej":"Gley","luvizem":"Parabraunerde, stark lessiviert (Luvizem)","hnědozem":"Parabraunerde aus Löss (Hnědozem)","ranker":"Ranker","litozem":"Felshumusboden bzw. Syrosem (Litozem)",
 "regozem":"Regosol","rendzina":"Rendzina","pararendzina":"Pararendzina","organozem":"Moorboden (Organozem)","fluvizem":"Auenboden (Fluvizem)","černice":"Tschernitza (Černice)",
 "černozem":"Tschernosem","antropozem":"Aufschüttungsboden (Antropozem)","koluvizem":"Kolluvisol","šedozem":"Grauerde (Šedozem)","vodní":"Gewässer"}
SUBT=[("slabě oglejen","schwach staunass"),("slabě glejov","schwach grundwasserbeeinflusst"),("oglejen","staunass"),("glejov","grundwasserbeeinflusst"),("modální","typisch"),("dystrick","basenarm (dystrisch)"),
 ("oligotrof","sehr basenarm (oligotroph)"),("mesobazick","mittel basenhaltig"),("eutrof","basenreich (eutroph)"),("eubazick","basenreich"),("podzolov","podsolig"),("rankerov","flachgründig, steinig"),
 ("arenick","sandig"),("pelick","tonig"),("psefitick","kiesig bzw. grusig"),("luvick","lessiviert"),("kambick","verbraunt"),("histick","mit Torfauflage"),("zrašel","vertorft"),("fluvick","auentypisch"),
 ("litick","flachgründig über Fels"),("suťov","aus Schutt"),("železit","eisenreich"),("humózn","humusreich"),("kaolinick","kaolinitisch"),("hořečnat","magnesiumreich"),("akvick","sehr nass"),
 ("umbrick","mit dunklem, saurem Humushorizont"),("karbonátov","carbonathaltig"),("vyluhovan","entkalkt"),("mesick","mäßig zersetzt"),("fibrick","wenig zersetzt"),("saprick","stark zersetzt"),("melanick","humos"),("planick","Plateau-Gley")]
def de(p1):
    if not isinstance(p1,str) or not p1: return "Bodentyp ohne Angabe"
    w=p1.split(); t=w[0]; base=TYP.get(t,t)
    adds=[]; rest=p1[len(t):]
    for k,v in SUBT:
        if k in rest and v not in adds:
            if k=="oglejen" and "schwach staunass" in adds: continue
            if k=="glejov" and "schwach grundwasserbeeinflusst" in adds: continue
            adds.append(v)
    return base+(", "+", ".join(adds) if adds else "")
GRP={"acid":"saures Silikatgestein","basic":"basenreiches Gestein","carb":"Kalk, Mergel","loess":"Löss","loesslehm":"Lösslehm","sand":"Sand, Kies","clay":"Ton","skel":"Schutt, Grus","loam":"Lehm (Deckschicht)","other":"sonstiges Gestein","?":"ohne Angabe"}
def flags(r):
    s=lambda v: v if isinstance(v,str) else ""
    p1=s(r.p1); p2=s(r.p2); p3=s(r.p3); allp=" ".join([p1,p2,p3]); t=p1.split()[0] if p1 else ""; w=s(r.wrb)
    weak="slabě oglej" in p1
    F=dict(br=t in("kambizem","luvizem","hnědozem"), ranker=t in("kambizem","ranker","regozem"), felshumus=t=="litozem" or "litick" in p1,
      podsol=("podzol" in allp) or ("podzolov" in allp), podsol_main=t in("podzol","kryptopodzol"),
      stau_main=t in("pseudoglej","stagnoglej") or (("oglejen" in p1 or "oglejený" in p1) and not weak), gw_main=t in("glej","fluvizem","černice") or "glejov" in p1,
      anmoor=bool(re.search(r"histick|zrašel",p1)), torf=t=="organozem" or bool(re.search(r"histick|zrašel",p1)), hochmoor="fibrick" in p1, stagnogley=t=="stagnoglej",
      kalk=r.grp in("carb","loess") or "karbonát" in p1, basisch=r.grp=="basic", acid=r.grp=="acid", loess=r.grp in("loess","loesslehm"),
      sandig=r.grp=="sand" or "arenick" in p1 or "Arenic" in w, tonig=r.grp in("clay","loam","loesslehm","other") or "pelick" in p1,
      lehmig=r.grp in("loam","loesslehm","other") and "arenick" not in p1, skelett=bool(re.search(r"ranker|litick|suťov|psefit",p1)) or r.grp=="skel" or bool(re.search(r"Skeletic|Leptic|Lithic",w)),
      dyst=bool(re.search(r"dystrick|oligotrof",p1)) or "Dystric" in w, eutr=bool(re.search(r"eutrof|eubazick",p1)) or "Eutric" in w)
    return F
def criteria(F,h,neig,p5):
    hoch=h is not None and h>=700
    C={"6":[("Hauptboden Braunerde oder Parabraunerde",F["br"]),("lehmige Bodenart",F["lehmig"]),("kein Kalk",not F["kalk"]),("nicht podsolig",not F["podsol"]),("kein Stau-/Grundwasser im Hauptboden",not(F["stau_main"] or F["gw_main"])),("nicht basenarm laut Bodenkarte (nicht dystrisch)",not F["dyst"])],
       "7":[("Hauptboden Braunerde oder Parabraunerde",F["br"]),("basenreich (Kalk, Löss oder basisches Gestein)",F["kalk"] or F["basisch"]),("nicht podsolig",not F["podsol"]),("kein Stau-/Grundwasser im Hauptboden",not(F["stau_main"] or F["gw_main"])),("basenreich laut Bodenkarte (eutroph)",F["eutr"])],
       "8":[("Stauwasser im Hauptboden",F["stau_main"]),("Lehm oder Ton",F["tonig"]),("nicht sehr sauer (kein saures Kristallin, kein Podsol)",not(F["acid"] or F["podsol_main"]))],
       "13":[("Braunerde, Ranker oder Regosol",F["ranker"]),("saures Silikatgestein",F["acid"]),("Grus, Schutt oder skeletthaltig",F["skelett"]),("kein Kalk, Mergel oder Basalt",not(F["kalk"] or F["basisch"])),("kein Löss",not F["loess"]),("Hanglage: ≥ 50 % der Fläche mit ≥ 5° Neigung (DMR 4G, 100 m)",p5>=0.5)],
       "14":[("Podsol oder podsolig",F["podsol"] or F["podsol_main"]),("sandig",F["sandig"]),("kein Stau-/Grundwasser im Hauptboden",not(F["stau_main"] or F["gw_main"])),("kein Kalk",not F["kalk"])],
       "15":[("Grundwasser- oder Anmoorboden",F["gw_main"] or F["anmoor"]),("Sand oder Lehm",F["sandig"] or F["tonig"]),("sehr sauer (kein Kalk)",not F["kalk"]),("Podsol oder Anmoor genannt",F["podsol"] or F["anmoor"])],
       "16":[("Anmoor, Moorgley oder Stau mit Torf",F["anmoor"] or (F["stau_main"] and F["torf"])),("saures Silikatgestein",F["acid"]),("Hochlage ab 700 m",hoch),("kein Kalk oder Basalt",not(F["kalk"] or F["basisch"])),("kein Hochmoor",not F["hochmoor"])],
       "2":[("Felshumusboden, Ranker oder Litozem",F["felshumus"]),("saures Gestein",F["acid"]),("Hochlage ab 700 m",hoch),("kein Kalk",not F["kalk"])],
       "19":[("Stagnogley oder Moorstagnogley",F["stagnogley"]),("Torf oder Anmoor an der Oberfläche",F["torf"] or F["anmoor"]),("saures Silikatgestein",F["acid"]),("Plateaulage: mittlere Neigung < 3°",neig<3)]}
    return C
def fmt(x,d=0): return f"{x:.{d}f}".replace(".",",")
units={}; legs={}; match={}; critnames=None
for i,r in enumerate(u.itertuples()):
    leg=str(i+1); legs[r.Index]=leg
    s=lambda v: v if isinstance(v,str) else ""
    code=s(r.code); sub=s(r.sub)
    dom=de(r.p1); p2=de(r.p2) if s(r.p2) else ""; p3=de(r.p3) if s(r.p3) else ""
    src="Übersichtskarte 1:1 Mio. (Lückenfüllung)" if r.src=="1M" else "Bodenkarte 1:50 000"
    text=f"{dom}"+(f", begleitend {p2}" if p2 else "")+(f", ergänzend {p3}" if p3 else "")
    text+=f" · {s(r.p1)}"+(f" + {s(r.p2)}" if s(r.p2) else "")+(f" ({code})" if code else "")
    text+=(f" · Substrat: {sub}" if sub else f" · Gestein (geol. Karte): {GRP.get(r.grp,r.grp)}")+f" · {src}"
    F=flags(r)
    stau="staunass (Pseudogley-Merkmal)" if F["stau_main"] else "grundwasserbeeinflusst" if F["gw_main"] else "Torf bzw. Anmoor" if F["torf"] else "ohne Nässemerkmal (terrestrischer Boden)"
    sae=[]; 
    _p1=s(r.p1); _wb=(" · WRB "+s(r.wrb) if s(r.wrb) else "")
    if re.search(r"dystrick|oligotrof",_p1): sae.append({"art":"basenarm laut Bodenkarte (dystrisch bzw. oligotroph)","status":"genannt","beleg":_p1+_wb})
    elif "mesobazick" in _p1: sae.append({"art":"mittel basenhaltig laut Bodenkarte (mesobasisch)"+(", im WRB-Namen „Dystric“ (Basensättigung unter 50 %)" if "Dystric" in s(r.wrb) else ""),"status":"genannt","beleg":_p1+_wb})
    elif F["dyst"]: sae.append({"art":"basenarm laut WRB-Name der Bodenkarte („Dystric“, Basensättigung unter 50 %)","status":"genannt","beleg":_p1+_wb})
    if F["eutr"]: sae.append({"art":"basenreich laut Bodenkarte (eutroph)","status":"genannt","beleg":s(r.p1)+(" · WRB "+s(r.wrb) if s(r.wrb) else "")})
    if F["podsol"]: sae.append({"art":"sauer: Podsolierung genannt","status":"genannt","beleg":s(r.p1)})
    if F["kalk"]: sae.append({"art":"basisch: Kalk oder Löss im Substrat","status":"genannt" if sub else "abgeleitet","beleg":sub or "geologische Karte 1:50 000"})
    if F["acid"] and not F["dyst"]: sae.append({"art":"eher sauer: basenarmes Ausgangsgestein","status":"genannt" if sub else "abgeleitet","beleg":sub or "geologische Karte 1:50 000"})
    saew="; ".join(b["art"] for b in sae) or "keine Angabe"
    lage="Hang- und Steillage" if r.p5>=0.5 else ("eben bis flach" if r.neig<2 else "flach bis mäßig geneigt")
    P={"bodentyp":{"wert":dom,"detail":text,"status":"genannt","beleg":s(r.p1),"hinweis":("WRB 2022: "+s(r.wrb)) if s(r.wrb) else "", "regel":"Dominante Bodeneinheit der ČGS-Bodenkarte (TKSP), deutsche Bezeichnung als Näherung"},
       "textur":{"wert":(sub or "keine Angabe"),"oberboden":"","status":"genannt" if sub else "fehlt","beleg":sub,"regel":"Bodensubstrat laut ČGS-Bodenkarte (Feld n_txt bzw. sg_txt)"},
       "wasserhaushalt":{"wert":stau,"status":"abgeleitet","belege":[{"art":stau,"ort":"Bodentyp","beleg":s(r.p1)}] if stau!="ohne Nässemerkmal (terrestrischer Boden)" else [],"regel":"Aus Bodentyp und Subtyp (oglejená, glejová, histická) der TKSP-Klassifikation"},
       "organik":{"wert":"Torf bzw. Torfauflage genannt" if F["torf"] else "keine Angabe","status":"genannt" if F["torf"] else "fehlt","belege":[{"art":"Torf","beleg":s(r.p1)}] if F["torf"] else [],"regel":"Organische Auflagen laut Bodentyp"},
       "saeure":{"wert":saew,"status":"genannt" if any(b["status"]=="genannt" for b in sae) else ("abgeleitet" if sae else "fehlt"),"belege":sae,"regel":"Basensättigungsangaben der TKSP-Subtypen (dystrisch, mesobasisch, eutroph) und Indizien aus Gestein und Podsolierung. Für Tschechien gibt es hier keine gemessenen Kennwerte wie die LfU-Basensättigung in Bayern."},
       "moor":{"wert":"Moorboden (Organozem)" if s(r.p1).startswith("organozem") else "kein Moorboden laut Bodenkarte","status":"genannt","treffer":s(r.p1).startswith("organozem"),"beleg":"","regel":"Bodentyp Organozem der ČGS-Bodenkarte"},
       "gestein":{"wert":GRP.get(r.grp,r.grp),"status":"genannt" if sub else "abgeleitet","beleg":(sub if sub else "geologische Karte 1:50 000 am Flächenmittelpunkt"),"regel":"Gesteinsgruppe aus dem Substrat der Bodenkarte, sonst aus der geologischen Karte ČR 1:50 000 (ČGS) am Mittelpunkt der jeweiligen Fläche"},
       "relief":{"wert":f"{lage}: mittlere Neigung {fmt(r.neig,1)}°, {fmt(r.p5*100)} % der Fläche ≥ 5°","status":"berechnet","regel":"Aus dem Höhenmodell DMR 4G (ČÚZK) auf 100 m gemittelt, über alle Flächen der Einheit"}}
    units[leg]={"text":text,"p":P}
    C=criteria(F,r.h,r.neig,r.p5); match[leg]={k:[[n,bool(ok)] for n,ok in c] for k,c in C.items()}
    if critnames is None: critnames={k:[n for n,_ in c] for k,c in C.items()}
u["leg"]=[legs[i] for i in u.index]
u.to_parquet("cz_units2.parquet")
json.dump({"units":units,"match":match,"critnames":critnames},open("props_cz.json","w"),ensure_ascii=False,separators=(",",":"))
print(len(units)); print(units["1"]["text"]); print(units["5"]["text"])
