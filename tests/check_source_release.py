"""Check exact source-example and review bindings, never aesthetic judgment."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    from figure_workbench.contracts import make_plan
    base=ROOT/'examples/source-v093';review=load(base/'review-ledger.json')
    assert len(review['records'])==405 and not review['aesthetic_publication_approval']
    seen={(r['scope'],r['id']):r for r in review['records']};native=0
    for scope,count in [('single',96),('volume/small',87),('volume/medium',87),('volume/large',87),('layout',48)]:
        doc=load(base/scope/'manifest.json');assert len(doc['records'])==count
        assert (base/scope/'index.html').is_file()
        for r in doc['records']:
            row=seen[scope,r['id']]
            for suffix in ['png','svg','pdf']:
                p=(base/scope/r['file']).with_suffix('.'+suffix)
                assert p.is_file() and sha(p)==row[suffix+'_sha256'],(scope,r['id'],suffix)
            assert row['decision']=='screen_reviewed' and not row['scientific_acceptance']
            for name,digest in r.get('files',r.get('output_sha256',{})).items():
                assert sha((base/scope/r['file']).parent/name)==digest,(scope,r['id'],name)
            if 'adapter' in r:
                p=(base/scope/r['file']).parent/'example.spec.json';spec=load(p)
                request=load(p.parent/'request.json')
                assert spec['renderer']==r['adapter'];make_plan(spec,p.parent);native+=1
                assert spec['parameters']==request['parameters'] and spec['theme']==request['theme']
                assert spec.get('layout')==r.get('requested_layout')
                assert sha(p.parent/spec['input']['path'])==r['input_sha256']
    assert native==355
    source=load(SKILL/'references/source-design-v093.json');assert len(source['forms'])==90 and len(source['new_sources'])==34
    assert all(r['original_source_ids'] and r['adopted_designs'] and r['reviewed_png_sha256'] for r in source['forms'])
    gallery=SKILL/'assets/source-gallery';installed=load(gallery/'manifest.json')['records'];assert len(installed)==96
    for r in installed:
        assert sha(gallery/r['assets']['png'])==seen['single',r['id']]['png_sha256']
        for kind,p in r['assets'].items():assert sha(gallery/p)==r['sha256'][kind]
        if 'example.spec.json' in r['assets']:
            p=gallery/r['assets']['example.spec.json'];make_plan(load(p),p.parent)
    print(json.dumps(dict(status='SOURCE_RELEASE_BINDINGS_PASS',forms=90,export_views=405,portable_native_specs=355,installed_views=96,aesthetic_approval=False,scientific_acceptance=False)))
if __name__=='__main__':main()
