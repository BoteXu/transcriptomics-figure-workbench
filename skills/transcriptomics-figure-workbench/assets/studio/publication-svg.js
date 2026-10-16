/* Finish a frozen SVG display. No input fitting, external resources or inference. */
(() => {
  const NS='http://www.w3.org/2000/svg',XLINK='http://www.w3.org/1999/xlink';
  const ink='#273540',muted='#637381';
  const node=(name,attrs={})=>{const el=document.createElementNS(NS,name);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,String(v));return el};
  const text=(value,x,y,size,color=ink)=>{const el=node('text',{x,y,fill:color,'font-family':'Arial, Liberation Sans, sans-serif','font-size':size,'font-weight':400});el.textContent=value;return el};
  const box=(el)=>{const b=el.getBBox();return {x:b.x,y:b.y,width:b.width,height:b.height}};
  const shapeRows=(root)=>[...root.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,use,image')]
    .filter(el=>!el.closest('defs')&&!el.closest('[data-page-background]'))
    .map(el=>[el.tagName,...[...el.attributes].filter(a=>!['style','class','id','fill','stroke','clip-path'].includes(a.name)).map(a=>[a.name,a.value]).sort()])
    .sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
  function safeParse(source){
    if(source.length>24*1024*1024||/<!ENTITY|<\?xml-stylesheet/i.test(source))throw Error('Unsupported SVG source');
    source=source.replace(/<!DOCTYPE svg PUBLIC[^>]+>/g,'');
    const doc=new DOMParser().parseFromString(source,'image/svg+xml');
    if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg'||doc.documentElement.namespaceURI!==NS||[...doc.childNodes].some(n=>n.nodeType===7))throw Error('Expected inert SVG');
    const svg=document.importNode(doc.documentElement,true);
    // Exporter metadata may use RDF/DC namespaces; it is not rendered or executed.
    svg.querySelectorAll('metadata').forEach(el=>el.remove());
    const allowed=new Set(['svg','g','defs','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','title','desc','clipPath','linearGradient','radialGradient','stop','pattern','image','use','style','symbol','mask','metadata']);
    for(const el of [svg,...svg.querySelectorAll('*')]){
      if(!allowed.has(el.localName)||el.namespaceURI!==NS)throw Error('Active or unsupported SVG refused');
      for(const attr of [...el.attributes]){
        if(/^on/i.test(attr.name))throw Error('SVG event handlers refused');
        if(/javascript:|@import|expression\s*\(/i.test(attr.value))throw Error('Active SVG style refused');
        if(['href','xlink:href'].includes(attr.name)&&!(attr.value.startsWith('#')||/^data:image\/(png|jpeg);base64,/.test(attr.value)))throw Error('External SVG reference refused');
        for(const match of attr.value.matchAll(/url\(([^)]+)\)/gi))if(!match[1].trim().replace(/^['"]|['"]$/g,'').startsWith('#'))throw Error('External paint reference refused');
      }
    }
    for(const style of svg.querySelectorAll('style'))if(/@import|url\(|javascript:|expression\s*\(/i.test(style.textContent))throw Error('External or active stylesheet refused');
    svg.querySelectorAll('metadata').forEach(el=>el.remove());
    return svg;
  }
  function realText(svg){return [...svg.querySelectorAll('text')].filter(el=>el.textContent.trim()&&el.getBoundingClientRect().width>0)}
  function audit(svg){
    const vb=svg.viewBox.baseVal, issues=[];
    const texts=realText(svg).map(el=>{const r=el.getBBox(),m=el.getCTM();return {el,b:el.getBoundingClientRect(),s:el.textContent.trim(),
      poly:[[r.x,r.y],[r.x+r.width,r.y],[r.x+r.width,r.y+r.height],[r.x,r.y+r.height]].map(([x,y])=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f}))}});
    const intersects=(p,q)=>{
      for(const shape of [p,q])for(let k=0;k<4;k++){
        const a=shape[k],b=shape[(k+1)%4],dx=-(b.y-a.y),dy=b.x-a.x,len=Math.hypot(dx,dy);
        if(!len)continue;const project=points=>points.map(v=>(v.x*dx+v.y*dy)/len),pp=project(p),qq=project(q);
        if(Math.min(Math.max(...pp),Math.max(...qq))-Math.max(Math.min(...pp),Math.min(...qq))<.6)return false;
      }return true;
    };
    const frame=svg.getBoundingClientRect();
    for(const {b,s}of texts){if(b.left<frame.left-1||b.top<frame.top-1||b.right>frame.right+1||b.bottom>frame.bottom+1)issues.push({kind:'text_clipping',text:s.slice(0,100)})}
    // Inspect text against text; geometric flags require visual review, never auto-certify aesthetics.
    for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
      const a=texts[i],b=texts[j];
      if(a.el.contains(b.el)||b.el.contains(a.el))continue;
      const w=Math.min(a.b.right,b.b.right)-Math.max(a.b.left,b.b.left),h=Math.min(a.b.bottom,b.b.bottom)-Math.max(a.b.top,b.b.top);
      if(w>1.5&&h>1.5&&w*h>.12*Math.min(a.b.width*a.b.height,b.b.width*b.b.height)&&intersects(a.poly,b.poly))issues.push({kind:'text_overlap',texts:[a.s.slice(0,80),b.s.slice(0,80)]});
    }
    return {scope:'Browser text bounds and text/text overlaps only; no perceptual acceptance',text_count:texts.length,issues,width_pt:vb.width,height_pt:vb.height};
  }
  function finish(source,context,patch={}){
    const svg=safeParse(source),host=document.getElementById('stage');host.replaceChildren(svg);
    svg.style.overflow='visible';const vb=svg.viewBox.baseVal;
    const originalWidth=vb.width,originalHeight=vb.height;
    if(!originalWidth||!originalHeight||originalWidth>5000||originalHeight>8000)throw Error('Bounded physical SVG dimensions required');
    svg.setAttribute('width',originalWidth);svg.setAttribute('height',originalHeight);
    // The figure background is page furniture rather than a data-encoded patch.
    const page=svg.querySelector('g[id="figure_1"] > g[id="patch_1"]');
    if(page)page.setAttribute('data-page-background','true');
    // Some exporters paint an identical legend twice. Remove only exact
    // duplicates after normalizing their generated IDs, before freezing data.
    const duplicateGuides=[];const seenGuides=new Set();
    for(const legend of [...svg.querySelectorAll('[id^="legend_"]')]){
      const clone=legend.cloneNode(true);
      clone.querySelectorAll('defs').forEach(el=>el.remove());
      for(const el of [clone,...clone.querySelectorAll('*')])el.removeAttribute('id');
      const key=clone.outerHTML.replace(/>\s+</g,'><').trim();
      if(seenGuides.has(key)){duplicateGuides.push(legend.id);legend.remove()}else seenGuides.add(key);
    }
    const before=JSON.stringify(shapeRows(svg));
    if(page)page.remove();
    const changes=['compact provenance','normal-weight title hierarchy','dark readable body labels','tight outer canvas'];
    if(duplicateGuides.length)changes.push('removed exact duplicate guide paint: '+duplicateGuides.join(', '));
    let title=context.title_en||'';const notes=[];
    const removed=[];
    for(const el of [...svg.querySelectorAll('text')]){
      const s=el.textContent.trim();
      if(/^SYNTHETIC (?:DEMO|LAYOUT EXAMPLE)/i.test(s)||/^Software test fixture[;:]|^Synthetic software fixture/i.test(s)){
        removed.push(s);el.remove();continue;
      }
      const size=parseFloat(getComputedStyle(el).fontSize)||9;
      if(!el.closest('[id^="axes_"]')&&s.length>4&&el.getBBox().y<originalHeight*.15&&size>=10.5&&!context.preserve_title){
        if(!title)title=s;
        removed.push(s);el.remove();continue;
      }
      el.style.fontFamily='Arial, Liberation Sans, sans-serif';
      const weight=parseInt(getComputedStyle(el).fontWeight)||400;
      if(weight>=600&&s.length>3){el.style.fontWeight='400';if(size>10.5)el.style.fontSize='10.5px'}
      const fill=getComputedStyle(el).fill;
      if(!['rgb(255, 255, 255)','white','#ffffff'].includes(fill)&&!context.preserve_text_colors)el.style.fill=ink;
    }
    // Source node, curve, tile, interval and image geometry remains byte-for-byte unchanged.
    // Groups may be translated as a whole; numeric coordinate axes are never rescaled independently.
    const axes=[...svg.querySelectorAll('[id^="axes_"]')];
    if(patch.axis_moves)for(const [id,shift]of Object.entries(patch.axis_moves)){
      const axis=svg.querySelector(`[id="${id}"]`);if(!axis)throw Error('Unknown axis move');
      const wrapper=node('g',{transform:`translate(${shift[0]} ${shift[1]})`});axis.replaceWith(wrapper);wrapper.append(axis);
      changes.push('explicit whole-axis spacing: '+id);
    }
    if(patch.group_moves)for(const [id,shift]of Object.entries(patch.group_moves)){
      const el=svg.querySelector(`[id="${id}"]`);if(!el)throw Error('Unknown layout group');
      const wrapper=node('g',{transform:`translate(${shift[0]} ${shift[1]})`});el.replaceWith(wrapper);wrapper.append(el);
      changes.push('explicit display-group spacing: '+id);
    }
    if(axes.length===1||context.title_en){
      for(const axis of axes)for(const child of [...axis.children]){
        const labels=[...child.querySelectorAll('text')];
        if(!/^text_/.test(child.id)||!labels.length)continue;
        const el=labels[0],s=child.textContent.trim(),size=parseFloat(getComputedStyle(el).fontSize)||9;
        if(s.length>5&&(s===context.title_en||(axes.length===1&&size>=10.5&&!el.getAttribute('transform')?.includes('rotate(-90')))){
          if(!title)title=s;else if(title!==s)notes.push(s);removed.push(s);child.remove();
        }
      }
    }
    const guides=[...svg.querySelectorAll('[id^="legend_"]')].filter(el=>!el.parentElement.closest('[id^="legend_"]'));
    const rootGroup=svg.querySelector('g[id="figure_1"]')||svg;
    if(rootGroup!==svg)for(const child of [...rootGroup.children]){
      if(!/^text_/.test(child.id)||!child.querySelector('text'))continue;
      const values=[...child.querySelectorAll('text')].map(t=>t.textContent.trim()).filter(Boolean);
      if(values.length&&values.join('').length>3){notes.push(values.join(' '));child.remove()}
    }
    const primaryAxes=axes.filter(ax=>ax.querySelector('[id^="matplotlib.axis_"]')||ax.querySelectorAll('[id^="PathCollection"],[id^="line2d"],[id^="FillBetween"]').length>0);
    if(patch.guide_axis_ids){
      const group=node('g');svg.append(group);
      for(const id of patch.guide_axis_ids){const el=svg.querySelector(`[id="${id}"]`);if(!el)throw Error('Unknown guide axis');group.append(el)}
      const main=box(rootGroup),b=box(group);group.setAttribute('transform',`translate(${main.x+main.width+(patch.guide_gap_pt??16)-b.x} 0)`);
      changes.push('explicit compact guide-axis column');
    }else if(axes.length===1&&guides.length){
      const wraps=[];
      for(const guide of guides){const wrap=node('g');guide.replaceWith(wrap);wrap.append(guide);svg.append(wrap);wraps.push(wrap)}
      const b=box(rootGroup),gap=patch.guide_gap_pt??16;let y=b.y;
      for(const wrap of wraps){const r=box(wrap);const onTop=patch.guide_position==='top'||(!patch.guide_position&&r.width>r.height*4);wrap.setAttribute('transform',onTop?`translate(${b.x-r.x} ${b.y-gap-r.y-r.height})`:`translate(${b.x+b.width+gap-r.x} ${y-r.y})`);y+=r.height+9}
      changes.push('independent compact guide lane');
    }
    const body=node('g',{'data-publication-body':'true'});
    for(const child of [...svg.children])if(!['defs','style','metadata'].includes(child.localName))body.append(child);
    svg.append(body);
    if(patch.remove_texts){for(const el of [...body.querySelectorAll('text')])if(patch.remove_texts.includes(el.textContent.trim()))el.remove()}
    if(patch.text_moves){for(const [label,shift]of Object.entries(patch.text_moves))for(const el of [...body.querySelectorAll('text')])if(el.textContent.trim()===label){const wrap=node('g',{transform:`translate(${shift[0]} ${shift[1]})`});el.replaceWith(wrap);wrap.append(el)}}
    if(patch.foreground_axis_text){
      const labels=[...body.querySelectorAll('[id^="matplotlib.axis_"] text')];
      for(const el of labels){const m=body.getCTM().inverse().multiply(el.getCTM()),style=getComputedStyle(el),wrap=node('g',{transform:`matrix(${m.a} ${m.b} ${m.c} ${m.d} ${m.e} ${m.f})`});
        el.setAttribute('style',`font:${style.font};fill:${style.fill};text-anchor:${style.textAnchor};dominant-baseline:${style.dominantBaseline};stroke:white;stroke-width:2.8;stroke-linejoin:round;paint-order:stroke fill`);el.removeAttribute('transform');wrap.append(el);body.append(wrap)}
      changes.push('axis text painted above gutter links with white backing');
    }
    if(patch.color_map)for(const el of body.querySelectorAll('*')){
      const style=el.getAttribute('style');if(style)el.setAttribute('style',style.replace(/#[0-9a-fA-F]{6}/g,c=>patch.color_map[c.toLowerCase()]||c));
      for(const name of ['fill','stroke']){const v=el.getAttribute(name);if(v&&patch.color_map[v.toLowerCase()])el.setAttribute(name,patch.color_map[v.toLowerCase()])}
    }
    if(patch.color_map)changes.push('explicit consistent color map: '+JSON.stringify(patch.color_map));
    if(patch.element_opacity){
      for(const [id,opacity]of Object.entries(patch.element_opacity)){
        if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(id)||!Number.isFinite(opacity)||opacity<.1||opacity>1)throw Error('Invalid bounded decorative opacity');
        const target=[...body.querySelectorAll('[id]')].find(el=>el.id===id);
        if(!target)throw Error('Unknown decorative opacity target');
        for(const el of [target,...target.querySelectorAll('path,use,polygon,circle')]){
          if(el.getAttribute('style')?.includes('opacity:')){
            el.style.opacity=String(opacity);el.style.fillOpacity=String(opacity);el.style.strokeOpacity=String(opacity);
            // Use one alpha channel; avoid multiplying three replacement alphas.
            el.style.opacity='1';
          }
        }
      }
      changes.push('explicit bounded decorative-opacity repair');
    }
    if(patch.body_bounds)changes.push('explicit visible-body bounds: '+JSON.stringify(patch.body_bounds));
    const b=patch.body_bounds?{x:patch.body_bounds[0],y:patch.body_bounds[1],width:patch.body_bounds[2],height:patch.body_bounds[3]}:box(body),fontSizes=[...body.querySelectorAll('text')].filter(el=>el.textContent.trim().length>2).map(el=>parseFloat(getComputedStyle(el).fontSize)||9).filter(n=>n>=5).sort((a,b)=>a-b);
    const low=fontSizes[Math.floor(fontSizes.length*.03)]||9;
    const scale=patch.scale??Math.max(1,Math.min(1.55,7.3/low));
    const left=18,top=53,width=Math.max(260,b.width*scale+36);
    if(patch.notes){if(!Array.isArray(patch.notes)||patch.notes.some(s=>typeof s!=='string'||s.length>1000))throw Error('Invalid display notes');notes.push(...patch.notes);changes.push('explicit retained context notes')}
    const noteLines=[];
    for(const value of notes){
      const words=value.split(/\s+/);let line='';
      for(const word of words){const next=line?line+' '+word:word;if(next.length>(width-36)/3.6){if(line)noteLines.push(line);line=word}else line=next}if(line)noteLines.push(line);
    }
    const height=b.height*scale+top+24+(noteLines.length?noteLines.length*9+10:0);
    if(width*height>2_000_000)throw Error('Figure exceeds bounded page area');
    body.setAttribute('transform',`translate(${left-b.x*scale} ${top-b.y*scale}) scale(${scale})`);
    svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('width',width+'pt');svg.setAttribute('height',height+'pt');
    svg.insertBefore(node('rect',{x:0,y:0,width,height,fill:'white','data-page-background':'true'}),svg.firstChild);
    title=patch.title||title||context.kind?.replace(/_/g,' ')||'Frozen result';
    const titleNode=text(title,18,33,10.5);svg.append(titleNode);
    // Long scientific titles are retained in full on a separate header row.
    if(titleNode.getComputedTextLength()>width-36){
      let size=10.5;
      while(titleNode.getComputedTextLength()>width-36&&size>8){size-=.25;titleNode.setAttribute('font-size',size)}
      if(titleNode.getComputedTextLength()>width-36)throw Error('Title needs an explicit wrapped layout');
    }
    const provenance=context.role==='palette'?'REFERENCE COLOR CARD':context.synthetic?'SYNTHETIC DEMO':'PUBLIC COORDINATES';
    const badge=text(provenance+' | '+context.id,width-18,12,6.5,muted);badge.setAttribute('text-anchor','end');svg.append(badge);
    const footer=text(context.role==='palette'?'Exact declared colors retained':context.synthetic?'Frozen display; no biological inference':'Original structure raster retained; display frame updated',18,height-8,6.7,muted);svg.append(footer);
    noteLines.forEach((value,i)=>svg.append(text(value,18,top+b.height*scale+16+i*9,7.2,ink)));
    const after=JSON.stringify(shapeRows(body));
    if(before!==after)throw Error('Frozen graphical geometry changed unexpectedly');
    const axisGeometry=(context.axes||[]).map(a=>{
      const [x,y,w,h]=a.bounds;return {...a,rect_pt:[left+(x*originalWidth-b.x)*scale,top+((1-y-h)*originalHeight-b.y)*scale,w*originalWidth*scale,h*originalHeight*scale]};
    });
    return {svg:new XMLSerializer().serializeToString(svg),width_pt:width,height_pt:height,
      audit:audit(svg),geometry_fingerprint:before,axis_geometry:axisGeometry,
      changes,removed_page_furniture:removed,source_viewbox:[originalWidth,originalHeight],body_transform:{scale,translate:[left-b.x*scale,top-b.y*scale]}};
  }
  window.FigurePublication={finish,audit,safeParse};
})();
