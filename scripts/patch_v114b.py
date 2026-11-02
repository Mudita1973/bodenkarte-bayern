"""v11.4 Teil 2: Fehler aus der Code-Prüfung (gilt für beide Karten)."""
import sys
p=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bk/template10.html"
t=open(p,encoding="utf-8").read()
def rep(a,b,n=1):
    global t
    c=t.count(a)
    if c!=n: sys.exit(f"{c} Treffer statt {n}: {a[:80]!r}")
    t=t.replace(a,b)
# Hängende Nutzungskacheln: beim Wegzoomen auch wartende Einträge verwerfen; wartende ohne Warteplatz neu einreihen
rep('  if(!vecWanted()){ vecQ=[]; luvSoon(); return; }',
    '  if(!vecWanted()){ vecQ=[]; for(const s of ["a","i"]) for(const [k,x] of [...VT[s]]) if(x.st==="wait") VT[s].delete(k); luvSoon(); return; }')
rep('for(const w of want){ const [s,k]=w.split(":"), t=VT[s].get(k); if(!t||(t.st==="err"&&Date.now()-t.t>60000)){ VT[s].set(k,{st:"wait"}); vecQ.push(w); } }',
    'const inQ=new Set(vecQ); for(const w of want){ const [s,k]=w.split(":"), t=VT[s].get(k); if(!t||(t.st==="err"&&Date.now()-t.t>60000)||(t.st==="wait"&&!inQ.has(w))){ VT[s].set(k,{st:"wait"}); vecQ.push(w); } }')
# Nachbarkarten-Link: Nutzungsauswahl in die Unterarten der anderen Karte übersetzen
rep('OTHER_C="49.50%2C13.85&z=8";','OTHER_C="49.50%2C13.85&z=8", OTHER_LU={gw:"gs",gm:"gs",gp:"gs",gs:"gs",wl:"wm",wn:"wm",wm:"wm",oh:""};')
rep('  if(!inside) parts=["c="+OTHER_C].concat(parts.filter(x=>!/^(c|z)=/.test(x)));',
    '  if(!inside) parts=["c="+OTHER_C].concat(parts.filter(x=>!/^(c|z)=/.test(x)));\n'
    '  parts=parts.map(x=>{ if(!x.startsWith("l=")) return x; const v=[...new Set(decodeURIComponent(x.slice(2)).split(".").flatMap(i=>(i in OTHER_LU?OTHER_LU[i]:i).split(".")).filter(Boolean))]; return v.length?"l="+v.join("."):""; }).filter(Boolean);')
# Zustand aus Link oder Sicherung: nur bekannte Kategorien und Einheiten übernehmen
rep('Object.assign(S,{sel:st.sel,units:st.units,','Object.assign(S,{sel:(st.sel||[]).filter(x=>CL[x]),units:(st.units||[]).filter(u=>D.units[u]),')
# Textur: „Oberboden:“ nur mit Wert
rep('P.textur.beleg?`Oberboden: ${esc(P.textur.oberboden)}<br>${q(P.textur.beleg)}`:""',
    'P.textur.beleg?`${P.textur.oberboden?"Oberboden: "+esc(P.textur.oberboden)+"<br>":""}${q(P.textur.beleg)}`:""')
rep('const c=map.getCenter(), inside=c.lat>=OTHER_BB[0]&&c.lat<=OTHER_BB[2]&&c.lng>=OTHER_BB[1]&&c.lng<=OTHER_BB[3];',
    'const b=map.getBounds(), inside=b.getSouth()<=OTHER_BB[2]&&b.getNorth()>=OTHER_BB[0]&&b.getWest()<=OTHER_BB[3]&&b.getEast()>=OTHER_BB[1];')
open(p,"w",encoding="utf-8").write(t); print("ok 2")
