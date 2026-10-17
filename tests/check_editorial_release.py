"""Check evidence scope, byte preservation and exact current export/review binding."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
    forms={f['id'] for f in load(SKILL/'references/form-catalog.json')['forms']}
    search=load(SKILL/'references/journal-search-v092.json')
    assert len(search['records'])==len(forms)==90
    assert {r['form'] for r in search['records']}==forms
    for r in search['records']:
        assert r['query'] and r['candidates'] and r['inspection']=='search_results_only'
        assert not r['design_adoption_authorized']
        assert all(c['url'].startswith('https://') and '?' not in c['url'] for c in r['candidates'])
    sources=load(SKILL/'references/journal-design-v092.json')['sources'];ids={s['id'] for s in sources}
    assert len(sources)==8 and len({s['url'] for s in sources})==7
    assert all(s['inspection']=='caption_and_original_pixels' and s['adopt'] and s['reject'] and s['implementation'] for s in sources)
    decisions=load(SKILL/'references/journal-form-review-v092.json')['records']
    assert {r['form'] for r in decisions}==forms and len(decisions)==90
    for r in decisions:assert set(r['reviewed_source_ids'])<=ids and len(r['decision'])>20
    for base in [ROOT/'examples/editorial-v092',SKILL/'assets/editorial-gallery']:
        d=load(base/'manifest.json');ledger=load(base/'review-ledger.json')
        assert d['version']=='0.9.2' and len(d['records'])==27
        lookup={r['id']:r for r in ledger['records']}
        assert not ledger['aesthetic_publication_approval']
        assert sum(r['input_unchanged'] for r in d['records'])==23
        assert sum('before_png' in r for r in d['records'])==23
        for r in d['records']:
            for key,digest in r['sha256'].items():assert sha(base/r['assets'][key])==digest,(r['id'],key)
            assert r['sha256']['png']==lookup[r['id']]['png_sha256']==r['visual_review']['png_sha256']
            spec=load(base/r['assets']['spec']);table=(base/r['assets']['spec']).parent/spec['input']['path']
            assert sha(table)==spec['input']['sha256']
            if 'before_png' in r:assert sha(base/r['before_png'])==r['before_sha256']
    # Existing galleries and old versioned snapshots each retain independent receipts.
    updated=0
    for name in ['study','chapter','subgroup','chapter-layouts']:
        base=SKILL/('assets/'+name+'-gallery');doc=load(base/'manifest.json')
        lookup={r['id']:r for r in load(base/'review-ledger.json')['records']}
        for r in doc['records']:
            assert sha(base/r['assets']['png'])==r['sha256']['png']==lookup[r['id']]['png_sha256']
            if r.get('display_revision')=='0.9.2' or '0.9.2' in r.get('display_revision_history',[]):
                updated+=1;spec=load(base/r['assets']['spec'])
                assert sha((base/r['assets']['spec']).parent/spec['input']['path'])==spec['input']['sha256']
    assert updated==23
    studio=(SKILL/'assets/figure-studio.html').read_text(encoding='utf8')
    state=json.loads(studio.split('studio-data',1)[1].split('>',1)[1].split('</script>',1)[0])
    assert not state['examples'] and len(state['design_examples'])==94
    assert [r['id'] for r in state['design_examples'][:2]]==['RoutineBulkPCA','RoutineCellTypes']
    assert state['registry']==load(SKILL/'references/renderer-registry.json')
    for r in state['design_examples']:
        p=(SKILL/'assets'/r['png']).resolve()
        assert SKILL.resolve() in p.parents and p.is_file(),'Installed preview escapes the portable skill'
    full=(ROOT/'examples/studio/index.html').read_text(encoding='utf8')
    assert len(json.loads(full.split('studio-data',1)[1].split('>',1)[1].split('</script>',1)[0])['examples'])==260
    print(json.dumps(dict(status='EDITORIAL_RELEASE_PASS',forms_searched=90,reviewed_original_figures=8,screened_exports=27,refreshed_existing_exports=23,scientific_acceptance=False)))
if __name__=='__main__':check()
