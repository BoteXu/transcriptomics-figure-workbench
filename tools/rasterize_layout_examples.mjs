/* Inert complete-SVG exports. No network, arbitrary JS or analysis is allowed. */
import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const folder=path.resolve(process.argv[2]);const manifest=JSON.parse(await fs.readFile(path.join(folder,'manifest.json'),'utf8'));
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');let context;
try{for(let i=0;i<manifest.records.length;i++){
 const row=manifest.records[i];if(row.files?.[path.basename(row.png)])continue;
 if(i%8===0||!context){if(context)await context.close();context=await browser.newContext({deviceScaleFactor:1});}
 const page=await context.newPage();await page.route('**/*',r=>r.request().url().startsWith('data:')?r.continue():r.abort());
 const svg=await fs.readFile(path.join(folder,row.file),'utf8');
 await page.setContent('<meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}</style><div id="stage"></div>');
 await page.locator('#stage').evaluate((e,s)=>{const doc=new DOMParser().parseFromString(s,'image/svg+xml');if(doc.querySelector('parsererror,script,foreignObject'))throw Error('Active or invalid SVG');e.append(document.importNode(doc.documentElement,true));},svg);
 const box=await page.locator('#stage > svg').evaluate(e=>({w:e.viewBox.baseVal.width,h:e.viewBox.baseVal.height}));
 const factor=Math.min(130/72,Math.sqrt(14e6/(box.w*box.h)));
 await page.locator('#stage > svg').evaluate((e,s)=>{e.style.width=s.w+'px';e.style.height=s.h+'px';},{w:box.w*factor,h:box.h*factor});
 await page.setViewportSize({width:Math.ceil(box.w*factor)+2,height:Math.ceil(box.h*factor)+2});
 await page.locator('#stage > svg').screenshot({path:path.join(folder,row.png),timeout:60000});
 // Return CSS dimensions to the explicit physical vector page for PDF export.
 await page.locator('#stage > svg').evaluate((e,b)=>{e.style.width=b.w+'pt';e.style.height=b.h+'pt';},box);
 const pdf=row.file.replace(/\.svg$/,'.pdf');await page.pdf({path:path.join(folder,pdf),width:box.w/72+'in',height:box.h/72+'in',printBackground:true,margin:{top:0,bottom:0,left:0,right:0},pageRanges:'1'});
 row.output_sha256={};for(const file of [row.file,row.png,pdf])row.output_sha256[path.basename(file)]=sha(await fs.readFile(path.join(folder,file)));
 row.raster_pixels=[Math.ceil(box.w*factor),Math.ceil(box.h*factor)];await page.close();
 process.stdout.write(row.id+' RASTERIZED_UNREVIEWED\n');
 await fs.writeFile(path.join(folder,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
}}finally{if(context)await context.close();await browser.close();}
