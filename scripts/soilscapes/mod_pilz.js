// ---------------- Pilzsuche ----------------
const PZ={
  sauer:{n:"Saure Böden",col:"#8e2c6b",pilze:"Echter Pfifferling, Trompeten-Pfifferling, Maronen-Röhrling, Fichten-Steinpilz, Frauen-Täubling, Kuhmaul",
    regel:"Basensättigung unter 20 % (LfU-Kennwert, Waldwert bevorzugt) und Oberboden kalkfrei (Carbonat unter 0,5 %)"},
  basisch:{n:"Basen- und kalkreiche Böden",col:"#00a3b4",pilze:"Morcheln, Mönchskopf, Blasser und Starkriechender Pfifferling, Schweinsohr, Sommer-Trüffel",
    regel:"Oberboden kalkhaltig (Carbonat ab 0,5 %) oder Basensättigung ab 80 % oder mindestens 50 % basisches Gestein (BAG500)"},
  wasser:{n:"Gute Wasserspeicher",col:"#334199",pilze:"in Trockenphasen die besseren Chancen, etwa Sommer-Steinpilz auf Lösslehm",
    regel:"nutzbare Feldkapazität ab 140 mm (hoch) und Wasserdurchlässigkeit unter 40 cm/Tag"}};
function pzMatch(K,p){ const u=D.units[K.leg]; if(!u||!u.z) return false; const [bs,ca,nfk,kf,s,b]=u.z;
  if(p==="sauer") return (bs!=null&&bs<20&&(ca==null||ca<0.5)) || (bs==null&&s!=null&&s>=50&&(ca==null||ca<0.5));
  if(p==="basisch") return (ca!=null&&ca>=0.5)||(bs!=null&&bs>=80)||(b!=null&&b>=50);
  if(p==="wasser") return nfk!=null&&nfk>=140&&kf!=null&&kf<40;
  return false; }
function pzOf(leg){ const K={leg}; return Object.keys(PZ).filter(p=>pzMatch(K,p)); }
function pzChips(){ const box=$("pzChips"); if(!box) return; box.innerHTML=Object.entries(PZ).map(([k,p])=>`<button class="pzc" data-pz="${k}" aria-pressed="${S.pz.includes(k)}" title="${esc(p.regel)}"><span class="sw" style="background:${p.col}"></span>${p.n}</button>`).join("");
  box.querySelectorAll("[data-pz]").forEach(b=>b.onclick=()=>{ const k=b.dataset.pz; S.pz.includes(k)?removeCat("p:"+k):addCat("p:"+k); pzChips(); }); }

// Hangrichtung aus Höhenkacheln (AWS Terrain Tiles, Terrarium-Kodierung)
const TERR=(z,x,y)=>`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${x}/${y}.png`;
const terrCache=new Map();
function terrTile(z,x,y){ const k=z+"/"+x+"/"+y; if(terrCache.has(k)) return terrCache.get(k);
  const p=new Promise((res,rej)=>{ const im=new Image(); im.crossOrigin="anonymous";
    im.onload=()=>{ try{ const c=document.createElement("canvas"); c.width=c.height=256; const g=c.getContext("2d"); g.drawImage(im,0,0); const d=g.getImageData(0,0,256,256).data, e=new Float32Array(65536); for(let i=0,q=0;i<65536;i++,q+=4) e[i]=d[q]*256+d[q+1]+d[q+2]/256-32768; res(e); }catch(err){ rej(err); } };
    im.onerror=()=>rej(new Error("Höhenkachel nicht erreichbar")); im.src=TERR(z,x,y); });
  terrCache.set(k,p); p.catch(()=>terrCache.delete(k)); if(terrCache.size>300) terrCache.delete(terrCache.keys().next().value); return p; }
const tileLat=(y,z)=>Math.atan(Math.sinh(Math.PI*(1-2*y/Math.pow(2,z))))*180/Math.PI;
const ASP=[["Nordhang","#2f6fbf"],["Osthang","#d6a419"],["Südhang","#d1452b"],["Westhang","#2f9e8f"]];
function aspCls(az){ return az>=315||az<45?0:az<135?1:az<225?2:3; }
function gradAt(e,i,j,px){ const at=(a,b)=>e[Math.min(255,Math.max(0,b))*256+Math.min(255,Math.max(0,a))];
  const gx=((at(i+1,j-1)+2*at(i+1,j)+at(i+1,j+1))-(at(i-1,j-1)+2*at(i-1,j)+at(i-1,j+1)))/(8*px);
  const gs=((at(i-1,j+1)+2*at(i,j+1)+at(i+1,j+1))-(at(i-1,j-1)+2*at(i,j-1)+at(i+1,j-1)))/(8*px);
  const sl=Math.atan(Math.hypot(gx,gs))*180/Math.PI; let az=Math.atan2(-gx,gs)*180/Math.PI; if(az<0) az+=360; return [sl,az]; }
