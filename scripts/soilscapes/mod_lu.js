// ---------------- Nutzung: Auswahl und Darstellung ----------------
let luOpenG={};
function buildLuBoxes(){
  const box=$("luList"); if(!box){ syncLuMode(); return; }
  box.innerHTML=`<div class="lsh"><span></span><span id="luBasis">Anteil im Ausschnitt</span></div>`+LUG.map(G=>`<div class="grp"><div class="gr"><button class="ex" data-ex="${G.g}" aria-expanded="${!!luOpenG[G.g]}" title="Unterarten zeigen">${luOpenG[G.g]?"▾":"▸"}</button><label><input type="checkbox" data-g="${G.g}"><span class="sw" style="background:${SUB[G.subs[0][0]].col}"></span>${G.n}</label><span class="pc" id="pc_${G.g}"></span></div>`+
    `<div class="subs"${luOpenG[G.g]?"":" hidden"}>${G.subs.map(([id,n,col])=>`<div class="gr sr"><span></span><label><input type="checkbox" data-s="${id}"${S.lu.has(id)?" checked":""}><span class="sw" style="background:${col}"></span>${n}</label><span class="pc" id="pc_${id}"></span></div>`).join("")}${G.g==="g"?`<div class="nt" style="margin:2px 0 4px 26px">Wiese, Mähweide und Weide sind erst ab Zoomstufe ${INV_Z} getrennt (Agrarantrag). Darunter zählt alles als „ohne nähere Angabe“.</div>`:""}</div></div>`).join("");
  LUG.forEach(G=>{ const cb=box.querySelector(`input[data-g="${G.g}"]`), n=G.subs.filter(s=>S.lu.has(s[0])).length;
    cb.checked=n===G.subs.length; cb.indeterminate=n>0&&n<G.subs.length;
    cb.onchange=()=>{ G.subs.forEach(([id])=>cb.checked?S.lu.add(id):S.lu.delete(id)); luTouched(); }; });
  box.querySelectorAll("input[data-s]").forEach(cb=>cb.onchange=()=>{ cb.checked?S.lu.add(cb.dataset.s):S.lu.delete(cb.dataset.s); luTouched(); });
  box.querySelectorAll("[data-ex]").forEach(b=>b.onclick=()=>{ luOpenG[b.dataset.ex]=!luOpenG[b.dataset.ex]; buildLuBoxes(); luShares(); });
  syncLuMode(); }
function luTouched(){ if(!S.luMask&&!S.luLayer){ S.luLayer=true; luAutoBase(); } buildLuBoxes(); restyle(); }
function syncLuMode(){
  for(const [a,b] of [["luLay","cLuLayer"],["luMsk","cMask"]]){ const v=a==="luLay"?S.luLayer:S.luMask; if($(a)) $(a).checked=v; if($(b)) $(b).checked=v; }
  if($("luSoil")) $("luSoil").checked=S.soil; if($("cSoil")) $("cSoil").checked=S.soil;
  const t=$("luTog"); if(t){ const on=S.luLayer||S.luMask; t.innerHTML=`Nutzung${on?' <span class="dot"></span>':""} ▾`; t.classList.toggle("on",on); } }
