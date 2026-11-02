const { chromium, devices } = require('playwright'); const fs=require('fs');
const LP=fs.readFileSync('test/mock_lpis.xml','utf8');
(async()=>{ const b=await chromium.launch(); const errs=[];
  const mk=async(opt)=>{ const ctx=await b.newContext(opt||{viewport:{width:1440,height:950}}); await ctx.route(/^https?:\/\/(?!localhost)/,r=>r.abort());
    await ctx.route(/mze\.gov\.cz/,async r=>{ await new Promise(z=>setTimeout(z,1500)); r.fulfill({status:200,contentType:'text/xml',body:LP,headers:{'access-control-allow-origin':'*'}}).catch(()=>{}); });
    const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message)); return [ctx,p]; };
  const ready=p=>p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000});
  // 1) Zoom 14 -> 11 -> 14 (früher hängend), beide Karten
  for(const [port,ll] of [[8766,[49.31,13.32]],[8765,[49.60,10.95]]]){ const [ctx,p]=await mk(); await p.goto(`http://localhost:${port}/#c=${ll[0]}%2C${ll[1]}&z=14&s=6.13.16&m=z&ll=1`); await ready(p);
    await p.waitForTimeout(150); await p.evaluate(()=>{ map.setZoom(11,{animate:false}); return 1}); await p.waitForTimeout(300); await p.evaluate(()=>{ map.setZoom(14,{animate:false}); return 1});
    await p.waitForTimeout(port===8766?7000:9000);
    console.log(port,'Zoom 14-11-14:',JSON.stringify(await p.evaluate(()=>({st:vecState(),q:vecQ.length,wait:[...VT.a.values(),...VT.i.values()].filter(t=>t.st==="wait").length}))));
    await ctx.close(); }
  // 2) Maske an der Grenze (CZ)
  { const [ctx,p]=await mk(); await p.goto('http://localhost:8766/#c=50.09%2C12.17&z=13&s=6.13.16&m=z&l=gs&lm=1'); await ready(p); await p.waitForTimeout(5000);
    const r=await p.evaluate(()=>{ const c=document.querySelector('canvas.luvec'), x=c.getContext('2d'), rr=c.getBoundingClientRect(), mr=document.getElementById('map').getBoundingClientRect(), sz=map.getSize(); let inC=0,inMask=0,outC=0,outMask=0;
      const reg=D.region.map(r=>{ const a=[]; for(let j=0;j<r.length;j+=2) a.push(utmToLatLng(r[j],r[j+1])); return a; });
      const inside=ll=>{ let c2=false; for(const ring of reg) for(let i=0,j=ring.length-1;i<ring.length;j=i++){ const A=ring[i],B=ring[j]; if(((A[0]>ll.lat)!==(B[0]>ll.lat))&&(ll.lng<(B[1]-A[1])*(ll.lat-A[0])/(B[0]-A[0])+A[1])) c2=!c2; } return c2; };
      for(let i=0;i<40;i++) for(let j=0;j<40;j++){ const cp=L.point(sz.x*(i+.5)/40,sz.y*(j+.5)/40), ll=map.containerPointToLatLng(cp); const a=x.getImageData(Math.round((cp.x+mr.left-rr.left)*luvLayer._dpr),Math.round((cp.y+mr.top-rr.top)*luvLayer._dpr),1,1).data[3];
        if(inside(ll)){ inC++; if(a>150) inMask++; } else { outC++; if(a>20) outMask++; } }
      return {shown:luvShown(),innen:inC,innenAbgedeckt:inMask,aussen:outC,aussenBemalt:outMask}; });
    console.log('Grenze Maske:',JSON.stringify(r)); await p.screenshot({path:'test/border_mask_neu.png'}); await ctx.close(); }
  // 3) Link-Übersetzung der Nutzung
  for(const [port,h] of [[8766,"#c=49.31%2C13.32&z=12&s=6.13&m=z&l=gs.wm&lm=1"],[8765,"#c=49.60%2C12.40&z=12&s=6.13&m=z&l=gw.gp.wl&lm=1"],[8765,"#c=48.14%2C11.58&z=11&s=6.13&m=z"]]){ const [ctx,p]=await mk(); await p.goto(`http://localhost:${port}/${h}`); await ready(p); await p.waitForTimeout(800);
    console.log(port,'Link:',await p.evaluate(()=>{const e=document.getElementById('otherMap');return e.textContent+' -> '+e.href.split('#')[1];})); await ctx.close(); }
  // 4) Pilz-Hash in CZ
  { const [ctx,p]=await mk(); await p.goto('http://localhost:8766/#c=49.31%2C13.32&z=11&s=6&m=z&pz=sauer.wasser&pa=1&pt=1&pi=1&u=190'); await ready(p); await p.waitForTimeout(800);
    console.log('CZ Pilz-Hash:',await p.evaluate(()=>({pz:S.pz,units:S.units,asp:S.asp,tree:S.tree,leg:document.querySelectorAll('#legend li').length}))); await ctx.close(); }
  // 5) Beschriftungen ohne Überlappung + Handy-Quellenzeile
  for(const port of [8765,8766]){ const [ctx,p]=await mk({...devices['Pixel 7']}); await p.goto(`http://localhost:${port}/`); await ready(p); await p.waitForTimeout(800);
    console.log(port,'Labels:',await p.evaluate(()=>{ const els=[...document.querySelectorAll('.lbl')].filter(e=>getComputedStyle(e.parentElement).visibility!=="hidden"&&getComputedStyle(e.parentElement).display!=="none"); const R=els.map(e=>e.getBoundingClientRect()); let ov=0; for(let i=0;i<R.length;i++) for(let j=i+1;j<R.length;j++){ const a=R[i],c=R[j]; if(a.left<c.right&&a.right>c.left&&a.top<c.bottom&&a.bottom>c.top) ov++; } const att=document.querySelector('.leaflet-control-attribution'); return {sichtbar:els.length,ueberlappend:ov,quellenHoehe:Math.round(att.getBoundingClientRect().height)}; }));
    await p.screenshot({path:`test/mob_${port}.png`}); await ctx.close(); }
  console.log('Fehler',errs); await b.close(); })();
