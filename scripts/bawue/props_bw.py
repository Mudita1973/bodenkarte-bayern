"""Eigenschaften, Kriterien und Pilzgruppen je BK50-Kartiereinheit (Baden-Württemberg)."""
import json, re, numpy as np, pandas as pd
from run_fix_bw import c, s, build, kalk_core, carbsub2, ph
REC=['colon','kalkab','carbsub2','ton','pslast','acidloess','sand','baendchen','anmoorph','podswald','loess','adj','haft','diorit','acidgap','pelpods','acidsand2','sand14','tf7','podsolreg']
c.FIX=dict((f,True) for f in REC); c.FIX['carbsub']=True

U=pd.read_parquet("bw_units_cls.parquet")
A=pd.read_parquet("bw_att.parquet").drop_duplicates("ke").set_index("ke")
A.index=A.index.str.strip()
keys=json.load(open("keys.json")); KE={k.split("|")[0]:k for k in keys}
REL=pd.read_parquet("relief_bw.parquet").set_index("key")

def st(v): return s(v).strip()
def fmt(x,d=0):
    if x is None or x!=x: return "?"
    return f"{x:,.{d}f}".replace(",","X").replace(".",",").replace("X",".")
def num(v):
    try: f=float(str(v).replace(",",".")); return None if f!=f else f
    except Exception: return None

KA5={"Ss":"reiner Sand","Sl2":"schwach lehmiger Sand","Sl3":"mittel lehmiger Sand","Sl4":"stark lehmiger Sand","Slu":"schluffig-lehmiger Sand",
 "St2":"schwach toniger Sand","St3":"mittel toniger Sand","Su2":"schwach schluffiger Sand","Su3":"mittel schluffiger Sand","Su4":"stark schluffiger Sand",
 "Ls2":"schwach sandiger Lehm","Ls3":"mittel sandiger Lehm","Ls4":"stark sandiger Lehm","Lt2":"schwach toniger Lehm","Lt3":"mittel toniger Lehm",
 "Lts":"sandig-toniger Lehm","Lu":"schluffiger Lehm","Uu":"reiner Schluff","Uls":"sandig-lehmiger Schluff","Us":"sandiger Schluff",
 "Ut2":"schwach toniger Schluff","Ut3":"mittel toniger Schluff","Ut4":"stark toniger Schluff","Tt":"reiner Ton","Tl":"lehmiger Ton",
 "Tu2":"schwach schluffiger Ton","Tu3":"mittel schluffiger Ton","Tu4":"stark schluffiger Ton","Ts2":"schwach sandiger Ton","Ts3":"mittel sandiger Ton",
 "Ts4":"stark sandiger Ton","S":"Sand","L":"Lehm","U":"Schluff","T":"Ton","Hh":"Hochmoortorf","Hn":"Niedermoortorf","H":"Torf"}
MAIN={"S":"Sand","L":"Lehm","U":"Schluff","T":"Ton","H":"Torf"}
def ka5(code):
    code=st(code)
    if not code or code=="-" or code.lower()=="kein feinboden": return ""
    return f"{code} ({KA5[code]})" if code in KA5 else code
def boda_text(b):
    """Grobe Lesart von BODA_1: erste Bodenart je Schicht (Schichten durch ';')."""
    out=[]
    for lay in [x for x in st(b).split(";") if x.strip()][:3]:
        tok=re.sub(r"\([^)]*\)","",lay.split(",")[0]).strip()
        parts=[p for p in re.split(r"[-–]",tok) if p]
        m=[re.match(r"[fmg]?([SLUTH])",p) for p in parts]; m=[x.group(1) for x in m if x]
        if m: out.append("–".join(dict.fromkeys(MAIN[x] for x in m)))
    return " über ".join(out)

PH={"8":"schwach alkalisch (pH 7 bis 8)","7":"neutral (pH 7)","6b":"sehr schwach sauer (pH 6,5 bis 7)","6a":"schwach sauer (pH 6 bis 6,5)",
    "6":"schwach bis sehr schwach sauer (pH 6 bis 7)","5":"mittel sauer (pH 5 bis 6)","4":"stark sauer (pH 4 bis 5)","3":"sehr stark sauer (pH 3 bis 4)","2":"äußerst sauer (pH unter 3)"}
