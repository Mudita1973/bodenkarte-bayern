"""Erzeugt template_cz.html aus der bayerischen Vorlage template10.html (Westböhmen-Fassung)."""
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

SRC_ATTR=('Boden: Půdní mapa 1 : 50 000 und Půdní mapa 1 : 1 000 000. In: Mapové služby ČGS [online]. Praha: Česká geologická služba [cit. 2026-11-02]. '
 'Dostupné z: <a href="https://mapy.geology.cz/arcgis/rest/services/Pudy">mapy.geology.cz</a>; Gestein: Geologická mapa 1 : 50 000 (GEOČR50), ebenda. '
 'Verändert: in Soilscapes-Vergleichsklassen eingeteilt, Bodenbezeichnungen übersetzt, Linien vereinfacht.')

# ---- Kopf und Texte ----
rep("<title>Bodenkarte Bayern: Soilscapes-Klassen aus der ÜBK25</title>","<title>Bodenkarte Westböhmen: Soilscapes-Klassen aus der ČGS-Bodenkarte</title>")
rep("<h1>Bodenkarte Bayern</h1>","<h1>Bodenkarte Westböhmen</h1>")
rep("<p class=\"sub\">ÜBK25 (LfU Bayern), verglichen mit","<p class=\"sub\">Karlovarský, Plzeňský und Jihočeský kraj. Bodenkarte 1 : 50 000 der Tschechischen Geologischen Anstalt (ČGS), verglichen mit")
rep('placeholder="Ort suchen, z. B. Bodenmais oder 49.07, 13.10"','placeholder="Ort suchen, z. B. Klatovy oder 49.40, 13.30"')
rep('placeholder="Kategorie oder ÜBK25-Einheit: Nummer oder Text"','placeholder="Kategorie oder Bodeneinheit: Nummer oder Text"')
rep('<option value="topo">Topografisch (basemap.de)</option>','<option value="topo">Topografisch (ČÚZK, ZTM)</option>')
rep('<option value="dop">Luftbild Bayern (DOP40)</option>','<option value="dop">Luftbild Tschechien (ČÚZK Ortofoto)</option>')
rep("Das Luftbild Bayern sucht sich die passende Bildebene selbst; ist der Dienst nicht erreichbar, erscheint automatisch das Esri-Luftbild, bei der topografischen Karte ersatzweise OpenStreetMap.",
    "Ist der ČÚZK-Dienst nicht erreichbar, erscheint automatisch das Esri-Luftbild, bei der topografischen Karte ersatzweise OpenStreetMap.")
rex(r'<p class="note">Quellen: In der Übersicht CORINE Land Cover 5 ha.*?</p>',
 '<p class="note">Quellen: In der Übersicht die Flächen der ZABAGED (ČÚZK), als Raster von etwa 80 m offline enthalten. Ab Zoomstufe 13 die ZABAGED-Flächen selbst (auf etwa 15 m vereinfacht, von dieser Seite geladen); die 714.538 Gebäude des Gebiets sind dabei zu bebauten Flächen verschmolzen (Lücken bis etwa 12 m geschlossen). Ab Zoomstufe 14 zusätzlich die Feldblöcke aus dem tschechischen Agrarregister LPIS (Landwirtschaftsministerium) mit Kultur und Fläche, live abgefragt. Wiese und Weide trennen beide Quellen nicht.</p>')
rep("<summary>Statistik je Landkreis</summary>","<summary>Statistik je Bezirk (okres)</summary>")
rep('<option value="p">nach Anteil am Kreis sortieren</option>','<option value="p">nach Anteil am Bezirk sortieren</option>')
rep("Klick in die Karte: Bodeneigenschaften mit Belegstatus, Moorbodenprüfung, Vergleichskategorien, Höhe, Nutzung und Links.","Klick in die Karte: Bodeneigenschaften mit Belegstatus, Vergleichskategorien, Höhe, Nutzung und Links.")

