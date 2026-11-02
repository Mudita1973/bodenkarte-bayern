const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1300,height:900}}); const errs=[];
  await ctx.route(/^https?:\/\//, r=>r.abort());
  const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message));
  const t0=Date.now(); await p.goto('file:///home/claude/cz/bodenkarte_westboehmen_detail.html'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:180000});
  console.log('geladen',Date.now()-t0,'ms');
  await p.evaluate(()=>{ S.luLayer=true; syncLuMode(); restyle(); map.setView([49.02,13.62],13,{animate:false}); return 1}); await p.waitForTimeout(3000);
  console.log(await p.evaluate(()=>({det:detailActive(),detN:detLayers().length,shown:luvShown(),st:vecState(),vf:VF.size,src:document.getElementById('luSrc').textContent.slice(0,80)})));
  await p.screenshot({path:'test/file_sumava.png'}); console.log('Fehler',errs); await b.close(); })();
