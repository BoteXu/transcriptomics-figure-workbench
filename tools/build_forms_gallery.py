"""Build the consolidated public and portable galleries, with nested extensions."""
import copy,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'


def build():
    catalog=json.loads((SKILL/'references/form-catalog.json').read_text(encoding='utf8'))
    records={r['id']:r for r in json.loads((ROOT/'examples/forms-v080/manifest.json').read_text(encoding='utf8'))['records']}
    template=(SKILL/'assets/studio/forms-gallery.html').read_text(encoding='utf8')
    portable=SKILL/'assets/forms-gallery';portable.mkdir(exist_ok=True)
    for folder,embedded in [(ROOT/'examples/forms-v080',False),(portable,True)]:
        d=copy.deepcopy(catalog)
        for g in d['forms']:
            for e in g['extensions']:
                k=e['id'];r=records[k]
                if embedded:
                    image=portable/(k+'.jpg')
                    with Image.open(ROOT/r['assets']['png']) as im:
                        im.thumbnail((1100,1400));im.convert('RGB').save(image,quality=91)
                    e['png']=k+'.jpg'
                    prefix='https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v0.8.0/'
                    e['links']={ext:prefix+r['assets'][ext] for ext in ['svg','pdf','meta']}
                    table=ROOT/'examples/forms-v080'/k/(k+'.tsv')
                    if table.is_file():e['links']['table']=prefix+table.relative_to(ROOT).as_posix()
                    e['previous_png']=None
                else:
                    e['png']=k+'/'+k+'.png';e['links']={ext:k+'/'+k+('.json' if ext=='meta' else '.'+ext) for ext in ['svg','pdf','meta']}
                    if (folder/k/(k+'.tsv')).is_file():e['links']['table']=k+'/'+k+'.tsv'
                    e['previous_png']='../../'+r['previous_assets']['png']
                e['review_note']=r['visual_review'].get('note','最终屏幕复查进行中；尚未授予视觉验收')
        (folder/'index.html').write_text(template.replace('/*FORM_DATA*/{}',json.dumps(d,ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    print(json.dumps(catalog['counts']))


if __name__=='__main__':build()
