/* Actual offline browser routes for every preserved source and method. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const out=process.argv[2];if(!out)throw Error('Fresh evidence directory required');await fs.mkdir(out,{recursive:false});
const base=path.resolve('skills/transcriptomics-figure-workbench/assets/visual-library');
const d=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
const errors=[],external=[];
try{
 const p=await browser.newPage({viewport:{width:1550,height:1050}});p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():(external.push(r.request().url()),r.abort()));
 const url=pathToFileURL(path.join(base,'index.html')).href;
 await p.goto(url);await p.locator('#art').evaluate(im=>im.decode());
 assert.equal(await p.locator('#menu button').count(),d.entries.length);
 async function open(id){await p.evaluate(id=>{location.hash=encodeURIComponent(id)},id);const target=d.aliases[id]||id;await p.waitForFunction(id=>document.querySelector('#edition').value===id,target);await p.locator('#art').evaluate(im=>im.decode())}
 // Direct links and both selectors must keep 3D and radar genuinely drawable.
 for(const id of ['radar','reference-surface-grid__surface','mass-spectrum-mirror','sequence-logo','roc','source-gallery/network__circular','H02_forest','D01_Scatter3D','D02_Volume','D03_Trajectory','D01_Scatter3D_Composition']){
  await open(id);await p.screenshot({path:path.join(out,id.replaceAll('/','_')+'.png'),fullPage:true});
 }
 for(const f of JSON.parse(await fs.readFile(path.resolve('skills/transcriptomics-figure-workbench/references/form-catalog.json'),'utf8')).forms)await open(f.id);
 for(const r of d.records)await open(r.id);
 // Every manifest source alias resolves, including asset paths shared by
 // chapter and companion catalogs. This detects silent alias loss.
 for(const c of d.coverage)await open(c.source_id);
 await open('radar');await p.locator('#history').uncheck();
 assert.equal(await p.locator('#menu button').count(),d.entries.length);
 await p.locator('#search').fill('三维');assert.ok(await p.locator('#menu button').count()>=2);
 assert.ok((await p.locator('#title').textContent()).includes('三维'));
 await p.locator('#search').fill('');await p.selectOption('#domain','modelling');
 const expected=d.entries.filter(e=>e.member_ids.some(id=>{const r=d.records.find(r=>r.id===id);return !r.history&&r.domains.includes('modelling')}));
 assert.equal(await p.locator('#menu button').count(),expected.length);
 await p.screenshot({path:path.join(out,'modelling.png'),fullPage:true});
 await open('radar');await p.setViewportSize({width:390,height:844});
 assert.equal(await p.locator('#methodSelect option').count(),d.entries.length);
 await p.selectOption('#methodSelect','reference-surface-grid');await p.locator('#art').evaluate(im=>im.decode());
 assert.ok((await p.locator('#title').textContent()).includes('三维'));await p.selectOption('#methodSelect','radar');
 assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await p.locator('#zoom').click();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.locator('#zoom').click();
 await p.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={state:'COMPLETE_VISUAL_BROWSER_PASS',source_links_opened:d.coverage.length,record_images_decoded:d.records.length,base_form_links_opened:90,visible_families:d.entries.length,external_requests:0,aesthetic_acceptance:false};
 await fs.writeFile(path.join(out,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close()}
