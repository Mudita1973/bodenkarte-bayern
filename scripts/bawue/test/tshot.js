const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1300,height:900}}); await ctx.route(/^https?:\/\/(?!localhost)/, r=>r.abort());
  const p=await ctx.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('http://localhost:8767/'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000}); await p.waitForTimeout(2000);
  await p.screenshot({path:'test/s_ov.png'});
  await p.evaluate(()=>{ map.setView([47.95,8.0],10,{animate:false}); return 1}); await p.waitForTimeout(4000); await p.screenshot({path:'test/s_z10.png'});
  await b.close(); })();
