"""Compose reviewed, hash-verified single-page bundles without changing data.

Inputs retain their separate tables, guide scales and provenance. Shared legend
inference or implicit data alignment is deliberately absent.
"""
from pathlib import Path
import json,hashlib,shutil,math,re,copy
import fitz
from matplotlib import font_manager
from PIL import Image,ImageChops

def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def arrangement_layout(layout,arrangement,*,panel_width_pt=440,panel_height_pt=340,gap_pt=28,margin_pt=28):
    """Reflow complete panel cells; preserve every component and its guides."""
    if arrangement not in ('horizontal','vertical'):raise ValueError('Use horizontal or vertical panel arrangement')
    if any(not math.isfinite(v) or v<=0 for v in [panel_width_pt,panel_height_pt,gap_pt,margin_pt]):raise ValueError('Positive finite cell dimensions required')
    result=copy.deepcopy(layout);n=len(result['panels'])
    if not n:raise ValueError('At least one component required')
    width=2*margin_pt+(n*panel_width_pt+(n-1)*gap_pt if arrangement=='horizontal' else panel_width_pt)
    height=2*margin_pt+20+(panel_height_pt if arrangement=='horizontal' else n*panel_height_pt+(n-1)*gap_pt)
    result['size_pt']=[width,height];result['arrangement']=arrangement
    for i,cell in enumerate(result['panels']):
        x=margin_pt+i*(panel_width_pt+gap_pt) if arrangement=='horizontal' else margin_pt
        y=margin_pt+12 if arrangement=='horizontal' else margin_pt+12+i*(panel_height_pt+gap_pt)
        cell['rect_pt']=[x,y,x+panel_width_pt,y+panel_height_pt]
        cell['crop_white_margins']=True
    return result

def _validate_layout(panels,layout):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',layout.get('id','')):raise ValueError('Safe composition ID required')
    width,height=layout['size_pt']
    if not all(math.isfinite(v) and v>0 for v in [width,height]):raise ValueError('Positive finite page dimensions required')
    if not panels or len(panels)!=len(layout['panels']):raise ValueError('Every cell must have one source panel')
    ids=[];rectangles=[];page=fitz.Rect(0,0,width,height)
    for cell in layout['panels']:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',cell.get('id','')):raise ValueError('Safe unique panel IDs required')
        ids.append(cell['id']);rect=fitz.Rect(cell['rect_pt'])
        if any(not math.isfinite(v) for v in rect) or rect.is_empty or not page.contains(rect) or any((rect&r).get_area()>1 for r in rectangles):raise ValueError('Invalid or overlapping panel cells')
        if cell.get('label') and rect.y0<18:raise ValueError('Reserve a visible panel-label gutter above every cell')
        rectangles.append(rect)
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate panel IDs')


def align_data_rects(prepared,groups):
    """Align explicitly declared scientific axes, preserving isotropic PDF scale.

    Only equal limits/scales and explicit shared coordinate definitions qualify.
    Bounds come from full-page export receipts, never raster edge guesses.
    """
    used=set();receipts=[];lookup={p['cell']['id']:p for p in prepared}
    for group in groups:
        dim=group.get('dimension');members=group.get('panels',[])
        if dim not in ('x','y') or not group.get('coordinate_definition') or len(members)<2:
            raise ValueError('Axis alignment needs dimension, coordinate definition and at least two panels')
        ids=[m['id'] for m in members]
        if len(ids)!=len(set(ids)) or set(ids)-set(lookup) or used.intersection(ids):raise ValueError('Unknown, repeated or multiply constrained alignment panels')
        used.update(ids);sources=[];coordinate=None;keys=None
        for member in members:
            p=lookup[member['id']];meta=p['meta'];axis=member['axis'];axes=meta.get('layout_geometry',[])
            if type(axis) is not int or axis<0 or axis>=len(axes):raise ValueError('Alignment needs a recorded exported axis index')
            a=axes[axis]
            if a.get('colourbar') or a.get('projection','rectilinear')!='rectilinear':raise ValueError('Only scientific rectangular axes may share alignment')
            signature=(tuple(a[dim+'lim']),a[dim+'scale'])
            if coordinate is not None and signature!=coordinate:raise ValueError('Shared axis limits/scales differ')
            coordinate=signature
            if 'keys' in member:
                if keys is not None and member['keys']!=keys:raise ValueError('Shared index IDs or order differ')
                keys=member['keys']
            w=meta['width_inches']*72;h=meta['height_inches']*72
            if abs(w-p['source'][0].rect.width)>.1 or abs(h-p['source'][0].rect.height)>.1:raise ValueError('Receipt does not describe full-page coordinates')
            bx,by,bw,bh=a['bounds'];clip=p['clip'];cell=fitz.Rect(p['cell']['rect_pt'])
            offset=(bx*w-clip.x0) if dim=='x' else ((1-by-bh)*h-clip.y0)
            span=bw*w if dim=='x' else bh*h;length=clip.width if dim=='x' else clip.height
            if min(offset,length-offset-span)<-.1 or span<=0:raise ValueError('Axis outside preserved source crop')
            sources.append((p,offset,span,length,cell))
        if keys is not None and any('keys' not in m for m in members):raise ValueError('Supply index IDs for every aligned panel or none')
        low=max(c.x0 if dim=='x' else c.y0 for _,_,_,_,c in sources);high=min(c.x1 if dim=='x' else c.y1 for _,_,_,_,c in sources)
        before=max(o/s for _,o,s,_,_ in sources);after=max((l-o-s)/s for _,o,s,l,_ in sources)
        span=(high-low)/(1+before+after)
        for p,o,s,l,c in sources:
            orth_cell=c.height if dim=='x' else c.width;orth_source=p['clip'].height if dim=='x' else p['clip'].width
            span=min(span,orth_cell*s/orth_source)
        if span<=0:raise ValueError('Shared data axis has no feasible nonoverlapping page span')
        anchor=low+before*span
        for p,o,s,l,c in sources:
            scale=span/s;left=c.x0 if dim=='y' else anchor-o*scale;top=c.y0 if dim=='x' else anchor-o*scale
            fitted=fitz.Rect(left,top,left+p['clip'].width*scale,top+p['clip'].height*scale)
            if not c.contains(fitted):raise ValueError('Data alignment would clip a complete panel')
            p['fitted']=fitted
        receipts.append(dict(dimension=dim,panels=ids,coordinate_definition=group['coordinate_definition'],limits=list(coordinate[0]),scale=coordinate[1],target_span_pt=[anchor,anchor+span],keys=keys))
    return receipts

