/* Rebuild all saved combinations from individually finished, verified SVG panels. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const [planFile,componentsDir,outDir,...selected]=process.argv.slice(2);
if(!planFile||!componentsDir||!outDir)throw Error('Supply bound plan, verified component directory and fresh output');
const root=process.cwd(),plan=JSON.parse(await fs.readFile(planFile,'utf8'));
const recipes=selected.length?plan.compositions.filter(i=>selected.includes(i.id)):plan.compositions;
if(selected.length&&recipes.length!==selected.length)throw Error('Select exact unique composition IDs');
await fs.mkdir(outDir,{recursive:false});
const sha=v=>crypto.createHash('sha256').update(v).digest('hex');
const modulePath=process.env.FIGURE_PLAYWRIGHT_MODULE;
const {chromium}=modulePath?await import(pathToFileURL(modulePath)):await import('playwright');
const opts={headless:true};if(process.env.FIGURE_BROWSER_EXECUTABLE)opts.executablePath=process.env.FIGURE_BROWSER_EXECUTABLE;else if(process.platform==='win32')opts.channel='msedge';
const browser=await chromium.launch(opts);let context,page;const external=[],records=[],failures=[];
async function start(){
  if(context)await context.close();context=await browser.newContext({viewport:{width:1600,height:1200},deviceScaleFactor:300/96});page=await context.newPage();
  await page.route('**/*',r=>{if(r.request().url().startsWith('data:'))return r.continue();external.push(r.request().url());return r.abort()});
  await page.setContent('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}</style><div id="stage"></div>');
  await page.addScriptTag({content:await fs.readFile(path.join(root,'skills/transcriptomics-figure-workbench/assets/studio/publication-svg.js'),'utf8')});
}
function pngDpi(png){
  const payload=Buffer.alloc(9);payload.writeUInt32BE(11811,0);payload.writeUInt32BE(11811,4);payload[8]=1;
  const type=Buffer.from('pHYs'),data=Buffer.concat([type,payload]);let crc=0xffffffff;
  for(const v of data){crc^=v;for(let k=0;k<8;k++)crc=(crc>>>1)^((crc&1)?0xedb88320:0)}
  const part=Buffer.alloc(21);part.writeUInt32BE(9,0);type.copy(part,4);payload.copy(part,8);part.writeUInt32BE((crc^0xffffffff)>>>0,17);
  let at=8;const parts=[png.subarray(0,8)];while(at<png.length){const n=png.readUInt32BE(at),kind=png.subarray(at+4,at+8).toString('ascii');if(kind!=='pHYs')parts.push(png.subarray(at,at+n+12));if(kind==='IHDR')parts.push(part);at+=n+12}return Buffer.concat(parts);
}
try{
  await start();
  for(let i=0;i<recipes.length;i++){
    const recipe=recipes[i];if(i&&i%8===0)await start();
    try{
      if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(recipe.id))throw Error('Unsafe composition ID');
      const components=[];
      for(const id of recipe.components){
        if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(id))throw Error('Unsafe component ID');
        const bundle=path.join(componentsDir,id),meta=JSON.parse(await fs.readFile(path.join(bundle,id+'.json'),'utf8'));
        const source=await fs.readFile(path.join(bundle,id+'.svg'));
        if(sha(source)!==meta.output_sha256[id+'.svg'])throw Error('Component SVG changed');
        components.push({id,svg:source.toString('utf8'),sha256:sha(source),input_sha256:meta.input_sha256});
      }
      const result=await page.evaluate(({recipe,components})=>{
        const NS='http://www.w3.org/2000/svg';const node=(tag,attrs={})=>{const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n};
        const text=(s,x,y,size=9)=>{const n=node('text',{x,y,'font-family':'Arial, Liberation Sans, sans-serif','font-size':size,fill:'#273540'});n.textContent=s;return n};
        const parsed=components.map((component,index)=>{
          const svg=window.FigurePublication.safeParse(component.svg),vb=svg.viewBox.baseVal;
          const width=vb.width,height=vb.height-36;
          for(const el of [...svg.querySelectorAll('text')])if(/^SYNTHETIC DEMO|^Frozen display; no biological inference/.test(el.textContent.trim()))el.remove();
          const prefix='panel'+index+'__',ids=new Map([...svg.querySelectorAll('[id]')].map(el=>[el.id,prefix+el.id]));
          for(const el of [svg,...svg.querySelectorAll('*')])for(const attr of [...el.attributes]){
            if(attr.name==='id')el.setAttribute('id',ids.get(attr.value)||prefix+attr.value);
            else if(attr.value.startsWith('#')&&ids.has(attr.value.slice(1)))el.setAttributeNS(attr.namespaceURI,attr.name,'#'+ids.get(attr.value.slice(1)));
            else if(attr.value.includes('url(#'))el.setAttribute(attr.name,attr.value.replace(/url\(#([^\)]+)\)/g,(_,id)=>'url(#'+(ids.get(id)||id)+')'));
          }
          svg.setAttribute('viewBox',`0 18 ${width} ${height}`);svg.setAttribute('width',width);svg.setAttribute('height',height);svg.setAttribute('overflow','hidden');
          return {svg,width,height};
        });
        const n=parsed.length,cols=recipe.orientation==='vertical'?1:recipe.orientation==='horizontal'?n:Math.min(n,2),rows=Math.ceil(n/cols),gap=20,margin=18,top=57;
        const widths=Array.from({length:cols},(_,c)=>Math.max(...parsed.filter((_,i)=>i%cols===c).map(p=>p.width)));
        const heights=Array.from({length:rows},(_,r)=>Math.max(...parsed.slice(r*cols,(r+1)*cols).map(p=>p.height+22)));
        const width=widths.reduce((a,b)=>a+b,0)+(cols-1)*gap+2*margin,height=heights.reduce((a,b)=>a+b,0)+(rows-1)*gap+top+22;
        const svg=node('svg',{xmlns:NS,viewBox:`0 0 ${width} ${height}`,width:width+'pt',height:height+'pt'});
        svg.append(node('rect',{width,height,fill:'white'}));svg.append(text(recipe.title,margin,33,10.5));
        const badge=text('SYNTHETIC COMPOSITION | '+recipe.id,width-margin,12,6.5);badge.setAttribute('text-anchor','end');badge.setAttribute('fill','#637381');svg.append(badge);
        const positions=[];
        for(let j=0;j<n;j++){
          const col=j%cols,row=Math.floor(j/cols);let x=margin+widths.slice(0,col).reduce((a,b)=>a+b+gap,0),y=top+heights.slice(0,row).reduce((a,b)=>a+b+gap,0);
          if(recipe.orientation==='default'&&row===rows-1&&n%cols===1)x=(width-parsed[j].width)/2;
          svg.append(text(String.fromCharCode(65+j),x+1,y+10,9));
          parsed[j].svg.setAttribute('x',x);parsed[j].svg.setAttribute('y',y+17);svg.append(parsed[j].svg);
          positions.push({id:components[j].id,x_pt:x,y_pt:y+17,width_pt:parsed[j].width,height_pt:parsed[j].height,scale:1});
        }
        const footer=text('All panels retain their own data, units and guides; no inferred shared axis.',margin,height-8,6.7);footer.setAttribute('fill','#637381');svg.append(footer);
        document.querySelector('#stage').replaceChildren(svg);
        return {svg:new XMLSerializer().serializeToString(svg),width,height,positions,audit:window.FigurePublication.audit(svg)};
      },{recipe,components});
      if(result.width*result.height*(300/72)**2>80_000_000)throw Error('Composition exceeds bounded raster area');
      const dir=path.join(outDir,recipe.id);await fs.mkdir(dir,{recursive:false});
      await fs.writeFile(path.join(dir,recipe.id+'.svg'),result.svg,'utf8');
      await page.setViewportSize({width:Math.ceil(result.width*96/72)+2,height:Math.ceil(result.height*96/72)+2});
      if(Math.max(result.width,result.height)*300/72>16000){
        // Chromium may repeat pixels beyond a GPU texture boundary. Capture bounded
        // viewport tiles at exactly 300 DPI, then join bytes with Pillow, without resizing.
        const pixelWidth=Math.ceil(result.width*300/72),pixelHeight=Math.ceil(result.height*300/72),tile=6000,tiles=[];
        for(let y=0;y<pixelHeight;y+=tile)for(let x=0;x<pixelWidth;x+=tile){
          const w=Math.min(tile,pixelWidth-x),h=Math.min(tile,pixelHeight-y),file=path.join(dir,`tile-${x}-${y}.png`);
          await page.setViewportSize({width:Math.ceil(w*96/300),height:Math.ceil(h*96/300)});
          await page.evaluate(({x,y})=>{const stage=document.querySelector('#stage');stage.style.cssText='position:fixed;inset:0;overflow:hidden';const svg=stage.firstElementChild;svg.style.cssText=`position:absolute;left:${-x*96/300}px;top:${-y*96/300}px`;},{x,y});
          await page.screenshot({path:file,clip:{x:0,y:0,width:w*96/300,height:h*96/300},timeout:60000});tiles.push({file,x,y,w,h});
        }
        const join=path.join(dir,'tiles.json');await fs.writeFile(join,JSON.stringify({width:pixelWidth,height:pixelHeight,tiles}));
        await promisify(execFile)(process.env.FIGURE_IMAGE_PYTHON||(process.platform==='win32'?'python':'python3'),['-c','import json,sys;from PIL import Image;d=json.load(open(sys.argv[1]));out=Image.new("RGB",(d["width"],d["height"]),"white");[(out.paste(Image.open(t["file"]).crop((0,0,t["w"],t["h"])),(t["x"],t["y"]))) for t in d["tiles"]];out.save(sys.argv[2],dpi=(300,300))',join,path.join(dir,recipe.id+'.png')]);
        for(const t of tiles)await fs.unlink(t.file);await fs.unlink(join);
        await page.evaluate(()=>{document.querySelector('#stage').removeAttribute('style');document.querySelector('#stage > svg').removeAttribute('style')});
        await page.setViewportSize({width:Math.ceil(result.width*96/72)+2,height:Math.ceil(result.height*96/72)+2});
      }else await fs.writeFile(path.join(dir,recipe.id+'.png'),pngDpi(await page.locator('#stage > svg').screenshot({timeout:60000})));
      await page.pdf({path:path.join(dir,recipe.id+'.pdf'),width:result.width/72+'in',height:result.height/72+'in',margin:{top:0,bottom:0,left:0,right:0},printBackground:true,pageRanges:'1'});
      const outputs={};for(const ext of ['svg','png','pdf'])outputs[recipe.id+'.'+ext]=sha(await fs.readFile(path.join(dir,recipe.id+'.'+ext)));
      const receipt={schema_version:1,id:recipe.id,status:'COMPOSED_PENDING_VISUAL_REVIEW',source_recipe:recipe.source_id,
        arrangement:recipe.orientation,relationship:recipe.relationship,components:components.map(({svg,...c})=>c),
        component_placement:result.positions,width_pt:result.width,height_pt:result.height,output_sha256:outputs,
        geometry_audit:result.audit,scientific_acceptance:false,visual_acceptance:false,
        layout_policy:'Full independent panels at original physical scale; no shared-axis inference; source values unchanged'};
      await fs.writeFile(path.join(dir,recipe.id+'.json'),JSON.stringify(receipt,null,2)+'\n');
      records.push({id:recipe.id,issues:result.audit.issues.length,png_sha256:outputs[recipe.id+'.png']});
      process.stdout.write(JSON.stringify({composed:i+1,total:recipes.length,...records.at(-1)})+'\n');
    }catch(error){failures.push({id:recipe.id,error:error.message});process.stdout.write(JSON.stringify(failures.at(-1))+'\n')}
    await fs.writeFile(path.join(outDir,'composition-manifest.json'),JSON.stringify({status:failures.length?'PARTIAL_REQUIRES_REPAIR':'COMPOSED_PENDING_VISUAL_REVIEW',records,failures,external_requests:external},null,2)+'\n');
  }
  if(external.length)throw Error('Unexpected external browser request');
  if(failures.length)process.exitCode=1;
}finally{await browser.close()}
