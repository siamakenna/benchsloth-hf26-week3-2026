const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
 const root=path.resolve(__dirname,'..');const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:root+'/assets/recordings',size:{width:1440,height:1000}}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const input='1. Wait for 5 minutes.\n2. Incubate overnight.\n3. Record the example identifier.';
 await page.goto('http://127.0.0.1:8766');await page.waitForFunction(()=>document.querySelector('#modelStatus').textContent.includes('ready'));await page.waitForTimeout(3000);await page.locator('#protocol').fill(input);await page.waitForTimeout(5000);
 const started=Date.now();const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/parse'),{timeout:150000});await page.locator('#parseBtn').click();const response=await responsePromise;const result=await response.json();const seconds=(Date.now()-started)/1000;
 fs.writeFileSync(root+'/evaluation/live-ui.json',JSON.stringify({input,endpoint:'/api/parse',status:response.status(),result,observed_seconds:seconds,errors,recording:'Unmodified browser capture. No mocked requests, no acceleration.'},null,2));
 if(!response.ok())throw Error('Live parse failed '+JSON.stringify(result));await page.waitForSelector('.step');await page.screenshot({path:root+'/assets/desktop-live-gemma.png',fullPage:true});await page.waitForTimeout(6000);
 await page.getByRole('button',{name:'Source line 2',exact:false}).click();await page.waitForTimeout(5000);await page.getByRole('button',{name:'Timer',exact:false}).filter({hasText:'Timer'}).first().click();await page.waitForTimeout(1000);await page.screenshot({path:root+'/assets/hands-off-live-gemma.png'});await page.waitForTimeout(10000);await page.keyboard.press('Escape');await page.waitForTimeout(2000);await page.locator('#timerCancel').click();await page.waitForTimeout(2000);
 // Keep the authentic sequence at real speed. Hold on the result to reach ~70s.
 const elapsed=(Date.now()-started)/1000;await page.waitForTimeout(Math.max(0,70000-elapsed*1000));
 const video=page.video();await context.close();await video.saveAs(root+'/assets/live-gemma-demo.webm');await browser.close();console.log(JSON.stringify({inference_seconds:seconds,windows:result.rest_windows,review:result.review_needed,video:root+'/assets/live-gemma-demo.webm'}));
})().catch(e=>{console.error(e);process.exit(1)});
