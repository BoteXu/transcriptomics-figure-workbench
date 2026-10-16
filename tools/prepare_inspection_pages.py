"""Prepare bounded side-by-side individual views and dense-figure detail crops."""
from pathlib import Path
import argparse,json,hashlib,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def build(index,output):
    output.mkdir(exist_ok=False,parents=True);rows=json.loads(index.read_text(encoding='utf8'))['records'];leaves=[r for r in rows if not r.get('components')];comps=[r for r in rows if r.get('components')]
    pages=[]
    for kind,items,cell in [('single',leaves,(960,1050)),('composition',comps,(960,1050))]:
        for start in range(0,len(items),2):
            selected=items[start:start+2];canvas=Image.new('RGB',(cell[0]*2,cell[1]),'#edf1f3');d=ImageDraw.Draw(canvas)
            for j,r in enumerate(selected):
                x=j*cell[0];d.text((x+20,12),r['id']+' | full image screen view',fill='#243449')
                with Image.open(ROOT/r['assets']['png']) as image:
                    image.thumbnail((cell[0]-32,cell[1]-60));tile=image.convert('RGB');canvas.paste(tile,(x+16+(cell[0]-32-tile.width)//2,44));tile.close()
            name=kind+'-'+str(start//2+1).zfill(3)+'.jpg';canvas.save(output/name,quality=95);canvas.close();pages.append(dict(file=name,ids=[r['id'] for r in selected],scope='two_independent_full_images_on_screen' if kind=='single' else 'composition_overview_and_component_identity'))
    (output/'manifest.json').write_text(json.dumps(dict(pages=pages,source_index_sha256=hashlib.sha256(index.read_bytes()).hexdigest(),visual_acceptance=False),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(single_pages=math.ceil(len(leaves)/2),composition_pages=math.ceil(len(comps)/2),scope='Prepared only; visual inspection pending')))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--index',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.index,a.output)