METH='''<div class="in" style="font-size:12.5px;color:var(--text-secondary)">
      <p><b>Grundlage:</b> Půdní mapa 1 : 50 000 der ČGS (neue digitale Edition, Bodenklassifikation TKSP nach Němeček und andere 2011). Sie deckt 14.256 km² der 21.007 km² großen Region ab. Die Lücken (6.735 km², vor allem Šumava zwischen Železná Ruda und Vimperk, um Domažlice, Nepomuk und Blatná, Český Krumlov und Hluboká) sind mit der ČGS-Übersichtskarte 1 : 1 000 000 gefüllt, die dasselbe Klassifikationssystem nutzt. Diese Flächen sind grob und immer als unsicher markiert. SoilGrids wurde dafür nicht genutzt, weil es nur geschätzte Eigenschaften, aber keine Bodentypen liefert.</p>
      <p><b>Belegstatus je Eigenschaft:</b> <span class="badge b-genannt">in Bodenkarte genannt</span> steht in der ČGS-Bodenkarte (Bodentyp, Subtyp, Substrat; tschechischer Text wird gezeigt, die deutsche Bezeichnung ist eine Näherung). <span class="badge b-abgeleitet">abgeleitet</span> wurde erschlossen, etwa „sauer“ aus Granit; die Regel steht dabei. <span class="badge b-fehlt">keine Angabe</span>: die Karte sagt dazu nichts. Gemessene Kennwerte wie die Basensättigung des LfU in Bayern gibt es hier nicht; die Basenangaben stammen aus den TKSP-Subtypen (dystrisch, mesobasisch, eutroph).</p>
      <p><b>Zuordnung:</b> jede Bodeneinheit genau eine Kategorie, nach demselben Regelwerk wie in Bayern, übertragen auf die TKSP-Bodentypen. Wo die Bodenkarte kein Substrat nennt, kommt die Gesteinsgruppe aus der geologischen Karte 1 : 50 000 (GEOČR50) am Mittelpunkt der Fläche. Solche Zuordnungen und alle Lückenfüllungen gelten als unsicher; das betrifft 72,8 % der Fläche.</p>
      <p><b>Prüfung:</b> Ein unabhängiger Prüfdurchgang hat 278 Einheiten mit 90 % der Fläche gegen das Dokument geprüft: 94,8 % der geprüften Fläche zutreffend, 0,9 % fraglich, 4,3 % falsch. Alle 28 beanstandeten Fälle (979 km²) sind korrigiert, unter anderem: Sandlehm-Deckschichten zählen nicht mehr als Sand (Klasse 6 statt 0), Braunerden mit Lösslehmdecke (kambizem luvická) zu Klasse 6, eutrophe Braunerden und Böden aus den Alkalivulkaniten des Duppauer Gebirges zu Klasse 7, basenarme Braunerden über Festgestein zu Klasse 13. Insgesamt haben 283 Einheiten mit 1.120 km² die Klasse gewechselt.</p>
      <p><b>Teilmerkmale:</b> je Kategorie die Merkmale aus dem Dokument, geprüft an Bodentyp, Subtyp, Substrat, Gestein, mittlerer Höhe und Hangneigung (DMR 4G). Eine Fläche kann mehrere Kategorien teilweise oder ganz erfüllen; Überschneidungen sind gestreift.</p>
      <p><b>Höhe am Punkt:</b> DMR 4G der ČÚZK, für die Webkarte auf etwa 260 m vergröbert. <b>Nutzung am Punkt:</b> in der Übersicht ZABAGED als Raster von etwa 80 m, ab Zoomstufe 13 die ZABAGED-Fläche und, wo vorhanden, der LPIS-Feldblock. LPIS-Kulturen ohne eindeutige Nutzung (andere Kultur, nicht produktive Fläche, Containerflächen) bleiben bei der ZABAGED-Angabe.</p>
      <p><b>Generalisierung:</b> Linien in der Übersicht auf etwa 600 m, in der Normalansicht auf etwa 60 m vereinfacht. Flächenangaben stammen aus den ungeneralisierten Daten. <span id="detailNote">Ab Zoomstufe 12 lädt die Karte genauere Flächen nach (auf etwa 10 m vereinfacht).</span></p>
      <p><b>Statistik je Bezirk:</b> 17 Bezirke (okresy) nach RÚIAN (ČÚZK), ausgezählt auf einem 50-m-Raster aus Bodenkarte und ZABAGED. Der Grünlandanteil ist das ZABAGED-Dauergrünland an genau diesen Rasterzellen. Gewässer sind ausgelassen.</p>
      <p><b>Pilzsuche:</b> Die Bodengruppen kommen aus der ČGS-Bodenkarte: sauer (basenarm oder podsoliert, ohne Kalk) 5.564 km², basen- oder kalkreich 976 km² (basisches Gestein aus der geologischen Karte zählt nur, wenn die Bodenkarte nicht basenarm oder mittel basenhaltig angibt), gute Wasserspeicher (tiefgründiger Lehm aus Löss oder Lösslehm) 1.775 km². In Bayern beruhen dieselben Gruppen auf gemessenen LfU-Kennwerten; hier sind sie eine Näherung. Hangrichtung, Wetter und Fundmeldungen funktionieren wie in Bayern, Baumarten fehlen.</p>
      <p><b>Agrarregister LPIS:</b> Der Dienst enthält auch Namen und Anschriften der Bewirtschafter. Die Karte fragt nur Geometrie, Kultur und Fläche ab; die persönlichen Angaben werden nicht übertragen und nirgends angezeigt.</p>
      <p><b>Standortauskunft:</b> Mapy.com wird direkt an der Koordinate geöffnet. Die ČGS-Bodenkarte bietet keinen dokumentierten Direktlink zu einer Koordinate; dort über die Ortssuche hinzoomen.</p>
    </div>'''
