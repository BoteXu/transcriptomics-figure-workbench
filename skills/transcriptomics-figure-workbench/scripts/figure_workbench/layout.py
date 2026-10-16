"""Flexible complete-SVG layouts; standard library only, no scientific inference."""
import copy,hashlib,json,math,re,shutil
from pathlib import Path
from xml.etree import ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
SAFE=re.compile(r'^[A-Za-z][A-Za-z0-9_-]*$')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def number(x,name,low=0,high=14400):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not low<=x<=high:raise ValueError('Invalid '+name)
    return float(x)
def integer(x,name,low=1,high=1000):
    if type(x) is not int or not low<=x<=high:raise ValueError('Invalid '+name)
    return x
def load_svg(path):
    p=Path(path)
    if p.stat().st_size>12*1024**2:raise ValueError('Selected SVG exceeds bounded input size')
    text=p.read_text(encoding='utf8')
    if '<!ENTITY' in text.upper():raise ValueError('Entity declarations are not allowed')
    text=re.sub(r'<!DOCTYPE[^>]*>','',text,flags=re.I)
    root=ET.fromstring(text)
    if root.tag!='{'+NS+'}svg':raise ValueError('Expected SVG')
    allowed={'svg','g','defs','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','title','desc','clipPath','linearGradient','radialGradient','stop','pattern','image','use','style','symbol','mask','metadata'}
    for n in root.iter():
        tag=n.tag.rsplit('}',1)[-1]
        if tag not in allowed and tag!='RDF' and not n.tag.startswith(('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}','{http://purl.org/dc/elements/1.1/}','{http://creativecommons.org/ns#}')):raise ValueError('Unsupported active SVG element')
        for key,value in n.attrib.items():
            name=key.rsplit('}',1)[-1]
            if name.lower()=='base':raise ValueError('External base resolution rejected')
            if name=='style' and '\\' in value:raise ValueError('Escaped CSS requires source normalization')
            if name.lower().startswith('on'):raise ValueError('SVG event handler rejected')
            if name=='href' and not (re.fullmatch(r'#[\w:.-]+',value) or re.fullmatch(r'data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+',value)):raise ValueError('External SVG resource rejected')
            if re.search(r'javascript:|@import|expression\s*\(',value,re.I):raise ValueError('Active SVG style rejected')
            if any(not re.fullmatch(r'url\(\s*[\'"]?#[\w:.-]+[\'"]?\s*\)',u,re.I) for u in re.findall(r'url\([^)]*\)',value,re.I)):raise ValueError('External SVG style rejected')
        if tag=='style':
            css=n.text or ''
            if '\\' in css:raise ValueError('Escaped CSS requires source normalization')
            if re.search(r'@import|javascript:|expression\s*\(',css,re.I) or any(not re.fullmatch(r'url\(\s*[\'"]?#[\w:.-]+[\'"]?\s*\)',u,re.I) for u in re.findall(r'url\([^)]*\)',css,re.I)):raise ValueError('External CSS rejected')
    for child in list(root):
        if child.tag.endswith('}metadata'):root.remove(child)
    box=[float(v) for v in re.split(r'[\s,]+',root.get('viewBox','').strip())]
    if len(box)!=4 or not all(math.isfinite(v) for v in box) or min(box[2:])<=0:raise ValueError('Finite SVG viewBox required')
    return root,box

