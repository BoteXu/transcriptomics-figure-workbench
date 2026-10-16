/* Balanced complete-panel composition; inputs and every component hash are pinned. */
import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const [planFile,componentsDir,outDir,...ids]=process.argv.slice(2),root=process.cwd();
const plan=JSON.parse(await fs.readFile(planFile,'utf8')),rows=ids.length?plan.compositions.filter(r=>ids.includes(r.id)):plan.compositions;
await fs.mkdir(outDir,{recursive:false});const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {chromium}=await import(pathToFileURL(process.env.FIGURE_PLAYWRIGHT_MODULE));
const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});let context,page;const records=[],failures=[],external=[];
async function fresh(){if(context)await context.close();context=await browser.newContext({viewport:{width:1200,height:1000},deviceScaleFactor:200/96});page=await context.newPage();await page.route('**/*',r=>r.request().url().startsWith('data:')?r.continue():(external.push(r.request().url()),r.abort()));await page.setContent('<style>html,body{margin:0}svg{display:block}</style><div id="stage"></div>');await page.addScriptTag({content:await fs.readFile('skills/transcriptomics-figure-workbench/assets/studio/publication-svg.js','utf8')});}
try{for(let i=0;i<rows.length;i++){
 if(i%8===0)await fresh();const row=rows[i];
 try{
  const parts=[];for(const id of row.components){const dir=path.join(componentsDir,id),meta=JSON.parse(await fs.readFile(path.join(dir,id+'.json'),'utf8')),s=await fs.readFile(path.join(dir,id+'.svg'));if(sha(s)!==meta.output_sha256[id+'.svg'])throw Error('Changed component');parts.push({id,svg:s.toString('utf8'),svg_sha256:sha(s),input_sha256:meta.input_sha256||null});}
  const source=await fs.readFile(path.join(root,row.source.svg));if(sha(source)!==row.source_sha256.svg)throw Error('Changed source composition');
  const result=await page.evaluate(({parts,row,source})=>{
   const NS='http://www.w3.org/2000/svg',node=(tag,a={})=>{const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(a))n.setAttribute(k,String(v));return n;};
   const text=(s,x,y,size=11)=>{const n=node('text',{x,y,'font-family':'Arial, Liberation Sans, sans-serif','font-size':size,fill:'#283740'});n.textContent=s;return n;};
   const original=window.FigurePublication.safeParse(source),title=original.querySelector(':scope > text')?.textContent||row.id;
   const cols=row.orientation==='vertical'?1:row.orientation==='horizontal'?parts.length:Math.min(parts.length,2),gap=22,margin=18,header=45;
   const tileW=cols===1?490:cols===2?340:300;
   const parsed=parts.map((part,i)=>{
    const s=window.FigurePublication.safeParse(part.svg),v=s.viewBox.baseVal,w=v.width,h=v.height;
    const panelTitle=[...s.children].find(n=>n.localName==='text'&&Number(n.getAttribute('y'))===27)?.textContent||parts[i].id;
    for(const n of [...s.children])if(n.localName==='text'&&(Number(n.getAttribute('y'))<34||Number(n.getAttribute('y'))>h-12))n.remove();
    s.querySelectorAll('[data-page-background]').forEach(n=>n.remove());
    const prefix='v080_'+i+'_',map=new Map([...s.querySelectorAll('[id]')].map(n=>[n.id,prefix+n.id]));
    for(const n of [s,...s.querySelectorAll('*')])for(const a of [...n.attributes]){if(a.name==='id')n.setAttribute('id',map.get(a.value)||prefix+a.value);else if(a.value.startsWith('#')&&map.has(a.value.slice(1)))n.setAttributeNS(a.namespaceURI,a.name,'#'+map.get(a.value.slice(1)));else if(a.value.includes('url(#'))n.setAttribute(a.name,a.value.replace(/url\(#([^)]+)\)/g,(_,id)=>'url(#'+(map.get(id)||id)+')'));}
    s.setAttribute('viewBox',`0 35 ${w} ${h-51}`);s.setAttribute('width',tileW);s.setAttribute('height',(h-51)*tileW/w);return {svg:s,h:(h-51)*tileW/w,scale:tileW/w,w:tileW,panelTitle};
   });
   const heights=Array.from({length:Math.ceil(parts.length/cols)},(_,r)=>Math.max(...parsed.slice(r*cols,(r+1)*cols).map(p=>p.h+25)));
   const width=cols*tileW+(cols-1)*gap+2*margin,height=header+heights.reduce((a,b)=>a+b,0)+gap*(heights.length-1)+20;
   const svg=node('svg',{xmlns:NS,viewBox:`0 0 ${width} ${height}`,width:width+'pt',height:height+'pt'});svg.append(node('rect',{width,height,fill:'white'}));const t=text(title,margin,27,12);t.setAttribute('font-weight','600');svg.append(t);const positions=[];
   parsed.forEach((p,i)=>{const c=i%cols,r=Math.floor(i/cols),x=margin+c*(tileW+gap),y=header+heights.slice(0,r).reduce((a,b)=>a+b+gap,0);const heading=text(String.fromCharCode(65+i)+'  '+p.panelTitle,x,y+10,9);svg.append(heading);while(heading.getComputedTextLength()>tileW&&parseFloat(heading.getAttribute('font-size'))>7)heading.setAttribute('font-size',parseFloat(heading.getAttribute('font-size'))-.2);p.svg.setAttribute('x',x);p.svg.setAttribute('y',y+19);svg.append(p.svg);positions.push({id:parts[i].id,x,y:y+19,scale:p.scale,width_pt:p.w,height_pt:p.h});});
   const f=text('SYNTHETIC DISPLAY · '+row.id+' · complete independent panels',margin,height-6,6.5);f.setAttribute('fill','#66767d');svg.append(f);document.querySelector('#stage').replaceChildren(svg);
   return {svg:new XMLSerializer().serializeToString(svg),width_pt:width,height_pt:height,positions,audit:window.FigurePublication.audit(svg)};
  },{parts,row,source:source.toString('utf8')});
  if(result.width_pt*result.height_pt*(200/72)**2>45e6)throw Error('Bounded raster exceeded');
  const dir=path.join(outDir,row.id);await fs.mkdir(dir);await fs.writeFile(path.join(dir,row.id+'.svg'),result.svg);await page.setViewportSize({width:Math.ceil(result.width_pt*96/72)+2,height:Math.ceil(result.height_pt*96/72)+2});await page.locator('#stage > svg').screenshot({path:path.join(dir,row.id+'.png'),timeout:60000});await page.pdf({path:path.join(dir,row.id+'.pdf'),width:result.width_pt/72+'in',height:result.height_pt/72+'in',printBackground:true,margin:{top:0,bottom:0,left:0,right:0},pageRanges:'1'});
  const outputs={};for(const ext of ['svg','png','pdf'])outputs[row.id+'.'+ext]=sha(await fs.readFile(path.join(dir,row.id+'.'+ext)));
  const receipt={schema_version:1,id:row.id,status:'COMPOSED_PENDING_VISUAL_REVIEW',same_form:true,source:row.source,source_sha256:row.source_sha256,components:parts.map(({svg,...p})=>p),component_placement:result.positions,arrangement:row.orientation,relationship:row.relationship,width_pt:result.width_pt,height_pt:result.height_pt,raster_dpi:200,output_sha256:outputs,geometry_audit:result.audit,visual_acceptance:false,scientific_acceptance:false,limitations:'Overview uses complete uniformly scaled independent panels; target paper size requires separate acceptance. Independent 300 DPI components supplied.'};
  await fs.writeFile(path.join(dir,row.id+'.json'),JSON.stringify(receipt,null,2)+'\n');records.push({id:row.id,issues:result.audit.issues.length,output_sha256:outputs});process.stdout.write(JSON.stringify({composed:i+1,total:rows.length,id:row.id,issues:result.audit.issues.length})+'\n');
 }catch(e){failures.push({id:row.id,error:e.message});process.stdout.write(JSON.stringify(failures.at(-1))+'\n');}
 await fs.writeFile(path.join(outDir,'manifest.json'),JSON.stringify({records,failures,external_requests:external,visual_acceptance:false},null,2)+'\n');
}if(failures.length||external.length)process.exitCode=1;}finally{await browser.close();}
