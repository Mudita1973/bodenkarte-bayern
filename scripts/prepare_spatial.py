"""Make a small, explicitly coarse overview and spatial detail packs from the lossless PWA data.

Every source feature occurs in exactly one pack. Pack bounds include the entire
geometry (not just its centre), so long polygons cannot disappear at tile edges.
The 750 m overview samples cell centres and must never be used for point queries.
"""
from pathlib import Path
from array import array
import argparse, gzip, hashlib, json, math

root = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=root/'dist');args=parser.parse_args()
source=args.source
dist = root / 'dist'
data = json.loads((source / 'data/index-87c444f03acc.json').read_text())
features = []
for part in data['feature_parts']:
    raw = (source / part['url']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == part['sha256']
    records = json.loads(gzip.decompress(raw))
    assert len(records) == part['count']
    features.extend(records)
assert len(features) == data['feature_count']

def emit(name, obj):
    raw = gzip.compress(json.dumps(obj, separators=(',', ':')).encode(), compresslevel=9, mtime=0)
    sha = hashlib.sha256(raw).hexdigest()
    url = 'data/' + name + '-' + sha[:12] + '.bin'
    (dist / url).write_bytes(raw)
    return dict(url=url, count=len(obj), bytes=len(raw), sha256=sha)

step = 750
nx = math.ceil((data['bounds'][2] - data['bounds'][0]) / step)
ny = math.ceil((data['bounds'][3] - data['bounds'][1]) / step)
pixels = array('H', [0]) * (nx * ny)
entries = []
for serial, (li, rings) in enumerate(features):
    xs = [x for ring in rings for x in ring[::2]]
    ys = [y for ring in rings for y in ring[1::2]]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    cx, cy = int((bbox[0]+bbox[2])/2/50000), int((bbox[1]+bbox[3])/2/50000)
    # Separate regional files; stable ordering within each file retains overlaps.
    entries.append(((cx, cy), serial, bbox))
    crossings = {}
    for ring in rings:
        for j in range(0, len(ring)-2, 2):
            x0, y0, x1, y1 = ring[j:j+4]
            if y0 == y1:
                continue
            for row in range(max(0, math.ceil(min(y0,y1)/step-.5)), min(ny, math.ceil(max(y0,y1)/step-.5))):
                y = (row+.5)*step
                crossings.setdefault(row, []).append(x0 + (y-y0)*(x1-x0)/(y1-y0))
    for row, cuts in crossings.items():
        cuts.sort()
        for a,b in zip(cuts[::2], cuts[1::2]):
            left, right = max(0,math.ceil(a/step-.5)), min(nx,math.ceil(b/step-.5))
            if right > left:
                pixels[row*nx+left:row*nx+right] = array('H',[li+1])*(right-left)

overview = {}
for y in range(ny):
    x = 0
    while x < nx:
        label = pixels[y*nx+x]
        end = x+1
        while end < nx and pixels[y*nx+end] == label:
            end += 1
        if label:
            x0,y0,x1,y1 = x*step,y*step,end*step,(y+1)*step
            overview.setdefault(label-1, []).append([x0,y0,x1,y0,x1,y1,x0,y1,x0,y0])
        x = end
overview_part = emit('overview', sorted(overview.items()))
overview_part['resolution_m'] = step

groups = {}
for region, serial, bbox in entries:
    groups.setdefault(region, []).append((serial,bbox))
parts=[]
for (cx,cy), group in sorted(groups.items()):
    # Split large regions so decoding never monopolizes the main thread.
    for offset in range(0,len(group),4000):
        chunk=group[offset:offset+4000]
        part=emit('region-%02d-%02d-%02d'%(cx,cy,offset//4000), [features[i] for i,b in chunk])
        part['bbox']=[min(b[0] for i,b in chunk),min(b[1] for i,b in chunk),max(b[2] for i,b in chunk),max(b[3] for i,b in chunk)]
        parts.append(part)
assert sum(p['count'] for p in parts)==len(features)
data.update(feature_parts=parts, overview=overview_part, spatial_version=1)
raw=json.dumps(data,separators=(',',':'),ensure_ascii=False).encode()
index='data/spatial-index-'+hashlib.sha256(raw).hexdigest()[:12]+'.json'
(dist/index).write_bytes(raw)
(dist/'data/spatial-manifest-path.txt').write_text(index)
assets=json.loads((dist/'offline-assets.json').read_text())
assets['assets']=[p for p in assets['assets'] if not p.startswith('data/')]+[index,overview_part['url']]+[p['url'] for p in parts]
assets['dataBytes']=len(raw)+overview_part['bytes']+sum(p['bytes'] for p in parts)
(dist/'offline-assets.json').write_text(json.dumps(assets,separators=(',',':')))
report=dict(features=len(features),parts=len(parts),overview_bytes=overview_part['bytes'],index_bytes=len(raw),full_data_bytes=assets['dataBytes'],overview_resolution_m=step)
(root/'checks/spatial_build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
