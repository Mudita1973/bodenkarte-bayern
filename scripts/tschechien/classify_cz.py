"""Zuordnung der ČGS-Bodeneinheiten (TKSP, Bodenkarte 1:50 000) zu Soilscapes-Klassen,
analog zum bayerischen Regelwerk (classify.py), nach dem Dokument „Soilscapes-Klassen in deutsche Bodentypen (KA5) übertragen“."""
import re

ACID=re.compile(r"žul|granit|granodiorit|rul[ay]?\b|rula|pararul|ortorul|migmatit|svor|fylit|fylonit|kvarcit|granulit|křemen[cn]|metagranit|porfyr|ryolit|rohovec|drob|břidlic|pískovc[eiů]? křem|pískovce křem|arkóz|kyselé horniny|kyselé metamorf|minerálně chudé|anatexit|aplit|pegmatit|greisen",re.I)
BASIC=re.compile(r"amfibol(?!-biotit)|amfibolit|bazalt|čedič|diabas|gabr|serpentinit|dioritu?\b|andezit|eklogit|tefrit|bazick|ultrabaz|metabazit|spilit|pyroklast|tuf|fonolit|lamprofyr|foidit|analcim|nefelin|bazanit|leucit|lahar",re.I)
CARB=re.compile(r"vápen|vápnit|slín|dolomit|opuk|travertin|mramor|krystalick[éý] vápen|spraš(?!ov)|karbonát|kalc",re.I)
LOESS=re.compile(r"spraš",re.I)
LOOSE=re.compile(r"písek|písk[uy]",re.I)
SAND=re.compile(r"písek|písk[uy]|(?<!hlinito-)písč(?!ito-hlinit)|navátý|štěrkopís|arenick|psamit",re.I)
SKEL=re.compile(r"suť|sutě|kamenit|balvan|blok|skelet|psefit|eluvi",re.I)
CLAY=re.compile(r"jíl(?!ovit[ýé] pís)|pelit|pelick|slín",re.I)
COVER=re.compile(r"nivní|deluvi|koluvi|hlín|sediment|polygenet|navátý|navážka|rašelin|slatin|hnilokal|antropogen",re.I)
def grp(sub, geotxt):
    t=sub if sub else geotxt
    if not t: return "?"
    if CARB.search(t): return "carb" if not LOESS.search(t) else "loess"
    if LOESS.search(t): return "loesslehm"
    if BASIC.search(t) and not ACID.search(t): return "basic"
    if LOOSE.search(t) and not re.search(r"pískov",t,re.I): return "sand"
    if ACID.search(t) and not COVER.search(t if sub else "") : return "acid"
    if SAND.search(t): return "sand"
    if CLAY.search(t): return "clay"
    if SKEL.search(t): return "skel"
    return "loam" if re.search(r"hlín|hlinit|sediment|polygenet|koluvi|deluvi|nivní",t,re.I) else "other"
M1={"pseudogleje s kambizeměmi oglejenými":("pseudoglej modální","kambizem oglejená"),
    "kambizemě dystrické":("kambizem dystrická",None),"kambizemě modální mesobazické":("kambizem modální mesobazická",None),
    "luvizemě s luvizeměmi oglejenými":("luvizem modální","luvizem oglejená"),"kryptopodzoly s podzoly":("kryptopodzol modální","podzol modální"),
    "organozemě":("organozem",None),"kambizemě s podzoly na terasových uloženinách":("kambizem arenická","podzol arenický"),
    "podzoly":("podzol modální",None),"kambizemě s rankery a litozeměmi":("kambizem rankerová","ranker modální"),
    "rendziny":("rendzina modální",None),"podzoly, rankery a litozemě (alpinské půdní formy)":("podzol modální","ranker modální"),
    "fluvizemě":("fluvizem modální",None),"hnědozemě":("hnědozem modální",None)}