map.createPane("aspPane").style.zIndex=433; map.getPane("aspPane").style.pointerEvents="none";
const AspLayer=L.GridLayer.extend({ createTile(co,done){ const t=document.createElement("canvas"); t.width=t.height=256;
  const zz=Math.min(co.z,15), sc=Math.pow(2,co.z-zz), X=Math.floor(co.x/sc), Y=Math.floor(co.y/sc), n=256/sc, ox=(co.x-X*sc)*n, oy=(co.y-Y*sc)*n;
  terrTile(zz,X,Y).then(e=>{ const lat=tileLat(Y+0.5,zz), px=40075016.686*Math.cos(lat*Math.PI/180)/(256*Math.pow(2,zz));
    const sub=document.createElement("canvas"); sub.width=sub.height=n; const g=sub.getContext("2d"), im=g.createImageData(n,n), o=im.data; const cols=ASP.map(a=>hex(a[1]));
    for(let j=0;j<n;j++) for(let i=0;i<n;i++){ const [sl,az]=gradAt(e,ox+i,oy+j,px); if(sl<5) continue; const c=cols[aspCls(az)], q=(j*n+i)*4; o[q]=c[0];o[q+1]=c[1];o[q+2]=c[2];o[q+3]=Math.round(255*Math.min(0.8,0.25+(sl-5)/20*0.55)); }
    g.putImageData(im,0,0); const tg=t.getContext("2d"); tg.imageSmoothingEnabled=false; tg.drawImage(sub,0,0,256,256); done(null,t); }).catch(err=>done(err,t));
  return t; } });
const aspLayer=new AspLayer({pane:"aspPane",minZoom:11,maxZoom:18,opacity:0.85,attribution:"Hangrichtung: Höhendaten AWS Terrain Tiles (u. a. EU-DEM, SRTM)"});
async function aspectAt(ll){ const z=15, n=Math.pow(2,z), fx=(ll.lng+180)/360*n, s=Math.sin(ll.lat*Math.PI/180), fy=(0.5-Math.log((1+s)/(1-s))/(4*Math.PI))*n;
  const X=Math.floor(fx), Y=Math.floor(fy), i=Math.floor((fx-X)*256), j=Math.floor((fy-Y)*256); const e=await terrTile(z,X,Y);
  const px=40075016.686*Math.cos(ll.lat*Math.PI/180)/(256*n); let ssl=0,sx=0,sy=0,c=0;
  for(let dj=-2;dj<=2;dj++) for(let di=-2;di<=2;di++){ const [sl,az]=gradAt(e,i+di,j+dj,px); ssl+=sl; sx+=Math.sin(az*Math.PI/180); sy+=Math.cos(az*Math.PI/180); c++; }
  let az=Math.atan2(sx,sy)*180/Math.PI; if(az<0) az+=360; return {sl:ssl/c, az, h:e[j*256+i]}; }