function luAutoBase(){ if(luAutoBase.done) return; luAutoBase.done=true; if(S.base==="none" && !inArtifact()){ setBase("topo"); toast("Topografische Hintergrundkarte eingeschaltet (änderbar unter „Darstellung“)"); } }
function luSetLayer(v){ S.luLayer=v; if(v) luAutoBase(); syncLuMode(); restyle(); }
function luSetMask(v){ S.luMask=v; if(v) luAutoBase(); syncLuMode(); restyle(); }
$("luLay").onchange=e=>luSetLayer(e.target.checked); $("cLuLayer").onchange=e=>luSetLayer(e.target.checked);
$("luMsk").onchange=e=>luSetMask(e.target.checked); $("cMask").onchange=e=>luSetMask(e.target.checked);
$("luSoil").onchange=e=>{ S.soil=e.target.checked; syncLuMode(); restyle(); };
const LU_PRE={alle:()=>SUB_IDS, gruen:()=>SUB_IDS.filter(s=>SUB[s].g==="g"), acker:()=>SUB_IDS.filter(s=>SUB[s].g==="a"), ohnewald:()=>SUB_IDS.filter(s=>SUB[s].g!=="w"), wald:()=>SUB_IDS.filter(s=>SUB[s].g==="w")};
document.querySelectorAll("#luPanel .pre button").forEach(b=>b.onclick=()=>{ S.lu=new Set(LU_PRE[b.dataset.p]()); if(b.dataset.p!=="alle"){ for(const g of "agwso") luOpenG[g]=false; luOpenG[{gruen:"g",acker:"a",wald:"w"}[b.dataset.p]]=true; } luTouched(); });
const LuBtn=L.Control.extend({options:{position:"topright"},onAdd(){ const d=L.DomUtil.create("div","lucard leaflet-control"); d.id="luCtl";
  d.innerHTML=`<button class="tog" id="luTog" aria-expanded="false" aria-controls="luPanel">Nutzung ▾</button>`; L.DomEvent.disableClickPropagation(d); return d; }});
new LuBtn().addTo(map);
function luPanel(open){ $("luPanel").hidden=!open; $("luTog").setAttribute("aria-expanded",open); $("luCtl").style.visibility=open?"hidden":""; if(open){ luStatus(); ensureLU(()=>luShares()); luShares(); } }
$("luTog").onclick=()=>luPanel(true); $("luClose").onclick=()=>luPanel(false);
if($("luOpen")) $("luOpen").onclick=()=>{ luPanel(true); $("map").scrollIntoView({behavior:"smooth",block:"start"}); };
function normLu(arr){ if(!arr) return SUB_IDS.slice(); const out=new Set(); for(const v of arr){ if(SUB[v]) out.add(v); else if(LUN[+v]) LUN[+v].s.forEach(s=>out.add(s)); } return [...out]; }

// ---------------- Amtliche Nutzung (online): ATKIS Basis-DLM und InVeKoS-Schläge ----------------
const VEC_Z=13, INV_Z=14, TILE=4000;
const ATKIS_URL="https://geoservices.bayern.de/wfs/v1/ogc_atkis_basisdlm.cgi";
const GSA_URL="https://gdiserv.bayern.de/srv66381/services/invekos_gsa-wfs";
const TN_TYPES=["AX_Wohnbauflaeche","AX_IndustrieUndGewerbeflaeche","AX_Halde","AX_TagebauGrubeSteinbruch","AX_FlaecheGemischterNutzung","AX_FlaecheBesondererFunktionalerPraegung","AX_SportFreizeitUndErholungsflaeche","AX_Friedhof","AX_Strassenverkehr","AX_Platz","AX_Bahnverkehr","AX_Flugverkehr","AX_Schiffsverkehr","AX_Landwirtschaft","AX_Wald","AX_Gehoelz","AX_Heide","AX_Moor","AX_Sumpf","AX_UnlandVegetationsloseFlaeche","AX_Fliessgewaesser","AX_StehendesGewaesser","AX_Hafenbecken"];
const VF=new Map(), VT={a:new Map(),i:new Map()}; let vecQ=[], vecRun=0, vecOk=0, vecFail=0, vecDead=false, LUVIS=[];
function atkisSub(t,vm){
  if(t==="AX_Landwirtschaft"){ if(vm===1020||vm===1021) return "gs"; if([1012,1030,1031,1040,1050,1051,1052].includes(vm)) return "sk"; return "ak"; }
  if(t==="AX_Wald") return vm===1100?"wl":vm===1200?"wn":"wm";
  if(t==="AX_Gehoelz") return "wg"; if(t==="AX_Heide") return "oh"; if(t==="AX_Moor"||t==="AX_Sumpf") return "om";
  if(t==="AX_UnlandVegetationsloseFlaeche") return "of";
  if(t==="AX_Fliessgewaesser"||t==="AX_StehendesGewaesser"||t==="AX_Hafenbecken") return "sw";
  return "ss"; }
