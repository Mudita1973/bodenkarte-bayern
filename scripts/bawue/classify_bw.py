"""Zuordnung der ÜBK25-Legendeneinheiten zu Soilscapes-Klassen
nach dem Regelwerk "Soilscapes-Klassen in deutsche Bodentypen (KA5) übertragen".
"""
import re, csv

CARB = re.compile(r"Rendzina|kalkhaltig|kalkhalig|[Cc]arbonat|Kalk|[Mm]ergel|Dolomit|Terra fusca|Löss(?!lehm|sand)|Muschelkalk|Malm|Kalktuff|\bAlm\b|Kalkpaternia")
BASIC = re.compile(r"Basalt|Diabas|Amphibolit|Gabbro|Diorit|Eklogit|Serpentinit|Prasinit|Grünschiefer|[Mm]etabasit|\(Meta\)basit|Keratophyr|Hornblendegneis|Kalksilikat|Marmor")
ACID = re.compile(r"Granit|Gneis|Glimmerschiefer|Phyllit|Tonschiefer|Kieselschiefer|Bordenschiefer|Graphitschiefer|Grauwacke|Quarzit|Mylonit|Metarhyolith|Porphyr|Radiolarit|quarzreich|Buntsandstein|Kristallin")
LOESS = re.compile(r"Löss")
SKEL = re.compile(r"Grus|grus|Schutt|schutt|[Ss]kelett|Kryo|[Bb]lock|flach")
SANDY = re.compile(r"Sand|sand|Kies")
LOAMY = re.compile(r"Lehm|lehm|Schluff|schluff|Ton\b|ton\b|Löss")

ACID = re.compile(ACID.pattern, re.I); BASIC = re.compile(BASIC.pattern, re.I)
CUR_BODA = None
SKEL = re.compile(SKEL.pattern+r"|[Zz]ersatz|Hangschutt|steinig")
def buntsandstein(leg, subst=""):
    # Nummernkreis 57x liegt im Spessart/Rhön-Vorland (Buntsandstein); nur Einheiten über Sandstein (Röt-Tone ausgenommen)
    return re.match(r"57\d", leg) is not None and re.search(r"Sand\(?-?stein", subst) is not None

def split(text):
    t = re.sub(r"^[^:]*:\s*", "", text, count=1)
    t = t.replace("Bodenkomplex: ", "")
    m = re.search(r"\s+aus\s+", t)
    types, subst = (t[:m.start()], t[m.end():]) if m else (t, "")
    dom = re.split(r",\s*(?:gering verbreitet|selten|verbreitet|untergeordnet|unter Wald)|\s+(?:und\s+)?(?:gering\s+)?verbreitet\s|\s+vergesellschaftet", types)[0]
    dom = re.sub(r"^(Fast ausschließlich|Vorherrschend|Überwiegend|überwiegend)\s+", "", dom.strip())
    first = re.split(r"\s+und\s+|,\s*", dom)[0].strip()
    first = re.sub(r"^(humusreiche[rs]?|pseudovergleyte|podsolige|kalkhaltige[rs]?|flache[rs]?|\(.*?\))\s*", "", first)
    first = re.sub(r"^(Braunerde|Regosol|Ranker|Pseudogley|Podsol|Gley)(n|e)\b", r"\1", first)
    return t, types, dom, first, subst

_split_by=split
ADJ=re.compile(r"^(mittel|mäßig|sehr|und|bis)\s+(?=(und|bis|mäßig|mittel|tief|flach|sehr)\b)|^(und|bis)\s+|^(stark |sehr |schwach )?(podsolige|erodierte|pseudovergleyte|vergleyte|humose|kalkhaltige|kalkreiche|kalkarme|rötliche|lessivierte|reliktische|degradierte|verbraunte)[rsn]?\s+|^((sehr |mäßig |mittel |mittelgründige |mittel- bis )?(flach|tief)(e[rsn]?)?\s+((und|bis)\s+)?)+",re.I)
def split(text):
    t, types, dom, first, subst = _split_by(text)
    f=dom
    for _ in range(6):
        n=ADJ.sub("",f,count=1)
        if n==f: break
        f=n
    first=re.split(r"\s+und\s+|,\s*",f)[0].strip()
    first=re.sub(r"\s+(mit Bändern|\(.*?\))$","",first)
    if first: first=first[0].upper()+first[1:]
    return t, types, dom, first, subst

