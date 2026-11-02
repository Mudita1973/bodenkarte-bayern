"""v11.4: Beschriftungen ohne Überlappung, kompakte Quellenzeile auf dem Handy, Bezeichnungen für Auswahllisten,
Nachbarkarten-Link fällt außerhalb des Nachbargebiets auf dessen Übersicht zurück."""
import sys
p="/home/claude/bk/template10.html"; t=open(p,encoding="utf-8").read()
def rep(a,b,n=1):
    global t
    c=t.count(a)
    if c!=n: sys.exit(f"{c} Treffer statt {n}: {a[:80]!r}")
    t=t.replace(a,b)
# 1) Beschriftungen entzerren: Städte vor Landschaften, überlappende ausblenden
rep('''  map.on("zoomend",()=>{ const z=map.getZoom(); grp.eachLayer(m=>{ const el=m.getElement(); if(el) el.style.display = z>11 ? "none" : ""; }); });''',
'''  const lab=()=>{ const z=map.getZoom(), items=[], kept=[];
    grp.eachLayer(m=>{ const el=m.getElement(); if(!el) return; el.style.display = z>11 ? "none" : ""; el.style.visibility=""; items.push(el); });
    if(z>11) return;
    items.sort((a,b)=>(a.querySelector(".land")?1:0)-(b.querySelector(".land")?1:0));
    for(const el of items){ const r=(el.firstElementChild||el).getBoundingClientRect(); if(!r.width) continue;
      if(kept.some(k=>r.left<k.right+3&&r.right>k.left-3&&r.top<k.bottom+2&&r.bottom>k.top-2)) el.style.visibility="hidden"; else kept.push(r); } };
  map.on("zoomend resize",lab); setTimeout(lab,0);''')
rep('const st=getComputedStyle(el.parentElement); if(st.display==="none") continue;','const st=getComputedStyle(el.parentElement); if(st.display==="none"||st.visibility==="hidden") continue;')
# 2) Quellenzeile auf schmalen Bildschirmen einzeilig, Antippen klappt auf
rep('</style>\n</head>','''.leaflet-control-attribution.compact{max-height:1.45em;overflow:hidden;cursor:pointer;white-space:nowrap;text-overflow:ellipsis;max-width:70vw}
.leaflet-control-attribution.compact.open{max-height:none;white-space:normal}
</style>
</head>''')
rep('map.attributionControl.setPrefix(false)','(()=>{ const a=map.attributionControl.getContainer(); if(matchMedia("(max-width: 700px)").matches){ a.classList.add("compact"); a.title="Quellen anzeigen"; a.addEventListener("click",()=>a.classList.toggle("open")); } })();\nmap.attributionControl.setPrefix(false)')
# 3) Bezeichnungen für Auswahllisten (Bildschirmleser)
rep('id="op" min=','id="op" aria-label="Deckkraft der Bodenfarben" min=')
rep('<select id="basemap"','<select id="basemap" aria-label="Hintergrundkarte"')
rep('<select id="phSrc"','<select id="phSrc" aria-label="pH-Grundlage"')
rep('<select id="stCls"','<select id="stCls" aria-label="Klasse für die Statistik"')
rep('<select id="stSort"','<select id="stSort" aria-label="Sortierung der Statistik"')
# 4) Nachbarkarten-Link: außerhalb des Nachbargebiets dessen Übersicht öffnen
rep('const OTHER_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/";',
    'const OTHER_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/", OTHER_BB=[48.55,12.09,50.46,15.60], OTHER_C="49.50%2C13.85&z=8";')
rep('function otherLink(){ const el=$("otherMap"); if(!el||!D) return; const h=stateToHash().replace(/^[^#]*#/,""); el.href=OTHER_URL+"#"+h.split("&").filter(x=>x&&!/^(u|p|pz|ph|phf|pa|pt|pi)=/.test(x)).join("&"); }',
'''function otherLink(){ const el=$("otherMap"); if(!el||!D) return; if(!el.dataset.t) el.dataset.t=el.textContent;
  const c=map.getCenter(), inside=c.lat>=OTHER_BB[0]&&c.lat<=OTHER_BB[2]&&c.lng>=OTHER_BB[1]&&c.lng<=OTHER_BB[3];
  let parts=stateToHash().replace(/^[^#]*#/,"").split("&").filter(x=>x&&!/^(u|p|pz|ph|phf|pa|pt|pi)=/.test(x));
  if(!inside) parts=["c="+OTHER_C].concat(parts.filter(x=>!/^(c|z)=/.test(x)));
  el.href=OTHER_URL+"#"+parts.join("&"); el.textContent=el.dataset.t+(inside?"":" (Übersicht, dieser Ausschnitt liegt außerhalb)"); }''')
open(p,"w",encoding="utf-8").write(t); print("ok")
