"""Create coherent fictional frozen result packages, not an RNA-seq analysis.

All numerical channels below are declared illustrative inputs. No statistical
model, clustering, dimensional reduction or enrichment algorithm is run.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys
from full_layout_cases import ROOT,SKILL,cases
sys.path.insert(0,str(SKILL/'scripts'))


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def prepare(out, seed=9031):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    from project_theme import create_theme
    out.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(seed)
    donor_names=['Donor '+str(i+1).zfill(2) for i in range(12)]
    sample_names=['S'+str(i+1).zfill(2) for i in range(12)]
    groups=['Control','Treated'];types=['T cells','B cells','Myeloid','Stromal','Endothelial']
    batches=['Batch 1','Batch 2','Batch 3'];pathways=['Interferon response','Extracellular matrix','Mitochondrial function','RNA processing','Cell cycle','Inflammatory response']
    slots={g:i for i,g in enumerate(groups)};slots.update({g:i for i,g in enumerate(types)});slots.update({g:i for i,g in enumerate(batches)});slots.update({g:i for i,g in enumerate(pathways)})
    theme=create_theme('synthetic-transcriptomic-study','package_editorial',slots,font_family='DejaVu Sans',roles={'positive':'#D8795B','negative':'#4477AA'})
    theme['continuous']['sequential']=['#DFE7EA','#326B8D'];theme['continuous']['diverging']=['#4477AA','#F7F7F7','#D8795B']
    pal={g:theme['palette_colors'][slots[g]] for g in groups}
    samples=pd.DataFrame(dict(sample_id=sample_names,donor_id=donor_names,group=[groups[i//6] for i in range(12)],batch=[batches[i%3] for i in range(12)]))
    (out/'samples.tsv').write_bytes(table_bytes(samples))
    source_cases={r['form']:r for r in cases() if r['route']=='native'}
    all_specs={};metadata={}
    def add(key,data,adapter,params,unit,denominator,layout=None):
        folder=out/key;folder.mkdir();raw=table_bytes(data);table=folder/(key+'.tsv');table.write_bytes(raw)
        numeric=[c for c in data if pd.api.types.is_numeric_dtype(data[c])]
        params=copy.deepcopy(params)
        spec=dict(schema_version=1,figure_id=key,renderer=adapter,input=dict(path=key+'.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=numeric),parameters=params,theme=copy.deepcopy(theme),
            provenance=dict(source='Fictional frozen study fixture v0.9; illustrative numbers, not an analysis result',input_unit=unit,
                experimental_unit='Synthetic donor; cells nested within donors',contrast='Treated versus Control; purely illustrative',denominator=denominator,
                model='No statistical model fitted; every estimate and uncertainty channel is an illustrative frozen input',
                limits='Declared complete display scope; data have no biomedical validity',filtering='Declared fixture selection only; no research filtering',
                uncertainty='Only explicitly supplied illustrative intervals; no new uncertainty estimation',interpretation_limit='Software and visual acceptance only; no biological or clinical conclusions',synthetic=True),
            appearance=dict(preset='paper'),export=dict(raster_dpi=300,target_width_mm=210,minimum_text_pt=7,readability_policy='block'))
        if layout:spec['layout']=layout
        write(folder/(key+'.spec.json'),spec);all_specs[key]=key+'/'+key+'.spec.json';metadata[key]=dict(rows=len(data),unit=unit,denominator=denominator)
    qc=pd.DataFrame([dict(cell_id='Feature '+str(k+1),sample=s,value=float(v)) for i,s in enumerate(sample_names) for k,v in enumerate(rng.lognormal(1.7+i*.012,.35,180))])
    add('BulkQC',qc,'figure_core.plot_qc',dict(y_label='Stored log2 expression'),'Synthetic gene-sample measurement','All 180 illustrative genes in each of 12 samples')
    pca=pd.DataFrame(dict(unit_id=sample_names,group=samples.group,x=[-2.8,-2.1,-2.5,-1.9,-2.4,-1.6,1.5,2.0,2.6,2.1,3.0,2.3],y=[-.5,.8,.1,-1,.5,-.2,.4,-.7,.2,1.,-.4,.6]))
    add('BulkPCA',pca,'xy_points',dict(palette=pal,x_label='Stored PC1 (38.4%)',y_label='Stored PC2 (17.6%)',unit_label='Synthetic donor',label_points=True),'Synthetic donor','One stored PCA coordinate per synthetic donor')
    corr=pd.DataFrame([dict(feature=a,sample=b,value=1. if i==j else (.76 if i//6==j//6 else .39)+.035*np.cos(i+j)) for i,a in enumerate(sample_names) for j,b in enumerate(sample_names)])
    add('BulkCorrelation',corr,'figure_core.plot_heatmap',dict(value_label='Stored sample correlation r',scale_type='sequential',center=0),'Synthetic sample pair','Complete 12 by 12 illustrative correlation matrix; no correlation calculated')
    library=pd.DataFrame(dict(sample_id=sample_names,group=samples.group,value=[28,32,26,35,31,29,33,30,37,29,34,32]))
    add('LibrarySizes',library,'figure_core.plot_samples',dict(palette=pal,y_label='Stored assigned reads (million)'),'Synthetic donor','One supplied library size for each of 12 biological donors')
    n=1200;genes=['G'+str(i+1).zfill(4) for i in range(n)];idx=np.arange(n)
    effects=rng.normal(0,.7,n);effects[:80]+=2.0;effects[80:155]-=2.0
    probabilities=np.clip(rng.uniform(.08,1,n),.000001,1);probabilities[:155]=10**(-rng.uniform(1.5,6,155))
    de=pd.DataFrame(dict(gene=genes,log2FC=effects,padj=probabilities))
    add('BulkDE',de,'figure_styles.plot_volcano_editorial',dict(alpha=.05,fc=1,labels=[genes[i] for i in [8,37,90,122]]),'Synthetic gene result','All 1200 fictional gene results from a declared donor-level contrast')
    status=np.where((probabilities<=.05)&(effects>=1),'up',np.where((probabilities<=.05)&(effects<=-1),'down','other'))
    ma=pd.DataFrame(dict(feature_id=genes,effect=effects,status=status,average=rng.uniform(2,12,n)))
    ma_params=dict(mode='ma',contract=dict(source_definition='Fictional frozen mean-effect results',independent_unit='12 synthetic donors',denominator='1200 fictional genes',effect_definition='Stored log2 fold change',status_definition='Illustrative frozen FDR and fold-change classes',feature_selection='Complete fictional gene universe',average_definition='Stored mean log2 expression'),title='Mean-effect relationship')
    add('BulkMA',ma,'figure_qc_de.plot_frozen_qc_de',ma_params,'Synthetic gene result','All 1200 fictional gene effects and separately supplied expression means')
    selected=genes[:12]+genes[80:92]
    mat=pd.DataFrame([dict(feature=g,sample=s,value=float(np.clip((1 if i<12 else -1)*(1 if j>=6 else -1)*1.2+rng.normal(0,.35),-2.8,2.8))) for i,g in enumerate(selected) for j,s in enumerate(sample_names)])
    mat['sample_group']=mat['sample'].map(dict(zip(sample_names,samples.group)));mat['feature_block']=mat.feature.map({g:'Positive program' if i<12 else 'Negative program' for i,g in enumerate(selected)})
    add('BulkHeatmap',mat,'figure_extensions.plot_annotated_heatmap',dict(value_label='Stored row z-score',scale_type='signed',group_palette=pal,block_palette={'Positive program':'#D8795B','Negative program':'#4477AA'},row_order=selected,column_order=sample_names,column_annotation_label='Condition',row_annotation_label='Prespecified program'),'Synthetic selected gene-sample result','24 explicitly selected genes; all 12 donors; no rescaling or clustering')
    forest=pd.DataFrame(dict(label=[genes[i] for i in [8,37,90,122]],estimate=effects[[8,37,90,122]],lower=effects[[8,37,90,122]]-.38,upper=effects[[8,37,90,122]]+.38))
    add('GeneEffects',forest,'figure_core.plot_forest',dict(x_label='Stored log2 fold change',interval_label='Four prespecified genes / supplied 95% intervals',effect_scale='difference'),'Synthetic gene estimate','Four prespecified genes with illustrative uncertainty')
    ora=pd.DataFrame(dict(term=pathways,score=[.24,.20,.18,.15,.12,.09],padj=[.0001,.0006,.002,.009,.02,.045],count=[48,40,36,30,24,18]))
    add('Pathways',ora,'figure_styles.plot_enrichment_lollipop',dict(score_type='GeneRatio',denominator_label='Stored ORA / 200 query genes',count_label='Overlap genes'),'Synthetic pathway result','200 fictional query genes; supplied overlap counts and gene ratios')
    ranked=1200;ranks=np.arange(1,ranked+1);hit_ranks=np.arange(13,ranked,39);curve=.65*np.sin(np.pi*(ranks-1)/(ranked-1));curve[-1]=0
    gsea=pd.DataFrame([dict(kind='curve',pathway=pathways[0],rank=int(r),value=float(v)) for r,v in zip(ranks,curve)]+
        [dict(kind='metric',rank=int(r),value=float(v)) for r,v in zip(ranks,np.linspace(3,-3,ranked))]+
        [dict(kind='hit',pathway=pathways[0],rank=int(r),gene=genes[r-1],leading_edge=int(r<ranked/2)) for r in hit_ranks]+
        [dict(kind='summary',pathway=pathways[0],NES=1.92,padj=.0008,set_size=len(hit_ranks))])
    gp=copy.deepcopy(source_cases['gsea']['parameters']);gp['options'].update(curve_order=[pathways[0]],ranked_universe=ranked,contrast='Treated versus Control / illustrative',gene_set_version='Fictional complete gene set v0.9',title='Stored enrichment / exact ranked tracks')
    gp['contract'].update(source_definition='Fictional complete ranked result v0.9',independent_unit='Synthetic ranked identifiers; donor contrast supplied separately')
    add('EnrichmentTracks',gsea,'refined',gp,'Synthetic ranked gene and hit','All 1200 ranks; exact declared hit genes; no enrichment calculation')
    bulk_roles={'qc_distribution':'BulkQC','sample_embedding':'BulkPCA','sample_correlation':'BulkCorrelation','library_summary':'LibrarySizes','differential_expression':'BulkDE','differential_heatmap':'BulkHeatmap','effect_intervals':'GeneEffects','ma':'BulkMA','enrichment_summary':'Pathways','gsea_curves':'EnrichmentTracks'}
    count=900;cell_ids=['Cell '+str(i+1).zfill(4) for i in range(count)];donor=np.repeat(np.arange(12),[48,56,66,62,74,70,75,80,84,90,95,100])
    ct=np.array([rng.choice(len(types),p=[.30,.18,.17,.20,.15] if d<6 else [.20,.13,.32,.14,.21]) for d in donor])
    angle=np.arange(len(types))*2*np.pi/len(types);x=np.cos(angle[ct])*3+rng.normal(0,.45,count);y=np.sin(angle[ct])*3+rng.normal(0,.45,count)
    cells=pd.DataFrame(dict(cell_id=cell_ids,donor_id=[donor_names[i] for i in donor],group=[groups[i//6] for i in donor],celltype=[types[i] for i in ct],batch=[batches[i%3] for i in donor],x=x,y=y))
    (out/'cells.tsv').write_bytes(table_bytes(cells))
    cell_qc=pd.concat([pd.DataFrame(dict(cell_id=cell_ids,sample=[sample_names[i] for i in donor],metric=metric,value=values)) for metric,values in [('genes',rng.lognormal(7.5,.35,count)),('umis',rng.lognormal(9,.42,count)),('mitochondrial',np.clip(rng.normal(6,2,count),.3,18))]],ignore_index=True)
    add('CellQC',cell_qc,'figure_core.plot_qc',dict(y_label='Stored cell QC',metric_field='metric',metric_labels={'genes':'Detected genes / cell','umis':'Total UMIs / cell','mitochondrial':'Mitochondrial fraction (%)'}),'Synthetic cell-metric','All 900 cells across 12 donors; three stored QC metrics; no filtering or threshold estimation')
    counts=pd.DataFrame(dict(sample_id=donor_names,group=samples.group,value=[int((donor==i).sum()) for i in range(12)]))
    add('DonorCounts',counts,'figure_core.plot_samples',dict(palette=pal,y_label='Stored retained cells per donor'),'Synthetic donor','One total count per donor; 12 donors, two conditions')
    emb=cells[['cell_id','celltype','x','y']].rename(columns={'celltype':'group'})
    add('CellTypes',emb,'figure_core.plot_embedding',dict(palette={t:theme['palette_colors'][slots[t]] for t in types},axis_prefix='Stored mock UMAP'),'Synthetic cell','All 900 supplied cell coordinates; five fictional annotations')
    batch=cells[['cell_id','batch','x','y']].rename(columns={'batch':'group'})
    add('CellBatches',batch,'figure_core.plot_embedding',dict(palette={t:theme['palette_colors'][slots[t]] for t in batches},axis_prefix='Stored mock UMAP'),'Synthetic cell','Identical stored coordinates; original fictional batch labels')
    markers=genes[:20]
    dots=pd.DataFrame([dict(feature=g,group=t,value=float(.4+3.3*(i%5==j)+.1*np.sin(i+j)),fraction=float(.15+.7*(i%5==j)+.05*np.cos(i+j))) for i,g in enumerate(markers) for j,t in enumerate(types)])
    add('MarkerDot',dots,'figure_core.plot_dot',dict(value_label='Stored mean expression',value_semantics='mean_all',denominator_label='All cells in each type',row_order=markers,column_order=types),'Synthetic gene-celltype result','All annotated cells per type; supplied mean and detection fraction')
    features=pd.DataFrame([dict(cell_id=cell_ids[j],x=float(x[j]),y=float(y[j]),feature=markers[i],value=float(.05+4.*(ct[j]==i)+.5*(j%7)/7)) for i in range(4) for j in range(count)])
    add('MarkerFeatures',features,'figure_publication.plot_feature_facets',dict(value_label='Stored expression',limits=[0,5],ncols=2),'Synthetic cell-feature result','Four prespecified markers; all 900 unchanged cell coordinates')
    comps=pd.DataFrame([dict(sample=donor_names[i],group=groups[i//6],celltype=t,count=int(((donor==i)&(ct==j)).sum())) for i in range(12) for j,t in enumerate(types)])
    add('DonorComposition',comps,'figure_styles.plot_composition_panels',dict(palette=pal,unit_label='synthetic donor',ncols=3),'Synthetic donor-celltype count','Complete 12-donor by 5-celltype counts; fractions use each donor total')
    common_de=de.assign(record_type='de')
    bulk_main=pd.concat([pca.rename(columns={'unit_id':'object_id'}).assign(record_type='embedding'),common_de,
        mat.assign(record_type='matrix'),ora.assign(record_type='enrichment')],ignore_index=True)
    add('BulkMain',bulk_main,'figure_study_overview.plot_transcriptomic_overview',dict(assay='bulk',contrast='Treated versus Control / illustrative',independent_unit='12 synthetic donors / all results are fictional',denominator='Complete 1200 gene results; prespecified 24-gene matrix; six supplied ORA terms',embedding_axes=['PC1 (38.4%)','PC2 (17.6%)'],labels=[genes[8],genes[90]]),'Synthetic frozen study channel','Exact supplied records for four complementary panels; no analysis')
    single_main=pd.concat([emb.rename(columns={'cell_id':'object_id'}).assign(record_type='embedding'),common_de,
        dots.assign(record_type='marker_dot'),comps.rename(columns={'celltype':'category','group':'condition'}).assign(record_type='composition')],ignore_index=True)
    add('SingleCellMain',single_main,'figure_study_overview.plot_transcriptomic_overview',dict(assay='single_cell',contrast='Cell identity and myeloid donor response / illustrative',independent_unit='12 synthetic donors / 900 nested cells / fictional results',denominator='All 900 stored cell coordinates; 20 markers; all 12 donor compositions; 1200 myeloid donor-level gene results',panel_titles={'de':'Myeloid donor response'},labels=[genes[8],genes[90]]),'Synthetic frozen study channel','Four complementary panels; donor-level inference inputs are distinct from cell observations')
    for key in ['BulkMain','SingleCellMain']:
        path=out/key/(key+'.spec.json');spec=json.loads(path.read_text(encoding='utf8'));spec['export'].update(target_width_mm=178,minimum_text_pt=7.5);spec['appearance']['note_pt']=9;write(path,spec)
    bulk_roles['study_overview']='BulkMain'
    # Separate scope-specific specifications prevent bulk provenance from being
    # mistaken for donor-pseudobulk evidence. Values are still fictional frozen
    # inputs, reused deliberately; no pseudobulk fitting takes place here.
    cell_result_keys={}
    for source,key in [('BulkDE','DonorDE'),('GeneEffects','DonorEffects'),('BulkMA','DonorMA'),('BulkHeatmap','DonorHeatmap'),('Pathways','DonorPathways'),('EnrichmentTracks','DonorEnrichmentTracks')]:
        folder=out/key;folder.mkdir();spec=copy.deepcopy(json.loads((out/source/(source+'.spec.json')).read_text(encoding='utf8')))
        raw=(out/source/(source+'.tsv')).read_bytes();(folder/(key+'.tsv')).write_bytes(raw)
        spec.update(figure_id=key);spec['input']['path']=key+'.tsv'
        spec['provenance'].update(input_unit='Fictional myeloid donor-pseudobulk result',denominator='One prespecified myeloid annotation across 12 synthetic donors; exact supplied gene or pathway scope',model='Fictional donor-level pseudobulk channel; illustrative values reused from the frozen bulk fixture; no analysis performed')
        if source=='BulkMA':spec['parameters']['contract']['independent_unit']='12 synthetic myeloid donors'
        if source=='EnrichmentTracks':spec['parameters']['contract']['independent_unit']='Synthetic ranked genes from the declared myeloid donor contrast'
        write(folder/(key+'.spec.json'),spec);all_specs[key]=key+'/'+key+'.spec.json';metadata[key]=dict(rows=metadata[source]['rows'],unit='Fictional myeloid donor result',denominator=spec['provenance']['denominator']);cell_result_keys[source]=key
    cell_roles={'study_overview':'SingleCellMain','qc_distribution':'CellQC','donor_summary':'DonorCounts','batch_embedding':'CellBatches','celltype_embedding':'CellTypes','marker_dot':'MarkerDot','marker_features':'MarkerFeatures','donor_composition':'DonorComposition','donor_differential':'DonorDE','effect_intervals':'DonorEffects','ma':'DonorMA','differential_heatmap':'DonorHeatmap','enrichment_summary':'DonorPathways','gsea_curves':'DonorEnrichmentTracks'}
    for assay,roles in [('bulk',bulk_roles),('single_cell',cell_roles)]:
        manifest=dict(schema_version=1,assay=assay,title='Fictional '+assay+' transcriptomic result package',contrast='Treated versus Control / illustrative',independent_unit='Synthetic donor; n=12; cells nested within donors',denominator='12 synthetic donors; 1200 fictional gene results; explicit cell-level display denominators',frozen_results=True,upstream_qc='reviewed',results=[dict(role=role,spec=all_specs[key]) for role,key in roles.items()])
        write(out/(assay+'.manifest.json'),manifest)
    write(out/'fixture-receipt.json',dict(scope='Coherent fictional result channels prepared before drawing; not data generated by an RNA-seq pipeline',seed=seed,donors=12,cells=count,genes=n,figures=metadata,inference_performed=False,scientific_acceptance=False))
    print(json.dumps(dict(specifications=len(all_specs),assays=2,donors=12,cells=count,genes=n)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();prepare(a.output)