rex(r'<div class="in" style="font-size:12.5px;color:var\(--text-secondary\)">\s*<p><b>Belegstatus je Eigenschaft:</b>.*?</div>\s*</details>', METH+"\n  </details>")
rex(r'<p class="src">Boden: ÜBK25.*?</p>',
 '<p class="src">'+SRC_ATTR+' Nutzung (ZABAGED), Höhe (DMR 4G), Bezirksgrenzen (RÚIAN), Hintergrund ZTM und Ortofoto: © ČÚZK, CC BY 4.0 (Nutzung zu 9 Gruppen zusammengefasst, Gebäude zu bebauten Flächen verschmolzen, Linien vereinfacht, Höhe vergröbert). Feldblöcke: LPIS © Ministerstvo zemědělství ČR. Ortssuche und Ersatzkarte: © OpenStreetMap-Mitwirkende (ODbL). Luftbild Esri: © Esri, Maxar, Earthstar Geographics. Kategorien: eigene Auswertung nach „Soilscapes-Klassen in deutsche Bodentypen (KA5) übertragen“.</p>')
rep('<div id="printHead"><h2>Bodenkarte Bayern: Soilscapes-Vergleich</h2>','<div id="printHead"><h2>Bodenkarte Westböhmen: Soilscapes-Vergleich</h2>')

rep('<a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/" target="_blank" rel="noopener">Nachbarkarte: Bodenkarte Westböhmen (Tschechien) →</a>',
    '<a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes/" target="_blank" rel="noopener">Nachbarkarte: Bodenkarte Bayern →</a>')
rep('const OTHER_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/", OTHER_BB=[48.55,12.09,50.46,15.60], OTHER_C="49.50%2C13.85&z=8", OTHER_LU={gw:"gs",gm:"gs",gp:"gs",gs:"gs",wl:"wm",wn:"wm",wm:"wm",oh:""};',
    'const OTHER_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes/", OTHER_BB=[47.27,8.97,50.57,13.84], OTHER_C="48.95%2C11.40&z=7", OTHER_LU={gs:"gw.gm.gp.gs",wm:"wl.wn.wm"};')
# ---- Konstanten ----
rep('const PAGES_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes/";','const PAGES_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/";')
rep('const STORE_KEY = "bodenkarte_bayern_v3";','const STORE_KEY = "bodenkarte_westboehmen_v1";')
rep('db.collection("data/users/"+uid).doc("bodenkarte")','db.collection("data/users/"+uid).doc("bodenkarte_cz")')
rex(r"const LUG=\[.*?\];\nconst SUB=\{\};",
'''const LUG=[
  {g:"a",n:"Acker",subs:[["ak","Ackerland","#e2c766"],["sk","Sonderkulturen (Obst, Garten, Hopfen, Wein)","#b783a8"]]},
  {g:"g",n:"Grünland",subs:[["gs","Dauergrünland (Wiese und Weide)","#6dbb5e"]]},
  {g:"w",n:"Wald und Gehölz",subs:[["wm","Wald","#2e6c46"],["wg","Gehölz, Krummholz, Aufforstung","#8aae78"]]},
  {g:"s",n:"Siedlung und Wasser",subs:[["ss","Siedlung, Verkehr, Abbau","#9a9a9a"],["sw","Wasser","#5fb0e3"]]},
  {g:"o",n:"Sonstiges",subs:[["om","Moor, Sumpf","#5c98a8"],["of","Fels, Schutt","#cfcfcf"]]}];
const SUB={};''')
rex(r"const LU = \[.*?\];\nLU\.forEach",
'''const LU = [
  {c:1,n:"Acker",s:["ak"]},{c:2,n:"Sonderkulturen",s:["sk"]},{c:3,n:"Dauergrünland",s:["gs"]},
  {c:6,n:"Wald",s:["wm"]},{c:7,n:"Gehölz, Krummholz",s:["wg"]},{c:8,n:"Moor, Sumpf",s:["om"]},{c:9,n:"Siedlung, Verkehr",s:["ss"]},
  {c:10,n:"Wasser",s:["sw"]},{c:11,n:"Fels, Schutt",s:["of"]}];
LU.forEach''')
rex(r"map\.attributionControl\.setPrefix\(false\)\.addAttribution\('ÜBK25.*?'\);",
 "map.attributionControl.setPrefix(false).addAttribution('Boden © ČGS (verändert) · ZABAGED, DMR 4G © ČÚZK, CC BY 4.0 · LPIS © MZe');")

