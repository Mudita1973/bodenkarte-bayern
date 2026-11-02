"""v11.8: stufenlose Deckkraft je Ebene und eigener Standort (gilt für beide Karten)."""
import sys
p=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bk/template10.html"
t=open(p,encoding="utf-8").read()
def rep(a,b,n=1):
    global t
    c=t.count(a)
    if c!=n: sys.exit(f"{c} Treffer statt {n}: {a[:90]!r}")
    t=t.replace(a,b)

# ---------- 1) Deckkraft je Ebene ----------
SL=lambda k,n: (f'<div class="row oprow" id="opRow_{k}" style="margin-top:4px"><span style="flex:1">{n}</span>'
                f'<input type="range" class="opl" data-k="{k}" aria-label="Deckkraft {n}" min="0" max="1" step="0.05" value="1" style="width:140px"><span class="opv" id="opv_{k}" style="width:42px;text-align:right">100 %</span></div>')
rep('      <div class="row"><label><input type="checkbox" id="cOutline"> nur Umrisse (für Luftbild)</label>',
    '      <div class="row" style="margin-top:10px;font-weight:600;color:var(--text-primary)">Deckkraft der Ebenen</div>\n'
    + "\n".join("      "+SL(k,n) for k,n in (("lu","Nutzung"),("pz","Pilzböden"),("asp","Hangrichtung"),("ph","pH-Karte"),("tree","Baumarten"),("inat","Fundmeldungen")))
    + '\n      <p class="note" style="margin-top:2px">Wirkt auf die eingeblendeten Ebenen; die Bodenfarben regelt der Schieber „Deckkraft“ oben.</p>\n'
    '      <div class="row"><label><input type="checkbox" id="cOutline"> nur Umrisse (für Luftbild)</label>')
rep('lu:new Set(SUB_IDS), luMask:false,','lu:new Set(SUB_IDS), opL:{lu:1,pz:1,asp:1,ph:1,tree:1,inat:1}, luMask:false,')
rep('$("op").oninput=e=>{ S.op=+e.target.value; for(const l of allLayers()) l.setStyle(styleFor(l)); detailRestyle(); };',
'''$("op").oninput=e=>{ S.op=+e.target.value; for(const l of allLayers()) l.setStyle(styleFor(l)); detailRestyle(); };
const OPL_PANE={lu:"luPane",asp:"aspPane",ph:"phPane",tree:"treePane",inat:"inatPane"};
function applyOpL(restyleSoil){ for(const [k,pn] of Object.entries(OPL_PANE)){ const pane=map.getPane(pn); if(pane) pane.style.opacity=S.opL[k]; }
  document.querySelectorAll("input.opl").forEach(i=>{ i.value=S.opL[i.dataset.k]; const v=$("opv_"+i.dataset.k); if(v) v.textContent=Math.round(S.opL[i.dataset.k]*100)+" %"; });
  if(restyleSoil){ for(const l of allLayers()) l.setStyle(styleFor(l)); detailRestyle(); } }
document.querySelectorAll("input.opl").forEach(i=>i.addEventListener("input",()=>{ const k=i.dataset.k; S.opL[k]=+i.value; applyOpL(k==="pz"); if(k==="pz"&&typeof phLayer!=="undefined"&&map.hasLayer(phLayer)) phLayer.redraw(); updateHash(); }));''')
# Pilzböden: eigener Faktor, wenn die Fläche nur über Pilzgruppen eingefärbt ist
rep('  if(cats.length && S.unsureDim && S.mode==="zuordnung" && !K.s) st.fillOpacity*=0.5;',
    '  if(cats.length && cats.every(c=>c.startsWith("p:"))) st.fillOpacity*=S.opL.pz;\n  if(cats.length && S.unsureDim && S.mode==="zuordnung" && !K.s) st.fillOpacity*=0.5;')
# Zustand: im Link und in gespeicherten Ständen
rep('lu:[...S.lu],luMask:S.luMask,luLayer:S.luLayer,outline:S.outline,base:S.base,','lu:[...S.lu],opL:{...S.opL},luMask:S.luMask,luLayer:S.luLayer,outline:S.outline,base:S.base,')
rep(' if(st.inat) o.pi=st.inat;',' if(st.inat) o.pi=st.inat; { const ks=Object.keys(S.opL); if(ks.some(k=>st.opL&&st.opL[k]!==1)) o.oe=ks.map(k=>Math.round(st.opL[k]*100)).join("."); }')
rep('inat:p.pi||"",base:p.b||"none",','inat:p.pi||"",opL:p.oe?Object.fromEntries(Object.keys(S.opL).map((k,i)=>[k,Math.min(1,Math.max(0,(+p.oe.split(".")[i]||100)/100))])):null,base:p.b||"none",')
rep('  if(S.pz.length||st.asp||st.tree||st.inat) S.pilzOpen=true; pzChips(); phSync();',
    '  S.opL=Object.assign({lu:1,pz:1,asp:1,ph:1,tree:1,inat:1},st.opL||{}); applyOpL(false);\n  if(S.pz.length||st.asp||st.tree||st.inat) S.pilzOpen=true; pzChips(); phSync();')
