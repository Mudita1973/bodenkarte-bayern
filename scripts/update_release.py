from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[1];dist=root/'dist'
for original,versioned in [('loader.js','loader-3.1.js'),('mobile.js','mobile-3.1.js')]:
    (dist/versioned).write_bytes((dist/original).read_bytes())
ph_name='ph-'+hashlib.sha256((dist/'ph.js').read_bytes()).hexdigest()[:12]+'.js'
(dist/ph_name).write_bytes((dist/'ph.js').read_bytes())
index=dist/'index.html';index.write_text(re.sub(r'<script src="ph(?:-[^"]+)?\.js"></script>', '<script src="'+ph_name+'"></script>',index.read_text()))
p=dist/'offline-assets.json';manifest=json.loads(p.read_text())
for name in ['loader-3.1.js','mobile-3.1.js','interpretation.js','spatial.js','ph.js']:
    if name not in manifest['assets']:manifest['assets'].append(name)
p.write_text(json.dumps(manifest,separators=(',',':')))
manifest['assets']=[p for p in manifest['assets'] if not re.fullmatch(r'ph-[a-f0-9]+\.js',p)]+[ph_name]
p.write_text(json.dumps(manifest,separators=(',',':')))
assets=manifest['assets'];digest=hashlib.sha256()
for name in assets:
    path=dist/('index.html' if name=='./' else name)
    if not path.is_file():raise RuntimeError('Missing asset: '+name)
    digest.update(path.read_bytes())
template=(root/'scripts/finalize_pwa.py').read_text().split("worker=r'''",1)[1].split("'''.replace",1)[0]
# An installed update may activate without losing notes or reloading an open map.
# Versioned boot scripts and content-addressed data let old tabs finish safely.
template=template.replace("self.addEventListener('message',event=>{", "self.addEventListener('message',event=>{if(event.data?.type==='ACTIVATE_UPDATE'){self.skipWaiting();return}")
(dist/'sw.js').write_text(template.replace('VERSION',digest.hexdigest()[:16]).replace('ASSETS_JSON',json.dumps(assets)))
print(json.dumps({'cacheVersion':digest.hexdigest()[:16],'assets':len(assets)}))
