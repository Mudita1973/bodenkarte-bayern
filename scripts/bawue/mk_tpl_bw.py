"""Erzeugt template_bw.html aus der bayerischen Vorlage template10.html (Fassung Baden-Württemberg)."""
import re, sys
t=open("/home/claude/bk/template10.html",encoding="utf-8").read()
def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n<count or (count==1 and n!=1): sys.exit(f"Treffer {n} statt {count}: {old[:90]!r}")
    t=t.replace(old,new) if count!=1 else t.replace(old,new,1)
def rex(pat,new,flags=re.S):
    global t
    t2,n=re.subn(pat,lambda m:new,t,count=1,flags=flags)
    if n!=1: sys.exit("Muster fehlt: "+pat[:80])
    t=t2
V=open("/home/claude/bw/val_text.txt",encoding="utf-8").read().strip().split("\n") if __import__("os").path.exists("/home/claude/bw/val_text.txt") else ["","",""]
VAL_W, VAL_L, VAL_METH = (V+["","",""])[:3]

# ---- Kopf und Texte ----
rep("<title>Bodenkarte Bayern: Soilscapes-Klassen aus der ÜBK25</title>","<title>Bodenkarte Baden-Württemberg: Soilscapes-Klassen aus der BK50</title>")
rep("<h1>Bodenkarte Bayern</h1>","<h1>Bodenkarte Baden-Württemberg</h1>")
rep('<p class="sub">ÜBK25 (LfU Bayern), verglichen mit','<p class="sub">Bodenkarte 1 : 50 000 (BK50) des Landesamts für Geologie, Rohstoffe und Bergbau (LGRB), verglichen mit')
rep('Nachbarkarten: <a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/" target="_blank" rel="noopener">Westböhmen (Tschechien) →</a> · <a id="otherMap2" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-bw/" target="_blank" rel="noopener">Baden-Württemberg →</a> öffnen denselben Ausschnitt mit denselben Kategorien.',
    'Nachbarkarte: <a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes/" target="_blank" rel="noopener">Bodenkarte Bayern →</a> öffnet denselben Ausschnitt mit denselben Kategorien.')
rex(r'const OTHERS=\[\{id:"otherMap".*?\}\];',
    'const OTHERS=[{id:"otherMap",url:"https://mudita1973.github.io/bodenkarte-bayern/soilscapes/",bb:[47.27,8.97,50.57,13.84],c:"48.95%2C11.40&z=7",lu:{}}];')
rep('placeholder="Ort suchen, z. B. Bodenmais oder 49.07, 13.10"','placeholder="Ort suchen, z. B. Todtnau oder 47.83, 7.94"')
rep('placeholder="Kategorie oder ÜBK25-Einheit: Nummer oder Text"','placeholder="Kategorie oder BK50-Einheit: Kürzel oder Text"')
rep('<option value="dop">Luftbild Bayern (DOP40)</option>','<option value="dop">Luftbild Baden-Württemberg (DOP20)</option>')
rep("Das Luftbild Bayern sucht sich die passende Bildebene selbst; ist der Dienst nicht erreichbar,","Ist das Luftbild des LGL nicht erreichbar,")
rep('<label><input type="checkbox" id="cUnsure" checked> unsichere Zuordnungen blasser</label>','<label><input type="checkbox" id="cUnsure" checked> unsichere Zuordnungen blasser (19,7 % der Fläche)</label>')
rex(r'<p class="note">Quellen: In der Übersicht CORINE Land Cover 5 ha.*?</p>',
 '<p class="note">Quellen: In der Übersicht CORINE Land Cover 5 ha, Stand 2021 (offline enthalten, grob). Ab Zoomstufe 13 die amtliche Bodenbedeckung aus dem ATKIS Basis-DLM (LGL Baden-Württemberg, INSPIRE-Dienst) mit Laub-, Nadel- und Mischwald. Ab Zoomstufe 14 zusätzlich die Schläge aus dem Agrarantrag (FIONA, Antragsjahr 2022, Ministerium für Ländlichen Raum) mit Wiese, Mähweide, Weide, Rebfläche und Ackerfrucht. Die amtlichen Daten werden online geladen. Nicht beantragte Flächen fehlen im Agrarantrag; dort gilt ATKIS.</p>')