const ATKIS_NAME={AX_Wohnbauflaeche:"Wohnbaufläche",AX_IndustrieUndGewerbeflaeche:"Industrie- und Gewerbefläche",AX_Halde:"Halde",AX_TagebauGrubeSteinbruch:"Tagebau, Grube, Steinbruch",AX_FlaecheGemischterNutzung:"Fläche gemischter Nutzung",AX_FlaecheBesondererFunktionalerPraegung:"Fläche besonderer funktionaler Prägung",AX_SportFreizeitUndErholungsflaeche:"Sport-, Freizeit- und Erholungsfläche",AX_Friedhof:"Friedhof",AX_Strassenverkehr:"Straßenverkehr",AX_Platz:"Platz",AX_Bahnverkehr:"Bahnverkehr",AX_Flugverkehr:"Flugverkehr",AX_Schiffsverkehr:"Schiffsverkehr",AX_Gehoelz:"Gehölz",AX_Heide:"Heide",AX_Moor:"Moor",AX_Sumpf:"Sumpf",AX_UnlandVegetationsloseFlaeche:"Unland, vegetationslose Fläche",AX_Fliessgewaesser:"Fließgewässer",AX_StehendesGewaesser:"Stehendes Gewässer",AX_Hafenbecken:"Hafenbecken"};
const LW_NAME={1010:"Ackerland",1011:"Streuobstacker",1012:"Hopfen",1013:"Spargel",1020:"Grünland",1021:"Streuobstwiese",1030:"Gartenland",1031:"Baumschule",1040:"Weingarten",1050:"Obstplantage",1051:"Obstbaumplantage",1052:"Obststrauchplantage"};
function gsaSub(code,mc,desc){
  if(mc==="GL"){ if(/mähweide/i.test(desc)) return "gm"; if(/weide/i.test(desc)) return "gp"; if(/wiese/i.test(desc)) return "gw"; return "gs"; }
  if(mc==="DA"||code===844||code===983||/hopfen|obst|reb|wein|baumschul/i.test(desc)) return "sk";
  if(mc==="SF"){ if(code===930||code===940) return "sw"; if(code===921||code===942) return "ak"; return null; }
  if(mc==="SL") return code===592?"gs":"ak";
  if(code>=990) return null;
  return "ak"; }
function toZ0(arr){ const o=new Float64Array(arr.length); for(let j=0;j<arr.length;j+=2){ const [la,lo]=utmToLatLng(arr[j],arr[j+1]); const s=Math.sin(la*Math.PI/180); o[j]=256*(0.5+lo/360); o[j+1]=256*(0.5-Math.log((1+s)/(1-s))/(4*Math.PI)); } return o; }
function parsePolys(chunk){ const polys=[];
  for(const pc of chunk.split(/<gml:Polygon(?:Patch)?[\s>]/).slice(1)){ const rings=[];
    for(const m of pc.matchAll(/<gml:(exterior|interior)>([\s\S]*?)<\/gml:\1>/g)){ let a=[]; for(const p of m[2].matchAll(/<gml:posList[^>]*>([^<]+)<\/gml:posList>/g)) a=a.concat(p[1].trim().split(/\s+/).map(Number)); if(a.length>=6) rings.push(toZ0(a)); }
    if(rings.length) polys.push(rings); }
  return polys; }
