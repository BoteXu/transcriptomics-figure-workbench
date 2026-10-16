/* Serial inert-SVG restyling. Each exported primitive and input is source-bound. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const [planFile,outDir,...ids]=process.argv.slice(2);
if(!planFile||!outDir)throw Error('plan and fresh output required');
const root=process.cwd(),plan=JSON.parse(await fs.readFile(planFile,'utf8'));
const rows=ids.length?plan.items.filter(r=>ids.includes(r.id)):plan.items;
if(ids.length&&rows.length!==ids.length)throw Error('Unknown or duplicate ID');
await fs.mkdir(outDir,{recursive:false});
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const bound=x=>{const p=path.resolve(root,x);if(!p.startsWith(root+path.sep))throw Error('Source escaped repository');return p;};
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
let context,page;const records=[],failures=[],external=[];
async function fresh(){
 if(context)await context.close();
 context=await browser.newContext({viewport:{width:1200,height:1000},deviceScaleFactor:300/96});page=await context.newPage();
 await page.route('**/*',r=>r.request().url().startsWith('data:')?r.continue():(external.push(r.request().url()),r.abort()));
 await page.setContent('<meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}#stage{width:max-content}</style><div id="stage"></div>');
 for(const name of ['publication-svg.js','form-polish.js'])await page.addScriptTag({content:await fs.readFile(path.join(root,'skills/transcriptomics-figure-workbench/assets/studio',name),'utf8')});
}
try{
 for(let i=0;i<rows.length;i++){
  if(i%8===0)await fresh();const row=rows[i];
  try{
   const source=await fs.readFile(bound(row.source.svg));if(sha(source)!==row.source_sha256.svg)throw Error('Source SVG changed');
   const meta=await fs.readFile(bound(row.source.meta));if(sha(meta)!==row.source_sha256.meta)throw Error('Source metadata changed');
   if(row.table&&sha(await fs.readFile(bound(row.table)))!==row.input_sha256)throw Error('Frozen table changed');
   const result=await page.evaluate(({source,row})=>window.FigureFormPolish.finish(source,row),{source:source.toString('utf8'),row});
   if(result.width_pt*result.height_pt*(300/72)**2>50_000_000)throw Error('Raster exceeds bounded area');
   const dir=path.join(outDir,row.id);await fs.mkdir(dir);await fs.writeFile(path.join(dir,row.id+'.svg'),result.svg);
   await page.setViewportSize({width:Math.ceil(result.width_pt*96/72)+2,height:Math.ceil(result.height_pt*96/72)+2});
   await page.locator('#stage > svg').screenshot({path:path.join(dir,row.id+'.png'),timeout:60000});
   await page.pdf({path:path.join(dir,row.id+'.pdf'),width:result.width_pt/72+'in',height:result.height_pt/72+'in',printBackground:true,margin:{top:0,bottom:0,left:0,right:0},pageRanges:'1'});
   if(row.table)await fs.copyFile(bound(row.table),path.join(dir,row.id+'.tsv'));
   const outputs={};for(const ext of ['svg','png','pdf'])outputs[row.id+'.'+ext]=sha(await fs.readFile(path.join(dir,row.id+'.'+ext)));
   const receipt={schema_version:1,id:row.id,status:'RENDERED_PENDING_INDIVIDUAL_VISUAL_REVIEW',source:row.source,source_sha256:row.source_sha256,
    input_table:row.table,input_sha256:row.input_sha256,profile:row.profile,kind:row.kind,variant:result.variant,
    same_form:true,all_measured_primitives_retained:true,frozen_graphical_geometry_sha256:sha(result.graphical_fingerprint),
    layout_groups:result.layout_groups,width_pt:result.width_pt,height_pt:result.height_pt,raster_dpi:300,
    sizing:result.sizing,changes:result.changes,retained_notes:result.retained_notes,geometry_audit:result.audit,
    output_sha256:outputs,visual_acceptance:false,scientific_acceptance:false};
   await fs.writeFile(path.join(dir,row.id+'.json'),JSON.stringify(receipt,null,2)+'\n');
   records.push({id:row.id,source:row.source,profile:row.profile,output_sha256:outputs,sizing:result.sizing,issues:result.audit.issues.length});
   process.stdout.write(JSON.stringify({rendered:i+1,total:rows.length,id:row.id,issues:result.audit.issues.length})+'\n');
  }catch(e){failures.push({id:row.id,error:e.message});process.stdout.write(JSON.stringify(failures.at(-1))+'\n');}
  await fs.writeFile(path.join(outDir,'manifest.json'),JSON.stringify({schema_version:1,version:'0.8.0',records,failures,external_requests:external,visual_acceptance:false,scientific_acceptance:false},null,2)+'\n');
 }
 if(failures.length||external.length)process.exitCode=1;
}finally{await browser.close();}