rep("Sauer und basisch richten sich nach der gewählten pH-Grundlage, „gute Wasserspeicher“ immer nach den LfU-Wasserwerten.",
    "Sauer und basisch richten sich nach der gewählten pH-Grundlage, „gute Wasserspeicher“ immer nach den Wasserkennwerten der BK50.")
rep("Klick in die Karte: Bodeneigenschaften mit Belegstatus, Moorbodenprüfung, Vergleichskategorien, Höhe, Nutzung und Links.",
    "Klick in die Karte: Bodeneigenschaften mit Belegstatus, Kennwerten der BK50, Vergleichskategorien, Höhe, Nutzung und Links.")

METH='''<div class="in" style="font-size:12.5px;color:var(--text-secondary)">
      <p><b>Grundlage:</b> Bodenkarte 1 : 50 000 (BK50) des LGRB, Stand Juni 2026, 223.102 Flächen in 4.109 Kartiereinheiten, 35.748 km². Zu jeder Einheit gehören der amtliche Bodentyp (Kurzlegende), das Ausgangsmaterial, die Bodenarten nach KA5 und Kennwerte wie pH-Bereich unter Wald und unter Acker oder Grünland, Kalkgehalt, nutzbare Feldkapazität und Wasserdurchlässigkeit.</p>
      <p><b>Belegstatus je Eigenschaft:</b> <span class="badge b-genannt">in Legende genannt</span> steht wörtlich in der BK50 (Bodentyp, Moor). <span class="badge b-amtlich">amtlich (LGRB)</span> ist ein Kennwert oder Schlüssel der BK50 (pH, Bodenart, Humus, Wasser). <span class="badge b-abgeleitet">abgeleitet</span> wurde aus genannten Merkmalen erschlossen; die Regel steht dabei. <span class="badge b-berechnet">berechnet</span> stammt aus dem Höhenmodell.</p>
      <p><b>Zuordnung:</b> jede Kartiereinheit genau eine Kategorie, nach demselben Regelwerk wie in Bayern (Hauptboden, Ausgangsmaterial, Ausschlussbegriffe), ergänzt um die Kennwerte der BK50: Bodenart des Oberbodens für sandig oder lehmig, Kalk ab der Oberfläche, pH unter Wald bei Anmoor und Terra fusca. Neu gegenüber Bayern: Bändchenstaupodsole des Hochschwarzwalds zählen zu Klasse 16 (unsicher), Bändchenpodsole ohne Stauwasser zu 14.</p>
      <p><b>Prüfung:</b> Ein unabhängiger Prüfdurchgang hat die Einheiten mit dem größten Flächenanteil gegen das Dokument geprüft: 88,7 % der geprüften Fläche zutreffend, 7,0 % fraglich, 4,3 % falsch. Daraus folgten 19 Regelkorrekturen (unter anderem Kalk erst ab 4 dm Tiefe zählt nicht als kalkhaltiger Oberboden, Sand-Oberboden auf Buntsandstein ist Klasse 14, Pseudogley am Ende des Bodennamens ist Staunässe). Dadurch wechselten 216 Einheiten mit 3.038 km² die Kategorie. Sieben Einzelfälle mit zusammen 91 km² sind von Hand zugeordnet und als unsicher markiert.</p>
      <p><b>Teilmerkmale:</b> je Kategorie die Merkmale aus dem Dokument, geprüft an Bodentyp, Bodenart, Ausgangsmaterial, pH unter Wald, mittlerer Höhe und Hangneigung (DGM200). Eine Fläche kann mehrere Kategorien teilweise oder ganz erfüllen; Überschneidungen sind gestreift.</p>
      '''+(VAL_METH and f"<p><b>Pilzgruppen an echten Funden geprüft:</b> {VAL_METH}</p>\n      ")+'''<p><b>Höhe am Punkt:</b> DGM200, für die Webkarte auf etwa 400 m vergröbert. <b>Nutzung am Punkt:</b> CORINE 5 ha, Stand 2021, etwa 125 m Raster; ab Zoomstufe 13 ATKIS und Agrarantrag.</p>
      <p><b>Generalisierung:</b> In der Normalansicht sind Flächen unter 15 ha dem Nachbarn mit der längsten gemeinsamen Grenze zugeschlagen (das betrifft 78 % aller Teilflächen, aber nur einen kleinen Teil der Fläche) und die Linien auf etwa 60 m vereinfacht. Flächenangaben stammen aus den ungeneralisierten Daten. <span id="detailNote">Ab Zoomstufe 12 lädt die Karte die Originalflächen nach (Linien auf etwa 10 m vereinfacht, keine Fläche entfernt). In der Landesansicht (unter Zoomstufe 9) zeigt sie eine stark vereinfachte Übersicht (Flächen unter 2 km² zugeschlagen).</span></p>
      <p><b>Statistik je Kreis:</b> aus einem 50-m-Raster der BK50, getrennt nach den 44 Kreisdateien des LGRB (35 Landkreise, 9 Stadtkreise); der Grünlandanteil stammt aus CORINE.</p>
      <p><b>Standortauskunft:</b> Zu jeder Kartiereinheit verlinkt die Karte den amtlichen Steckbrief des LGRB (PDF) und die Beschreibung in LGRBwissen.</p>
    </div>'''
