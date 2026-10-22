/* Actual identity coordination, keyboard/filter semantics and responsive/export checks. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const out=process.argv[2];if(!out)throw Error('Choose a fresh evidence directory');
await fs.mkdir(out,{recursive:false});
const base=path.resolve('skills/transcriptomics-figure-workbench/assets/connected-examples');
const manifest=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
const errors=[],external=[],records=[];
try{
 for(const record of manifest.records){
  const p=await browser.newPage({viewport:{width:1500,height:1100}});
  try{
   p.on('pageerror',e=>errors.push(e.message));
   await p.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():(external.push(r.request().url()),r.abort()));
   await p.goto(pathToFileURL(path.join(base,record.page)).href);
   await p.waitForFunction(()=>document.querySelectorAll('.dot').length>0);
   const data=await p.evaluate(()=>window.linkedInspector.data);
   const pointCount=data.views.reduce((n,v)=>n+data.rows.filter(r=>[v.x,v.y,...(v.kind==='interval'?[v.x_lower,v.x_upper]:[])].every(k=>r.values[k]!==null)).length,0);
   assert.equal(data.rows.length,record.rows);assert.equal(await p.locator('.dot').count(),pointCount);
   const columns=await p.locator('#views').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length);
   assert.equal(columns,record.id==='Custom'?2:Math.min(3,record.views));
   assert.equal(await p.locator('.dot[tabindex="0"]').count(),record.views);
   await p.locator('.view:first-child .dot[tabindex="0"]').focus();await p.keyboard.press('ArrowRight');
   assert.equal(await p.evaluate(()=>document.activeElement.dataset.objectId),data.rows.filter(r=>[data.views[0].x,data.views[0].y].every(k=>r.values[k]!==null))[1].id);
   await p.screenshot({path:path.join(out,record.id+'-default.png'),fullPage:true});
   const id=data.rows.find(r=>data.views.every(v=>[v.x,v.y].every(k=>r.values[k]!==null))).id;
   await p.locator(`.view:first-child .dot[data-object-id="${id}"]`).click();
   assert.equal(await p.locator('.dot[aria-pressed="true"]').count(),record.views);
   assert.ok((await p.locator('#status').textContent()).includes('1 selected'));
   await p.locator(`.view:first-child .dot[data-object-id="${id}"]`).focus();await p.keyboard.press('Space');
   assert.equal(await p.locator('.dot[aria-pressed="true"]').count(),0);
   await p.keyboard.press('Enter');assert.equal(await p.locator('.dot[aria-pressed="true"]').count(),record.views);
   assert.equal(await p.locator('#rows tr').count(),Math.min(8,record.rows));await p.locator('#all').click();assert.equal(await p.locator('#rows tr').count(),1);await p.locator('#all').click();
   await p.screenshot({path:path.join(out,record.id+'-selected.png'),fullPage:true});
   const domains=await p.evaluate(()=>window.linkedInspector.domains);
   await p.locator('#group').selectOption(data.rows.at(-1).group);
   assert.deepEqual(await p.evaluate(()=>window.linkedInspector.domains),domains);
   assert.equal(await p.evaluate(()=>window.linkedInspector.selected.size),1);
   await p.locator('#reset').click();assert.equal(await p.locator('.dot').count(),pointCount);
   await p.locator('#find').fill(id);assert.equal(await p.locator('.dot').count(),pointCount);
   const downloadPromise=p.waitForEvent('download');await p.locator('#export').click();
   const download=await downloadPromise;const svgFile=path.join(out,record.id+'-aligned.svg');await download.saveAs(svgFile);
   const svg=await fs.readFile(svgFile,'utf8');assert.ok(svg.includes(data.input_sha256));
   for(const group of Object.keys(data.colors))assert.ok(svg.includes(group));
   assert.equal((svg.match(/class="dot"/g)||[]).length,pointCount);
   assert.ok(await p.evaluate(text=>!new DOMParser().parseFromString(text,'image/svg+xml').querySelector('parsererror'),svg),'Exported SVG must parse independently');
   const preview=path.join(out,record.id+'-svg-preview.html');
   await fs.writeFile(preview,'<!doctype html><meta charset="utf-8"><title>Exact exported SVG</title><style>body{margin:20px;background:white}img{display:block;max-width:100%;height:auto}</style><img alt="Exact exported coordinated views" src="'+encodeURIComponent(path.basename(svgFile))+'">');
   const exportPage=await browser.newPage({viewport:{width:1500,height:1100}});
   try{await exportPage.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():r.abort());await exportPage.goto(pathToFileURL(preview).href);await exportPage.locator('img').evaluate(im=>im.decode());assert.ok(await exportPage.locator('img').evaluate(im=>im.naturalWidth>500&&im.naturalHeight>200));await exportPage.screenshot({path:path.join(out,record.id+'-svg-export.png'),fullPage:true})}finally{await exportPage.close()}
   await p.locator('#reset').click();if(record.rows>8){await p.locator('#next').click();assert.ok((await p.locator('#page').textContent()).startsWith('9'))}
   await p.setViewportSize({width:900,height:1000});assert.equal(await p.locator('#views').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length),2);
   await p.screenshot({path:path.join(out,record.id+'-tablet.png'),fullPage:true});
   await p.setViewportSize({width:390,height:844});await p.waitForTimeout(100);
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert.equal(await p.locator('#views').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length),1);
   await p.screenshot({path:path.join(out,record.id+'-mobile.png'),fullPage:true});
   await p.locator('#find').fill(id);
   assert.equal(await p.evaluate(()=>window.linkedInspector.exportSvg()),svg,'SVG export geometry must be independent of the screen viewport');
   records.push({id:record.id,rows:record.rows,shared_identity:true,keyboard:true,unchanged_filter_axes:true,desktop_tablet_mobile:true,svg_export:true});
  }finally{await p.close()}
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={state:'CONNECTED_BROWSER_PASS',records,external_requests:0,aesthetic_approval:false};
 await fs.writeFile(path.join(out,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close()}