function featBB(polys){ let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; for(const r of polys) { const e=r[0]; for(let j=0;j<e.length;j+=2){ const x=e[j],y=e[j+1]; if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } } return [x0,y0,x1,y1]; }
function parseAtkis(tx){ const out=[];
  for(const ch of tx.split("<wfs:member>")){ const m=/<(AX_[A-Za-z]+) gml:id="([^"]+)"/.exec(ch); if(!m) continue;
    const vmm=/<vegetationsmerkmal>(\d+)/.exec(ch), vm=vmm?+vmm[1]:0, polys=parsePolys(ch); if(!polys.length) continue;
    const sub=atkisSub(m[1],vm); const name=m[1]==="AX_Landwirtschaft"?(LW_NAME[vm]||"Landwirtschaft"):m[1]==="AX_Wald"?SUB[sub].n:(ATKIS_NAME[m[1]]||m[1].slice(3));
    out.push({id:"a:"+m[2],src:"a",sub,polys,bb:featBB(polys),name}); }
  return out; }
function parseGsa(tx){ const out=[];
  for(const ch of tx.split("<wfs:member>")){ const m=/gml:id="([^"]+)"/.exec(ch); const d=/<gml:description>([^<]*)<\/gml:description>/.exec(ch); if(!m||!d) continue;
    const code=parseInt(d[1],10), crop=d[1].replace(/^\s*\d+\s*-\s*/,"").trim(), mcm=/CropValue\/([A-Z]+)/.exec(ch), mc=mcm?mcm[1]:"";
    const sub=gsaSub(code,mc,crop); if(!sub) continue; const polys=parsePolys(ch); if(!polys.length) continue;
    const ha=/declaredArea[^>]*>([\d.]+)/.exec(ch), vf=/<gsaa:validFrom>(\d{4})/.exec(ch);
    out.push({id:"i:"+m[1],src:"i",sub,polys,bb:featBB(polys),crop,code,ha:ha?+ha[1]:null,since:vf?+vf[1]:null}); }
  return out; }
function bboxXml(x0,y0,x1,y1){ return TN_TYPES.map(t=>`<wfs:Query typeNames="adv:${t}"><fes:Filter><fes:BBOX><fes:ValueReference>adv:position</fes:ValueReference><gml:Envelope srsName="urn:ogc:def:crs:EPSG::25832"><gml:lowerCorner>${x0} ${y0}</gml:lowerCorner><gml:upperCorner>${x1} ${y1}</gml:upperCorner></gml:Envelope></fes:BBOX></fes:Filter></wfs:Query>`).join(""); }
async function wfsGet(src,x0,y0,x1,y1,ms){
  const ctl=new AbortController(), to=setTimeout(()=>ctl.abort(),ms||40000);
  try{ let r;
    if(src==="a") r=await fetch(ATKIS_URL,{method:"POST",signal:ctl.signal,headers:{"Content-Type":"text/xml"},body:`<?xml version="1.0" encoding="UTF-8"?><wfs:GetFeature service="WFS" version="2.0.0" count="30000" xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:adv="http://www.adv-online.de/namespaces/adv/gid/7.1">${bboxXml(x0,y0,x1,y1)}</wfs:GetFeature>`});
    else r=await fetch(`${GSA_URL}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=gsaa:AgriculturalParcel&COUNT=30000&BBOX=${x0},${y0},${x1},${y1},urn:ogc:def:crs:EPSG::25832`,{signal:ctl.signal});
    if(!r.ok) throw new Error("HTTP "+r.status);
    const tx=await r.text(); if(/ExceptionReport/.test(tx.slice(0,800))) throw new Error("Dienstfehler");
    return src==="a"?parseAtkis(tx):parseGsa(tx);
  } catch(e){ if(e.name==="AbortError") throw new Error("Zeitüberschreitung"); throw e; } finally{ clearTimeout(to); } }
function vecWanted(){ return (S.luLayer||S.luMask) && map.getZoom()>=VEC_Z && !vecDead && !inArtifact(); }
function vecNeed(){ const b=map.getBounds().pad(0.05); const P=[b.getSouthWest(),b.getNorthEast(),b.getNorthWest(),b.getSouthEast()].map(p=>latLngToUtm(p.lat,p.lng));
  const E=P.map(p=>p[0]), N=P.map(p=>p[1]), out=[];
  for(let ix=Math.floor(Math.min(...E)/TILE); ix<=Math.floor(Math.max(...E)/TILE); ix++) for(let iy=Math.floor(Math.min(...N)/TILE); iy<=Math.floor(Math.max(...N)/TILE); iy++) out.push(ix+"_"+iy);
  return out; }
