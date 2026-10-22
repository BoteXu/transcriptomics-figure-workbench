"""Scientific channel and frozen-input checks for the new compositions (CI)."""
import copy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))


def main(output):
    import matplotlib.pyplot as plt
    from render_frozen_table import load_table,render
    from figure_workbench.pipeline import project_appearance
    out=Path(output);manifest=json.loads((out/'manifest.json').read_text('utf8'))
    assert len(manifest['records'])==28 and not manifest['analysis_performed']
    for r in manifest['records']:
        f=out/r['id'];spec=json.loads((f/'figure.spec.json').read_text('utf8'));bundle=f/'export'/r['id'];receipt=json.loads((bundle/(r['id']+'.json')).read_text('utf8'))
        assert r['rendered'] and r['screen_review']=='UNREVIEWED'
        assert hashlib.sha256((f/'input.tsv').read_bytes()).hexdigest()==r['input_sha256']==spec['input']['sha256']
        assert (f/'input.tsv').read_bytes()==(bundle/(r['id']+'.tsv')).read_bytes()
        assert receipt['workbench']['input_sha256']==r['input_sha256']
        assert not receipt['workbench']['scientific_acceptance'] and not receipt['workbench']['visual_acceptance']
        assert receipt['workbench']['print_readability']['state']=='MEASUREMENT_PASS',r['id']+' font-size measurement failed'
    # Missing or inconsistent scientific channels must be rejected rather than
    # prettified with invented density, uncertainty, expression or curve tracks.
    def rejects(name,mutate):
        path=out/name;spec=json.loads((path/'figure.spec.json').read_text('utf8'))
        data=load_table(path/'input.tsv',spec['renderer'],spec['parameters'],spec['input']['numeric_columns']);before=data.to_csv(index=False)
        altered,params=mutate(data.copy(deep=True),copy.deepcopy(spec['parameters']))
        try:
            fig,_=render(spec['renderer'],altered,params,project_appearance(spec));plt.close(fig)
        except ValueError:pass
        else:raise AssertionError('Missing channel incorrectly accepted: '+name)
        finally:plt.close('all')
        assert data.to_csv(index=False)==before
    rejects('PCA_evidence',lambda d,p:(d[d.record_type!='ellipse'],p))
    rejects('PCA_evidence',lambda d,p:(d,{**p,'ncols':2}))
    rejects('Volcano_evidence',lambda d,p:(d[d.record_type!='de_x_bin'],p))
    rejects('GSEA_cards',lambda d,p:(d[d.kind!='metric'],p))
    rejects('GSEA_aligned',lambda d,p:(d,{**p,'ncols':2}))
    def missing_cloud(d,p):
        p['panels'][0]['cloud_shapes'].pop(next(iter(p['panels'][0]['cloud_shapes'])));return d,p
    rejects('Expression_raincloud_horizontal',missing_cloud)
    rejects('Subgroup_01_paired_cards',lambda d,p:(d[~((d.record_type=='feature_map')&(d.feature==p['marker_order'][0]))],p))
    # Reproduce observed collisions at real rendered font/physical sizes.
    for name in ['PCA_facets','PCA_one_column','GSEA_single','GSEA_cards','Expression_raincloud_horizontal']:
        f=out/name;spec=json.loads((f/'figure.spec.json').read_text('utf8'))
        d=load_table(f/'input.tsv',spec['renderer'],spec['parameters'],spec['input']['numeric_columns'])
        fig,_=render(spec['renderer'],d,spec['parameters'],project_appearance(spec));fig.canvas.draw();renderer=fig.canvas.get_renderer()
        for legend in fig.legends:
            box=legend.get_window_extent(renderer)
            assert all(not box.overlaps(a.title.get_window_extent(renderer)) for a in fig.axes if a.title.get_text()),name+' legend/title collision'
        if name=='Expression_raincloud_horizontal':
            for a in fig.axes:
                for text in a.get_yticklabels():
                    box=text.get_window_extent(renderer)
                    assert all(not box.overlaps(b.get_window_extent(renderer)) for b in fig.axes if b is not a),name+' labels invade another panel'
        if name.startswith('GSEA'):
            for text in fig.texts:
                if text.get_text().startswith('Leading hits:'):
                    assert all(not text.get_window_extent(renderer).overlaps(a.get_window_extent(renderer)) for a in fig.axes),name+' leading-edge text invades track'
        plt.close(fig)
    print('28 exact bindings/native font measurements, 7 channel/layout rejections and 5 measured collision regressions passed; visual/scientific acceptance remains separate')


if __name__=='__main__':main(sys.argv[1])
