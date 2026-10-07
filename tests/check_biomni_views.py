"""Independent scientific-channel checks for five frozen-result renderers."""
from pathlib import Path
import sys,json,copy,tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from biomni_view_fixture import biomni_view_cases
from render_frozen_table import render,load_table
from figure_design import geometry_signature
from figure_layout import apply_page_layout
from project_theme import create_theme


def main():
    theme=json.loads((ROOT/'examples/gallery/project_theme.json').read_text(encoding='utf8'));theme['font_family']='DejaVu Sans';cases=biomni_view_cases();negative=0
    for id_,c in cases.items():
        original=c['data'].copy(deep=True);f=c['function'](c['data'],theme,**c['params']);f.canvas.draw()
        pd.testing.assert_frame_equal(c['data'],original);sig=geometry_signature(f)
        if id_=='E38':
            ax=f.axes[0]
            for p in ax.patches:
                if not str(p.get_gid()).startswith('logo:'):continue
                _,position,symbol=p.get_gid().split(':');height=c['data'].query('position_id == @position and symbol == @symbol').height.iloc[0]
                vertices=ax.transData.inverted().transform(p.get_transform().transform(p.get_path().vertices))
                assert np.isclose(np.ptp(vertices[:,1]),height)
        if id_=='E39':
            expected=c['data'].loc[c['data'].record_type=='contact','value'].to_numpy()
            array=f.axes[0].collections[0].get_array();assert np.allclose(array.filled(np.nan),expected,equal_nan=True)
            for track in [a for a in f.axes[1:] if not hasattr(a,'_colorbar')]:
                assert track.get_xlim()==f.axes[0].get_xlim()
                assert np.allclose([track.bbox.x0,track.bbox.x1],[f.axes[0].bbox.x0,f.axes[0].bbox.x1])
        if id_=='E40':
            for line in f.axes[0].lines:
                if str(line.get_gid()).startswith('branch:'):
                    node=line.get_gid().split(':')[1];value=c['data'].set_index('node_id').loc[node,'branch_length']
                    assert np.isclose(np.ptp(line.get_xdata()),value)
        if id_=='E41':
            for ax,view in zip(f.axes,c['params']['view_order']):
                expected=c['data'][c['data'].view==view].pivot(index='v',columns='u',values='intensity').to_numpy()
                assert np.array_equal(ax.images[0].get_array(),expected)
        if id_=='E42':
            d=c['data'];fixed=d.pivot(index='v',columns='u',values='fixed').to_numpy();reg=d.pivot(index='v',columns='u',values='registered').to_numpy()
            yy,xx=np.indices(fixed.shape);n=c['params']['tile_pixels']
            assert np.array_equal(f.axes[2].images[0].get_array(),np.where((xx//n+yy//n)%2,fixed,reg))
            assert np.array_equal(f.axes[3].images[0].get_array(),reg-fixed)
        apply_page_layout(f,'portrait');assert geometry_signature(f)==sig;plt.close(f)
        # Logo outline shape belongs to typography; its quantitative heights
        # remain covered by the independent glyph oracle above.
        alternate=create_theme(theme['project_id'],'card_07',theme['group_slots'],font_family='DejaVu Sans' if id_=='E38' else 'DejaVu Serif')
        fig=c['function'](c['data'],alternate,**c['params']);fig.canvas.draw()
        assert geometry_signature(fig)==sig,id_+' theme changed quantitative geometry';plt.close(fig)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'result.tsv';original.to_csv(p,sep='\t',index=False)
            replay=load_table(p,c['adapter'],c['params']);fig,audit=render(c['adapter'],replay,c['params'],theme);plt.close(fig)
        if id_ in ('E41','E42'):
            for direction in ('horizontal','vertical'):
                p=dict(c['params'],arrangement=direction);fig=c['function'](c['data'],theme,**p);plt.close(fig)
    def reject(id_,change_data=None,change_params=None):
        nonlocal negative
        c=cases[id_];d=c['data'].copy(deep=True);p=copy.deepcopy(c['params'])
        if change_data:d=change_data(d)
        if change_params:p.update(change_params)
        try:f=c['function'](d,theme,**p)
        except (ValueError,TypeError):negative+=1;return
        plt.close(f);raise AssertionError('Invalid result accepted: '+id_)
    reject('E38',lambda d:d.iloc[1:]);reject('E38',lambda d:d.assign(height=-1));reject('E38',change_params={'position_order':['bad']})
    reject('E39',lambda d:d.iloc[:-1]);reject('E39',lambda d:d[d.bin_j!='B15']);reject('E39',change_params={'value_limits':[0,.2]})
    reject('E40',lambda d:d.assign(branch_length=-1));reject('E40',change_params={'leaf_order':list('ACBDE')});reject('E40',change_params={'root_id':'bad'})
    reject('E41',lambda d:d.iloc[1:]);reject('E41',change_params={'label_slots':{}});reject('E41',change_params={'orientation_definition':''})
    reject('E42',lambda d:d.iloc[1:]);reject('E42',change_params={'tile_pixels':0});reject('E42',change_params={'difference_limits':[0,1]})
    print(json.dumps(dict(status='BIOMNI_VIEW_RENDERING_PASS',renderers=len(cases),negative_checks=negative,theme_replacement_checks=5,independent_channel_oracles=5,analysis_engines_executed=False)))

if __name__=='__main__':main()
