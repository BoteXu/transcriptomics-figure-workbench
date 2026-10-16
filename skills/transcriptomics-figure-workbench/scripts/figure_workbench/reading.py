"""Uniform-scale vector reading editions; no result recalculation or plot pruning."""
from pathlib import Path
import copy,io,json,math
from .contracts import hash_value,read_json,write_new
from .registry import digest,source_identity

PAGE_W=595.276;PAGE_H=841.89;LEFT=43.0;BOTTOM=52.0;DETAIL_H=650.0

def _bound(root,value):
    if not isinstance(value,str) or not value or Path(value).is_absolute() or '\\' in value or '..' in Path(value).parts:raise ValueError('Use a safe relative public asset reference')
    raw=root/value
    if raw.is_symlink():raise ValueError('Linked assets are outside the selected scope')
    path=raw.resolve()
    if root not in path.parents or path.is_symlink() or not path.is_file() or path.stat().st_size>64*1024**2:raise ValueError('Selected asset missing, linked, outside scope or too large')
    return path

def make_reading_plan(index,root,width_mm=178.,minimum_text_pt=7.5,volume_size=75):
    root=Path(root).resolve();index=Path(index).resolve()
    if type(width_mm) not in {int,float} or not math.isfinite(width_mm) or not 100<=width_mm<=180:raise ValueError('A4 reading width must be 100 to 180 mm')
    if type(minimum_text_pt) not in {int,float} or not math.isfinite(minimum_text_pt) or not 6<=minimum_text_pt<=12:raise ValueError('Declare a 6 to 12 pt minimum for measured body spans')
    if type(volume_size) is not int or not 1<=volume_size<=90:raise ValueError('Use a bounded 1 to 90 figures per volume')
    data=read_json(index);records=data.get('records',[])
    if not isinstance(records,list) or not 1<=len(records)<=500:raise ValueError('Select one bounded figure index')
    ids=[];bindings={}
    for record in records:
        key=record['id']
        if not isinstance(key,str) or not key.isascii() or not key.replace('_','').replace('-','').isalnum() or key in ids:raise ValueError('Unique ASCII figure identities required')
        ids.append(key)
        if type(record.get('components',[])) is not list:raise ValueError('Explicit component identities required')
        for ext in ['pdf','png','svg','meta']:
            value=record['assets'][ext];p=_bound(root,value);actual=digest(p)
            if actual!=record['sha256'][ext]:raise ValueError('Changed export: '+key)
            bindings[value]=actual
    by={r['id']:r for r in records}
    for r in records:
        if any(k not in by or by[k].get('components') or k==r['id'] for k in r.get('components',[])):raise ValueError('Composition maps must reference included standalone figures')
    return dict(schema_version=1,state='READING_PLAN_ONLY',input_index=str(index),index_sha256=digest(index),root=str(root),
        width_mm=width_mm,minimum_text_pt=minimum_text_pt,volume_size=volume_size,records=records,asset_bindings=bindings,
        source_identity=source_identity(),scientific_acceptance=False,visual_acceptance=False,
        boundary='Uniform-scale PDF placement, complete source coverage and component navigation; not a manuscript composition or paper proof')

def _measure(page):
    height=float(page.mediabox.height);sizes=[]
    def visit(text,cm,tm,font,size):
        y=tm[4]*cm[1]+tm[5]*cm[3]+cm[5]
        scale=math.hypot(tm[2]*cm[0]+tm[3]*cm[2],tm[2]*cm[1]+tm[3]*cm[3])
        if text.strip() and height*.08<y<height*.92 and scale*size>0:sizes.append(float(scale*size))
    page.extract_text(visitor_text=visit)
    return min(sizes) if sizes else None

def _positions(length,capacity,overlap=14.):
    if length<=capacity+.01:return [0.]
    n=math.ceil((length-overlap)/(capacity-overlap))
    return [i*(length-capacity)/(n-1) for i in range(n)]

def _append_compressed(writer,page):
    """Compress raw drawing operators without parsing or changing their bytes."""
    from pypdf.generic import NameObject,ArrayObject,DecodedStreamObject
    page=writer.add_page(page);contents=page.get('/Contents')
    if contents is None:return page
    obj=contents.get_object();parts=list(obj) if isinstance(obj,ArrayObject) else [contents];refs=[]
    for ref in parts:
        stream=ref.get_object();raw=stream.get_data();decoded=DecodedStreamObject();decoded.set_data(raw);encoded=decoded.flate_encode(level=6)
        if encoded.get_data()!=raw:raise ValueError('PDF compression changed drawing instructions')
        refs.append(writer._add_object(encoded))
    page[NameObject('/Contents')]=ArrayObject(refs) if isinstance(obj,ArrayObject) else refs[0]
    return page

