"""Prepare the buildless PWA from a validated local map export."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re

p=argparse.ArgumentParser();p.add_argument('--source-html',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];dist=root/'dist';dist.mkdir(exist_ok=True);(dist/'data').mkdir(exist_ok=True)
source=Path(args.source_html).read_text()
packed=re.search(r'<script id="geodata"[^>]*>(.*?)</script>',source,re.S).group(1)
data=json.loads(gzip.decompress(base64.b64decode(packed)))
features=data.pop('features');parts=[]
for i in range(0,len(features),6000):
    chunk=features[i:i+6000];raw=json.dumps(chunk,separators=(',',':'),ensure_ascii=False).encode();body=gzip.compress(raw,compresslevel=8,mtime=0)
    digest=hashlib.sha256(body).hexdigest()[:12];name=f'data/part-{i//6000:02}-{digest}.bin';(dist/name).write_bytes(body)
    parts.append({'url':name,'count':len(chunk),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
data['feature_parts']=parts;data['feature_count']=len(features)
meta=json.dumps(data,separators=(',',':'),ensure_ascii=False).encode();digest=hashlib.sha256(meta).hexdigest()[:12];meta_name=f'data/index-{digest}.json';(dist/meta_name).write_bytes(meta)
for x in (dist/'data').iterdir():
    if x.name not in {Path(meta_name).name,*[Path(a['url']).name for a in parts]}:x.unlink()
html=re.sub(r'<script id="geodata"[^>]*>.*?</script>','',source,flags=re.S)
old="const b64=$('geodata').textContent.trim(),bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0)),stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));DATA=JSON.parse(await new Response(stream).text());$('geodata').remove();"
if old not in html:raise RuntimeError('Map loader changed; review adapter')
html=html.replace(old,"DATA=await loadHostedSoil();")
css=re.search(r'<style>(.*?)</style>',html,re.S).group(1);(dist/'base.css').write_text(css);html=re.sub(r'<style>.*?</style>','<link rel="stylesheet" href="base.css">',html,count=1,flags=re.S)
html=html.replace('</head>','<link rel="stylesheet" href="mobile.css"><link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#214d3a"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png"><link rel="icon" href="icons/icon.svg"><meta name="description" content="Bayerns Böden erkunden: amtliche Bodendaten, Luftbilder, Nutzungsfilter und Offline-Ausschnitte."><script src="loader.js"></script></head>')
html=html.replace('content="width=device-width, initial-scale=1"','content="width=device-width, initial-scale=1, viewport-fit=cover"')
html=html.replace('<title>Bayern · Bodenbeschaffenheit</title>','<title>Bodenkarte Bayern</title>').replace('<html lang="de">','<html lang="de" data-boden-app="3">')
html=html.replace('Bodenbeschaffenheit im Überblick','Bodenkarte Bayern').replace('Version 2.5 ·','Web-App 3.0 ·')
html=html.replace('<aside class="left">','<aside class="left" id="filterPanel" aria-label="Kartenfilter">').replace('<aside class="right">','<aside class="right" id="detailPanel" aria-label="Punktdetails">')
html=html.replace('</header>','<div class="app-actions"><button id="appInstall" class="app-install">App installieren</button><button id="appInfo" aria-label="Informationen und Offline-Speicherung">Info</button></div></header>')
html=html.replace('</body>','<div id="mobileBackdrop" hidden></div><nav class="mobile-nav" aria-label="Kartenbedienung"><button id="navMap" aria-pressed="true">Karte</button><button id="navFilters" aria-controls="filterPanel" aria-expanded="false">Filter &amp; Suche</button><button id="navDetails" aria-controls="detailPanel" aria-expanded="false">Punktdetails</button></nav><dialog id="appDialog"><button id="closeAppDialog" class="dialog-close" aria-label="Schließen">×</button><h2>Deine Bodenkarte für unterwegs</h2><p id="installHelp">Auf dem iPhone in Safari: Teilen → „Zum Home-Bildschirm“. Auf Android im Browsermenü „App installieren“ oder „Zum Startbildschirm hinzufügen“ wählen.</p><p>Private Testversion. Die Daten sind eine Orientierung im Maßstab 1:25.000. Bodengrenzen sind vereinfacht; pH und aktuelle Feuchte sind keine Messwerte dieser App.</p><button id="cacheApp" class="wide">Bodenkarte offline bereithalten</button><p id="cacheStatus" role="status">Für die gesamte Bodengrundlage werden beim ersten Aufruf etwa 27 MB geladen. Zusatzbilder und Nutzungs-/Moorflächen separat als Offline-Paket sichern.</p><p>Merkpunkte und Notizen bleiben auf diesem Gerät. Zum Übertragen JSON exportieren. <a href="about.html" target="_blank" rel="noopener">Datenquellen, Datenschutz und Hinweise</a></p></dialog><script src="mobile.js"></script></body>')
(dist/'index.html').write_text(html)
(dist/'loader.js').write_text("window.SOIL_MANIFEST="+json.dumps(meta_name)+";\n"+"""async function loadHostedSoil(){
 const mr=await fetch(window.SOIL_MANIFEST,{credentials:'same-origin'});if(!mr.ok)throw Error('Bodendaten-Index nicht erreichbar (HTTP '+mr.status+').');const data=await mr.json();if(!Array.isArray(data.feature_parts)||!Number.isInteger(data.feature_count))throw Error('Ungültiger Bodendaten-Index.');data.features=[];
 for(let i=0;i<data.feature_parts.length;i++){const part=data.feature_parts[i];document.getElementById('status').textContent='Bodendaten laden · '+(i+1)+' / '+data.feature_parts.length;const response=await fetch(part.url,{credentials:'same-origin'});if(!response.ok)throw Error('Datenpaket nicht erreichbar (HTTP '+response.status+').');const bytes=new Uint8Array(await response.arrayBuffer());const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');if(actual!==part.sha256)throw Error('Datenpaket ist beschädigt. Bitte online neu laden.');let json;if(bytes[0]===31&&bytes[1]===139){json=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text()}else throw Error('Datenpaket hat ein unerwartetes Format.');const features=JSON.parse(json);if(!Array.isArray(features)||features.length!==part.count)throw Error('Datenpaket ist unvollständig.');for(const f of features)data.features.push(f);await new Promise(r=>setTimeout(r,0));}
 if(data.features.length!==data.feature_count)throw Error('Bodenbestand ist unvollständig.');return data;
}
""")
assets=['offline-assets.json','./','index.html','base.css','mobile.css','mobile.js','loader.js','manifest.webmanifest','about.html','icons/icon-192.png','icons/icon-512.png','icons/apple-touch-icon.png','icons/icon.svg',meta_name]+[x['url'] for x in parts]
(dist/'offline-assets.json').write_text(json.dumps({'assets':assets,'dataBytes':sum(x['bytes'] for x in parts),'featureCount':len(features)}))
print(json.dumps({'features':len(features),'parts':len(parts),'compressedBytes':sum(x['bytes'] for x in parts),'largestAsset':max(x['bytes'] for x in parts),'manifest':meta_name}))