# ---- Hintergrund ----
rex(r'const DOP_URL=.*?\nconst BASEMAPS=\{.*?\n\};',
'''const CZ_TILE=n=>`https://ags.cuzk.gov.cz/arcgis1/rest/services/${n}/MapServer/tile/{z}/{y}/{x}`;
const BASEMAPS={
  topo:async()=>[
    ()=>L.tileLayer(CZ_TILE("ZTM_WM"),{maxZoom:19,maxNativeZoom:18,attribution:'ZTM © <a href="https://geoportal.cuzk.gov.cz">ČÚZK</a>, CC BY 4.0'}),
    ()=>L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende'})],
  dop:async()=>[
    ()=>L.tileLayer(CZ_TILE("ORTOFOTO_WM"),{maxZoom:20,maxNativeZoom:19,attribution:'Ortofoto © <a href="https://geoportal.cuzk.gov.cz">ČÚZK</a>, CC BY 4.0'}),
    ()=>L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Luftbild © Esri, Maxar, Earthstar Geographics"})],
  esri:async()=>[()=>L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Luftbild © Esri, Maxar, Earthstar Geographics"})],
};''')
rep('toast("Luftbild Bayern nicht erreichbar, zeige Esri-Luftbild")','toast("ČÚZK-Luftbild nicht erreichbar, zeige Esri-Luftbild")',2)
rep('toast("basemap.de nicht erreichbar, zeige OpenStreetMap")','toast("ČÚZK-Karte nicht erreichbar, zeige OpenStreetMap")',2)
rep("countrycodes=de&viewbox=8.9,50.6,13.9,47.2&bounded=1","countrycodes=cz&viewbox=12.0,50.5,15.7,48.5&bounded=1")
rep("(a>100000 ? utmToLatLng(a,b) : [b,a])","(a>100000 ? utmToLatLng(a,b,15) : [b,a])")
rep("Koordinaten (z. B. 49.07, 13.10) funktionieren immer.","Koordinaten (z. B. 49.40, 13.30) funktionieren immer.")

# ---- Nutzung ----
rep('${G.g==="g"?`<div class="nt" style="margin:2px 0 4px 26px">Wiese, Mähweide und Weide sind erst ab Zoomstufe ${INV_Z} getrennt (Agrarantrag). Darunter zählt alles als „ohne nähere Angabe“.</div>`:""}',
    '${G.g==="g"?`<div class="nt" style="margin:2px 0 4px 26px">ZABAGED und LPIS trennen Wiese und Weide nicht. LPIS-Ackergras zählt zum Acker.</div>`:""}')
