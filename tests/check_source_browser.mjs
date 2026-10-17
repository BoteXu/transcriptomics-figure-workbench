/* Offline navigation and actual image decode, not an aesthetic judge. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh output');await fs.mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';browser=await chromium.launch(options);
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(/^(file:|data:)/.test(r.request().url()))return r.continue();external.push(r.request().url());return r.abort()});
 const scopes=[['examples/source-v093/single',96],['examples/source-v093/volume/small',87],['examples/source-v093/volume/medium',87],['examples/source-v093/volume/large',87],['examples/source-v093/layout',48],['skills/transcriptomics-figure-workbench/assets/source-gallery',96]];
 let decoded=0;
 for(const [folder,count] of scopes){
  await page.goto(pathToFileURL(path.resolve(folder,'index.html')).href);assert.equal(await page.locator('article').count(),count);
  decoded+=await page.locator('article img').evaluateAll(async images=>{for(const im of images){im.loading='eager';await im.decode();if(!im.naturalWidth)throw Error('Empty image')}return images.length});
  await page.locator('#search').fill('no-such-view');assert.equal(await page.locator('article:visible').count(),0);await page.locator('#search').fill('');
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'narrow screen overflow');
  await page.screenshot({path:path.join(output,folder.split('/').slice(-1)[0]+'-'+count+'.png')});await page.setViewportSize({width:1440,height:1000});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={status:'SOURCE_BROWSER_PASS',galleries:scopes.length,images_decoded:decoded,external_requests:0,aesthetic_acceptance:false};
 await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
