"""Lossless catalog coverage, actual assets and runnable template exports."""
import ast
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(S/'scripts'))
from figure_workbench.visual_library import library,find,export,BASE
from figure_workbench.contracts import make_plan


def main():
    d=library(); by={r['id']:r for r in d['records']}; families={e['id']:e for e in d['entries']}
    forms=json.loads((S/'references/form-catalog.json').read_text(encoding='utf8'))['forms']
    assert len(by)==len(d['records'])
    assert sorted(k for e in families.values() for k in e['member_ids'])==sorted(by)
    for e in families.values():
        assert by[e['default_id']]['history'] is False, 'A whole method was hidden behind history'
        assert len(e['member_ids'])==len(set(e['member_ids']))
        if e['id'] not in {'scatter3d','volume-rendering','molecular-trajectory'}:
            assert not e['default_id'].startswith('method-upgrade-gallery/'),'Historical migration replaced a richer current default'
    for f in forms:
        assert f['id'] in d['aliases']
        for ext in f['extensions']:
            assert d['aliases'][ext['id']]=='legacy/'+ext['id']
            assert by['legacy/'+ext['id']]['form']==f['id']
    assert len([r for r in by.values() if r['history']])==458
    covered={c['source_id'] for c in d['coverage']}
    # Inspect all authoritative manifests, independently of the builder list.
    folders={a.split('/')[0] for a in covered if not a.startswith('legacy/')}
    assert len(folders)==21
    for folder in folders:
        m=json.loads((S/'assets'/folder/'manifest.json').read_text(encoding='utf8'))
        for r in m['records']:
            assert folder+'/'+r.get('key',r['id']) in covered
    for r in by.values():
        assert set(r['domains'])<=set(x['id'] for x in d['domains'])
        for kind,p in r['assets'].items():
            if p.startswith('https:'):
                assert r['history'] and '/blob/v0.8.0/' in p
            else:
                path=(BASE/p).resolve(); assert S in path.parents and path.is_file(),(r['id'],kind)
        if r['executable_spec']:
            spec=json.loads((BASE/r['assets']['spec']).read_text(encoding='utf8'))
            table=(BASE/r['assets']['spec']).parent/spec['input']['path']
            assert hashlib.sha256(table.read_bytes()).hexdigest()==spec['input']['sha256']
    coverage={r['renderer']:r for r in d['renderer_coverage']}
    registry=json.loads((S/'references/renderer-registry.json').read_text(encoding='utf8'))['renderers']
    assert set(coverage)=={r['id'] for r in registry}
    assert all(r['state']!='SOURCE_ONLY' for r in coverage.values())
    assert sum(r['state']=='CURRENT_SPEC' for r in coverage.values())==135
    assert not any(r['state']=='HISTORICAL_RECIPE' for r in coverage.values())
    # The one wrapper is accounted for as a wrapper, not a fictitious example.
    tree=ast.parse((S/'scripts/figure_palette_applications.py').read_text(encoding='utf8'))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='plot_palette_panel')
    call=next(n.value for n in fn.body if isinstance(n,ast.Return))
    assert isinstance(call.func,ast.Name) and call.func.id=='plot_palette_plate'
    assert coverage['figure_palette_applications.plot_palette_panel']['state']=='DELEGATING_WRAPPER'
    for a,b in [('heatmap','correlation'),('forest','point-interval'),('raincloud','box'),('raincloud','violin')]:
        assert by[d['aliases'][a]]['method']==by[d['aliases'][b]]['method']
    with tempfile.TemporaryDirectory() as tmp:
        for name in ['radar','reference-surface-grid__surface','mass-spectrum-mirror','roc','splice-tracks','H02_forest','D01_Scatter3D','D02_Volume','D03_Trajectory']:
            out=Path(tmp)/name; result=export(name,out)
            spec=json.loads((out/'example.spec.json').read_text(encoding='utf8')); make_plan(spec,out)
            if name=='radar': assert spec['parameters']['panel_specs'][0]['type']=='radar'
            if name.endswith('__surface'): assert spec['parameters']['projection']=='surface'
            assert result['analysis_performed'] is False
        try: export('T37',Path(tmp)/'history')
        except ValueError: pass
        else: raise AssertionError('Historical preview misrepresented as executable spec')
    assert find('雷达')['families'] and find('三维')['families']
    print(json.dumps(dict(state='COMPLETE_VISUAL_INDEX_PASS',**d['counts'],new_aesthetic_acceptance=False)))


if __name__=='__main__': main()
