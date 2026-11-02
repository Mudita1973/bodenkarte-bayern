// ---------------- Genaue Nutzung: ZABAGED-Kacheln (statisch) und LPIS-Feldblöcke (online) ----------------
const VEC_Z=13, INV_Z=14, TILE=4000;
const LU_TILE_URL="lu/";
const LPIS_URL="https://mze.gov.cz/public/app/wms/plpis_wfs.fcgi";
const LU_IDX=new Set((typeof LU_INDEX!=="undefined"&&LU_INDEX)?LU_INDEX:[]);
const ZB={138:["ak","Ackerland und sonstige Flächen"],135:["sk","Obstgarten, Garten"],136:["sk","Weinberg"],137:["sk","Hopfenfeld"],
  139:["gs","Dauergrünland"],142:["wm","Wald"],140:["wg","Wald mit Buschbestand"],141:["wg","Latschenkiefern (Krummholz)"],
  131:["om","Sumpf, Morast"],18:["om","Torfmoor"],130:["of","Felsen"],129:["of","Rutschung, Schutt"],132:["sw","Wasserfläche"],
  114:["ss","Betriebs- und Zweckbebauung"],115:["ss","sonstige Fläche in Siedlungen"],116:["ss","Friedhof"],117:["ss","Deponie"],118:["ss","Tagebau, Steinbruch"],
  119:["ss","Lagerplatz"],121:["ss","Bahnhofsgelände"],122:["ss","Gleisanlage"],123:["ss","Parkplatz, Rastplatz"],124:["ss","Start- und Landebahn"],
  125:["ss","Flugplatz"],126:["ss","Kraftwerk"],127:["ss","Umspannwerk"],134:["ss","gepflegtes Grün (Park, Sportfläche)"],99:["ss","bebaute Fläche (Gebäude)"]};
const LPIS_DE={"standardní orná půda":"Ackerland","trvalý travní porost":"Dauergrünland","travní porost (na orné půdě)":"Ackergras","úhor":"Brache",
  "ovocný sad":"Obstanlage","chmelnice":"Hopfen","vinice":"Weinberg","školka":"Baumschule","zalesněná půda":"aufgeforstete Fläche",
  "rychle rostoucí dřeviny":"schnellwachsende Gehölze","jiná trvalá kultura":"andere Dauerkultur","rybník":"Teich","mimoprodukční plocha":"nicht produktive Fläche",
  "zelinářská půda":"Gemüsebau","krajinotvorný sad":"Landschaftsobstgarten","trvalý travní porost (TTP)":"Dauergrünland"};
const VF=new Map(), VT={a:new Map(),i:new Map()}, vecCtl=new Map(); let vecQ=[], vecRun=0, vecRunI=0, vecOk=0, vecFail=0, vecDead=false, LUVIS=[], REG=null;
function regRings(){ if(!REG) REG=(D.region||[]).map(r=>toZ0(r)); return REG; }
function regPath(x,k,ox,oy){ x.beginPath(); for(const r of regRings()){ for(let j=0;j<r.length;j+=2){ const X=r[j]*k-ox, Y=r[j+1]*k-oy; if(j===0) x.moveTo(X,Y); else x.lineTo(X,Y); } x.closePath(); } }
function lpisSub(k){ k=(k||"").toLowerCase();
  if(/trvalý travní/.test(k)) return "gs";
  if(/orná|úhor|na orné|víceletými produkčními/.test(k)) return "ak";
  if(/chmel|vinic|sad|školk|trvalá kultura|rychle rostoucí|zelin/.test(k)) return "sk";
  if(/zalesn/.test(k)) return "wg"; if(/rybník|vodní/.test(k)) return "sw";
  return null; }