// Baumarten (Thünen-Institut, WMS)
const TH_URL="https://atlas.thuenen.de/geoserver/ows";
const TREE={2:["Birke","#d1efe2"],3:["Buche","#49ca45"],4:["Douglasie","#e7ec47"],5:["Eiche","#1a761c"],6:["Erle","#67844d"],8:["Fichte","#cd8673"],9:["Kiefer","#de1317"],10:["Lärche","#df3fea"],14:["Tanne","#ffd54d"],16:["sonstiges Laubholz, langlebig","#25a0ed"],17:["sonstiges Laubholz, kurzlebig","#8ebcd9"]};
const TREE_PILZ={9:"Edel-Reizker und Krause Glucke wachsen nur bei Kiefern",3:"Sommer-Steinpilz mag Buche und Eiche",5:"Sommer-Steinpilz mag Buche und Eiche",8:"Rauchblättriger Schwefelkopf wächst an Nadelholz; junge, dichte Fichtenbestände können viele Pfifferlinge tragen",10:"Rauchblättriger Schwefelkopf wächst an Nadelholz",4:"Rauchblättriger Schwefelkopf wächst an Nadelholz",14:"Rauchblättriger Schwefelkopf wächst an Nadelholz",16:"Igel-Stachelbart wächst an Laubholz",17:"Igel-Stachelbart wächst an Laubholz; Espen-Rotkappe nur bei Zitterpappeln",2:"Igel-Stachelbart wächst an Laubholz",6:"Igel-Stachelbart wächst an Laubholz"};
map.createPane("treePane").style.zIndex=432; map.getPane("treePane").style.pointerEvents="none";
const treeLayer=L.tileLayer.wms(TH_URL,{layers:"geonode:Dominant_Species_Class",format:"image/png",transparent:true,version:"1.1.1",pane:"treePane",opacity:0.75,minZoom:9,maxZoom:18,attribution:"Baumarten: Thünen-Institut, Blickensdörfer et al. 2024 (Daten 2017/2018)"});
async function treeAt(ll){ const p=L.CRS.EPSG3857.project(ll), d=15; const u=`${TH_URL}?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=geonode:Dominant_Species_Class&query_layers=geonode:Dominant_Species_Class&styles=&srs=EPSG:3857&bbox=${p.x-d},${p.y-d},${p.x+d},${p.y+d}&width=3&height=3&x=1&y=1&info_format=application/json`;
  const ctl=new AbortController(), to=setTimeout(()=>ctl.abort(),12000);
  try{ const j=await (await fetch(u,{signal:ctl.signal})).json(); const v=j.features&&j.features[0]&&j.features[0].properties.GRAY_INDEX; return v||0; } finally{ clearTimeout(to); } }

// Pilzfunde aus iNaturalist
const INAT={on:false,taxon:null,area:null,busy:false,t:null,grp:L.layerGroup()};
map.createPane("inatPane").style.zIndex=640;
const inatRenderer=L.canvas({pane:"inatPane",padding:0.3});
function inatMsg(t){ if($("inatNote")) $("inatNote").textContent=t; }
async function inatLoad(force){
  if(!INAT.on) return; if(inArtifact()){ inatMsg("In der Claude-Artifact-Ansicht gesperrt; die Online-Fassung nutzen."); return; }
  if(map.getZoom()<10){ inatMsg("Für Fundmeldungen näher heranzoomen (ab Zoomstufe 10)."); return; }
  const b=map.getBounds(); if(!force&&INAT.area&&INAT.area.contains(b)) return; if(INAT.busy) return; INAT.busy=true;
  const bp=b.pad(0.25), prm=new URLSearchParams({swlat:bp.getSouth().toFixed(4),swlng:bp.getWest().toFixed(4),nelat:bp.getNorth().toFixed(4),nelng:bp.getEast().toFixed(4),taxon_id:INAT.taxon?INAT.taxon.id:47170,per_page:200,order_by:"observed_on",order:"desc",locale:"de",verifiable:"true"});
  inatMsg("lade Fundmeldungen …");
  try{ const ctl=new AbortController(), to=setTimeout(()=>ctl.abort(),20000);
    const js=await (await fetch("https://api.inaturalist.org/v1/observations?"+prm,{signal:ctl.signal})).json(); clearTimeout(to);
    INAT.grp.clearLayers(); const now=Date.now(); let n=0;
    for(const o of js.results||[]){ if(!o.geojson) continue; const [lng,lat]=o.geojson.coordinates; n++;
      const age=o.observed_on?(now-new Date(o.observed_on).getTime())/864e5:9999, col=age<=30?"#d1452b":age<=365?"#e39342":"#8a8a8a";
      const t=o.taxon||{}, name=t.preferred_common_name||t.name||"unbestimmt";
      const m=L.circleMarker([lat,lng],{renderer:inatRenderer,radius:5.5,color:o.obscured?"#555":"#fff",weight:o.obscured?1.5:1.2,dashArray:o.obscured?"2 2":null,fillColor:col,fillOpacity:0.95}).addTo(INAT.grp);
      m.bindTooltip(esc(name)); m.bindPopup(`<b>${esc(name)}</b>${t.name&&t.name!==name?`<br><i>${esc(t.name)}</i>`:""}<br>${esc(o.observed_on||"ohne Datum")} · ${o.quality_grade==="research"?"von der Community bestätigt":"noch nicht bestätigt"}${o.obscured?"<br>Ort absichtlich ungenau (bis etwa 20 km)":o.positional_accuracy?`<br>Ortsgenauigkeit etwa ${fmt(o.positional_accuracy)} m`:""}<br><a href="https://www.inaturalist.org/observations/${o.id}" target="_blank" rel="noopener">bei iNaturalist ansehen</a>`);
      m.on("click",ev=>L.DomEvent.stopPropagation(ev)); }
    INAT.area=bp; inatMsg(`${fmt(n)} Fundmeldungen${INAT.taxon?" für "+INAT.taxon.label:" von Pilzen"} im Ausschnitt${js.total_results>n?` (die neuesten ${fmt(n)} von ${fmt(js.total_results)})`:""}. Rot: letzte 30 Tage, orange: letztes Jahr, grau: älter. Gestrichelt: Ort absichtlich ungenau.`);
  }catch(e){ inatMsg("iNaturalist ist gerade nicht erreichbar."); }
  INAT.busy=false; }
