"""Verify complete coverage, consolidation and artifact-bound review scope."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.forms import catalog_forms,form_entry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    c=json.loads((SKILL/'references/form-catalog.json').read_text(encoding='utf8'))
    m=json.loads((ROOT/'examples/forms-v080/manifest.json').read_text(encoding='utf8'))
    old=json.loads((ROOT/'examples/review-v070/review-index.json').read_text(encoding='utf8'))
    assert c['counts']==dict(base_forms=90,retained_examples=458,standalone=332,compositions=126,new_chart_types=0)
    ids=[e['id'] for g in c['forms'] for e in g['extensions']]
    assert len(ids)==len(set(ids))==458 and set(ids)=={r['id'] for r in old['records']}
    assert set(c['aliases'])==set(ids) and len(m['records'])==458
    assert not m['scientific_label_findings'] and not m['failures']
    for g in c['forms']:
        examples={e['id'] for e in g['extensions']}
        assert g['default'] in examples
        assert sorted(k for v in g['variants'] for k in v['example_ids'])==sorted(examples)
        assert all(v['preferred_example'] in v['example_ids'] for v in g['variants'])
    for same in [('P12a','T30','M02','PKG22','P36','E35'),('T06','T13','T38'),('T20','T21','T22','T23'),('PKG17','PKG18'),('R01','R02'),('E02','E03','E04','E05'),('K01','ALT_K01_horizontal','ALT_K01_vertical')]:
        assert len({c['aliases'][k] for k in same})==1
    for k in ['bars','gating','palettes','ridges','donut']:
        assert len(form_entry(k)['variants'])==1
    assert form_entry('PKG22')['id']=='heatmap' and form_entry('PKG22')['alias_resolved']
    assert catalog_forms('GSEA')['forms']
    engine=sha(SKILL/'assets/studio/form-polish.js')
    for r in m['records']:
        k=r['id'];meta=json.loads((ROOT/r['assets']['meta']).read_text(encoding='utf8'))
        for e,p in r['assets'].items():assert sha(ROOT/p)==r['sha256'][e],k+e
        for e,p in r['previous_assets'].items():assert sha(ROOT/p)==r['previous_sha256'][e],k+' source '+e
        assert meta['finisher_sha256']==engine and not meta['scientific_acceptance']
        v=r['visual_review'];assert v['status']=='SCREEN_REVIEWED' and v['png_sha256']==r['sha256']['png']
        assert not v['final_size_inspected'] and not v['calibrated_paper_proof'] and not v['independent_second_review']
        assert r['print_screen']['status']=='TARGET_SIZE_UNASSESSED'
        if not r.get('components'):
            assert meta['all_measured_primitives_retained'] and meta['same_form']
            assert meta['scientific_label_retention']['status']=='PASS'
            if meta['input_table']:assert sha(ROOT/meta['input_table'])==meta['input_sha256']
        else:
            assert {c['id'] for c in meta['components']}==set(r['components'])
            for c in meta['components']:assert sha(ROOT/'examples/forms-v080'/c['id']/(c['id']+'.svg'))==c['svg_sha256']
    print(json.dumps(dict(status='FORMS_RELEASE_PASS',base_entries=90,exports=458,scientific_acceptance=False)))
if __name__=='__main__':main()