function toZ0(arr){ const o=new Float64Array(arr.length); for(let j=0;j<arr.length;j+=2){ const [la,lo]=utmToLatLng(arr[j],arr[j+1]); const s=Math.sin(la*Math.PI/180); o[j]=256*(0.5+lo/360); o[j+1]=256*(0.5-Math.log((1+s)/(1-s))/(4*Math.PI)); } return o; }
function llZ0(arr){ const o=new Float64Array(arr.length); for(let j=0;j<arr.length;j+=2){ const la=arr[j], lo=arr[j+1], s=Math.sin(la*Math.PI/180); o[j]=256*(0.5+lo/360); o[j+1]=256*(0.5-Math.log((1+s)/(1-s))/(4*Math.PI)); } return o; }
function featBB(polys){ let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; for(const r of polys) { const e=r[0]; for(let j=0;j<e.length;j+=2){ const x=e[j],y=e[j+1]; if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } } return [x0,y0,x1,y1]; }
function zbDecode(u,k){ let p=0;
  const rd=()=>{ let r=0,s=1,b; do{ b=u[p++]; r+=(b&127)*s; s*=128; }while(b&128); return r; };
  const zd=()=>{ const v=rd(); return v%2 ? -(v+1)/2 : v/2; };
  const [ix,iy]=k.split("_").map(Number), x0=ix*TILE, y0=iy*TILE, n=rd(), out=[];
  for(let f=0;f<n;f++){ const l=rd(), np=rd(), polys=[];
    for(let q=0;q<np;q++){ const nr=rd(), rings=[];
      for(let r=0;r<nr;r++){ const m=rd(), a=new Float64Array(m*2); let x=x0,y=y0; for(let i=0;i<m;i++){ x+=zd(); y+=zd(); a[2*i]=x; a[2*i+1]=y; } rings.push(toZ0(a)); }
      polys.push(rings); }
    const z=ZB[l]||["ss","Fläche ("+l+")"]; out.push({id:"a:"+k+":"+f,src:"a",sub:z[0],polys,bb:featBB(polys),name:z[1],top:l===99}); }
  return out; }
const zbCache=new Map();
async function zbGet(k){
  if(!LU_IDX.has(k)) return [];
  if(zbCache.has(k)) return zbCache.get(k);
  let u;
  if(typeof LUT!=="undefined"&&LUT){ const b=LUT[k]; if(!b) return []; const s=atob(b); u=new Uint8Array(s.length); for(let i=0;i<s.length;i++) u[i]=s.charCodeAt(i); }
  else { const r=await fetch(LU_TILE_URL+k+".bin"); if(!r.ok) throw new Error("HTTP "+r.status); u=new Uint8Array(await r.arrayBuffer()); }
  const fs=zbDecode(u,k); if(zbCache.size>60) zbCache.delete(zbCache.keys().next().value); zbCache.set(k,fs); return fs; }
function parseLpis(tx){ const out=[];
  for(const ch of tx.split("<wfs:member>").slice(1)){ const m=/gml:id="([^"]+)"/.exec(ch); if(!m) continue;
    const ku=/<ms:kultura>([^<]*)<\/ms:kultura>/.exec(ch), kult=ku?ku[1].trim():"", sub=lpisSub(kult); if(!sub) continue;
    const polys=[];
    for(const pc of ch.split(/<gml:Polygon[\s>]/).slice(1)){ const rings=[];
      for(const r of pc.matchAll(/<gml:(exterior|interior)>([\s\S]*?)<\/gml:\1>/g)){ let a=[]; for(const q of r[2].matchAll(/<gml:posList[^>]*>([^<]+)<\/gml:posList>/g)) a=a.concat(q[1].trim().split(/\s+/).map(Number)); if(a.length>=6) rings.push(llZ0(a)); }
      if(rings.length) polys.push(rings); }
    if(!polys.length) continue;
    const vy=/<ms:vymera>\s*([\d.,]+)/.exec(ch);
    out.push({id:"i:"+m[1],src:"i",sub,polys,bb:featBB(polys),crop:LPIS_DE[kult]||kult,ha:vy?+vy[1].replace(",","."):null}); }
  return out; }
