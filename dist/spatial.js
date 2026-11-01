let geometryState={key:'',parts:[],pending:false,error:''},geometryTimer=0,geometryGeneration=0;
function soilOverviewActive(){return !window.SOIL_EAGER&&!!DATA?.overview_features?.length&&scale/baseScale<4}
function geometryParts(){const b=[-ox/scale,-oy/scale,(W-ox)/scale,(H-oy)/scale];return DATA.feature_parts.filter(p=>p.bbox[2]>=b[0]&&p.bbox[0]<=b[2]&&p.bbox[3]>=b[1]&&p.bbox[1]<=b[3])}
function geometryViewComplete(){return !!window.SOIL_EAGER||!soilOverviewActive()&&geometryParts().every(p=>DATA.loadedParts.has(p.url))}
function updateGeometryMessage(){const node=$('geometryStatus');if(!node)return;const parts=geometryState.parts,done=parts.filter(p=>DATA.loadedParts.has(p.url)).length;
 node.textContent=soilOverviewActive()?'Bayern-Übersicht: 750-m-Raster. Für genaue Bodeneinheiten hineinzoomen.':geometryState.error?'Detaildaten fehlen: '+geometryState.error:geometryViewComplete()?'Detaildaten für den sichtbaren Ausschnitt bereit. Bodengrenzen bleiben etwa 25 m vereinfacht.':'Regionale Detaildaten laden · '+done+' / '+parts.length+' Pakete. Noch keine vollständige Punktzuordnung.';
 $('retryGeometry').hidden=!geometryState.error;
 $('retryGeometry').onclick=()=>{geometryState.key='';geometryState.error='';queueGeometryView()};
}
function queueGeometryView(){
 if(!DATA||!extensionReady||window.SOIL_EAGER)return;
 if(soilOverviewActive()){clearTimeout(geometryTimer);geometryGeneration++;geometryState={key:'',parts:[],pending:false,error:''};updateGeometryMessage();return}
 const parts=geometryParts(),key=parts.map(p=>p.url).join('|');
 if(geometryState.key===key){updateGeometryMessage();return}
 clearTimeout(geometryTimer);const ticket=++geometryGeneration;geometryState={key,parts,pending:true,error:''};updateGeometryMessage();
 geometryTimer=setTimeout(async()=>{
  try{await loadSoilParts(DATA,parts,{cacheOnly:offlineEnabled(),onBatch:indexSoilFeatures});if(ticket!==geometryGeneration)return;geometryState.pending=false;geometryState.error=''}
  catch(e){if(ticket!==geometryGeneration)return;geometryState.pending=false;geometryState.error=e.message}
  if(ticket===geometryGeneration){cancelSoilRender();updateGeometryMessage();request()}
 },160);
}
