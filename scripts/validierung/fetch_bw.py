import requests, json, time, sys
T=json.load(open("taxa.json")); jobs=[(v["id"],n) for n,v in T.items()]+[(47170,"Fungi")]
BB=dict(swlat=47.50,swlng=7.48,nelat=49.81,nelng=10.52)
out={}
for tid,name in jobs:
    rows=[]; last=0
    while True:
        p=dict(BB,taxon_id=tid,quality_grade="research",acc_below=251,geoprivacy="open",taxon_geoprivacy="open",per_page=200,order="asc",order_by="id",id_above=last,
               fields="id,observed_on,geojson,positional_accuracy,user.id,taxon.id,taxon.name,obscured")
        for t in range(5):
            try: r=requests.get("https://api.inaturalist.org/v1/observations",params=p,timeout=90); j=r.json(); break
            except Exception as e: time.sleep(5+10*t)
        res=j.get("results",[])
        for o in res:
            if not o.get("geojson") or o.get("obscured"): continue
            lng,lat=o["geojson"]["coordinates"]
            rows.append([o["id"],lat,lng,(o.get("user") or {}).get("id"),o.get("observed_on"),(o.get("taxon") or {}).get("id"),o.get("positional_accuracy")])
        if len(res)<200: break
        last=res[-1]["id"]; time.sleep(1.0)
    out[name]=rows; print(name,tid,len(rows),flush=True)
    json.dump(out,open("obs_bw.json","w"))
print("fertig",flush=True)
