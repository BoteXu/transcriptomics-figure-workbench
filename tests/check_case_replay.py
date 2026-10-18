"""Inspect one actually rendered fictional study; no analysis is fitted."""
import hashlib,json,sys
from pathlib import Path
def run(base):
    import pandas as pd
    import numpy as np
    from pypdf import PdfReader
    m=json.loads((base/'manifest.json').read_text(encoding='utf8'));rr={r['id']:r for r in m['records']}
    proof={r['id']:r for r in json.loads((base/'visual-review.json').read_text(encoding='utf8'))['records']}
    assert len(rr)==len(proof)==43 and len(PdfReader(base/'Bulk_and_SingleCell_FigureBook.pdf').pages)==43
    for k,r in rr.items():
        assert hashlib.sha256((base/r['assets']['png']).read_bytes()).hexdigest()==r['png_sha256']==proof[k]['png_sha256']
        assert proof[k]['notes'] and proof[k]['scientific_acceptance'] is False
        s=json.loads((base/r['assets']['spec']).read_text(encoding='utf8'))
        assert hashlib.sha256((base/r['assets']['tsv']).read_bytes()).hexdigest()==s['input']['sha256']
    def table(k):return pd.read_csv(base/rr[k]['assets']['tsv'],sep='\t',float_precision='round_trip')
    atlas=table('CellTypes');emb=atlas[atlas.record_type=='embedding'].set_index('object_id');assert len(emb)==900
    for i in range(1,6):
        d=table('Subgroup_0'+str(i));maps=d[d.record_type=='feature_map'];dots=d[d.record_type=='marker_dot']
        assert len(maps)==900*4
        for gene,q in maps.groupby('feature',sort=False):
            q=q.set_index('object_id').loc[emb.index];np.testing.assert_array_equal(q[['x','y']],emb[['x','y']])
            for group in emb.group.unique():
                values=q.loc[emb.group==group,'value'];dot=dots[(dots.feature==gene)&(dots.group==group)].iloc[0]
                np.testing.assert_allclose([dot.value,dot.fraction],[values.mean(),(values>0).mean()],rtol=0,atol=1e-14)
    for k in ['EnrichmentTracks','DonorEnrichmentTracks']:
        d=table(k);assert len(d[d.kind=='metric'])==1200
        for name,q in d[d.kind=='curve'].groupby('pathway',sort=False):
            hits=d[(d.kind=='hit')&(d.pathway==name)];delta=np.diff(np.r_[0,q.value]);miss=np.ones(1200,bool);miss[hits['rank'].astype(int)-1]=False
            assert np.all(delta[hits['rank'].astype(int)-1]>0) and np.all(delta[miss]<0) and abs(q.value.iloc[-1])<1e-12
    for k,de in [('Pathways','BulkDE'),('DonorPathways','DonorDE')]:
        d=table(de).query("record_type == 'de'");n=int(((d.padj<=.05)&(d.log2FC.abs()>=1)).sum());q=table(k).query("record_type == 'term'")
        assert (q['count']>0).all();np.testing.assert_allclose(q.ratio,q['count']/n,rtol=0,atol=1e-15)
    for k,orig in [('Subgroup_01_Custom','Subgroup_01'),('Subgroup_03_Custom','Subgroup_03'),('EnrichmentTracks_Custom','EnrichmentTracks')]:assert (base/rr[k]['assets']['tsv']).read_bytes()==(base/rr[orig]['assets']['tsv']).read_bytes()
    assert len(m['navigation']['entries'])==38 and m['forms']['navigation_entries']==21
    print(json.dumps(dict(state='FRESH_CASE_REPLAY_BINDINGS_PASS',final_figures=43,screen_reviews=43,pdf_pages=43,shared_cell_coordinates=900,marker_channels=20,complete_gsea_ranking=1200,ora_zero_overlap_exclusions_recorded=True,custom_layout_inputs_unchanged=True,scientific_acceptance=False)))
if __name__=='__main__':run(Path(sys.argv[1]))
