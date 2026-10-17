/* Offline installed/public chapter galleries; no upload or external requests. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh test directory');await fs.mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';browser=await chromium.launch(options);
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(r.request().url().startsWith('file:')||r.request().url().startsWith('data:'))return r.continue();external.push(r.request().url());return r.abort()});
 for(const root of ['examples/chapters-v091','skills/transcriptomics-figure-workbench/assets/chapter-gallery']){
  await page.goto(pathToFileURL(path.resolve(root,'index.html')).href);assert.equal(await page.locator('article').count(),4);assert.match(await page.locator('#count').innerText(),/^58/);
  await page.locator('article img').first().evaluate(im=>im.decode());await page.locator('article img').first().click();await page.locator('#large').evaluate(im=>im.decode());assert.ok(await page.locator('#zoom').evaluate(x=>x.open));await page.locator('#close').click();
  await page.locator('#assay').selectOption('single_cell');assert.match(await page.locator('#count').innerText(),/^30/);await page.locator('#q').fill('communication');assert.equal(await page.locator('article').count(),1);await page.locator('article img').evaluate(im=>im.decode());
  await page.locator('#q').fill('');await page.locator('#assay').selectOption('');await page.locator('#next').click();assert.match(await page.locator('#count').innerText(),/第2页/);
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,root.startsWith('examples')?'public-mobile.png':'installed-mobile.png')});await page.setViewportSize({width:1440,height:1050});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={status:'CHAPTER_BROWSER_PASS',chapters:58,external_requests:0,checks:['offline file access','pagination','assay and method search','full-pixel zoom','portable installed assets','narrow screen']};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
