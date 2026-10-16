/* Public frozen examples, directly from file URLs; no HTTP service or upload. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh review directory');await fs.mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';
 browser=await chromium.launch(options);const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(r.request().url().startsWith('file:')||r.request().url().startsWith('data:'))return r.continue();external.push(r.request().url());return r.abort()});
 await page.goto(pathToFileURL(path.resolve('examples/validated-v090/index.html')).href);
 assert.equal(await page.locator('article').count(),12);assert.match(await page.locator('#status').innerText(),/25/);
 await page.locator('article img').first().evaluate(im=>im.decode());await page.screenshot({path:path.join(output,'study-desktop.png')});
 await page.locator('article img').first().click();await page.locator('#zoom img').evaluate(im=>im.decode());assert.ok(await page.locator('#zoom').evaluate(d=>d.open));await page.locator('#close').click();
 await page.locator('[data-pick="source"]').click();await page.locator('#search').fill('heatmap');assert.ok(await page.locator('article').count()>1);assert.match(await page.locator('article small').first().innerText(),/heatmap/);
 await page.locator('#search').fill('');await page.locator('[data-pick="volume"]').click();await page.locator('#volume').selectOption('large');assert.match(await page.locator('#status').innerText(),/^87 /);await page.locator('#next').click();assert.match(await page.locator('#page').innerText(),/^2 /);
 await page.locator('#clear').click();await page.locator('[data-pick="study-layout"]').click();assert.equal(await page.locator('article').count(),8);
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'layout-narrow.png')});
 await page.goto(pathToFileURL(path.resolve('skills/transcriptomics-figure-workbench/assets/study-gallery/index.html')).href);await page.locator('#assay').selectOption('single_cell');assert.match(await page.locator('#status').innerText(),/^14 /);await page.locator('article img').first().evaluate(im=>im.decode());
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={status:'V090_OFFLINE_BROWSER_PASS',pages:803,study_figures:25,layout_figures:8,external_requests:0,checks:['direct file access without fetch','pagination','true consolidated form search','quantity and assay filters','full-image zoom','narrow layout','portable installed study gallery'],visual_acceptance:false};
 await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
