import requests, json, concurrent.futures as cf, os, time
B="https://mapy.geology.cz/arcgis/rest/services/Pudy/pudni_typy50/MapServer/1/query"
geom="12.09,48.55,15.62,50.45"
base=dict(where="1=1",geometry=geom,geometryType="esriGeometryEnvelope",inSR="4326",spatialRel="esriSpatialRelIntersects")
ids=requests.get(B,params=dict(base,returnIdsOnly="true",f="json"),timeout=120).json()["objectIds"]
ids.sort(); print(len(ids))
chunks=[ids[i:i+500] for i in range(0,len(ids),500)]
def get(i):
    fn=f"raw/c{i:04d}.geojson"
    if os.path.exists(fn) and os.path.getsize(fn)>100: return 0
    for t in range(4):
        try:
            r=requests.post(B,data=dict(objectIds=",".join(map(str,chunks[i])),outFields="*",outSR="32633",f="geojson"),timeout=180)
            j=r.json(); assert "features" in j, str(j)[:200]
            json.dump(j,open(fn,"w")); return len(j["features"])
        except Exception as e:
            time.sleep(3+t*5); err=e
    print("FEHLER",i,err); return -1
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(get,range(len(chunks))))
print(sum(r for r in res if r>0), sum(1 for r in res if r<0))
