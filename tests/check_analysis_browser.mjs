/* Actual offline pages, all image decodes, chapter routing and responsive controls. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh output');await fs.mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';browser=await chromium.launch(options);
 const p=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],external=[];
 p.on('pageerror',e=>errors.push(e.message));await p.route('**/*',r=>{if(/^(file:|data:)/.test(r.request().url()))return r.continue();external.push(r.request().url());return r.abort()});
 let total=0;
 for(const folder of ['analysis-gallery','analysis-library']){
  await p.goto(pathToFileURL(path.resolve('skills/transcriptomics-figure-workbench/assets',folder,'index.html')).href);
  await p.selectOption('#chapter','');await p.locator('#variants').check();const buttons=p.locator('#menu button'),count=await buttons.count();
  if(folder==='analysis-gallery')assert.equal(count,43);else assert.ok(count>100);
  for(let i=0;i<count;i++){
   await buttons.nth(i).click();await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#counter').textContent(),`${i+1} / ${count}`);
   assert.equal(await p.locator('#links a').count(),5);assert.ok((await p.locator('#definition').textContent()).length>20);
  }
  total+=count;
 }
 await p.locator('#variants').uncheck();await p.selectOption('#chapter','bulk.wgcna');assert.ok(await p.locator('#menu button').count()>=20);
 await p.locator('#menu button').filter({hasText:'Topological overlap with frozen'}).click();await p.locator('#art').evaluate(im=>im.decode());await p.screenshot({path:path.join(output,'wgcna-desktop.png'),fullPage:true});
 await p.locator('#zoom').click();assert.equal(await p.locator('#art').evaluate(im=>im.classList.contains('native')),true);await p.locator('#zoom').click();
 const before=await p.locator('#counter').textContent();await p.keyboard.press('ArrowRight');assert.notEqual(await p.locator('#counter').textContent(),before);await p.locator('#prev').click();assert.equal(await p.locator('#counter').textContent(),before);
 await p.locator('#search').fill('剪接');assert.ok(await p.locator('#menu button').count()>0);assert.equal(await p.locator('#chapter').inputValue(),'');
 await p.locator('#search').fill('no-such-analysis');assert.equal(await p.locator('#empty').isVisible(),true);
 await p.selectOption('#chapter','single_cell.hdwgcna');await p.locator('#art').evaluate(im=>im.decode());
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Narrow viewport overflow');await p.screenshot({path:path.join(output,'hdwgcna-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={state:'ANALYSIS_BROWSER_PASS',images_decoded:total,analysis_chapters:58,offline:true,external_requests:0,narrow_overflow:false,aesthetic_approval:false};await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
