"""Verify the new public source and exact reviewed display exports; no analysis."""
from pathlib import Path
import ast,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/scientific-visualization';G=ROOT/'examples/scientific-v220'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((S/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
 expected={r['path']:r for r in d['files']};actual={p.relative_to(S).as_posix():p for p in S.rglob('*') if p.is_file() and p!=S/'SOURCE_MANIFEST.json' and '__pycache__' not in p.parts}
 assert set(expected)==set(actual)
 for name,p in actual.items():assert sha(p)==expected[name]['sha256'] and p.stat().st_size==expected[name]['bytes'],name
 assert (S/'VERSION').read_text().strip()==(ROOT/'SCIENTIFIC_VERSION').read_text().strip()=='2.2.0'
 entry=(S/'SKILL.md').read_text(encoding='utf8');assert '\nid:' not in entry and 'name: "scientific-visualization"' in entry
 catalog=json.loads((S/'assets/figure_catalog.json').read_text(encoding='utf8'))
 for key,n in [('figures',140),('modules',22),('composites',7)]:assert len(catalog[key])==len({x['id'] for x in catalog[key]})==n
 records=json.loads((G/'visual_reviews.json').read_text(encoding='utf8'));assert len(records)==16
 for r in records:
  assert r['visual_review']=='PASS_FOR_DECLARED_FROZEN_DISPLAY_CASE' and not r['text_outside_canvas']
  for name,h in r['outputs'].items():assert sha(G/name)==h
 assert all((G/'licenses'/n).is_file() for n in ['fgsea-LICENCE.txt','AutoDock-Vina-LICENSE.txt','MDAnalysis-LICENSE.txt'])
 assert (S/'assets/fonts/OFL.txt').is_file() and (S/'assets/viewer/LICENSE.txt').is_file()
 # The original literal values remain in the manifests; no target or data is
 # executed to obtain these results. Source/runtime/scientific states differ.
 for p in S.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'))
 print(json.dumps({'scientific_source_files':len(actual)+1,'catalog':d['catalog_counts'],'reviewed_frozen_display_exports':16,'source_manifest':'PASS','native_scientific_engines_run':0}))
if __name__=='__main__':main()