def make_layout(request,base):
    """Plan arbitrary counts, spans, weighted columns and pagination from selected files."""
    req=copy.deepcopy(request);base=Path(base).resolve()
    if not SAFE.fullmatch(req.get('id','')):raise ValueError('Safe layout ID required')
    panels=req.get('panels',[])
    if not isinstance(panels,list) or not 1<=len(panels)<=500:raise ValueError('Select 1 to 500 complete panels')
    width=number(req.get('canvas_width_pt',738),'canvas width',120)
    gap=number(req.get('gap_pt',18),'gap',0,300);pad=number(req.get('padding_pt',24),'padding',12,300)
    heading=number(req.get('heading_pt',32),'heading',0,100);gutter=number(req.get('panel_label_gutter_pt',18),'label gutter',12,100)
    target=number(req.get('preferred_panel_width_pt',320),'preferred panel width',60,2000)
    cols=req.get('columns','auto')
    if cols=='auto':cols=max(1,min(len(panels),math.floor((width-2*pad+gap)/(target+gap))))
    cols=integer(cols,'columns',1,64)
    usable=width-2*pad-gap*(cols-1)
    if usable<cols*24:raise ValueError('Canvas too narrow for selected columns; expand canvas')
    weights=req.get('column_weights',[1]*cols)
    if not isinstance(weights,list) or len(weights)!=cols:raise ValueError('One positive weight per column required')
    weights=[number(v,'column weight',.01,1000) for v in weights];cw=[usable*v/sum(weights) for v in weights]
    fixed_rows=req.get('rows');fixed_rows=integer(fixed_rows,'rows') if fixed_rows is not None else None
    per_page=req.get('max_rows_per_page');per_page=integer(per_page,'page rows') if per_page is not None else None
    if fixed_rows and per_page and fixed_rows!=per_page:raise ValueError('Use rows or max_rows_per_page consistently')
    limit=fixed_rows or per_page or 1000;occupied=set();reserved=set();cells=[];seen=set();cursor_page=0
    # Explicit positions are reserved before auto placement, regardless of input order.
    for item in panels:
        if not any(k in item for k in ['row','column','page']):continue
        if 'row' not in item or 'column' not in item:raise ValueError('Explicit placement needs row and column')
        pg=integer(item.get('page',0),'page',0,499);rr=integer(item['row'],'row',0,999);cc=integer(item['column'],'column',0,cols-1)
        rs=integer(item.get('row_span',1),'row span');cs=integer(item.get('column_span',1),'column span',1,cols)
        slots={(pg,r,c) for r in range(rr,rr+rs) for c in range(cc,cc+cs)}
        if rr+rs>limit or cc+cs>cols or reserved&slots:raise ValueError('Explicit panels overlap or exceed the grid')
        reserved.update(slots)
    for i,item in enumerate(panels):
        k=item.get('id','')
        if not SAFE.fullmatch(k) or k in seen:raise ValueError('Safe unique panel IDs required')
        if not isinstance(item.get('svg'),str) or not item['svg'].strip():raise ValueError('Select an actual SVG file for every panel; reference thumbnails are drafts')
        seen.add(k);p=(base/item['svg']).resolve();svg,box=load_svg(p)
        if item.get('sha256') and item['sha256']!=digest(p):raise ValueError('Selected SVG hash differs from requested source')
        rs=integer(item.get('row_span',1),'row span');cs=integer(item.get('column_span',1),'column span',1,cols)
        if rs>limit:raise ValueError('Panel span exceeds page row capacity')
        explicit=any(v in item for v in ['row','column','page'])
        if explicit:
            if 'row' not in item or 'column' not in item:raise ValueError('Explicit placement needs row and column')
            page=integer(item.get('page',0),'page',0,499);row=integer(item['row'],'row',0,999);col=integer(item['column'],'column',0,cols-1)
        else:
            page=cursor_page;found=False
            while page<500 and not found:
                for row in range(limit-rs+1):
                    for col in range(cols-cs+1):
                        if not any((page,r,c) in occupied or (page,r,c) in reserved for r in range(row,row+rs) for c in range(col,col+cs)):found=True;break
                    if found:break
                if not found:
                    if not per_page:raise ValueError('Requested row capacity is insufficient; allow more rows or pagination')
                    page+=1
            if not found:raise ValueError('Page limit exceeded')
            cursor_page=page
        slots={(page,r,c) for r in range(row,row+rs) for c in range(col,col+cs)}
        if col+cs>cols or row+rs>limit or occupied&slots:raise ValueError('Panel is outside the grid or overlaps another panel')
        occupied.update(slots);w=sum(cw[col:col+cs])+gap*(cs-1)
        label=str(item.get('label',chr(65+i) if i<26 else str(i+1)))
        want=number(item['height_pt'],'panel height',24) if 'height_pt' in item else w*box[3]/box[2]+(gutter if label else 0)
        entry=dict(id=k,source_svg=str(p),source_svg_sha256=digest(p),source_viewbox=box,page=page,row=row,column=col,row_span=rs,column_span=cs,label=label,desired_height_pt=want)
        if item.get('table'):
            table=(base/item['table']).resolve()
            if table.stat().st_size>100*1024**2:raise ValueError('Selected table exceeds copy budget')
            entry.update(source_table=str(table),source_table_sha256=digest(table))
        cells.append(entry)
    pages=[]
    for index in sorted({e['page'] for e in cells}):
        selected=[e for e in cells if e['page']==index];nrows=fixed_rows or max(e['row']+e['row_span'] for e in selected)
        given=req.get('row_heights_pt')
        if given is not None:
            if not isinstance(given,list) or len(given)!=nrows:raise ValueError('One height for every row on each page required')
            rh=[number(v,'row height',24) for v in given]
        else:
            rh=[24.]*nrows
            for e in sorted(selected,key=lambda x:x['row_span']):
                a=e['row'];b=a+e['row_span'];short=e['desired_height_pt']-sum(rh[a:b])-gap*(e['row_span']-1)
                if short>0:
                    for j in range(a,b):rh[j]+=short/e['row_span']
        if req.get('canvas_height_pt') is not None:
            canvas_height=number(req['canvas_height_pt'],'canvas height',120)
            room=canvas_height-2*pad-heading-gap*(nrows-1)
            if room<nrows*24:raise ValueError('Canvas too short for rows')
            rh=[h*room/sum(rh) for h in rh]
        height=2*pad+heading+sum(rh)+gap*(nrows-1)
        number(height,'computed canvas height',120)
        for e in selected:
            x=pad+sum(cw[:e['column']])+gap*e['column'];y=pad+heading+sum(rh[:e['row']])+gap*e['row']
            w=sum(cw[e['column']:e['column']+e['column_span']])+gap*(e['column_span']-1);h=sum(rh[e['row']:e['row']+e['row_span']])+gap*(e['row_span']-1)
            if h<gutter+12:raise ValueError('Panel too short for its label')
            e['rect_pt']=[x,y,w,h];e['content_rect_pt']=[x,y+(gutter if e['label'] else 0),w,h-(gutter if e['label'] else 0)]
            e['uniform_scale']=min(w/e['source_viewbox'][2],e['content_rect_pt'][3]/e['source_viewbox'][3])
        pages.append(dict(page=index,width_pt=width,height_pt=height,columns=cols,rows=nrows,column_widths_pt=cw,row_heights_pt=rh,panels=selected))
    packing=req.get('packing','grid')
    if packing not in {'grid','masonry'}:raise ValueError('Use grid or masonry packing')
    if packing=='masonry':
        if fixed_rows or per_page or req.get('canvas_height_pt') or req.get('row_heights_pt') or any(any(k in p for k in ['row','column','page']) or p.get('row_span',1)!=1 or p.get('column_span',1)!=1 for p in panels):raise ValueError('Masonry uses natural panel heights; use grid for fixed rows, spans and row-based pagination')
        if req.get('packing_order','tall_first') not in {'input','tall_first'}:raise ValueError('Use input or tall_first packing order')
        ends=[pad+heading]*cols;counts=[0]*cols
        selected=sorted(cells,key=lambda p:p['source_viewbox'][3]/p['source_viewbox'][2],reverse=True) if req.get('packing_order','tall_first')=='tall_first' else cells
        for e in selected:
            col=min(range(cols),key=lambda i:ends[i]);w=cw[col];h=w*e['source_viewbox'][3]/e['source_viewbox'][2]+(gutter if e['label'] else 0)
            x=pad+sum(cw[:col])+gap*col;y=ends[col];e.update(page=0,row=counts[col],column=col,row_span=1,column_span=1,rect_pt=[x,y,w,h],content_rect_pt=[x,y+(gutter if e['label'] else 0),w,h-(gutter if e['label'] else 0)],uniform_scale=w/e['source_viewbox'][2])
            ends[col]=y+h+gap;counts[col]+=1
        height=max(ends)-gap+pad;number(height,'masonry canvas height',120)
        pages=[dict(page=0,width_pt=width,height_pt=height,columns=cols,rows=max(counts),column_widths_pt=cw,row_heights_pt=None,panels=cells,packing='masonry',packing_order=req.get('packing_order','tall_first'))]
    if req.get('label_order','input') not in {'input','reading'}:raise ValueError('Use input or reading label order')
    if req.get('label_order')=='reading':
        custom={p['id'] for p in panels if 'label' in p}
        for page in pages:
            for i,e in enumerate(sorted(page['panels'],key=lambda e:(e['rect_pt'][1],e['rect_pt'][0]))):
                if e['id'] not in custom:e['label']=chr(65+i) if i<26 else str(i+1)
    return dict(schema_version=1,status='FLEXIBLE_LAYOUT_PLAN',id=req['id'],title=str(req.get('title','')),pages=pages,panel_count=len(cells),shared_data_axes_declared=False,shared_legends_inferred=False,source_content_preserved=True,scientific_analysis=False,visual_acceptance=False,target_size_assessed=False,visual_review_after_layout='REQUIRED')

