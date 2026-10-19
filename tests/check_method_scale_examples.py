"""Verify actual scale diversity, exact custom inputs and per-image review binding."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';G=S/'assets/method-scale-gallery'
sys.path.insert(0,str(S/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.layout import make_layout

def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    doc=read(G/'manifest.json');rows=doc['records'];by={r['id']:r for r in rows};reviews={r['id']:r for r in read(G/'visual-review.json')['records']}
    assert len(rows)==len(by)==len(reviews)==225
    assert doc['methods']==45 and doc['native_examples']==180 and doc['composition_examples']==45
    assert doc['scientific_acceptance'] is False and doc['aesthetic_approval'] is False
    methods={}
    for row in rows:
        methods.setdefault(row['method_id'],{})[row['scale_variant']]=row
        for k,value in row['assets'].items():
            p=(G/value).resolve();assert G.resolve() in p.parents and p.is_file() and p.stat().st_size
        image=G/row['assets']['png'];rev=reviews[row['id']]
        assert rev['state']=='SCREEN_REVIEWED' and rev['png_sha256']==sha(image)==row['visual_review']['png_sha256']
        assert len(rev['notes'])>45
        if row.get('composition'):
            request=read(G/row['assets']['layout']);plan=make_layout(request,(G/row['assets']['layout']).parent)
            assert plan['source_content_preserved'] and plan['panel_count']==2
        else:
            p=G/row['assets']['spec'];spec=read(p);make_plan(spec,p.parent)
            assert spec['provenance']['synthetic'] is True
            assert sha(p.parent/spec['input']['path'])==row['input_sha256']==sha(G/row['assets']['tsv'])
            assert not re.search(r'[A-Za-z]:[\\/]|/(?:home|Users)/|127\.0\.0\.1|10\.10\.0\.',p.read_text('utf8'))
    assert len(methods)==45
    for method,variants in methods.items():
        assert set(variants)=={'Small','Medium','Large','Custom','Composition'}
        assert len({variants[v]['input_sha256'] for v in ['Small','Medium','Large']})==3,(method,'scale inputs not distinct')
        assert variants['Large']['input_sha256']==variants['Custom']['input_sha256']==variants['Composition']['input_sha256']
        large=read(G/variants['Large']['assets']['spec']);custom=read(G/variants['Custom']['assets']['spec'])
        assert large['parameters']!=custom['parameters'] or large.get('layout')!=custom.get('layout'),method
        # The actual physical canvas must differ too; changing only an ID or an
        # ignored request cannot count as a custom-layout test.
        import xml.etree.ElementTree as ET
        boxes=[ET.parse(G/variants[v]['assets']['svg']).getroot().get('viewBox') for v in ['Large','Custom']]
        assert boxes[0]!=boxes[1],(method,'ignored custom canvas')
    frames=[]
    for variant in ['Small','Medium','Large','Custom']:
        row=methods['D03_Trajectory'][variant];meta=read(G/row['assets']['animation']);frames.append(len(meta['frame_ids']))
        assert meta['atom_count']==24 and meta['explicit_bonds']==23 and meta['coordinates_refit'] is False
        assert all(a<b for a,b in zip(meta['times'],meta['times'][1:]))
    assert frames==[6,12,24,24]
    media=read(G/'animation-review.json');assert len(media['records'])==4 and media['external_requests']==0
    for record in media['records']:
        row=by[record['id']]
        assert record['input_sha256']==row['input_sha256'] and record['screen_review']
        for kind,digest in record['asset_sha256'].items():assert sha(G/row['assets'][kind])==digest
    print(json.dumps(dict(state='ACTUAL_45_METHOD_SCALE_AND_LAYOUT_REVIEWS_PASS',methods=45,distinct_scale_inputs=135,native_images=180,complete_compositions=45,scientific_acceptance=False)))

if __name__=='__main__':main()
