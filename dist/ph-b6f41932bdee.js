// SoilGrids WMS: pH in water, modelled at 250 m. Never relabel these as local measurements.
const PH_SERVICE='https://maps.isric.org/mapserv';
const PH_DEPTHS=['0-5cm','5-15cm','15-30cm'];
const phCache=new Map();let phDepth='0-5cm',phAutomatic=true,phTicket=0,phTimer=0,phController=null,phBusyKey='';
function phKey(point,depth=phDepth){return [point.lat.toFixed(6),point.lon.toFixed(6),depth].join('|')}
function phClass(value){return value<7?'sauer':value>7?'basisch':'neutral'}
function phNumber(value){return value.toFixed(1).replace('.',',')}
function phUncertainty(lo,hi){return lo<7&&hi>7?'Die Modellspanne umfasst saure und basische Werte. Die Einordnung am Standort ist unsicher.':lo<=7&&hi>=7?'Die Modellspanne erreicht den Neutralpunkt. Die Einordnung am Standort ist unsicher.':'Die Spanne ist eine Modellunsicherheit, keine gemessene Schwankungsbreite der Wiese.'}
function phUrl(point,depth,quantile){
 if(!PH_DEPTHS.includes(depth)||!['Q0.05','Q0.5','Q0.95'].includes(quantile))throw Error('Ungültige pH-Abfrage.');
 const layer='phh2o_'+depth+'_'+quantile,u=new URL(PH_SERVICE),d=.005;
 u.search=new URLSearchParams({map:'/map/phh2o.map',SERVICE:'WMS',VERSION:'1.3.0',REQUEST:'GetFeatureInfo',CRS:'EPSG:4326',BBOX:[point.lat-d,point.lon-d,point.lat+d,point.lon+d].join(','),WIDTH:'3',HEIGHT:'3',I:'1',J:'1',LAYERS:layer,QUERY_LAYERS:layer,STYLES:'',FORMAT:'image/png',INFO_FORMAT:'text/html',FEATURE_COUNT:'1'});
 return u.href;
}
function parsePhResponse(html,layer){
 if(!html.includes('>'+layer+'<'))throw Error('Für diesen Rasterpunkt wurden keine eindeutigen pH-Daten geliefert.');
 const values=[...html.matchAll(/<span\s+id=["']value["']\s*>\s*([-+]?\d+(?:\.\d+)?)\s*<\/span>/gi)].map(m=>Number(m[1]));
 if(values.length!==1||!Number.isInteger(values[0])||values[0]<0||values[0]>140)throw Error('pH-Dienst liefert keinen gültigen Zahlenwert.');
 return values[0]/10;
}
function phSamplePoint(html,point){
 const a=html.match(/id=["']latitude["']\s*>\s*([-+0-9.]+)\s*</i),b=html.match(/id=["']longitude["']\s*>\s*([-+0-9.]+)\s*</i);
 if(!a||!b)throw Error('pH-Dienst liefert keine prüfbare Rasterposition.');
 let lat=Number(a[1]),lon=Number(b[1]);
 // The service's WMS 1.3 HTML template can swap latitude/longitude labels.
 // Disambiguation is restricted to the non-overlapping Bavarian coordinate ranges.
 if(lat>=8&&lat<=15&&lon>=47&&lon<=51)[lat,lon]=[lon,lat];
 if(lat<47||lat>51||lon<8||lon>15)throw Error('pH-Rasterposition liegt außerhalb Bayerns.');
 const distance=6371000*Math.hypot((lat-point.lat)*Math.PI/180,(lon-point.lon)*Math.PI/180*Math.cos(point.lat*Math.PI/180));
 if(!Number.isFinite(distance)||distance>250)throw Error('Kein ausreichend naher pH-Rasterwert am gewählten Punkt.');
 return {lat,lon,distance_m:Math.round(distance)};
}
function validPhRecord(raw,point=null){
 if(!raw||raw.source!=='ISRIC SoilGrids250m 2.0'||raw.method!=='pH(H2O)'||!PH_DEPTHS.includes(raw.depth)||!raw.point||!Number.isFinite(raw.point.lat)||!Number.isFinite(raw.point.lon)||raw.point.lat<47||raw.point.lat>51||raw.point.lon<8||raw.point.lon>15||![raw.low,raw.median,raw.high].every(n=>Number.isFinite(n)&&n>=0&&n<=14)||raw.low>raw.median||raw.median>raw.high||typeof raw.retrievedAt!=='string'||raw.retrievedAt.length>50||point&&(Math.abs(raw.point.lat-point.lat)>.000001||Math.abs(raw.point.lon-point.lon)>.000001))throw Error('Ungültiger pH-Modell-Datensatz.');
 if(raw.gridPoint&&(![raw.gridPoint.lat,raw.gridPoint.lon,raw.gridPoint.distance_m].every(Number.isFinite)||raw.gridPoint.lat<47||raw.gridPoint.lat>51||raw.gridPoint.lon<8||raw.gridPoint.lon>15||raw.gridPoint.distance_m<0||raw.gridPoint.distance_m>250))throw Error('Ungültige pH-Rasterposition.');
 return {source:raw.source,method:raw.method,depth:raw.depth,resolution_m:250,point:{lat:raw.point.lat,lon:raw.point.lon},median:raw.median,low:raw.low,high:raw.high,retrievedAt:raw.retrievedAt,...(raw.gridPoint?{gridPoint:{lat:raw.gridPoint.lat,lon:raw.gridPoint.lon,distance_m:raw.gridPoint.distance_m}}:{})};
}
function phRecordsForPoint(point){if(!point)return [];return PH_DEPTHS.map(d=>phCache.get(phKey(point,d))).filter(Boolean)}
async function fetchPh(point,depth,signal){
 const samples=await Promise.all(['Q0.05','Q0.5','Q0.95'].map(async q=>{const r=await fetch(phUrl(point,depth,q),{signal,mode:'cors',credentials:'omit'});if(!r.ok||r.redirected)throw Error('pH-Dienst antwortet mit HTTP '+r.status);const html=await r.text();return {value:parsePhResponse(html,'phh2o_'+depth+'_'+q),point:phSamplePoint(html,point)}}));
 if(samples.some(s=>Math.abs(s.point.lat-samples[0].point.lat)>.00001||Math.abs(s.point.lon-samples[0].point.lon)>.00001))throw Error('pH-Quantile beziehen sich auf unterschiedliche Rasterzellen.');
 const numbers=samples.map(s=>s.value);
 return validPhRecord({source:'ISRIC SoilGrids250m 2.0',method:'pH(H2O)',depth,resolution_m:250,point,gridPoint:samples[0].point,low:numbers[0],median:numbers[1],high:numbers[2],retrievedAt:new Date().toISOString()});
}
function phMarkup(record,error=''){
 const source='<p class="note">ISRIC SoilGrids250m 2.0 · Modell im 250-m-Raster · pH in Wasser (H₂O), keine Vor-Ort-Messung. Nicht direkt mit pH(CaCl₂) vergleichen. <a href="https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html" target="_blank" rel="noopener noreferrer">Daten und Unsicherheit ↗</a></p>';
 if(!selectedPoint)return '<h3>pH-Wert · sauer oder basisch?</h3><p>Für einen Zahlenwert zuerst einen Punkt in der Karte wählen. Die ÜBK25-Legende selbst enthält hier keinen pH-Messwert.</p>'+source;
 let value=record?'<p class="ph-value">pH '+phNumber(record.median)+' <span>'+phClass(record.median)+' · Modellmedian</span></p><p><b>90-%-Modellintervall: '+phNumber(record.low)+' bis '+phNumber(record.high)+'</b><br>'+esc(phUncertainty(record.low,record.high))+'</p>':'<p role="status">'+esc(error||'pH-Modellwert wird abgefragt …')+'</p>';
 return '<h3>pH-Wert · sauer oder basisch?</h3>'+value+'<label for="phDepth">Bodentiefe</label><select id="phDepth">'+PH_DEPTHS.map(d=>'<option value="'+d+'"'+(d===phDepth?' selected':'')+'>'+d.replace('cm',' cm')+'</option>').join('')+'</select><button id="loadPh">'+(record?'pH erneut abfragen':'pH-Modellwerte abfragen')+'</button><p class="note">Vereinfachte Einordnung: unter 7 sauer, 7 neutral, über 7 basisch. Sie beschreibt den Modellmedian; das Intervall kann mehrere Bereiche umfassen.'+(record?' Abruf: '+esc(record.retrievedAt.slice(0,10))+'.'+(record.gridPoint?' Rasterzentrum etwa '+record.gridPoint.distance_m+' m vom Klickpunkt.':''):'')+'</p>'+source;
}
function renderPh(error=''){
 const panel=$('phPanel');if(!panel)return;
 const record=selectedPoint?phCache.get(phKey(selectedPoint)):null;panel.innerHTML=phMarkup(record,error);
 if($('phDepth'))$('phDepth').onchange=()=>{phDepth=$('phDepth').value;startPhQuery(true)};
 if($('loadPh')){$('loadPh').disabled=offlineEnabled();$('loadPh').onclick=()=>startPhQuery(true,true)}
}
function mountPhCard(){
 if(!$('phPanel'))$('detail').insertAdjacentHTML('afterbegin','<section class="ph-card" id="phPanel"></section>');
 renderPh();if(selectedPoint)startPhQuery(phAutomatic);
}
function startPhQuery(auto=true,refresh=false){
 const ticket=++phTicket;clearTimeout(phTimer);phController?.abort();phController=null;phBusyKey='';
 if(!selectedPoint){renderPh();return}
 const point={lat:selectedPoint.lat,lon:selectedPoint.lon},depth=phDepth,key=phKey(point,depth),cached=phCache.get(key);
 if(cached&&!refresh){renderPh();return}
 if(offlineEnabled()){renderPh('Für diesen Punkt und diese Tiefe ist kein pH-Modellwert gespeichert. Offline wird kein Zahlenwert geschätzt.');return}
 if(!auto){renderPh('Noch nicht abgefragt. Über die Schaltfläche einen pH-Modellwert laden.');return}
 renderPh();phBusyKey=key;
 phTimer=setTimeout(async()=>{
  if(ticket!==phTicket)return;if(offlineEnabled()){renderPh('Offline: kein neuer pH-Abruf.');return}
  const controller=new AbortController();phController=controller;const timer=setTimeout(()=>controller.abort(),18000);
  try{const record=await fetchPh(point,depth,controller.signal);if(ticket!==phTicket)return;phCache.set(key,record);while(phCache.size>200)phCache.delete(phCache.keys().next().value);phBusyKey='';renderPh()}
  catch(e){if(ticket!==phTicket)return;phBusyKey='';renderPh('pH derzeit nicht verfügbar: '+(e.name==='AbortError'?'Zeitüberschreitung.':e.message)+' Kein Mess- oder Modellwert wird erfunden.')}
  finally{clearTimeout(timer);if(ticket===phTicket)phController=null}
 },180);
}
async function installPh(){
 for(let i=0;i<3000&&window.BODEN_QA?.release!=='2.5';i++)await new Promise(r=>setTimeout(r,10));if(window.BODEN_QA?.release!=='2.5')return;
 $('clear').insertAdjacentHTML('afterend','<section class="extra-panel"><h3>pH-Wert am Kartenpunkt</h3><label class="checkrow"><input type="checkbox" id="autoPh" checked>pH-Modellwerte beim Kartenklick laden</label><p class="note">Zusatzdaten: ISRIC SoilGrids, 250 m. Abfrage des gewählten Punkts und der Bodentiefe online; keine automatische Standortermittlung. Ohne Daten bleibt die Einordnung ausdrücklich offen.</p></section>');
 $('autoPh').onchange=()=>{phAutomatic=$('autoPh').checked;if(selectedPoint)startPhQuery(phAutomatic)};
 const oldDetail=detail;detail=function(li){oldDetail(li);mountPhCard()};
 const oldUp=cv.onpointerup;cv.onpointerup=e=>{const wasDrag=dragged;oldUp(e);if(!wasDrag&&!dragged&&selectedPoint)mountPhCard()};
 const oldValidate=validateSaved;validateSaved=function(raw){const result=oldValidate(raw);for(let i=0;i<result.points.length;i++)if(raw.points[i].phRecords){if(!Array.isArray(raw.points[i].phRecords)||raw.points[i].phRecords.length>3)throw Error('Ungültige pH-Sicherung.');result.points[i].phRecords=raw.points[i].phRecords.map(r=>validPhRecord(r,result.points[i].point))}return result};
 const oldSave=saveCurrent;saveCurrent=function(kind){const before=savedStore.points.length;oldSave(kind);if(kind==='points'&&savedStore.points.length>before){savedStore.points.at(-1).phRecords=phRecordsForPoint(selectedPoint);persistSaved()}};
 const oldOffline=setOfflineMode;setOfflineMode=function(on){oldOffline(on);if(on)startPhQuery(false)};
 try{const savedRaw=localStorage.getItem(SAVED_KEY);if(savedRaw){const restored=validateSaved(JSON.parse(savedRaw));for(const item of restored.points){const current=savedStore.points.find(p=>p.id===item.id);if(current&&item.phRecords)current.phRecords=item.phRecords}}}catch{}
 const oldOpen=openSaved;openSaved=function(kind,id){const item=savedStore[kind].find(x=>x.id===id);if(item?.phRecords)for(const record of item.phRecords){const r=validPhRecord(record,item.point);phCache.set(phKey(r.point,r.depth),r)}oldOpen(kind,id);if(kind==='points')mountPhCard()};
 window.BODEN_QA={...window.BODEN_QA,ph_model:true,ph_measurements:false};
}
installPh();
