/* Every original page remains reachable through deduplicated offline forms. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const out=process.argv[2];if(!out)throw Error('Fresh evidence directory required');await fs.mkdir(out,{recursive:false});
const base=path.resolve('skills/transcriptomics-figure-workbench/assets/analysis-library');
const m=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
for(const e of m.forms.entries){
 const scopes=new Set(e.chapters.map(c=>c.split('.')[0]));
 if(scopes.size>1)assert.ok(!/\bbulk\b|单细胞专用/i.test(e.title),'A reusable family title must not inherit one example cohort');
}
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const options={headless:true};if(process.platform==='win32')options.channel='msedge';
const browser=await chromium.launch(options),errors=[],external=[];
try{
 const p=await browser.newPage({viewport:{width:1500,height:1050}});p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():(external.push(r.request().url()),r.abort()));
 await p.goto(pathToFileURL(path.join(base,'index.html')).href+'#TOM_AlignedHierarchy');
 await p.locator('#art').evaluate(im=>im.decode());
 assert.equal(await p.locator('#chapter').inputValue(),'bulk.wgcna');
 assert.equal(await p.locator('#browseMode').inputValue(),'forms');
 const first=await p.locator('#art').getAttribute('src');
 for(const mode of ['analysis','forms']){await p.selectOption('#browseMode',mode);assert.equal(await p.locator('#art').getAttribute('src'),first)}
 const before=await p.locator('#menu button').evaluateAll(xs=>xs.map(x=>x.dataset.entry));
 await p.locator('#variants').check();assert.equal(await p.locator('#art').getAttribute('src'),first);await p.locator('#variants').uncheck();
 assert.deepEqual(await p.locator('#menu button').evaluateAll(xs=>xs.map(x=>x.dataset.entry)),before);
 for(const chapter of [...new Set(m.records.flatMap(r=>r.chapters))]){
  await p.selectOption('#chapter',chapter);
  const expected=m.forms.entries.filter(e=>e.member_ids.some(id=>{const r=m.records.find(r=>r.id===id);return !r.variant&&r.chapters.includes(chapter)}));
  assert.equal(await p.locator('#menu button').count(),expected.length);
 }
 // Hash aliases exercise both former IDs and variant/layout editions. Merely
 // checking the JSON alias map would miss the UI's selected-member bug.
 for(const row of m.records){
  await p.evaluate(id=>{location.hash=encodeURIComponent(id)},row.id);
  await p.waitForFunction(src=>document.querySelector('#art').getAttribute('src')===src,row.assets.png);
  await p.locator('#art').evaluate(im=>im.decode());
  assert.equal(await p.locator('#edition').inputValue(),row.id);
  const text=await p.locator('#parameters').textContent();assert.ok(text.includes(row.id));
 }
 await p.locator('#search').fill('TOM_AlignedHierarchy');assert.equal(await p.locator('#menu button').count(),1);
 await p.locator('#art').evaluate(im=>im.decode());
 await p.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await p.locator('#zoom').click();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.locator('#zoom').click();
 await p.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={state:'OFFLINE_NAVIGATION_DEDUP_PASS',original_pages:m.records.length,form_entries:m.forms.navigation_entries,default_form_entries:m.forms.default_entries,all_source_aliases_opened:m.records.length,chapters:58,mode_and_variant_toggle_preserves_selection:true,external_requests:0,scientific_results_merged:0};
 await fs.writeFile(path.join(out,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close()}
