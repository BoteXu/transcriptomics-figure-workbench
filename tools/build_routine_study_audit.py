"""Fresh, internally bound synthetic study results for ordinary-request QA.

No RNA-seq analysis engine is run. Values, intervals and probabilities are
fictional. Arithmetic constructs exact display fixtures before rendering.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
from build_rich_study_examples import build as build_rich
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))


def build(out,seed=20261017):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    build_rich(out,seed=seed)
    def read(key):return pd.read_csv(out/key/(key+'.tsv'),sep='\t',float_precision='round_trip')
    def spec(key):return json.loads((out/key/(key+'.spec.json')).read_text(encoding='utf8'))
    def put(key,data,s):
        folder=out/key;folder.mkdir(exist_ok=True);s=copy.deepcopy(s);raw=table_bytes(data)
        (folder/(key+'.tsv')).write_bytes(raw);s['figure_id']=key
        s['input'].update(path=key+'.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in data if pd.api.types.is_numeric_dtype(data[c])])
        s['provenance'].update(source='Synthetic routine-request audit; seed '+str(seed),synthetic=True)
        (folder/(key+'.spec.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    manifests={a:json.loads((out/(a+'.manifest.json')).read_text()) for a in ['bulk','single_cell']}
    def add(assay,role,key,data,s,identity=None):
        put(key,data,s);row=dict(role=role,spec=key+'/'+key+'.spec.json')
        if identity:row['id']=identity
        manifests[assay]['results'].append(row)
    def cloud(values,bandwidth):
        values=np.asarray(values,float);grid=np.linspace(values.min(),values.max(),128)
        width=np.exp(-.5*((grid[:,None]-values[None,:])/bandwidth)**2).sum(axis=1)
        return dict(grid=grid.tolist(),width=width.tolist(),n=len(values),definition='Fictional supplied Gaussian display mixture; fixed bandwidth '+str(bandwidth)+' in displayed units; restricted to observed range; not inferential evidence')
    # The atlas already provides the sc overview; do not repeat identical art.
    manifests['single_cell']['results']=[r for r in manifests['single_cell']['results'] if r['role']!='study_overview']
    cells=pd.read_csv(out/'cells.tsv',sep='\t',float_precision='round_trip')
    samples=pd.read_csv(out/'samples.tsv',sep='\t')
    atlas=read('CellTypes');emb=atlas[atlas.record_type=='embedding'].copy()
    dots=atlas[atlas.record_type=='marker_dot'].copy()
    channels=pd.read_csv(out/'all-marker-channels.tsv',sep='\t',float_precision='round_trip')
    groups=list(spec('CellTypes')['parameters']['group_order'])
    for i,group in enumerate(groups):
        selected=list(dots[dots.feature_group==group].feature.unique())
        table=pd.concat([emb,dots[dots.feature.isin(selected)],channels[channels.feature.isin(selected)]],ignore_index=True)
        s=spec('CellTypes');s['parameters'].update(mode='subgroup',title=group+' · four-marker evidence',focus_group=group,marker_order=selected,composition='evidence')
        s['appearance'].update(label_pt=10,tick_pt=9.5,title_pt=11,note_pt=10)
        s['export'].update(target_width_mm=260)
        add('single_cell','marker_subgroup','Subgroup_'+str(i+1).zfill(2),table,s,'subgroup_'+str(i+1).zfill(2))
    def chapter(key,title,parts,panels,assay,role):
        s=spec('BulkQC');s['renderer']='figure_chapter_views.plot_transcriptomic_chapter'
        s['parameters']=dict(panels=panels,title=title,scope_note='12 fictional donors · six per condition · supplied results only',columns='auto')
        s['export'].update(target_width_mm=297,minimum_text_pt=7.5)
        s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        add(assay,role,key,pd.concat(parts,ignore_index=True),s)
    design=pd.DataFrame([dict(panel_id='design',label=r.sample_id,series=f,value=float(v)) for r in samples.itertuples() for f,v in [('Treated',r.group=='Treated'),('Batch 2',r.batch=='Batch 2'),('Batch 3',r.batch=='Batch 3')]])
    p=dict(id='design',kind='matrix',title='Declared design columns',value_label='Design indicator',limits=[0,1],show_values=True,x_label='',y_label='')
    chapter('StudyDesign','Donors, condition and batch',[design],[p],'bulk','design_map')
    add('single_cell','design_map','CellStudyDesign',design,spec('StudyDesign'))
    # Preserve the same embedding for every condition, complete donor support.
    condition=pd.concat([cells.assign(panel_id=g,label=cells.cell_id,series=cells.celltype).query('group == @g') for g in ['Control','Treated']],ignore_index=True)
    ps=[dict(id=g,kind='embedding',title=g+' · same coordinate system',x_label='Stored mock UMAP 1',y_label='Stored mock UMAP 2',series_order=groups,coordinate_limits=[float(cells.x.min()-.3),float(cells.x.max()+.3),float(cells.y.min()-.3),float(cells.y.max()+.3)]) for g in ['Control','Treated']]
    chapter('ConditionAtlas','Cell identities by condition',[condition],ps,'single_cell','condition_embedding')
    counts=read('DonorComposition');rows=[dict(panel_id='counts',label=t,series=d,value=int(counts.query('sample == @d and celltype == @t')['count'].iloc[0])) for t in groups for d in samples.donor_id]
    p=dict(id='counts',kind='matrix',title='Independent donor support for every identity',value_label='Retained cells',limits=[0,max(r['value'] for r in rows)],show_values=True,x_label='',y_label='')
    chapter('DonorTypeSupport','Cell support and donor coverage',[pd.DataFrame(rows)],[p],'single_cell','donor_cell_support')
    # Separate observed donor expression from a gene-effect interval.
    matrix=read('BulkHeatmap');selected=list(matrix.feature.unique())[:4]
    observations=matrix[matrix.feature.isin(selected)].copy()
    parts=[];ps=[]
    for i,gene in enumerate(selected):
        q=observations[observations.feature==gene].merge(samples,left_on='sample',right_on='sample_id')
        parts.append(pd.DataFrame(dict(panel_id='g'+str(i),series=q.group,x=q.group.map({'Control':0,'Treated':1}),y=q.value)))
        ps.append(dict(id='g'+str(i),kind='points',title=gene+' · raincloud',x_label='',y_label='Supplied row z-score',point_unit='one independent donor',grouped_distribution=True,series_order=['Control','Treated'],cloud_shapes={g:cloud(q.loc[q.group==g,'value'],.20) for g in ['Control','Treated']}))
    chapter('GeneExpression','Prespecified donor expression patterns',parts,ps,'bulk','gene_expression')
    # Exact toy walks are constructed BEFORE plotting from declared hit/miss
    # increments. They are synthetic frozen outputs, not computed research GSEA.
    # Ranking comes from the same fictional gene-effect list, with no new fit.
    for assay,de_key,track_key,ora_key in [('bulk','BulkDE','EnrichmentTracks','Pathways'),('single_cell','DonorDE','DonorEnrichmentTracks','DonorPathways')]:
        de=read(de_key).query("record_type == 'de'").sort_values('log2FC',ascending=False,kind='stable')
        n=len(de);ranks=np.arange(1,n+1);metric=de.log2FC.to_numpy();genes=de.gene.to_numpy()
        terms=['Interferon response','Extracellular matrix','Mitochondrial function','RNA processing','Cell cycle','Inflammatory response']
        positions=[np.linspace(2,460,96,dtype=int),np.linspace(100,760,96,dtype=int),np.linspace(n-460,n-1,96,dtype=int),np.r_[np.linspace(20,220,24,dtype=int),np.linspace(300,980,72,dtype=int)],np.r_[np.linspace(5,300,48,dtype=int),np.linspace(920,1195,48,dtype=int)],np.linspace(25,600,96,dtype=int)]
        query=set(de.loc[(de.padj<=.05)&(de.log2FC.abs()>=1),'gene']);ora=[];alltracks=[pd.DataFrame(dict(kind='metric',rank=ranks,value=metric,gene=genes))];membership=[];summaries=[]
        fdr=[.0008,.006,.002,.08,.12,.014]
        for i,(term,ix) in enumerate(zip(terms,positions)):
            ix=np.unique(ix);increments=np.full(n,-1/(n-len(ix)));weights=np.abs(metric[ix]);weights/=weights.sum();increments[ix]=weights
            walk=np.cumsum(increments);walk[-1]=0.;peak=int(np.argmax(np.abs(walk)));sign=1 if walk[peak]>0 else -1
            leading=(ix<=peak) if sign>0 else (ix>=peak);nes=sign*[1.92,1.66,1.81,1.12,1.03,1.5][i]
            summaries.append(dict(record_type='term',term=term,contrast='Treated versus Control',family='Immune theme' if i in [0,5] else 'Matrix theme' if i==1 else 'Metabolic theme' if i==2 else 'RNA theme' if i==3 else 'Cellular theme',NES=nes,padj=fdr[i],count=len(ix),ratio=len(ix)/n))
            alltracks.extend([pd.DataFrame(dict(kind='curve',pathway=term,rank=ranks,value=walk)),pd.DataFrame(dict(kind='hit',pathway=term,rank=ix+1,gene=genes[ix],leading_edge=leading.astype(int))),pd.DataFrame([dict(kind='summary',pathway=term,NES=nes,padj=fdr[i],set_size=len(ix))])])
            hitgenes=set(genes[ix]);overlap=len(hitgenes&query)
            ora.append(dict(record_type='term',term=term,contrast='Treated versus Control',family=summaries[-1]['family'],padj=[.0001,.0006,.002,.009,.02,.045][i],count=overlap,ratio=overlap/len(query)))
            for g in de.gene.iloc[[8,37,90,122]]:membership.append(dict(record_type='membership',term=term,gene=g,member=int(g in hitgenes)))
        alltracks=pd.concat(alltracks,ignore_index=True)
        s=spec(track_key);s['parameters']['options'].update(curve_order=terms[:3],line_encoding='pathway',title='GSEA · three complete ranked tracks',ncols=2,panel_width=4.4,panel_height=3.8,metric_label='Supplied log2 fold change')
        s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        s['export'].update(target_width_mm=240,minimum_text_pt=7.5)
        table=alltracks[(alltracks.kind=='metric')|alltracks.pathway.isin(terms[:3])]
        put(track_key,table,s)
        # Keep a dedicated single-pathway companion available for direct use.
        one=copy.deepcopy(s);one['parameters']['options'].update(curve_order=terms[:1],line_encoding='pathway',title='Interferon response · complete GSEA evidence')
        put(assay+'_GSEADetail',alltracks[(alltracks.kind=='metric')|alltracks.pathway.isin(terms[:1])],one)
        selected=de.iloc[[8,37,90,122]][['gene','log2FC']].rename(columns={'log2FC':'effect'}).assign(record_type='gene')
        support=pd.concat([pd.DataFrame(summaries),pd.DataFrame(membership),selected],ignore_index=True)
        s=spec(ora_key);s['parameters'].update(mode='gsea_comparison',title='GSEA pathway responses and gene support',background_definition='Complete fictional 1200-gene ranking',tested_size=n,query_size=None,support_contrast='Treated versus Control',nes_limits=[-3,3],gene_effect_limits=[-6,6])
        add(assay,'enrichment_contrasts',assay+'_GSEASummary',support,s)
        s['parameters'].update(mode='gene_support',title='ORA membership and selected gene effects',query_size=len(query))
        orasupport=pd.concat([pd.DataFrame(ora),pd.DataFrame(membership),selected],ignore_index=True)
        add(assay,'pathway_gene_support',assay+'_GeneSupport',orasupport,s)
        s=spec(ora_key);s['parameters'].update(query_size=len(query),tested_size=n,background_definition=str(len(query))+' fictional DE-query genes / 1200 tested genes',gene_effect_limits=[-6,6])
        put(ora_key,pd.concat([pd.DataFrame(ora),pd.DataFrame(membership),selected],ignore_index=True),s)
    for assay,m in manifests.items():
        m['title']='Synthetic '+assay+' routine result set / seed '+str(seed)
        (out/(assay+'.manifest.json')).write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    # The overview must reuse the revised enrichment numbers, not the earlier
    # generic fixture that happened to be copied into its mixed input table.
    main=read('BulkMain');terms=read('Pathways').query("record_type == 'term'").rename(columns={'ratio':'score'}).assign(record_type='enrichment')
    s=spec('BulkMain');s['parameters']['denominator']='1200 fictional genes; 24 prespecified matrix genes; '+str(spec('Pathways')['parameters']['query_size'])+' fictional DE-query genes; exact ORA companion values'
    put('BulkMain',pd.concat([main[main.record_type!='enrichment'],terms],ignore_index=True),s)
    for key,title in [('GeneEffects','Selected gene effects'),('DonorEffects','Myeloid donor effects')]:
        s=spec(key);s['parameters'].update(title=title,axis_labels=['Treated versus Control'+(' / Myeloid donor-level' if key=='DonorEffects' else ' / donor-level')]);put(key,read(key),s)
    for key,title in [('BulkCorrelation','Bulk sample correlation'),('BulkHeatmap','Bulk selected expression programs'),('DonorHeatmap','Myeloid donor expression programs')]:
        s=spec(key);s['parameters']['title']=title;put(key,read(key),s)
    for key in ['DonorPathways','DonorEnrichmentTracks','single_cell_GSEASummary','single_cell_GeneSupport','single_cell_GSEADetail']:
        s=spec(key);p=s['parameters'].get('options',s['parameters']);p['title']='Myeloid · '+p['title'];put(key,read(key),s)
    for key in ['BulkQC','CellQC']:
        d=read(key);s=spec(key);shapes={}
        for metric,part in d.groupby('metric',sort=False):
            bw=300 if metric.startswith('Detected') else 2000 if metric.startswith('Total UMIs') else .8 if metric.startswith('Mitochondrial') else .5
            shapes[metric]={sample:cloud(q.value,bw) for sample,q in part.groupby('sample',sort=False)}
        s['parameters'].update(cloud_shapes=shapes,title='Expression QC · raincloud distributions',observation_unit='genes' if key=='BulkQC' else 'cells')
        s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        s['export'].update(target_width_mm=240)
        put(key,d,s)
    (out/'coherence.json').write_text(json.dumps(dict(seed=seed,donors=12,cells=900,tested_genes=1200,marker_channels=20,markers_per_identity=4,identities=groups,analysis_performed=False,limits=['Synthetic frozen result construction only; no RNA-seq engine acceptance','The declared 95% PCA contours are illustrative reference dispersion, not fitted sample confidence','NES, FDR and uncertainty values are fictional inputs, not inferred probabilities','Primary single-cell donor contrast is explicitly myeloid; no other cell-type DE is implied'],checks=['Shared exact cell coordinates and expression across overview and subgroup pages','Marker means and detection match all displayed cell values','GSEA hit genes, exact walk increments and leading edge agree','ORA query and overlap ratios use the declared fictional DE query']),indent=2)+'\n')
    print(json.dumps(dict(status='ROUTINE_STUDY_FIXTURES_PREPARED',figures={a:len(m['results']) for a,m in manifests.items()},seed=seed)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=int,default=20261017);a=p.parse_args();build(a.output,a.seed)
