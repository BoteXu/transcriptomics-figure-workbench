"""Bounded individual image inspection sheets; never grant visual acceptance."""
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image, ImageDraw


def build(source, output):
    output.mkdir(parents=True, exist_ok=False)
    rows=json.loads((source/'manifest.json').read_text())['records'];pages=[]
    for start in range(0,len(rows),6):
        selected=rows[start:start+6];canvas=Image.new('RGB',(2400,3000),'#eaf0f2');draw=ImageDraw.Draw(canvas)
        for i,r in enumerate(selected):
            k=r['id'];x=(i%2)*1200;y=(i//2)*1000
            draw.text((x+18,y+10),k+' | independent full image',fill='#283740')
            with Image.open(source/k/(k+'.png')) as im:
                im.thumbnail((1160,950));canvas.paste(im.convert('RGB'),(x+(1200-im.width)//2,y+36))
        file='sheet-'+str(start//6+1).zfill(3)+'.jpg';canvas.save(output/file,quality=94);canvas.close()
        pages.append(dict(file=file,ids=[r['id'] for r in selected],sha256=hashlib.sha256((output/file).read_bytes()).hexdigest(),scope='six separately framed full images; screen only'))
    (output/'manifest.json').write_text(json.dumps(dict(pages=pages,prepared_only=True,visual_acceptance=False),indent=2)+'\n')
    print(json.dumps(dict(pages=len(pages),figures=len(rows))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();build(a.source,a.output)
