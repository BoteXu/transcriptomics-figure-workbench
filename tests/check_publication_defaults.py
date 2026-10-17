"""Check new display channels and rejected corrupt scopes, never aesthetic truth."""
import copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.collections import PathCollection
    from render_frozen_table import load_table,render
    from figure_workbench.pipeline import project_appearance
    base=ROOT/'skills/transcriptomics-figure-workbench/assets/routine-gallery'
    rows=json.loads((base/'manifest.json').read_text(encoding='utf8'))['records']
    by={r['id']:r for r in rows}
    def case(k):
        p=base/by[k]['assets']['spec'];s=json.loads(p.read_text(encoding='utf8'))
        d=load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
        return s,d
    def draw(s,d):return render(s['renderer'],d,s['parameters'],project_appearance(s))[0]
    def rejected(fn):
        try:fn()
        except ValueError:return
        raise AssertionError('Corrupt display scope accepted')
    for r in rows:
        assert r['frozen_tsv_unchanged'] and len(r['before_png_sha256'])==64
        assert hashlib.sha256((base/r['before_png']).read_bytes()).hexdigest()==r['before_png_sha256']
        assert hashlib.sha256((base/r['assets']['tsv']).read_bytes()).hexdigest()==r['input_sha256']==r['before_input_sha256']
    from figure_workbench.contracts import make_plan
    layouts=base.parent/'routine-layouts'
    probes=json.loads((layouts/'manifest.json').read_text(encoding='utf8'))['records'];assert len(probes)==6
    for r in probes:
        assert hashlib.sha256((layouts/r['assets']['png']).read_bytes()).hexdigest()==r['png_sha256']
        p=layouts/r['spec'];make_plan(json.loads(p.read_text(encoding='utf8')),p.parent)
        assert r['readability']['state']=='MEASUREMENT_PASS' and r['notes'] and not r['scientific_acceptance']
    s,d=case('BulkQC');f=draw(s,d)
    points=[c for a in f.axes for c in a.collections if isinstance(c,PathCollection)]
    assert sum(len(c.get_offsets()) for c in points)==len(d)==2160
    assert len(f.axes)==2
    plt.close(f)
    bad=copy.deepcopy(s);next(iter(next(iter(bad['parameters']['cloud_shapes'].values())).values()))['n']+=1
    rejected(lambda:draw(bad,d));plt.close('all')
    s,d=case('BulkCorrelation');f=draw(s,d);arr=f.axes[0].images[0].get_array()
    assert arr.shape==(12,12) and (~np.ma.getmaskarray(arr)).sum()==66
    assert np.ma.getmaskarray(arr).diagonal().all();plt.close(f)
    bad=d.copy();bad.loc[bad.index[1],'value']+=.001
    rejected(lambda:draw(s,bad));plt.close('all')
    s,d=case('Pathways');before=d.to_csv(index=False);f=draw(s,d)
    assert before==d.to_csv(index=False)
    assert any('FDR' in a.get_xlabel() for a in f.axes)
    dots=[c for c in f.axes[0].collections if isinstance(c,PathCollection) and c.get_sizes()[0]==72]
    assert len(dots)==6 and len({tuple(c.get_facecolors()[0]) for c in dots})==6
    plt.close(f)
    s,d=case('DonorComposition');before=d.to_csv(index=False);f=draw(s,d)
    assert len(f.axes[0].patches)==60
    assert sum(len(c.get_offsets()) for a in f.axes[1:] for c in a.collections if isinstance(c,PathCollection))==60
    assert before==d.to_csv(index=False);plt.close(f)
    s,d=case('CellBatches');bad=copy.deepcopy(s);bad['parameters']['identity_by_cell'].pop(next(iter(bad['parameters']['identity_by_cell'])))
    rejected(lambda:draw(bad,d));plt.close('all')
    print(json.dumps(dict(state='PUBLICATION_DEFAULT_CHANNELS_PASS',before_after_inputs=43,unique_correlation_pairs=66,all_qc_observations=2160,composition_donor_fractions=60,invalid_cloud_and_mapping_rejected=True,aesthetic_acceptance=False)))


if __name__=='__main__':main()