# Bildexport: Deckkraft der Ebene übernehmen
rep('const r=el.getBoundingClientRect(); if(!r.width) continue; x.save(); x.beginPath(); x.rect(0,0,swipeClip,H); x.clip(); x.drawImage(el,r.left-mr.left,r.top-mr.top,r.width,r.height); x.restore(); }',
    'const r=el.getBoundingClientRect(); if(!r.width) continue; const pn=el.closest(".leaflet-pane"); x.save(); x.globalAlpha=pn?(+getComputedStyle(pn).opacity||1):1; x.beginPath(); x.rect(0,0,swipeClip,H); x.clip(); x.drawImage(el,r.left-mr.left,r.top-mr.top,r.width,r.height); x.restore(); }')

# ---------- 2) Eigener Standort ----------
rep('new LuBtn().addTo(map);','''new LuBtn().addTo(map);
// Eigener Standort (nur im Browser, wird nicht gespeichert und an niemanden übertragen)
map.createPane("posPane").style.zIndex=650;
const POS={watch:null,mk:null,acc:null,first:true};
const PosBtn=L.Control.extend({options:{position:"topleft"},onAdd(){ const d=L.DomUtil.create("div","leaflet-bar leaflet-control");
  d.innerHTML='<a href="#" id="posBtn" role="button" title="Meinen Standort zeigen" aria-label="Meinen Standort zeigen" aria-pressed="false" style="font-size:17px;line-height:30px">◎</a>';
  L.DomEvent.disableClickPropagation(d); return d; }});
new PosBtn().addTo(map);
function posStop(){ if(POS.watch!=null) navigator.geolocation.clearWatch(POS.watch); POS.watch=null; if(POS.mk) map.removeLayer(POS.mk); if(POS.acc) map.removeLayer(POS.acc); POS.mk=POS.acc=null;
  const b=$("posBtn"); b.setAttribute("aria-pressed","false"); b.style.color=""; b.title="Meinen Standort zeigen"; }
function posStart(){
  if(!("geolocation" in navigator)){ toast("Dieser Browser kann den Standort nicht bestimmen."); return; }
  if(inArtifact()){ toast("In der Claude-Artifact-Ansicht ist der Standort gesperrt; die Online-Fassung nutzen."); return; }
  POS.first=true; const b=$("posBtn"); b.setAttribute("aria-pressed","true"); b.style.color=css("--hl")||"#1a73e8"; b.title="Standort ausblenden"; toast("Standort wird bestimmt …");
  POS.watch=navigator.geolocation.watchPosition(p=>{ const ll=L.latLng(p.coords.latitude,p.coords.longitude), a=p.coords.accuracy||0;
      if(!POS.mk){ POS.acc=L.circle(ll,{radius:a,pane:"posPane",color:"#1a73e8",weight:1,fillColor:"#1a73e8",fillOpacity:0.12,interactive:false}).addTo(map);
        POS.mk=L.circleMarker(ll,{radius:7,pane:"posPane",color:"#fff",weight:2.5,fillColor:"#1a73e8",fillOpacity:1}).addTo(map).bindTooltip("Mein Standort");
        POS.mk.on("click",ev=>{ L.DomEvent.stopPropagation(ev); const q=POS.mk.getLatLng(); showPoint(q,findLayerAt(q)); }); }
      else { POS.mk.setLatLng(ll); POS.acc.setLatLng(ll).setRadius(a); }
      if(POS.first){ POS.first=false; map.setView(ll,Math.max(map.getZoom(),14)); toast(`Standort auf etwa ${fmt(a)} m genau. Antippen des blauen Punkts zeigt den Boden dort.`); } },
    e=>{ posStop(); toast(e.code===1?"Standortfreigabe verweigert. Im Browser für diese Seite erlauben.":e.code===3?"Standort nicht rechtzeitig gefunden.":"Standort nicht verfügbar (ohne GPS, offline oder Datei vom Rechner)."); },
    {enableHighAccuracy:true,maximumAge:10000,timeout:20000}); }
$("posBtn").onclick=ev=>{ ev.preventDefault(); if(POS.watch!=null){ const q=POS.mk&&POS.mk.getLatLng(); if(q&&!map.getBounds().contains(q)){ map.setView(q); return; } posStop(); } else posStart(); };''')
open(p,"w",encoding="utf-8").write(t); print("ok v118")
