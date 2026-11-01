from pathlib import Path
from collections import Counter
import gzip,hashlib,json
root=Path(__file__).resolve().parents[1];dist=root/'dist'
original=json.loads((dist/'data/index-87c444f03acc.json').read_text())
spatial=json.loads((dist/(dist/'data/spatial-manifest-path.txt').read_text()).read_text())
def check(manifest,check_bbox=False):
    seen=Counter();count=0
    for part in manifest['feature_parts']:
        raw=(dist/part['url']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==part['sha256'],part['url']
        records=json.loads(gzip.decompress(raw))
        assert len(records)==part['count']
        count+=len(records)
        for record in records:
            assert 0<=record[0]<len(manifest['legends'])
            seen[hashlib.sha256(json.dumps(record,separators=(',',':')).encode()).digest()]+=1
            if check_bbox:
                b=part['bbox']
                for ring in record[1]:
                    for j in range(0,len(ring),2):
                        assert b[0]<=ring[j]<=b[2] and b[1]<=ring[j+1]<=b[3],part['url']
    assert count==manifest['feature_count']
    return seen,count
before,count=check(original);after,new_count=check(spatial,True)
assert before==after,'Geometrien oder Häufigkeiten wurden verändert'
assert original['legends']==spatial['legends'],'Amtliche Legenden wurden verändert'
report=dict(passed=True,features=count,regional_packs=len(spatial['feature_parts']),all_geometries_identical=True,all_pack_bounds_enclose_full_geometry=True,original_legend_unchanged=True)
(root/'checks/geometry_integrity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