def compose_bundles(panels,layout,output,*,preview_dpi=300):
    _validate_layout(panels,layout)
    if not math.isfinite(preview_dpi) or preview_dpi<=0:raise ValueError('Positive finite preview resolution required')
    output=Path(output)
    if output.exists():raise FileExistsError('Fresh output required')
    width,height=layout['size_pt']; book=fitz.open(); page=book.new_page(width=width,height=height); receipts=[]; themes=set(); fonts=[]; synthetic_flags=[]
    if len(panels)!=len(layout['panels']): raise ValueError('Every layout cell must have one supplied bundle')
    rectangles=[];prepared=[]
    for item,cell in zip(panels,layout['panels']):
        prefix=Path(item['prefix']); metadata=Path(item.get('metadata',prefix.with_suffix('.json')))
        meta=json.loads(metadata.read_text(encoding='utf8')); pdf=prefix.with_suffix('.pdf')
        for ext in ('.pdf','.svg','.png','.tsv'):
            f=prefix.with_suffix(ext)
            if _sha(f)!=meta['output_sha256'][f.name]: raise ValueError('Changed source bundle')
        theme=meta['figure_spec'].get('project_theme_sha256')
        if layout.get('require_same_theme',True) and not theme: raise ValueError('Project theme required in each source bundle')
        themes.add(theme)
        family=meta['figure_spec'].get('project_theme',{}).get('font_family')
        if not family: raise ValueError('Explicit project font required for composition labels')
        fonts.append(family); synthetic_flags.append(bool(meta['synthetic']))
        rect=fitz.Rect(cell['rect_pt'])
        if rect.is_empty or not page.rect.contains(rect) or any((rect&r).get_area()>1 for r in rectangles): raise ValueError('Invalid or overlapping panel cells')
        rectangles.append(rect); source=fitz.open(pdf)
        if len(source)!=1: raise ValueError('Single-page source panel required')
        clip=source[0].rect
        if cell.get('crop_software_labels'):
            if not meta['synthetic']: raise ValueError('Software-label cropping only for explicitly synthetic fixtures')
            # Remove complete known software-label lines in this in-memory copy.
            # Source files remain unchanged; graphics and images are never redacted.
            scientific=[]; removed=[]
            for block in source[0].get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    text=''.join(s['text'] for s in line['spans'])
                    if text.startswith(('SYNTHETIC DEMO','Software test fixture')):
                        removed.append(text)
                        for span in line['spans']:
                            b=fitz.Rect(span['bbox']); b.y0+=.5; b.y1-=.5
                            source[0].add_redact_annot(b,fill=False)
                    else: scientific.append(text)
            if removed: source[0].apply_redactions(images=0,graphics=0,text=0)
            after=[''.join(s['text'] for s in line['spans']) for block in source[0].get_text('dict')['blocks'] for line in block.get('lines',[])]
            if sorted(after)!=sorted(scientific): raise ValueError('Software-label normalization changed scientific text')
            # Tighten white margins using the actual raster bounds; still embed PDF vectors.
            pix=source[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
            raster=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            bbox=ImageChops.difference(raster,Image.new('RGB',raster.size,'white')).getbbox()
            if not bbox: raise ValueError('Empty panel after software-label normalization')
            clip=fitz.Rect(bbox[0]/2-6,bbox[1]/2-6,bbox[2]/2+6,bbox[3]/2+6)&source[0].rect
            for block in source[0].get_text('dict')['blocks']:
                if 'lines' not in block: continue
                for line in block['lines']:
                    for span in line['spans']:
                        b=fitz.Rect(span['bbox']); t=span['text']
                        if not clip.contains(b):
                            raise ValueError('Crop would remove scientific text: '+t)
        if cell.get('crop_white_margins') and not cell.get('crop_software_labels'):
            pix=source[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
            raster=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            bbox=ImageChops.difference(raster,Image.new('RGB',raster.size,'white')).getbbox()
            if not bbox:raise ValueError('Empty panel')
            clip=fitz.Rect(bbox[0]/2-6,bbox[1]/2-6,bbox[2]/2+6,bbox[3]/2+6)&source[0].rect
            for block in source[0].get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        if not clip.contains(fitz.Rect(span['bbox'])):raise ValueError('White-margin crop would remove scientific text')
        scale=min(rect.width/clip.width,rect.height/clip.height)
        fitted=fitz.Rect(rect.x0,rect.y0,rect.x0+clip.width*scale,rect.y0+clip.height*scale)
        prepared.append(dict(cell=cell,source=source,clip=clip,fitted=fitted,meta=meta,pdf=pdf,prefix=prefix,theme=theme,family=family))
    if layout.get('require_same_theme',True) and len(themes)!=1: raise ValueError('Different project themes cannot be silently composed')
    if len(set(fonts))!=1: raise ValueError('Composition panel fonts must agree')
    alignment=align_data_rects(prepared,layout.get('align_data',[]))
    for p in prepared:
        cell=p['cell'];rect=fitz.Rect(cell['rect_pt']);fitted=p['fitted'];clip=p['clip'];source=p['source'];prefix=p['prefix'];pdf=p['pdf'];theme=p['theme'];family=p['family']
        page.show_pdf_page(fitted,source,0,clip=clip,keep_proportion=True); source.close()
        label=cell.get('label','')
        if label:
            font_path=font_manager.findfont(font_manager.FontProperties(family=family,weight='bold'),fallback_to_default=False)
            label_font='ProjectBold'+str(len(receipts)); page.insert_font(fontname=label_font,fontfile=str(font_path))
            page.insert_text((rect.x0,rect.y0-7),label,fontsize=11,fontname=label_font)
        receipts.append({'id':cell['id'],'source_pdf_sha256':_sha(pdf),'source_table_sha256':_sha(prefix.with_suffix('.tsv')),'source_theme_sha256':theme,'cell':cell,'fitted_rect_pt':list(fitted),'source_clip_pt':list(clip),'table_source':prefix.with_suffix('.tsv')})
    if layout.get('require_same_theme',True) and len(themes)!=1: raise ValueError('Different project themes cannot be silently composed')
    if len(set(fonts))!=1: raise ValueError('Composition panel fonts must agree')
    if any(synthetic_flags):
        font_path=font_manager.findfont(font_manager.FontProperties(family=fonts[0]),fallback_to_default=False)
        page.insert_font(fontname='ProjectRegular',fontfile=str(font_path))
        page.insert_text((25,height-7),'SYNTHETIC LAYOUT EXAMPLE - component data and guides preserved',fontsize=8,fontname='ProjectRegular',color=(.28,.33,.38))
    output.mkdir(parents=True,exist_ok=False)
    for receipt in receipts:
        shutil.copy2(receipt.pop('table_source'),output/(receipt['id']+'.tsv'))
    prefix=output/layout['id']; book.save(prefix.with_suffix('.pdf'),deflate=True)
    page.get_pixmap(matrix=fitz.Matrix(preview_dpi/72,preview_dpi/72)).save(prefix.with_suffix('.png'))
    prefix.with_suffix('.svg').write_text(page.get_svg_image(text_as_path=False),encoding='utf8'); book.close()
    record={'status':'COMPOSED_UNREVIEWED','layout':layout,'panels':receipts,'data_alignment':alignment,'font_family':fonts[0],'synthetic':any(synthetic_flags),'scientific_inference':False,'shared_legends':'none; each supplied guide preserved','files':{p.name:_sha(p) for p in output.iterdir() if p.is_file()}}
    prefix.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8'); return record

