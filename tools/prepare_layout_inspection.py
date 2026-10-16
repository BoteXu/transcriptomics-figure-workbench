"""Prepare separately framed complete-image sheets; never approve a figure."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image,ImageDraw


def main(roots,out,selected=None):
    out.mkdir(parents=True,exist_ok=False);rows={}
    for root in roots:
        report=json.loads((root/'manifest.json').read_text())
        for r in report['records']:
            if selected and r['id'] not in selected:continue
            p=(root/r['file']).with_suffix('.png') if r.get('file') else root/r['id']/(r['id']+'.png')
            if p.is_file() and r.get('status')!='FAILED':rows[r['id']]=dict(id=r['id'],png=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    rows=list(rows.values());sheets=[]
    for start in range(0,len(rows),4):
        items=rows[start:start+4];canvas=Image.new('RGB',(2400,2000),'#EAF0F2');draw=ImageDraw.Draw(canvas)
        for i,row in enumerate(items):
            x=(i%2)*1200;y=(i//2)*1000;draw.text((x+16,y+12),row['id'],fill='#24343C')
            with Image.open(row['png']) as source:
                source.thumbnail((1160,940));canvas.paste(source.convert('RGB'),(x+(1200-source.width)//2,y+40+(940-source.height)//2))
        file='sheet-'+str(start//4+1).zfill(3)+'.jpg';canvas.save(out/file,quality=95);canvas.close();sheets.append(dict(file=file,ids=[r['id'] for r in items]))
    (out/'manifest.json').write_text(json.dumps(dict(sheets=sheets,images=rows,review_status='PENDING',scope='Separately framed complete images, resized on screen; dense details require enlargement'),indent=2)+'\n')
    print(json.dumps(dict(sheets=len(sheets),images=len(rows))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--roots',nargs='+',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.roots,a.output)
