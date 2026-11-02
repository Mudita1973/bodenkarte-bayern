import requests, json, concurrent.futures as cf, os, time
B="https://ags.cuzk.gov.cz/arcgis/rest/services/ZABAGED_POLOHOPIS/MapServer"
LAY=[138,139,142,140,141,135,136,137,132,131,18,130,129,114,115,116,117,118,119,121,122,123,124,125,126,127,134]
base=dict(where="1=1",geometry="12.09,48.55,15.62,50.45",geometryType="esriGeometryEnvelope",inSR="4326",spatialRel="esriSpatialRelIntersects")
jobs=[]
for l in LAY:
    ids=requests.get(f"{B}/{l}/query",params=dict(base,returnIdsOnly="true",f="json"),timeout=300).json().get("objectIds") or []
    ids.sort(); print(l,len(ids),flush=True)
    for i in range(0,len(ids),1000): jobs.append((l,i//1000,ids[i:i+1000]))
def get(job):
    l,i,ids=job; fn=f"zab/z{l}_{i:04d}.json"
    if os.path.exists(fn) and os.path.getsize(fn)>50: return 0
    for t in range(4):
        try:
            r=requests.post(f"{B}/{l}/query",data=dict(objectIds=",".join(map(str,ids)),outFields="OBJECTID",outSR="32633",maxAllowableOffset="15",returnGeometry="true",f="json"),timeout=240)
            j=r.json(); assert "features" in j, str(j)[:200]
            json.dump({"l":l,"f":[f["geometry"]["rings"] for f in j["features"] if f.get("geometry")]},open(fn,"w")); return len(j["features"])
        except Exception as e: time.sleep(3+5*t); err=e
    print("FEHLER",l,i,err,flush=True); return -1
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(get,jobs))
print("fertig",sum(r for r in res if r>0),sum(1 for r in res if r<0),flush=True)