rex(r'<div class="in" style="font-size:12.5px;color:var\(--text-secondary\)">\s*<p><b>Belegstatus je Eigenschaft:</b>.*?</div>\s*</details>', METH+"\n  </details>")
SRC=('<p class="src">Boden: Datenquelle: Regierungspräsidium Freiburg - LGRB, <a href="https://www.lgrb-bw.de">www.lgrb-bw.de</a>, Bodenkarte 1 : 50 000, '
 '<a href="https://www.govdata.de/dl-de/by-2-0">Datenlizenz Deutschland - Namensnennung - Version 2.0</a>; verändert: in Soilscapes-Vergleichskategorien eingeteilt, Linien vereinfacht. '
 'Nutzung: CORINE Land Cover 5 ha 2021, Höhe: DGM200, Hintergrund topografisch: basemap.de, alle © GeoBasis-DE / <a href="http://www.bkg.bund.de">BKG</a> 2026 (Daten verändert). '
 'Luftbild (DOP20) und ATKIS Basis-DLM: © LGL, <a href="https://www.lgl-bw.de">www.lgl-bw.de</a>, dl-de/by-2-0. Schläge aus dem Agrarantrag (FIONA): Ministerium für Ländlichen Raum und Verbraucherschutz Baden-Württemberg, dl-de/by-2-0. '
 'Ortssuche: © OpenStreetMap-Mitwirkende (ODbL). Pilzsuche: Baumarten © Thünen-Institut (Blickensdörfer et al. 2024, Daten 2017/2018); Hangrichtung aus AWS Terrain Tiles (u. a. EU-DEM, SRTM); Wetter Open-Meteo (CC BY 4.0, Modelldaten u. a. DWD); Fundmeldungen iNaturalist (Lizenzen der Beobachter). pH-Karte © Thünen-Institut (Scherstjanoi, Grüneberg, Wellbrock 2021); SoilGrids © ISRIC (CC BY 4.0). '
 'Faustregeln nach dem Pilzsammler-Buch, Kapitel „Digital Hotspots finden“ und „Digital den perfekten Moment finden“. Kategorien: eigene Auswertung nach „Soilscapes-Klassen in deutsche Bodentypen (KA5) übertragen“.</p>')
rex(r'<p class="src">Boden: ÜBK25 ©.*?</p>', SRC)
rep('<div id="printHead"><h2>Bodenkarte Bayern: Soilscapes-Vergleich</h2>','<div id="printHead"><h2>Bodenkarte Baden-Württemberg: Soilscapes-Vergleich</h2>')
rep("<summary>Statistik je Landkreis</summary>","<summary>Statistik je Kreis</summary>")