async function wfsGet(src,x0,y0,x1,y1,ms,sig){
  if(src==="a") return zbGet(Math.floor(x0/TILE)+"_"+Math.floor(y0/TILE));
  const P=[[x0,y0],[x1,y0],[x0,y1],[x1,y1]].map(p=>utmToLatLng(p[0],p[1])), la=P.map(p=>p[0]), lo=P.map(p=>p[1]);
  const bb=[Math.min(...la),Math.min(...lo),Math.max(...la),Math.max(...lo)].map(v=>v.toFixed(6)).join(",");
  const ctl=new AbortController(), to=setTimeout(()=>ctl.abort(),ms||40000); if(sig) sig.addEventListener("abort",()=>ctl.abort());
  try{
    // Nur Geometrie, Kultur und Fläche abfragen: Namen und Adressen der Bewirtschafter werden gar nicht erst übertragen.
    const r=await fetch(`${LPIS_URL}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=ms:LPIS_DPB_UCINNE&COUNT=30000&PROPERTYNAME=ms:GEOMETRY,ms:kultura,ms:vymera&SRSNAME=urn:ogc:def:crs:EPSG::4326&BBOX=${bb},urn:ogc:def:crs:EPSG::4326`,{signal:ctl.signal});
    if(!r.ok) throw new Error("HTTP "+r.status);
    const tx=await r.text(); if(/ExceptionReport/.test(tx.slice(0,800))) throw new Error("Dienstfehler");
    return parseLpis(tx);
  } catch(e){ if(e.name==="AbortError") throw new Error("Zeitüberschreitung"); throw e; } finally{ clearTimeout(to); } }
function vecWanted(){ return (S.luLayer||S.luMask) && map.getZoom()>=VEC_Z && !vecDead && !inArtifact(); }
function vecNeed(){ const b=map.getBounds().pad(0.05); const P=[b.getSouthWest(),b.getNorthEast(),b.getNorthWest(),b.getSouthEast()].map(p=>latLngToUtm(p.lat,p.lng));
  const E=P.map(p=>p[0]), N=P.map(p=>p[1]), out=[];
  for(let ix=Math.floor(Math.min(...E)/TILE); ix<=Math.floor(Math.max(...E)/TILE); ix++) for(let iy=Math.floor(Math.min(...N)/TILE); iy<=Math.floor(Math.max(...N)/TILE); iy++){ const k=ix+"_"+iy; if(LU_IDX.has(k)) out.push(k); }
  return out; }
function vecAdd(s,k,fs){ const ids=[]; for(const f of fs){ const ex=VF.get(f.id); if(ex) ex.n++; else { f.n=1; VF.set(f.id,f); } ids.push(f.id); } VT[s].set(k,{st:"ok",ids}); }
function vecDrop(s,k){ const t=VT[s].get(k); if(t&&t.ids) for(const id of t.ids){ const f=VF.get(id); if(f&&--f.n<=0) VF.delete(id); } VT[s].delete(k); }
function vecUpdate(){
  if(!vecWanted()){ vecQ=[]; for(const s of ["a","i"]) for(const [k,x] of [...VT[s]]) if(x.st==="wait"||(s==="i"&&x.st==="load")) VT[s].delete(k); for(const c of vecCtl.values()) c.abort(); vecCtl.clear(); luvSoon(); return; }
  const need=vecNeed(); if(need.length>40){ luvSoon(); return; }
  const want=[]; for(const k of need){ want.push("a:"+k); if(map.getZoom()>=INV_Z) want.push("i:"+k); }
  const ws=new Set(want);
  vecQ=vecQ.filter(w=>{ if(ws.has(w)) return true; const [s,k]=w.split(":"); const t=VT[s].get(k); if(t&&t.st==="wait") VT[s].delete(k); return false; });
  for(const [w,c] of [...vecCtl]) if(!ws.has(w)){ c.abort(); vecCtl.delete(w); VT.i.delete(w.split(":")[1]); }
  const inQ=new Set(vecQ); for(const w of want){ const [s,k]=w.split(":"), t=VT[s].get(k); if(!t||(t.st==="err"&&Date.now()-t.t>60000)||(t.st==="wait"&&!inQ.has(w))){ VT[s].set(k,{st:"wait"}); vecQ.push(w); } }
  vecQ.sort((p,q)=>(p[0]==="a"?0:1)-(q[0]==="a"?0:1));
  const ns=new Set(need); for(const s of ["a","i"]) if(VT[s].size>36) for(const [k,t] of [...VT[s]]) if(!ns.has(k)&&t.st==="ok") vecDrop(s,k);
  vecPump(); luvSoon(); }