def classify(u):
    s=lambda v: v if isinstance(v,str) else ""
    p1=s(u["p1"]).strip(); p2=s(u["p2"]); p3=s(u["p3"]); grp=u["grp"]; sub=s(u["sub"]); geo=not sub
    rest=(p2+" "+p3)
    one=u["src"]=="1M"
    acid=grp=="acid"; basic=grp=="basic"; carb=grp in ("carb","loess"); sand=(grp=="sand" and not geo and not re.search(r"jílovit|hlinit",sub)) or bool(re.search(r"arenick|psefitick",p1))
    if geo and grp=="loess" and re.search(r"mesobaz|dystrick|oligotrof",p1): carb=False
    def r(k,why,sure=True):
        if one: why="Lückenfüllung aus der Übersichtskarte 1:1 Mio.: "+why; sure=False
        elif geo and k in ("13","7","6","14") and grp in ("acid","basic","carb","loess"):
            why+=" (Gestein aus der geologischen Karte 1:50 000, weil die Bodenkarte hier kein Substrat nennt)"; sure=False
        return k,why,sure
    t=p1.split()[0] if p1 else ""
    sub_=p1[len(t):]
    weak="slabě oglej" in p1
    gleyed=("oglejen" in p1 or "oglejený" in p1) and not weak
    pods="podzolovan" in p1; skel=bool(re.search(r"ranker|litick|suťov|psefit",p1)) or bool(re.search(r"Skeletic|Leptic|Lithic",s(u["wrb"])))
    if p1 in ("vodní plochy",): return r("W","Gewässer")
    if t=="antropozem": return r("X","Antropozem: Aufschüttung, Halde, Abbau oder Siedlung")
    if t=="organozem": return r("M","Organozem: Moorboden mit mächtigem Torf, keine der Dokumentklassen")
    # Klasse 2: sehr flachgründige Böden auf saurem Fels
    if t=="litozem":
        if acid: return r("2","Litozem (sehr flachgründiger Boden direkt auf Fels) auf saurem Gestein: nächste Entsprechung zum Felshumusboden",sure=False)
        return r("0","Litozem auf nicht saurem Gestein: laut Dokument nicht sauer genug")
    # Klasse 16 und 15: nasse, sehr saure Böden mit Torf oder Anmoor
    hist=bool(re.search(r"histick|zrašel",p1))
    if t=="stagnoglej" or (t=="glej" and hist):
        if acid and not carb and (t=="stagnoglej" or re.search(r"pseudoglej|stagnoglej|podzol",rest)):
            return r("16","Stagnoglej bzw. Glej mit Torfauflage im Verbund mit Stau- oder Podsolböden auf saurem Gestein: nächste Entsprechung zu Stagnogley-Podsol/Moorstagnogley",sure=False)
        if carb: return r("0","nasser Torfboden, aber kalkhaltig: nicht sehr sauer")
        if t=="stagnoglej": return r("8","Stagnoglej (stark staunass) ohne saures Gestein: gehemmte Entwässerung",sure=False)
        return r("15","Glej mit Torfauflage (histický/zrašelinělý) ohne Kalk: von Natur aus nasser, saurer Boden, entspricht Anmoor- bzw. Moorgley")
    if t=="podzol" and re.search(r"oglejen|glejov",p1):
        return r("15","Podsol mit Stau- oder Grundwassereinfluss (podzol oglejený/glejový): nasser, sehr saurer Sandboden; Dokument nennt für 15 Gley-Podsol",sure=False)
    if t=="podzol" and hist:
        return r("15","Podsol mit Torfauflage: nasser, sehr saurer Boden",sure=False)
    if t=="kryptopodzol" and gleyed:
        return r("15","Kryptopodsol mit Stauwasser: nasser, sehr saurer Boden",sure=False)
    if t in ("glej","fluvizem","černice","koluvizem","černozem") or (t=="kambizem" and re.search(r"glejov|fluvick",p1)):
        return r("0","Grundwasser-, Auen- oder Schwarzerdeboden ohne Torf: keine der Dokumentklassen")
    # Klasse 14: Podsole, Kryptopodsole, podsolige Sandböden
    if t=="podzol" and not carb: return r("14","Podsol: gut durchlässiger, sehr saurer Boden (Suchbegriff ‚Podsol‘)")
    if t=="kryptopodzol" and not carb:
        return r("14","Kryptopodsol (Entic Podzol, entspricht etwa Braunerde-Podsol bzw. Podsol-Braunerde): sehr sauer, im bayerischen Regelwerk Klasse 14")
    if t in ("kambizem","regozem","luvizem") and sand and (pods or re.search(r"podzol",rest)) and not carb:
        return r("14","sandige Braunerde bzw. Regosol, podsolig: sandiger, saurer Oberboden")
    # Klasse 8: Staunässe
    if t=="pseudoglej":
        if acid and not carb: return r("8","Pseudogley auf saurem Gestein: im Dokument nur als Klasse 8 erfasst, tatsächlich saurer als ‚schwach sauer‘",sure=False)
        return r("8","Pseudogley: Lehm- und Tonboden mit gehemmter Entwässerung")
    if t in ("kambizem","luvizem","hnědozem","regozem") and gleyed:
        return r("8","Braunerde bzw. Parabraunerde mit Stauwasser im Unterboden (TKSP ‚oglejená‘, entspricht etwa Pseudogley-Braunerde): gehemmte Entwässerung",sure=False)
    # Klasse 7 und 13: Braunerden, Ranker, Regosole nach Gestein
    br=t in ("kambizem","ranker","regozem")
    dyst=bool(re.search(r"dystrick|oligotrof",p1))
    if t=="kambizem" and ("luvick" in p1 or "Aeolic" in s(u["wrb"])):
        return r("6","Braunerde mit Tonverlagerung bzw. Lösslehmdecke (kambizem luvická, WRB ‚Aeolic‘): schwach saurer Lehmboden, im bayerischen Regelwerk sauer + Löss = Klasse 6",sure=False)
    if br and "eutrofn" in p1 and not sand:
        return r("7",f"{t.capitalize()}, laut Bodenkarte basenreich (eutrofní)")
    if br and (dyst or ("rankerov" in p1 and not basic)) and grp in ("acid","basic","other","skel"):
        why={"kambizem":"Braunerde","ranker":"Ranker","regozem":"Regosol"}[t]+(" basenarm (dystrisch)" if dyst else " flachgründig (rankerová)")+" über Festgestein: saurer Lehm über Fels"
        return r("13",why,sure=grp=="acid")
    if br and basic and not carb:
        return r("7",f"{t.capitalize()} aus basenreichem Gestein (Basalt, Amphibolit, Diabas, Alkalivulkanite u. a.)")
    if t in ("kambizem","hnědozem","pararendzina") and carb: return r("7","Braunerde bzw. Parabraunerde über Kalk, Mergel oder Löss: basenreich")
    if t=="hnědozem": return r("6","Hnědozem (Parabraunerde aus Lösslehm) ohne Kalk im Oberboden: schwach saurer Lehmboden",sure=False)
    if t=="kambizem" and "arenick" in p1 and not pods and not carb:
        return r("0","sandige Braunerde (arenická) ohne Podsolierung: eher Soilscapes-Klasse 10, die im Dokument fehlt; Klasse 13 verlangt Lehm",sure=False)
    if br and acid and not carb:
        why={"kambizem":"Braunerde","ranker":"Ranker","regozem":"Regosol"}[t]+" aus saurem Silikatgestein (Granit, Gneis, Glimmerschiefer, Phyllit, Quarzsandstein u. a.)"
        if pods: why+=", podsolig"
        if skel: why+=", steinig bzw. flachgründig"
        return r("13",why)
    if t in ("ranker","regozem"): return r("0",f"{t.capitalize()} ohne saures oder basenreiches Gestein: keine der Dokumentklassen")
    if t in ("rendzina","pararendzina","šedozem","smonice"): return r("0","kalkhaltiger oder toniger Boden ohne Entsprechung im Dokument")
    # Klasse 6 und 14: Braunerden und Parabraunerden aus Lehm
    if t in ("kambizem","luvizem"):
        if sand: return r("0","Braunerde aus Sand ohne Podsolierung: eher Soilscapes-Klasse 10, die im Dokument fehlt")
        if pods: return r("14","podsolige Braunerde aus Lehm, nicht über saurem Gestein: Podsolierung schließt 6 aus",sure=False)
        if re.search(r"dystrick|oligotrof",p1): return r("6","basenarme Braunerde bzw. Parabraunerde aus Lehm (dystrisch): schwach bis stark sauer, als Klasse 6 eingeordnet",sure=False)
        return r("6","Braunerde bzw. Parabraunerde aus Lehm, ohne Kalk, ohne Podsolierung")
    return r("0","keine eindeutige Entsprechung")