def export_reading(plan,output):
    from pypdf import PdfReader,PdfWriter,Transformation
    from pypdf.generic import NameObject,RectangleObject
    from reportlab.pdfgen.canvas import Canvas
    if make_reading_plan(plan['input_index'],plan['root'],plan['width_mm'],plan['minimum_text_pt'],plan['volume_size'])!=plan:raise ValueError('Reading plan changed; prepare a fresh plan')
    output=Path(output);output.mkdir(parents=True,exist_ok=False);root=Path(plan['root']);width=plan['width_mm']*72/25.4
    layouts=[];alloc={};volume=-1;number=1
    for i,row in enumerate(plan['records']):
        if i%plan['volume_size']==0:volume+=1;number=2
        p=_bound(root,row['assets']['pdf']);reader=PdfReader(p)
        if len(reader.pages)!=1:raise ValueError('One source PDF page per figure required')
        page=reader.pages[0];w,h=float(page.mediabox.width),float(page.mediabox.height)
        annotations=page.get('/Annots',[]);annotations=annotations.get_object() if hasattr(annotations,'get_object') else annotations
        if '/AA' in page or annotations:raise ValueError('Active/annotated source pages are outside the reading adapter: '+row['id'])
        low=_measure(page);s=max(width/w,plan['minimum_text_pt']/low if low else 0)
        xs=_positions(w*s,width);ys=_positions(h*s,DETAIL_H)
        if len(xs)*len(ys)>64:raise ValueError('Figure needs more than 64 reading tiles; select a scoped alternative')
        components=row.get('components',[]);overview=bool(components) or len(xs)*len(ys)>1
        pages=1 if components else int(overview)+len(xs)*len(ys)
        layout=dict(id=row['id'],volume=volume+1,start_page=number,page_count=pages,source_pdf=row['assets']['pdf'],source_sha256=row['sha256']['pdf'],
            width_pt=w,height_pt=h,scale=s,source_body_minimum_pt=low,detail_body_minimum_pt=low*s if low else None,
            xs=xs,ys=ys,overview=overview,components=components,source_assets=row['assets'],source_hashes=row['sha256'],
            strategy='component_navigation' if components else 'uniform_scale_detail_tiles' if overview else 'uniform_scale_single_page')
        layouts.append(layout);alloc[row['id']]=layout;number+=pages
        reader.close()
        if (i+1)%50==0:print(str(i+1)+' source PDF layouts measured',flush=True)
    files=[];cache={}
    def source(item):
        if item['id'] not in cache:cache[item['id']]=PdfReader(_bound(root,item['source_pdf']))
        return cache[item['id']].pages[0]
    def frame(title,subtitle,page_number,mini=None,links=()):
        buf=io.BytesIO();c=Canvas(buf,pagesize=(PAGE_W,PAGE_H),pageCompression=1,invariant=1)
        c.setTitle('Frozen figure reading edition');c.setAuthor('Figure Workbench Contributors');c.setCreator('Figure Workbench')
        c.setFillColorRGB(.14,.20,.28);c.setFont('Helvetica-Bold',12);c.drawString(LEFT,PAGE_H-35,title[:85])
        c.setFont('Helvetica',8);c.setFillColorRGB(.39,.45,.51);c.drawString(LEFT,PAGE_H-51,subtitle[:115])
        c.setStrokeColorRGB(.86,.90,.93);c.line(LEFT,PAGE_H-64,PAGE_W-LEFT,PAGE_H-64)
        c.setFont('Helvetica',7.5);c.drawString(LEFT,28,'Frozen display reading edition. Uniform scale; source values and all visible regions retained.')
        c.drawRightString(PAGE_W-LEFT,16,str(page_number));c.drawString(LEFT,16,'Detail tiles refer to the complete source context. Not a final manuscript layout or paper proof.')
        for text,url,y in links:
            c.setFillColorRGB(.12,.49,.51);c.setFont('Helvetica',9);c.drawString(LEFT,y,text);c.linkURL(url,(LEFT,y-3,PAGE_W-LEFT,y+11),relative=1,thickness=0)
        c.showPage();c.save();return PdfReader(buf).pages[0]
    def merge(dest,item,scale,x,y,crop=None):
        src=copy.copy(source(item))
        if crop is not None:src[NameObject('/CropBox')]=RectangleObject(crop)
        dest.merge_transformed_page(src,Transformation().scale(scale).translate(x,y),over=True,expand=False)
    count=math.ceil(len(layouts)/plan['volume_size'])
    for v in range(1,count+1):
        writer=PdfWriter();selected=[x for x in layouts if x['volume']==v]
        intro=frame('Figure reading library | Volume '+str(v)+' / '+str(count),'Source-bound figures, readable details and component navigation',1)
        _append_compressed(writer,intro);page_n=2
        for item in selected:
            assert page_n==item['start_page'];w,h=item['width_pt'],item['height_pt'];key=item['id'];s=item['scale']
            if item['overview']:
                links=[]
                if item['components']:
                    for j,k in enumerate(item['components']):
                        target=alloc[k];filename=f'reading-volume-{target["volume"]:02d}.pdf'
                        links.append((chr(65+j)+'  '+k+'  |  volume '+str(target['volume'])+', page '+str(target['start_page']),filename+'#page='+str(target['start_page']),250-j*17))
                p=frame(key+' | complete source overview','Use the detail pages or linked standalone components; overview text is intentionally reduced.',page_n,links=links)
                scale=min(width/w,430/h);merge(p,item,scale,LEFT+(width-w*scale)/2,310+(430-h*scale)/2)
                _append_compressed(writer,p);page_n+=1
            if not item['components']:
                for iy,top in enumerate(item['ys']):
                    for ix,left in enumerate(item['xs']):
                        title=key+' | '+('detail '+str(iy*len(item['xs'])+ix+1)+' / '+str(len(item['ys'])*len(item['xs'])) if item['overview'] else 'reading view')
                        subtitle='Source PDF SHA256 '+item['source_sha256'][:20]+' | '+('measured body minimum '+f'{item["detail_body_minimum_pt"]:.2f} pt' if item['detail_body_minimum_pt'] else 'raster/outlined text: size unassessed')
                        p=frame(title,subtitle,page_n);bottom=max(0,h-(top+DETAIL_H)/s);right=min(w,(left+width)/s);upper=h-top/s
                        # The page is clipped to this explicit source rectangle. Tiles overlap,
                        # and their union covers the entire original page, including all guides.
                        merge(p,item,s,LEFT-left,BOTTOM-h*s+top+DETAIL_H,crop=(left/s,bottom,right,upper))
                        if item['overview']:
                            ms=min(70/w,55/h);mx=PAGE_W-LEFT-70;my=PAGE_H-130
                            merge(p,item,ms,mx,my)
                            mark=io.BytesIO();c=Canvas(mark,pagesize=(PAGE_W,PAGE_H),invariant=1);c.setStrokeColorRGB(.85,.36,.27);c.setLineWidth(1)
                            c.rect(mx+left/s*ms,my+bottom*ms,(right-left/s)*ms,(upper-bottom)*ms,fill=0,stroke=1);c.setFont('Helvetica',7);c.setFillColorRGB(.39,.45,.51);c.drawString(mx-80,my+10,'Source region '+str(ix+1)+','+str(iy+1));c.showPage();c.save();p.merge_page(PdfReader(mark).pages[0])
                        _append_compressed(writer,p);page_n+=1
            print(key+' reading pages prepared',flush=True)
        writer.add_metadata({'/Title':'Frozen figure reading edition '+str(v),'/Author':'Figure Workbench Contributors','/Creator':'Figure Workbench'})
        writer.compress_identical_objects()
        name=f'reading-volume-{v:02d}.pdf';dest=output/name
        with dest.open('xb') as stream:writer.write(stream)
        writer.close();files.append(dict(file=name,sha256=digest(dest),pages=page_n-1))
        for r in cache.values():r.close()
        cache={}
    for row in layouts:
        row.pop('source_assets');row.pop('source_hashes');row['file']=f'reading-volume-{row["volume"]:02d}.pdf'
    result=dict(schema_version=1,state='READING_PDFS_UNREVIEWED',source_index_sha256=plan['index_sha256'],source_identity=plan['source_identity'],
        figures=len(layouts),volumes=files,records=layouts,target_width_mm=plan['width_mm'],body_minimum_target_pt=plan['minimum_text_pt'],
        text_scope='All nonempty measurable PDF body spans within 8%-92% page height; page furniture excluded. Raster/outlined glyphs remain unassessed.',
        full_region_coverage=True,uniform_transform_only=True,scientific_acceptance=False,visual_acceptance=False)
    write_new(output/'reading-index.json',result);return result