function vecPump(){
  // ZABAGED-Kacheln sind statisch und schnell: ohne Platzbegrenzung. LPIS ist live und langsam: höchstens 4 gleichzeitig, veraltete Anfragen werden abgebrochen.
  for(let n=0;n<vecQ.length;){ const w=vecQ[n], [s,k]=w.split(":"), t=VT[s].get(k);
    if(!t||t.st!=="wait"){ vecQ.splice(n,1); continue; }
    if(s==="i"&&vecRunI>=4){ n++; continue; }
    vecQ.splice(n,1); t.st="load"; vecRun++; if(s==="i") vecRunI++;
    const ctl=new AbortController(); if(s==="i") vecCtl.set(w,ctl);
    const [ix,iy]=k.split("_").map(Number);
    wfsGet(s,ix*TILE,iy*TILE,(ix+1)*TILE,(iy+1)*TILE,0,ctl.signal).then(fs=>{ if(VT[s].get(k)!==t) return; vecAdd(s,k,fs); if(s==="a") vecOk++; })
      .catch(e=>{ if(VT[s].get(k)!==t) return; VT[s].set(k,{st:"err",t:Date.now(),e:String(e&&e.message||e)}); if(s==="a"){ vecFail++; if(!vecOk&&vecFail>=3) vecDead=true; } })
      .finally(()=>{ vecRun--; if(s==="i"){ vecRunI--; if(vecCtl.get(w)===ctl) vecCtl.delete(w); } luvSoon(); vecPump(); }); } }
function vecState(){ const need=vecNeed(), z=map.getZoom(); let a=0,ao=0,ae=0,i=0,io=0,ie=0; for(const k of need){ const t=VT.a.get(k); a++; if(t&&t.st==="ok") ao++; if(t&&t.st==="err") ae++; if(z>=INV_Z){ const u=VT.i.get(k); i++; if(u&&(u.st==="ok"||u.st==="err")) io++; if(u&&u.st==="err") ie++; } }
  return {n:need.length,a,ao,ae,i,io,ie,complete:need.length<=40 && ao>0 && ao+ae===a}; }
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
  const cut=()=>{ x.globalCompositeOperation="destination-out"; x.globalAlpha=1; x.fillStyle="#000"; x.fill("evenodd"); x.globalCompositeOperation="source-over"; };
  // Alles wird auf das Kartengebiet (drei Kraje) beschnitten, damit nichts über Bayern oder Nachbarkreisen liegt.
  // Straßen und Gebäudeblöcke wurden aus ZABAGED nicht übernommen. Für „Boden nur auf gewählter Nutzung“ wird deshalb erst das ganze Gebiet abgedeckt
  // und nur die gewählten Nutzungen werden wieder freigestellt; Lücken bleiben abgedeckt.
  x.save(); if(regRings().length){ regPath(x,k,ox,oy); x.clip("evenodd"); }
  if(S.luMask){ x.globalAlpha=0.86; x.fillStyle=surf; x.fillRect(0,0,Ly._W,Ly._H); }
  for(const pass of ["a","i"]){ if(pass==="i"&&z<INV_Z) continue;
    for(const f of VF.values()){ if(f.src!==pass) continue; const b=f.bb; if(b[2]<vb[0]||b[0]>vb[2]||b[3]<vb[1]||b[1]>vb[3]) continue; LUVIS.push(f);
      x.beginPath();
      for(const poly of f.polys) for(const r of poly){ let lx=0,ly=0; const n=r.length;
        for(let j=0;j<n;j+=2){ const X=r[j]*k-ox, Y=r[j+1]*k-oy; if(j===0){ x.moveTo(X,Y); lx=X; ly=Y; } else if(Math.abs(X-lx)+Math.abs(Y-ly)>0.7||j===n-2){ x.lineTo(X,Y); lx=X; ly=Y; } }
        x.closePath(); }
      const on=S.lu.has(f.sub);
      if(pass==="i"){ cut(); if(S.luMask&&!on){ x.globalAlpha=0.86; x.fillStyle=surf; x.fill("evenodd"); } }
      else if(S.luMask&&on) cut();
      else if(S.luMask&&f.top){ x.globalAlpha=0.86; x.fillStyle=surf; x.fill("evenodd"); }
      if(S.luLayer&&on){ x.globalAlpha=S.luMask?0.35:(S.soil?0.62:0.95); x.fillStyle=SUB[f.sub].col; x.fill("evenodd"); }
      if(pass==="i"&&z>=15&&(S.luLayer||(S.luMask&&on))){ x.globalAlpha=0.45; x.lineWidth=0.8; x.strokeStyle="#333"; x.stroke(); } } }
  x.restore(); x.globalAlpha=1; luSharesSoon(); }
