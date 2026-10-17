"""Actual per-chapter coverage, portable templates and exact reviewed artifacts."""
import csv,hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'));sys.path.insert(0,str(ROOT/'tools'))
from figure_workbench.contracts import read_json,make_plan
from figure_workbench.analysis_suites import analysis_library,analysis_suite
from analysis_companion_recipes import RECIPES,validate_recipes

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def read_catalog(path):
    # The aggregate shipped catalogue is larger than a single FigureSpec.
    # Keep the product's 2 MiB user-configuration gate unchanged.
    assert path.stat().st_size <= 8*1024*1024
    return json.loads(path.read_text(encoding='utf8'))

def check_revised_core_ledgers():
    # A panel's callable ID must not replace its parent gallery's ledger key.
    for name in ['analysis-gallery','chapter-gallery','method-depth-gallery']:
        folder=SKILL/'assets'/name;gallery=read_catalog(folder/'manifest.json')['records']
        ledger={r['id']:r for r in read_catalog(folder/'review-ledger.json')['records']}
        assert set(ledger)=={r['id'] for r in gallery},name
        for r in gallery:
            assert ledger[r['id']]['png_sha256']==sha(folder/r['assets']['png'])

def main():
    assert validate_recipes()==56
    base=SKILL/'assets/companion-gallery';m=read_catalog(base/'manifest.json');proof=read_json(base/'review-ledger.json')
    assert m['version']=='0.10.0' and len(m['records'])==425 and proof['state']=='SCREEN_REVIEWED'
    by={r['id']:r for r in proof['records']};assert len(by)==425
    for r in m['records']:
        assert r['review']==by[r['id']] and r['review']['state']=='SCREEN_REVIEWED'
        assert r['sha256']['png']==r['review']['png_sha256'] and r['review']['notes']
        assert r['readability']['state']=='MEASUREMENT_PASS' and not r['scientific_acceptance']
        for k,digest in r['sha256'].items():assert sha(base/r['assets'][k])==digest,(r['id'],k)
        p=base/r['assets']['spec'];s=read_json(p);make_plan(s,p.parent)
        assert s['renderer']=='figure_analysis_evidence.plot_analysis_evidence' and s['provenance']['synthetic'] is True
        assert sha(p.parent/s['input']['path'])==s['input']['sha256']
        assert all(p['definition'] for p in s['parameters']['panels'])
        if r['large_data']:assert s['parameters']['columns'] in [1,3]
    suites=analysis_library();assert len(suites)==58
    all_views={v['id']:v for v in read_json(SKILL/'references/analysis-views.json')['views']}
    for chapter in RECIPES:
        suite=next(s for s in suites if s['id']==chapter)
        rows=[r for r in m['records'] if chapter in r['chapters']]
        assert len(rows)>=7 and any(r['large_data'] for r in rows),chapter
        assert any(r['id'].endswith('_Evidence') for r in rows),chapter
        assert suite['coverage']['qc'] and suite['coverage']['validation'] and suite['coverage']['layout'],chapter
        assert len(suite['primary_views'])>=6,chapter
        assert any(all_views[k].get('catalog_origin')!='analysis_companions_v100' for k in suite['primary_views']),chapter
        # Every chapter exports its actual full default templates into an isolated root.
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'suite';receipt=analysis_suite(chapter,out);manifest=read_json(out/'manifest.json')
            assert receipt['figures']==len(suite['primary_views'])==len(manifest['records'])
            for row in manifest['records']:
                p=out/row['spec'];make_plan(read_json(p),p.parent)
    library=read_catalog(SKILL/'assets/analysis-library/manifest.json')
    assert library['actual_pages']==len(library['records'])>=550
    for r in library['records']:
        for key in ['png','svg','pdf','tsv','spec']:
            path=(SKILL/'assets/analysis-library'/r['assets'][key]).resolve();assert SKILL.resolve() in path.parents and path.is_file()
    check_revised_core_ledgers()
    print(json.dumps(dict(state='ALL_ANALYSIS_COMPANION_COVERAGE_PASS',chapters=58,expanded_chapters=56,individually_reviewed_exports=425,portable_suites_checked=56,scientific_acceptance=False)))

if __name__=='__main__':main()
