"""Check portable reviewed examples against exact inputs and current code."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.registry import source_identity

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    root=SKILL/'assets/transcriptomic-alternatives';manifest=json.loads((root/'manifest.json').read_text('utf8'));review=json.loads((root/'screen-review.json').read_text('utf8'))
    assert len(manifest['records'])==len(review['records'])==28
    assert {r['id'] for r in manifest['records']}=={r['id'] for r in review['records']}
    assert review['state']=='SCREEN_SELF_REVIEW_PASS'
    identity=source_identity()
    for r in review['records']:
        assert r['state']=='SCREEN_SELF_REVIEW_PASS' and not r['print_proof'] and not r['independent_review'] and not r['scientific_acceptance']
        for ext,item in r['exports'].items():
            p=(root/item['path']).resolve();assert root.resolve() in p.parents and sha(p)==item['sha256']
        folder=root/r['id'];spec=json.loads((folder/'figure.spec.json').read_text('utf8'));bundle=folder/'export'/r['id'];receipt=json.loads((bundle/(r['id']+'.json')).read_text('utf8'))
        assert sha(folder/'input.tsv')==r['input_sha256']==spec['input']['sha256']==sha(bundle/(r['id']+'.tsv'))
        assert receipt['source_file']==r['id']+'.tsv' and (bundle/receipt['source_file']).is_file()
        assert receipt['workbench']['source_identity']==identity,'Code changed: rerender and inspect the affected examples'
        assert not receipt['workbench']['visual_acceptance'] and not receipt['workbench']['scientific_acceptance']
    print('28 portable screen-review/input/export bindings match current source; print, independent and scientific acceptance remain false')

if __name__=='__main__':main()
