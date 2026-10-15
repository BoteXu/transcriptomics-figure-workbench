"""Two compact review sheets from actual exported PNGs; no scientific computation."""
import argparse
from pathlib import Path


def main(gallery, output):
    from PIL import Image,ImageDraw,ImageFont,ImageOps
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for prefix,filename in [('A','redesigned-modes-v030.jpg'),('B','new-drawing-modes-v030.jpg')]:
        sheet=Image.new('RGB',(2200,2170),'#EDF1F5');draw=ImageDraw.Draw(sheet)
        for i in range(6):
            id=prefix+str(i+1).zfill(2);x=30+(i%2)*1090;y=30+(i//2)*710
            draw.rounded_rectangle((x,y,x+1060,y+680),radius=12,fill='white')
            with Image.open(Path(gallery)/id/(id+'.png')) as original:
                panel=ImageOps.contain(original.convert('RGB'),(1030,640))
                sheet.paste(panel,(x+(1060-panel.width)//2,y+20+(640-panel.height)//2))
                panel.close()
        sheet.save(output/filename,quality=94,subsampling=0);sheet.close()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--gallery',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.gallery,a.output)
