/* Serial offline rendering of complete source-bound composition audit pages. */
import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const base=path.resolve(process.argv[2]);const manifest=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
const external=[];
try{
 const context=await browser.newContext({viewport:{width:1500,height:1100},deviceScaleFactor:1.5});const page=await context.newPage();
 await page.route('**/*',r=>r.request().url().startsWith('data:')?r.continue():(external.push(r.request().url()),r.abort()));
 for(let i=0;i<manifest.records.length;i++){
  const r=manifest.records[i],file=path.join(base,r.file),svg=await fs.readFile(file,'utf8');
  const [,,w,h]=svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const scale=Math.min(1,Math.sqrt(18_000_000/(w*h*4))),cw=Math.ceil(w*96/72*scale),ch=Math.ceil(h*96/72*scale);
  await page.setViewportSize({width:cw+2,height:ch+2});
  await page.setContent('<meta charset="utf-8"><style>html,body{margin:0;background:white}body>svg{display:block;width:'+cw+'px;height:'+ch+'px}</style>'+svg);
  await page.locator('body > svg').screenshot({path:file.replace(/\.svg$/,'.png')});
  await page.pdf({path:file.replace(/\.svg$/,'.pdf'),width:w/72+'in',height:h/72+'in',printBackground:true,margin:{top:0,bottom:0,left:0,right:0},pageRanges:'1'});
  r.sha256={};for(const ext of ['svg','png','pdf'])r.sha256[ext]=sha(await fs.readFile(file.replace(/\.svg$/,'.'+ext)));
  r.rendered=true;r.external_requests=0;r.preview_dpi=144*scale;r.visual_acceptance=false;
  if(i%10===9)console.log('Rendered '+(i+1)+' / '+manifest.records.length);
 }
 if(external.length)throw Error('Unexpected external request');
 await fs.writeFile(path.join(base,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify({status:'COMPLETE_COMPOSITIONS_RENDERED',pages:manifest.records.length,external_requests:0,visual_acceptance:false}));
}finally{await browser.close();}
