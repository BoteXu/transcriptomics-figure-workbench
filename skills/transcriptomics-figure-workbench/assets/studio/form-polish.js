/* Same-form finishing of an inert, frozen scientific SVG. No statistical work. */
(() => {
  const NS='http://www.w3.org/2000/svg';
  const ink='#283740', muted='#66767d';
  function node(tag,attrs={}) {const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));return n;}
  function label(s,x,y,size=10,fill=ink){const n=node('text',{x,y,'font-family':'Arial, Liberation Sans, sans-serif','font-size':size,fill});n.textContent=s;return n;}
  function bounds(n){const b=n.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height};}
  function primitives(svg) {
    return [...svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,use,image')]
      .filter(n=>!n.closest('defs')&&!n.closest('[data-page-background]')&&!n.closest('[data-form-decoration]'))
      .map(n=>[n.localName,...[...n.attributes].filter(a=>!['style','class','id','fill','stroke'].includes(a.name)).map(a=>[a.name,a.value]).sort()])
      .sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
  }
  function wrapAt(el,x,y) {const g=node('g',{transform:`translate(${x} ${y})`});el.replaceWith(g);g.append(el);return g;}
  function finish(source,item,options={}) {
    const variant=options.variant||'journal';
    if(!['journal','presentation'].includes(variant))throw Error('Unknown within-form style');
    const svg=window.FigurePublication.safeParse(source),host=document.getElementById('stage');host.replaceChildren(svg);
    svg.style.overflow='visible';const old=svg.viewBox.baseVal, oldW=old.width,oldH=old.height;
    svg.setAttribute('width',oldW);svg.setAttribute('height',oldH);
    const before=JSON.stringify(primitives(svg));const changes=[];
    // Page furniture is independently versioned; no data artist is removed.
    let title=item.context?.title_en||'';const retainedNotes=[];
    for(const n of [...svg.children]) {
      if(n.localName==='text'){
        const s=n.textContent.trim();
        const furniture=/^SYNTHETIC|PUBLIC COORDINATES|REFERENCE COLOR|Frozen display|Exact declared|Original structure/.test(s);
        if(!title&&!furniture&&parseFloat(n.getAttribute('y'))<65)title=s;
        else if(!furniture&&parseFloat(n.getAttribute('y'))>=55&&s!==item.id)retainedNotes.push(s);
        n.remove();
      } else if(n.localName==='rect'&&n.getAttribute('data-page-background'))n.remove();
    }
    const originalPage=svg.querySelector('g[id="figure_1"] > g[id="patch_1"]');
    if(originalPage){originalPage.setAttribute('data-page-background','true');originalPage.remove();}
    for(const n of [...svg.querySelectorAll('text')]){
      const s=n.textContent.trim();
      if(/^SYNTHETIC (DEMO|LAYOUT EXAMPLE)|^Software test fixture[;:]|^Synthetic software fixture|^Frozen display;/.test(s)) {n.remove();continue;}
      if(!n.closest('[id^="axes_"]')&&n.getBBox().y<oldH*.14&&(parseFloat(getComputedStyle(n).fontSize)||0)>=10.5){if(!title)title=s;n.remove();continue;}
      const cs=getComputedStyle(n),size=parseFloat(cs.fontSize)||9,fill=cs.fill;
      // Axis legends and short annotations retain their original anchor/rotation.
      n.style.fontFamily='Arial, Liberation Sans, sans-serif';
      n.style.fontWeight=/^(?:[A-H]|NES|FDR)$/.test(s)?'600':'400';
      if(item.profile!=='reference'&&!['rgb(255, 255, 255)','white'].includes(fill)&&!/url\(/.test(fill))n.style.fill=ink;
      if(size>14&&s.length>3)n.style.fontSize='12px';
    }
    // Softer frames and guide rules; measured line widths, point areas and colour scales stay fixed.
    for(const n of svg.querySelectorAll('[id^="legend_"] > [id^="patch_"]')){
      for(const p of n.querySelectorAll('path'))if(['white','rgb(255, 255, 255)'].includes(getComputedStyle(p).fill))p.style.stroke='none';
    }
    for(const n of svg.querySelectorAll('[id^="matplotlib.axis_"] [id^="line2d_"] path')){
      const c=getComputedStyle(n).stroke;
      if(['rgb(176, 176, 176)','rgb(204, 204, 204)','rgb(211, 211, 211)','rgb(221, 221, 221)'].includes(c))n.style.stroke='#e1e7e9';
    }
    changes.push('quiet guide frames; consistent text and title hierarchy; retained data channels');
    if(item.id==='T35'){
      const ids=new Set([...svg.querySelectorAll('[id^="line2d_"] use')].map(n=>n.getAttribute('href')||n.getAttribute('xlink:href')));
      for(const ref of ids){const p=ref&&svg.querySelector(`[id="${ref.slice(1)}"]`);if(p&&p.closest('defs'))p.setAttribute('transform','scale(0.32)');}
      changes.push('identity markers reduced to 32 percent linear size; no marker-area quantity is encoded in this profile; all vertices retained');
    }
    // Root annotations at the bottom are provenance, retained verbatim in the receipt.
    for(const n of [...svg.querySelectorAll('g[id="figure_1"] > g[id^="text_"]')]){
      const s=n.textContent.trim().replace(/\s+/g,' ');
      // NES/FDR, pathway names and leading-edge keys are scientific labels, not furniture.
      if(s&&(s.length>110||/^(?:Contrast:|Illustrative condition|Frozen .*\/)/.test(s))){retainedNotes.push(s);n.remove();}
    }
    let body;
    if(item.layout_groups){
      body=node('g',{'data-form-body':'true'});svg.append(body);
      const groups=[];
      for(const ids of item.layout_groups){
        const g=node('g');body.append(g);
        for(const id of ids){const a=svg.querySelector(`[id="${id}"]`);if(!a)throw Error('Missing complete axis '+id);g.append(a);}
        groups.push(g);
      }
      const place=(el,parent,x,y)=>{parent.append(el);const b=bounds(el);el.setAttribute('transform',`translate(${x-b.x} ${y-b.y})`);};
      if(item.id==='R04'){
        const key=svg.querySelector('[id="axes_2"]'),ring=bounds(svg.querySelector('[id="axes_1"]'));
        const labels=[...key.querySelectorAll('text')],markers=[...key.children].filter(n=>n.id.startsWith('PathCollection'));
        if(labels.length===70&&markers.length===70){
          labels.forEach((t,i)=>{
            const holder=t.closest('[id^="text_"]'),b=bounds(holder),c=Math.floor(i/10),r=i%10;
            const x=ring.x+c*74,y=ring.y+ring.h+24+r*12;
            const shift=[x-b.x,y-b.y];wrapAt(holder,...shift);wrapAt(markers[i],...shift);t.style.fontSize='7.3px';
          });
        }
        place(key,groups[0],ring.x,ring.y+ring.h+18);
      }
      if(item.id==='R11'){
        const ring=bounds(svg.querySelector('[id="axes_11"]'));
        place(svg.querySelector('[id="axes_12"]'),groups[5],ring.x,ring.y-45);
      }
      // Guides outside Matplotlib axes have their own anchors, not source-page offsets.
      for(const legend of [...svg.querySelectorAll('[id^="legend_"]')].filter(n=>!n.closest('[data-form-body]'))){
        const parent=groups.at(-1),b=bounds(parent);place(legend,parent,b.x,b.y+b.h+14);
      }
      if(item.id==='R24')for(const [id,j] of [['patch_232',1],['patch_233',2],['patch_234',3]]){
        const p=svg.querySelector(`[id="${id}"]`);if(p)groups[j].insertBefore(p,groups[j].firstChild);
      }
      const rest=node('g');
      for(const n of [...svg.children])if(n!==body&&!['defs','style'].includes(n.localName))rest.append(n);
      if(primitives(rest).length||rest.querySelector('text'))throw Error('Unassigned non-axis artists');
      const sizes=groups.map(bounds),cols=item.layout_columns||1,gap=28;
      if(item.id==='R24'){
        const rows=[[0],[1,2,3],[4,5]];let y=0;
        for(const row of rows){let x=0;for(const i of row){groups[i].setAttribute('transform',`translate(${x-sizes[i].x} ${y-sizes[i].y})`);x+=sizes[i].w+gap;}y+=Math.max(...row.map(i=>sizes[i].h))+gap;}
      }else{
        const widths=Array.from({length:cols},(_,c)=>Math.max(...sizes.filter((_,i)=>i%cols===c).map(b=>b.w)));
        const heights=Array.from({length:Math.ceil(groups.length/cols)},(_,r)=>Math.max(...sizes.slice(r*cols,(r+1)*cols).map(b=>b.h)));
        groups.forEach((g,i)=>{const c=i%cols,r=Math.floor(i/cols),x=widths.slice(0,c).reduce((a,b)=>a+b+gap,0),y=heights.slice(0,r).reduce((a,b)=>a+b+gap,0);g.setAttribute('transform',`translate(${x-sizes[i].x} ${y-sizes[i].y})`);});
      }
      // Keep only empty wrappers/defs outside the selected complete axes.
      for(const a of svg.querySelectorAll('[id^="axes_"]'))if(!a.closest('[data-form-body]'))throw Error('Unassigned axis would be lost');
      changes.push('complete linked axis groups reflowed without independent coordinate distortion');
    } else {
      body=node('g',{'data-form-body':'true'});
      for(const n of [...svg.children])if(!['defs','style'].includes(n.localName))body.append(n);
      svg.append(body);
    }
    let b=bounds(body);
    if(item.id==='T02'){
      // Geographic shapes extend behind clipping rectangles; invisible land is not page content.
      const x=Math.max(0,b.x),y=Math.max(30,b.y),right=Math.min(oldW,b.x+b.w),bottom=Math.min(oldH-13,b.y+b.h);
      b={x,y,w:right-x,h:bottom-y};changes.push('crop to original visible map frame; clipped geographic paths retained');
    }
    if(b.w<=0||b.h<=0)throw Error('Empty figure');
    const pad=variant==='presentation'?24:16,top=variant==='presentation'?52:43;
    const width=Math.max(280,b.w+2*pad);
    const lines=[];
    for(const value of [...new Set(retainedNotes.map(s=>s.replace(/\s+/g,' ').trim()).filter(Boolean))]){
      let line='';const probe=label('',0,0,7.2);svg.append(probe);
      for(const word of value.split(/\s+/)){probe.textContent=line?line+' '+word:word;if(probe.getComputedTextLength()>width-2*pad&&line){lines.push(line);line=word;}else line=probe.textContent;}
      if(line)lines.push(line);probe.remove();
    }
    const height=b.h+top+24+(lines.length?lines.length*10+9:0);
    body.setAttribute('transform',`translate(${pad-b.x} ${top-b.y})`);
    svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('width',width+'pt');svg.setAttribute('height',height+'pt');
    svg.insertBefore(node('rect',{width,height,fill:'white','data-page-background':'true'}),svg.firstChild);
    title=title||item.kind.replaceAll('_',' ');
    const t=label(title,pad,27,variant==='presentation'?14:12);t.setAttribute('font-weight','600');svg.append(t);
    while(t.getComputedTextLength()>width-2*pad&&parseFloat(t.getAttribute('font-size'))>9)t.setAttribute('font-size',parseFloat(t.getAttribute('font-size'))-.25);
    const tag=label(item.id,width-pad,11,6.3,muted);tag.setAttribute('text-anchor','end');svg.append(tag);
    const foot=label(item.profile==='reference'?'REFERENCE PALETTE · exact supplied colours':item.profile==='structure'?'PUBLIC STRUCTURE · original raster retained':'SYNTHETIC DISPLAY · frozen values',pad,height-7,6.3,muted);svg.append(foot);
    lines.forEach((s,i)=>svg.append(label(s,pad,top+b.h+17+i*10,7.2,muted)));
    const after=JSON.stringify(primitives(body));
    if(before!==after){
      // Page rectangle alone may have been included in raw Matplotlib sources.
      const clean=window.FigurePublication.safeParse(source);
      clean.querySelector('g[id="figure_1"] > g[id="patch_1"]')?.setAttribute('data-page-background','true');
      if(JSON.stringify(primitives(clean))!==after){const a=primitives(clean),b=primitives(body),extra=a.filter(r=>!b.some(v=>JSON.stringify(v)===JSON.stringify(r)));throw Error('Measured primitives changed '+a.length+'/'+b.length+' '+JSON.stringify(extra.slice(0,2)));}
    }
    const textSizes=[...body.querySelectorAll('text')].filter(n=>n.textContent.trim().length>1).map(n=>parseFloat(getComputedStyle(n).fontSize)||9).sort((a,b)=>a-b);
    const low=textSizes[Math.floor(textSizes.length*.1)]||9;
    return {svg:new XMLSerializer().serializeToString(svg),width_pt:width,height_pt:height,changes,retained_notes:retainedNotes,
      graphical_fingerprint:after, audit:window.FigurePublication.audit(svg),
      sizing:{nominal_width_mm:178,body_font_p10_pt:low,at_178mm_pt:low*178*72/25.4/width,minimum_width_for_7pt_mm:width*7/low*25.4/72},
      layout_groups:item.layout_groups||null,variant};
  }
  window.FigureFormPolish={finish,primitives};
})();