mod=open("/home/claude/cz/mod_lu_cz.js",encoding="utf-8").read()
a=t.index("// ---------------- Amtliche Nutzung (online): ATKIS Basis-DLM und InVeKoS-Schläge ----------------")
b=t.index("// Anteile der Nutzungen im Ausschnitt (Stichprobenraster)")
t=t[:a]+mod+t[b:]
rep('basis=map.getZoom()>=INV_Z?"amtlich (ATKIS, Agrarantrag)":"amtlich (ATKIS)";','basis=map.getZoom()>=INV_Z?"ZABAGED und LPIS":"ZABAGED";')
rep('basis="CORINE 2021, grob"; }','basis="ZABAGED-Übersicht, etwa 80 m"; }')
rex(r'  else if\(inArtifact\(\)\) t="In der Claude-Artifact-Ansicht.*?\n  el\.textContent=t; \}',
'''  else if(inArtifact()) t="In der Claude-Artifact-Ansicht sind die genauen Nutzungsflächen gesperrt. Angezeigt wird die ZABAGED-Übersicht (Raster von etwa 80 m). Die Online-Fassung und die Ordner-Datei laden die genauen Flächen.";
  else if(vecDead) t="Die genauen Nutzungsflächen ließen sich nicht laden (etwa bei der Datei ohne Detailfassung oder ohne Internet). Angezeigt wird die ZABAGED-Übersicht (Raster von etwa 80 m).";
  else if(z<VEC_Z) t=`Jetzt: ZABAGED-Übersicht als Raster von etwa 80 m. Ab Zoomstufe ${VEC_Z} erscheinen die ZABAGED-Flächen, ab ${INV_Z} zusätzlich die Feldblöcke aus dem Agrarregister LPIS.`;
  else { const st=vecState();
    if(!st.n) t="Außerhalb des Kartengebiets gibt es keine Nutzungsflächen.";
    else if(st.n>40) t="Ausschnitt zu groß für die genauen Flächen; etwas näher heranzoomen.";
    else if(!st.complete) t=`Lade Nutzungsflächen … ${st.ao} von ${st.a} Kacheln. Bis dahin die Übersicht.`;
    else { t="Jetzt: ZABAGED-Flächen (ČÚZK), Gebäude zu bebauten Flächen zusammengefasst. Straßen sind nicht als Fläche enthalten und bleiben bei „Boden nur auf gewählter Nutzung“ abgedeckt";
      t+= z>=INV_Z ? `, darüber die LPIS-Feldblöcke (MZe)${st.io<st.i?` (lädt noch ${st.i-st.io} von ${st.i})`:""}${st.ie?`; ${st.ie} LPIS-Abfrage(n) fehlgeschlagen`:""}.` : `. Für die LPIS-Feldblöcke auf Zoomstufe ${INV_Z} gehen.`;
      if(st.ae) t+=` ${st.ae} Kachel(n) nicht geladen, dort fehlen Flächen.`; } }
  el.textContent=t; }''')

# ---- UTM: intern Zone 32 (Kachelraster), angezeigt Zone 33 ----
rep("function latLngToUtm(lat,lon){ const a=6378137,f=1/298.257222101,k0=0.9996,e2=f*(2-f),ep2=e2/(1-e2),lon0=9*Math.PI/180;",
    "function latLngToUtm(lat,lon,cm){ const a=6378137,f=1/298.257222101,k0=0.9996,e2=f*(2-f),ep2=e2/(1-e2),lon0=(cm||9)*Math.PI/180;")
rep("function utmToLatLng(E,Nn){ const a=6378137,f=1/298.257222101,k0=0.9996,e2=f*(2-f),ep2=e2/(1-e2),e1=(1-Math.sqrt(1-e2))/(1+Math.sqrt(1-e2)),lon0=9*Math.PI/180;",
    "function utmToLatLng(E,Nn,cm){ const a=6378137,f=1/298.257222101,k0=0.9996,e2=f*(2-f),ep2=e2/(1-e2),e1=(1-Math.sqrt(1-e2))/(1+Math.sqrt(1-e2)),lon0=(cm||9)*Math.PI/180;")

# ---- Punktabfrage ----
rep("const lat=ll.lat.toFixed(5), lng=ll.lng.toFixed(5), e=Math.round(E), n=Math.round(N);",
    "const lat=ll.lat.toFixed(5), lng=ll.lng.toFixed(5), [E33,N33]=latLngToUtm(ll.lat,ll.lng,15), e=Math.round(E33), n=Math.round(N33); curPoint.E33=E33; curPoint.N33=N33;")
rep('· UTM32 ${e} / ${n}${h!==null?','· UTM33 ${e} / ${n}${h!==null?')
rep('(CORINE, grob)`:""}</span></div>`;','(ZABAGED-Übersicht)`:""}</span></div>`;')
rex(r'<a href="https://atlas\.bayern\.de/\?z=15&c=\$\{e\},\$\{n\}" target="_blank" rel="noopener">BayernAtlas</a><a href="https://www\.umweltatlas\.bayern\.de[^"]*" target="_blank" rel="noopener">UmweltAtlas Boden</a>',
 '<a href="https://mapy.com/de/zakladni?x=${lng}&y=${lat}&z=15&source=coor&id=${lng}%2C${lat}" target="_blank" rel="noopener">Mapy.com</a><a href="https://mapy.geology.cz/pudy/" target="_blank" rel="noopener">ČGS-Bodenkarte</a>')
