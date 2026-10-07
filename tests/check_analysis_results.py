"""Independent quantitative-channel and rejection checks for added result views."""
from pathlib import Path
import sys,json,copy,tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from analysis_result_fixture import analysis_result_cases
from render_frozen_table import render,load_table
from figure_layout import apply_page_layout
from figure_design import geometry_signature
from project_theme import create_theme


def main():
    theme=json.loads((ROOT/'examples/gallery/project_theme.json').read_text(encoding='utf8'));theme['font_family']='DejaVu Sans';cases=analysis_result_cases();negative=0
    for id_,c in cases.items():
        before=c['data'].copy(deep=True);f,audit=render(c['adapter'],c['data'],c['params'],theme);f.canvas.draw()
        pd.testing.assert_frame_equal(before,c['data']);signature=geometry_signature(f)
        if id_=='E43':
            found=0
            for ax in f.axes:
                for p in ax.patches:
                    if str(p.get_gid()).startswith('junction:'):
                        _,s,a,b=p.get_gid().split(':');q=before[(before.sample_id==s)&(before.start==float(a))&(before.end==float(b))&(before.record_type=='junction')]
                        assert np.isclose(p.get_linewidth(),q['count'].iloc[0]*.045);found+=1
            assert found==int((before.loc[before.record_type=='junction','count']>0).sum())
            assert len(f._omics_spec['zero_junctions'])==2
            assert all(np.allclose(ax.get_xlim(),c['params']['region']) for ax in f.axes)
        if id_=='E44':
            for ax,s in zip(f.axes,c['params']['signal_order']):
                q=before[before.signal==s];segments=ax.collections[0].get_segments()
                assert np.allclose([a[1,1] for a in segments],q.pip)
                assert np.allclose([a[1,0] for a in segments],q.position)
                assert sum(len(a.get_offsets()) for a in ax.collections[1:])==len(q)
        if id_=='E45':
            heights=[line.get_ydata()[1] for line in f.axes[1].lines]
            assert np.array_equal(heights,before.n)
        if id_ in ('E46','E50'):
            for line,s in zip(f.axes[0].lines,list(before.series.unique())):
                assert np.allclose(line.get_xdata(),before[before.series==s].time)
                assert np.allclose(line.get_ydata(),before[before.series==s].estimate)
        if id_ in ('E47','E48','E49'):
            q=f._omics_spec;ro=q['row_order'];co=q['column_order']
            expected=before.pivot(index='feature',columns='sample',values='value').loc[ro,co].to_numpy()
            assert np.array_equal(f.axes[0].images[0].get_array(),expected)
            if id_=='E47':assert sum(t.get_text()==c['params']['title'] for t in f.findobj(__import__('matplotlib').text.Text))==1
        if id_=='E51':
            expected=np.r_[0,np.cumsum(before.contribution)]
            assert np.allclose([v['end'] for v in f._omics_spec['levels']],expected[1:])
            patches=f.axes[0].patches[1:-1]
            assert np.allclose([p.get_height() for p in patches],abs(before.contribution))
            assert np.allclose([p.get_y() for p in patches],np.minimum(expected[:-1],expected[1:]))
        apply_page_layout(f,'portrait');assert geometry_signature(f)==signature;plt.close(f)
        alternate=create_theme(theme['project_id'],'card_07',theme['group_slots'],font_family='DejaVu Serif')
        f,_=render(c['adapter'],c['data'],c['params'],alternate);f.canvas.draw()
        assert geometry_signature(f)==signature,id_+' theme changed quantitative geometry';plt.close(f)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.tsv';before.to_csv(path,sep='\t',index=False)
            replay=load_table(path,c['adapter'],c['params']);f,_=render(c['adapter'],replay,c['params'],theme);plt.close(f)
        print(id_+' independent data-channel and TSV replay PASS',flush=True)
    def reject(id_,change_data=None,change_params=None):
        nonlocal negative
        c=cases[id_];data=c['data'].copy(deep=True);params=copy.deepcopy(c['params'])
        if change_data:data=change_data(data)
        if change_params:params.update(change_params)
        try:f,_=render(c['adapter'],data,params,theme)
        except (ValueError,TypeError):negative+=1;return
        plt.close(f);raise AssertionError('Invalid frozen result accepted: '+id_)
    reject('E43',lambda d:d.assign(start=901));reject('E43',lambda d:d.assign(count=-1));reject('E43',change_params={'coordinate_definition':''})
    reject('E44',lambda d:d.assign(pip=1.1));reject('E44',lambda d:d.iloc[1:]);reject('E44',change_params={'label_ids':['unknown']})
    reject('E45',lambda d:d.assign(n=0));reject('E45',lambda d:d.assign(lower=.99))
    reject('E46',lambda d:pd.concat([d,d.iloc[:1]],ignore_index=True));reject('E50',change_params={'unit_label':''})
    reject('E47',lambda d:d.iloc[1:]);reject('E48',change_params={'row_order':['missing']})
    reject('E49',lambda d:pd.concat([d,d.iloc[:1]],ignore_index=True))
    reject('E51',change_params={'total':.7});reject('E51',change_params={'component_order':['bad']})
    # More than old example-specific model/series limits now retains all input.
    for id_,field,n in [('E45','model',5),('E50','series',7)]:
        c=cases[id_];source=c['data'][c['data'][field]=='G1'];d=pd.concat([source.assign(**{field:f'G{i+1}'}) for i in range(n)],ignore_index=True)
        p=copy.deepcopy(c['params']);p['palette']={f'G{i+1}':None for i in range(n)};f,_=render(c['adapter'],d,p,theme);plt.close(f)
    print(json.dumps(dict(status='ANALYSIS_RESULT_VIEWS_PASS',modes=len(cases),independent_channel_checks=9,theme_replacement_checks=9,negative_checks=negative,expanded_cardinality_checks=2,analysis_engines_executed=False)))

if __name__=='__main__':main()
