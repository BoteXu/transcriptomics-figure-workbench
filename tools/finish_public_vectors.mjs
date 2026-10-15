/* Serial, bounded publication rendering of selected frozen local SVGs. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const [planFile,outDir,...selected]=process.argv.slice(2);
if(!planFile||!outDir)throw Error('Supply a local frozen-vector plan and a fresh output directory');
const root=process.cwd(),plan=JSON.parse(await fs.readFile(planFile,'utf8'));
const chosen=selected.length?plan.items.filter(i=>selected.includes(i.id)):plan.items;
if(selected.length&&chosen.length!==selected.length)throw Error('Unknown or duplicate selected IDs');
await fs.mkdir(outDir,{recursive:false});
const bound=relative=>{const p=path.resolve(root,relative);if(!p.startsWith(root+path.sep))throw Error('Source escapes selected repository');return p};
const sha=value=>crypto.createHash('sha256').update(value).digest('hex');
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE;
const {chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');
const launch={headless:true};
if(process.env.FIGURE_BROWSER_EXECUTABLE)launch.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;
else if(process.platform==='win32')launch.channel='msedge';
const browser=await chromium.launch(launch);
let context,page;
const external=[];
async function freshPage(){
  if(context)await context.close();
  context=await browser.newContext({viewport:{width:1600,height:1200},deviceScaleFactor:300/96});
  page=await context.newPage();
  await page.route('**/*',r=>{const u=r.request().url();if(u.startsWith('data:')||u.startsWith('blob:'))return r.continue();external.push(u);return r.abort()});
  await page.setContent('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}#stage{width:max-content}</style><div id="stage"></div>');
  await page.addScriptTag({content:await fs.readFile(path.join(root,'skills/transcriptomics-figure-workbench/assets/studio/publication-svg.js'),'utf8')});
}
function dpiChunk(buffer){
  const payload=Buffer.alloc(9);payload.writeUInt32BE(11811,0);payload.writeUInt32BE(11811,4);payload[8]=1;
  const kind=Buffer.from('pHYs');const data=Buffer.concat([kind,payload]);let crc=0xffffffff;
  for(const byte of data){crc^=byte;for(let k=0;k<8;k++)crc=(crc>>>1)^((crc&1)?0xedb88320:0)}
  const chunk=Buffer.alloc(21);chunk.writeUInt32BE(9,0);kind.copy(chunk,4);payload.copy(chunk,8);chunk.writeUInt32BE((crc^0xffffffff)>>>0,17);
  let offset=8;const parts=[buffer.subarray(0,8)];let inserted=false;
  while(offset<buffer.length){const length=buffer.readUInt32BE(offset);const type=buffer.subarray(offset+4,offset+8).toString('ascii');const end=offset+length+12;
    if(type!=='pHYs')parts.push(buffer.subarray(offset,end));
    if(type==='IHDR'&&!inserted){parts.push(chunk);inserted=true}offset=end;
  }
  return Buffer.concat(parts);
}
const records=[],failures=[];
try{
  await freshPage();
  for(let index=0;index<chosen.length;index++){
    const item=chosen[index];if(index&&index%12===0)await freshPage();
    try {
    if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(item.id))throw Error('Unsafe figure ID');
    const sourcePath=bound(item.svg);if(!sourcePath.startsWith(root+path.sep))throw Error('Source outside selected public repository');
    const source=await fs.readFile(sourcePath);if(sha(source)!==item.source_sha256)throw Error('Source SVG changed');
    if(sha(await fs.readFile(bound(item.meta)))!==item.source_metadata_sha256)throw Error('Source metadata changed');
    if(item.tsv&&sha(await fs.readFile(bound(item.tsv)))!==item.input_sha256)throw Error('Source table changed');
    const result=await page.evaluate(({source,context,patch})=>window.FigurePublication.finish(source,context,patch),{source:source.toString('utf8'),context:item.context,patch:item.patch||{}});
    if(result.width_pt*result.height_pt*(300/72)**2>40_000_000)throw Error('Raster page exceeds 40 million pixels');
    const destination=path.join(outDir,item.id);await fs.mkdir(destination,{recursive:false});
    const svg=path.join(destination,item.id+'.svg');await fs.writeFile(svg,result.svg,'utf8');
    await page.setViewportSize({width:Math.ceil(result.width_pt*96/72)+2,height:Math.ceil(result.height_pt*96/72)+2});
    const png=path.join(destination,item.id+'.png');const screenshot=await page.locator('#stage > svg').screenshot({type:'png',timeout:60000});await fs.writeFile(png,dpiChunk(screenshot));
    const pdf=path.join(destination,item.id+'.pdf');await page.pdf({path:pdf,width:(result.width_pt/72)+'in',height:(result.height_pt/72)+'in',margin:{top:0,bottom:0,left:0,right:0},printBackground:true,pageRanges:'1'});
    const outputs={};for(const name of [item.id+'.svg',item.id+'.png',item.id+'.pdf'])outputs[name]=sha(await fs.readFile(path.join(destination,name)));
    const receipt={schema_version:1,id:item.id,status:'RENDERED_PENDING_VISUAL_REVIEW',source_svg:item.svg,source_sha256:item.source_sha256,
      source_metadata:item.meta,source_metadata_sha256:item.source_metadata_sha256,input_table:item.tsv||null,input_sha256:item.input_sha256||null,
      frozen_graphical_geometry_sha256:sha(result.geometry_fingerprint),coordinates_and_shapes_retained:true,
      route:'frozen SVG graphical primitives; publication layout and text finishing; no upstream result recomputation',
      width_pt:result.width_pt,height_pt:result.height_pt,raster_dpi:300,axis_geometry:result.axis_geometry,
      finishing_patch:item.patch||{},finisher_sha256:sha(await fs.readFile(path.join(root,'skills/transcriptomics-figure-workbench/assets/studio/publication-svg.js'))),changes:result.changes,removed_page_furniture:result.removed_page_furniture,body_transform:result.body_transform,
      geometry_audit:result.audit,output_sha256:outputs,scientific_acceptance:false,visual_acceptance:false};
    if(item.tsv)await fs.copyFile(path.join(root,item.tsv),path.join(destination,item.id+'.tsv'));
    await fs.writeFile(path.join(destination,item.id+'.json'),JSON.stringify(receipt,null,2)+'\n');
    records.push({id:item.id,issues:result.audit.issues.length,png_sha256:outputs[item.id+'.png']});
    process.stdout.write(JSON.stringify({rendered:index+1,total:chosen.length,...records.at(-1)})+'\n');
    }catch(error){failures.push({id:item.id,error:error.message});process.stdout.write(JSON.stringify({failed:item.id,error:error.message})+'\n')}
    await fs.writeFile(path.join(outDir,'render-manifest.json'),JSON.stringify({status:failures.length?'PARTIAL_RENDER_REQUIRES_REPAIR':'RENDERED_PENDING_VISUAL_REVIEW',records,failures,external_requests:external,scientific_acceptance:false},null,2)+'\n');
  }
  if(external.length)throw Error('Unexpected external browser requests');
  if(failures.length)process.exitCode=1;
}finally{await browser.close()}