def sandy_top(subst):
    top = subst.split(" über ")[0]
    w = re.sub(r"^(\([^)]*\)\s*|flache[mn]?\s+|skelettführende[mn]?\s+|grusführende[mn]?\s+|kiesführende[mn]?\s+)+", "", top.strip())
    return re.match(r"(Rein|Kies|Grus|Lehm|Schutt|Kryo)?-?[Ss]and(?!lehm\b)|\(Grus-\)Sand|Sandgrus|Kiessand|Sandkies|Grussand|Schuttsand|Sand\b", w) is not None

_sandy_text = sandy_top
def sandy_top(subst):
    # BW: Bodenart des Oberbodens direkt aus der BK50 (KA5-Kürzel, z. B. Su2, Ls3, Ut3)
    if CUR_BODA:
        m = re.match(r"[\s(]*([SLUT])[a-z]?", CUR_BODA)
        if m: return m.group(1) == "S"
    return _sandy_text(subst)

BR = r"((Para)?[Bb]raunerde-)?((\(Para-\))?(Para)?[Bb]raunerde|Humusbraunerde|Lockerbraunerde|Humusparabraunerde|Parabraunerde)(?![-\w])"

def classify(leg, text, kalk_core=None):
    t, types, dom, first, subst = split(text)
    t_c = re.sub(r"\(Kalk-\)(?=Sandstein)", "", t)  # optionales „(Kalk-)Sandstein“ macht sandige Podsol-Braunerden nicht kalkhaltig
    carb = bool(CARB.search(t_c)) if kalk_core is None else (kalk_core or bool(re.search(r"Rendzina|Terra fusca|Kalkstein|Mergel|Dolomit|Löss(?!lehm|sand)|Muschelkalk|Kalktuff|Seekreide|Kalk", dom+" "+subst.split(";")[0])))
    basic = bool(BASIC.search(t))
    acid = (bool(ACID.search(t)) or buntsandstein(leg, subst)) and not basic and not ("Schotter" in t and not re.search(r"Granit|Gneis|Schiefer|Grauwacke", t))
    loess = bool(LOESS.search(t))
    pods_dom = "podsol" in dom.lower()
    pods_wald = re.search(r"unter Wald (meist |verbreitet |überwiegend )?(podsolig|Podsol)", types) is not None
    pods_any = re.search(r"(?<!selten )(podsolig|Podsol)", types) is not None
    pseudo_dom = re.search(r"Pseudogley", dom) is not None
    pelosol_dom = re.search(r"Pelosol", dom) is not None
    complex_ = "Bodenkomplex" in text

    def r(k, why, sure=True):
        return k, why, (sure and not complex_)

    # 0) Nicht-Boden, anthropogen, Moore
    if leg in ("998","500"): return r("W", "Gewässer")
    if leg in ("1","2","3","4"): return r("X", "Siedlung, Abtrag, Auftrag oder Hochwasserdamm: bodenkundlich nicht kartiert")
    if leg in ("800",): return r("X", "Gletscher, Firn")
    if leg in ("997a", "997b", "940") or re.match(r"93\d", leg):
        return r("X", "Siedlung, Abbau, Aufschüttung oder Truppenübungsplatz: bodenkundlich nicht differenziert")
    if "Rigosol" in first:
        return r("0", "Rigosol (tief umgebrochener Weinbergs- oder Gartenboden): kartierter, aber menschlich überprägter Boden, im Dokument nicht vorgesehen", sure=False)
    if re.search(r"Hochmoor", dom):
        return r("M", "Hochmoor mit mächtigem Torf: laut Dokument ausgeschlossen (eher britische Klasse ‚Blanket bog‘)")
    if re.search(r"Niedermoor|Übergangsmoor", first) or re.search(r"über Niedermoor|Niedermoore", dom):
        return r("M", "Niedermoor/Übergangsmoor: Torfboden, keine der Dokumentklassen")

    # Einzelfallprüfung (01.11.2026): 574a nach LfU-Kartierpunkten sandig statt lehmig
    if leg == "__nur_bayern__":
        return r("14", "Braunerde und podsolige Braunerde aus Grussand über Buntsandstein. Geprüft an 2.708 LfU-Kartierpunkten: Oberboden zu 82 % Sand und nur 13 % Lehm, 41 % podsolig oder Podsol, 85 % Wald, Basensättigung unter Wald 7 %. Die Soilscapes-Definition trennt 13 (‚loamy‘) und 14 (‚sandy, some loamy‘) über die Bodenart, daher 14. Für 13 sprechen Buntsandstein und Steillage (im Mittel 8,8°)", sure=False)

    # 1) Klasse 2: Felshumus-/Skeletthumusböden über saurem Gestein
    if re.search(r"Felshumusboden|O/C-Böden|Skeletthumusboden", dom):
        if acid and not carb:
            return r("2", "Felshumusboden / O/C-Boden bzw. Ranker auf saurem Gestein (Gipfel- und Blocklagen)")
        return r("0", "Felshumus- oder Rohboden, aber auf Kalk-, Dolomit- oder basenreichem Gestein: laut Dokument nicht sauer genug")

    # 2) Klasse 16: Anmoor/Moor + Stau-/Podsolböden auf saurem Silikatgestein
    if re.search(r"Anmoor|Moorgley|Stagnogley", dom) and re.search(r"Pseudogley|Stagnogley|Podsol", t) and acid and not carb and not basic and not loess:
        return r("16", "Anmoorgley/Pseudogley mit Podsol auf saurem Kristallin über verfestigter Basislage: nächste Entsprechung zu Stagnogley-Podsol/Moorstagnogley", sure=False)

    # 3) Klasse 15: nasse, sehr saure Sand- und Lehmböden (Anmoorgley, Gley-Podsol)
    if re.match(r"(Pseudogley-Podsol|Podsol-Pseudogley)(?![-\w])", first) and not carb:
        return r("15", f"Hauptboden {first}: nasser (Stauwasser), sehr saurer Sandboden; Dokument nennt für 15 Gley-Podsol, hier Stau- statt Grundwasser", sure=False)
    if re.search(r"[Aa]nmoorgley|[Mm]oorgley|Gley-Podsol|Podsol-Gley|Oxigley", dom):
        if carb:
            return r("0", "Anmoorgley, aber kalkhaltig bzw. carbonathaltig: nicht ‚sehr sauer‘")
        return r("15", "Anmoorgley bzw. Moorgley ohne Kalk: von Natur aus nasser, saurer Boden (Suchbegriff ‚Anmoor‘)")
    if re.match(r"Kolluvisol|Kolluvium", first):
        return r("0", "Kolluvisol (umgelagerter Bodenabtrag): im Dokument nicht genannt; vom Aufbau her oft wie Klasse 6", sure=False)
    if re.search(r"Gestörtes Gelände|Bodenmosaik", first):
        return r("0", "Gestörtes Gelände bzw. Bodenmosaik: ursprüngliche Böden stark verändert oder kleinräumig wechselnd", sure=False)
    if re.search(r"(?<![Pp]seudo)(?<!Stagno)(?<!stagno)[Gg]ley|Vega|Paternia|Tschernitza|Rambla|Auenboden|Auengley|Auenbraunerde|Auenpseudogley|Auenrendzina|Auenpararendzina", first):
        return r("0", "Grundwasser- oder Auenboden ohne Anmoor/Podsol: keine der Dokumentklassen")

    # BW: Bändchen- bzw. Bändchenstaupodsol (Hochschwarzwald): Stauwasser über Eisenbändchen, sehr sauer, oft mit Rohhumus- bis Torfauflage
    if re.search(r"[Bb]ändchen", first) and not carb:
        return r("16", "Bändchenstaupodsol: sehr saurer, staunasser Boden des Berglands mit Eisenbändchen und meist mächtiger Rohhumus- bis Torfauflage; nächste Entsprechung zum Stagnopodsol der Klasse 16", sure=False)
    # 4) Klasse 14: Podsol-dominierte bzw. podsolige Sandböden
    if re.match(r"(Podsol|Braunerde-Podsol|Podsol-Braunerde)(?![-\w])", first) and not carb and not basic:
        return r("14", f"Hauptboden {first}: gut durchlässiger, sehr saurer Boden (Suchbegriff ‚Podsol‘)")
    if re.match(r"(Braunerde|Regosol|Braunerde-Regosol)(?![-\w])", first) and (pods_dom or pods_wald) and SANDY.search(subst) \
            and not acid and not carb and not basic and sandy_top(subst):
        return r("14", "Braunerde/Regosol, podsolig, aus Sand (Flug-, Terrassen- oder Keupersand bzw. Molassesand)")

    if re.match(r"(Braunerde|Regosol|Braunerde-Regosol)(?![-\w])", first) and pods_any and sandy_top(subst) \
            and not carb and not basic and not (acid and SKEL.search(subst) and not sandy_top(subst)) and not buntsandstein(leg, subst) and not ACID.search(t):
        return r("14", "Braunerde aus Sand, zumindest teilweise podsolig: sandiger, saurer Oberboden (Klasse 14 statt 6)", sure=False)

    # 5) Klasse 13: saure, steinige Braunerden/Ranker/Regosole über Fels
    if acid and not carb and not loess and re.match(r"(Braunerde|Lockerbraunerde|Regosol|Braunerde-Regosol|Ranker|Braunerde-Ranker|Podsol-Braunerde)(?![-\w])", first) \
            and (pods_dom or pods_wald or SKEL.search(subst) or "Ranker" in t):
        why = "Braunerde/Regosol/Ranker aus Grus oder Schutt saurer Silikatgesteine"
        if buntsandstein(leg, subst): why += " (Buntsandstein)"
        if pods_dom: why += ", podsolig"
        return r("13", why)
    if acid and loess and re.match(BR, first) and not carb and pods_dom:
        return r("13", "Braunerde, podsolig, auf saurem Gestein mit Lösslehmanteil: Podsolierung schließt 6 aus", sure=False)
    if acid and loess and re.match(BR, first) and not carb:
        return r("6", "Braunerde auf saurem Gestein, aber mit Lösslehm: nach Ausschlussregel (‚Löss‘) nicht Klasse 13, daher Klasse 6", sure=False)

    # 6) Klasse 8: Staunässeböden (Pseudogley, Pseudogley-Braunerde/-Parabraunerde)
    if re.match(r"(\(Haft-\))?(Pseudogley|Humuspseudogley|Pelosol-Pseudogley|Braunerde-\(Haft-\)Pseudogley|Braunerde-Pseudogley|Parabraunerde-Pseudogley|Pseudogley-Braunerde|Pseudogley-Parabraunerde|\(Haft-\)Pseudogley-Braunerde|Stagnogley)", first) \
            or (re.match(r"Pelosol|Regosol", first) and "pseudovergleyt" in dom):
        if "Podsol-Pseudogley" in first:
            return r("0", "Podsol-Pseudogley: staunass und sehr sauer, im Dokument nicht behandelt")
        if acid and not carb:
            return r("8", "Staunass auf saurem Kristallin, Schiefer oder Buntsandstein ohne Torfauflage: im Dokument nur als Klasse 8 erfasst, tatsächlich saurer als ‚schwach sauer‘ (britisch eher Klasse 17)", sure=False)
        return r("8", f"Hauptboden {first}: Lehm- und Tonboden mit gehemmter Entwässerung", sure=not re.match(r"Pelosol|Regosol", first))

    if re.match(BR + r"|Pelosol-Braunerde|Pelosol", first) and (pseudo_dom or (pelosol_dom and not carb)) and not pods_dom:
        return r("8", "Pseudogley- oder Pelosolanteil im Hauptboden (z. B. Pseudogley-Braunerde, Braunerde-Pelosol): gehemmte Entwässerung, laut Dokument Klasse 8", sure=False)
    if re.match(BR, first) and "pseudovergleyt" in dom and re.search(r"über\s+(\S+\s+)?(\([^)]*\)\s*)?(Lehmton|Schluffton|Ton|Tonschluff|\(Grus-\)Ton)\b", subst) and not carb:
        return r("8", "Pseudovergleyte Braunerde über Ton: gehemmte Entwässerung (Dokument-Suchmuster ‚über Ton‘)", sure=False)
    if re.match(r"(Regosol|Braunerde-Regosol|Ranker)(?![-\w])", first) and basic and not carb:
        return r("7", f"Hauptboden {first} aus basenreichem Gestein (Basalt, Diabas u. a.)")

    # 7) Klasse 7: basenreiche Braunerden/Parabraunerden
    if re.match(BR + r"|Pararendzina-Braunerde|Terra fusca-Braunerde|Terra fusca-Parabraunerde|Braunerde-Terra [Ff]usca|Pelosol-Braunerde|Pelosol-Parabraunerde", first) and not pods_dom:
        if basic:
            return r("7", "Braunerde aus basenreichem Gestein (Basalt, Diabas, Amphibolit u. a.)")
        if carb and sandy_top(subst) and not LOAMY.search(subst.split(" über ")[0]):
            return r("0", "Braunerde aus Sand über kalkhaltigem Untergrund: weder Lehmboden (6/7) noch podsolig (14), eher Soilscapes-Klasse 10")
        if carb:
            return r("7", "Braunerde bzw. Parabraunerde über Kalk-, Mergel-, Löss- oder carbonatischem Moränenuntergrund: basenreich")

    # 8) Klasse 6: schwach saure Lehmböden
    if re.match(BR + r"|Pelosol-Braunerde", first) and not carb and not basic:
        top = subst.split(" über ")[0]
        if pods_dom:
            return r("14", "Podsolige Braunerde aus Lehm, nicht über saurem Silikatgestein: Podsolierung schließt 6 aus, Dokument nennt für 14 auch Lehmböden", sure=False)
        if (LOAMY.search(top) or CUR_BODA) and not sandy_top(subst):
            if pods_wald:
                return r("6", "Braunerde aus Lehm, unter Wald teils podsolig", sure=False)
            if pods_any:
                return r("6", "Braunerde aus Lehm; Podsol-Braunerde nur als Begleitboden", sure=False)
            return r("6", "Braunerde/Parabraunerde aus Lehm oder Lösslehm, ohne Kalk, ohne Podsolierung")
        if LOAMY.search(subst):
            return r("6", "Braunerde aus Sand über Lehm: Oberboden sandiger als für Klasse 6 typisch", sure=False)
        return r("0", "Braunerde aus Sand ohne Podsolierung: eher Soilscapes-Klasse 10, die im Dokument fehlt")

    if re.search(r"[Rr]endzina|Terra [Ff]usca|Pelosol|Syrosem|Regosol|Ranker", first):
        return r("0", f"Hauptboden {first}: kalkhaltig, tonig oder Rohboden, keine der Dokumentklassen")
    return r("0", "keine eindeutige Entsprechung")

