// Metadata and overview first. Complete regional geometry is fetched only on demand.
window.SOIL_MANIFEST='data/spatial-index-89a6d95ddbf9.json';
let soilSlots=0;const soilWaiters=[];
async function readSoilPart(part,cacheOnly=false){
 if(soilSlots>=3)await new Promise(resolve=>soilWaiters.push(resolve));else soilSlots++;
 try{return await decodeSoilPart(part,cacheOnly)}finally{const next=soilWaiters.shift();if(next)next();else soilSlots--}
}
async function decodeSoilPart(part,cacheOnly=false){
 let response;
 if(cacheOnly){
  if(!('caches' in window))throw Error('Dieser Ausschnitt ist nicht offline gespeichert.');
  response=await caches.match(new URL(part.url,location.href).href);
  if(!response)throw Error('Detaildaten für diesen Ausschnitt fehlen offline. Unter Info vorher die Bodengrundlage sichern.');
 }else response=await fetch(part.url,{credentials:'same-origin'});
 if(!response.ok||response.redirected)throw Error('Datenpaket nicht erreichbar (HTTP '+response.status+').');
 const bytes=new Uint8Array(await response.arrayBuffer());
 const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
 if(actual!==part.sha256)throw Error('Datenpaket ist beschädigt. Bitte online neu laden.');
 if(bytes[0]!==31||bytes[1]!==139)throw Error('Datenpaket hat ein unerwartetes Format.');
 const records=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
 if(!Array.isArray(records)||records.length!==part.count)throw Error('Datenpaket ist unvollständig.');
 return records;
}
async function loadSoilParts(data,parts,{cacheOnly=false,onBatch=null}={}){
 let cursor=0;
 await Promise.all(Array.from({length:Math.min(3,parts.length)},async()=>{
  while(cursor<parts.length){
   const part=parts[cursor++];
   if(data.loadedParts.has(part.url))continue;
   if(!data.inflightParts.has(part.url)){
    const job=(async()=>{
     const features=await readSoilPart(part,cacheOnly);
     const start=data.features.length;
     for(const f of features)data.features.push(f);
     if(onBatch)await onBatch(start,data.features.length);
     data.loadedParts.add(part.url);
     data.geometryRevision++;if(data.onGeometryChanged)data.onGeometryChanged();
    })();
    data.inflightParts.set(part.url,job);
    job.finally(()=>data.inflightParts.delete(part.url)).catch(()=>{});
   }
   await data.inflightParts.get(part.url);
  }
 }));
}
async function loadHostedSoil(){
 const response=await fetch(window.SOIL_MANIFEST,{credentials:'same-origin'});
 if(!response.ok)throw Error('Bodendaten-Index nicht erreichbar (HTTP '+response.status+').');
 const data=await response.json();
 if(!Array.isArray(data.feature_parts)||!Number.isInteger(data.feature_count)||data.feature_parts.reduce((n,p)=>n+p.count,0)!==data.feature_count)throw Error('Ungültiger Bodendaten-Index.');
 data.features=[];data.loadedParts=new Set();data.inflightParts=new Map();data.geometryRevision=0;
 if(window.SOIL_EAGER){await loadSoilParts(data,data.feature_parts);data.overview_features=[]}
 else{document.getElementById('status').textContent='Bayern-Übersicht laden …';data.overview_features=await readSoilPart(data.overview)}
 return data;
}
