"""Ordinary-request coverage and internal synthetic-display consistency."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'skills/transcriptomics-figure-workbench/scripts')]


def main():
    import numpy as np,pandas as pd
    from build_routine_study_audit import build
    from figure_workbench.study import study_plan,select_stages
    def rejected(fn):
        try:fn()
        except (ValueError,FileNotFoundError):return
        raise AssertionError('Invalid scoped request was accepted')
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)/'fixtures';build(base)
        def read(k):return pd.read_csv(base/k/(k+'.tsv'),sep='\t',float_precision='round_trip')
        m=json.loads((base/'single_cell.manifest.json').read_text())
        p=study_plan(m,'帮我把单细胞结果画成整套图',base)
        assert p['state']=='FIGURE_SET_PLANNED' and len(p['panels'])==23
        subgroup=[x for x in p['panels'] if x['role']=='marker_subgroup']
        assert len(subgroup)==5 and len({x['id'] for x in subgroup})==5
        assert len([x for x in study_plan(m,'展示各个亚群的 marker',base)['panels'] if x['role']=='marker_subgroup'])==5
        assert select_stages('bulk','画完整的图')==['overview','qc','differential','pathways']
        assert next(x for x in p['presentation_decisions'] if x['role']=='qc_distribution')['state']=='RAINCLOUD_SELECTED'
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from figure_raincloud_geometry import draw_supplied_raincloud
        s=json.loads((base/'GeneExpression/GeneExpression.spec.json').read_text())
        raw=read('GeneExpression')
        for panel in s['parameters']['panels']:
            for group,cloud in panel['cloud_shapes'].items():
                values=raw[(raw.panel_id==panel['id'])&(raw.series==group)].y.to_numpy()
                fig,ax=plt.subplots();draw_supplied_raincloud(ax,0,values,'#248C8C',cloud)
                np.testing.assert_array_equal(ax.collections[1].get_offsets()[:,1],values)
                plt.close(fig)
                invalid=copy.deepcopy(cloud);invalid['n']+=1
                fig,ax=plt.subplots();rejected(lambda:draw_supplied_raincloud(ax,0,values,'#248C8C',invalid));plt.close(fig)
                invalid=copy.deepcopy(cloud);invalid['grid'][0]-=1
                fig,ax=plt.subplots();rejected(lambda:draw_supplied_raincloud(ax,0,values,'#248C8C',invalid));plt.close(fig)
        for key,unit in [('BulkQC','genes'),('CellQC','cells')]:
            s=json.loads((base/key/(key+'.spec.json')).read_text())
            assert s['parameters']['observation_unit']==unit
            for metric,part in read(key).groupby('metric'):
                for sample,q in part.groupby('sample'):
                    assert s['parameters']['cloud_shapes'][metric][sample]['n']==len(q)
        # Older explicit box/point specifications keep their compact count
        # labels; adding a new optional unit must not silently expand them.
        from figure_integrated_views import plot_integrated_view
        s=json.loads((base/'BulkQC/BulkQC.spec.json').read_text())
        f=plot_integrated_view(read('BulkQC'),s['theme'],mode='qc',title='Legacy bounded fixture')
        assert f.axes[0].get_xticklabels()[0].get_text()=='S01\nn=180'
        plt.close(f)
        emb=read('CellTypes').query("record_type == 'embedding'").set_index('object_id')
        for i in range(1,6):
            table=read('Subgroup_'+str(i).zfill(2));dots=table.query("record_type == 'marker_dot'")
            maps=table.query("record_type == 'feature_map'")
            assert len(maps)==900*4
            for gene,q in maps.groupby('feature',sort=False):
                q=q.set_index('object_id').loc[emb.index]
                np.testing.assert_array_equal(q[['x','y']],emb[['x','y']])
                for group in emb.group.unique():
                    values=q.loc[emb.group==group,'value'];s=dots[(dots.feature==gene)&(dots.group==group)].iloc[0]
                    np.testing.assert_allclose([s.value,s.fraction],[values.mean(),(values>0).mean()],rtol=0,atol=1e-14)
        for key in ['EnrichmentTracks','DonorEnrichmentTracks']:
            d=read(key);assert len(d[d.kind=='metric'])==1200
            for name,q in d[d.kind=='curve'].groupby('pathway',sort=False):
                hits=d[(d.kind=='hit')&(d.pathway==name)];delta=np.diff(np.r_[0,q.value])
                assert np.all(delta[hits['rank'].astype(int)-1]>0)
                miss=np.ones(1200,bool);miss[hits['rank'].astype(int)-1]=False
                assert np.all(delta[miss]<0) and abs(q.value.iloc[-1])<1e-12
                peak=int(q.iloc[q.value.abs().argmax()]['rank']);positive=q.value.abs().max()==q.value.max()
                expected=hits['rank']<=peak if positive else hits['rank']>=peak
                np.testing.assert_array_equal(hits.leading_edge,expected.astype(int))
        for key,de in [('Pathways','BulkDE'),('DonorPathways','DonorDE')]:
            d=read(de).query("record_type == 'de'");query=int(((d.padj<=.05)&(d.log2FC.abs()>=1)).sum())
            t=read(key).query("record_type == 'term'");np.testing.assert_allclose(t.ratio,t['count']/query,rtol=0,atol=1e-15)
        for mutation in ['duplicate_focus','unsafe_id','wrong_contract']:
            bad=copy.deepcopy(m);row=copy.deepcopy(next(x for x in bad['results'] if x['role']=='marker_subgroup'))
            if mutation=='unsafe_id':row['id']='../escape'
            elif mutation=='wrong_contract':row.update(id='bad_contract',spec='BulkDE/BulkDE.spec.json')
            else:row['id']='same_focus'
            bad['results'].append(row);rejected(lambda:study_plan(bad,'整套图',base))
    print(json.dumps(dict(state='ROUTINE_STUDY_CONTRACT_PASS',checks=['ordinary whole-set requests','five scoped multi-marker defaults','20 exact shared marker channels','GSEA hit, walk and leading-edge consistency','ORA denominator consistency','raincloud raw observations and scope validation','explicit QC count units','unsafe and duplicate scope rejected'],scientific_acceptance=False)))


if __name__=='__main__':main()
