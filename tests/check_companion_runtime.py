"""Reject semantic mistakes and exercise actual complete custom compositions."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from figure_workbench.contracts import read_json
    from figure_workbench.pipeline import project_appearance
    from figure_analysis_evidence import plot_analysis_evidence,KINDS
    from render_frozen_table import load_table,render
    base=SKILL/'assets/companion-gallery';manifest=base/'manifest.json'
    assert manifest.stat().st_size <= 8*1024*1024
    rows=json.loads(manifest.read_text(encoding='utf8'))['records'];lookup={r['id']:r for r in rows}
    assert set(KINDS)-{'embedding'}=={p['kind'] for r in rows for p in r['parameters']['panels']}
    def get(key):
        p=base/lookup[key]['assets']['spec'];s=read_json(p);return s,load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
    def bad(s,d,p=None):
        try:plot_analysis_evidence(d,project_appearance(s),**(p or s['parameters']))
        except ValueError:return
        finally:plt.close('all')
        raise AssertionError('Invalid display accepted')
    s,d=get('B_design_05');x=d.copy();x.loc[x.index[0],'n']=999;bad(s,x)
    x=d.copy();x.loc[x.index[0],'upper']=-9;bad(s,x)
    p=copy.deepcopy(s['parameters']);p['columns']=True;bad(s,d,p)
    p=copy.deepcopy(s['parameters']);p['context']['independent_n']=True;bad(s,d,p)
    s,d=get('B_design_04');x=d.copy();x['value']=x['value'].astype(float);x.loc[x.index[0],'value']=.5;bad(s,x)
    s,d=get('B_reads_04');x=d.copy();x.loc[x.index[0],'y']+=.1;bad(s,x)
    s,d=get('B_reads_03');x=d.copy();x.loc[x.index[1],'start']+=.1;bad(s,x)
    s,d=get('B_normalization_03');p=copy.deepcopy(s['parameters']);p['panels'][0]['cloud_shapes']={};bad(s,d,p)
    x=d.copy();groups=list(x.series.unique());x.loc[x.series==groups[1],'unit']=x.loc[x.series==groups[0],'unit'].to_numpy();bad(s,x)
    s,d=get('B_normalization_02');bad(s,d.iloc[:-1])
    s,d=get('B_splicing_01');p=copy.deepcopy(s['parameters']);p['panels'][0].pop('contig');bad(s,d,p)
    s,d=get('B_survival_04');x=d.copy();x.loc[x.index[0],'lower']=-1;bad(s,x)
    s,d=get('B_survival_02');x=d.copy();x.loc[x.index[1],'y']=1.1;bad(s,x)
    s,d=get('S_resolution_04');x=d.copy();x.loc[x.index[0],'upper']=1.1;bad(s,x)
    s,d=get('B_design_01');x=d.copy();x.loc[x.index[0],'value']+=.1;bad(s,x)
    s,d=get('B_differential_Evidence');p=copy.deepcopy(s['parameters']);p.update(rows=1,columns=1);bad(s,d,p)
    for key in ['B_differential_Evidence','B_differential_Layout','B_differential_ThreeColumns','S_communication_Evidence','S_multiome_Layout']:
        s,d=get(key);original=d.copy(deep=True);fig,audit=render(s['renderer'],d,s['parameters'],project_appearance(s));fig.canvas.draw()
        assert not audit['issues'] and d.equals(original)
        effects=[a for a in fig.axes if getattr(a,'_analysis_effect_table',False)]
        assert effects and len(fig.axes)>=len(s['parameters']['panels'])+len(effects)
        plt.close(fig)
    print(json.dumps(dict(state='ANALYSIS_COMPANION_RUNTIME_PASS',rejections=16,complete_compositions=5,source_unchanged=True,scientific_acceptance=False)))

if __name__=='__main__':main()