function vecAdd(s,k,fs){ const ids=[]; for(const f of fs){ const ex=VF.get(f.id); if(ex) ex.n++; else { f.n=1; VF.set(f.id,f); } ids.push(f.id); } VT[s].set(k,{st:"ok",ids}); }
function vecDrop(s,k){ const t=VT[s].get(k); if(t&&t.ids) for(const id of t.ids){ const f=VF.get(id); if(f&&--f.n<=0) VF.delete(id); } VT[s].delete(k); }
function vecUpdate(){
  if(!vecWanted()){ vecQ=[]; luvSoon(); return; }
  const need=vecNeed(); if(need.length>40){ luvSoon(); return; }
  const want=[]; for(const k of need){ want.push("a:"+k); if(map.getZoom()>=INV_Z) want.push("i:"+k); }
  const ws=new Set(want);
  vecQ=vecQ.filter(w=>{ if(ws.has(w)) return true; const [s,k]=w.split(":"); const t=VT[s].get(k); if(t&&t.st==="wait") VT[s].delete(k); return false; });
  for(const w of want){ const [s,k]=w.split(":"), t=VT[s].get(k); if(!t||(t.st==="err"&&Date.now()-t.t>60000)){ VT[s].set(k,{st:"wait"}); vecQ.push(w); } }
  vecQ.sort((p,q)=>(p[0]==="a"?0:1)-(q[0]==="a"?0:1));
  const ns=new Set(need); for(const s of ["a","i"]) if(VT[s].size>36) for(const [k,t] of [...VT[s]]) if(!ns.has(k)&&t.st==="ok") vecDrop(s,k);
  vecPump(); luvSoon(); }
function vecPump(){
  while(vecRun<4 && vecQ.length){ const w=vecQ.shift(), [s,k]=w.split(":"), t=VT[s].get(k); if(!t||t.st!=="wait") continue;
    t.st="load"; vecRun++; const [ix,iy]=k.split("_").map(Number);
    wfsGet(s,ix*TILE,iy*TILE,(ix+1)*TILE,(iy+1)*TILE).then(fs=>{ vecAdd(s,k,fs); vecOk++; })
      .catch(e=>{ VT[s].set(k,{st:"err",t:Date.now(),e:String(e&&e.message||e)}); vecFail++; if(!vecOk&&vecFail>=3) vecDead=true; })
      .finally(()=>{ vecRun--; luvSoon(); vecPump(); }); } }
function vecState(){ const need=vecNeed(), z=map.getZoom(); let a=0,ao=0,ae=0,i=0,io=0; for(const k of need){ const t=VT.a.get(k); a++; if(t&&t.st==="ok") ao++; if(t&&t.st==="err") ae++; if(z>=INV_Z){ const u=VT.i.get(k); i++; if(u&&(u.st==="ok"||u.st==="err")) io++; } }
  return {n:need.length,a,ao,ae,i,io,complete:need.length<=40 && ao>0 && ao+ae===a}; }
function luvShown(){ return vecWanted() && vecState().complete; }
let luvT=null; function luvSoon(){ clearTimeout(luvT); luvT=setTimeout(()=>{ luvSync(); luvLayer.redraw(); luStatus(); },100); }
function luvSync(){ const sh=luvShown(); if(luOverlay){ const el=luOverlay.getElement(); if(el) el.style.display=sh?"none":""; } }
const LuVec=L.Layer.extend({
  onAdd(m){ this._c=L.DomUtil.create("canvas","luvec leaflet-zoom-hide"); Object.assign(this._c.style,{position:"absolute",pointerEvents:"none"}); m.getPane("luPane").appendChild(this._c); m.on("moveend",this._reset,this); this._reset(); },
  onRemove(m){ L.DomUtil.remove(this._c); m.off("moveend",this._reset,this); },
  _reset(){ const m=this._map, s=m.getSize(), P=0.25, W=Math.round(s.x*(1+2*P)), H=Math.round(s.y*(1+2*P)), dpr=Math.min(2,window.devicePixelRatio||1);
    this._tl=m.containerPointToLayerPoint([-Math.round(s.x*P),-Math.round(s.y*P)]); this._W=W; this._H=H; this._dpr=dpr;
    const c=this._c; c.width=Math.round(W*dpr); c.height=Math.round(H*dpr); c.style.width=W+"px"; c.style.height=H+"px"; L.DomUtil.setPosition(c,this._tl); this.redraw(); },
  redraw(){ if(this._map) luvDraw(this); } });
