"""Author executable chapter recipes and fictional, method-specific display inputs.

Only drawing examples are produced. No RNA analysis, estimation or inference.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))

SOURCES={
 'scrna':'https://junjunlab.github.io/scRNAtoolVis-manual/jjdotplot.html',
 'volcano':'https://junjunlab.github.io/scRNAtoolVis-manual/jjvolcano.html',
 'scplotter':'https://pwwang.github.io/scplotter/',
 'gseavis':'https://junjunlab.github.io/gseavis-manual/basic-usage.html',
 'enrichplot':'https://yulab-smu.top/clusterProfiler-book/',
 'hdwgcna':'https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html',
 'deseq':'https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html',
 'bestpractices':'https://www.sc-best-practices.org/',
 'complexheatmap':'https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html'}

# ID, title, method family, required frozen results, specific design/QC and limit.
BULK=[
 ('design','Design and independent units','design','sample_covariates;library_counts','Review design rank, pairing and confounding; technical libraries do not increase biological n.'),
 ('reads','Read quality and sequence composition','reads','base_quality;read_classes','Complete base positions and all read classes; no silent removal of failed libraries.'),
 ('alignment','Alignment and gene-body coverage','alignment','alignment_classes;gene_body_coverage','Reference build, strandedness and assay must match; coverage is not expression.'),
 ('filtering','Detection and filtering sensitivity','filtering','threshold_profile;retained_feature_counts','Freeze tested universe and rule; do not choose thresholds for more discoveries.'),
 ('normalization','Normalization and mean-variance diagnostics','normalization','rle_density;mean_variance','Declare RLE/reference and transformed scale; drawing never estimates density or normalization.'),
 ('batch','Sample architecture and batch coverage','rich:BulkPCA','embedding;ellipse_geometry;marginal_counts;variance_profile','Ellipse meaning and all samples required; separation does not establish successful batch correction.'),
 ('differential','Differential expression with full distributions','rich:BulkDE','complete_de;effect;p_adj;marginal_counts','Freeze contrast, independent units and FDR family; no selected-gene-only volcano.'),
 ('interaction','Interactions across conditions and time','interaction','interaction_effects;model_predictions','Require a same-study factorial design and estimable interaction; separate cohorts cannot identify interaction.'),
 ('model_qc','Model fit and influence diagnostics','diagnostics','residuals;dispersion_curve;influence','Use actual fitted-model residuals and influential observations; a model is not accepted by a pretty plot.'),
 ('programs','Gene programs and selected effects','programs','selected_expression;effect_intervals','Freeze selection and scale; interval level and denominator must be declared.'),
 ('ora','ORA themes, ratios and supporting genes','story:ora','term_ratio;term_fdr;gene_term_membership','Actual tested background and mapping versions required; ORA does not establish activity direction.'),
 ('gsea','Full GSEA tracks and leading edge','rich:EnrichmentTracks','complete_rank_curve;rank_metric;hit_ranks;leading_edge;NES;FDR','Full signed ranked universe, ties and gene-set version required; never reconstruct a curve from NES.'),
 ('pathway_contrasts','Pathway enrichment across contrasts','story:gsea_comparison','NES_grid;FDR_grid;set_coverage','Keep not-tested distinct from nonsignificant; cross-contrast effect and FDR families must be explicit.'),
 ('gene_support','Pathway membership and signed gene evidence','story:gene_support','term_overlap;gene_term_membership;gene_effects','Absence of membership differs from missing annotation; selection and background must be frozen.'),
 ('gsea_multitrack','Multiple GSEA curves with complete rank tracks','multi_gsea','complete_curves;rank_metric;hits;leading_edge;NES;FDR','Every curve and rank is supplied; no invented ES curve, recomputed FDR or selected-rank truncation.'),
 ('gsva','Sample-level gene-set scoring','scores','sample_scores;coverage;score_effects','GSVA/ssGSEA scale and subsequent donor-level model differ; do not interpret scores as absolute activity.'),
 ('wgcna','Coexpression modules and preservation','modules','module_trait;preservation;fixed_network','Freeze module assignment and test/train cohorts; coexpression does not prove regulation.'),
 ('tf_activity','Transcription-factor footprints','regulation','TF_activity;TF_effects;targets','Record regulon/sign and coverage; inferred activity is not direct binding evidence.'),
 ('deconvolution','Cell-mixture estimates and uncertainty','mixture','sample_fractions;fraction_effects','Declare reference and compositional denominator; model fractions are not measured cell counts.'),
 ('splicing','Alternative splicing and junction support','splicing','junction_coverage;delta_PSI;isoform_usage','Freeze event coordinates/build and donor support; gene DE and splicing are distinct tests.'),
 ('dtu','Differential transcript usage','usage','transcript_fractions;usage_intervals','Require transcript-version mapping and parent-gene denominator; transcript fractions are compositional.'),
 ('timecourse','Longitudinal response and uncertainty','time','time_predictions;effect_intervals','Repeated donors and time units required; supplied model curves only, no smoothing for appearance.'),
 ('replication','Independent-cohort replication','replication','cohort_effects;matched_features','Harmonize effect scale and biological context; prevent overlap and discovery-validation leakage.'),
 ('survival','Conditional clinical outcome association','survival','survival_curves;risk_table;hazard_intervals','Clinical use requires endpoint/censoring/design review; association is not clinical prediction validation.'),
 ('ppi','Protein-interaction evidence','network','fixed_nodes;fixed_edges;edge_weights','Record evidence class, full selected edges and species; graph proximity is not mechanism.'),
 ('connectivity','Perturbation-signature matching','connectivity','connection_scores;signature_coverage','Preserve perturbation/dose/cell context; reversed signatures do not establish efficacy.'),
 ('noncoding','Noncoding RNA and target hypotheses','noncoding','RNA_effects;RNA_target_edges','Require RNA biotype and target-evidence provenance; coexpression is not a validated ceRNA mechanism.'),
 ('fusions','Fusion and transcript-structure evidence','fusion','breakpoint_support;coverage;validation_summary','Needs sequence-level evidence and artifact checks; a breakpoint call is not validated oncogenicity.')]
SC=[
 ('design','Donor, capture and condition design','design','donor_covariates;capture_counts','Cells, captures and donors differ; record nested design and donor replication.'),
 ('barcode','Barcode rank and retained droplets','barcode','barcode_rank;droplet_classes','Need raw droplet totals and selected threshold; cell calling does not validate cell identity.'),
 ('qc','Cell quality across donors','rich:CellQC','cell_metrics;donor_labels','Retain metric units and actual thresholds; cells remain nested within donors.'),
 ('ambient_doublet','Ambient RNA and doublet diagnostics','ambient','doublet_scores;ambient_profile;donor_rates','Method scores and reviewed calls are separate; preserve flagged cells and removal rules.'),
 ('integration','Batch integration and signal preservation','integration','stored_embeddings;mixing_scores;biology_scores','Use frozen pre/post diagnostics and batch-donor mapping; good mixing can erase biology.'),
 ('hvg_pca','Feature selection and PC support','pca','variance_profile;loadings;feature_dispersion','Selection source and PC loading signs required; no PCA fit during plotting.'),
 ('resolution','Cluster resolution and donor support','resolution','resolution_edges;stability;donor_support','Freeze cluster lineage and selected resolution; stability does not establish biological identity.'),
 ('annotation','Subpopulations with marker support','rich:CellTypes','embedding;label_anchors;marker_means;detection_fractions','Atlas identity and specificity; per-subgroup multi-marker pages are complete separate companions. Annotation specificity and uncertainty require review.'),
 ('subcluster','Lineage-focused subcluster atlas','subcluster','lineage_embedding;markers;parent_child_labels','Explicit parent selection and child annotation; subclustering requires actual reanalysis upstream.'),
 ('markers','Marker specificity and detection','rich:MarkerDot','marker_means;detection_fractions;annotation_blocks','Denominator must be all declared cells in a group; marker ranking is not donor-level DE.'),
 ('composition','Donor-level composition','rich:DonorComposition','donor_type_counts;donor_totals','Use complete donor denominators; pooled cell fractions do not provide independent replication.'),
 ('abundance','Differential abundance with donor effects','abundance','neighborhood_effects;donor_fractions;coordinates','Milo/scCODA need distinct model/null/denominator; abundance and expression are different estimands.'),
 ('pseudobulk','Donor-level differential response','rich:DonorDE','complete_donor_de;contrast;FDR;marginal_counts','Donor/celltype counts and design must be reviewed; no cell-level pseudoreplication.'),
 ('multi_contrast','Celltype-by-contrast differential atlas','multi_contrast','effect_grid;FDR_grid;tested_feature_counts','Keep separate comparison families and not-tested entries; do not pool donor and cell p-values.'),
 ('pathways','Celltype pathway responses','story:gsea_comparison','NES_grid;FDR_grid;leading_edge','Preserve celltype contrast and set coverage; activity direction cannot be inferred from ORA.'),
 ('gene_support','Celltype pathway membership and gene evidence','story:gene_support','term_overlap;gene_term_membership;gene_effects','Preserve celltype-specific tested universe and exact annotation membership.'),
 ('states','Cell-state, stress and cycle scores','scores','state_scores;coverage;donor_effects','Score coverage/cell cycle and donor model need review; cell scores do not increase independent n.'),
 ('hdwgcna','Celltype coexpression modules','modules','module_trait;preservation;fixed_network','Declare metacell/donor independence and module preservation; metacells are not new donors.'),
 ('trajectory','Branches, progression and gene dynamics','trajectory','embedding;pseudotime;branch_curves;gene_trends','Freeze root/branch and uncertainty; pseudotime is not chronological time or lineage proof.'),
 ('velocity','RNA velocity and phase diagnostics','velocity','vectors;spliced_unspliced;fit_diagnostics','Require assay-compatible splicing layers, fitted vectors and scale; arrows do not prove fate.'),
 ('communication','Communication themes and ligand-receptor support','communication','sender_receiver;LR_scores;coverage','CellChat/LIANA/CellPhoneDB scores are method-specific; donor-aware contrast and permutations required.'),
 ('ligand_target','Ligand-to-target evidence chains','ligand_target','ligand_activity;target_potential;network','NicheNet prior and receiver context required; target potential does not prove signaling causality.'),
 ('regulons','Regulon activity and target specificity','regulation','regulon_scores;specificity;target_edges','SCENIC/AUCell motif/score evidence is not direct binding or causal regulation.'),
 ('cnv','Inferred copy-number patterns','cnv','ordered_CNV;reference_cells;clone_support','Genomic coordinates and normal reference required; RNA-inferred CNV needs independent genomic validation.'),
 ('vdj','Clonotypes, expansion and sharing','clones','clonotype_counts;VDJ_QC;sharing','Require real VDJ calls and donor denominators; transcriptome-only data do not identify clonotypes.'),
 ('splicing','Celltype-specific RNA processing','splicing','junction_coverage;delta_PSI;isoform_usage','Donor support and event mapping required; cell-level detection sparsity must be reviewed.'),
 ('perturbseq','Perturbation assignment and response','perturbation','guide_assignment;perturbation_effects;replicate_QC','Actual guide calls, controls and independent replicates required; guide abundance is not perturbation efficacy.'),
 ('replication','Cross-cohort annotation and effect transfer','replication','cohort_effects;transfer_confidence;coverage','Independent cohorts and matching cell ontology required; transfer confidence is not validation truth.'),
 ('spatial','Spatial localization and donor/section context','spatial','registered_coordinates;region_scores;section_effects','Requires measured spatial assay and registration; dissociated UMAP is not tissue geography.'),
 ('multiome','Paired RNA-ATAC regulatory support','multiome','paired_embeddings;peak_gene_links;motif_scores','Paired assay, build and peak/link evidence required; peak-gene association is not causal regulation.')]

def catalog():
    rows=[]
    for assay,entries in [('bulk',BULK),('single_cell',SC)]:
        for key,title,family,inputs,limit in entries:
            source=['deseq','complexheatmap'] if assay=='bulk' else ['scrna','scplotter','bestpractices']
            if key in ['ora','gsea','pathways','pathway_contrasts','gsva']:source=['gseavis','enrichplot']
            if key in ['wgcna','hdwgcna']:source=['hdwgcna']
            rows.append(dict(id=assay+'.'+key,assay=assay,title=title,family=family,
                required_results=inputs.split(';'),specific_qc_and_limit=limit,
                plot_capability='IMPLEMENTED_WITH_EXECUTABLE_EXAMPLE',example='assets/chapter-gallery/'+assay+'.'+key+'/input/example.spec.json',
                code='scripts/figure_annotation_views.py' if key=='annotation' else 'scripts/figure_wgcna_views.py' if key in ['wgcna','hdwgcna'] else 'scripts/figure_lineage_views.py' if key in ['resolution','trajectory'] else 'scripts/figure_enrichment_story.py' if family.startswith('story:') else 'scripts/figure_refined_views.py' if family=='multi_gsea' else 'scripts/figure_chapter_views.py' if not family.startswith('rich:') else 'scripts/figure_integrated_views.py and existing attributed drawing modules',
                sources=[SOURCES[s] for s in source],analysis_execution='Existing server workflow; separately validated actual backend',
                selection='Explicit scientific question and assay prerequisites; conditional chapters are never automatically imposed'))
    return dict(schema_version=1,version='0.9.1',chapters=rows,sources=SOURCES,
        source_adoption='Original drawing code; community/author layout ideas reviewed. No third-party source, data, scripts or weights redistributed.',
        example_scope='Fictional frozen display inputs; every chapter has a runnable example; no analysis engines executed')

def build(out,rich,wgcna=None,depth=None):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    out.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(9148)
    base=json.loads((rich/'BulkQC/BulkQC.spec.json').read_text(encoding='utf8'));records=[]
    terms=['Interferon response','Matrix organization','Oxidative metabolism','RNA processing','Cell cycle','Antigen presentation']
    modules=['Module M1','Module M2','Module M3','Module M4','Module M5','Module M6']
    celltypes=['T cells','B cells','Myeloid','Stromal','Endothelial']
    genes=['STAT1','IRF7','COL1A1','NDUFA1','SRSF1','MKI67']
    stable=dict(base['theme']['group_slots'])
    identity_groups=[['Control','Treated'],celltypes,['Capture A','Capture B','Capture C'],['Root state','Branch A','Branch B'],['Before','After'],['Lower score','Higher score'],['Gene A','Gene B'],['Pass','Warning','Fail'],['Unique','Multi-map','Unmapped'],['Library 1','Library 2'],['Cohort A','Cohort B'],['Observed summary','Fitted trend'],['Program A','Program B'],['Singleton','Small clone','Expanded clone'],['Transcript 1','Transcript 2','Transcript 3'],['Isoform 1','Isoform 2'],['Singlet','Ambiguous','Doublet'],['Retained','Ambiguous','Background'],['Reference','Clone A','Clone B'],['Region A','Region B','Region C'],['State A','State B','State C'],['Single guide','Multiple','Unassigned'],['Immune themes','Cellular programs'],['Declared relationship'],['Read 1','Read 2'],['Complete supplied PCs']]
    for identities in identity_groups:
        for i,name in enumerate(identities):stable[name]=i
    def panel(kind,title,x='',y='',**kw):return dict(kind=kind,title=title,x_label=x,y_label=y,**kw)
    for row in catalog()['chapters']:
        k=row['id'];family=row['family'];folder=out/k;folder.mkdir();spec=copy.deepcopy(base);parts=[];panels=[]
        def add(p,rows):
            p['id']='p'+str(len(panels)+1);panels.append(p);d=pd.DataFrame(rows);d['panel_id']=p['id'];parts.append(d)
        def matrix(title,labels,cols,values=None,value_label='Supplied score',limits=(-2,2),bubble=False):
            values=np.clip(rng.normal(0,.9,(len(labels),len(cols))),limits[0]+.05,limits[1]-.05) if values is None else values
            add(panel('bubble' if bubble else 'matrix',title,value_label=value_label,limits=list(limits),fraction_definition='Explicit fictional detection or coverage fraction in each declared group',size_label='Coverage',show_values=len(labels)*len(cols)<=36),[dict(label=l,series=c,value=float(values[i,j]),fraction=float(.18+.75*((i+j)%4)/3)) for i,l in enumerate(labels) for j,c in enumerate(cols)])
        def effects(title,labels,xlabel='Supplied effect and 95% interval',values=None):
            vals=rng.normal(0,.7,len(labels)) if values is None else values
            add(panel('interval',title,xlabel,interval_definition='Explicit fictional 95% intervals; no interval estimation'),[dict(label=l,x=float(v),lower=float(v-.22-.04*(i%3)),upper=float(v+.22+.04*(i%3))) for i,(l,v) in enumerate(zip(labels,vals))])
        def curves(title,names,xlabel,ylabel,n=24,positive=False):
            rows=[]
            for j,s in enumerate(names):
                xx=np.linspace(0,1,n);yy=.4*np.sin(xx*np.pi*(j+1)/2)+.35*j+(1.1 if positive else 0);spread=.09
                if family=='reads':yy=34-9*xx**3-j*2;spread=.7
                elif family=='barcode':yy=5.2-4*xx**.3-j*.25
                elif family=='filtering':yy=.98-.65*xx-.05*j;spread=.02
                elif family=='normalization':
                    xx=np.linspace(-2,2,n);sigma=.9 if j==0 else .48;yy=np.exp(-xx**2/(2*sigma**2))/(sigma*np.sqrt(2*np.pi));spread=.015
                elif family=='pca':
                    xx=np.arange(1,n+1);yy=np.exp(-np.arange(n)/5);yy=100*yy/yy.sum();spread=.02
                lower=yy-spread;upper=yy+spread
                if family in ['normalization','pca']:lower=np.maximum(lower,0)
                if family=='filtering':lower=np.maximum(lower,0);upper=np.minimum(upper,1)
                rows.extend(dict(series=s,x=float(x),y=float(y),lower=float(lo),upper=float(hi)) for x,y,lo,hi in zip(xx,yy,lower,upper))
            add(panel('curve',title,xlabel,ylabel,interval_definition='Explicit fictional range coordinates; no smoothing/fitting',interval_label='Shading: supplied illustrative range'),rows)
        def stacks(title,labels,segments,xlabel='Supplied fraction'):
            rows=[]
            for i,l in enumerate(labels):
                vals=np.array([1+(i+j*2)%5 for j in range(len(segments))],float);vals/=vals.sum()
                rows.extend(dict(label=l,series=s,value=float(v)) for s,v in zip(segments,vals))
            add(panel('stack',title,xlabel,denominator_definition='All explicitly declared observations for each displayed object; full segments sum to one'),rows)
        def network(title,names):
            theta=np.arange(len(names))*2*np.pi/len(names);coords=dict(zip(names,zip(np.cos(theta),np.sin(theta))));rr=[]
            for i,l in enumerate(names):
                for j in range(i+1,len(names)):
                    if (i+j)%2:
                        x,y=coords[l];tx,ty=coords[names[j]];rr.append(dict(label=l,target=names[j],series='Declared relationship',x=x,y=y,target_x=tx,target_y=ty,value=float(.3+.7*((i+j)%5)/4)))
            add(panel('network',title,edge_definition='Complete explicitly selected illustrative edge list; weights and coordinates supplied; no layout fit or pruning'),rr)
        def points(title,names,xlabel,ylabel,n=60):
            rr=[]
            for j,s in enumerate(names):
                for i in range(n):
                    noise=rng.normal(0,.12);x=float(i/n*4);y=float(.5+j*.45+.8*np.sin(i*.12)+noise)
                    if family=='ambient':x=(i+1)/(n+1);y=float(np.clip(.04+.2*x+.125*noise+.05*j,0,1))
                    elif family=='velocity':y=float(max(.01,.6+j*.45+.4*np.sin(i*.12)+.5*noise))
                    elif family=='normalization':y=float((.35+.25*x**1.7)*(1.6 if j==0 else 1)+abs(noise)*.4+.02)
                    elif family=='diagnostics':y=float(noise*3.75+.20*np.sin(i*.12))
                    rr.append(dict(series=s,x=x,y=y))
            unit='Cell' if family=='ambient' else 'Cell-phase observation' if family=='velocity' else 'Gene' if family=='normalization' else 'Supplied model observation'
            add(panel('points',title,xlabel,ylabel,point_unit=unit),rr)
        def embedding(title,names):
            rr=[]
            for j,s in enumerate(names):
                a=j*2*np.pi/len(names);cx,cy=3*np.cos(a),3*np.sin(a)
                for i in range(50):rr.append(dict(label=s+' '+str(i+1),series=s,x=float(cx+rng.normal(0,.38)),y=float(cy+rng.normal(0,.38)),anchor_x=float(cx),anchor_y=float(cy+.65)))
            add(panel('embedding',title,'Stored coordinate 1','Stored coordinate 2'),rr)
        if family.startswith('story:'):
            contrasts=['Contrast A','Contrast B','Contrast C'] if family.endswith('gsea_comparison') else ['Treated versus Control']
            rr=[dict(record_type='term',term=t,contrast=c,family='Immune themes' if i<2 or i==5 else 'Cellular programs',padj=float(10**(-(.7+(i+j)%5*.7))),count=12+i*4,ratio=(12+i*4)/200,NES=float(np.clip(1.8*np.sin((i+1)*(j+1)),-2,2))) for i,t in enumerate(terms) for j,c in enumerate(contrasts)]
            rr.extend(dict(record_type='membership',term=t,gene=g,member=int((i+j)%3==0 or i==j)) for i,t in enumerate(terms) for j,g in enumerate(genes))
            rr.extend(dict(record_type='gene',gene=g,effect=float(v)) for g,v in zip(genes,[1.6,1.2,-1.4,-1.0,.7,1.8]));data=pd.DataFrame(rr)
            is_gsea=family.endswith('gsea_comparison')
            spec.update(renderer='figure_enrichment_story.plot_enrichment_story',parameters=dict(mode=family.split(':')[1],title=row['title'],background_definition='Fictional complete 1200-gene ranked universe' if is_gsea else 'Fictional 200-gene query / 1200 tested genes',tested_size=1200,query_size=None if is_gsea else 200,nes_limits=[-3,3],gene_effect_limits=[-3,3],gene_set_version='Illustrative frozen sets v0.9.1',selection_definition='All six explicitly selected terms; all six declared support genes; no results filtered for appearance',support_contrast=contrasts[0],columns='auto'))
            spec['export'].update(target_width_mm=297,minimum_text_pt=7.5,raster_dpi=300,readability_policy='block');spec['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        elif family=='multi_gsea':
            source='EnrichmentTracks';spec=json.loads((rich/source/(source+'.spec.json')).read_text(encoding='utf8'));original=pd.read_csv(rich/source/(source+'.tsv'),sep='\t');frames=[original[original.kind=='metric']]
            for i,t in enumerate(terms[:3]):
                q=original[original.kind!='metric'].copy();q['pathway']=t;q.loc[q.kind=='curve','value']*=1 if i==0 else -.8 if i==1 else .7;q.loc[q.kind=='summary','NES']=1.92 if i==0 else -1.6 if i==1 else 1.4
                if i==1:q.loc[q.kind=='hit','leading_edge']=(q.loc[q.kind=='hit','rank']>600).astype(int)
                frames.append(q)
            data=pd.concat(frames,ignore_index=True);spec['parameters']['options'].update(curve_order=terms[:3],title=row['title'],line_encoding='pathway',ncols=1,panel_width=7,panel_height=3.6);spec['export'].update(target_width_mm=210,minimum_text_pt=7.5)
            spec['theme']['group_slots'].update({t:i for i,t in enumerate(terms[:3])})
        elif family.startswith('rich:'):
            source=family.split(':')[1];spec=json.loads((rich/source/(source+'.spec.json')).read_text(encoding='utf8'));data=pd.read_csv(rich/source/(source+'.tsv'),sep='\t');spec['parameters']=copy.deepcopy(spec['parameters'])
        else:
            if family=='design':
                matrix('Covariates and independent units',['Condition','Batch','Pair ID'],['D01','D02','D03','D04','D05','D06'],values=np.array([[-1,-1,-1,1,1,1],[-1,0,1,-1,0,1],[-1,0,1,-1,0,1]]),value_label='Declared design code');stacks('Capture contribution by donor',['D01','D02','D03','D04','D05','D06'],['Capture A','Capture B'])
            elif family in ['reads','alignment','barcode','filtering']:
                if family=='reads':curves('Per-base quality profile',['Read 1','Read 2'],'Scaled read position','Supplied quality score');stacks('Complete read classes',['S01','S02','S03','S04'],['Pass','Warning','Fail'])
                elif family=='alignment':stacks('Alignment categories',['S01','S02','S03','S04'],['Unique','Multi-map','Unmapped']);curves('Gene-body coverage',['Library 1','Library 2'],'Relative gene position','Supplied normalized coverage',positive=True)
                elif family=='barcode':curves('Barcode rank profile',['Capture A','Capture B'],'Scaled barcode rank','Supplied log UMI count',positive=True);stacks('Droplet classification',['Capture A','Capture B','Capture C'],['Retained','Ambiguous','Background'])
                else:curves('Filtering sensitivity',['Cohort A','Cohort B'],'Declared filter threshold','Supplied retained fraction',positive=True);effects('Sensitivity of selected effects',genes)
            elif family=='normalization':curves('Supplied RLE profiles',['Before','After'],'Relative log expression','Supplied density',positive=True);points('Mean-variance relationship',['Before','After'],'Supplied mean','Supplied variance')
            elif family=='interaction':curves('Condition-by-time predictions',['Control','Treated'],'Scaled time','Supplied prediction');effects('Interaction terms',genes,xlabel='Supplied interaction coefficient and 95% interval')
            elif family=='diagnostics':points('Residual structure',['Batch 1','Batch 2'],'Supplied fitted value','Supplied residual');curves('Dispersion trend',['Observed summary','Fitted trend'],'Supplied mean','Supplied dispersion',positive=True)
            elif family in ['programs','scores','regulation','noncoding']:
                labels=terms if family=='scores' else ['STAT1 regulon','IRF7 regulon','NFKB1 regulon','JUN regulon','KLF2 regulon','ELF1 regulon'] if family=='regulation' else ['RNA001','RNA002','RNA003','RNA004','RNA005','RNA006'] if family=='noncoding' else genes
                matrix('Coordinated sample-level patterns',labels,['D01','D02','D03','D04','D05','D06'],value_label='Supplied score');effects('Donor-level effects and uncertainty',labels)
            elif family in ['enrichment','pathway']:
                matrix('Themes across conditions',terms,['Contrast A','Contrast B','Contrast C'],value_label='Supplied signed NES' if family=='pathway' else 'Supplied -log10 FDR',limits=(-2,2) if family=='pathway' else (0,5),values=None,bubble=True)
                matrix('Gene-level supporting evidence',genes,terms[:4],values=np.array([[1,0,0,1],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,1,0,1]],float),value_label='Supplied membership',limits=(0,1))
            elif family=='modules':matrix('Module-trait relationships',modules,['Condition','Age','Severity'],value_label='Supplied correlation',limits=(-1,1));effects('External module preservation',modules,xlabel='Supplied preservation difference and interval');network('Frozen module connections',['STAT1','IRF7','IFIT1','ISG15','MX1','OAS1'])
            elif family in ['mixture','usage','clones']:
                segments=celltypes if family=='mixture' else ['Transcript 1','Transcript 2','Transcript 3'] if family=='usage' else ['Singleton','Small clone','Expanded clone']
                stacks('Within-donor composition',['D01','D02','D03','D04','D05','D06'],segments);effects('Prespecified compositional comparisons',segments,xlabel='Supplied log-ratio effect and 95% interval')
                if family=='clones':matrix('Clonotype sharing',['D01','D02','D03','D04'],['D01','D02','D03','D04'],values=np.array([[1,.2,.1,.3],[.2,1,.4,.2],[.1,.4,1,.1],[.3,.2,.1,1]]),value_label='Supplied overlap index',limits=(0,1))
            elif family=='splicing':curves('Frozen junction/coverage profiles',['Control','Treated'],'Declared genomic offset','Supplied coverage',positive=True);effects('Junction usage differences',['Junction 1','Junction 2','Junction 3','Junction 4'],xlabel='Supplied delta PSI and 95% interval',values=[.22,-.18,.31,-.27]);stacks('Transcript usage',['D01','D02','D03','D04'],['Isoform 1','Isoform 2'])
            elif family=='fusion':
                add(panel('bars','Independent breakpoint support','Supplied supporting read count'),[dict(label=x,value=n) for x,n in [('Split reads · event A',24),('Spanning pairs · event A',18),('Split reads · event B',11),('Spanning pairs · event B',9)]])
                matrix('Breakpoint evidence checklist',['Event A','Event B'],['In-frame','Unique mapping','Orthogonal support'],values=np.array([[1,1,0],[0,1,0]],float),value_label='Declared binary evidence / not validation',limits=(0,1))
            elif family=='time':curves('Longitudinal expression profiles',['Program A','Program B'],'Scaled study time','Supplied response');effects('Time interaction estimates',genes)
            elif family=='replication':effects('Independent-cohort effect estimates',['Discovery','Replication 1','Replication 2','Prespecified meta'],values=[.7,.6,.82,.7]);matrix('Feature-level direction and magnitude',genes,['Discovery','Replication 1','Replication 2'],value_label='Supplied log2 effect')
            elif family=='survival':
                rr=[]
                for j,s in enumerate(['Lower score','Higher score']):
                    for x in range(9):
                        y=1-x*(.055+j*.025);rr.append(dict(series=s,x=x,y=y,lower=max(0,y-.06),upper=min(1,y+.06)))
                add(panel('curve','Supplied survival estimates','Time (declared units)','Survival probability',interval_definition='Explicit fictional 95% survival intervals',interval_label='Shading: supplied 95% interval',drawstyle='steps-post'),rr)
                matrix('At-risk counts',['Lower score','Higher score'],['0','2','4','6'],values=np.array([[40,34,26,18],[40,31,22,13]]),value_label='Supplied people at risk',limits=(0,40));effects('Adjusted outcome associations',['Prespecified score','Sensitivity model'],xlabel='Supplied log hazard ratio and 95% interval',values=[.3,.25])
            elif family in ['network','ligand_target']:network('Explicit evidence relationships',['Ligand A','Receptor B','TF C','Target D','Target E','Target F']);matrix('Selected relationship support',['Evidence 1','Evidence 2','Evidence 3'],['Edge A','Edge B','Edge C'],value_label='Supplied evidence score',limits=(0,2))
            elif family=='connectivity':effects('Signature connection scores',['Compound A','Compound B','Compound C','Compound D'],xlabel='Supplied connection score and interval');matrix('Signature coverage across contexts',terms,['Context A','Context B','Context C'],value_label='Supplied connection score')
            elif family=='ambient':points('Doublet and ambient diagnostics',['Capture A','Capture B'],'Supplied doublet score','Supplied ambient fraction');stacks('Reviewed calls by donor',['D01','D02','D03','D04'],['Singlet','Ambiguous','Doublet'])
            elif family=='integration':embedding('Fixed integrated coordinates',celltypes);matrix('Biology and batch diagnostics',['Batch mixing','Celltype conservation','Donor conservation'],['Before','After'],value_label='Supplied diagnostic score',limits=(0,2))
            elif family=='pca':curves('Explained-variance profile',['Complete supplied PCs'],'Scaled PC order','Supplied variance percent',positive=True);matrix('Selected PC loadings',genes,['PC1','PC2','PC3'],value_label='Supplied loading')
            elif family=='resolution':network('Frozen cluster lineage',['R0.2 A','R0.2 B','R0.5 A','R0.5 B','R0.8 A','R0.8 B']);matrix('Donor support across clusters',['Cluster 1','Cluster 2','Cluster 3','Cluster 4'],['D01','D02','D03','D04'],value_label='Supplied donor support',limits=(0,2))
            elif family=='subcluster':embedding('Selected lineage and child annotations',['State A','State B','State C']);matrix('Child-state marker specificity',genes,['State A','State B','State C'],value_label='Supplied mean expression',limits=(0,2),bubble=True)
            elif family=='abundance':effects('Donor-aware abundance contrasts',celltypes,xlabel='Supplied log abundance ratio and 95% interval');stacks('Complete donor composition',['D01','D02','D03','D04'],celltypes)
            elif family=='multi_contrast':matrix('Celltype-by-contrast effect atlas',celltypes,['Contrast A','Contrast B','Interaction'],value_label='Supplied log2 effect');effects('Prespecified celltype comparisons',celltypes)
            elif family=='trajectory':embedding('Frozen branch structure',['Root state','Branch A','Branch B']);curves('Supplied branch dynamics',['Branch A','Branch B'],'Supplied pseudotime','Supplied gene program');matrix('Ordered gene progression',genes,['Bin 1','Bin 2','Bin 3','Bin 4','Bin 5'],value_label='Supplied scaled expression')
            elif family=='velocity':
                rr=[dict(label='Cell '+str(i),x=float(i%12)/4,y=float(i//12)/3,u=float(.13+.03*np.sin(i)),v=float(.10*np.cos(i)),value=float(i/59)) for i in range(60)]
                add(panel('vector','Supplied velocity field','Frozen coordinate 1','Frozen coordinate 2',vector_definition='Supplied illustrative velocities in frozen embedding coordinates',arrow_scale=1,value_label='Supplied latent time'),rr);points('Splicing phase diagnostics',['Gene A','Gene B'],'Supplied spliced','Supplied unspliced')
            elif family=='communication':matrix('Sender-receiver landscape',celltypes,celltypes,value_label='Supplied interaction score',limits=(0,2));matrix('Ligand-receptor support',['L1 - R1','L2 - R2','L3 - R3','L4 - R4','L5 - R5'],['T to Myeloid','Myeloid to Stromal','Stromal to T'],value_label='Supplied LR score',limits=(0,2),bubble=True)
            elif family=='cnv':matrix('Genomically ordered copy-number scores',['chr1 bin 1','chr1 bin 2','chr2 bin 1','chr2 bin 2','chr3 bin 1','chr3 bin 2'],['Reference','Clone A','Clone B','Clone C'],value_label='Supplied relative CNV');stacks('Clone support by donor',['D01','D02','D03','D04'],['Reference','Clone A','Clone B'])
            elif family=='perturbation':stacks('Guide assignments by replicate',['Rep 1','Rep 2','Rep 3'],['Single guide','Multiple','Unassigned']);effects('Guide-level donor response',['Guide 1','Guide 2','Guide 3','Control A','Control B']);matrix('Perturbation programs',terms,['Target A','Target B','Control'],value_label='Supplied effect')
            elif family=='spatial':embedding('Registered measured spatial coordinates',['Region A','Region B','Region C']);effects('Donor/section region contrasts',['Region A','Region B','Region C']);matrix('Regional molecular programs',terms,['Region A','Region B','Region C'],value_label='Supplied regional score')
            elif family=='multiome':embedding('Frozen paired-cell coordinates',celltypes);matrix('Motif and RNA support',['STAT1','IRF7','JUN','KLF2','NFKB1'],['RNA','ATAC','Link score'],value_label='Supplied standardized evidence');network('Frozen peak-gene links',['Peak A','STAT1','Peak B','IRF7','Peak C','ISG15'])
            else:raise ValueError('No executable family: '+family)
            data=pd.concat(parts,ignore_index=True)
            spec.update(renderer='figure_chapter_views.plot_transcriptomic_chapter',parameters=dict(panels=panels,title=row['title'],scope_note='Fictional frozen inputs · '+row['assay']+' · no analysis performed',columns='auto'))
            spec['export'].update(target_width_mm=297,minimum_text_pt=7.5,raster_dpi=300,readability_policy='block');spec['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        dedicated={'bulk.wgcna':(wgcna,'WGCNA_ModuleTrait'),'single_cell.hdwgcna':(wgcna,'hdWGCNA_MetacellQC'),'single_cell.resolution':(depth,'ClusterFlow_2Column'),'single_cell.trajectory':(depth,'Trajectory_2Column')}
        if k in dedicated and dedicated[k][0] is not None:
            root,key=dedicated[k];p=root/key/'example.spec.json';spec=json.loads(p.read_text(encoding='utf8'));data=pd.read_csv(p.parent/spec['input']['path'],sep='\t')
        raw=table_bytes(data);(folder/'example.tsv').write_bytes(raw);spec.update(figure_id=k.replace('.','_'))
        spec['theme']['group_slots'].update(stable)
        spec['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in data if pd.api.types.is_numeric_dtype(data[c])])
        spec['provenance'].update(source='Fictional frozen chapter fixture v0.9.1; not an analysis output',input_unit='Explicit fictional '+row['family']+' display channels',model='No analysis or model fitted; numerical channels supplied as illustrative input',denominator='Complete explicit example table; selected display scope only',interpretation_limit=row['specific_qc_and_limit'],synthetic=True)
        (folder/'example.spec.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        records.append(dict(id=k,spec=k+'/example.spec.json',family=family,assay=row['assay']))
    (out/'manifest.json').write_text(json.dumps(dict(records=records,analysis_performed=False),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(status='CHAPTER_INPUTS_PREPARED',chapters=len(records),analysis_performed=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--rich',type=Path);p.add_argument('--wgcna',type=Path);p.add_argument('--depth',type=Path);p.add_argument('--catalog',action='store_true');a=p.parse_args()
    if a.catalog:(SKILL/'references/transcriptomic-chapters.json').write_text(json.dumps(catalog(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if a.output:build(a.output,a.rich,a.wgcna,a.depth)
