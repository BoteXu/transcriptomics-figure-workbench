"""Read-only bundle checks plus isolated PDF/gray previews; optional installed PyMuPDF/Pillow."""
from pathlib import Path
import json,sys,xml.etree.ElementTree as ET
from figure_core import file_sha256
root=Path(sys.argv[1]);review=root/(sys.argv[2] if len(sys.argv)>2 else '_export_review');review.mkdir(exist_ok=False)
import fitz
from PIL import Image,ImageOps,ImageDraw
records=[]
for receipt_path in sorted(root.glob('*/*.json')):
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    if 'output_sha256' not in receipt:continue
    name=receipt['figure_id'];base=receipt_path.parent
    for file,h in receipt['output_sha256'].items():
        assert file_sha256(base/file)==h,(name,file)
    assert file_sha256(base/(name+'.tsv'))==receipt['input_hash']
    svg=ET.parse(base/(name+'.svg')).getroot()
    def count(tag):return len(svg.findall('.//{http://www.w3.org/2000/svg}'+tag))
    assert count('text')>0 and count('path')>0
    svgdoc=fitz.open(base/(name+'.svg'));assert len(svgdoc)==1
    svgdoc[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(review/(name+'_svg.png'));svgdoc.close()
    doc=fitz.open(base/(name+'.pdf'));assert len(doc)==1
    page=doc[0];text=page.get_text()
    assert 'SYNTHETIC DEMO' in text
    outside=[]
    for word in page.get_text('words'):
        x0,y0,x1,y1=word[:4]
        if x0 < -.5 or y0 < -.5 or x1 > page.rect.width+.5 or y1 > page.rect.height+.5:outside.append(word[4])
    assert not outside,(name,'text_outside_page',outside)
    pix=page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
    pix.save(review/(name+'_pdf.png'))
    image=Image.open(base/(name+'.png'));assert image.width>1000 and image.height>600
    ImageOps.grayscale(image).save(review/(name+'_gray.png'))
    fonts=page.get_fonts(full=True)
    records.append({'id':name,'pdf_pages':1,'pdf_fonts':[f[3] for f in fonts],
                    'pdf_text_outside_page':outside,'svg_text_elements':count('text'),
                    'svg_path_elements':count('path'),'svg_image_elements':count('image'),
                    'pdf_sha256':file_sha256(base/(name+'.pdf')),
                    'png_sha256':file_sha256(base/(name+'.png')),
                    'svg_sha256':file_sha256(base/(name+'.svg')),
                    'visual_review':'PENDING','svg_pixel_review':'LIMITED_PYMUPDF_PREVIEW_NOT_VISUAL_ACCEPTANCE'})
    doc.close()
new=[r for r in records if r['id'] not in ('old_heatmap','new_heatmap')]
for mode in ('pdf','svg','gray'):
    canvas=Image.new('RGB',(1600,1700),'white');draw=ImageDraw.Draw(canvas)
    for i,r in enumerate(new):
        p=review/(r['id']+'_'+mode+'.png');im=Image.open(p).convert('RGB');im.thumbnail((770,510))
        x=(i%2)*800+(800-im.width)//2;y=(i//2)*560+30
        canvas.paste(im,(x,y));draw.text(((i%2)*800+25,(i//2)*560+10),r['id'],fill='#27323C')
    canvas.save(review/(mode+'_contact.png'))
(review/'export_checks.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps({'bundles':len(records),'hashes':'PASS','PDF_fonts_text_and_bounds':'PASS',
                  'SVG_actual_vector_text_structure':'PASS','PDF_previews':str(review),
                  'SVG_pixel_render':'LIMITED_PYMUPDF_PREVIEW; verify in standards-compliant browser'}))


