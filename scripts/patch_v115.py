"""v11.5: weniger Speicher, vor allem auf dem Handy (gilt für beide Karten)."""
import sys
p=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bk/template10.html"
t=open(p,encoding="utf-8").read()
def rep(a,b,n=1):
    global t
    c=t.count(a)
    if c!=n: sys.exit(f"{c} Treffer statt {n}: {a[:90]!r}")
    t=t.replace(a,b)
# 1) Gepackte Daten nicht als JS-Zeichenkette halten, sondern aus einem Textelement lesen und es danach entfernen
rep('let D=null; const D_GZ="/*DATAGZ*/";','let D=null;')
rep('<script>/*LEAFLET_JS*/</script>','<script type="text/plain" id="dgz">/*DATAGZ*/</script>\n<script>/*LEAFLET_JS*/</script>')
rep('const bin=atob(D_GZ), u=new Uint8Array(bin.length);','const el=document.getElementById("dgz"), bin=atob(el.textContent.trim()); el.remove(); const u=new Uint8Array(bin.length);')
# 2) Rasterbilder nach dem Entpacken freigeben
rep('    const cbs=q[kind]; q[kind]=null; cbs.forEach(f=>f());','    src.png=null; const cbs=q[kind]; q[kind]=null; cbs.forEach(f=>f());')
# 3) Generalisierte Ebene: Rohdaten nach dem Entpacken freigeben, nicht vorab an die Karte hängen
rep('function genPrepare(){ if(genQueue||genBuilt) return; const G=decode(D.bin,D.tr); genQueue=G.map((p,i)=>[p,D.feat[i]]);',
    'function genPrepare(){ if(genQueue||genBuilt) return; const G=decode(D.bin,D.tr); D.bin=null; genQueue=G.map((p,i)=>[p,D.feat[i]]);')
rep('function ensureGen(){ if(genBuilt) return; if(!map.hasLayer(genGroup)) genGroup.addTo(map); genPrepare();','function ensureGen(){ if(genBuilt) return; genPrepare();')
rep('function ensureGenIdle(){ if(genBuilt) return; if(!map.hasLayer(genGroup)) genGroup.addTo(map); genPrepare();','function ensureGenIdle(){ if(genBuilt) return; genPrepare();')
rep('  const G=decode(D.ov.bin, D.ov.tr);','  const G=decode(D.ov.bin, D.ov.tr); D.ov.bin=null;')
# 4) Unsichtbare Ebene von der Karte nehmen statt nur verstecken (spart Neuberechnung bei jedem Zoom)
rep('  if(ov){ ovRenderer._container&&(ovRenderer._container.style.display=""); if(!map.hasLayer(ovGroup)) ovGroup.addTo(map); genShow(false); }\n'
    '  else { if(!genBuilt) ensureGen(); if(ovRenderer._container) ovRenderer._container.style.display="none"; genShow(!(det && complete)); }',
    '  if(ov){ ovRenderer._container&&(ovRenderer._container.style.display=""); if(!map.hasLayer(ovGroup)) ovGroup.addTo(map); if(map.hasLayer(genGroup)) map.removeLayer(genGroup); genShow(false); }\n'
    '  else { if(!genBuilt) ensureGen(); if(!map.hasLayer(genGroup)) genGroup.addTo(map); if(map.hasLayer(ovGroup)) map.removeLayer(ovGroup); genShow(!(det && complete)); }')
# 5) Auf dem Handy die generalisierte Ebene erst beim Hineinzoomen bauen und weniger Detailkacheln vorhalten
rep('idle(()=>{ ensureDEM(); ensureGenIdle(); },{timeout:4000});','idle(()=>{ ensureDEM(); if(!TOUCH) ensureGenIdle(); },{timeout:4000});')
rep('if(detLoaded.size>80) detLoaded.delete(t);','if(detLoaded.size>(TOUCH?30:80)) detLoaded.delete(t);')
open(p,"w",encoding="utf-8").write(t); print("ok v115")
