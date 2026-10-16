'use strict';
const DATA=JSON.parse(document.getElementById('studio-data').textContent);
const $=s=>document.querySelector(s);
const state={selected:null,example:null,spec:null,original:null,finished:null,publicationReceipt:null,edited:null,sourceHash:null,expectedSvgHash:null,zoom:1,board:[],urls:[]};
const presets={paper:[10,9,11,8],compact:[9,8,10,7],presentation:[15,13,17,11],large_print:[13,12,15,10]};
const names={raincloud:'雨云图',paired:'配对观测',heatmap:'热图',dot_matrix:'点阵矩阵',forest:'效应区间森林图',
  volcano:'火山图',volcano_marginal:'火山图与边际分布',upset:'集合交集 UpSet',rank_bump:'排名变化',
  running_enrichment:'已有富集曲线',frozen_curve:'已有 ROC / PR 曲线',qc_de:'转录组 QC / DE 结果',
  effect_matrix:'效应区间矩阵',splice_tracks:'剪接轨道',sequence_logo:'序列字母堆叠',typed_network:'类型互作网络'};
function message(text){$('#message').textContent=text;}
function title(row){return row.display_name||row.aliases.map(a=>names[a]).find(Boolean)||row.function.replace(/^plot_/,'').replaceAll('_',' ');}
function download(name,text,type='application/json'){
  const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
}
async function sha(text){
  const bytes=typeof text==='string'?new TextEncoder().encode(text):text;
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');
}
function safeSVG(text){
  if(text.length>5*1024*1024||/<!ENTITY/i.test(text))throw Error('SVG 太大或含有实体声明。');
  const clean=text.replace(/<!DOCTYPE[^>]*>/gi,'');
  const doc=new DOMParser().parseFromString(clean,'image/svg+xml');
  if([...doc.childNodes].some(n=>n.nodeType===7))throw Error('SVG 含有外部处理指令。');
  if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg'||doc.documentElement.namespaceURI!=='http://www.w3.org/2000/svg')throw Error('文件不是有效 SVG。');
  doc.querySelectorAll('metadata').forEach(n=>n.remove());
  const allowed=new Set(['svg','g','defs','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','title','desc','clipPath','linearGradient','radialGradient','stop','pattern','image','use','style','symbol','mask']);
  for(const node of doc.querySelectorAll('*')){
    if(!allowed.has(node.localName))throw Error('SVG 含有不支持的活动或外部内容：'+node.localName);
    for(const attr of [...node.attributes]){
      if(/^on/i.test(attr.localName))throw Error('SVG 含有事件脚本。');
      if(attr.localName==='href'&&!/^#[\w:.-]+$/.test(attr.value)&&!/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+$/.test(attr.value))throw Error('SVG 引用了外部资源。');
      if(/(?:javascript:|@import|expression\s*\()/i.test(attr.value))throw Error('SVG 含有活动样式。');
      const urls=attr.value.match(/url\s*\([^)]*\)/gi)||[];
      if(urls.some(u=>!/^url\s*\(['"]?#[\w:.-]+['"]?\)$/i.test(u)))throw Error('SVG 样式引用了外部资源。');
    }
    if(node.localName==='style'){
      const css=node.textContent;
      if(/@import|expression\s*\(|javascript:/i.test(css)||(css.match(/url\s*\([^)]*\)/gi)||[]).some(u=>!/^url\s*\(['"]?#[\w:.-]+['"]?\)$/i.test(u)))throw Error('SVG 样式包含外部内容。');
    }
  }
  return doc;
}
function geometry(doc){
  return JSON.stringify([...doc.querySelectorAll('*')].map(n=>{
    const clone=n.cloneNode(false);
    if(['text','tspan'].includes(n.localName)){
      clone.style.removeProperty('font-family');clone.style.removeProperty('font-size');
      if(!clone.getAttribute('style'))clone.removeAttribute('style');
    }
    return [n.localName,[...clone.attributes].map(a=>[a.name,a.value]).sort((a,b)=>a[0].localeCompare(b[0])),
      ['text','tspan'].includes(n.localName)?n.textContent:null];
  }));
}
function appearance(){
  const sizes=presets[$('#preset').value],factor=Number($('#text-scale').value)/100;
  return {preset:$('#preset').value,font_family:$('#font-family').value.trim()||'Arial',
    label_pt:+(sizes[0]*factor).toFixed(2),tick_pt:+(sizes[1]*factor).toFixed(2),
    title_pt:+(sizes[2]*factor).toFixed(2),note_pt:+(sizes[3]*factor).toFixed(2)};
}
function changedSVG(text,font,scale){
  const doc=safeSVG(text),before=geometry(doc);
  for(const node of doc.querySelectorAll('text,tspan')){
    const explicit=node.style.fontSize||node.getAttribute('font-size');
    let size=parseFloat(explicit),unit=(explicit||'').replace(/^[\d.]+/,'')||'px';
    if(!Number.isFinite(size)){
      const match=(node.getAttribute('style')||'').match(/font:\s*([\d.]+)(px|pt)/);
      if(match){size=Number(match[1]);unit=match[2];}
      else if(node.localName==='text'){size=12;unit='px';}
    }
    node.style.fontFamily=font;
    if(Number.isFinite(size))node.style.fontSize=(size*scale).toFixed(3)+unit;
  }
  if(geometry(doc)!==before)throw Error('预览修改影响了坐标或其他图形属性，已阻止。');
  return new XMLSerializer().serializeToString(doc);
}
function svgFrame(svg){
  const html='<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\';style-src \'unsafe-inline\';img-src data:;base-uri \'none\'"><style>body{margin:0;background:#fff}svg{display:block;width:100%;height:auto}</style>'+svg;
  const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'}));state.urls.push(url);
  const frame=document.createElement('iframe');frame.sandbox='';frame.className='svg-frame';frame.title='离线 SVG 图形预览';frame.src=url;
  const bounds=safeSVG(svg).documentElement.getAttribute('viewBox')?.trim().split(/[\s,]+/).map(Number);
  if(bounds?.length===4&&bounds[2]>0&&bounds[3]>0)frame.style.aspectRatio=bounds[2]+'/'+bounds[3];
  return frame;
}
function renderSVG(){
  if(!state.original)return;
  if(state.expectedSvgHash&&state.sourceHash&&state.expectedSvgHash!==state.sourceHash){
    state.edited=null;$('#preview-content').textContent='SVG 与所选导出记录不一致，请载入对应文件。';
    $('#before-view').replaceChildren();$('#after-view').replaceChildren();message('文件哈希不匹配，已阻止关联编辑。');return false;
  }
  try{
    state.edited=changedSVG(state.finished||state.original,$('#font-family').value.trim()||'Arial',Number($('#text-scale').value)/100);
    state.urls.forEach(URL.revokeObjectURL);state.urls=[];
    $('#preview-content').replaceChildren(svgFrame(state.edited));
    $('#before-view').replaceChildren(svgFrame(new XMLSerializer().serializeToString(safeSVG(state.original))));
    $('#after-view').replaceChildren(svgFrame(state.edited));
    $('#preview-state').textContent='PREVIEW_EDIT_UNREVIEWED';
    $('#scale-value').textContent=$('#text-scale').value+'%';
  }catch(e){message(e.message);return false;}
}
function showRenderer(row){
  state.selected=row;$('#figure-title').textContent=title(row);$('#figure-subtitle').textContent=row.summary||'从已审核的结果表绘制；参数约束见实际实现和来源记录。';
  $('#eyebrow').textContent=row.id;$('#renderer-detail').replaceChildren();
  const note=document.createElement('p');note.textContent='已实现源码；运行、视觉和科学验收分别记录。';$('#renderer-detail').append(note);
  for(const p of row.parameters){const div=document.createElement('div');div.className='param';const key=document.createElement('b');key.textContent=p.name;div.append(key);
    const small=document.createElement('div');small.className=p.required?'required':'';small.textContent=p.required?'必填':'默认 '+JSON.stringify(p.default);div.append(small);$('#renderer-detail').append(div);}
  renderCatalog();
}
function showExample(item,design=false){
  state.example=item;state.original=null;state.finished=null;state.publicationReceipt=null;state.edited=null;state.sourceHash=null;
  $('#figure-title').textContent=item.title;$('#figure-subtitle').textContent=item.input_shape;$('#eyebrow').textContent=(design?'当前优选 ':'历史来源 ')+item.id;
  const image=document.createElement('img');image.src=item.png;image.alt=item.title;$('#preview-content').replaceChildren(image);
  $('#before-view').replaceChildren(image.cloneNode());$('#after-view').replaceChildren(image.cloneNode());$('#preview-state').textContent=design?'DESIGN_EXAMPLE_SYNTHETIC':'历史合成示例 · 原编号保留';
  const open=document.createElement('a');open.href=item.source;open.textContent='查看原示例、输入表与来源';open.target='_blank';open.rel='noopener';
  const add=document.createElement('button');add.textContent='添加到组图草案';add.onclick=()=>{if(!state.board.some(x=>x.id===item.id))state.board.push(item);renderBoard();message('已加入组图草案；完整面板仍可独立使用。');};
  $('#renderer-detail').replaceChildren(open,document.createElement('br'),add);renderCatalog();
}
function showMethod(entry){
  state.method=entry;state.selected=null;state.example=null;
    state.original=null;state.finished=null;state.publicationReceipt=null;state.edited=null;state.sourceHash=null;state.expectedSvgHash=null;state.spec=null;
    state.urls.forEach(URL.revokeObjectURL);state.urls=[];
    $('#preview-content').replaceChildren();$('#before-view').replaceChildren();$('#after-view').replaceChildren();
    if(entry.example_files){const image=document.createElement('img');image.src=entry.example_files.png;image.alt=entry.id+' 合成结果表示例';image.id='method-example';image.style.maxWidth='100%';$('#preview-content').append(image);$('#preview-state').textContent='PACKAGE_EXAMPLE_SYNTHETIC';}
  $('#figure-title').textContent=entry.id;$('#figure-subtitle').textContent=entry.purpose;$('#eyebrow').textContent=entry.package;
  const box=$('#renderer-detail');box.replaceChildren();
  for(const [key,value] of [['绘图器',entry.renderer],['输入字段',entry.required_columns.join(', ')],['必须说明',entry.required_context.join('; ')],['固定参数',JSON.stringify(entry.fixed_parameters)],['接入方式',entry.input_route]]){const p=document.createElement('p');p.textContent=key+'：'+value;box.append(p)}
  const b=document.createElement('button');b.textContent='导出专用入口说明';b.onclick=()=>download(entry.id+'.entry.json',JSON.stringify(entry,null,2));box.append(b);
    if(entry.example_files){const links=document.createElement('p');for(const kind of ['svg','pdf','tsv','spec','gallery']){const a=document.createElement('a');a.href=entry.example_files[kind];a.textContent=kind.toUpperCase();a.target='_blank';a.rel='noopener';links.append(a,document.createTextNode('  '));}box.append(links);}
  const hint=document.createElement('p');hint.textContent='用 method-spec 绑定已选择的结果表、课题主题和来源，再 plan / render。不会在本机执行原软件包。';box.append(hint);renderCatalog();
}
function renderCatalog(){
  const mode=$('#catalog-mode').value,design=mode==='design',example=mode==='example'||design,method=mode==='method',query=$('#search').value.trim().toLocaleLowerCase();
  const rows=(design?DATA.design_examples:example?DATA.examples:method?DATA.method_entries:DATA.registry.renderers).filter(r=>JSON.stringify(r).toLocaleLowerCase().includes(query)||(!example&&!method&&title(r).toLocaleLowerCase().includes(query)));
  $('#catalog-count').textContent=rows.length;$('#catalog-list').replaceChildren();
  for(const row of rows){const b=document.createElement('button');b.textContent=example?row.title:method?row.id:title(row);
    b.className=(example?state.example?.id===row.id:method?state.method?.id===row.id:state.selected?.id===row.id)?'active':'';
    const small=document.createElement('small');small.textContent=example?row.id:method?row.package:(row.aliases.join(' · ')||row.function);b.append(small);b.onclick=()=>example?showExample(row,design):method?showMethod(row):showRenderer(row);$('#catalog-list').append(b);}
  if(example&&!design&&!DATA.examples.length)message('此安装版未附带历史图库。可在构建 Studio 时选定现有完整图库，或导入本机 SVG。');
}

let dragged=null,boardSerial=0;
function boardColumns(){const x=$('#board-columns').value;return x==='auto'?Math.max(1,Math.floor((Number($('#board-width').value)-30)/338)):x==='custom'?Number($('#board-custom-columns').value):Number(x);}
function boardRequest(){
  const cols=boardColumns(),width=Number($('#board-width').value),gap=Number($('#board-gap').value);
  if(!Number.isInteger(cols)||cols<1||cols>64||!Number.isFinite(width)||width<120||width>14400||!Number.isFinite(gap)||gap<0||gap>300)throw Error('请检查列数、画布宽度和间距。');
  const req={id:'SelectedLayout',canvas_width_pt:width,columns:cols,gap_pt:gap,panels:[],source_files_selected:state.board.every(x=>x.svg_filename)};
  for(const [id,key] of [['board-rows','rows'],['board-page-rows','max_rows_per_page']])if($('#'+id).value){const n=Number($('#'+id).value);if(!Number.isInteger(n)||n<1||n>1000)throw Error('行数须为正整数。');req[key]=n;}
  if($('#board-weights').value.trim()){req.column_weights=$('#board-weights').value.split(/[,，\s]+/).map(Number);if(req.column_weights.length!==cols||req.column_weights.some(n=>!Number.isFinite(n)||n<=0))throw Error('请为每一列填写一个正的宽度占比。');}
  req.panels=state.board.map((item,i)=>{const p={id:item.id,label:i<26?String.fromCharCode(65+i):String(i+1),svg:item.svg_filename||null,sha256:item.svg_sha256||null,row_span:item.row_span||1,column_span:item.column_span||1};
    if(p.column_span>cols)throw Error('面板跨列数超过当前列数。');
    if(item.grid_row||item.grid_column){if(!item.grid_row||!item.grid_column)throw Error('指定位置时，请同时填写行和列。');p.row=item.grid_row-1;p.column=item.grid_column-1;}
    if(item.height_pt)p.height_pt=item.height_pt;
    return p;});
  const occupied=new Set();
  for(const p of req.panels){if(p.row===undefined)continue;if(p.column+p.column_span>cols)throw Error('指定位置加跨列数超出画布。');for(let r=p.row;r<p.row+p.row_span;r++)for(let c=p.column;c<p.column+p.column_span;c++){const cell=r+','+c;if(occupied.has(cell))throw Error('指定位置的面板重叠，请调整行列。');occupied.add(cell);}}
  return req;
}
function layoutBoard(){
  const grid=$('#board-grid');let req;try{req=boardRequest();}catch(e){message(e.message);return;}
  grid.style.gridTemplateColumns=(req.column_weights||Array(req.columns).fill(1)).map(v=>`minmax(0,${v}fr)`).join(' ');grid.style.gap=req.gap_pt+'px';grid.style.gridAutoRows='minmax(160px,auto)';
  [...grid.children].forEach((panel,index)=>{const item=state.board[index];if(!item)return;panel.style.gridColumn=(item.grid_column?item.grid_column+' / ':'')+'span '+(item.column_span||1);panel.style.gridRow=(item.grid_row?item.grid_row+' / ':'')+'span '+(item.row_span||1);});
}
function renderBoard(){
  const grid=$('#board-grid');let req;try{req=boardRequest();}catch(e){message(e.message);return;}
  grid.style.gridTemplateColumns=(req.column_weights||Array(req.columns).fill(1)).map(v=>`minmax(0,${v}fr)`).join(' ');grid.style.gap=req.gap_pt+'px';grid.style.gridAutoRows='minmax(160px,auto)';grid.replaceChildren();
  state.board.forEach((item,index)=>{const panel=document.createElement('article');panel.className='board-panel';panel.draggable=true;
    panel.style.gridColumn=(item.grid_column?item.grid_column+' / ':'')+'span '+(item.column_span||1);panel.style.gridRow=(item.grid_row?item.grid_row+' / ':'')+'span '+(item.row_span||1);
    panel.ondragstart=()=>{dragged=index;};panel.ondragover=e=>e.preventDefault();panel.ondrop=e=>{e.preventDefault();if(dragged!==null&&dragged!==index){const [v]=state.board.splice(dragged,1);state.board.splice(index,0,v);renderBoard();}dragged=null;};
    const image=document.createElement('img');image.src=item.png;image.alt=item.title;const label=document.createElement('div');const span=document.createElement('span');span.textContent=String.fromCharCode(65+index)+' · '+item.id;
    const remove=document.createElement('button');remove.textContent='移除';remove.onclick=()=>{if(item.board_url)URL.revokeObjectURL(item.board_url);state.board.splice(index,1);renderBoard();};label.append(span,remove);panel.append(image,label);
    const controls=document.createElement('div');controls.className='panel-layout-controls';
    for(const [key,name,def] of [['row_span','跨行',1],['column_span','跨列',1],['grid_row','指定行',null],['grid_column','指定列',null],['height_pt','高度pt',null]]){const l=document.createElement('label');l.textContent=name;const inp=document.createElement('input');inp.type='number';inp.min='1';inp.value=item[key]||def||'';inp.placeholder=def?'':'自动';inp.setAttribute('aria-label',item.id+' '+name);inp.onchange=()=>{const v=inp.value?Number(inp.value):null;if(v!==null&&(!Number.isFinite(v)||v<1||!Number.isInteger(v))){message('布局使用正整数。');return;}item[key]=v;renderBoard();};l.append(inp);controls.append(l);}
    panel.append(controls);grid.append(panel);});
}
$('#board-svg-files').onchange=async e=>{try{for(const file of e.target.files){if(state.board.length>=100)throw Error('浏览器草案最多100面板；更多面板请用有界布局命令分页。');if(file.size>5*1024**2)throw Error('单张SVG需不超过5MiB。');const raw=await file.text(),doc=safeSVG(raw),hash=await sha(raw);if(state.board.some(x=>x.svg_filename===file.name&&x.svg_sha256===hash))continue;
 if(state.board.some(x=>x.svg_filename===file.name&&x.svg_sha256!==hash))throw Error('不同内容的SVG不能使用相同文件名，请先重命名。');
 let id;do{id='Panel_'+(++boardSerial);}while(state.board.some(x=>x.id===id));const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(doc)],{type:'image/svg+xml'}));state.board.push({id,title:file.name,png:url,board_url:url,svg_filename:file.name,svg_sha256:hash});}renderBoard();message('已载入完整本机面板，未上传；布局请求需与这些源文件一起保存。');}catch(err){message(err.message);}e.target.value='';};
function swatches(){
  $('#color-swatches').replaceChildren();for(const color of state.spec?.theme?.palette_colors||[]){if(!/^#[a-f0-9]{6}$/i.test(color))continue;const span=document.createElement('span');span.style.backgroundColor=color;span.title=color;$('#color-swatches').append(span);}
}
$('#svg-file').onchange=async e=>{
  const file=e.target.files[0];if(!file)return;
  try{if(file.size>5*1024*1024)throw Error('请载入不超过 5 MiB 的单张 SVG。');const bytes=await file.arrayBuffer();const text=new TextDecoder().decode(bytes);safeSVG(text);
    state.finished=null;state.publicationReceipt=null;state.sourceHash=await sha(bytes);state.original=text;state.example=null;$('#asset-label').textContent=file.name+' · SHA256 '+state.sourceHash.slice(0,12);
    if(renderSVG()!==false)message(state.expectedSvgHash?'SVG 与导出记录哈希一致；当前修改仍是未验收预览。':'SVG 已载入；未绑定导出记录，当前仅作文字预览。');
  }catch(error){message(error.message);}e.target.value='';};
$('#spec-file').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{
  if(file.size>2*1024*1024)throw Error('配置文件超过 2 MiB。');const loaded=JSON.parse(await file.text());
  const spec=loaded.workbench?.spec||loaded;
  if(spec.schema_version!==1||!spec.input||!spec.parameters||!spec.theme||!spec.provenance||typeof spec.figure_id!=='string')throw Error('请选择 FigureSpec 配置。');
  state.spec=spec;state.expectedSvgHash=loaded.workbench?loaded.output_sha256?.[loaded.figure_id+'.svg']||null:null;
  $('#font-family').value=spec.appearance?.font_family||spec.theme.font_family||'Arial';$('#preset').value=spec.appearance?.preset||'paper';
  $('#raster-dpi').value=String(spec.export?.raster_dpi||300);$('#include-tiff').checked=spec.export?.tiff===true;
  $('#target-width').value=String(spec.export?.target_width_mm||178);$('#minimum-text').value=String(spec.export?.minimum_text_pt||7);
  const row=DATA.registry.renderers.find(r=>r.id===spec.renderer||r.aliases.includes(spec.renderer));if(row)showRenderer(row);swatches();renderSVG();
  if(!state.expectedSvgHash||!state.sourceHash)message('配置已载入；SVG 与配置尚未做文件绑定。可载入对应导出记录核对，再准备重绘。');
  else if(state.expectedSvgHash===state.sourceHash)message('SVG 与导出记录哈希一致。外观修改仍需重绘与最终验收。');
}catch(error){message(error.message);}e.target.value='';};
$('#export-spec').onclick=()=>{
  const app=appearance();if(!state.spec){download('appearance.json',JSON.stringify(app,null,2));message('已导出外观设置；原数据与参数未知，未生成绘图结果。');return;}
  const spec=JSON.parse(JSON.stringify(state.spec));spec.appearance=app;spec.figure_id=spec.figure_id+'_restyled';
  const width=Number($('#target-width').value),minimum=Number($('#minimum-text').value);
  if(!Number.isFinite(width)||width<40||width>1000||!Number.isFinite(minimum)||minimum<5||minimum>30){message('请填写有效的目标宽度和最小字号。');return;}
  spec.export={...spec.export,raster_dpi:Number($('#raster-dpi').value),tiff:$('#include-tiff').checked,target_width_mm:width,minimum_text_pt:minimum,readability_policy:'block'};
  download(spec.figure_id+'.spec.json',JSON.stringify(spec,null,2));message('已导出重绘配置。请保存在原配置旁以保留相对数据路径，再预检与重绘。');
};
$('#publication-finish').onclick=async()=>{
  if(!state.original){message('请先载入本机 SVG。');return;}
  if(state.expectedSvgHash&&state.sourceHash!==state.expectedSvgHash){message('文件哈希不匹配，已阻止版式整理。');return;}
  try{
    const result=window.FigurePublication.finish(state.original,{id:'LOCAL_PREVIEW',synthetic:false,title_en:'Frozen result'},{});
    state.finished=result.svg;state.publicationReceipt={status:'PUBLICATION_PREVIEW_UNREVIEWED',source_svg_sha256:await sha(state.original),changes:result.changes,geometry_audit:result.audit,output_svg_sha256:await sha(result.svg),visual_acceptance:false,scientific_acceptance:false};
    if(renderSVG()===false)throw Error('预览未成功。');
    $('#preview-state').textContent='PUBLICATION_PREVIEW_UNREVIEWED';
    message('已整理标题、正文和留白；冻结数值图形保持。请放大检查实际预览。');
  }catch(e){state.finished=null;state.publicationReceipt=null;message('未整理：'+e.message);}
};
$('#form-polish').onclick=async()=>{
  if(!state.original){message('请先载入本机 SVG。');return;}
  if(state.expectedSvgHash&&state.sourceHash!==state.expectedSvgHash){message('文件哈希不匹配，已阻止版式整理。');return;}
  try{
    const result=window.FigureFormPolish.finish(state.original,{id:'LOCAL_PREVIEW',kind:'frozen_display',profile:'journal',context:{title_en:state.spec?.title||'Frozen result'}},{});
    const safeResult=window.FigurePublication.safeParse(result.svg);
    for(const n of safeResult.querySelectorAll('text'))if(n.textContent==='SYNTHETIC DISPLAY · frozen values')n.textContent='FROZEN RESULT · source-bound preview';
    result.svg=new XMLSerializer().serializeToString(safeResult);
    state.finished=result.svg;state.publicationReceipt={status:'SAME_FORM_PREVIEW_UNREVIEWED',source_svg_sha256:await sha(state.original),changes:result.changes,retained_notes:result.retained_notes,geometry_audit:result.audit,output_svg_sha256:await sha(result.svg),visual_acceptance:false,scientific_acceptance:false,target_size_assessed:false};
    if(renderSVG()===false)throw Error('预览未成功。');
    $('#preview-state').textContent='SAME_FORM_PREVIEW_UNREVIEWED';
    message('已应用同图型整理，保留数值图形和科学标注；请逐项检查标签、图例、留白与实际尺寸。');
  }catch(e){state.finished=null;state.publicationReceipt=null;message('未整理：'+e.message);}
};
$('#export-svg').onclick=()=>{if(!state.edited){message('请先载入本机 SVG。');return;}download('preview-unreviewed.svg',state.edited,'image/svg+xml');if(state.publicationReceipt){sha(state.edited).then(hash=>download('preview-unreviewed.review.json',JSON.stringify({...state.publicationReceipt,output_svg_sha256:hash},null,2)));}message('已下载未验收 SVG 预览；正式输出仍需重绘并检查最终尺寸。');};
$('#export-board').onclick=()=>{if(!state.board.length){message('先选择面板。');return;}try{const req=boardRequest();download('composition-draft.json',JSON.stringify({...req,schema_version:1,status:'LAYOUT_DRAFT',shared_data_axes_declared:false,final_export_created:false},null,2));message(req.source_files_selected?'已导出源文件绑定请求；将请求保存在源SVG旁，再做layout-plan和layout-export。':'已导出参考草案；选择对应本机SVG后才能执行布局。');}catch(e){message(e.message);}};
$('#search').oninput=renderCatalog;$('#catalog-mode').onchange=renderCatalog;$('#board-columns').onchange=layoutBoard;
for(const id of ['board-custom-columns','board-width','board-rows','board-gap','board-weights','board-page-rows'])$('#'+id).onchange=layoutBoard;
for(const id of ['font-family','text-scale'])$('#'+id).oninput=()=>{renderSVG();$('#scale-value').textContent=$('#text-scale').value+'%';};
$('#preset').onchange=()=>message('场景字号已写入重绘设置；SVG 预览只应用所选文字缩放，最终排版请重新绘制。');
$('#reset-edit').onclick=()=>{state.finished=null;state.publicationReceipt=null;$('#text-scale').value='100';$('#font-family').value=state.spec?.theme?.font_family||'Arial';renderSVG();};
function zoom(delta){state.zoom=Math.max(.5,Math.min(2,state.zoom+delta));$('#preview-content').style.transform='scale('+state.zoom+')';$('#zoom-value').textContent=Math.round(state.zoom*100)+'%';}
$('#zoom-in').onclick=()=>zoom(.1);$('#zoom-out').onclick=()=>zoom(-.1);
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(t=>t.classList.toggle('active',t===b));document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id===b.dataset.tab));});
$('#help').onclick=()=>$('#help-dialog').showModal();$('#close-help').onclick=()=>$('#help-dialog').close();
renderCatalog();swatches();
if(DATA.demo_svg){state.original=DATA.demo_svg;renderSVG();$('#asset-label').textContent='SYNTHETIC DEMO · 冻结结果示例';}
else if(DATA.design_examples?.length){showExample(DATA.design_examples[0],true);}
window.FigureStudioCore={safeSVG,changedSVG,geometry,appearance,boardRequest};