def export_layout(plan,output,base=None):
    """Export complete inert SVG panels at uniform scale into a fresh folder."""
    plan=copy.deepcopy(plan);base=Path(base or '.').resolve()
    if plan.get('status')!='FLEXIBLE_LAYOUT_PLAN' or not SAFE.fullmatch(plan.get('id','')):raise ValueError('Expected a safe layout plan')
    out=Path(output)
    if out.exists():raise FileExistsError('Fresh output required')
    allpanels=[p for page in plan['pages'] for p in page['panels']]
    for p in allpanels:
        for key in ['source_svg','source_table']:
            if p.get(key):p[key]=str((base/p[key]).resolve())
    if len(allpanels)!=plan['panel_count'] or not 1<=len(allpanels)<=500:raise ValueError('Panel coverage changed')
    if len({p['id'] for p in allpanels})!=len(allpanels):raise ValueError('Repeated panels')
    page_ids=[]
    for page in plan['pages']:
        page_ids.append(integer(page['page'],'page',0,499));w=number(page['width_pt'],'page width',120);h=number(page['height_pt'],'page height',120);rects=[]
        for p in page['panels']:
            if not SAFE.fullmatch(p['id']):raise ValueError('Unsafe panel ID')
            x,y,cw,ch=[number(v,'panel rectangle',0) for v in p['rect_pt']]
            cx,cy,ccw,cch=[number(v,'content rectangle',0) for v in p['content_rect_pt']]
            if min(cw,ch,ccw,cch)<=0 or x+cw>w+.01 or y+ch>h+.01 or cx<x or cy<y or cx+ccw>x+cw+.01 or cy+cch>y+ch+.01:raise ValueError('Panel outside canvas')
            if any(min(x+cw,b+v)>max(x,b)+.01 and min(y+ch,c+z)>max(y,c)+.01 for b,c,v,z in rects):raise ValueError('Overlapping cells')
            rects.append((x,y,cw,ch))
    if len(page_ids)!=len(set(page_ids)):raise ValueError('Repeated pages')
    for p in allpanels:
        if digest(p['source_svg'])!=p['source_svg_sha256']:raise ValueError('Source SVG changed after planning')
        if p.get('source_table') and digest(p['source_table'])!=p['source_table_sha256']:raise ValueError('Source table changed after planning')
    staged=[]
    for page in plan['pages']:
        w=page['width_pt'];h=page['height_pt'];root=ET.Element('{'+NS+'}svg',dict(viewBox=f'0 0 {w} {h}',width=f'{w}pt',height=f'{h}pt'))
        ET.SubElement(root,'{'+NS+'}rect',dict(width=str(w),height=str(h),fill='white'))
        if plan['title']:ET.SubElement(root,'{'+NS+'}text',{'x':'24','y':'28','font-size':'13','font-family':'Arial, sans-serif','fill':'#283740'}).text=plan['title']
        for item in page['panels']:
            svg,box=load_svg(item['source_svg']);prefix=item['id']+'_';ids={n.get('id'):prefix+n.get('id') for n in svg.iter() if n.get('id')}
            scope=ids.get(svg.get('id'),prefix+'scope');svg.set('id',scope)
            for n in svg.iter():
                if n.get('id') and n is not svg:n.set('id',ids[n.get('id')])
                for key,value in list(n.attrib.items()):
                    value=re.sub(r'url\([\'"]?#([\w:.-]+)[\'"]?\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',value)
                    if key.rsplit('}',1)[-1]=='href' and value.startswith('#'):value='#'+ids.get(value[1:],value[1:])
                    n.set(key,value)
                if n.tag.endswith('}style') and n.text:
                    css=re.sub(r'/\*.*?\*/','',n.text,flags=re.S)
                    if '@' in css or css.count('{')!=css.count('}'):raise ValueError('Complex CSS requires source normalization')
                    rules=[]
                    for selectors,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
                        selectors=re.sub(r'#([A-Za-z_][\w.-]*)',lambda m:'#'+ids.get(m[1],m[1]),selectors)
                        body=re.sub(r'url\([\'"]?#([\w:.-]+)[\'"]?\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',body)
                        rules.append(','.join('#'+scope+' '+s.strip() for s in selectors.split(','))+'{'+body+'}')
                    n.text='\n'.join(rules)
            x,y,cw,ch=item['content_rect_pt'];svg.set('x',str(x));svg.set('y',str(y));svg.set('width',str(cw));svg.set('height',str(ch));svg.set('preserveAspectRatio','xMinYMin meet');root.append(svg)
            if item['label']:
                ET.SubElement(root,'{'+NS+'}text',{'x':str(item['rect_pt'][0]),'y':str(item['rect_pt'][1]+11),'font-size':'10','font-family':'Arial, sans-serif','font-weight':'600','fill':'#283740'}).text=item['label']
        raw=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        ET.fromstring(raw)  # Verify the actual serialized XML, including non-ASCII labels.
        staged.append((f"{plan['id']}-page-{page['page']+1:02d}.svg",raw))
    out.mkdir(parents=True)
    for name,raw in staged:(out/name).write_bytes(raw)
    for p in allpanels:
        if p.get('source_table'):shutil.copyfile(p['source_table'],out/(p['id']+'.tsv'))
    receipt=dict(status='FLEXIBLE_LAYOUT_EXPORTED_UNREVIEWED',layout=plan,files={p.name:digest(p) for p in out.iterdir()},scientific_analysis=False,visual_acceptance=False,target_size_assessed=False,export_types=['svg'],visual_review_after_layout='REQUIRED')
    (out/'layout-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return receipt


def inspect_layout(directory,review=None):
    """Bind layout review to current output and source bytes, without inferring beauty."""
    base=Path(directory);receipt=json.loads((base/'layout-receipt.json').read_text(encoding='utf8'));issues=[];current={}
    for name,h in receipt['files'].items():
        if Path(name).name!=name:raise ValueError('Unsafe receipt filename')
        f=base/name
        if not f.is_file():issues.append('missing output '+name)
        else:
            current[name]=digest(f)
            if current[name]!=h:issues.append('changed output '+name)
    for page in receipt['layout']['pages']:
        for p in page['panels']:
            source=(base/p['source_svg']).resolve()
            if not source.is_file() or digest(source)!=p['source_svg_sha256']:issues.append('changed source '+p['id'])
    bound=hashlib.sha256(json.dumps({'receipt':digest(base/'layout-receipt.json'),'files':current},sort_keys=True).encode()).hexdigest()
    state='UNREVIEWED'
    if review:
        state='SCREEN_REVIEWED' if not issues and review.get('layout_sha256')==bound and review.get('screen_review_completed') is True else 'STALE_REVIEW'
    return dict(status='LAYOUT_INSPECTED',issues=issues,layout_sha256=bound,review_status=state,visual_acceptance=False,target_size_assessed=False)