function luvDraw(Ly){
  const c=Ly._c, x=c.getContext("2d"); x.setTransform(Ly._dpr,0,0,Ly._dpr,0,0); x.clearRect(0,0,Ly._W,Ly._H); LUVIS=[];
  const show=luvShown(); c.style.display=show?"":"none"; if(!show){ luSharesSoon(); return; }
  const z=map.getZoom(), k=Math.pow(2,z), po=map.getPixelOrigin(), ox=po.x+Ly._tl.x, oy=po.y+Ly._tl.y, vb=[ox/k,oy/k,(ox+Ly._W)/k,(oy+Ly._H)/k], surf=css("--surface-0")||"#f6f5f1";
  for(const pass of ["a","i"]){ if(pass==="i"&&z<INV_Z) continue;
    for(const f of VF.values()){ if(f.src!==pass) continue; const b=f.bb; if(b[2]<vb[0]||b[0]>vb[2]||b[3]<vb[1]||b[1]>vb[3]) continue; LUVIS.push(f);
      x.beginPath();
      for(const poly of f.polys) for(const r of poly){ let lx=0,ly=0; const n=r.length;
        for(let j=0;j<n;j+=2){ const X=r[j]*k-ox, Y=r[j+1]*k-oy; if(j===0){ x.moveTo(X,Y); lx=X; ly=Y; } else if(Math.abs(X-lx)+Math.abs(Y-ly)>0.7||j===n-2){ x.lineTo(X,Y); lx=X; ly=Y; } }
        x.closePath(); }
      if(pass==="i"){ x.globalCompositeOperation="destination-out"; x.globalAlpha=1; x.fillStyle="#000"; x.fill("evenodd"); x.globalCompositeOperation="source-over"; }
      const on=S.lu.has(f.sub);
      if(S.luMask&&!on){ x.globalAlpha=0.86; x.fillStyle=surf; x.fill("evenodd"); }
      else if(S.luLayer&&on){ x.globalAlpha=S.luMask?0.35:(S.soil?0.62:0.95); x.fillStyle=SUB[f.sub].col; x.fill("evenodd"); }
      if(pass==="i"&&z>=15&&(S.luLayer||(S.luMask&&on))){ x.globalAlpha=0.45; x.lineWidth=0.8; x.strokeStyle="#333"; x.stroke(); } } }
  x.globalAlpha=1; luSharesSoon(); }
const luvLayer=new LuVec(); map.whenReady(()=>luvLayer.addTo(map));
function pipZ0(f,px,py){ for(const poly of f.polys){ let ins=false; for(const r of poly){ for(let i=0,j=r.length-2;i<r.length;j=i,i+=2){ const yi=r[i+1], yj=r[j+1]; if((yi>py)!==(yj>py) && px<(r[j]-r[i])*(py-yi)/(yj-yi)+r[i]) ins=!ins; } } if(ins) return true; } return false; }
function z0Of(ll){ const s=Math.sin(ll.lat*Math.PI/180); return [256*(0.5+ll.lng/360), 256*(0.5-Math.log((1+s)/(1-s))/(4*Math.PI))]; }
function vecAt(ll,src,list){ const [px,py]=z0Of(ll); for(const f of (list||VF.values())){ if(f.src!==src) continue; const b=f.bb; if(px<b[0]||px>b[2]||py<b[1]||py>b[3]) continue; if(pipZ0(f,px,py)) return f; } return null; }
function vecText(a,i){
  if(i){ const nm=SUB[i.sub].n, extra=(["ak","sk","gs","sw"].includes(i.sub)&&i.crop)?` (${i.crop})`:""; return `${nm}${extra}, Schlag ${i.ha!=null?fmt(i.ha,2)+" ha":"ohne Flächenangabe"} · Agrarantrag`; }
  if(a) return `${a.name} · ATKIS`; return null; }
