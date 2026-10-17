"""Upgrade the same fictional study channels into compatible richer defaults.

No new fitted analysis. Marginal counts are exact display summaries of the
fictional points. Ellipse geometry is declared illustrative reference input.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
from build_transcriptomic_study_examples import prepare
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))

def build(out, seed=9031):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    prepare(out, seed=seed)
    def read(k):return pd.read_csv(out/k/(k+'.tsv'),sep='\t')
    def spec(k):return json.loads((out/k/(k+'.spec.json')).read_text(encoding='utf8'))
    def write(k,d,params,renderer='figure_integrated_views.plot_integrated_view',width=210):
        s=spec(k);raw=table_bytes(d);(out/k/(k+'.tsv')).write_bytes(raw)
        s['input'].update(sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in d if pd.api.types.is_numeric_dtype(d[c])]);s.update(renderer=renderer,parameters=params)
        s['export'].update(target_width_mm=width,minimum_text_pt=7.5);s['provenance']['source']='Fictional frozen study v0.9.1; same point/results, explicit supplied display channels; no analysis'
        if renderer=='figure_enrichment_story.plot_enrichment_story':s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        if renderer=='figure_enrichment_story.plot_enrichment_story':s['theme']['group_slots'].update({x:i for i,x in enumerate(['Immune theme','Matrix theme','Metabolic theme','RNA theme','Cellular theme'])})
        if params.get('mode') in ['annotation_atlas','single_cell_main']:s['appearance'].update(note_pt=9,tick_pt=9.5)
        (out/k/(k+'.spec.json')).write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    def bins(d,x,y,xkind,ykind,n=14):
        rows=[]
        for field,kind in [(x,xkind),(y,ykind)]:
            lo,hi=float(d[field].min()),float(d[field].max());pad=max((hi-lo)*.02,.01);edges=np.linspace(lo-pad,hi+pad,n+1)
            for group in d.group.unique():
                counts,_=np.histogram(d[d.group==group][field],edges)
                rows.extend(dict(record_type=kind,group=group,left=float(a),right=float(b),count=int(c)) for a,b,c in zip(edges[:-1],edges[1:],counts))
        return pd.DataFrame(rows)
    pca=read('BulkPCA').rename(columns={'unit_id':'object_id'}).assign(record_type='embedding')
    ell=pd.DataFrame([dict(record_type='ellipse',group=g,x=x,y=y,width=w,height=h,angle=a,coverage=.95) for g,x,y,w,h,a in [('Control',-2.2,-.05,1.7,2.35,-12),('Treated',2.25,.15,2.1,2.3,12)]])
    variance=pd.DataFrame(dict(record_type='pc_variance',component=['PC'+str(i+1) for i in range(10)],percent=[38.4,17.6,12,8,6,5,4,3.5,3,2.5]))
    pca_bins=bins(pca,'x','y','pca_x_bin','pca_y_bin',n=9)
    ellipse_definition='Supplied 95% reference ellipses; illustrative dispersion, not mean confidence or a group test'
    write('BulkPCA',pd.concat([pca,ell,pca_bins,variance],ignore_index=True),dict(mode='pca',title='Sample structure · dispersion and marginal proportions',axis_labels=['PC1 (38.4%)','PC2 (17.6%)'],ellipse_definition=ellipse_definition))
    de_bins={}
    for key in ['BulkDE','DonorDE']:
        d=read(key).assign(record_type='de');d['group']=np.where((d.padj<=.05)&(d.log2FC>=1),'Up',np.where((d.padj<=.05)&(d.log2FC<=-1),'Down','Other'));d['strength']=-np.log10(d.padj)
        b=bins(d,'log2FC','strength','de_x_bin','de_y_bin',n=24);de_bins[key]=b
        write(key,pd.concat([d,b],ignore_index=True),dict(mode='volcano',title=('Myeloid donor response' if key=='DonorDE' else 'Differential response')+' · stacked distributions',labels=spec(key)['parameters']['labels'],alpha=.05,fc=1))
    for key in ['BulkMA','DonorMA']:
        d=read(key).assign(record_type='ma');d['group']=d.status;b=bins(d,'average','effect','ma_x_bin','ma_y_bin',n=24)
        write(key,pd.concat([d,b],ignore_index=True),dict(mode='ma',title=('Myeloid donor mean–effect' if key=='DonorMA' else 'Mean–effect')+' · complete marginal counts'))
    for key,de_key in [('Pathways','BulkDE'),('DonorPathways','DonorDE')]:
        # Retain the exact supplied ORA statistics. Additional membership is
        # explicitly fictional demonstration input, never inferred biology.
        original=read(key);summary=original.rename(columns={'score':'ratio'}).assign(record_type='term',contrast='Treated versus Control',family=['Immune theme','Matrix theme','Metabolic theme','RNA theme','Cellular theme','Immune theme'])
        selected=read(de_key).query("record_type == 'de'").iloc[[8,37,90,122]].rename(columns={'log2FC':'effect'})[['gene','effect']].assign(record_type='gene')
        membership=pd.DataFrame([dict(record_type='membership',term=t,gene=g,member=int((i+j)%3==0 or i==j)) for i,t in enumerate(original.term) for j,g in enumerate(selected.gene)])
        write(key,pd.concat([summary,selected,membership],ignore_index=True),dict(mode='ora',title='Enrichment themes · ratios, FDR and selected gene support',background_definition='Fictional 200-gene query / 1200 tested genes',tested_size=1200,query_size=200,gene_effect_limits=[-4,4],gene_set_version='Illustrative frozen study sets v0.9.1',selection_definition='All six original ORA terms; four explicitly selected genes with fictional membership',support_contrast='Treated versus Control'),renderer='figure_enrichment_story.plot_enrichment_story',width=297)
    sample_map=pd.read_csv(out/'samples.tsv',sep='\t').set_index('sample_id').group.to_dict()
    for key in ['BulkQC','CellQC']:
        d=read(key);d['group']=d['sample'].map(sample_map)
        if 'metric' in d:d['metric']=d.metric.map({'genes':'Detected genes / cell','umis':'Total UMIs / cell','mitochondrial':'Mitochondrial fraction (%)'})
        else:d['metric']='Stored log2 expression'
        write(key,d,dict(mode='qc',title='Sample distributions'))
    for key in ['GeneEffects','DonorEffects']:write(key,read(key),dict(mode='effect_table',title='Prespecified effects · estimates and supplied intervals'))
    for key in ['LibrarySizes','DonorCounts']:
        old=spec(key);write(key,read(key),dict(mode='unit_profile',title='Library coverage by sample' if key=='LibrarySizes' else 'Retained cells by donor',axis_labels=[old['parameters']['y_label']]))
    correlation=read('BulkCorrelation');correlation['sample_group']=correlation['sample'].map(sample_map);correlation['feature_block']=correlation.feature.map(sample_map)
    heat=spec('BulkHeatmap')['parameters'];heat.update(value_label='Stored sample correlation r',scale_type='sequential',row_order=list(correlation.feature.unique()),column_order=list(correlation['sample'].unique()),row_annotation_label='Condition',block_palette=heat['group_palette'],merge_annotation_legends=True)
    write('BulkCorrelation',correlation,heat,renderer=spec('BulkHeatmap')['renderer'])
    write('CellBatches',read('CellBatches'),dict(mode='batch_facets',title='Batch coverage · identical embedding coordinates'))
    types=['T cells','B cells','Myeloid','Stromal','Endothelial']
    markers=['CD3D','MS4A1','LYZ','COL1A1','PECAM1','TRAC','CD79A','LST1','DCN','VWF','IL7R','CD74','FCER1G','LUM','KDR','CD2','CD37','CTSS','COL3A1','EMCN']
    dots=read('MarkerDot');old=list(dots.feature.unique());mapping=dict(zip(old,markers));dots['feature']=dots.feature.map(mapping);dots['feature_group']=dots.feature.map({g:types[i%5] for i,g in enumerate(markers)});dots['record_type']='marker_dot'
    write('MarkerDot',dots,dict(mode='marker_dot',title='Marker specificity · annotation blocks and detection fractions'))
    cells=pd.read_csv(out/'cells.tsv',sep='\t');emb=read('CellTypes').rename(columns={'cell_id':'object_id'}).assign(record_type='embedding')
    angle=np.arange(5)*2*np.pi/5
    anchors=pd.DataFrame([dict(record_type='embedding_label',group=t,label=t,x=float(np.cos(a)*3),y=float(np.sin(a)*3+.85)) for t,a in zip(types,angle)])
    # Declare every cell-marker channel first. The overview and all subgroup
    # companions then share these exact values and exact display summaries.
    # These means/fractions describe the fictional display, not a fitted model.
    feature_frames=[];summary_rows=[]
    for i,g in enumerate(markers):
        t=types[i%5];idx=np.arange(len(cells));target=(cells.celltype==t).to_numpy()
        values=np.where(target,2.1+.38*(i//5)+.95*(np.sin(idx*.41+i)+1)/2,
                        .03+.12*(np.sin(idx*.27+i)+1)/2)
        values=np.where((idx+i*3)%(7+i//5)==0,0,values)
        values=np.where((~target)&((idx+i)%4<3),0,values)
        feature_frames.append(pd.DataFrame(dict(record_type='feature_map',object_id=cells.cell_id,
            feature=g,x=cells.x,y=cells.y,value=values)))
        for comparison in types:
            v=values[(cells.celltype==comparison).to_numpy()]
            summary_rows.append(dict(record_type='marker_dot',feature=g,group=comparison,
                feature_group=t,value=float(v.mean()),fraction=float(np.mean(v>0))))
    features=pd.concat(feature_frames,ignore_index=True);dots=pd.DataFrame(summary_rows)
    write('MarkerDot',dots,dict(mode='marker_dot',title='Marker specificity · annotation blocks and detection fractions'))
    # Plausible gene labels name entirely fictional expression channels; this
    # is not a validated marker annotation or a biological result.
    atlas=pd.concat([emb,anchors,dots,features],ignore_index=True)
    atlas_page=pd.concat([emb,anchors,dots],ignore_index=True)
    annotation_params=dict(mode='atlas',title='Cell identities and marker evidence',
        expression_label='log1p normalized expression',
        detection_definition='Fraction of all displayed cells in each identity with supplied expression > 0',
        expression_limits=[0,5],group_order=types,
        marker_order=[g for t in types for g in dots[dots.feature_group==t].feature.unique()])
    write('CellTypes',atlas_page,annotation_params,renderer='figure_annotation_views.plot_annotation_evidence',width=240)
    old_features=features[features.feature.isin(markers[:5])].drop(columns='record_type').rename(columns={'object_id':'cell_id'})
    write('MarkerFeatures',old_features,dict(spec('MarkerFeatures')['parameters'],ncols='auto'),renderer=spec('MarkerFeatures')['renderer'])
    # Retained for scoped per-identity pages; atlas itself stays focused.
    (out/'all-marker-channels.tsv').write_bytes(table_bytes(features))
    comp=read('DonorComposition').rename(columns={'celltype':'category','group':'condition'}).assign(record_type='composition')
    donor_de=read('DonorDE');full=pd.concat([atlas,comp,donor_de],ignore_index=True)
    write('SingleCellMain',atlas_page,dict(annotation_params,title='Single-cell atlas · annotation evidence'),renderer='figure_annotation_views.plot_annotation_evidence',width=240)
    main=read('BulkMain');main=pd.concat([main,ell,pca_bins,de_bins['BulkDE']],ignore_index=True);params=spec('BulkMain')['parameters'];params.update(presentation='integrated',ellipse_definition=ellipse_definition)
    params.update(panel_width=5.6,panel_height=4.2)
    write('BulkMain',main,params,renderer=spec('BulkMain')['renderer'],width=297)
    (out/'presentation-upgrade.json').write_text(json.dumps(dict(version='0.9.1',analysis_performed=False,ellipse_geometry='Explicit fictional reference contours, not fitted covariance',marker_labels='Plausible names on fictional expression; not annotation validation',default_policy='Prefer compatible supplied multi-channel presentation; never infer absent channels for decoration'),indent=2)+'\n')
    print('RICH_STUDY_INPUTS_PREPARED',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
