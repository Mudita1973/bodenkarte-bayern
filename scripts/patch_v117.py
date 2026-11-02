import sys
p=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bk/template10.html"
t=open(p,encoding="utf-8").read()
def rep(a,b):
    global t; c=t.count(a)
    if c!=1: sys.exit(f"{c} Treffer: {a[:80]!r}")
    t=t.replace(a,b)
rep('let genDropT=null;','let genDropT=null;\n'
    'function genBuildAsync(){ if(genBuilt||genQueue) return; genPrepare(); const tick=()=>{ if(genBuilt||!genQueue) return; genStep(250); if(genBuilt) levelUpdate(); else setTimeout(tick,0); }; setTimeout(tick,0); }')
rep('  else { clearTimeout(genDropT); if(!genBuilt) ensureGen();',
    '  else { clearTimeout(genDropT);\n'
    '    // Handy: generalisierte Ebene in Schritten bauen, die Übersicht bleibt so lange stehen (kein Einfrieren)\n'
    '    if(!genBuilt&&TOUCH){ genBuildAsync(); if(!map.hasLayer(genGroup)) genGroup.addTo(map); if(!map.hasLayer(ovGroup)) ovGroup.addTo(map); if(ovRenderer._container) ovRenderer._container.style.display=""; genShow(true); applySwipe(); return; }\n'
    '    if(!genBuilt) ensureGen();')
open(p,"w",encoding="utf-8").write(t); print("ok v117")
