"""Generate deterministic app icons and the bounded service worker."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];dist=root/'dist';icons=dist/'icons';icons.mkdir(exist_ok=True)
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="108" fill="#214d3a"/><path d="M118 204 256 124 394 204 256 284Z" fill="#d8e8a1"/><path d="m118 254 138 80 138-80v44l-138 80-138-80Z" fill="#cfab73"/><path d="m118 348 138 80 138-80v-36l-138 80-138-80Z" fill="#8caa87"/></svg>'
(icons/'icon.svg').write_text(svg)
for size,name in [(192,'icon-192.png'),(512,'icon-512.png'),(180,'apple-touch-icon.png')]:
    im=Image.new('RGB',(1024,1024),'#214d3a');d=ImageDraw.Draw(im)
    def poly(points,color):d.polygon([(int(x*2),int(y*2)) for x,y in points],fill=color)
    poly([(118,204),(256,124),(394,204),(256,284)],'#d8e8a1');poly([(118,254),(256,334),(394,254),(394,298),(256,378),(118,298)],'#cfab73');poly([(118,312),(256,392),(394,312),(394,348),(256,428),(118,348)],'#8caa87')
    im.resize((size,size),Image.Resampling.LANCZOS).save(icons/name)
assets=json.loads((dist/'offline-assets.json').read_text())['assets'];digest=hashlib.sha256()
for name in assets:
    p=dist/('index.html' if name=='./' else name)
    if not p.is_file():raise RuntimeError('Missing PWA asset: '+name)
    digest.update(p.read_bytes())
version=digest.hexdigest()[:16]
worker=r'''const CACHE='bodenkarte-app-VERSION';
const ASSETS=ASSETS_JSON;
const PREFIX=new URL('./',self.location.href);
const URLS=ASSETS.map(p=>new URL(p,PREFIX).href);
const ALLOWED=new Set(URLS);
const CORE=URLS.filter(u=>!u.includes('/data/'));
async function safeResponse(response,url){if(!response||!response.ok||response.redirected)return false;const type=response.headers.get('content-type')||'';if(url.endsWith('.bin')){const bytes=new Uint8Array(await response.clone().arrayBuffer());return bytes[0]===31&&bytes[1]===139}if(url.endsWith('.json')||url.endsWith('.webmanifest')){if(type.includes('text/html'))return false;try{await response.clone().json();return true}catch{return false}}if(type.includes('text/html')||url.endsWith('.html')||url===PREFIX.href){const html=await response.clone().text();return html.includes(url.endsWith('about.html')?'data-boden-info="3"':'data-boden-app="3"')}return true}
self.addEventListener('install',event=>{event.waitUntil((async()=>{const cache=await caches.open(CACHE);for(const url of CORE){const response=await fetch(url,{credentials:'same-origin'});if(!await safeResponse(response,url))throw Error('App-Datei konnte nicht sicher gespeichert werden.');await cache.put(url,response)}})())});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('bodenkarte-app-')&&name!==CACHE)await caches.delete(name);await self.clients.claim()})())});
self.addEventListener('fetch',event=>{const request=event.request;if(request.method!=='GET')return;const url=new URL(request.url);if(url.origin!==PREFIX.origin||!ALLOWED.has(url.href))return;event.respondWith((async()=>{const cache=await caches.open(CACHE);if(request.mode==='navigate'){try{const fresh=await fetch(request);if(await safeResponse(fresh,url.href))await cache.put(url.href,fresh.clone());return fresh}catch{const saved=await cache.match(url.href)||await cache.match(new URL('index.html',PREFIX).href);return saved||new Response('Bodenkarte noch nicht offline gespeichert.',{status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}})}}const saved=await cache.match(url.href);if(saved)return saved;const fresh=await fetch(request);if(await safeResponse(fresh,url.href))await cache.put(url.href,fresh.clone());return fresh})())});
self.addEventListener('message',event=>{if(event.data?.type!=='CHECK_OFFLINE')return;event.waitUntil((async()=>{const cache=await caches.open(CACHE);let cached=0;for(const url of URLS)if(await cache.match(url))cached++;event.source?.postMessage({type:'OFFLINE_STATUS',complete:cached===URLS.length,cached,total:URLS.length})})())});
'''.replace('VERSION',version).replace('ASSETS_JSON',json.dumps(assets))
(dist/'sw.js').write_text(worker)
(dist/'_headers').write_text('/sw.js\n  Cache-Control: no-cache\n  Service-Worker-Allowed: /\n/manifest.webmanifest\n  Content-Type: application/manifest+json\n  Cache-Control: no-cache\n/data/*\n  Cache-Control: public, max-age=31536000, immutable\n  X-Content-Type-Options: nosniff\n/*\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Content-Type-Options: nosniff\n')
print(json.dumps({'cacheVersion':version,'assets':len(assets),'maxFileBytes':max(p.stat().st_size for p in dist.rglob('*') if p.is_file())}))