# ---- Konstanten, Speicher ----
rep('const PAGES_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes/";','const PAGES_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-bw/";')
rep('const STORE_KEY = "bodenkarte_bayern_v3";','const STORE_KEY = "bodenkarte_bw_v1";')
rep('db.collection("data/users/"+uid).doc("bodenkarte")','db.collection("data/users/"+uid).doc("bodenkarte_bw")')
rex(r"map\.attributionControl\.setPrefix\(false\)\.addAttribution\('ÜBK25.*?'\);",
 "map.attributionControl.setPrefix(false).addAttribution('Boden: Datenquelle: Regierungspräsidium Freiburg - LGRB, www.lgrb-bw.de, dl-de/by-2-0 (verändert) · CLC5, DGM200 © GeoBasis-DE / <a href=\"http://www.bkg.bund.de\">BKG</a> 2026 (Daten verändert) · ATKIS © LGL, FIONA © MLR, dl-de/by-2-0');")
# Regeltexte stehen in D.reg nur einmal
rep("  return JSON.parse(await new Response(st).text());\n}",
    "  const d=JSON.parse(await new Response(st).text());\n  if(d.reg) for(const u of Object.values(d.units)) for(const p of Object.values(u.p)) if(typeof p.regel===\"number\") p.regel=d.reg[p.regel];\n  return d;\n}")

# ---- Hintergrund: Luftbild LGL ----
rex(r'const DOP_URL=.*?\nconst BASEMAPS=\{.*?\n\};',
'''const DOP_URL="https://owsproxy.lgl-bw.de/owsproxy/ows/WMS_LGL-BW_ATKIS_DOP_20_C?";
const BASEMAPS={
  topo:async()=>[
    ()=>L.tileLayer("https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",{maxZoom:18,attribution:'basemap.de © GeoBasis-DE / <a href="http://www.bkg.bund.de">BKG</a> 2026, CC BY 4.0'}),
    ()=>L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende'})],
  dop:async()=>[
    ()=>L.tileLayer.wms(DOP_URL,{layers:"IMAGES_DOP_20_RGB",format:"image/jpeg",version:"1.3.0",maxZoom:20,attribution:'Luftbild DOP20 © <a href="https://www.lgl-bw.de">LGL</a>, dl-de/by-2-0'}),
    ()=>L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Luftbild © Esri, Maxar, Earthstar Geographics"})],
  esri:async()=>[()=>L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Luftbild © Esri, Maxar, Earthstar Geographics"})],
};''')
rep('toast("Luftbild Bayern nicht erreichbar, zeige Esri-Luftbild")','toast("Luftbild des LGL nicht erreichbar, zeige Esri-Luftbild")',2)
rep("countrycodes=de&viewbox=8.9,50.6,13.9,47.2&bounded=1","countrycodes=de&viewbox=7.4,49.9,10.6,47.4&bounded=1")
rep("Koordinaten (z. B. 49.07, 13.10) funktionieren immer.","Koordinaten (z. B. 47.83, 7.94) funktionieren immer.")