const luvLayer=new LuVec(); map.whenReady(()=>luvLayer.addTo(map));
function pipZ0(f,px,py){ for(const poly of f.polys){ let ins=false; for(const r of poly){ for(let i=0,j=r.length-2;i<r.length;j=i,i+=2){ const yi=r[i+1], yj=r[j+1]; if((yi>py)!==(yj>py) && px<(r[j]-r[i])*(py-yi)/(yj-yi)+r[i]) ins=!ins; } } if(ins) return true; } return false; }
function z0Of(ll){ const s=Math.sin(ll.lat*Math.PI/180); return [256*(0.5+ll.lng/360), 256*(0.5-Math.log((1+s)/(1-s))/(4*Math.PI))]; }
function vecAt(ll,src,list){ const [px,py]=z0Of(ll); let hit=null; for(const f of (list||VF.values())){ if(f.src!==src) continue; const b=f.bb; if(px<b[0]||px>b[2]||py<b[1]||py>b[3]) continue; if(pipZ0(f,px,py)){ if(f.top) return f; if(!hit) hit=f; } } return hit; }
function vecText(a,i){
  if(i){ const nm=SUB[i.sub].n, extra=i.crop&&i.crop!==nm?` (${i.crop})`:""; return `${nm}${extra}, Feldblock ${i.ha!=null?fmt(i.ha,2)+" ha":"ohne Flächenangabe"} · LPIS`; }
  if(a) return `${a.name} · ZABAGED`; return null; }
async function luPointInfo(ll){
  if(map.getZoom()<VEC_Z||vecDead||inArtifact()) return null;
  const [E,N]=latLngToUtm(ll.lat,ll.lng), k=Math.floor(E/TILE)+"_"+Math.floor(N/TILE);
  if(!LU_IDX.has(k)) return null;
  const ta=VT.a.get(k), ti=VT.i.get(k);
  let a=(ta&&ta.st==="ok")?vecAt(ll,"a"):undefined, i=(ti&&ti.st==="ok")?vecAt(ll,"i"):undefined;
  try{
    if(a===undefined){ const fs=await zbGet(k); a=vecAt(ll,"a",fs); }
    if(i===undefined && (!a||["ak","sk","gs"].includes(a.sub))){ const fs=await wfsGet("i",E-1,N-1,E+1,N+1,15000); i=vecAt(ll,"i",fs); }
  }catch(e){ return a||i?{text:vecText(a,i)}:null; }
  const t=vecText(a,i); return t?{text:t, sub:(i||a).sub}:null; }

