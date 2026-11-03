const { chromium, devices } = require('playwright'); const fs=require('fs');
(async()=>{
  const b=await chromium.launch(); const errs=[], cons=[];
  const LC=fs.readFileSync('test/mock_lc.xml','utf8'), FI=fs.readFileSync('test/mock_fiona.xml','utf8'); let nA=0,nI=0,nD=0, ext=new Set();
  for(const [name,opt] of [["Desktop",{viewport:{width:1440,height:950}}],["Handy",{...devices['Pixel 7']}]]){
    const ctx=await b.newContext(opt);
    await ctx.route(/^https?:\/\/(?!localhost)/, r=>{ ext.add(new URL(r.request().url()).host); r.abort(); });
    await ctx.route(/Bodenbedeckung_ATKIS/, r=>{ nA++; r.fulfill({status:200,contentType:'text/xml',body:LC,headers:{'access-control-allow-origin':'*'}}); });
    await ctx.route(/FIONA/, r=>{ nI++; r.fulfill({status:200,contentType:'text/xml',body:FI,headers:{'access-control-allow-origin':'*'}}); });
    const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(name+': '+e.message)); p.on('console',m=>{ if(m.type()==='error') cons.push(name+': '+m.text().slice(0,160)); });
    p.on('request',r=>{ if(/\/detail\/r\d+\.json/.test(r.url())) nD++; });
    const t0=Date.now(); await p.goto('http://localhost:8767/'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000});
    console.log(name,'geladen in',Date.now()-t0,'ms', await p.evaluate(()=>({keys:D.keys.length,kreise:D.kreise.length,small:D.small.length,leg:document.querySelectorAll('#legend li').length,center:map.getCenter(),zoom:map.getZoom(),reg:typeof Object.values(D.units)[0].p.saeure.regel})));
    await p.screenshot({path:`test/ov_${name}.png`});
    // Punkt am Schauinsland
    await p.evaluate(()=>{ map.setView([47.91,7.90],12,{animate:false}); return 1}); await p.waitForTimeout(3000);
    await p.evaluate(()=>{ const ll=L.latLng(47.912,7.905); showPoint(ll,findLayerAt(ll)); return 1}); await p.waitForTimeout(900);
    console.log(name,'Punkt:',await p.evaluate(()=>document.getElementById('point').innerText.slice(0,1800).replace(/\n+/g,' | ')));
    console.log(name,'Links:',await p.evaluate(()=>[...document.querySelectorAll('#point .links a')].map(a=>a.textContent+' '+a.href).join(' ; ')));
    console.log(name,'Detail aktiv:',await p.evaluate(()=>({det:detailActive(),n:detLayers().length})));
    await p.screenshot({path:`test/z12_${name}.png`});
    // Nutzung (Kraichgau, Mock)
    await p.click('#luTog'); await p.waitForTimeout(300);
    await p.evaluate(()=>{ map.setView([49.2079,8.7419],14,{animate:false}); return 1}); await p.waitForTimeout(800);
    await p.click('#luPanel .pre button[data-p="alle"]'); await p.waitForTimeout(300);
    await p.evaluate(()=>{ S.luLayer=true; S.luMask=false; syncLuMode(); buildLuBoxes(); restyle(); vecUpdate(); return 1}); await p.waitForTimeout(5000);
    console.log(name,'z14:',await p.evaluate(()=>{ const c={}; for(const f of VF.values()) c[f.src+":"+f.sub]=(c[f.src+":"+f.sub]||0)+1; return {shown:luvShown(),vf:VF.size,c,st:vecState(),pc:Object.fromEntries(["ak","sk","gw","gm","gp","gs","wl","wn","wm","wg","ss"].map(k=>[k,(document.getElementById('pc_'+k)||{}).textContent])),basis:document.getElementById('luBasis').textContent,src:document.getElementById('luSrc').textContent}; }));
    await p.screenshot({path:`test/z14_${name}.png`});
    await p.evaluate(()=>{ const ll=L.latLng(49.2079,8.7419); showPoint(ll,findLayerAt(ll)); return 1}); await p.waitForTimeout(1500);
    console.log(name,'Punkt Nutzung:',await p.evaluate(()=>(document.getElementById('ptLu')||{}).textContent));
    // Statistik
    await p.evaluate(()=>{ document.getElementById('stCls').value="13"; document.getElementById('stCls').dispatchEvent(new Event('change')); return 1});
    console.log(name,'Statistik:',await p.evaluate(()=>[...document.querySelectorAll('#stTable .it')].slice(0,4).map(e=>e.textContent.replace(/\s+/g,' ')).join(' || ')+' … '+document.querySelectorAll('#stTable .it').length+' Zeilen'));
    console.log(name,'Nachbar:',await p.evaluate(()=>{ otherLink(); return document.getElementById('otherMap').href; }));
    console.log(name,'Speicher MB:',await p.evaluate(()=>performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):null));
    await ctx.close();
  }
  console.log('Anfragen ATKIS',nA,'FIONA',nI,'Detail',nD,'extern blockiert',[...ext].join(','));
  console.log('Fehler',errs); console.log('Konsole',cons.slice(0,8)); await b.close();
})();