# ---- Amtliche Nutzung online: ATKIS Basis-DLM (INSPIRE-Bodenbedeckung) und FIONA ----
rex(r'const ATKIS_URL=.*?\nfunction toZ0\(',
r'''const LC_URL="https://owsproxy.lgl-bw.de/owsproxy/wfs/WFS_INSP_BW_Bodenbedeckung_ATKIS_Basis-DLM";
const FIONA_URL="https://owsproxy.lgl-bw.de/owsproxy/wfs/WFS_LW-BW_FIONA_Flaecheninformation";
const VF=new Map(), VT={a:new Map(),i:new Map()}; let vecQ=[], vecRun=0, vecOk=0, vecFail=0, vecDead=false, LUVIS=[];
const LC_NAME={"1":"bebaute Fläche","1-1":"Gebäude und bauliche Nebenflächen","1-2":"Verkehrs- und Tiefbaufläche","2":"vegetationslose Fläche","2-1":"Fels","2-2":"vegetationsloser Boden, Kies, Sand",
  "3":"Vegetation (gemischt)","3-1":"krautige Vegetation","3-1--1":"Gras (Grünland)","3-1--2":"Röhricht, Schilf","3-1--3":"Ackerland (Getreide, Stauden)","3-2":"Gehölzvegetation","3-2--2":"Gehölz","3-2--3":"Büsche, Sträucher","3-2--4":"Zwergsträucher, Heide","4":"Wasser"};
function lcSub(cl,mo){ const all=[cl].concat(mo), tree=all.some(m=>m.startsWith("3-2--1"));
  if(cl.startsWith("4")) return ["sw","Wasser"];
  if(cl.startsWith("1")) return ["ss",LC_NAME[cl.slice(0,3)]||LC_NAME[cl[0]]];
  if(cl.startsWith("2")) return ["of",LC_NAME[cl.slice(0,3)]||LC_NAME["2"]];
  if(cl.startsWith("3-1--2")) return ["om",LC_NAME["3-1--2"]];
  if(cl.startsWith("3-1--3")) return ["ak",LC_NAME["3-1--3"]];
  if(cl.startsWith("3-1--1")) return /^3-1--1---1/.test(cl)?["om","Gras, ganzjährig nass"]:["gs",LC_NAME["3-1--1"]];
  if(cl.startsWith("3-2--1")||((cl==="0"||cl==="3"||cl==="3-2")&&tree&&cl!=="3")){ const lf=new Set(); for(const m of all){ const x=/^3-2--1---\d-(\d)/.exec(m); if(x&&x[1]!=="0") lf.add(x[1]); }
    return lf.size===1?(lf.has("1")?["wl","Laubwald"]:["wn","Nadelwald"]):["wm",lf.size?"Mischwald":"Wald"]; }
  if(cl==="3"&&tree) return ["wg","Vegetation mit Bäumen (Streuobst, Garten, Gehölz)"];
  if(cl.startsWith("3-2--4")) return ["oh",LC_NAME["3-2--4"]];
  if(cl.startsWith("3-2")) return ["wg",LC_NAME[cl.slice(0,6)]||LC_NAME["3-2"]];
  if(cl.startsWith("3-1")||cl==="3") return ["gs",LC_NAME[cl]||"krautige Vegetation"];
  return ["ss","nicht eindeutig bestimmbar"]; }
function fionaSub(g,b){
  if(g==="Dauergrünland"){ if(/mähweide/i.test(b)) return "gm"; if(/weide/i.test(b)) return "gp"; if(/wiese/i.test(b)) return "gw"; return "gs"; }
  if(g==="Aus der Produktion genommen") return /grünland/i.test(b)?"gs":/dauerkultur/i.test(b)?"sk":"ak";
  if(g==="Dauerkulturen"||g==="Zierpflanzen") return /spargel|rhabarber/i.test(b)?"ak":"sk";
  if(g==="Ackerfutter"){ if(/^weiden/i.test(b)) return "gp"; if(/^wiesen/i.test(b)) return "gw"; return "ak"; }
  if(g==="D"||g==="Sonstige Flächen"){ if(/hecke|waldrand|biotope ohne/i.test(b)) return null; if(/grünland|ÖVF GL/i.test(b)) return "gs"; return "ak"; }
  return "ak"; }
function xmlTxt(s){ return s.replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&quot;/g,'"').replace(/&apos;/g,"'").trim(); }
function toZ0(''')
rex(r'function parseAtkis\(tx\)\{.*?\nfunction vecWanted\(\)',
r'''function parseAtkis(tx){ const out=[];
  for(const ch of tx.split("<wfs:member>")){ const m=/<lcv:LandCoverUnit[^>]*gml:id="([^"]+)"/.exec(ch); if(!m) continue;
    const ob=ch.slice(ch.indexOf("<lcv:landCoverObservation>")), cls=[...ob.matchAll(/LandCoverClassValue\/([^"]+)"/g)].map(x=>x[1]); if(!cls.length) continue;
    const polys=parsePolys(ch.slice(0,ch.indexOf("<lcv:landCoverObservation>"))); if(!polys.length) continue;
    const [sub,name]=lcSub(cls[0],cls.slice(1));
    out.push({id:"a:"+m[1],src:"a",sub,polys,bb:featBB(polys),name}); }
  return out; }
function parseGsa(tx){ const out=[];
  for(const ch of tx.split("<wfs:member>")){ const m=/<lw:v_fiona_flaecheninformation gml:id="([^"]+)"/.exec(ch); if(!m) continue;
    const g=/<lw:Kulturartengruppe>([^<]*)/.exec(ch), b=/<lw:Bezeichnung>([^<]*)/.exec(ch), y=/<lw:Antragsjahr>(\d+)/.exec(ch);
    const crop=b?xmlTxt(b[1]):"", sub=fionaSub(g?xmlTxt(g[1]):"",crop); if(!sub) continue; const polys=parsePolys(ch); if(!polys.length) continue;
    out.push({id:"i:"+m[1],src:"i",sub,polys,bb:featBB(polys),crop,code:null,ha:null,since:y?+y[1]:null}); }
  return out; }
async function wfsGet(src,x0,y0,x1,y1,ms){
  const ctl=new AbortController(), to=setTimeout(()=>ctl.abort(),ms||45000), bb=`${x0},${y0},${x1},${y1},urn:ogc:def:crs:EPSG::25832`;
  try{ const u=src==="a"?`${LC_URL}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=lcv:LandCoverUnit&COUNT=30000&BBOX=${bb}`
                     :`${FIONA_URL}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=lw:v_fiona_flaecheninformation&COUNT=30000&BBOX=${bb}`;
    const r=await fetch(u,{signal:ctl.signal}); if(!r.ok) throw new Error("HTTP "+r.status);
    const tx=await r.text(); if(/ExceptionReport|Request Rejected/.test(tx.slice(0,800))) throw new Error("Dienstfehler");
    return src==="a"?parseAtkis(tx):parseGsa(tx);
  } catch(e){ if(e.name==="AbortError") throw new Error("Zeitüberschreitung"); throw e; } finally{ clearTimeout(to); } }
function vecWanted()''')
rex(r'function vecText\(a,i\)\{.*?\n  if\(a\) return `\$\{a\.name\} · ATKIS`; return null; \}',
r'''function vecText(a,i){
  if(i){ const nm=SUB[i.sub].n, extra=i.crop&&!new RegExp("^"+nm.split(" ")[0],"i").test(i.crop)?` (${i.crop})`:""; return `${nm}${extra} · Agrarantrag ${i.since||""}`.trim(); }
  if(a) return `${a.name} · ATKIS`; return null; }''')
