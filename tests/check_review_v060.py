"""Current review/reader bindings; historical files and native claims stay honest."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    folder=ROOT/'examples/review-v060';index=json.loads((folder/'figure-index.json').read_text());report=json.loads((folder/'review-index.json').read_text());reading=json.loads((ROOT/'examples/reading-v060/reading-index.json').read_text())
    assert len(report['records'])==443 and report['counts']['individual_screen_inspected']==317 and report['counts']['composition_overviews_inspected']==126
    assert reading['source_index_sha256']==sha(folder/'figure-index.json') and len(reading['records'])==443
    old={r['id']:r for r in json.loads((ROOT/'examples/review-v050/review-index.json').read_text())['records']}
    repaired=0
    for r in report['records']:
        key=r['id'];assert r['visual_review']['png_sha256']==r['sha256']['png']
        for ext,file in r['assets'].items():assert sha(ROOT/file)==r['sha256'][ext]
        q=next(q for q in reading['records'] if q['id']==key);assert q['source_sha256']==r['sha256']['pdf'] and r['reading']['source_pdf_sha256']==r['sha256']['pdf']
        assert r['reading']['page']==q['start_page'] and r['reading']['pdf'].endswith(q['file'])
        if r['collection']=='refined display repair':
            repaired+=1
            assert r['previous_sha256']==old[key]['sha256']
            meta=json.loads((ROOT/r['assets']['meta']).read_text());before=json.loads((ROOT/old[key]['assets']['meta']).read_text())
            if key not in ['P10','R05']:assert meta['frozen_graphical_geometry_sha256']==before['frozen_graphical_geometry_sha256']
            # The two rerendered sources use the exact original selected table;
            # only declared artist colours / semantic palette hooks changed.
            assert meta['input_sha256']==before['input_sha256']
        assert r['scientific_acceptance'] is False
    assert repaired==32
    for item in reading['volumes']:assert sha(ROOT/'examples/reading-v060'/item['file'])==item['sha256']
    print(json.dumps(dict(status='REVIEW_V060_BINDINGS_PASS',exports=443,repairs=32,reading_figures=443,historical_versions_preserved=True,scientific_acceptance=False)))
if __name__=='__main__':main()
