const { chromium, devices } = require('playwright');
(async()=>{ const b=await chromium.launch(); const errs=[];
 for(const [port,name] of [[8765,'BY'],[8766,'CZ']]) for(const dev of ['desk','mob']){
  const ctx=await b.newContext(dev==='desk'?{viewport:{width:1440,height:950},geolocation:{latitude:49.31,longitude:13.32,accuracy:18},permissions:['geolocation']}:{...devices['Pixel 7'],geolocation:{latitude:49.31,longitude:13.32,accuracy:18},permissions:['geolocation']});
  await ctx.route(/^https?:\/\/(?!localhost)/,r=>r.abort());
  const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(name+dev+': '+e.message));
  await p.goto(`http://localhost:${port}/#c=49.31%2C13.32&z=12&s=6.13.16&m=z&pz=sauer&pa=1&ll=1`); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000}); await p.waitForTimeout(1500);
  const rows=await p.evaluate(()=>[...document.querySelectorAll('.oprow')].filter(r=>getComputedStyle(r).display!=="none").map(r=>r.textContent.trim().replace(/\s+/g,' ')));
  // Schieber bewegen
  await p.evaluate(()=>{ for(const [k,v] of [["lu",0.3],["pz",0.4],["asp",0.5],["inat",0.6]]){ const i=document.querySelector(`input.opl[data-k="${k}"]`); i.value=v; i.dispatchEvent(new Event('input')); } return 1}); await p.waitForTimeout(600);
  const st=await p.evaluate(()=>({lu:map.getPane('luPane').style.opacity, asp:map.getPane('aspPane').style.opacity, inat:map.getPane('inatPane').style.opacity, pzFill:(()=>{ for(const l of allLayers()){ const c=keyCats(l.ki); if(c.length&&c.every(x=>x.startsWith('p:'))) return l.options.fillOpacity; } return null; })(), hash:location.hash.match(/oe=[^&]*/)?.[0]}));
  // Link wiederherstellen
  const h=await p.evaluate(()=>location.hash); await p.goto(`http://localhost:${port}/`+h.replace(/&p=[^&]*/,'')); await p.reload(); await p.waitForFunction(()=>!document.getElementById('loading'),null,{timeout:120000}); await p.waitForTimeout(800);
  const back=await p.evaluate(()=>({opL:S.opL, lu:map.getPane('luPane').style.opacity, label:document.getElementById('opv_lu').textContent}));
  // Standort
  await p.click('#posBtn'); await p.waitForTimeout(2000);
  const pos=await p.evaluate(()=>({an:!!POS.mk, ll:POS.mk&&POS.mk.getLatLng(), z:map.getZoom(), pressed:document.getElementById('posBtn').getAttribute('aria-pressed')}));
  await p.evaluate(()=>{ POS.mk.fire('click'); return 1}); await p.waitForTimeout(2500);
  const pt=await p.evaluate(()=>document.getElementById('point').innerText.slice(0,80).replace(/\n/g,' '));
  await p.click('#posBtn'); await p.waitForTimeout(300); const off=await p.evaluate(()=>!POS.mk);
  if(dev==='mob') await p.screenshot({path:`/home/claude/cz/test/pos_${name}.png`});
  const dl=await p.evaluate(async()=>{ let d=null; HTMLAnchorElement.prototype.click=function(){ d=this.download; }; await exportImage(); return d; });
  console.log(name,dev,JSON.stringify({rows,st,back,pos,pt,off,dl}));
  await ctx.close(); }
 console.log('Fehler',errs); await b.close(); })();