rep('<p class="ph">Außerhalb der ÜBK25-Flächen.</p>','<p class="ph">Außerhalb der Bodenkarte (nur Karlovarský, Plzeňský und Jihočeský kraj).</p>')
rep("<h3>ÜBK25-Einheit ${esc(K.leg)}</h3>","<h3>Bodeneinheit ${esc(K.leg)}</h3>")
rep("<b>Amtliche Beschreibung:</b>","<b>Beschreibung (ČGS-Bodenkarte, übersetzt):</b>")
rep('html+=propRow("Moorbodenprüfung", P.moor,','html+=propRow("Moorboden", P.moor,')
rep('propRow("Ausgangsgestein (BAG500)", P.gestein,','propRow("Ausgangsgestein", P.gestein,')
rep("(UTM32: ${Math.round(curPoint.E)} ${Math.round(curPoint.N)})","(UTM33: ${Math.round(curPoint.E33)} ${Math.round(curPoint.N33)})")
rep('nutzung:p.luName||(p.lu?LUN[p.lu].n+" (CORINE)":null)','nutzung:p.luName||(p.lu?LUN[p.lu].n+" (ZABAGED-Übersicht)":null)')
rep("const c=map.getCenter(), [E,N]=latLngToUtm(c.lat,c.lng);\n  $(\"phInfo\")","const c=map.getCenter(), [E,N]=latLngToUtm(c.lat,c.lng,15);\n  $(\"phInfo\")")
rep("(UTM32 ${Math.round(E)} / ${Math.round(N)}) · Vergleichsart","(UTM33 ${Math.round(E)} / ${Math.round(N)}) · Vergleichsart")
rep('genannt:\'<span class="badge b-genannt">in Legende genannt</span>\'','genannt:\'<span class="badge b-genannt">in Bodenkarte genannt</span>\'')

# ---- Statistik ----
rep('<div>Bayern gesamt</div>','<div>Gebiet gesamt</div>')
rep('${gr?" auf Grünland (CORINE)":""} je Landkreis bzw. kreisfreier Stadt,','${gr?" auf Dauergrünland (ZABAGED)":""} je Bezirk (okres),')
rep('[["landkreis","ags","flaeche_kreis_km2"','[["okres","kod","flaeche_bezirk_km2"')

rep('title="auf den Kreis zoomen"','title="auf den Bezirk zoomen"')
rep("% der Kreisfläche (${fmt(r.t)} km²)","% der Bezirksfläche im Kartengebiet (${fmt(r.t)} km²)")
# ---- Beschriftung ----
rex(r'  const cities=\[\["München".*?\]\];\n  const lands=\[.*?\]\];',
'''  const cities=[["Plzeň",49.747,13.378],["Karlovy Vary",50.231,12.872],["České Budějovice",48.975,14.474],["Cheb",50.080,12.374],["Sokolov",50.181,12.640],["Klatovy",49.396,13.295],["Domažlice",49.440,12.930],["Tábor",49.414,14.658],["Písek",49.309,14.148],["Strakonice",49.261,13.902],["Český Krumlov",48.811,14.315],["Prachatice",49.013,13.997],["Jindřichův Hradec",49.144,15.003],["Rokycany",49.743,13.594],["Tachov",49.798,12.634],["Mariánské Lázně",49.965,12.701],["Sušice",49.231,13.520],["Ostrov",50.306,12.939]];
  const lands=[["Šumava",49.02,13.62],["Český les",49.62,12.58],["Krušné hory",50.42,12.80],["Doupovské hory",50.25,13.12],["Slavkovský les",50.06,12.78],["Novohradské hory",48.68,14.72],["Třeboňská pánev",49.05,14.80]];''')

