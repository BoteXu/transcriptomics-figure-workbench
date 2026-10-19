/* Render each actual complete-SVG layout in the already provisioned browser. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(process.argv[2]||'');
if(!process.argv[2])throw Error('Select the exact packaged gallery');
const d=JSON.parse(await fs.readFile(path.join(root,'manifest.json'),'utf8'));
const selected=new Set(process.argv.slice(3));
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
try{
 for(const r of d.records.filter(r=>r.composition&&(!selected.size||selected.has(r.id)))){
  const page=await browser.newPage({deviceScaleFactor:1.5});
  try{
   await page.route('**/*',route=>/^(file:|data:)/.test(route.request().url())?route.continue():route.abort());
   await page.goto(pathToFileURL(path.join(root,r.assets.svg)).href);
   const size=await page.locator('svg').first().evaluate(n=>({w:Math.ceil(n.getBoundingClientRect().width),h:Math.ceil(n.getBoundingClientRect().height)}));
   if(size.w*size.h*2.25>40e6)throw Error('Layout preview exceeds selected drawing budget');
   await page.setViewportSize({width:Math.max(400,size.w),height:Math.max(400,Math.min(1200,size.h))});
   await page.locator('svg').first().screenshot({path:path.join(root,r.assets.png),timeout:90000});
   console.log(r.id+' COMPOSITION_RENDERED');
  }finally{await page.close()}
 }
}finally{await browser.close()}
