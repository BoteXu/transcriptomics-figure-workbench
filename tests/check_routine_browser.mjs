/* Decode every final image and exercise actual ordinary-set navigation. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh output');await fs.mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';browser=await chromium.launch(options);
 const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(/^(file:|data:)/.test(r.request().url()))return r.continue();external.push(r.request().url());return r.abort()});
 await page.goto(pathToFileURL(path.resolve('skills/transcriptomics-figure-workbench/assets/routine-gallery/index.html')).href);
 const buttons=page.locator('#menu button');assert.equal(await buttons.count(),43);
 for(let i=0;i<43;i++){
  await buttons.nth(i).click();await page.locator('#art').evaluate(async im=>{await im.decode();if(!im.naturalWidth)throw Error('Empty image')});
  assert.equal(await page.locator('#counter').textContent(),(i+1)+' / 43');assert.equal(await page.locator('#links a').count(),5);
  assert.ok((await page.locator('#notes').textContent()).length>15);
  if(await page.locator('#compare').count()){
   const current=await page.locator('#art').getAttribute('src');await page.locator('#compare').click();await page.locator('#art').evaluate(im=>im.decode());assert.notEqual(await page.locator('#art').getAttribute('src'),current);await page.locator('#compare').click();await page.locator('#art').evaluate(im=>im.decode());assert.equal(await page.locator('#art').getAttribute('src'),current);
  }
 }
 await buttons.nth(10).click();await page.locator('#art').evaluate(im=>im.decode());await page.screenshot({path:path.join(output,'raincloud-desktop.png'),fullPage:true});
 await page.locator('#zoom').click();assert.ok(await page.locator('#art').evaluate(im=>im.classList.contains('native')));await page.locator('#zoom').click();
 await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#counter').textContent(),'12 / 43');await page.locator('#prev').click();assert.equal(await page.locator('#counter').textContent(),'11 / 43');
 await page.setViewportSize({width:390,height:844});await page.locator('#art').evaluate(im=>im.decode());assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'narrow screen overflow');await page.screenshot({path:path.join(output,'raincloud-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={status:'ROUTINE_BROWSER_PASS',images_decoded:43,external_requests:0,navigation:true,zoom:true,narrow_overflow:false,aesthetic_approval:false};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