rep("(aus 400-m-Höhenraster, nur grob)","(aus etwa 260-m-Höhenraster, nur grob)")
rep('<label><input type="checkbox" id="cUnsure" checked> unsichere Zuordnungen blasser</label>','<label><input type="checkbox" id="cUnsure" checked> unsichere Zuordnungen blasser (72,8 % der Fläche, darunter die kantigen Blöcke aus der Übersichtskarte 1 : 1 Mio.)</label>')
# Merkpunkte in UTM33
rep("utm:[Math.round(p.E),Math.round(p.N)]","utm:[Math.round(p.E33),Math.round(p.N33)]")
rep('"utm32_e","utm32_n"','"utm33_e","utm33_n"')
rep("utm32_e:m.utm?m.utm[0]:null","utm33_e:m.utm?m.utm[0]:null"); rep("utm32_n:m.utm?m.utm[1]:null","utm33_n:m.utm?m.utm[1]:null")
rep('offerFile("bodenkarte_sicherung.json"','offerFile("bodenkarte_westboehmen_sicherung.json"')
# Pilzfunktionen auch über Link oder Sicherung nicht einschalten
rep('pilzSet("asp",!!st.asp); pilzSet("tree",!!st.tree); if(st.inat){','pilzSet("asp",!!st.asp); if(st.inat){')
# ---- Pilzsuche für Westböhmen: Bodengruppen aus der ČGS-Bodenkarte, keine Thünen-Karten ----
rep('regel:"Basensättigung unter 20 % (LfU-Kennwert, Waldwert bevorzugt) und Oberboden kalkfrei (Carbonat unter 0,5 %)"',
    'regel:"laut ČGS-Bodenkarte basenarm (dystrisch, oligotroph) oder podsoliert (Podsol, Kryptopodsol, podsolige Braunerde), ohne Kalk"')
rep('regel:"Oberboden kalkhaltig (Carbonat ab 0,5 %) oder Basensättigung ab 80 % oder mindestens 50 % basisches Gestein (BAG500)"',
    'regel:"laut ČGS-Bodenkarte eutroph oder kalkhaltig (Rendzina, Pararendzina, Kalk, Mergel, Löss) oder aus basischem Gestein (Basalt, Diabas, Amphibolit und ähnliche)"')
rep('regel:"nutzbare Feldkapazität ab 180 mm und Wasserdurchlässigkeit unter 40 cm/Tag (höchstens mittel)"',
    'regel:"tiefgründige Lehmböden aus Löss oder Lösslehm (Hnědozem, Luvizem, Braunerde mit Lösslehmdecke); Näherung, gemessene Feldkapazitäten gibt es hier nicht"')
rex(r'const PH_SRC=\{.*?\}\};\nfunction phRaster',
 'const PH_SRC={cgs:{n:"ČGS-Bodenkarte (Subtyp und Gestein)",kind:"unit",info:"Sauer und basisch nach den Angaben der Bodenkarte: Basenarmut (dystrisch, oligotroph) und Podsolierung gegen Eutrophie, Kalk und basisches Gestein. Gemessene Kennwerte wie die Basensättigung des LfU gibt es für Tschechien nicht; der SoilGrids-pH am Punkt dient als Gegenprobe."}};\nfunction phRaster')
rex(r'function pzMatch\(K,p,src\)\{.*?\n  return false; \}\n',
 'function pzMatch(K,p,src){ const u=D.units[K.leg]; if(!u||!u.zc) return false; return !!u.zc[{sauer:0,basisch:1,wasser:2}[p]]; }\n')
rex(r'    const rows=\[\n.*?\]\];\n',
 '    const rows=[\n      ["cgs", leg&&D.units[leg]?D.units[leg].p.saeure.wert:"keine Angabe", leg&&D.units[leg]&&D.units[leg].zc?unitCls("cgs"):null],\n'
 '      ["sg", parts.sg===undefined?"…":parts.sg==null?"keine Angabe":`pH ${fmt(parts.sg,1)} (in Wasser gemessen)`, parts.sg==null?null:clsPh(parts.sg-0.6)]];\n')