PHV={"8":7.5,"7":7.0,"6":6.5,"6b":6.75,"6a":6.25,"5":5.5,"4":4.5,"3":3.5,"2":2.75}
def ph_parse(x):
    """Oberbodenwert: Hauptstufen (ohne Klammer) und stellenweise Stufen (in Klammern)."""
    x=st(x)
    if not x or x=="-": return None
    top=x.split("/")[0]
    main=re.findall(r"6a|6b|[2-8]",re.sub(r"\(.*?\)","",top)); loc=re.findall(r"6a|6b|[2-8]","".join(re.findall(r"\((.*?)\)",top)))
    sub=re.findall(r"6a|6b|[2-8]",x.split("/")[1]) if "/" in x else []
    return {"main":main,"loc":loc,"sub":sub,"raw":x}
def ph_text(x):
    P=ph_parse(x)
    if not P: return None
    o=[PH[v] for v in P["main"]]
    t=" bis ".join(o[:1]+o[-1:]) if len(o)>1 else (o[0] if o else "")
    if P["loc"]: t+=", stellenweise "+" bis ".join(dict.fromkeys(PH[v].split(" (")[0] for v in P["loc"]))
    if P["sub"]: t+="; Unterboden "+" bis ".join(dict.fromkeys(PH[v].split(" (")[0] for v in P["sub"]))
    return t
def ph_range(x):
    P=ph_parse(x)
    if not P or not P["main"]: return None
    v=[PHV[y] for y in P["main"]]; return min(v),max(v)

HUM={"0":"humusfrei","1":"sehr schwach humos (< 1 %)","2":"schwach humos (1 bis 2 %)","3":"mittel humos (2 bis 4 %)","4":"stark humos (4 bis 8 %)",
     "5":"sehr stark humos (8 bis 15 %)","6":"anmoorig (15 bis 30 %)","7":"organisch, Torf (ab 30 %)"}
WHF={"1":"Mull","2":"mullartiger Moder","3":"typischer Moder","4":"rohhumusartiger Moder","5":"Rohhumus","6":"Anmoor","7":"Feuchtmull","8":"Feuchtmoder","9":"Feuchtrohhumus"}
GRU={"1":"sehr flach (< 1,5 dm)","2":"flach (1,5 bis 3 dm)","3":"mittel tief (3 bis 6 dm)","4":"mäßig tief (6 bis 10 dm)","5":"tief (ab 10 dm)"}
DUW={"1":"Unterboden mäßig durchwurzelbar","2":"Unterboden schlecht durchwurzelbar","3":"Unterboden sehr schlecht durchwurzelbar"}
def keylist(x,D):
    x=st(x)
    if not x or x in("-","–"): return ""
    main=[D[v] for v in re.findall(r"\d",re.sub(r"\(.*?\)","",x)) if v in D]
    loc=[D[v] for v in re.findall(r"\d","".join(re.findall(r"\((.*?)\)",x))) if v in D]
    t=" bis ".join(dict.fromkeys(main[:1]+main[-1:])) if main else ""
    if loc: t+=(", " if t else "")+"stellenweise "+", ".join(dict.fromkeys(loc))
    return t
def nfkstufe(v):
    return None if v is None else ("sehr gering" if v<50 else "gering" if v<90 else "mittel" if v<140 else "hoch" if v<200 else "sehr hoch")
def kfstufe(v):
    return None if v is None else ("sehr gering" if v<1 else "gering" if v<10 else "mittel" if v<40 else "hoch" if v<100 else "sehr hoch" if v<300 else "äußerst hoch")

