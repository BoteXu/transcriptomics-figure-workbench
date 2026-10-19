/* Actual offline playback, exact physical times and every embedded frame. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const out=process.argv[2];if(!out)throw Error('Choose a fresh evidence directory');
await fs.mkdir(out,{recursive:false});
const base=path.resolve('skills/transcriptomics-figure-workbench/assets/method-upgrade-gallery');
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
const errors=[],external=[],records=[];
try{
 for(const id of ['D03_Trajectory','D03_Trajectory_Custom','D03_Trajectory_Small']){
  const p=await browser.newPage({viewport:{width:1000,height:900}});
  try{
   p.on('pageerror',e=>errors.push(e.message));
   await p.route('**/*',r=>/^(file:|data:)/.test(r.request().url())?r.continue():(external.push(r.request().url()),r.abort()));
   const meta=JSON.parse(await fs.readFile(path.join(base,id,id+'.animation.json'),'utf8'));
   await p.goto(pathToFileURL(path.join(base,id,id+'.html')).href);
   const payload=await p.evaluate(()=>({ids:D.ids,times:D.times,time_unit:D.time_unit,fps:D.fps}));
   assert.deepEqual(payload.ids,meta.frame_ids);assert.deepEqual(payload.times,meta.times);assert.equal(payload.time_unit,meta.time_unit);
   await p.evaluate(async()=>{for(const src of D.frames){if(!src.startsWith('data:image/png;base64,'))throw Error('Nonlocal frame');const im=new Image();im.src=src;await im.decode();if(im.naturalWidth<100)throw Error('Empty frame')}});
   for(const i of [0,Math.floor(meta.frame_ids.length/2),meta.frame_ids.length-1]){
    await p.locator('#frame').fill(String(i));await p.locator('#frame').dispatchEvent('input');await p.locator('#art').evaluate(im=>im.decode());
    assert.equal(await p.locator('#time').textContent(),meta.frame_ids[i]+' · '+meta.times[i]+' '+meta.time_unit);
    await p.screenshot({path:path.join(out,id+'-'+i+'.png'),fullPage:true});
   }
   await p.locator('#frame').fill('0');await p.locator('#frame').dispatchEvent('input');
   await p.locator('#play').click();await p.waitForFunction(()=>Number(document.getElementById('frame').value)>0);
   await p.locator('#play').click();assert.equal(await p.locator('#play').textContent(),'Play');
   const stopped=await p.locator('#frame').inputValue();await p.waitForTimeout(400);assert.equal(await p.locator('#frame').inputValue(),stopped);
   await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   records.push({id,frames_decoded:meta.frame_ids.length,physical_times_checked:true,slider_and_play_pause:true});
  }finally{await p.close()}
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const result={state:'OFFLINE_TRAJECTORY_PLAYBACK_PASS',records,external_requests:0,aesthetic_approval:false};
 await fs.writeFile(path.join(out,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close()}
