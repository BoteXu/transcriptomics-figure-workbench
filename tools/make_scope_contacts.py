"""Prepare bounded screen-inspection sheets; creating a sheet never approves it."""
import argparse,json
from pathlib import Path
def main(source,out):
    from PIL import Image,ImageDraw,ImageFont
    from matplotlib import font_manager
    rows=[]
    for r in json.loads((source/'manifest.json').read_text(encoding='utf8'))['records']:
        p=next((Path(x) for x in r.get('result',{}).get('files',[]) if x.endswith('.png')),None)
        if p is None:p=(source/r['file']).with_suffix('.png')
        rows.append(dict(id=r['id'],path=str(p)))
    out.mkdir(parents=True,exist_ok=False);font=ImageFont.truetype(font_manager.findfont('DejaVu Sans'),24);index=[]
    for start in range(0,len(rows),4):
        chosen=rows[start:start+4];sheet=Image.new('RGB',(2200,1900),'#e8eff1');draw=ImageDraw.Draw(sheet)
        for j,r in enumerate(chosen):
            x=(j%2)*1100;y=(j//2)*950;draw.text((x+24,y+10),r['id'],font=font,fill='#244858')
            with Image.open(r['path']) as im:im.thumbnail((1070,880));im=im.convert('RGB');sheet.paste(im,(x+(1100-im.width)//2,y+50+(880-im.height)//2))
        name='sheet-'+str(start//4+1).zfill(2)+'.jpg';sheet.save(out/name,quality=96);index.append(dict(sheet=name,ids=[r['id'] for r in chosen]))
    (out/'index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(sheets=len(index),figures=len(rows),review_performed=False)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.source,a.output)