def feats(ke,r,a):
    t=build(r); c.CUR_BODA=s(r.boda) or None
    _,types,dom,first,subst=c.split(t)
    kul=s(r.kuleg); kc=kalk_core(r.kalk,ab=True); cs=carbsub2(r.kalk,kul)
    carb=kc or cs or bool(re.search(r"Rendzina|Terra fusca|Kalkstein|Mergel|Dolomit|Muschelkalk|Kalktuff|Seekreide",t))
    basic=bool(c.BASIC.search(t)) and not (c.ACID.search(t) and not re.search(r"Basalt|Diabas|Amphibolit|Gabbro|Serpentinit",t,re.I))
    acid=(bool(c.ACID.search(t)) or bool(re.search(r"Rhyolith|Migmatit|jungpaläozoisch|Rotliegend|Arkose",t))) and not basic
    loess=bool(c.LOESS.search(t))
    pods="podsol" in dom.lower() or re.search(r"unter Wald (meist |verbreitet |überwiegend |häufig |oft )?(podsolig|Podsol)",types) is not None
    stau=bool(re.search(r"Pseudogley|Stagnogley|Pelosol",dom)) or "pseudovergleyt" in dom
    gw=bool(re.search(r"(?<![Pp]seudo)(?<![Ss]tagno)[Gg]ley|Vega|Auen|Paternia|Kalkpaternia",dom))
    sandy=c.sandy_top(subst)
    b1=re.match(r"[\s(]*[fmg]?([SLUTH])",s(r.boda)); main=b1.group(1) if b1 else ""
    loamy=main in ("L","U","T") or (not main and bool(c.LOAMY.search(subst.split(" über ")[0])))
    clay=bool(re.search(r"Ton|ton|Lehm|lehm|Mergel",subst)) or main in ("L","T")
    gb=num(a.gb1_proz) if a is not None else None
    skel=bool(c.SKEL.search(subst)) or (gb is not None and gb>=10)
    rl=REL.loc[KE[ke]]
    hoch=rl.h==rl.h and rl.h>=700; hang=rl.p5==rl.p5 and rl.p5>=0.5; plat=rl.neig==rl.neig and rl.neig<3
    phw=ph_range(r.phw); phl=ph_range(r.phl)
    vsauer=(phw is not None and phw[1]<=4.5) or (phw is None and acid)
    return dict(br=re.match(c.BR,first) is not None,first=first,dom=dom,carb=carb,kc=kc,basic=basic,acid=acid,loess=loess,pods=pods,stau=stau,gw=gw,
                sandy=sandy,loamy=loamy,clay=clay,skel=skel,hoch=hoch,hang=hang,plat=plat,phw=phw,phl=phl,vsauer=vsauer,
                anm=bool(re.search(r"[Aa]nmoor|[Mm]oorgley|Stagnogley|[Bb]ändchen",dom)),torf=bool(re.search(r"[Aa]nmoor|Torf|[Mm]oor",t)),
                hochmoor=bool(re.search(r"Hochmoor",dom)),ranker=bool(re.search(r"Ranker|Felshumus|Regosol|O/C",first)),stagno=bool(re.search(r"Stagnogley|[Bb]ändchenstau",dom)))

def criteria(F):
    noW=not F["stau"] and not F["gw"]
    return {
     "6":[["Hauptboden Braunerde oder Parabraunerde",F["br"]],["lehmige oder schluffige Bodenart im Oberboden (BK50)",F["loamy"] and not F["sandy"]],
          ["kein Kalk im Oberboden",not F["carb"]],["nicht podsolig",not F["pods"]],["kein Stau- oder Grundwasser im Hauptboden",noW]],
     "7":[["Hauptboden Braunerde oder Parabraunerde",F["br"]],["basenreich (Kalk, Mergel, Löss oder basisches Gestein)",F["carb"] or F["basic"] or F["loess"]],
          ["nicht podsolig",not F["pods"]],["kein Stau- oder Grundwasser im Hauptboden",noW],
          ["unter Wald höchstens mittel sauer (ab pH 5, BK50)",F["phw"] is not None and F["phw"][0]>=5.5]],
     "8":[["Stauwasser im Hauptboden (Pseudogley, Pelosol, pseudovergleyt)",F["stau"]],["Lehm oder Ton",F["clay"]],
          ["nicht sehr sauer (kein saures Kristallin, kein Podsol)",not F["pods"] and not (F["acid"] and F["vsauer"])]],
     "13":[["Braunerde, Ranker oder Regosol",F["br"] or F["ranker"]],["saures Silikatgestein",F["acid"]],["Grus, Schutt oder skeletthaltig",F["skel"]],
           ["kein Kalk, Mergel oder Basalt",not F["carb"] and not F["basic"]],["kein Löss",not F["loess"]],["Hanglage: ≥ 50 % der Fläche mit ≥ 5° Neigung (DGM200)",F["hang"]]],
     "14":[["Podsol oder podsolig",F["pods"]],["sandig (Oberboden laut BK50)",F["sandy"]],["kein Stau- oder Grundwasser im Hauptboden",noW],["kein Kalk",not F["carb"]]],
     "15":[["Grundwasser- oder Anmoorboden",F["gw"] or F["anm"]],["Sand oder Lehm",F["sandy"] or F["loamy"]],["sehr sauer (kein Kalk, unter Wald unter pH 5)",F["vsauer"] and not F["carb"]],
           ["Podsol oder Anmoor genannt",F["pods"] or F["anm"]]],
     "16":[["Anmoor, Moorgley, Stagnogley oder Bändchenstaupodsol",F["anm"]],["saures Silikatgestein",F["acid"]],["Hochlage ab 700 m",F["hoch"]],
           ["kein Kalk oder Basalt",not F["carb"] and not F["basic"]],["kein Hochmoor",not F["hochmoor"]]],
     "2":[["Felshumusboden, Ranker oder Regosol",F["ranker"]],["saures Gestein",F["acid"]],["Hochlage ab 700 m",F["hoch"]],["kein Kalk",not F["carb"]]],
     "19":[["Stagnogley oder Bändchenstaupodsol",F["stagno"]],["Torf oder Anmoor an der Oberfläche",F["torf"]],["saures Silikatgestein",F["acid"]],
           ["Plateaulage: mittlere Neigung < 3°",F["plat"]]]}