rep('    else { t="Jetzt: amtliche Flächen, ATKIS Basis-DLM (Bayerische Vermessungsverwaltung)";','    else { t="Jetzt: amtliche Bodenbedeckung, ATKIS Basis-DLM (LGL)";')
rep('`, darüber die Feldstücke aus dem Agrarantrag (StMELF)${','`, darüber die Schläge aus dem Agrarantrag 2022 (FIONA)${')
rep("Ab Zoomstufe ${VEC_Z} erscheinen die amtlichen Flächen der Tatsächlichen Nutzung, ab ${INV_Z} zusätzlich die Feldstücke aus dem Agrarantrag mit Wiese, Mähweide, Weide und Ackerfrucht.",
    "Ab Zoomstufe ${VEC_Z} erscheint die amtliche Bodenbedeckung (ATKIS), ab ${INV_Z} zusätzlich die Schläge aus dem Agrarantrag mit Wiese, Mähweide, Weide, Rebfläche und Ackerfrucht.")

# ---- Punktabfrage ----
rex(r'<a href="https://atlas\.bayern\.de/\?z=15&c=\$\{e\},\$\{n\}" target="_blank" rel="noopener">BayernAtlas</a><a href="https://www\.umweltatlas\.bayern\.de[^"]*" target="_blank" rel="noopener">UmweltAtlas Boden</a>',
 '<a href="https://maps.lgrb-bw.de/" target="_blank" rel="noopener">LGRB-Kartenviewer</a>${U&&U.pdf?`<a href="${esc(U.pdf)}" target="_blank" rel="noopener">Steckbrief ${esc(K.leg)} (PDF)</a>`:""}${U&&U.node?`<a href="${esc(U.node)}" target="_blank" rel="noopener">LGRBwissen</a>`:""}')
