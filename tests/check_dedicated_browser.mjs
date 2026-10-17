/* Dedicated offline galleries use actual portable inputs and original pixels. */
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
 for(const [folder,count] of [['subgroup',8],['wgcna',14],['method-depth',16],['chapter-layouts',45]]){
  const root=path.resolve('skills/transcriptomics-figure-workbench/assets/'+folder+'-gallery');
  await page.goto(pathToFileURL(path.join(root,'index.html')).href);assert.match(await page.locator('#count').innerText(),new RegExp('^'+count));
  await page.locator('article img').first().evaluate(im=>im.decode());await page.locator('article img').first().click();await page.locator('#large').evaluate(im=>im.decode());assert.ok(await page.locator('#zoom').evaluate(x=>x.open));await page.locator('#close').click();
  const m=JSON.parse(await fs.readFile(path.join(root,'manifest.json'),'utf8'));const first=m.records[0];
  for(const [kind,file] of Object.entries(first.assets)){assert.ok((await fs.stat(path.join(root,file))).isFile(),kind+' missing')}
  await page.locator('#next').click();assert.match(await page.locator('#count').innerText(),/第2页/);
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,folder+'-mobile.png')});await page.setViewportSize({width:1440,height:1000});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={status:'DEDICATED_GALLERIES_BROWSER_PASS',galleries:4,external_requests:0,checks:['real image decode and zoom','exact portable assets','pagination','narrow screen']};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
