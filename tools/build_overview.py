"""Primary deduplicated overview and a separate complete source archive."""
from pathlib import Path
import json,csv,math
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont
import tempfile
from pypdf import PdfWriter
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'examples/gallery';O=ROOT/'examples/overview'
try:FONT=font_manager.findfont('Microsoft YaHei',fallback_to_default=False)
except ValueError:FONT=font_manager.findfont('DejaVu Sans')
def contact(items,columns,title,cell_width=560,cell_height=480):
    image=Image.new('RGB',(columns*cell_width,math.ceil(len(items)/columns)*cell_height+85),'white');d=ImageDraw.Draw(image);font=ImageFont.truetype(FONT,19)
    d.text((20,18),title,fill='#21313e',font=font)
    for n,x in enumerate(items):
        left=n%columns*cell_width;top=n//columns*cell_height+85
        label=x.get('entry_id',x['id'])+' / '+x['id']+' '+x.get('entry_title',x['title'])
        d.text((left+12,top+4),label[:37],fill='#34485c',font=font)
        with Image.open(G/x['png']) as source:
            source.draft('RGB',(cell_width,cell_height));pic=source.convert('RGB');pic.thumbnail((cell_width-24,cell_height-55))
        image.paste(pic,(left+(cell_width-pic.width)//2,top+42+(cell_height-55-pic.height)//2));pic.close()
    return image
def book(sections,path,title):
    manifest=[]
    # Serial raster contact pages; standalone figure PDFs remain the vector originals.
    # Temporary page files are private to this invocation and removed on exit.
    with tempfile.TemporaryDirectory(prefix='figure-overview-') as temporary:
      writer=PdfWriter()
      for section,values in sections:
        cols,rows=(3,5) if section.startswith('课题色卡') else (2,2) if section.startswith('原生结构与说明') else (3,4)
        per_page=cols*rows;cell_width=1260//cols;cell_height=1640//rows
        for offset in range(0,len(values),per_page):
          page=Image.new('RGB',(1260,1740),'white');draw=ImageDraw.Draw(page)
          draw.text((24,12),title,font=ImageFont.truetype(FONT,21),fill='#273540')
          draw.text((24,46),section+' | '+str(len(values))+' entries',font=ImageFont.truetype(FONT,16),fill='#566573')
          subset=values[offset:offset+per_page];manifest.append(dict(page=len(manifest)+1,section=section,examples=[x['id'] for x in subset]))
          for k,x in enumerate(subset):
            left=k%cols*cell_width+15;top=k//cols*cell_height+80
            label=x.get('entry_id',x['id'])+' / '+x['id']+' '+x.get('entry_title',x.get('title',x['id']))
            draw.text((left+4,top+4),label[:34],font=ImageFont.truetype(FONT,15),fill='#273540')
            with Image.open(G/x['png']) as source:
              source.draft('RGB',(1000,1000));pic=source.convert('RGB');pic.thumbnail((cell_width-30,cell_height-60))
            page.paste(pic,(int(left+4+(cell_width-30-pic.width)/2),int(top+40+(cell_height-60-pic.height)/2)));pic.close()
          draw.text((24,1715),'Contact overview only. Use standalone SVG/PDF for native-size inspection.',font=ImageFont.truetype(FONT,14),fill='#566573')
          file=Path(temporary)/(str(len(manifest))+'.pdf');page.save(file,'PDF',resolution=96,quality=85);page.close();writer.append(file)
      with path.open('wb') as stream:writer.write(stream)
      writer.close()
    return manifest

def main():
    O.mkdir(exist_ok=True);c=json.loads((G/'catalog.json').read_text(encoding='utf8'));items=[dict(x,png=x.get('current_preview',{}).get('png',x['png'])) for x in c['preserved_examples']];by={x['id']:x for x in items};methods=c['drawing_methods']
    primary=[dict(by[m['default']],entry_id=m['id'],entry_title=m['title'],entry_role=m['role'],png=by[m['default']].get('current_preview',{}).get('png',by[m['default']]['png'])) for m in methods]
    sections=[(label,[x for x in primary if x['entry_role'] in roles]) for roles,label in [(['figure'],'通用画法'),(['combination'],'具有明确数据关系的组合'),(['protein','support'],'原生结构与说明附表'),(['palette'],'课题色卡库（15套）')]]
    for name,values,title,cols in [('visualization-overview',primary,f"v{c['version']} 去重目录：{len(methods)}个入口；15套色卡单独归入库",3),('all-previews',items,f"v{c['version']} 来源档案：{len(items)}个原编号；包含重复与参数示例",4)]:
        im=contact(values,cols,title);im.save(O/(name+'.png'),optimize=True);im.save(O/(name+'.jpg'),quality=90);im.close()
    drawn=[x for x in primary if x['entry_role'] in ['figure','combination']]
    im=contact(drawn,3,'去重后的通用画法与组合；参数模式在各入口内选择');im.save(O/'general-patterns.png',optimize=True);im.save(O/'general-patterns.jpg',quality=90);im.close()
    pages=book(sections,O/'visualization-overview.pdf',f"v{c['version']} 去重后的画法、组合与色卡库")
    archive=book([('来源档案：含重复示例；请用主目录选择画法',items)],O/'source-archive-v021.pdf',f"v{c['version']} 完整来源档案")
    full=json.loads((G/'publication-v030/review-index.json').read_text(encoding='utf8'))
    book([('逐项自检：独立图与全部排版',[dict(id=x['id'],title=x['id'],png=x['assets']['png']) for x in full['records']])],O/'full-atlas-v030.pdf','v0.3.0 · 400 individually inspected exports')
    with (O/'index.tsv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['id','family','title','role','decision','canonical','data_required','expression','png'])
        for x in items:w.writerow([x[k] for k in ['id','family','title','role']]+[x['curation']['decision'],x['curation']['canonical'],x['data_required'],x['expression'],'../gallery/'+x['png']])
    with (O/'methods.tsv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['entry','primary_example','title','role','sources','modes'])
        for m in methods:w.writerow([m['id'],m['default'],m['title'],m['role'],' '.join(m['members']),' '.join(x['example'] for x in m['modes'])])
    import hashlib
    receipt=dict(version=c['version'],primary_entries=len(primary),drawing_entries=len(drawn),source_examples=len(items),primary_pages=pages,archive_pages=archive,
                 primary_assets=[dict(id=x['id'],png=x['png'],sha256=hashlib.sha256((G/x['png']).read_bytes()).hexdigest()) for x in primary])
    (O/'overview-index.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(primary_entries=len(primary),drawing_entries=len(drawn),sources=len(items),primary_pdf_pages=len(pages),archive_pdf_pages=len(archive))))
if __name__=='__main__':main()