function inatSet(on){ INAT.on=on; if($("cInat")) $("cInat").checked=on; if(on){ INAT.grp.addTo(map); INAT.area=null; inatLoad(true); } else { map.removeLayer(INAT.grp); inatMsg(""); } updateHash(); }
map.on("moveend",()=>{ if(!INAT.on) return; clearTimeout(INAT.t); INAT.t=setTimeout(()=>inatLoad(false),1200); });
let taxT=null;
function bindInatSearch(){ const inp=$("inatSearch"), box=$("inatRes"); if(!inp) return;
  inp.addEventListener("input",()=>{ clearTimeout(taxT); const q=inp.value.trim(); if(q.length<3){ box.style.display="none"; return; }
    taxT=setTimeout(async()=>{ try{ const js=await (await fetch(`https://api.inaturalist.org/v1/taxa/autocomplete?q=${encodeURIComponent(q)}&taxon_id=47170&locale=de&per_page=8`)).json();
      box.innerHTML=(js.results||[]).map((t,i)=>`<div data-i="${i}">${esc(t.preferred_common_name||t.name)} <small><i>${esc(t.name)}</i></small></div>`).join("")||`<div class="ph">keine Pilzart gefunden</div>`; box.style.display="block";
      box.querySelectorAll("[data-i]").forEach(d=>d.onclick=()=>{ const t=js.results[+d.dataset.i]; INAT.taxon={id:t.id,label:t.preferred_common_name||t.name}; inp.value=INAT.taxon.label; box.style.display="none"; $("inatClr").style.display=""; inatSet(true); }); }catch(e){ inatMsg("Artsuche nicht erreichbar."); } },500); });
  $("inatClr").onclick=()=>{ INAT.taxon=null; inp.value=""; $("inatClr").style.display="none"; if(INAT.on){ INAT.area=null; inatLoad(true); } }; }

// Pilzwetter am Punkt (Open-Meteo, Modelldaten u. a. DWD ICON)
const iso=d=>d.toISOString().slice(0,10);
async function pilzWetter(ll){
  const lat=ll.lat.toFixed(3), lng=ll.lng.toFixed(3), base="https://api.open-meteo.com/v1/forecast";
  const r=await fetch(`${base}?latitude=${lat}&longitude=${lng}&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,temperature_2m_mean&hourly=soil_moisture_3_to_9cm&past_days=31&forecast_days=7&timezone=Europe%2FBerlin`);
  if(!r.ok) throw new Error("Wetterdienst "+r.status); const w=await r.json(), d=w.daily, today=iso(new Date(Date.now()+3600e3));
  let i=d.time.indexOf(today); if(i<0) i=d.time.length-7;
  const sum=(a,b)=>{ let s=0; for(let k=Math.max(0,a);k<b;k++) s+=d.precipitation_sum[k]||0; return s; };
  const p7=sum(i-7,i), p30=sum(i-30,i), n7=sum(i,i+7); let dry=0; for(let k=i-1;k>=0&&(d.precipitation_sum[k]||0)<1;k--) dry++;
  const tx=[i-3,i-2,i-1].map(k=>d.temperature_2m_max[k]), tn=[i-3,i-2,i-1].map(k=>d.temperature_2m_min[k]); const avg=a=>a.reduce((s,x)=>s+x,0)/a.length;
  let frost=0; for(let k=i-7;k<i;k++) if(d.temperature_2m_min[k]<=0) frost++;
  const sm=w.hourly.soil_moisture_3_to_9cm, hi=w.hourly.time.findIndex(t=>t.startsWith(today)); const smNow=hi>0?sm[hi-1]:null, smWeek=hi>168?sm[hi-169]:null;
  const out={p7,p30,n7,dry,tmax:avg(tx),tmin:avg(tn),frost,smNow,smWeek,today};
  const m=new Date().getMonth();
  if(m<=4){ try{ const start=new Date().getFullYear()+"-01-01";
      let r2=await fetch(`${base}?latitude=${lat}&longitude=${lng}&daily=temperature_2m_mean&start_date=${start}&end_date=${today}&timezone=Europe%2FBerlin`);
      if(!r2.ok){ const ctl=new AbortController(); setTimeout(()=>ctl.abort(),12000); r2=await fetch(`https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lng}&daily=temperature_2m_mean&start_date=${start}&end_date=${today}&timezone=Europe%2FBerlin`,{signal:ctl.signal}); }
      const g=(await r2.json()).daily; let gs=0; g.time.forEach((t,k)=>{ const v=g.temperature_2m_mean[k]; if(v==null||v<=0) return; const mm=+t.slice(5,7); gs+=v*(mm===1?0.5:mm===2?0.75:1); }); out.gls=gs;
    }catch(e){ out.gls=null; } }
  return out; }
