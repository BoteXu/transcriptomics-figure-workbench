import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
export async function checkGallery(folder,output){
 await fs.mkdir(output,{recursive:false});const base=path.resolve('skills/transcriptomics-figure-workbench/assets',folder);
 const m=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
 const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
 const options={headless:true};if(process.platform==='win32')options.channel='msedge';const browser=await chromium.launch(options);
 try{
  const p=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],external=[];p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():(external.push(r.request().url()),r.abort()));
  const url=pathToFileURL(path.join(base,'index.html')).href;
  await p.goto(url);await p.selectOption('#browseMode','forms');await p.selectOption('#chapter','');await p.locator('#variants').check();
  assert.equal(await p.locator('#menu button').count(),m.forms.navigation_entries);
  assert.ok(m.forms.navigation_entries<m.records.length);
  for(const row of m.records){
   await p.evaluate(id=>{location.hash=encodeURIComponent(id)},row.id);
   await p.waitForFunction(src=>document.querySelector('#art').getAttribute('src')===src,row.assets.png);
   await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#edition').inputValue(),row.id);
   assert.equal(await p.locator('#links a').count(),5);assert.ok((await p.locator('#definition').textContent()).length>15);
   if(row.before_png){await p.locator('#compare').click();await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#art').getAttribute('src'),row.before_png);await p.locator('#compare').click()}
  }
  // Numeric legacy fragments remain aliases after the routine reader rebuild.
  if(folder==='routine-gallery'){await p.goto(url+'#11');await p.reload();await p.locator('#art').evaluate(im=>im.decode());assert.equal(await p.locator('#edition').inputValue(),m.records[10].id)}
  await p.screenshot({path:path.join(output,'desktop.png'),fullPage:true});await p.setViewportSize({width:390,height:844});
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.locator('#zoom').click();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const result={state:'ALL_SCOPED_GALLERY_SOURCES_REACHABLE',gallery:folder,sources:m.records.length,form_entries:m.forms.navigation_entries,external_requests:0,aesthetic_approval:false};
  await fs.writeFile(path.join(output,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{await browser.close()}
}
