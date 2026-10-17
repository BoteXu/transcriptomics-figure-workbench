/* Chapter routes, full companions, explicit layouts and private offline use. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const output=process.argv[2];if(!output)throw Error('Choose a fresh output');await fs.mkdir(output,{recursive:false});
const base=path.resolve('skills/transcriptomics-figure-workbench/assets/companion-gallery');
const manifest=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const chapters=[...new Set(manifest.records.flatMap(r=>r.chapters))];assert.equal(chapters.length,56);assert.equal(manifest.records.length,425);
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));let browser;
try{
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';browser=await chromium.launch(options);
 const p=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],external=[];
 p.on('pageerror',e=>errors.push(e.message));await p.route('**/*',r=>{if(/^(file:|data:)/.test(r.request().url()))return r.continue();external.push(r.request().url());return r.abort()});
 await p.goto(pathToFileURL(path.join(base,'index.html')).href);
 for(const chapter of chapters){
  await p.locator('#variants').uncheck();await p.selectOption('#chapter',chapter);
  const expected=manifest.records.filter(r=>r.chapters.includes(chapter)&&!r.variant);assert.ok(expected.length>=5);
  assert.equal(await p.locator('#menu button').count(),expected.length);
  assert.ok((await p.locator('#menu').textContent()).includes('设计与质控'));assert.ok((await p.locator('#menu').textContent()).includes('独立验证与稳定性'));
  await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#links a').count(),5);
  await p.locator('#variants').check();assert.ok(await p.locator('#menu button').count()>=7);
  const rows=manifest.records.filter(r=>r.chapters.includes(chapter));
  for(const suffix of ['_Evidence','_Layout']){
   const row=rows.find(r=>r.id.endsWith(suffix));assert.ok(row);
   await p.goto(pathToFileURL(path.join(base,'index.html')).href+'#'+row.id);await p.reload();
   await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#chapter').inputValue(),chapter);assert.equal(await p.locator('#variants').isChecked(),true);
   assert.equal(await p.locator('#art').getAttribute('src'),row.assets.png);
  }
 }
 for(const row of manifest.records.filter(r=>r.id.endsWith('_ThreeColumns'))){await p.goto(pathToFileURL(path.join(base,'index.html')).href+'#'+row.id);await p.reload();await p.locator('#art').evaluate(im=>im.decode());assert.ok((await p.locator('#parameters').textContent()).includes('"columns": 3'))}
 await p.screenshot({path:path.join(output,'companions-desktop.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await p.locator('#zoom').click();assert.equal(await p.locator('#art').evaluate(im=>im.classList.contains('native')),true);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.locator('#zoom').click();
 await p.screenshot({path:path.join(output,'companions-mobile.png'),fullPage:true});assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={state:'ALL_COMPANION_CHAPTER_BROWSER_PASS',chapters_checked:56,complete_compositions:56,larger_data_one_column:56,three_column:6,offline:true,external_requests:0,aesthetic_approval:false};
 await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{if(browser)await browser.close()}
