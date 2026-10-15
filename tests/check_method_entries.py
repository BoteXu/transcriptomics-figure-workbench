"""Fixed method routes, exact GSEA channels and invalid-result rejection."""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.methods import catalog_methods,prepare_method_spec
from figure_workbench.registry import digest


def main(gallery):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from render_frozen_table import load_table
    from figure_gsea import plot_gsea_tracks,plot_gsea_nes,plot_gsea_leading_edge,plot_ora_terms
    entries=catalog_methods();assert len(entries)==25 and len({x['id'] for x in entries})==25
    assert not any(x.get('native_package_executed') for x in entries)
    gallery=Path(gallery);inputs=gallery/'inputs';passed=[]
    for row in json.loads((gallery/'manifest.json').read_text())['records']:
        key=row['id'];spec=json.loads((inputs/(key+'.spec.json')).read_text())
        meta=json.loads((gallery/key/(key+'.json')).read_text());assert row['png_sha256']==digest(gallery/key/(key+'.png'))
        assert digest(inputs/(key+'.tsv'))==meta['workbench']['input_sha256']
        assert not meta['figure_spec']['text_geometry']['issues']
        for name,sha in meta['output_sha256'].items():assert digest(gallery/key/name)==sha
    spec=json.loads((inputs/'GSEA03.spec.json').read_text());data=load_table(inputs/'GSEA03.tsv',spec['renderer'],spec['parameters'])
    fig=plot_gsea_tracks(data,spec['theme'],**spec['parameters']);top=fig.axes[0]
    for line,pathway in zip(top.lines[:2],spec['parameters']['curve_order']):
        expected=data[(data.kind=='curve')&(data.pathway==pathway)]
        assert np.array_equal(line.get_xdata(),expected['rank']) and np.array_equal(line.get_ydata(),expected.value)
    plt.close(fig);passed.append('ES coordinates unchanged in both overlay curves')
    def reject(name,frame,params=None):
        try:plot_gsea_tracks(frame,spec['theme'],**(params or spec['parameters']))
        except (ValueError,KeyError,TypeError):passed.append(name);plt.close('all');return
        raise AssertionError('Invalid GSEA accepted: '+name)
    reject('truncated ranked metric rejected',data.drop(data[data.kind=='metric'].index[0]))
    reject('truncated curve rejected',data.drop(data[data.kind=='curve'].index[0]))
    bad=data.copy();bad.loc[bad.kind=='summary','NES']*=-1;reject('NES direction mismatch rejected',bad)
    bad=data.copy();bad.loc[bad.kind=='summary','set_size']+=1;reject('set-size mismatch rejected',bad)
    bad=data.copy();bad.loc[bad.kind=='hit','leading_edge']=2;reject('unknown leading-edge flag rejected',bad)
    bad=data.copy();bad.loc[bad.kind=='hit','rank']=999;reject('unknown hit rank rejected',bad)
    bad=data.copy();bad.loc[bad.kind=='summary','padj']=-.1;reject('negative adjusted probability rejected',bad)
    params=copy.deepcopy(spec['parameters']);params['mode']='classic';reject('classic cannot silently hide other selected pathways',data,params)
    bad=data.copy();bad.loc[bad.kind=='metric','rank']=list(reversed(bad.loc[bad.kind=='metric','rank'].tolist()));reject('reversed stored rank axis rejected',bad)
    ns=json.loads((inputs/'GSEA05.spec.json').read_text());nd=load_table(inputs/'GSEA05.tsv',ns['renderer'],ns['parameters']);nd.loc[nd.status=='not_tested','NES']=0
    try:plot_gsea_nes(nd,ns['theme'],**ns['parameters'])
    except ValueError:passed.append('untested NES cannot become zero')
    else:raise AssertionError('Invented NES accepted')
    ls=json.loads((inputs/'GSEA06.spec.json').read_text());ld=load_table(inputs/'GSEA06.tsv',ls['renderer'],ls['parameters']);ld.loc[ld.member==0,'leading_edge']=1
    try:plot_gsea_leading_edge(ld,ls['theme'],**ls['parameters'])
    except ValueError:passed.append('leading edge must be a membership subset')
    else:raise AssertionError('Invalid leading-edge membership accepted')
    os=json.loads((inputs/'ORA01.spec.json').read_text());od=load_table(inputs/'ORA01.tsv',os['renderer'],os['parameters']);od.loc[0,'count']=1000
    try:plot_ora_terms(od,os['theme'],**os['parameters'])
    except ValueError:passed.append('ORA count cannot exceed query denominator')
    else:raise AssertionError('Invalid ORA count accepted')
    try:prepare_method_spec('enrichplot.gseaplot2',spec,inputs,inputs/'never-written.json')
    except ValueError:passed.append('fixed classic method cannot be overridden to overlay')
    else:raise AssertionError('Fixed method silently overridden')
    print(json.dumps(dict(status='METHOD_ENTRIES_PASS',entries=25,actual_exports=8,checks=passed,native_packages_executed=False,scientific_acceptance=False)))


if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else ROOT/'examples/method-v030')
