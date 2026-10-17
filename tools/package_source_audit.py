"""Package selected public drawing checks and flexible complete-panel layouts.

Rendering and packaging never approve beauty. Screen review is recorded later
against exact output hashes. All source paths in the portable receipts are
relative; private render directories are never serialized into the package.
"""
import argparse,base64,copy,hashlib,html,io,json,os,shutil,sys
from pathlib import Path
from xml.etree import ElementTree as ET
from full_layout_cases import ROOT,SKILL
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.layout import make_layout,export_layout


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def merge(base,patch,out):
    out.mkdir(parents=True,exist_ok=False);records=[]
    overrides={r['id']:r for r in read(patch/'manifest.json')['records']}
    for original in read(base/'manifest.json')['records']:
        r=copy.deepcopy(overrides.get(original['id'],original));key=r['id'];src=patch if key in overrides else base
        if r['status']!='RENDERED_UNREVIEWED':raise ValueError('Unsuccessful render '+key)
        shutil.copytree(src/key,out/key)
        r.update(file=key+'/'+key+'.svg',png=key+'/'+key+'.png',visual_acceptance=False)
        records.append(r)
    write(out/'manifest.json',dict(records=records,visual_acceptance=False,scientific_acceptance=False))
    return records


def references(out,records):
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    for key,source in [('palettes','C01'),('structures','S01')]:
        dest=out/key;dest.mkdir();original=ROOT/'examples/forms-v080'/source
        if key=='palettes':
            shutil.copyfile(original/(source+'.svg'),dest/(key+'.svg'))
            note=dict(source_svg_sha256=sha(original/(source+'.svg')),source_content='Exact declared reference colour values; unchanged artwork')
        else:
            # Keep every original raster byte. Only the SVG's surrounding white
            # page is reframed; no molecule, colour or pixel is regenerated.
            from PIL import Image,ImageChops
            root=ET.parse(original/(source+'.svg')).getroot()
            im=next(n for n in root.iter() if n.tag.endswith('}image'))
            href=im.get('href') or im.get('{http://www.w3.org/1999/xlink}href')
            raw=base64.b64decode(href.split(',',1)[1]);image=Image.open(io.BytesIO(raw)).convert('RGB')
            diff=ImageChops.difference(image,Image.new('RGB',image.size,'white'))
            box=diff.getbbox();pad=28;box=[max(0,box[0]-pad),max(0,box[1]-pad),min(image.width,box[2]+pad),min(image.height,box[3]+pad)]
            width=560;body=width*(box[3]-box[1])/(box[2]-box[0]);height=body+78
            root=ET.Element('{'+ns+'}svg',{'viewBox':f'0 0 {width+32} {height}','width':str(width+32)+'pt','height':str(height)+'pt'})
            ET.SubElement(root,'{'+ns+'}rect',{'width':'100%','height':'100%','fill':'white'})
            def text(s,x,y,size):ET.SubElement(root,'{'+ns+'}text',{'x':str(x),'y':str(y),'font-family':'Arial, sans-serif','font-size':str(size),'fill':'#283740'}).text=s
            text('Public structure | retained original scene',16,24,12)
            view=ET.SubElement(root,'{'+ns+'}svg',{'x':'16','y':'40','width':str(width),'height':str(body),'viewBox':f'{box[0]} {box[1]} {box[2]-box[0]} {box[3]-box[1]}'})
            ET.SubElement(view,'{'+ns+'}image',{'width':str(image.width),'height':str(image.height),'href':href})
            text('Original image bytes retained; white page reframed; no structure computation.',16,height-12,8)
            (dest/(key+'.svg')).write_bytes(ET.tostring(root,encoding='utf8',xml_declaration=True))
            note=dict(source_svg_sha256=sha(original/(source+'.svg')),embedded_raster_sha256=hashlib.sha256(raw).hexdigest(),visible_raster_rectangle=box,source_content='Complete non-white original raster content plus 28-pixel padding; SVG viewport only')
            image.close()
        r=dict(id=key,form=key,route='fixed_reference',file=key+'/'+key+'.svg',png=key+'/'+key+'.png',
               status='RENDERED_UNREVIEWED',visual_acceptance=False,scientific_acceptance=False,reference=note)
        write(dest/'reference.json',r);records.append(r)
    write(out/'manifest.json',dict(records=records,visual_acceptance=False,scientific_acceptance=False))