async function luPointInfo(ll){
  if(map.getZoom()<VEC_Z||vecDead||inArtifact()) return null;
  const [E,N]=latLngToUtm(ll.lat,ll.lng), k=Math.floor(E/TILE)+"_"+Math.floor(N/TILE);
  const ta=VT.a.get(k), ti=VT.i.get(k);
  let a=(ta&&ta.st==="ok")?vecAt(ll,"a"):undefined, i=(ti&&ti.st==="ok")?vecAt(ll,"i"):undefined;
  try{
    if(a===undefined){ const fs=await wfsGet("a",E-1,N-1,E+1,N+1,15000); a=vecAt(ll,"a",fs); }
    if(i===undefined && (!a||["ak","sk","gs"].includes(a.sub))){ const fs=await wfsGet("i",E-1,N-1,E+1,N+1,15000); i=vecAt(ll,"i",fs); }
  }catch(e){ return a||i?{text:vecText(a,i)}:null; }
  const t=vecText(a,i); return t?{text:t, sub:(i||a).sub}:null; }

// Anteile der Nutzungen im Ausschnitt (Stichprobenraster)
let lsT=null; function luSharesSoon(){ clearTimeout(lsT); lsT=setTimeout(luShares,250); }
function luShares(){
  const pn=$("luPanel"); if(!pn||pn.hidden) return;
  const sz=map.getSize(), nx=64, ny=Math.max(16,Math.round(64*sz.y/Math.max(1,sz.x))), sx=sz.x/nx, sy=sz.y/ny, cnt={}; let tot=0, basis="";
  if(luvShown()){ const k=Math.pow(2,map.getZoom()), pb=map.getPixelBounds(), grid=new Array(nx*ny).fill(null), pri=new Uint8Array(nx*ny);
    for(const f of LUVIS){ const p=f.src==="i"?2:1;
      const i0=Math.max(0,Math.ceil((f.bb[0]*k-pb.min.x)/sx-0.5)), i1=Math.min(nx-1,Math.floor((f.bb[2]*k-pb.min.x)/sx-0.5));
      const j0=Math.max(0,Math.ceil((f.bb[1]*k-pb.min.y)/sy-0.5)), j1=Math.min(ny-1,Math.floor((f.bb[3]*k-pb.min.y)/sy-0.5));
      for(let j=j0;j<=j1;j++) for(let i=i0;i<=i1;i++){ const id=j*nx+i; if(pri[id]>=p) continue; if(pipZ0(f,(pb.min.x+(i+0.5)*sx)/k,(pb.min.y+(j+0.5)*sy)/k)){ grid[id]=f.sub; pri[id]=p; } } }
    for(const g of grid) if(g){ cnt[g]=(cnt[g]||0)+1; tot++; }
    basis=map.getZoom()>=INV_Z?"amtlich (ATKIS, Agrarantrag)":"amtlich (ATKIS)";
  } else if(LUD){ for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const r=rasterAt(LUD,map.containerPointToLatLng([(i+0.5)*sx,(j+0.5)*sy])); if(r===null) continue; const v=LUD.d[r]; if(!v||!LUN[v]) continue; const s=v===3?"gs":v===6?"wm":LUN[v].s[0]; cnt[s]=(cnt[s]||0)+1; tot++; }
    basis="CORINE 2021, grob"; }
  const pc=n=>!tot?"":(n===0?"–":(n/tot<0.005?"<1 %":Math.round(n/tot*100)+" %"));
  for(const G of LUG){ let gs=0; for(const [id] of G.subs){ const n=cnt[id]||0; gs+=n; const el=$("pc_"+id); if(el) el.textContent=pc(n); } const el=$("pc_"+G.g); if(el) el.textContent=pc(gs); }
  if($("luBasis")) $("luBasis").textContent=tot?"Anteil im Ausschnitt, "+basis:"Anteil im Ausschnitt"; }
