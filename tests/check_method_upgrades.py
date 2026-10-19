"""Portable 42-recipe migration, exact inputs and individually bound exports."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'skills/transcriptomics-figure-workbench'
G=S/'assets/method-upgrade-gallery'
sys.path.insert(0,str(S/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.layout import make_layout


def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    d=read(G/'manifest.json');rows=d['records'];by={r['id']:r for r in rows}
    baseline=read(S/'references/historical-upgrade-baseline.json')['records']
    reviews={r['id']:r for r in read(G/'visual-review.json')['records']}
    assert len(baseline)==len({b['renderer'] for b in baseline})==42
    assert len(rows)==len(by)==138 and len(reviews)==138
    current=[r for r in rows if 'spec' in r['assets']]
    assert len(current)==93 and sum(bool(r.get('composition')) for r in rows)==45
    assert d['scientific_acceptance'] is False and d['aesthetic_approval'] is False
    for r in rows:
        for kind,value in r['assets'].items():
            p=(G/value).resolve()
            assert G.resolve() in p.parents and p.is_file(),(r['id'],kind)
            assert p.stat().st_size>0
        image=G/r['assets']['png'];review=reviews[r['id']]
        assert review['png_sha256']==sha(image) and review['state']=='SCREEN_REVIEWED'
        assert len(review['notes'])>40
        assert r['visual_review']['png_sha256']==sha(image)
        if r.get('composition'):
            p=G/r['assets']['layout'];request=read(p);plan=make_layout(request,p.parent)
            assert len(request['panels'])==2 and plan['status']=='FLEXIBLE_LAYOUT_PLAN'
            assert plan['source_content_preserved'] is True and plan['panel_count']==2
        else:
            p=G/r['assets']['spec'];spec=read(p);plan=make_plan(spec,p.parent)
            assert spec['provenance']['synthetic'] is True
            assert sha(p.parent/spec['input']['path'])==r['input_sha256']
            assert not re.search(r'[A-Za-z]:[\\/]|/(?:home|Users)/|127\.0\.0\.1|10\.10\.0\.',p.read_text('utf8'))
    for b in baseline:
        match=[r for r in current if r.get('upgraded_from')==b['original_id']]
        assert len(match)==2 and all(r['renderer']==b['renderer'] for r in match)
        assert all(r['input_sha256']==b['input_sha256'] for r in match)
        assert all(sha(G/r['assets']['tsv'])==b['input_sha256'] for r in match)
    for key,count in [('D03_Trajectory',24),('D03_Trajectory_Custom',24),('D03_Trajectory_Small',6)]:
        r=by[key];meta=read(G/r['assets']['animation'])
        assert len(meta['frame_ids'])==len(meta['times'])==count
        assert meta['coordinates_refit'] is False and meta['atom_count']==24 and meta['explicit_bonds']==23
        assert all(a<b for a,b in zip(meta['times'],meta['times'][1:]))
    media=read(G/'animation-review.json')
    assert media['external_requests']==0 and len(media['records'])==3
    for record in media['records']:
        for kind,digest in record['asset_sha256'].items():assert sha(G/by[record['id']]['assets'][kind])==digest
        assert record['input_sha256']==by[record['id']]['input_sha256'] and record['screen_review']
    print(json.dumps(dict(state='MIGRATED_METHODS_PORTABLE_INPUTS_AND_BOUND_REVIEWS_PASS',historical_recipes=42,current_native_specs=93,complete_compositions=45,individual_screen_reviews=138,scientific_acceptance=False)))


if __name__=='__main__':main()
