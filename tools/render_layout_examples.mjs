/* Render the selected frozen layout SVGs serially; no numerical research work. */
import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const root=process.cwd(),base=path.join(root,'examples/layout-v080'),manifest=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});const external=[];
try{const context=await browser.newContext({viewport:{width:1500,height:1100},deviceScaleFactor:300/96}),page=await context.newPage();
await page.route('**/*',r=>r.request().url().startsWith('data:')?r.continue():(external.push(r.request().url()),r.abort()));
for(const r of manifest.records){const file=path.join(base,r.file),svg=await fs.readFile(file,'utf8'),[,,w,h]=svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
 if(w*h*(300/72)**2>50_000_000)throw Error('Example exceeds raster budget');
 await page.setContent('<meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}</style>'+svg);await page.setViewportSize({width:Math.ceil(w*96/72)+1,height:Math.ceil(h*96/72)+1});await page.locator('body > svg').screenshot({path:file.replace(/\.svg$/,'.png')});await page.pdf({path:file.replace(/\.svg$/,'.pdf'),width:w/72+'in',height:h/72+'in',printBackground:true,margin:{top:0,bottom:0,left:0,right:0},pageRanges:'1'});
 r.sha256={};for(const e of ['svg','png','pdf'])r.sha256[e]=sha(await fs.readFile(file.replace(/\.svg$/,'.'+e)));r.rendered=true;r.external_requests=0;}
if(external.length)throw Error('Unexpected external request');await fs.writeFile(path.join(base,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');console.log(JSON.stringify({status:'FLEXIBLE_EXAMPLES_RENDERED',pages:manifest.records.length,external_requests:0,visual_acceptance:false}));}finally{await browser.close();}
