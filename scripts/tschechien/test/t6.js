const { chromium } = require('playwright'); const zlib=require('zlib');
(async()=>{ const b=await chromium.launch(); const errs=[]; const ctx=await b.newContext({viewport:{width:1440,height:950}});
 await ctx.route(/^https?:\/\/(?!localhost)/,r=>r.abort());
 // Mocks: Open-Meteo, iNaturalist, SoilGrids, AWS-Höhenkachel (geneigte Ebene nach Süden)
 const days=38, time=[...Array(days)].map((_,i)=>new Date(Date.now()+(i-31)*864e5).toISOString().slice(0,10));
 await ctx.route(/api\.open-meteo\.com/,r=>r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({daily:{time,precipitation_sum:time.map((_,i)=>i>24&&i<31?3:1),temperature_2m_max:time.map(()=>17),temperature_2m_min:time.map(()=>8),temperature_2m_mean:time.map(()=>12)},hourly:{time:[...Array(days*24)].map((_,h)=>time[Math.floor(h/24)]+"T"+String(h%24).padStart(2,"0")+":00"),soil_moisture_3_to_9cm:[...Array(days*24)].map(()=>0.31)}})}));
 await ctx.route(/api\.inaturalist\.org\/v1\/observations/,r=>r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({total_results:2,results:[{geojson:{coordinates:[13.31,49.31]},observed_on:new Date().toISOString().slice(0,10),quality_grade:"research",taxon:{name:"Cantharellus cibarius",preferred_common_name:"Echter Pfifferling"}},{geojson:{coordinates:[13.33,49.32]},observed_on:"2025-09-01",quality_grade:"needs_id",taxon:{name:"Boletus edulis"}}]})}));
 await ctx.route(/maps\.isric\.org/,r=>r.fulfill({status:200,contentType:'text/html',headers:{'access-control-allow-origin':'*'},body:'<td id="value">52</td>'}));
 const png=(()=>{ const W=256,H=256,raw=Buffer.alloc((W*3+1)*H); for(let y=0;y<H;y++){ raw[y*(W*3+1)]=0; const v=32768+800-y*3; for(let x=0;x<W;x++){ const o=y*(W*3+1)+1+x*3; raw[o]=v>>8; raw[o+1]=v&255; raw[o+2]=0; } }
   const crc=(buf)=>{ let c,crcT=[]; for(let n=0;n<256;n++){ c=n; for(let k=0;k<8;k++) c=c&1?0xedb88320^(c>>>1):c>>>1; crcT[n]=c>>>0; } let x=0xffffffff; for(const bb of buf) x=crcT[(x^bb)&255]^(x>>>8); return (x^0xffffffff)>>>0; };
   const ch=(t,d)=>{ const l=Buffer.alloc(4); l.writeUInt32BE(d.length); const td=Buffer.concat([Buffer.from(t),d]); const c=Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l,td,c]); };
   const ih=Buffer.alloc(13); ih.writeUInt32BE(W,0); ih.writeUInt32BE(H,4); ih[8]=8; ih[9]=2; return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),ch('IHDR',ih),ch('IDAT',zlib.deflateSync(raw)),ch('IEND',Buffer.alloc(0))]); })();
 await ctx.route(/elevation-tiles-prod/,r=>r.fulfill({status:200,contentType:'image/png',headers:{'access-control-allow-origin':'*'},body:png}));
 const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8766/#c=49.31%2C13.32&z=12&s=6.13.16&m=z'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000});
 console.log('Pilzbox sichtbar:', await p.evaluate(()=>getComputedStyle(document.getElementById('pilzBox')).display!=="none"), 'Quellen:', await p.evaluate(()=>[...document.getElementById('phSrc').options].map(o=>o.text)));
 await p.evaluate(()=>{ document.getElementById('pilzBox').open=true; return 1});
 for(const k of ["sauer","basisch","wasser"]) await p.click(`[data-pz="${k}"]`);
 await p.waitForTimeout(800);
 console.log('Legende:', await p.evaluate(()=>[...document.querySelectorAll('#legend li')].map(l=>l.textContent.replace(/\s+/g,' ').slice(0,55)).join(' || ')));
 await p.check('#cAsp'); await p.check('#cInat'); await p.waitForTimeout(2500);
 console.log('Hang an:', await p.evaluate(()=>map.hasLayer(aspLayer)+" Kacheln "+Object.keys(aspLayer._tiles||{}).length+" / iNat: "+document.getElementById('inatNote').textContent.slice(0,60)));
 await p.evaluate(()=>{ const ll=L.latLng(49.31,13.32); showPoint(ll,findLayerAt(ll)); return 1}); await p.waitForFunction(()=>document.getElementById('ptPilz'),null,{timeout:20000});
 await p.evaluate(()=>{ const d=document.getElementById('ptPilz'); d.open=true; d.dispatchEvent(new Event('toggle')); return 1}); await p.waitForTimeout(3500);
 console.log('Punkt Pilz:', await p.evaluate(()=>document.getElementById('ptPilzIn').innerText.replace(/\n+/g,' | ').slice(0,900)));
 console.log('Karte Pilzboden:', await p.evaluate(()=>document.getElementById('cardS').textContent));
 console.log('Hash:', await p.evaluate(()=>location.hash));
 await p.screenshot({path:'test/pilz_cz.png'}); console.log('Fehler',errs); await b.close(); })();