function wetterText(w,leg){
  const L_=[]; const z=D.units[leg]&&D.units[leg].z; const nfk=z?z[2]:null;
  L_.push(`<b>Regen:</b> ${fmt(w.p7,0)} l/m² in den letzten 7 Tagen, ${fmt(w.p30,0)} l/m² in 30 Tagen; ${w.dry===0?"gestern geregnet":`seit ${w.dry} Tag${w.dry===1?"":"en"} kein nennenswerter Regen`}. Vorhersage 7 Tage: ${fmt(w.n7,0)} l/m².`);
  L_.push(`<b>Temperatur</b> (Mittel der letzten 3 Tage): ${fmt(w.tmax,0)} °C am Tag, ${fmt(w.tmin,0)} °C in der Nacht${w.frost?`; ${w.frost} Frostnächte in den letzten 7 Tagen`:""}.`);
  if(w.smNow!=null) L_.push(`<b>Bodenfeuchte</b> 3 bis 9 cm (Modell): ${fmt(w.smNow*100,0)} Vol.-%${w.smWeek!=null?`, vor einer Woche ${fmt(w.smWeek*100,0)} Vol.-%`:""}.`);
  const E=[];
  if(w.p7>=10) E.push("Feuchte: Mit mindestens etwa 10 l/m² in 7 Tagen ist es nach der Faustregel des Buchs feucht genug.");
  else E.push(`Feuchte: knapp (unter etwa 10 l/m² in 7 Tagen).${nfk!=null&&nfk>=140?" Dieser Boden speichert aber viel Wasser (nutzbare Feldkapazität "+fmt(nfk)+" mm); in Trockenphasen sind solche Böden die bessere Wahl.":""}`);
  if(w.p30<30) E.push("Nach längerer Trockenheit lösen kleine Regenmengen meist noch keinen Pilzschub aus.");
  if(w.frost) E.push("Nach Frost stellen viele Arten das Wachstum ein. Angefrorene Pilze nicht mehr essen (Gefahr einer Lebensmittelvergiftung). Frostharte Arten wie Austern-Seitling, Samtfußrübling und Judasohr können jetzt kommen.");
  else if(w.tmax>=15&&w.tmax<=20&&w.tmin>=5&&w.tmin<=15) E.push("Temperatur: ideal für die meisten „mildliebenden“ Arten (tags 15 bis 20 °C, nachts 5 bis 15 °C).");
  else if(w.tmax>25) E.push("Temperatur: eher zu warm; viele Arten wachsen erst wieder bei kühlerem Wetter.");
  if(w.gls!==undefined) E.push(w.gls==null?"Grünlandsumme: nicht abrufbar.":`Grünlandsumme seit 1. Januar: ${fmt(w.gls,0)} °C. Ab etwa 200 °C beginnt laut Buch die Morchelzeit (Spitz-Morchel zuerst).`);
  return `<div class="pr" style="margin:2px 0 4px">${L_.join("<br>")}</div><div class="pb"><b>Einschätzung nach den Faustregeln des Buchs:</b><br>${E.join("<br>")}</div><div class="pr">Wetter: Open-Meteo, Modelldaten (u. a. Deutscher Wetterdienst), Punktwert für ein Raster von wenigen Kilometern, keine Messstation.</div>`; }
