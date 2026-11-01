"""Bodeneigenschaften je ÜBK25-Legendeneinheit mit Belegstatus,
Moorbodenprüfung und Teilmerkmale je Soilscapes-Vergleichskategorie (je Schlüssel leg|klasse).

Belegstatus:
  "genannt"    Merkmal steht wörtlich in der amtlichen Legende (Beleg = Textstelle)
  "abgeleitet" aus genannten Merkmalen erschlossen (z. B. Säure aus Granit), Regel wird angegeben
  "fehlt"      Legende sagt dazu nichts
"""
import re, json, pandas as pd
from classify import split, CARB, BASIC, ACID, buntsandstein

z = pd.read_csv("zuordnung.tsv", sep="\t", header=None, names=["leg","k","sure","why","text"], dtype=str).drop_duplicates("leg")

def snippet(text, m, pad=0):
    a = max(0, m.start()-pad); e = min(len(text), m.end()+pad)
    while a > 0 and text[a-1] not in " ,;(": a -= 1
    while e < len(text) and text[e] not in " ,;)": e += 1
    if e < len(text) and text[e] == ")" : e += 1
    out = text[a:e].strip(" ,;")
    return ("… " if a > 0 else "") + out + (" …" if e < len(text) else "")

def first_hit(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m

def props_for(leg, full):
    t, types, dom, first, subst = split(full)
    P = {}
    # ---------- Bodentyp ----------
    P["bodentyp"] = {"wert": first if first else dom, "detail": types.strip(), "status": "genannt",
                     "beleg": types.strip(), "regel": "Erstgenannter Bodentyp der Legende = Hauptboden"}
    if "Bodenkomplex" in full:
        P["bodentyp"]["hinweis"] = "Bodenkomplex: mehrere Böden kleinräumig gemischt"
    # ---------- Textur / Bodenart ----------
    groups = []
    checks = [("Torf", r"\bTorf"), ("Sand", r"[Ss]and(?!stein)"), ("Lehm", r"[Ll]ehm"), ("Schluff", r"[Ss]chluff"),
              ("Ton", r"(?<![a-zäöü])[Tt]on(?!stein|mergel|schiefer)|[a-z]ton\b"), ("Kies", r"[Kk]ies"),
              ("Grus", r"[Gg]rus"), ("Schutt/Blöcke", r"[Ss]chutt|[Bb]lock")]
    for name, pat in checks:
        if re.search(pat, subst):
            groups.append(name)
    top = re.split(r"\s+über\s+", subst)[0]
    m = re.match(r"^[^()]*?(?:\([^)]*\)\s*)?([A-ZÄÖÜ][^\s,(]*(?:\s+bis\s+-?[^\s,(]+)*)", re.sub(r"^\((grus|kies|skelett|schutt)[^)]*\)\s*", "", top))
    oberboden = m.group(1) if m else top.split(" (")[0]
    P["textur"] = {"wert": ", ".join(groups) if groups else "keine Angabe",
                   "oberboden": oberboden.strip(),
                   "status": "genannt" if groups else "fehlt",
                   "beleg": subst.strip() if subst else "",
                   "regel": "Bodenarten aus dem Substratteil der Legende (nach „aus“)"}
    # ---------- Wasserhaushalt ----------
    wh = []
    def addw(label, pat, where, scope):
        mm = re.search(pat, where)
        if mm: wh.append({"art": label, "ort": scope, "beleg": snippet(where, mm, 25)})
    addw("Stauwasser", r"Pseudogley|pseudovergleyt|pseudovergleit|Stagnogley|Haft-\)?Pseudogley", dom, "Hauptboden")
    addw("Grundwasser", r"(?<!Pseudo)[Gg]ley(?!-Kalkpaternia)|vergleyt|Auengley|Nassgley|Anmoorgley", dom, "Hauptboden")
    addw("Hangwasser/Quellwasser", r"Hang-?\s?oder Quellengley|Hanggley|Quellengley|\(Hang-\)Gley", t, "Legende")
    addw("Überflutung (Aue)", r"Vega|Paternia|Rambla|Tschernitza|Auensediment", t, "Legende")
    addw("dauernass (Moor)", r"Niedermoor|Hochmoor|Übergangsmoor|Torf", t, "Legende")
    rest = types.replace(dom, "")
    if not any(w["ort"] == "Hauptboden" for w in wh):
        mm = re.search(r"Pseudogley|pseudovergleyt|Gley", rest)
        if mm:
            wh.append({"art": "Stau- oder Grundwasser nur in Begleitböden", "ort": "Begleitboden", "beleg": snippet(rest, mm, 25)})
    if wh:
        P["wasserhaushalt"] = {"wert": "; ".join(sorted({w["art"] + (" (Hauptboden)" if w["ort"] == "Hauptboden" else "") for w in wh})),
                               "status": "genannt", "belege": wh,
                               "regel": "Nässemerkmale aus Bodentypnamen nach KA5 (Pseudogley = Stauwasser, Gley = Grundwasser)"}
    else:
        P["wasserhaushalt"] = {"wert": "ohne Nässemerkmal (terrestrischer Boden)", "status": "abgeleitet", "belege": [],
                               "regel": "Kein Stau-, Grund- oder Moormerkmal in der Legende genannt"}
    # ---------- Organik / Torf ----------
    org = []
    for label, pat in [("Torf (Moorboden)", r"\bTorf|Niedermoor|Hochmoor|Übergangsmoor|[Mm]oorgley"),
                       ("Anmoor", r"Anmoor"), ("humusreich", r"[Hh]umusreich|Humusbraunerde|Humuspelosol|Humuspseudogley|Humusgley|Humusparabraunerde|humos"),
                       ("Rohhumus/Tangel", r"Tangel|Rohhumus"), ("Felshumus/Skeletthumus", r"Felshumus|Skeletthumus|O/C-Böden")]:
        mm = re.search(pat, t)
        if mm: org.append({"art": label, "beleg": snippet(t, mm, 25)})
    P["organik"] = {"wert": ", ".join(o["art"] for o in org) if org else "keine Angabe",
                    "status": "genannt" if org else "fehlt", "belege": org,
                    "regel": "Organische Auflagen und Humusformen, soweit in der Legende benannt"}
    # ---------- Säure-Indizien ----------
    s = []
    for label, pat, art in [("sauer: Podsolierung genannt", r"[Pp]odsol", "genannt"),
                            ("kalkhaltig/basisch: Kalk oder Carbonat genannt", r"Rendzina|kalkhaltig|kalkhalig|[Cc]arbonat|Kalkpaternia", "genannt"),
                            ("Kalk erst im Untergrund", r"im Untergrund carbonathaltig|carbonathaltig im Untergrund|Carbonat\(?-?gestein\)? im Untergrund|Carbonat im Untergrund", "genannt")]:
        mm = re.search(pat, t)
        if mm: s.append({"art": label, "status": art, "beleg": snippet(t, mm, 25)})
    if ACID.search(t) or buntsandstein(leg, subst):
        mm = ACID.search(t) or re.search(r"Sand\(?-?stein", subst)
        s.append({"art": "eher sauer: basenarmes Ausgangsgestein", "status": "abgeleitet", "beleg": snippet(t, mm, 20) if mm else "Buntsandstein (Spessart, Rhön-Vorland)"})
    mm = BASIC.search(t)
    if mm: s.append({"art": "basenreich: basisches Ausgangsgestein", "status": "abgeleitet", "beleg": snippet(t, mm, 20)})
    mm = re.search(r"Löss\b|\(Löss\)|Lösslehm", t)
    if mm and "Lösslehm" in mm.group(0):
        s.append({"art": "meist entkalkt: Lösslehm", "status": "abgeleitet", "beleg": snippet(t, mm, 15)})
    P["saeure"] = {"wert": "; ".join(x["art"] for x in s) if s else "keine Angabe",
                   "status": ("genannt" if any(x["status"] == "genannt" for x in s) else ("abgeleitet" if s else "fehlt")),
                   "belege": s,
                   "regel": "Indizien aus Bodentyp und Gestein. Die ÜBK25 nennt keine pH-Messwerte."}
    # ---------- Moorbodenprüfung ----------
    moor = None
    MOORS = [("Hochmoor", r"Hochmoor"), ("Übergangsmoor", r"Übergangsmoor"), ("Niedermoor", r"Niedermoor|Kalkniedermoor"),
             ("Moorgley/Anmoorgley (kohlenstoffreicher Mineralboden)", r"Moorgley|Anmoorgley|Anmoor"),
             ("Torf im Untergrund oder in Begleitböden", r"\bTorf")]
    for where_txt, where in [(dom, "Hauptboden"), (t, "Begleitboden")]:
        for label, pat in MOORS:
            mm = re.search(pat, where_txt)
            if mm:
                moor = {"wert": label, "ort": where, "beleg": snippet(where_txt, mm, 25)}
                break
        if moor: break
    P["moor"] = {"wert": (moor["wert"] + (" (Hauptboden)" if moor and moor["ort"] == "Hauptboden" else " (nur Begleitboden)")) if moor else "kein Moor- oder Anmoorboden genannt",
                 "status": "genannt" if moor else "fehlt",
                 "beleg": moor["beleg"] if moor else "",
                 "treffer": bool(moor),
                 "regel": "Prüfung gegen die amtliche ÜBK25-Legende. Die Übersichtsmoorbodenkarte ÜMBK25 des LfU ist aus der ÜBK25 abgeleitet, wurde hier aber nicht selbst geladen."}
    # Flags für Teilmerkmale
    F = {
        "br": bool(re.match(r"((\(Para-\))?(Para)?[Bb]raunerde|Humusbraunerde|Lockerbraunerde|Humusparabraunerde|Parabraunerde|Pararendzina-Braunerde|Terra fusca-Braunerde|Braunerde-Terra fusca|Pelosol-Braunerde|Braunerde-Regosol)(?![-\w])", first)),
        "ranker": bool(re.match(r"(Braunerde|Lockerbraunerde|Regosol|Braunerde-Regosol|Ranker|Braunerde-Ranker|Podsol-Braunerde)(?![-\w])", first)),
        "felshumus": bool(re.search(r"Felshumusboden|O/C-Böden|Skeletthumusboden|Ranker", dom)),
        "podsol": "podsol" in dom.lower() or bool(re.search(r"unter Wald (meist |verbreitet |überwiegend )?(podsolig|Podsol)", types)),
        "podsol_main": bool(re.match(r"(Podsol|Braunerde-Podsol|Podsol-Braunerde)(?![-\w])", first)),
        "stau_main": any(w["art"] == "Stauwasser" and w["ort"] == "Hauptboden" for w in wh),
        "gw_main": any(w["art"] == "Grundwasser" and w["ort"] == "Hauptboden" for w in wh),
        "anmoor": bool(re.search(r"Anmoor|Moorgley|Moorstagnogley", t)),
        "torf": bool(re.search(r"\bTorf|moor\b", t)),
        "hochmoor": "Hochmoor" in t,
        "stagnogley": "Stagnogley" in t,
        "kalk": bool(CARB.search(t)),
        "basisch": bool(BASIC.search(t)),
        "acid": (bool(ACID.search(t)) or buntsandstein(leg, subst)) and not bool(BASIC.search(t)),
        "loess": bool(re.search(r"Löss", t)),
        "lehmig": bool(re.search(r"[Ll]ehm|[Ss]chluff", top)) and not re.match(r"\(?(Rein)?[Ss]and\b", re.sub(r"^\([^)]*\)\s*", "", top)),
        "tonig": bool(re.search(r"[Ll]ehm|[Tt]on\b|[Tt]on\s|[Ss]chluff", subst)),
        "sandig": bool(re.search(r"[Ss]and(?!stein)", top)),
        "skelett": bool(re.search(r"Grus|grus|Schutt|schutt|[Ss]kelett|Kryo|[Bb]lock|flach", subst)),
    }
    return P, F

# Teilmerkmale je Vergleichskategorie (aus dem Dokument)
def criteria(F, h):
    hoch = h is not None and h >= 700
    C = {
      "6":  [("Hauptboden Braunerde oder Parabraunerde", F["br"]), ("lehmige Bodenart (Lehm, Schluff)", F["lehmig"]),
             ("kein Kalk", not F["kalk"]), ("nicht podsolig", not F["podsol"]), ("kein Stau-/Grundwasser im Hauptboden", not (F["stau_main"] or F["gw_main"]))],
      "7":  [("Hauptboden Braunerde oder Parabraunerde", F["br"]), ("basenreich (Kalk, Löss oder basisches Gestein)", F["kalk"] or F["basisch"]),
             ("nicht podsolig", not F["podsol"]), ("kein Stau-/Grundwasser im Hauptboden", not (F["stau_main"] or F["gw_main"]))],
      "8":  [("Stauwasser im Hauptboden", F["stau_main"]), ("Lehm oder Ton", F["tonig"]), ("nicht sehr sauer (kein saures Kristallin, kein Podsol)", not (F["acid"] or F["podsol_main"]))],
      "13": [("Braunerde, Ranker oder Regosol", F["ranker"]), ("saures Silikatgestein", F["acid"]), ("Grus, Schutt oder skeletthaltig", F["skelett"]),
             ("kein Kalk, Mergel oder Basalt", not (F["kalk"] or F["basisch"])), ("kein Löss", not F["loess"])],
      "14": [("Podsol oder podsolig", F["podsol"] or F["podsol_main"]), ("sandig", F["sandig"]), ("kein Stau-/Grundwasser im Hauptboden", not (F["stau_main"] or F["gw_main"])), ("kein Kalk", not F["kalk"])],
      "15": [("Grundwasser- oder Anmoorboden", F["gw_main"] or F["anmoor"]), ("Sand oder Lehm", F["sandig"] or F["tonig"]), ("sehr sauer (kein Kalk)", not F["kalk"]),
             ("Podsol oder Anmoor genannt", F["podsol"] or F["anmoor"])],
      "16": [("Anmoor, Moorgley oder Stau mit Torf", F["anmoor"] or (F["stau_main"] and F["torf"])), ("saures Silikatgestein", F["acid"]),
             ("Hochlage ab 700 m", hoch), ("kein Kalk oder Basalt", not (F["kalk"] or F["basisch"])), ("kein Hochmoor", not F["hochmoor"])],
      "2":  [("Felshumusboden, Ranker oder O/C-Boden", F["felshumus"]), ("saures Gestein", F["acid"]), ("Hochlage ab 700 m", hoch), ("kein Kalk", not F["kalk"])],
      "19": [("Stagnogley oder Moorstagnogley", F["stagnogley"]), ("Torf oder Anmoor an der Oberfläche", F["torf"] or F["anmoor"]), ("saures Silikatgestein", F["acid"])],
    }
    return C

if __name__ == "__main__":
    v = pd.read_parquet("v2.parquet")
    v["key"] = v.leg + "|" + v.k2
    v["hk"] = v.hoehe * v.km2
    agg = v.groupby("key").agg(km2=("km2", "sum"), hk=("hk", "sum"), leg=("leg", "first"), k2=("k2", "first"))
    agg["h"] = agg.hk / agg.km2
    units = {}; flags = {}
    for _, r in z.iterrows():
        P, F = props_for(r.leg, r.text)
        units[r.leg] = {"text": r.text.split(": ", 1)[1] if ": " in r.text else r.text, "p": P}
        flags[r.leg] = F
    match = {}
    for key, r in agg.iterrows():
        C = criteria(flags[r.leg], r.h)
        match[key] = {k: [[n, bool(ok)] for n, ok in crit] for k, crit in C.items()}
    json.dump({"units": units, "match": match}, open("props.json", "w"), ensure_ascii=False, separators=(",", ":"))
    # Kontrolle
    import collections
    full = collections.Counter(); part = collections.Counter(); area_full = collections.Counter()
    for key, M in match.items():
        for k, crit in M.items():
            sc = sum(ok for _, ok in crit) / len(crit)
            if sc == 1: full[k] += 1; area_full[k] += agg.loc[key, "km2"]
            elif sc >= .75: part[k] += 1
    print("voll:", dict(full)); print("teilw:", dict(part)); print("km² voll:", {k: round(v) for k, v in area_full.items()})
    for l in ["743", "5", "61a", "75c", "424a", "35", "78", "79", "700"]:
        u = units[l]["p"]
        print(l, "|", u["bodentyp"]["wert"], "|", u["textur"]["wert"], "|", u["wasserhaushalt"]["wert"], "|", u["organik"]["wert"], "|", u["saeure"]["wert"], "|", u["moor"]["wert"])