function luStatus(){
  const el=$("luSrc"); if(!el) return; const z=map.getZoom(); let t;
  if(!(S.luLayer||S.luMask)) t="Zum Einblenden „Nutzung einfärben“ oder „Boden nur auf gewählter Nutzung“ anhaken.";
  else if(inArtifact()) t="In der Claude-Artifact-Ansicht sind die amtlichen Nutzungsdaten gesperrt. Angezeigt wird CORINE 2021 (grob). Die Online-Fassung lädt die genauen Flächen.";
  else if(vecDead) t="Die amtlichen Nutzungsdienste sind gerade nicht erreichbar (offline, Datei vom Rechner oder Dienststörung). Angezeigt wird CORINE 2021 (grob). Seite neu laden für einen neuen Versuch.";
  else if(z<VEC_Z) t=`Jetzt: CORINE 2021, grob (Flächen ab 5 ha, Raster 85 m). Ab Zoomstufe ${VEC_Z} erscheinen die amtlichen Flächen der Tatsächlichen Nutzung, ab ${INV_Z} zusätzlich die Feldstücke aus dem Agrarantrag mit Wiese, Mähweide, Weide und Ackerfrucht.`;
  else { const st=vecState();
    if(st.n>40) t="Ausschnitt zu groß für die amtlichen Flächen; etwas näher heranzoomen.";
    else if(!st.complete) t=`Lade amtliche Nutzung … ${st.ao} von ${st.a} Kacheln. Bis dahin CORINE (grob).`;
    else { t="Jetzt: amtliche Flächen, ATKIS Basis-DLM (Bayerische Vermessungsverwaltung)";
      t+= z>=INV_Z ? `, darüber die Feldstücke aus dem Agrarantrag (StMELF)${st.io<st.i?` (lädt noch ${st.i-st.io} von ${st.i})`:""}.` : `. Für Wiese, Mähweide und Weide auf Zoomstufe ${INV_Z} gehen.`;
      if(st.ae) t+=` ${st.ae} Kachel(n) nicht geladen, dort fehlen Flächen.`; } }
  el.textContent=t; }
map.on("moveend",()=>{ vecUpdate(); luStatus(); luSharesSoon(); soilHintSoon(); });

// Hinweis, wenn keine gewählte Bodenkategorie im Ausschnitt liegt
let shT=null; function soilHintSoon(){ clearTimeout(shT); shT=setTimeout(soilHint,250); }
function soilHint(){
  const el=$("emptyHint"); if(!el||!D) return; const ids=[...S.sel.map(x=>"Klasse "+x),...S.units.map(u=>"Einheit "+u)];
  if(!ids.length||!S.soil){ el.style.display="none"; return; }
  const b=map.getBounds(), z=map.getZoom(); let hit=false;
  const test=arr=>{ for(const l of arr){ if(l.ki==null) continue; if(keyCats(l.ki).length && b.intersects(l.getBounds())) return true; } return false; };
  hit = test(z<OV_Z||!genBuilt?ovLayers:layers) || (detailActive()&&test(detLayers()));
  if(!hit && S.mode==="zuordnung") for(const [k,la,lo] of D.small){ if(S.sel.includes(k)&&b.contains([la,lo])){ hit=true; break; } }
  el.textContent=`Im Ausschnitt liegt keine Fläche der gewählten Kategorien (${ids.join(", ")}). Herauszoomen oder andere Kategorien wählen.`;
  el.style.display=hit?"none":"block"; }
