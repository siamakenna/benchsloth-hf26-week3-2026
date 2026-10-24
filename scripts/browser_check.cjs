const {chromium}=require('playwright');
const fs=require('fs');const path=require('path');
(async()=>{
 const root=path.resolve(__dirname,'..'),browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1050}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const checks=[];
 function assert(ok,name){if(!ok)throw Error(name);checks.push(name)}
 await page.goto('http://127.0.0.1:8765');await page.getByRole('button',{name:'Load sample bench run'}).click();await page.waitForSelector('.step');
 assert(await page.locator('.step').count()===10,'prepared ten lines');assert((await page.locator('#modeLabel').innerText()).includes('NO AI'),'honest prepared label');
 await page.screenshot({path:root+'/assets/desktop-prepared.png',fullPage:true});
 await page.getByRole('button',{name:'Source line 3',exact:false}).click();assert(await page.locator('#protocol').evaluate(n=>n.value.slice(n.selectionStart,n.selectionEnd).includes('20 minutes')),'source navigation highlights correct original');
 await page.getByRole('button',{name:'Demo 10s',exact:false}).first().click();assert(await page.locator('#breakOverlay').isVisible(),'rest view opens');await page.screenshot({path:root+'/assets/hands-off-prepared.png'});
 await page.waitForTimeout(10800);assert((await page.locator('#breakMessage').innerText()).includes('Demonstration finished'),'demo timer expires by elapsed wall time');await page.keyboard.press('Escape');assert(await page.locator('#breakOverlay').isHidden(),'escape closes dialog');
 await page.locator('#timerCancel').click();assert(await page.locator('#timerCard').isHidden(),'timer cancellation');
 await page.locator('#protocol').fill('Different notes: do not incubate for 10 min.');assert(await page.locator('.step').count()===0,'editing invalidates output');assert(await page.locator('#printBtn').isDisabled(),'editing disables stale print');
 // Delayed inference cannot overwrite newer input.
 let release;await page.route('**/api/parse',async route=>{await new Promise(r=>release=r);await route.fulfill({json:{steps:[],rest_windows:0,documented_rest_minutes:0,review_needed:0,mode:'inference',engine:'TEST RESPONSE',wall_seconds:1}})});
 await page.locator('#parseBtn').click();await page.waitForTimeout(100);await page.locator('#protocol').fill('Changed while inference was pending.');release();await page.waitForTimeout(250);assert(await page.locator('.step').count()===0,'late response discarded');await page.unroute('**/api/parse');
 await page.route('**/api/parse',r=>r.fulfill({status:503,json:{detail:'Local model unavailable (browser test fixture)'}}));await page.locator('#parseBtn').click();await page.waitForSelector('#error:not(.hidden)');assert((await page.locator('#error').innerText()).includes('unavailable'),'missing model has recoverable error');await page.unroute('**/api/parse');
 await page.locator('#protocol').fill('<script>alert(1)</script> & adversarial notes');assert(await page.locator('#protocol').inputValue()==='<script>alert(1)</script> & adversarial notes','adverse input remains text');
 await page.locator('#sampleBtn').click();await page.waitForSelector('.step');await page.locator('#printBtn').evaluate(n=>{window.print=()=>{};n.click()});await page.pdf({path:root+'/assets/bench-card.pdf',format:'A4',printBackground:true});assert((await page.locator('#printPage').innerText()).includes('Prepared sample'),'print retains provenance');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:root+'/assets/mobile-prepared.png',fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile has no horizontal overflow');
 await page.reload();assert(await page.locator('.step').count()===0,'reload clears plan and timers');
 await page.goto('file://'+root+'/demo/index.html');await page.locator('#sampleBtn').click();await page.waitForSelector('.step');assert(await page.locator('#parseBtn').isDisabled(),'static replay disables live AI');assert(await page.locator('#replayBanner').isVisible(),'static replay visible provenance');assert(await page.locator('.step').count()===10,'standalone replay needs no server');
 assert(errors.length===0,'no browser script errors');fs.writeFileSync(root+'/evaluation/browser-check.json',JSON.stringify({browser:await browser.version(),checks,errors,notes:'Mock response tests explicitly labeled; screenshots use hand-prepared example. No live inference asserted here.'},null,2));await browser.close();console.log(JSON.stringify({passed:checks.length,errors}));
})().catch(e=>{console.error(e);process.exit(1)});