def compose(source,output,groups=None):
    output.mkdir(parents=True,exist_ok=False);records=[];sources=read(source/'manifest.json')['records']
    # Whole independent panels are deliberately labelled layout QA. Adjacency
    # never implies common participants, an analysis or a shared colour scale.
    for index,start in enumerate(range(0,len(sources),4),1):
        if groups and index not in groups:continue
        selected=sources[start:start+4]
        widths={r['id']:float(ET.parse(source/r['file']).getroot().get('viewBox').split()[2]) for r in selected}
        for mode in ['balanced','custom']:
            key=f'Layout{index:02d}_{mode}';dest=output/key
            items=[dict(id='Panel'+str(i+1),svg=os.path.relpath(source/r['file'],output).replace('\\','/')) for i,r in enumerate(selected)]
            req=dict(id=key,title=f'Layout {index:02d} | independent display examples | no shared analysis',panels=items,
                     columns=2,canvas_width_pt=2*max(widths.values())+72,gap_pt=24,padding_pt=24,
                     label_order='reading',packing='masonry')
            if mode=='custom':
                order=sorted(range(len(selected)),key=lambda i:widths[selected[i]['id']],reverse=True)
                slots=[(0,0,2),(1,1,2),(0,2,1),(1,0,1)]
                for rank,i in enumerate(order):
                    row,col,span=slots[rank];items[i].update(row=row,column=col,column_span=span)
                weights=[1.15,.85,1.05]
                # Keep original physical typography: all complete source views
                # receive at least their original width, never tiny thumbnails.
                unit=max(widths[selected[i]['id']]/sum(weights[items[i]['column']:items[i]['column']+items[i]['column_span']]) for i in range(len(items)))
                req.update(packing='grid',columns=3,column_weights=weights,canvas_width_pt=unit*sum(weights)+96)
            write(output/(key+'.request.json'),req)
            plan=make_layout(req,output);export_layout(plan,dest)
            receipt=read(dest/'layout-receipt.json')
            for page in receipt['layout']['pages']:
                for p in page['panels']:
                    p['source_svg']=os.path.relpath(p['source_svg'],dest).replace('\\','/')
                    if p.get('source_table'):p['source_table']=os.path.relpath(p['source_table'],dest).replace('\\','/')
            write(dest/'layout-receipt.json',receipt)
            for page in plan['pages']:
                name=key+'-page-'+str(page['page']+1).zfill(2)
                records.append(dict(id=name,form='composition',file=key+'/'+name+'.svg',png=key+'/'+name+'.png',
                    layout=mode,components=[r['id'] for r in selected],request=key+'.request.json',
                    status='RENDERED_UNREVIEWED',visual_acceptance=False,scientific_acceptance=False))
    write(output/'manifest.json',dict(records=records,visual_acceptance=False,scientific_acceptance=False))


def gallery(folder):
    rows=read(folder/'manifest.json')['records'];cards=[]
    for r in rows:
        svg=r['file'];png=r['png'];pdf=str(Path(svg).with_suffix('.pdf')).replace('\\','/')
        files=[('SVG',svg),('PNG',png)]
        if (folder/pdf).is_file():files.append(('PDF',pdf))
        req=str(Path(svg).parent/'request.json').replace('\\','/')
        if (folder/req).is_file():files.append(('Request',req))
        if r.get('request'):files.append(('Layout request',r['request']))
        links=' · '.join(f'<a href="{html.escape(p)}">{n}</a>' for n,p in files)
        portable=str(Path(svg).parent/'example.spec.json').replace('\\','/')
        if (folder/portable).is_file():links+=' · <a href="'+html.escape(portable)+'">Portable runnable spec</a>'
        cards.append(f'<article id="{html.escape(r["id"])}"><h2>{html.escape(r["id"])}</h2><a href="{html.escape(svg)}"><img loading="lazy" src="{html.escape(png)}" alt="{html.escape(r["id"])}"></a><p>{links}</p></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Source-informed display examples</title><style>body{font:15px system-ui;color:#283740;background:#f6f8fa;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}article{background:white;border:1px solid #dce3e8;padding:18px;border-radius:9px}h2{font-size:16px}img{width:100%;height:310px;object-fit:contain}a{color:#356d91}header{max-width:1000px;margin-bottom:24px}</style><header><h1>Source-informed drawing and layout checks</h1><p>SYNTHETIC SOFTWARE EXAMPLES except the declared fixed public structure and reference colours. No biomedical findings. Open each complete view at reading size. Screen review is recorded separately; a new dataset or layout requires a new inspection.</p><p>Related panels have independent tables. No common cohort, legend or scientific relationship is inferred.</p></header><main>'''+''.join(cards)+'</main></html>'
    (folder/'index.html').write_text(page,encoding='utf8')
    page=page.replace('minmax(340px,1fr)','minmax(min(100%,340px),1fr)')
    page=page.replace('article{background','article{min-width:0;overflow-wrap:anywhere;background')
    page=page.replace('</header>','<p><label>Find a view <input id="search" type="search" placeholder="gsea, network, dot…"></label> <span id="count"></span></p></header>')
    page+='<script>const cards=[...document.querySelectorAll("article")],search=document.getElementById("search");function filter(){let n=0;for(const c of cards){c.hidden=!c.id.toLowerCase().includes(search.value.toLowerCase());if(!c.hidden)n++}document.getElementById("count").textContent=n+" / "+cards.length}search.addEventListener("input",filter);filter()</script>'
    (folder/'index.html').write_text(page,encoding='utf8')


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['merge','compose','gallery']);p.add_argument('--base',type=Path);p.add_argument('--patch',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--references',action='store_true');p.add_argument('--groups',type=int,nargs='+');a=p.parse_args()
    if a.action=='merge':
        rows=merge(a.base,a.patch,a.output)
        if a.references:references(a.output,rows)
    elif a.action=='compose':compose(a.base,a.output,a.groups)
    else:gallery(a.output)


if __name__=='__main__':main()