rex(r'    h\+=`<div class="prop"><div class="pn"><span>Baumart \(Thünen-Institut, 10 m\).*?\n','')
rex(r'  treeAt\(ll\)\.then.*?\n','')
rex(r'  thAt\("geonode:pH_map_0_30",ll\).*?\n','')
rex(r'  thAt\("geonode:pH_map_30_100",ll\).*?\n','')
rep('In der Claude-Artifact-Ansicht sind Wetter, Hang und Baumart gesperrt.','In der Claude-Artifact-Ansicht sind Wetter und Hang gesperrt.')
t=t.replace('"lfuW"','"cgs"')
rep('<div class="row"><label><input type="checkbox" id="cTree">','<div class="row" style="display:none"><label><input type="checkbox" id="cTree">')
rep('<div class="pzleg" id="treeLeg"></div>','<div class="pzleg" id="treeLeg" style="display:none"></div><p class="note">Eine offene Baumartenkarte wie die des Thünen-Instituts gibt es für Tschechien nicht. Laub- und Nadelwald trennt auch ZABAGED nicht.</p>')
rep("Sauer und basisch richten sich nach der gewählten pH-Grundlage, „gute Wasserspeicher“ immer nach den LfU-Wasserwerten.",
    "Sauer, basisch und „gute Wasserspeicher“ kommen aus den Angaben der ČGS-Bodenkarte (Bodentyp, Subtyp, Gestein); gemessene Kennwerte gibt es hier nicht.")
rex(r'<p class="note">Weitere Quellen: <a href="https://www\.ufz\.de/duerremonitor".*?</p>',
 '<p class="note">Weitere Quellen: <a href="https://www.intersucho.cz" target="_blank" rel="noopener">InterSucho</a> (Dürre und Bodenfeuchte in Tschechien), <a href="https://www.myko.cz" target="_blank" rel="noopener">Tschechische Mykologische Gesellschaft</a>.</p>')
rep('Ortssuche und Ersatzkarte: © OpenStreetMap-Mitwirkende (ODbL).','Ortssuche und Ersatzkarte: © OpenStreetMap-Mitwirkende (ODbL). Pilzsuche: Hangrichtung aus AWS Terrain Tiles (u. a. EU-DEM, SRTM); Wetter Open-Meteo (CC BY 4.0); Fundmeldungen iNaturalist (Lizenzen der Beobachter); pH am Punkt SoilGrids © ISRIC (CC BY 4.0). Faustregeln nach dem Pilzsammler-Buch, Kapitel „Digital Hotspots finden“ und „Digital den perfekten Moment finden“.')
rep("LfU-Werte und Gestein gelten als Mittel der ganzen Bodeneinheit, die Rasterkarten für diesen Punkt. Thünen-Werte stammen aus den Bodenzustandserhebungen (dort in der Regel in CaCl2 gemessen); SoilGrids misst in Wasser, das liegt meist 0,5 bis 1 pH-Einheit höher, deshalb ist für die Einstufung 0,6 abgezogen. SoilGrids ist ein weltweites Modell und nur zum Vergleich aufgeführt.",
    "Die Angaben der Bodenkarte gelten für die ganze Bodeneinheit, SoilGrids ist ein Modellwert für diesen Punkt (Raster 250 m). SoilGrids misst in Wasser, das liegt meist 0,5 bis 1 pH-Einheit über dem in CaCl2 gemessenen Wert, deshalb ist für die Einstufung 0,6 abgezogen.")
rep('<div class="pr">pH-Grundlage: ${esc(PH_SRC[S.phSrc].n)} (unter „Pilzsuche“ umstellbar).</div>','<div class="pr">Grundlage: ${esc(PH_SRC[S.phSrc].n)}; SoilGrids unten als Gegenprobe.</div>')
# ---- Bildexport ----
rep('x.fillText("Bodenkarte Bayern: Soilscapes-Vergleich",X,y)','x.fillText("Bodenkarte Westböhmen: Soilscapes-Vergleich",X,y)')
rex(r'wrap\("Boden: ÜBK25, ÜMBK25.*?"\+\(tainted',
 'wrap("Boden © Česká geologická služba (Bodenkarte 1 : 50 000 und 1 : 1 000 000, GEOČR50), verändert. Nutzung ZABAGED und Höhe DMR 4G © ČÚZK (CC BY 4.0); LPIS © MZe."+(tainted')
rep('const name="bodenkarte_bayern_"+new Date()','const name="bodenkarte_westboehmen_"+new Date()')

# ---- Pilzfunktionen still legen (keine Daten für Tschechien) ----

open("/home/claude/cz/template_cz.html","w",encoding="utf-8").write(t)
left=re.findall(r".{0,40}(?:ÜBK25|LfU|Bayern|CORINE|ATKIS|InVeKoS|Landkreis|basemap\.de|UTM32 \$).{0,40}",t)
print("fertig",len(t),"Reste:",len(left))
for l in left: print("  ",l)