def pz(r,F):
    """Pilzgruppen: [sauer Wald, basisch Wald, sauer LN, basisch LN, Wasserspeicher]"""
    def grp(rng):
        if rng is None: return False,False
        return rng[1]<=4.5 and not F["kc"], rng[0]>=6.25 or F["kc"]
    w=F["phw"] if F["phw"] is not None else F["phl"]
    sW,bW=grp(w); sL,bL=grp(F["phl"] if F["phl"] is not None else F["phw"])
    if F["phw"] is None and F["phl"] is None and F["kc"]: bW=bL=True
    n=num(r.nfk1m); k=num(r.kfub)
    return [int(sW),int(bW),int(sL),int(bL),int(n is not None and n>=180 and k is not None and k<40)]

REG_BT="Hauptbodenform der BK50-Kartiereinheit (Feld BOD_T, amtlicher Text). Der Hauptboden ist der erste Bodentyp der Kurzlegende."
units={}; match={}; critnames=None; stats={"pz":np.zeros(5)}
for ke,r in U.iterrows():
    a=A.loc[ke] if ke in A.index else None
    F=feats(ke,r,a); bod=st(r.bod_t); mat=st(r.mat_t); kul=st(r.kuleg)
    P={}
    P["bodentyp"]={"wert":F["first"] or kul.split(" aus ")[0] or "keine Angabe","detail":bod,"status":"genannt","beleg":bod[:400],"regel":REG_BT}
    if r.k in ("X","W"): P["bodentyp"]["hinweis"]="kein natürlicher Boden kartiert"
    fb1=ka5(a.fb1_einf) if a is not None else ""; fb2=ka5(a.fb2_einf) if a is not None else ""
    bt=boda_text(r.boda)
    P["textur"]={"wert":bt or "keine Angabe","oberboden":fb1+(f", darunter {fb2}" if fb2 else ""),"status":"amtlich" if bt else "fehlt",
                 "beleg":st(r.boda),"regel":"Bodenart nach KA5 aus der BK50 (BODA_1, Schichten durch Semikolon getrennt; FB1_EINF/FB2_EINF: typische Bodenart der oberen und mittleren Schicht)."}
    wb=[]
    for pat,art in [(r"Pseudogley|pseudovergleyt|Stagnogley|Stau",'Stauwasser'),(r"(?<![Pp]seudo)(?<![Ss]tagno)[Gg]ley|vergleyt|Auen",'Grundwasser'),(r"[Aa]nmoor|[Mm]oor",'nass, anmoorig')]:
        m=re.search(pat,bod)
        if m: wb.append({"art":art,"ort":"Hauptboden" if re.search(pat,F["dom"]) else "Kartiereinheit","beleg":bod[max(0,m.start()-50):m.end()+40].strip()})
    duw=keylist(a.duwuba,DUW) if a is not None else ""
    if duw: wb.append({"art":duw,"ort":"BK50 (DUWUBA)","beleg":st(a.duwuba)})
    n1=num(r.nfk1m); kub=num(r.kfub)
    P["wasserhaushalt"]={"wert":"; ".join(dict.fromkeys(b["art"]+(" (Hauptboden)" if b["ort"]=="Hauptboden" else "") for b in wb if b["ort"]!="BK50 (DUWUBA)")) or "ohne Nässemerkmal (terrestrischer Boden)",
        "status":"genannt" if wb else "abgeleitet","belege":wb,
        "regel":"Nässemerkmale aus dem Bodentyp der BK50 (Pseudogley, Gley, Anmoor) und der amtlichen Durchwurzelbarkeit. Wasserspeicher und Durchlässigkeit stehen bei den Bodenkennwerten."}
    ob=[]
    if a is not None:
        wh=keylist(a.wahuform,WHF)
        if wh: ob.append({"art":"Waldhumusform "+wh,"beleg":"BK50 WAHUFORM "+st(a.wahuform)})
        hu=keylist(a.humus_ob,HUM)
        if hu: ob.append({"art":"Humus im Oberboden (Acker/Grünland) "+hu,"beleg":"BK50 HUMUS_OB "+st(a.humus_ob)})
    P["organik"]={"wert":"; ".join(o["art"] for o in ob) or "keine Angabe","status":"amtlich" if ob else "fehlt","belege":ob,
                  "regel":"Waldhumusform und Humusstufe des Oberbodens laut BK50 (nach KA5). Der Humusgehalt gilt laut LGRB nur für landwirtschaftlich genutzte Flächen."}
    sb=[]; pw=ph_text(r.phw); pl=ph_text(r.phl)
    if pw: sb.append({"art":"unter Wald: "+pw,"status":"amtlich","beleg":"BK50 PH_WALD "+st(r.phw)})
    if pl: sb.append({"art":"unter Acker und Grünland: "+pl,"status":"amtlich","beleg":"BK50 PH_LN "+st(r.phl)})
    kt=st(r.kalk)
    if kt and kt!="-": sb.append({"art":"Carbonat: "+kt,"status":"amtlich","beleg":"BK50 KALK_T"})
    P["saeure"]={"wert":(f"Wald {pw}" if pw else "")+(("; " if pw else "")+f"Acker/Grünland {pl}" if pl else "") or "keine Angabe",
                 "status":"amtlich" if (pw or pl) else "fehlt","belege":sb,
                 "regel":"pH-Bereich im Oberboden laut BK50, getrennt nach Wald und landwirtschaftlicher Nutzung (LGRB-Schlüssel: 2 äußerst sauer < 3 bis 8 schwach alkalisch 7 bis 8; Klammer = stellenweise). Unter Acker und Grünland ist der pH durch Kalkung meist erhöht, daher zählt der Waldwert. Grenzen des Dokuments: schwach sauer pH 5,5 bis 6,5, sauer 4,5 bis 5,5, sehr sauer < 4,5."}
    mo=re.search(r"Niedermoor|Hochmoor|Übergangsmoor|Moorgley|Anmoor",bod)
    P["moor"]={"wert":(mo.group(0)+(" im Hauptboden" if re.search(mo.group(0),F["dom"]) else " in der Kartiereinheit genannt")) if mo else "kein Moor- oder Anmoorboden genannt",
               "status":"genannt","treffer":bool(mo),"beleg":bod[max(0,mo.start()-60):mo.end()+40].strip() if mo else "","regel":"Moor- und Anmoorböden laut Bodentyp der BK50 (BOD_T)"}
    gw_=[]
    if F["acid"]: gw_.append("saures Silikatgestein oder Sandstein")
    if F["basic"]: gw_.append("basisches Gestein")
    if F["carb"]: gw_.append("Kalk, Mergel oder carbonathaltiges Material")
    if F["loess"]: gw_.append("Löss oder Lösslehm")
    P["gestein"]={"wert":", ".join(gw_) or "keine eindeutige Gesteinsgruppe","status":"amtlich","beleg":mat[:500],
                  "regel":"Ausgangsmaterial der Bodenbildung laut BK50 (MAT_T, amtlicher Text). Die Gesteinsgruppen oben sind daraus abgeleitet (Schlüsselwörter wie Granit, Gneis, Buntsandstein; Kalk, Mergel; Basalt; Löss)."}
    rl=REL.loc[KE[ke]]; rt=st(a.relief) if a is not None else ""
    lage="Hang- und Steillage" if rl.p5>=0.5 else ("eben bis flach" if rl.neig<2 else "flach bis mäßig geneigt")
    P["relief"]={"wert":f"{lage}: mittlere Neigung {fmt(rl.neig,1)}°, {fmt(rl.p5*100)} % der Fläche ≥ 5°, {fmt(rl.p10*100)} % ≥ 10°"+(f"; laut BK50: {rt}" if rt else ""),
                 "status":"berechnet","regel":"Neigung aus dem Höhenmodell DGM200 (BKG, 200-m-Raster), über alle Flächen der Einheit gemittelt; das grobe Raster glättet steile Kleinformen. Dazu die amtliche Reliefbeschreibung der BK50 (RELIEF)."}
    rows=[]
    if a is not None:
        if n1 is not None: rows.append({"n":"nutzbare Feldkapazität bis 1 m","v":f"{fmt(n1)} mm ({nfkstufe(n1)})"})
        if num(a.fk_1m) is not None: rows.append({"n":"Feldkapazität bis 1 m","v":f"{fmt(num(a.fk_1m))} mm"})
        kob=num(a.kf_ob_gw)
        if kob is not None or kub is not None:
            rows.append({"n":"Wasserdurchlässigkeit (kf)","v":(f"Oberboden {fmt(kob)} cm/Tag ({kfstufe(kob)}, Wald/Grünland)" if kob is not None else "")+("; " if kob is not None and kub is not None else "")+(f"Unterboden {fmt(kub)} cm/Tag ({kfstufe(kub)})" if kub is not None else "")})
        g=keylist(a.grund,GRU); gc_=num(a.grund_cm)
        if g or gc_: rows.append({"n":"Gründigkeit","v":(g or "")+(f" (im Mittel {fmt(gc_)} cm)" if gc_ else "")})
        if num(a.gb1_proz) is not None: rows.append({"n":"Grobboden obere Schicht","v":f"{fmt(num(a.gb1_proz))} %"+(f" ({st(a.gb1_einf)})" if st(a.gb1_einf) else "")})
        cw=num(a.corg_ob_w); ca=num(a.corg_ob_a)
        if cw is not None or ca is not None:
            rows.append({"n":"organischer Kohlenstoff Oberboden","v":"; ".join(x for x in [f"{fmt(cw,1)} % (Wald)" if cw is not None else "",f"{fmt(ca,1)} % (Acker)" if ca is not None else ""] if x)})
        if num(a.kak_min) is not None: rows.append({"n":"Kationenaustauschkapazität (pot.)","v":f"{fmt(num(a.kak_min))} bis {fmt(num(a.kak_max))} mmolc/kg"})
        nb=st(a.natbod)
        if nb and nb!="-": rows.append({"n":"natürliche Bodenfruchtbarkeit","v":f"Bewertungsklasse {nb} (0 keine bis 4 sehr hoch, Bodenschutz 23)"})
    P["kennwerte"]={"wert":"","status":"amtlich" if rows else "fehlt","rows":rows,"hinweis":"",
                    "regel":"Amtliche Kennwerte der BK50 (LGRB), abgeleitet aus Bodenart, Humusgehalt und Lagerungsdichte der vorherrschenden Böden (über 75 % Flächenanteil) und an Musterprofilen abgestimmt."}
    u={"text":kul or bod,"p":P,"zc":pz(r,F)}
    if a is not None:
        if st(a.link).startswith("http"): u["pdf"]=st(a.link)
        if st(a.node).startswith("http"): u["node"]=st(a.node)
    units[ke]=u
    C=criteria(F); key=KE[ke]
    match[key]=C
    if critnames is None: critnames={k:[n for n,_ in v] for k,v in C.items()}
    stats["pz"]+=np.array(u["zc"])*r.km2
json.dump({"units":units,"match":{k:{c_:[[n,bool(o)] for n,o in v] for c_,v in C.items()} for k,C in match.items()},"critnames":critnames},
          open("props_bw.json","w"),ensure_ascii=False,separators=(",",":"))
print("Einheiten",len(units),"Pilzgruppen km² [sauerW,basW,sauerLN,basLN,Wasser]",stats["pz"].round(0).tolist())
# Plausibilität: Anteil erfüllter Kriterien der zugeordneten Klasse
ok=[];
for ke,r in U.iterrows():
    if r.k in match[KE[ke]]:
        v=match[KE[ke]][r.k]; ok.append((r.k,sum(o for _,o in v)/len(v),r.km2))
d=pd.DataFrame(ok,columns=["k","f","a"]); print(d.groupby("k").apply(lambda x:round((x.f*x.a).sum()/x.a.sum(),2)).to_dict())
