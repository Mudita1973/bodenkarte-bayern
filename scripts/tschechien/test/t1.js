const { chromium, devices } = require('playwright'); const fs=require('fs');
(async()=>{
  const b=await chromium.launch(); const errs=[], cons=[];
  const LP=fs.readFileSync('test/mock_lpis.xml','utf8'); let nL=0, nT=0, nD=0, ext=new Set();
  for(const [name,opt] of [["Desktop",{viewport:{width:1440,height:950}}],["Handy",{...devices['Pixel 7']}]]){
    const ctx=await b.newContext(opt);
    await ctx.route(/^https?:\/\/(?!localhost)/, r=>{ ext.add(new URL(r.request().url()).host); r.abort(); });
    await ctx.route(/mze\.gov\.cz/, r=>{ nL++; if(!/PROPERTYNAME=ms:GEOMETRY,ms:kultura,ms:vymera/.test(r.request().url())) errs.push("LPIS ohne PROPERTYNAME"); r.fulfill({status:200,contentType:'text/xml',body:LP,headers:{'access-control-allow-origin':'*'}}); });
    const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(name+': '+e.message)); p.on('console',m=>{ if(m.type()==='error') cons.push(name+': '+m.text().slice(0,160)); });
    p.on('request',r=>{ const u=r.url(); if(/\/lu\/.*\.bin/.test(u)) nT++; if(/\/detail\/r\d+\.json/.test(u)) nD++; });
    const t0=Date.now(); await p.goto('http://localhost:8766/'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000});
    console.log(name,'geladen in',Date.now()-t0,'ms', await p.evaluate(()=>({keys:D.keys.length,kreise:D.kreise.length,small:D.small.length,leg:document.querySelectorAll('#legend li').length,center:map.getCenter(),zoom:map.getZoom()})));
    await p.screenshot({path:`test/ov_${name}.png`});
    // Punkt bei Klatovy
    await p.evaluate(()=>{ map.setView([49.40,13.30],12,{animate:false}); return 1}); await p.waitForTimeout(2500);
    await p.evaluate(()=>{ const ll=L.latLng(49.405,13.27); showPoint(ll,findLayerAt(ll)); return 1}); await p.waitForTimeout(800);
    console.log(name,'Punkt:',await p.evaluate(()=>document.getElementById('point').innerText.slice(0,700).replace(/\n+/g,' | ')));
    console.log(name,'Detail aktiv:',await p.evaluate(()=>({det:detailActive(),n:detLayers().length})));
    await p.screenshot({path:`test/z12_${name}.png`});
    // Nutzung
    await p.click('#luTog'); await p.waitForTimeout(300);
    await p.click('#luPanel .pre button[data-p="gruen"]'); await p.waitForTimeout(800);
    await p.evaluate(()=>{ map.setView([49.31,13.32],14,{animate:false}); return 1}); await p.waitForTimeout(4000);
    console.log(name,'z14:',await p.evaluate(()=>({shown:luvShown(),vf:VF.size,st:vecState(),pc:Object.fromEntries(["a","ak","sk","g","gs","w","wm","s","o"].map(k=>[k,(document.getElementById('pc_'+k)||{}).textContent])),basis:document.getElementById('luBasis').textContent,src:document.getElementById('luSrc').textContent})));
    await p.screenshot({path:`test/z14_${name}.png`});
    await p.click('#luPanel .pre button[data-p="alle"]'); await p.waitForTimeout(300);
    await p.evaluate(()=>{ S.lu=new Set(["gs"]); S.luLayer=false; S.luMask=true; syncLuMode(); buildLuBoxes(); restyle(); return 1}); await p.waitForTimeout(1200);
    await p.screenshot({path:`test/maskgs_${name}.png`});
    const px=await p.evaluate(()=>{ const c=document.querySelector('canvas.luvec'), x=c.getContext('2d'), r=c.getBoundingClientRect(), mr=document.getElementById('map').getBoundingClientRect();
      const res={ttp:0,ttpClear:0,other:0,otherCov:0};
      const sz=map.getSize();
      for(let i=0;i<40;i++) for(let j=0;j<40;j++){ const cp=L.point(sz.x*(i+0.5)/40, sz.y*(j+0.5)/40), ll=map.containerPointToLatLng(cp);
        const f=vecAt(ll,"i")||vecAt(ll,"a"); const X=(cp.x+mr.left-r.left)*luvLayer._dpr, Y=(cp.y+mr.top-r.top)*luvLayer._dpr, a=x.getImageData(Math.round(X),Math.round(Y),1,1).data[3];
        if(f&&f.sub==="gs"){ res.ttp++; if(a<20) res.ttpClear++; } else { res.other++; if(a>150) res.otherCov++; } }
      return res; });
    console.log(name,'Maske Dauergrünland (Stichprobe 1600 Punkte):',JSON.stringify(px));
    await p.evaluate(()=>{ const ll=L.latLng(49.31,13.32); showPoint(ll,findLayerAt(ll)); return 1}); await p.waitForTimeout(1500);
    console.log(name,'Punkt Nutzung:',await p.evaluate(()=>(document.getElementById('ptLu')||{}).textContent));
    // Statistik
    await p.evaluate(()=>{ document.getElementById('stCls').value="13"; document.getElementById('stCls').dispatchEvent(new Event('change')); return 1});
    console.log(name,'Statistik:',await p.evaluate(()=>[...document.querySelectorAll('#stTable .it')].slice(0,4).map(e=>e.textContent.replace(/\s+/g,' ')).join(' || ')+' … '+document.querySelectorAll('#stTable .it').length+' Zeilen'));
    console.log(name,'Hash:',await p.evaluate(()=>location.hash));
    await ctx.close();
  }
  console.log('Anfragen LPIS',nL,'LU-Kacheln',nT,'Detail',nD,'extern blockiert',[...ext].join(','));
  console.log('Fehler',errs); console.log('Konsole',cons.slice(0,8)); await b.close();
})();
