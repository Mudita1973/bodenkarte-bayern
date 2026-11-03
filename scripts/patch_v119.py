import sys
p="/home/claude/bk/template10.html"; t=open(p,encoding="utf-8").read()
def rep(a,b):
    global t
    n=t.count(a)
    if n!=1: sys.exit(f"{n} Treffer: {a[:80]}")
    t=t.replace(a,b)
rep('<p class="note" style="margin:-4px 0 10px"><a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/" target="_blank" rel="noopener">Nachbarkarte: Bodenkarte Westböhmen (Tschechien) →</a> öffnet denselben Ausschnitt mit denselben Kategorien.</p>',
    '<p class="note" style="margin:-4px 0 10px">Nachbarkarten: <a id="otherMap" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/" target="_blank" rel="noopener">Westböhmen (Tschechien) →</a> · <a id="otherMap2" href="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-bw/" target="_blank" rel="noopener">Baden-Württemberg →</a> öffnen denselben Ausschnitt mit denselben Kategorien.</p>')
rep('const OTHER_URL="https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/", OTHER_BB=[48.55,12.09,50.46,15.60], OTHER_C="49.50%2C13.85&z=8", OTHER_LU={gw:"gs",gm:"gs",gp:"gs",gs:"gs",wl:"wm",wn:"wm",wm:"wm",oh:""};',
    'const OTHERS=[{id:"otherMap",url:"https://mudita1973.github.io/bodenkarte-bayern/soilscapes-cz/",bb:[48.55,12.09,50.46,15.60],c:"49.50%2C13.85&z=8",lu:{gw:"gs",gm:"gs",gp:"gs",gs:"gs",wl:"wm",wn:"wm",wm:"wm",oh:""}},\n  {id:"otherMap2",url:"https://mudita1973.github.io/bodenkarte-bayern/soilscapes-bw/",bb:[47.53,7.51,49.79,10.50],c:"48.65%2C9.00&z=8",lu:{}}];')
a=t.index("function otherLink(){"); b=t.index("function hashToState(h){")
t=t[:a]+'''function otherLink(){ if(!D) return; const b=map.getBounds();
  for(const O of OTHERS){ const el=$(O.id); if(!el) continue; if(!el.dataset.t) el.dataset.t=el.textContent;
    const inside=b.getSouth()<=O.bb[2]&&b.getNorth()>=O.bb[0]&&b.getWest()<=O.bb[3]&&b.getEast()>=O.bb[1];
    let parts=stateToHash().replace(/^[^#]*#/,"").split("&").filter(x=>x&&!/^(u|p|pz|ph|phf|pa|pt|pi)=/.test(x));
    if(!inside) parts=["c="+O.c].concat(parts.filter(x=>!/^(c|z)=/.test(x)));
    parts=parts.map(x=>{ if(!x.startsWith("l=")) return x; const v=[...new Set(decodeURIComponent(x.slice(2)).split(".").flatMap(i=>(i in O.lu?O.lu[i]:i).split(".")).filter(Boolean))]; return v.length?"l="+v.join("."):""; }).filter(Boolean);
    el.href=O.url+"#"+parts.join("&"); el.textContent=el.dataset.t+(inside?"":" (Übersicht, dieser Ausschnitt liegt außerhalb)"); } }
'''+t[b:]
rep('$("otherMap").addEventListener("click",otherLink);','OTHERS.forEach(O=>{ const el=$(O.id); if(el) el.addEventListener("click",otherLink); });')
rep('const L_=[]; const z=D.units[leg]&&D.units[leg].z; const nfk=z?z[2]:null;','const L_=[]; const z=D.units[leg]&&D.units[leg].z; const nfk=z?z[4]:null;')
open(p,"w",encoding="utf-8").write(t); print("ok")
