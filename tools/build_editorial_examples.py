# -*- coding: utf-8 -*-
"""Reproducible display revisions from public frozen fixtures, not analysis."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'

def build(out):
    out.mkdir(parents=True,exist_ok=False);records=[]
    galleries=['study-gallery','chapter-gallery','subgroup-gallery','chapter-layouts-gallery']
    for gallery in galleries:
        for source in sorted((SKILL/'assets'/gallery).glob('**/*.spec.json')):
            s=json.loads(source.read_text(encoding='utf8'))
            if not s['renderer'].startswith(('figure_annotation_views.','figure_enrichment_story.')):continue
            key=s['figure_id'];p=out/key;p.mkdir()
            raw=(source.parent/s['input']['path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==s['input']['sha256']
            s['input']['path']='example.tsv';(p/'example.tsv').write_bytes(raw)
            (p/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
            records.append(dict(id=key,spec=key+'/example.spec.json',assay='single_cell' if key.startswith(('single_cell','Subgroup','Layout','Cell','Single','Donor')) else 'bulk',
                origin_spec=source.relative_to(SKILL).as_posix(),frozen_input_unchanged=True))
    # Same form, larger supplied display scope. Fictional suffixes are explicit;
    # they are not discovered markers, real identities or new scientific tests.
    import pandas as pd
    seed=out/'Subgroup_01';s0=json.loads((seed/'example.spec.json').read_text(encoding='utf8'))
    d0=pd.read_csv(seed/'example.tsv',sep='\t')
    for count,cols in [(2,'auto'),(8,'auto'),(12,'auto'),(4,2)]:
        key='Evidence_'+str(count).zfill(2)+'Markers_'+str(cols)+'Columns';p=out/key;p.mkdir()
        s=copy.deepcopy(s0);s['figure_id']=key
        original=s['parameters']['marker_order'];selected=[];parts=[d0[d0.record_type=='embedding']]
        for i in range(count):
            name=original[i%4]+('_demo'+str(i//4+1) if i>=4 else '')
            selected.append(name);q=d0[d0.feature==original[i%4]].copy();q['feature']=name;parts.append(q)
        d=pd.concat(parts,ignore_index=True)
        raw=d.to_csv(sep='\t',index=False,float_format='%.17g',lineterminator='\n').encode('utf8')
        s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest())
        s['parameters'].update(marker_order=selected,composition='evidence',ncols=cols)
        s['export']['target_width_mm']=260 if count>4 else 240
        (p/'example.tsv').write_bytes(raw);(p/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        records.append(dict(id=key,spec=key+'/example.spec.json',assay='single_cell',frozen_input_unchanged=False,
            fixture_definition='Explicit fictional marker duplicates for layout stress only; no inference'))
    (out/'manifest.json').write_text(json.dumps(dict(version='0.9.2',records=records,analysis_performed=False),indent=2)+'\n',encoding='utf8')
    print('EDITORIAL_INPUTS '+str(len(records)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
