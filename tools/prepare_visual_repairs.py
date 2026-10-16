"""Prepare five source-bound display-only repairs, preserving old exports."""
from pathlib import Path
import argparse, copy, json, re, xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]


def prepare(path):
    plan=json.loads((ROOT/'examples/gallery/publication-v030/source-plan.json').read_text(encoding='utf8'))
    items=[]
    for key in ['R01','R02','R03','R07','R16']:
        row=copy.deepcopy(next(r for r in plan['items'] if r['id']==key));patch=row.setdefault('patch',{})
        if key in ['R01','R02']:
            patch['color_map']=({'#77deff':'#218c8d','#ff72ac':'#d8795b','#ff9e7b':'#4b70a6'} if key=='R01' else
                                {'#f3485d':'#218c8d','#edf7ec':'#d8795b','#a7dde1':'#4b70a6'})
            patch['element_opacity']={k:.12 for k in ['patch_7','patch_8','patch_9']}
        if key=='R03':
            root=E.fromstring((ROOT/row['svg']).read_text(encoding='utf8'))
            labels=[n.text.strip() for n in root.iter() if n.tag.endswith('}text') and n.text and re.fullmatch(r'\d\.\d state \d',n.text.strip())]
            assert len(labels)==28
            patch['text_moves']={s:[-10,0] for s in labels}
        if key=='R07':patch['color_map']={'#91dd6f':'#bdc7cf','#6c6092':'#4b70a6','#df3450':'#d8795b'}
        if key=='R16':
            root=E.fromstring((ROOT/row['svg']).read_text(encoding='utf8'))
            patch['element_opacity']={n.get('id'):.65 for n in root.iter() if n.get('id','').startswith('PathCollection')}
            assert patch['element_opacity']
        items.append(row)
    with path.open('x',encoding='utf8') as stream:json.dump(dict(schema_version=1,items=items),stream,ensure_ascii=False,indent=2)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);prepare(parser.parse_args().output)
