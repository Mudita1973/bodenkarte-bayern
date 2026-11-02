"""v11.6: Auf dem Handy die generalisierte Ebene freigeben, solange die Detailflächen vollständig da sind (gilt für beide Karten)."""
import sys
p=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bk/template10.html"
t=open(p,encoding="utf-8").read()
def rep(a,b,n=1):
    global t
    c=t.count(a)
    if c!=n: sys.exit(f"{c} Treffer statt {n}: {a[:90]!r}")
    t=t.replace(a,b)
rep('const G=decode(D.bin,D.tr); D.bin=null;','const G=decode(D.bin,D.tr); if(!TOUCH) D.bin=null;')
rep('let luSoon=null; function levelUpdateSoon(){',
    'let genDropT=null;\n'
    'function genDrop(){ if(!genBuilt) return; if(map.hasLayer(genGroup)) map.removeLayer(genGroup); genGroup.clearLayers(); for(const l of layers){ l._rings=null; l._parts=null; } layers.length=0; genBuilt=false; genQueue=null; if(hovLayer&&!hovLayer._map) hovLayer=null; }\n'
    'let luSoon=null; function levelUpdateSoon(){')
rep('  else { if(!genBuilt) ensureGen(); if(!map.hasLayer(genGroup)) genGroup.addTo(map); if(map.hasLayer(ovGroup)) map.removeLayer(ovGroup); genShow(!(det && complete)); }',
'''  else if(TOUCH && det){
    // Handy in der Detailansicht: generalisierte Ebene nur als Übergang; ist alles Detail geladen, wird sie nach 2,5 s freigegeben.
    if(complete){ if(map.hasLayer(ovGroup)) map.removeLayer(ovGroup); if(genBuilt){ genShow(false); clearTimeout(genDropT); genDropT=setTimeout(()=>{ if(TOUCH&&detailActive()&&detailUpdate()) genDrop(); },2500); } }
    else if(genBuilt){ clearTimeout(genDropT); if(!map.hasLayer(genGroup)) genGroup.addTo(map); genShow(true); if(map.hasLayer(ovGroup)) map.removeLayer(ovGroup); }
    else { if(!map.hasLayer(ovGroup)) ovGroup.addTo(map); if(ovRenderer._container) ovRenderer._container.style.display=""; } }
  else { clearTimeout(genDropT); if(!genBuilt) ensureGen(); if(!map.hasLayer(genGroup)) genGroup.addTo(map); if(map.hasLayer(ovGroup)) map.removeLayer(ovGroup); if(ovRenderer._container) ovRenderer._container.style.display="none"; genShow(!(det && complete)); }''')
rep('  ensureGen(); for(const l of layers) if(layerHas(l,ll)) return l;','  if(!(TOUCH&&detailActive())) ensureGen(); for(const l of layers) if(layerHas(l,ll)) return l;')
open(p,"w",encoding="utf-8").write(t); print("ok v116")
