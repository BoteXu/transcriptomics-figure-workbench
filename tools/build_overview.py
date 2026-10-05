"""Regenerate complete illustrated indexes from the release catalog."""
from pathlib import Path
import json,csv,math
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont
import fitz
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'examples/gallery';O=ROOT/'examples/overview'
FONT=font_manager.findfont('DejaVu Sans')
def contact(items,columns,cell_width=600,cell_height=510):
    image=Image.new('RGB',(columns*cell_width,math.ceil(len(items)/columns)*cell_height+75),'white');d=ImageDraw.Draw(image);font=ImageFont.truetype(FONT,22)
    d.text((20,18),f'Scientific figure workbench v0.2.0 | {len(items)} previews',fill='#21313e',font=font)
    for n,x in enumerate(items):
        left=n%columns*cell_width;top=n//columns*cell_height+75
        d.text((left+12,top+4),x['id']+' / '+x['family']+' / '+x['curation']['decision'],fill='#526272',font=font)
        pic=Image.open(G/x['png']).convert('RGB');pic.thumbnail((cell_width-24,cell_height-55))
        image.paste(pic,(left+(cell_width-pic.width)//2,top+40+(cell_height-55-pic.height)//2))
    return image
def main():
    O.mkdir(exist_ok=True);c=json.loads((G/'catalog.json').read_text(encoding='utf8'));items=c['preserved_examples'];by={x['id']:x for x in items}
    im=contact(items,4);im.save(O/'all-previews.png',optimize=True);im.save(O/'all-previews.jpg',quality=88)
    recommended=[by[g['default']] for g in c['general_entries']];im=contact(recommended,3);im.save(O/'general-patterns.png',optimize=True);im.save(O/'general-patterns.jpg',quality=92)
    book=fitz.open()
    for offset in range(0,len(items),12):
        page=book.new_page(width=1260,height=1740);page.insert_text((24,30),'Scientific figure workbench v0.2.0 - all stable examples',fontsize=17)
        page.insert_text((24,54),f'Page {offset//12+1} / {math.ceil(len(items)/12)} | Independent panels, compositions, structures and palettes',fontsize=10)
        for k,x in enumerate(items[offset:offset+12]):
            col=k%3;row=k//3;left=col*420+15;top=row*410+80
            page.insert_text((left+5,top+16),x['id']+' / '+x['family']+' / '+x['curation']['decision'],fontsize=11)
            image=Image.open(G/x['png']).convert('RGB');image.thumbnail((800,750));buf=BytesIO();image.save(buf,format='JPEG',quality=92)
            page.insert_image(fitz.Rect(left+4,top+31,left+399,top+398),stream=buf.getvalue(),keep_proportion=True)
        page.insert_text((24,1730),'Preview index only: use the standalone vector PDF for final-size review. Data tables and parameters remain separate.',fontsize=9)
    book.save(O/'all-previews.pdf',deflate=True);book.close()
    with (O/'index.tsv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['id','family','title','role','decision','canonical','data_required','expression','png'])
        for x in items:w.writerow([x[k] for k in ['id','family','title','role']]+[x['curation']['decision'],x['curation']['canonical'],x['data_required'],x['expression'],'../gallery/'+x['png']])
    print(json.dumps(dict(previews=len(items),pdf_pages=math.ceil(len(items)/12),general_entries=len(recommended))))
if __name__=='__main__':main()
