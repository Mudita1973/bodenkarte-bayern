import requests, json, concurrent.futures as cf, os, time, sys
B="https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa50/MapServer/2/query"
base=dict(where="1=1",geometry="12.09,48.55,15.62,50.45",geometryType="esriGeometryEnvelope",inSR="4326",spatialRel="esriSpatialRelIntersects")
ids=sorted(requests.get(B,params=dict(base,returnIdsOnly="true",f="json"),timeout=120).json()["objectIds"]); print(len(ids),flush=True)
ch=[ids[i:i+1000] for i in range(0,len(ids),1000)]
def get(i):
    fn=f"geo/g{i:04d}.geojson"
    if os.path.exists(fn) and os.path.getsize(fn)>100: return 0
    for t in range(4):
        try:
            r=requests.post(B,data=dict(objectIds=",".join(map(str,ch[i])),outFields="hor_karto,hor_typ,geneze,textura,zrnitost,mineralni_slozeni",outSR="32633",maxAllowableOffset="10",f="geojson"),timeout=240)
            j=r.json(); assert "features" in j, str(j)[:200]; json.dump(j,open(fn,"w")); return len(j["features"])
        except Exception as e: time.sleep(3+5*t); err=e
    print("FEHLER",i,err,flush=True); return -1
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(get,range(len(ch))))
print(sum(r for r in res if r>0), sum(1 for r in res if r<0))
B2="https://mapy.geology.cz/arcgis/rest/services/Pudy/pudni_typy_1mil/MapServer/0/query"
j=requests.post(B2,data=dict(where="1=1",geometry="12.09,48.55,15.62,50.45",geometryType="esriGeometryEnvelope",inSR="4326",outFields="*",outSR="32633",f="geojson"),timeout=240).json()
json.dump(j,open("pudy1mil.geojson","w")); print("1mil",len(j["features"]))
