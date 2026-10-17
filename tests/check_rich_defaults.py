"""Exercise rich default selection and reject fabricated/mismatched extra channels."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'skills/transcriptomics-figure-workbench/scripts')]
def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd,numpy as np
    from build_rich_study_examples import build
    from figure_integrated_views import plot_integrated_view
    from figure_workbench.pipeline import project_appearance
    from figure_workbench.study import study_plan
    def rejected(call):
        try:call()
        except (ValueError,AssertionError):return
        raise AssertionError('Invalid supplied channel accepted')
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)/'fixtures';build(base)
        def case(k):
            s=json.loads((base/k/(k+'.spec.json')).read_text(encoding='utf8'));return s,pd.read_csv(base/k/(k+'.tsv'),sep='\t')
        for assay,number in [('bulk',11),('single_cell',14)]:
            p=study_plan(json.loads((base/(assay+'.manifest.json')).read_text()),'做一套文章组图',base)
            assert p['state']=='FIGURE_SET_PLANNED' and len(p['panels'])==number
            assert all(x['state']=='RICH_PRESENTATION_SELECTED' for x in p['presentation_decisions'] if x['role'] in ['sample_embedding','celltype_embedding','differential_expression','donor_differential','marker_dot','study_overview'])
        s,d=case('BulkPCA');f=plot_integrated_view(d,project_appearance(s),**s['parameters']);patches=[p for a in f.axes for p in a.patches if type(p).__name__=='Ellipse'];assert len(patches)==2
        assert sum(len(c.get_offsets()) for a in f.axes if a.get_xlabel().startswith('PC1') for c in a.collections)==12;plt.close(f)
        bad=d.copy();bad.loc[bad.record_type=='pca_x_bin','count']+=1
        rejected(lambda:plot_integrated_view(bad,project_appearance(s),**s['parameters']));plt.close('all')
        rejected(lambda:plot_integrated_view(d,project_appearance(s),**dict(s['parameters'],ellipse_definition=None)));plt.close('all')
        from figure_annotation_views import plot_annotation_evidence
        s,d=case('CellTypes');f=plot_annotation_evidence(d,project_appearance(s),**s['parameters']);assert f._omics_spec['all_cells_retained'] and len(f._omics_spec['marker_order'])==20;plt.close(f)
        bad=d.copy();bad=bad.drop(bad[bad.record_type=='marker_dot'].index[0])
        rejected(lambda:plot_annotation_evidence(bad,project_appearance(s),**s['parameters']));plt.close('all')
        s,d=case('BulkDE');f=plot_integrated_view(d,project_appearance(s),**s['parameters']);a=next(a for a in f.axes if a.get_xlabel()=='log2 fold change');texts=a.texts;f.canvas.draw();r=f.canvas.get_renderer();boxes=[t.get_bbox_patch().get_window_extent(r) for t in texts]
        assert all(not x.overlaps(y) for i,x in enumerate(boxes) for y in boxes[i+1:]);plt.close(f)
    print(json.dumps(dict(status='RICH_DEFAULTS_PASS',checks=['ordinary tasks select compatible evidence views','12 PCA samples and supplied ellipses retained','marginal-count mismatch and absent ellipse meaning rejected','20 marker specificity channels retained','incomplete specificity grid rejected','volcano label boxes do not overlap'],scientific_acceptance=False)))
if __name__=='__main__':main()
