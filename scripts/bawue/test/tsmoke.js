const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch();
 for(const port of [8765,8766,8767]){ const ctx=await b.newContext({viewport:{width:1300,height:900}}); await ctx.route(/^https?:\/\/(?!localhost)/, r=>r.abort());
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:'+port+'/'); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000});
  await p.evaluate(()=>{ map.setView([48.9,10.2],9,{animate:false}); return 1}); await p.waitForTimeout(1500);
  const r=await p.evaluate(()=>{ otherLink(); return [...document.querySelectorAll('[id^=otherMap]')].map(a=>a.textContent+' -> '+a.href); });
  const w=await p.evaluate(()=>{ const leg=Object.keys(D.units).find(l=>pzMatch({leg:l},"wasser")); return leg? wetterText({p7:2,p30:20,dry:3,n7:1,tmax:18,tmin:8,frost:0,smNow:null,smWeek:null},leg).match(/Feldkapazität [^)]*/)?.[0]||"(kein nfk-Text)":"keine Wasser-Einheit"; });
  console.log(port,JSON.stringify(r),'|',w,'| Fehler',errs); await ctx.close(); }
 await b.close(); })();