async function pilzPoint(ll,leg,my){
  const box=$("ptPilzIn"); if(!box) return; box.innerHTML='<span class="ph">wird abgefragt …</span>';
  const parts={}; const show=()=>{ if(curPoint!==my||!$("ptPilzIn")) return;
    const pz=leg?pzOf(leg):[];
    let h=`<div class="prop"><div class="pn"><span>Bodengruppe für Pilze</span></div><div class="pv">${pz.length?pz.map(p=>`<span class="sw" style="background:${PZ[p].col};width:10px;height:10px;display:inline-block;border-radius:2px"></span> ${PZ[p].n}`).join("<br>"):"keine der drei Gruppen (mittlerer Basengehalt oder keine Angaben)"}</div>${pz.length?`<div class="pb">${pz.map(p=>`${PZ[p].n}: ${PZ[p].pilze}`).join("<br>")}</div>`:""}<div class="pr">Mittelwert der Bodeneinheit. Nadelstreu kann den Oberboden auf Kalk versauern, geschotterte Wege und Waldkalkung machen saure Wälder stellenweise basisch.</div></div>`;
    h+=`<div class="prop"><div class="pn"><span>Hang (Höhenmodell etwa 30 m)</span></div><div class="pv">${parts.asp===undefined?"…":parts.asp?(parts.asp.sl<3?`eben (Neigung ${fmt(parts.asp.sl,1)}°)`:`${ASP[aspCls(parts.asp.az)][0]} (${fmt(parts.asp.az)}°), Neigung ${fmt(parts.asp.sl,1)}°`):"nicht abrufbar"}</div><div class="pr">Südhänge tragen früh im Jahr, Nordhänge halten im trockenen Sommer länger feucht, Westhänge bekommen oft mehr Regen.</div></div>`;
    h+=`<div class="prop"><div class="pn"><span>Baumart (Thünen-Institut, 10 m)</span></div><div class="pv">${parts.tree===undefined?"…":parts.tree===null?"nicht abrufbar":parts.tree?TREE[parts.tree][0]:"kein Wald oder keine Angabe"}</div>${parts.tree&&TREE_PILZ[parts.tree]?`<div class="pb">${TREE_PILZ[parts.tree]}</div>`:""}<div class="pr">Satellitenkarte mit Daten aus 2017 und 2018; Fällungen und Borkenkäferschäden seitdem sind nicht enthalten.</div></div>`;
    h+=`<div class="prop"><div class="pn"><span>Pilzwetter</span></div>${parts.wx===undefined?'<div class="pv">…</div>':parts.wx===null?'<div class="pv">Wetterdienst nicht erreichbar.</div>':wetterText(parts.wx,leg)}</div>`;
    h+=`<div class="pr">Keine Bestimmungshilfe: Pilze nur essen, wenn sie sicher bestimmt sind, im Zweifel bei einer Pilzberatung (DGfM-Pilzsachverständige) vorlegen.</div>`;
    $("ptPilzIn").innerHTML=h; };
  show();
  if(inArtifact()){ $("ptPilzIn").innerHTML='<span class="ph">In der Claude-Artifact-Ansicht sind Wetter, Hang und Baumart gesperrt. Die Bodengruppe steht in der Online-Fassung; dort funktioniert alles.</span>'; return; }
  aspectAt(ll).then(a=>{ parts.asp=a; show(); }).catch(()=>{ parts.asp=null; show(); });
  treeAt(ll).then(t=>{ parts.tree=t; show(); }).catch(()=>{ parts.tree=null; show(); });
  pilzWetter(ll).then(w=>{ parts.wx=w; show(); }).catch(()=>{ parts.wx=null; show(); }); }
function pilzSet(k,on){ S[k]=on; const lay={asp:aspLayer,tree:treeLayer}[k]; if(on) lay.addTo(map); else map.removeLayer(lay); const cb=$(k==="asp"?"cAsp":"cTree"); if(cb) cb.checked=on;
  if(on&&map.getZoom()<(k==="asp"?11:9)) toast(k==="asp"?"Hangrichtung erscheint ab Zoomstufe 11":"Baumarten erscheinen ab Zoomstufe 9"); updateHash(); }
function pilzInit(){
  pzChips(); bindInatSearch();
  $("cAsp").onchange=e=>pilzSet("asp",e.target.checked); $("cTree").onchange=e=>pilzSet("tree",e.target.checked); $("cInat").onchange=e=>inatSet(e.target.checked);
  $("aspLeg").innerHTML=ASP.map(a=>`<span><span class="sw" style="background:${a[1]}"></span>${a[0]}</span>`).join("");
  $("treeLeg").innerHTML=Object.values(TREE).map(a=>`<span><span class="sw" style="background:${a[1]}"></span>${a[0]}</span>`).join(""); }
