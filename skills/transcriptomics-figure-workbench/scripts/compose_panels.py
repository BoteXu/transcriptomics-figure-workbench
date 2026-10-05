"""Compose reviewed, hash-verified single-page bundles without changing data.

Inputs retain their separate tables, guide scales and provenance. Shared legend
inference or implicit data alignment is deliberately absent.
"""
from pathlib import Path
import json,hashlib,shutil
import fitz
from matplotlib import font_manager
from PIL import Image,ImageChops

def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def compose_bundles(panels,layout,output):
    output=Path(output); output.mkdir(exist_ok=False)
    width,height=layout['size_pt']; book=fitz.open(); page=book.new_page(width=width,height=height); receipts=[]; themes=set(); fonts=[]; synthetic_flags=[]
    if len(panels)!=len(layout['panels']): raise ValueError('Every layout cell must have one supplied bundle')
    rectangles=[]
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
        page.show_pdf_page(rect,source,0,clip=clip,keep_proportion=True); source.close()
        label=cell.get('label','')
        if label:
            font_path=font_manager.findfont(font_manager.FontProperties(family=family,weight='bold'),fallback_to_default=False)
            label_font='ProjectBold'+str(len(receipts)); page.insert_font(fontname=label_font,fontfile=str(font_path))
            page.insert_text((rect.x0,rect.y0-7),label,fontsize=11,fontname=label_font)
        table_out=output/(cell['id']+'.tsv'); shutil.copy2(prefix.with_suffix('.tsv'),table_out)
        receipts.append({'id':cell['id'],'source_pdf_sha256':_sha(pdf),'source_table_sha256':_sha(table_out),'source_theme_sha256':theme,'cell':cell})
    if layout.get('require_same_theme',True) and len(themes)!=1: raise ValueError('Different project themes cannot be silently composed')
    if len(set(fonts))!=1: raise ValueError('Composition panel fonts must agree')
    if any(synthetic_flags):
        font_path=font_manager.findfont(font_manager.FontProperties(family=fonts[0]),fallback_to_default=False)
        page.insert_font(fontname='ProjectRegular',fontfile=str(font_path))
        page.insert_text((25,height-7),'SYNTHETIC LAYOUT EXAMPLE - component data and guides preserved',fontsize=8,fontname='ProjectRegular',color=(.28,.33,.38))
    prefix=output/layout['id']; book.save(prefix.with_suffix('.pdf'),deflate=True)
    page.get_pixmap(matrix=fitz.Matrix(300/72,300/72)).save(prefix.with_suffix('.png'))
    prefix.with_suffix('.svg').write_text(page.get_svg_image(text_as_path=False),encoding='utf8'); book.close()
    record={'status':'COMPOSED_UNREVIEWED','layout':layout,'panels':receipts,'font_family':fonts[0],'synthetic':any(synthetic_flags),'scientific_inference':False,'shared_legends':'none; each supplied guide preserved','files':{p.name:_sha(p) for p in output.iterdir() if p.is_file()}}
    prefix.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8'); return record