rep('<p class="ph">Außerhalb der ÜBK25-Flächen.</p>','<p class="ph">Außerhalb der BK50-Flächen (nur Baden-Württemberg).</p>')
rep("<h3>ÜBK25-Einheit ${esc(K.leg)}</h3>","<h3>BK50-Einheit ${esc(K.leg)}</h3>")
rep("<b>Amtliche Beschreibung:</b>","<b>Amtliche Kurzlegende (BK50):</b>")
rep('html+=propRow("Moorbodenprüfung", P.moor,','html+=propRow("Moor- und Anmoorboden", P.moor,')
rep('propRow("Ausgangsgestein (BAG500)", P.gestein,','propRow("Ausgangsmaterial (BK50)", P.gestein,')
rep('propRow("Bodenkennwerte (LfU)",','propRow("Bodenkennwerte (BK50)",')
rep('<span class="badge b-amtlich">amtlich (LfU)</span>','<span class="badge b-amtlich">amtlich (LGRB)</span>')
rep("(aus 400-m-Höhenraster, nur grob)","(aus 400-m-Höhenraster, nur grob)")

# ---- Statistik ----
rep('<div>Bayern gesamt</div>','<div>Baden-Württemberg gesamt</div>')
rep('${gr?" auf Grünland (CORINE)":""} je Landkreis bzw. kreisfreier Stadt,','${gr?" auf Grünland (CORINE)":""} je Land- bzw. Stadtkreis,')

# ---- Beschriftung ----
rex(r'  const cities=\[\["München".*?\]\];\n  const lands=\[.*?\]\];',
'''  const cities=[["Stuttgart",48.776,9.183],["Mannheim",49.488,8.466],["Karlsruhe",49.007,8.404],["Freiburg",47.999,7.842],["Heidelberg",49.399,8.672],["Ulm",48.398,9.991],["Heilbronn",49.142,9.219],["Pforzheim",48.891,8.704],["Reutlingen",48.491,9.204],["Konstanz",47.660,9.175],["Tübingen",48.520,9.053],["Ravensburg",47.782,9.611],["Offenburg",48.473,7.944],["Villingen-Schwenningen",48.062,8.494],["Aalen",48.837,10.093],["Schwäbisch Hall",49.112,9.737],["Baden-Baden",48.761,8.240],["Sigmaringen",48.087,9.216],["Tuttlingen",47.985,8.818],["Lörrach",47.615,7.661],["Waldshut",47.623,8.215],["Freudenstadt",48.463,8.411],["Bad Mergentheim",49.492,9.773],["Mosbach",49.353,9.145],["Biberach",48.098,9.788],["Göppingen",48.703,9.652]];
  const lands=[["Schwarzwald",48.25,8.15],["Schwäbische Alb",48.38,9.35],["Odenwald",49.55,8.98],["Oberschwaben",48.00,9.65],["Kraichgau",49.17,8.85],["Hohenlohe",49.27,9.62],["Bodensee",47.60,9.40],["Oberrheinebene",48.62,7.98],["Baar",47.96,8.58],["Schwäbisch-Fränkischer Wald",49.02,9.58],["Hegau",47.80,8.82],["Kaiserstuhl",48.10,7.67],["Allgäu",47.72,9.98],["Hochrhein",47.58,8.05]];''')

# ---- Pilzsuche: pH-Grundlage aus der BK50 ----
rep('regel:"Basensättigung unter 20 % (LfU-Kennwert, Waldwert bevorzugt) und Oberboden kalkfrei (Carbonat unter 0,5 %)"',
    'regel:"pH im Oberboden laut BK50 höchstens stark sauer (unter pH 5, Stufen 2 bis 4) und kein Kalk ab der Oberfläche oder in den obersten 4 dm"')
rep('regel:"Oberboden kalkhaltig (Carbonat ab 0,5 %) oder Basensättigung ab 80 % oder mindestens 50 % basisches Gestein (BAG500)"',
    'regel:"pH im Oberboden laut BK50 mindestens schwach sauer (ab pH 6, Stufen 6a bis 8) oder Kalk ab der Oberfläche oder in den obersten 4 dm"')
rep('regel:"nutzbare Feldkapazität ab 180 mm und Wasserdurchlässigkeit unter 40 cm/Tag (höchstens mittel)"',
    'regel:"nutzbare Feldkapazität bis 1 m ab 180 mm und Wasserdurchlässigkeit im Unterboden unter 40 cm/Tag (höchstens mittel), Kennwerte der BK50"')
