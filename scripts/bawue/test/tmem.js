const { chromium, devices } = require('playwright');
(async()=>{ const b=await chromium.launch();
  for(const [name,opt] of [["Handy",{...devices['Pixel 7']}],["Desktop",{viewport:{width:1440,height:950}}]]){
  const ctx=await b.newContext(opt); await ctx.route(/^https?:\/\/(?!localhost)/, r=>r.abort());
  const p=await ctx.newPage(); const cdp=await ctx.newCDPSession(p); await cdp.send('HeapProfiler.enable');
  const mem=async l=>{ await cdp.send('HeapProfiler.collectGarbage'); await p.waitForTimeout(300); console.log(name,l, Math.round((await cdp.send('Runtime.getHeapUsage')).usedSize/1e6),'MB'); };
  await p.goto('http://localhost:8767/'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000}); await p.waitForTimeout(1500); await mem('Übersicht');
  for(const [z,la,lo] of [[10,48.3,8.6],[12,47.91,7.90],[13,48.0,7.95],[8,48.6,9.0]]){ await p.evaluate(([z,la,lo])=>{ map.setView([la,lo],z,{animate:false}); return 1},[z,la,lo]); await p.waitForTimeout(5000); await mem('Zoom '+z); }
  await ctx.close(); }
  await b.close(); })();
