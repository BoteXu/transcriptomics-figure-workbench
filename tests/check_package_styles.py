"""Actual package exports, exact frozen channels and malformed-result rejection."""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))


def main(folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from PIL import Image
    from pypdf import PdfReader
    from figure_package_styles import plot_package_style
    from figure_workbench.methods import catalog_methods,prepare_method_spec
    from figure_workbench.registry import digest
    from render_frozen_table import load_table
    folder=Path(folder);manifest=json.loads((folder/'manifest.json').read_text());entries=catalog_methods();records=manifest['records'];checks=[]
    assert len(records)==25 and {r['entry'] for r in records}=={e['id'] for e in entries}
    assert not manifest['scientific_acceptance'] and not manifest['native_packages_executed']
    for r in records:
        k=r['id'];base=folder/k;spec=json.loads((folder/'inputs'/(k+'.spec.json')).read_text());meta=json.loads((base/(k+'.json')).read_text())
        assert spec['parameters']['view']==next(e for e in entries if e['id']==r['entry'])['publication_view']
        assert r['source_sha256']==digest(folder/'inputs'/(k+'.tsv'))==meta['workbench']['input_sha256']
        assert r['png_sha256']==digest(base/(k+'.png'))
        assert not meta['figure_spec']['text_geometry']['issues']
        for filename,sha in meta['output_sha256'].items():assert digest(base/filename)==sha
        with Image.open(base/(k+'.png')) as im:assert im.width>1200 and im.height>900 and abs(im.info['dpi'][0]-300)<1
        assert len(PdfReader(base/(k+'.pdf')).pages)==1
        left=load_table(folder/'inputs'/(k+'.tsv'),'package_style',spec['parameters']);right=load_table(base/(k+'.tsv'),'package_style',spec['parameters'])
        pd.testing.assert_frame_equal(left,right,check_dtype=False,atol=1e-12,rtol=1e-12)
    checks.append('all 25 actual bundles: exact source/export cells, PNG resolution, single-page PDF and output hashes')
    def sample(n):
        k='PKG'+str(n).zfill(2);s=json.loads((folder/'inputs'/(k+'.spec.json')).read_text());d=load_table(folder/'inputs'/(k+'.tsv'),'package_style',s['parameters']);return d,s
    def draw(d,s):return plot_package_style(d,s['theme'],**s['parameters'])
    def reject(label,n,mutate):
        d,s=sample(n);d,s=mutate(d,copy.deepcopy(s))
        try:draw(d,s)
        except (ValueError,TypeError,KeyError):checks.append(label);plt.close('all');return
        raise AssertionError('Invalid display accepted: '+label)
    d,s=sample(2);fig=draw(d,s)
    for line,name in zip(fig.axes[0].lines[::2],s['parameters']['options']['curve_order']):
        q=d[(d.kind=='curve')&(d.pathway==name)];assert np.array_equal(line.get_xdata(),q['rank']) and np.array_equal(line.get_ydata(),q.value)
    plt.close(fig);checks.append('GSEA ES coordinates preserved; NES remains a separate summary')
    d,s=sample(16);fig=draw(d,s);fractions=d.pivot(index='feature',columns='group',values='fraction').loc[s['parameters']['options']['row_order'],s['parameters']['options']['column_order']].to_numpy().ravel();assert np.allclose([x.get_sizes()[0] for x in fig.axes[0].collections],140*fractions);plt.close(fig);checks.append('marker dot areas encode supplied fractions')
    d,s=sample(17);fig=draw(d,s)
    for collection,name in zip(fig.axes[0].collections,d.group.unique()):assert np.array_equal(collection.get_offsets(),d[d.group==name][['x','y']])
    plt.close(fig);checks.append('all 800 stored embedding coordinates preserved')
    d,s=sample(24);fig=draw(d,s)
    for line,name in zip(fig.axes[0].lines,d[d.kind=='step'].group.unique()):
        q=d[(d.kind=='step')&(d.group==name)];assert np.array_equal(line.get_xdata(),q.time) and np.array_equal(line.get_ydata(),q.survival)
    assert np.array_equal(fig.axes[0].get_xticks(),fig.axes[-1].get_xticks());plt.close(fig);checks.append('survival steps and risk time axes aligned exactly')
    reject('incomplete GSEA ranking blocked',2,lambda d,s:(d.drop(d[d.kind=='metric'].index[0]),s))
    reject('untested NES cannot become zero',5,lambda d,s:(d.assign(NES=d.NES.mask(d.status=='not_tested',0)),s))
    reject('nonmember cannot be leading edge',6,lambda d,s:(d.assign(leading_edge=d.leading_edge.mask(d.member==0,1)),s))
    reject('ORA count cannot exceed denominator',7,lambda d,s:(d.assign(count=999),s))
    reject('density grid cannot be truncated',9,lambda d,s:(d.drop(index=0),s))
    reject('matrix missing cell cannot become zero',12,lambda d,s:(d.drop(index=0),s))
    reject('zero adjusted probability blocked',13,lambda d,s:(d.assign(padj=0),s))
    reject('inverted effect interval blocked',14,lambda d,s:(d.assign(lower=d.upper+1),s))
    reject('invalid cell fraction blocked',16,lambda d,s:(d.assign(fraction=1.1),s))
    reject('duplicated cell identity blocked',17,lambda d,s:(d.assign(cell_id='duplicate'),s))
    reject('unknown network endpoint blocked',20,lambda d,s:(d.assign(source=d.source.mask(d.kind=='edge','absent')),s))
    def arrow(d,s):s['parameters']['options']['directed']=True;return d,s
    reject('correlation cannot acquire arrows',20,arrow)
    reject('censor point must lie on stored curve',24,lambda d,s:(d.assign(survival=d.survival.mask(d.kind=='censor',.5)),s))
    reject('risk counts cannot increase',24,lambda d,s:(d.assign(at_risk=d.at_risk.mask((d.kind=='risk')&(d.time==4),999)),s))
    reject('reversed ROC coordinates blocked',25,lambda d,s:(d.iloc[::-1],s))
    def unknown(d,s):s['parameters']['options']['refit_model']=True;return d,s
    reject('unknown drawing options blocked',13,unknown)
    d,s=sample(2)
    try:prepare_method_spec('enrichplot.gseaplot2',s,folder/'inputs',folder/'inputs/never.json')
    except ValueError:checks.append('method arrangement cannot be overridden')
    else:raise AssertionError('Fixed method changed')
    if (folder/'self-review.json').is_file():
        review=json.loads((folder/'self-review.json').read_text());assert len(review['records'])==25
        for r in review['records']:assert r['png_sha256']==digest(folder/r['id']/(r['id']+'.png')) and r['status']=='SELF_REVIEWED'
        checks.append('individual visual review is bound to every exact final PNG')
    print(json.dumps(dict(status='PACKAGE_STYLES_PASS',examples=25,display_grammars=14,checks=checks,native_packages_executed=False,scientific_acceptance=False)))


if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'examples/package-v040')