rex(r'  lfuW:\{n:"LfU-Bodenkennwerte, Waldwert".*?\n  th30:',
 '  bkW:{n:"BK50 (LGRB), pH unter Wald",kind:"unit",info:"pH-Bereich im Oberboden unter Wald laut BK50 je Kartiereinheit (ohne Kalkung). Sauer: alle Hauptstufen unter pH 5 und kein Kalk im Oberboden; basisch: alle Hauptstufen ab pH 6 oder Kalk ab der Oberfläche. Wo die BK50 keinen Waldwert hat (meist reine Acker- und Grünlandeinheiten), gilt der Wert unter Acker und Grünland.'+(VAL_W and " "+VAL_W)+'"},\n'
 '  bkL:{n:"BK50 (LGRB), pH unter Acker und Grünland",kind:"unit",info:"Wie oben, aber der pH-Bereich unter landwirtschaftlicher Nutzung. Durch Kalkung meist höher als im Wald, daher weniger saure und mehr basische Flächen.'+(VAL_L and " "+VAL_L)+'"},\n  th30:')
rex(r'function pzMatch\(K,p,src\)\{.*?\n  return false; \}\n',
 'function pzMatch(K,p,src){ const u=D.units[K.leg]; if(!u||!u.zc) return false; src=src||S.phSrc;\n'
 '  if(p==="wasser") return !!u.zc[4]; if(PH_SRC[src].kind==="raster") return false; return !!u.zc[(src==="bkL"?2:0)+(p==="sauer"?0:p==="basisch"?1:9)]; }\n')
rex(r'    const rows=\[\n      \["lfuW".*?\n      \["bag".*?\n',
 '    const sa=leg&&D.units[leg]?D.units[leg].p.saeure.belege:[], phw=(sa.find(b=>/^unter Wald/.test(b.art))||{}).art, phl=(sa.find(b=>/^unter Acker/.test(b.art))||{}).art;\n'
 '    const rows=[\n      ["bkW", phw?phw.replace(/^unter Wald: /,""):(phl?"kein Waldwert, "+phl:"keine Angabe"), leg&&D.units[leg]?unitCls("bkW"):null],\n'
 '      ["bkL", phl?phl.replace(/^unter Acker und Grünland: /,""):"keine Angabe", leg&&D.units[leg]?unitCls("bkL"):null],\n')
rep("LfU-Werte und Gestein gelten als Mittel der ganzen Bodeneinheit, die Rasterkarten für diesen Punkt.","Die BK50-Werte gelten für die ganze Kartiereinheit, die Rasterkarten für diesen Punkt.")
rep("const L_=[]; const z=D.units[leg]&&D.units[leg].z; const nfk=z?z[4]:null;","const L_=[]; const nfk=D.units[leg]&&D.units[leg].nf!=null?D.units[leg].nf:null;")
t=t.replace('"lfuW"','"bkW"')

# ---- Bildexport ----
rep('x.fillText("Bodenkarte Bayern: Soilscapes-Vergleich",X,y)','x.fillText("Bodenkarte Baden-Württemberg: Soilscapes-Vergleich",X,y)')
rex(r'wrap\("Boden: ÜBK25, ÜMBK25.*?"\+\(tainted',
 'wrap("Boden: Datenquelle: Regierungspräsidium Freiburg - LGRB, www.lgrb-bw.de, BK50, dl-de/by-2-0 (verändert). Nutzung CORINE 5 ha und DGM200 © GeoBasis-DE / BKG 2026; ATKIS Basis-DLM © LGL; FIONA © MLR (dl-de/by-2-0)."+(tainted')
rep('const name="bodenkarte_bayern_"+new Date()','const name="bodenkarte_bw_"+new Date()')
rep('offerFile("bodenkarte_sicherung.json"','offerFile("bodenkarte_bw_sicherung.json"')

open("/home/claude/bw/template_bw.html","w",encoding="utf-8").write(t)
left=re.findall(r".{0,40}(?:ÜBK25|ÜMBK|LfU|Bayern|bayern\.de|BAG500|StMELF|InVeKoS|Landkreis|lfuW|lfuA|\"bag\").{0,40}",t)
print("fertig",len(t),"Reste:",len(left))
for l in left: print("  ",l)
