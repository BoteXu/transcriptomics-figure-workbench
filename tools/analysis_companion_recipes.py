"""Explicit per-analysis questions, channels and scientific boundaries.

Each row is an executable drawing recipe, not a claim that its analysis was
run. Reused geometry retains method-specific units, source definitions and
independent-unit requirements. Layout alternatives belong to the same form.
"""

GENES=['STAT1','IRF7','ISG15','COL1A1','NDUFA1','SRSF1','MKI67','KLF2','JUN','MX1','OAS1','IFIT1']
SETS=['Interferon response','Matrix organization','Oxidative metabolism','RNA processing','Cell cycle','Antigen presentation','Stress response','Lipid metabolism','Translation','Complement','Angiogenesis','DNA repair']
TYPES=['T cells','B cells','Myeloid','Stromal','Endothelial','NK cells','Pericytes','Mast cells','Epithelial','Progenitors','Plasma cells','Dendritic']
TFS=['STAT1','IRF7','JUN','KLF2','NFKB1','ELF1','GATA3','CEBPB','RUNX1','FOXP3']
LIGANDS=['TGFB1','CXCL12','IL6','VEGFA','CCL5','TNF','IFNG','EGF','FGF2','WNT3A']
LR=['TGFB1–TGFBR1','CXCL12–CXCR4','IL6–IL6R','VEGFA–KDR','CCL5–CCR5','TNF–TNFRSF1A','IFNG–IFNGR1','EGF–EGFR','FGF2–FGFR1']
LR_GENES=[g for pair in LR for g in pair.split('–')]
SIGNALS=['TGFB','CXCL','IL6','VEGF','CCL','TNF','IFN-II','EGF','FGF','WNT']
DONORS=['D'+str(i).zfill(2) for i in range(1,25)]

def R(kind,title,x,y='',*,labels=None,stage='interpretation',scale='signed',note='',**options):
    return dict(kind=kind,title=title,x_label=x,y_label=y,labels=labels or GENES,stage=stage,scale=scale,
                definition=note or title+'; all quantities are supplied frozen channels, with explicitly declared units and scope.',**options)

def E(title,labels=GENES,x='Effect · supplied 95% interval',**kw):
    # Context-bearing questions must actually show several contexts per feature.
    specific_models=all(any(w in str(v).lower() for w in ['primary','adjust','subset','cases','fit','cohort','discovery','synthesis','exclude','interaction','complete pairs','restricted time','influence','variance alternative']) for v in labels)
    if not specific_models and any(w in title.lower() for w in ['sensitivity','across','replication','independent','stability','after','reproducibility','choices']):
        cohort=any(w in title.lower() for w in ['cohort','replication','independent'])
        kw.setdefault('comparison_contexts',['Cohort A','Cohort B'] if cohort else ['Primary','Alternative'])
        kw.setdefault('independent_cohorts',cohort)
    return R('effects',title,x,labels=labels,**kw)
def C(title,y,**kw):return R('raincloud',title,kw.pop('x_label','Condition'),y,**kw)
def P(title,x,y,**kw):return R('profile',title,x,y,**kw)
def M(title,labels=GENES,cols=None,value='Supplied score',**kw):return R('matrix',title,'','',labels=labels,cols=cols or ['Control','Treated','Sensitivity'],value_label=value,**kw)
def F(title,labels=DONORS,segments=None,**kw):return R('fraction',title,'Fraction of declared denominator',labels=labels,segments=segments or ['Retained','Flagged','Unassigned'],scale='fraction',**kw)
def X(title,x,y,**kw):
    if kw.get('identity_reference') and 'Quantile' not in title and 'Unshrunk' not in title:kw.setdefault('series',['Cohort A','Cohort B'])
    return R('scatter',title,x,y,**kw)
def B(title,x,y='Supplied count',**kw):return R('bins',title,x,y,scale='positive',**kw)
def L(title,**kw):return R('locus',title,'Genomic position · declared reference build',labels=['Control','Treated'],**kw)
def A(title,y,**kw):return R('paired',title,'Repeated condition',y,series=['Before','After'],**kw)


RECIPES={
'bulk.design':[
 F('Biological units and library contributions',segments=['Library A','Library B','Library C'],stage='qc'),
 M('Covariates across independent donors',['Condition','Batch','Pair'],DONORS[:6],'Declared design code',categorical_design=True,stage='qc'),
 F('Group balance within batches',['Batch A','Batch B','Batch C'],['Control','Treated'],stage='qc',batch_donors=True),
 M('Missing covariate audit',['Condition','Age','Batch','Pair'],DONORS[:6],'Explicit missing indicator',scale='fraction',stage='qc',binary=True),
 E('Prespecified design sensitivity',['Primary design','Batch adjusted','Paired subset','Complete cases'],stage='validation')],
'bulk.reads':[
 P('Base-quality profiles by read','Read position (nt)','Phred quality',scale='quality',series=['Read 1','Read 2'],stage='qc'),
 P('Adapter content across read positions','Read position (nt)','Adapter fraction',scale='fraction',stage='qc'),
 B('Frozen read-length distribution','Read length (nt)',stage='qc'),
 P('Base composition across cycles','Read position (nt)','Base fraction',scale='fraction',series=['A','C','G','T'],composition_profile=True,stage='qc'),
 F('Duplication and unique-fragment classes',segments=['Unique','Duplicate','Unassigned'],stage='qc'),
 B('GC distributions against a frozen reference','GC fraction',series=['Observed','Frozen reference'],stage='qc'),
 F('Read retention through declared processing',['Raw','Trimmed','Assigned'],['Retained','Removed'],stage='validation',retention=True)],
'bulk.alignment':[
 F('Complete mapping categories',segments=['Unique','Multiple','Unmapped'],stage='qc'),
 P('Gene-body coverage by library','Relative gene position','Normalized coverage',scale='positive',series=['Library A','Library B'],stage='qc'),
 B('Insert-size distributions','Insert length (bp)',stage='qc'),
 F('Strandedness evidence by library',segments=['Sense','Antisense','Unassigned'],stage='qc'),
 F('Feature-assignment classes',segments=['Exonic','Intronic','Intergenic'],stage='qc'),
 B('Mapping-quality distributions','Mapping quality',stage='validation')],
'bulk.filtering':[
 X('Mean expression and detection','Supplied mean log count','Detection fraction',scale='fraction',stage='qc'),
 P('Gene-retention sensitivity','Declared count threshold','Retained fraction',scale='fraction',stage='qc'),
 F('Feature classes before and after filtering',['Before','After'],['Coding','Noncoding','Other'],feature_retention=True,stage='qc'),
 E('Effect stability across filter choices',['STAT1','IRF7','COL1A1','SRSF1'],stage='validation'),
 M('Detection support across groups',GENES,['Control','Treated'],'Detected donor fraction',scale='fraction',stage='qc')],
'bulk.normalization':[
 C('Library-size distributions by condition','Library size (millions)',scale='positive',stage='qc'),
 A('Paired donor RLE medians before/after normalization','Donor median relative log2 expression',rle_median=True,stage='qc'),
 C('Donor RLE medians after normalization','Donor median relative log2 expression',stage='qc'),
 X('Mean–variance transformation diagnostics','Supplied mean','Supplied variance',scale='positive',stage='qc'),
 E('Reference-feature normalization sensitivity',stage='validation')],
'bulk.batch':[
 F('Condition balance within each batch',['Batch A','Batch B','Batch C'],['Control','Treated'],batch_donors=True,stage='qc'),
 M('Complete covariate-associated variance',GENES,['Condition','Batch','Residual'],'Supplied variance fraction',scale='fraction',row_composition=True,stage='qc'),
 A('Donor RLE medians before/after batch adjustment','Donor median relative log2 expression',rle_median=True,stage='qc'),
 C('Interferon-program scores by batch','Supplied donor interferon score',series=['Batch A','Batch B','Batch C'],x_label='Batch',stage='interpretation'),
 E('Biological-effect preservation across choices',stage='validation')],
'bulk.differential':[
 P('Binned dispersion summaries and fitted trend','Supplied mean','Supplied dispersion',scale='positive',series=['Binned gene-wise summary','Frozen fitted trend'],stage='qc'),
 X('Cook influence across fitted expression','Supplied fitted log count','Supplied Cook distance',scale='positive',stage='qc'),
 E('Prespecified gene effects with uncertainty'),
 C('STAT1 expression in independent donors','Supplied log2 normalized STAT1 expression'),
 B('Complete raw probability distribution','Raw P value','Genes per supplied bin',series=['Primary contrast','Alternative contrast'],stage='validation'),
 X('Unshrunk versus shrunk effects','Unshrunk log2 fold change','Shrunk log2 fold change',series=['Primary contrast','Alternative contrast'],identity_reference=True,stage='validation'),
 E('Effect stability across prespecified models',stage='validation')],
'bulk.interaction':[
 M('Independent support for factorial cells',['Control early','Control late','Treated early','Treated late'],['Batch A','Batch B'],'Independent donor count',scale='count',stage='qc',factorial_repeated=True,note='The same independent donors are measured early and late; each time includes all twelve donors across two conditions and two batches.'),
 P('STAT1 condition-by-time predictions','Time (days)','Supplied log2 STAT1 expression',scale='positive',factorial_profile=True),
 E('Gene-wise interaction contrasts',x='Supplied log2 interaction contrast · interval',factorial_gene_effect=True,note='For each gene, the treatment-versus-control contrast at day 14 minus the contrast at day 0; supplied from the upstream time model.'),
 E('STAT1 simple effects at prespecified times',['Early treatment effect','Late treatment effect','Control time effect','Treated time effect'],explicit_effects=[-.70,-.17,.37,.90]),
 E('Interaction-model sensitivity',['Primary interaction','Adjusted interaction','Complete pairs','Restricted time'],explicit_effects=[.53,.50,.57,.51],stage='validation')],
'bulk.model_qc':[
 X('Fitted values and residual structure','Supplied fitted value','Supplied residual',stage='qc'),
 X('Quantile diagnostics with frozen reference','Theoretical quantile','Observed residual quantile',identity_reference=True,stage='qc'),
 C('Residual distributions by batch','Supplied residual',series=['Batch A','Batch B','Batch C'],x_label='Batch',stage='qc'),
 X('Leverage and observation influence','Supplied leverage','Supplied Cook distance',scale='positive',stage='qc'),
 E('Prespecified diagnostic sensitivity',['Primary fit','Robust fit','Influence sensitivity','Variance alternative'],stage='validation')],
'bulk.programs':[
 M('Program membership and complete gene support',GENES,SETS[:4],'Explicit membership',scale='fraction',binary=True,stage='qc'),
 C('Interferon-program distributions in independent donors','Supplied interferon-program score'),
 E('Program response estimates',SETS),
 P('Interferon-program progression across measured time','Time (days)','Supplied interferon-program score',stage='extension'),
 E('Interferon response in independent cohorts',['Discovery','Cohort B','Cohort C','Prespecified synthesis'],stage='validation',cohort_synthesis=True)],
'bulk.ora':[
 M('Selected queries and tested-universe coverage',SETS,['Query coverage','Annotation coverage'],'Supplied coverage fraction',scale='fraction',stage='qc'),
 E('Prespecified enrichment effect estimates',SETS,x='Supplied log odds ratio · supplied interval',stage='interpretation'),
 M('Complete term–gene support',SETS,GENES[:6],'Explicit annotation membership',scale='fraction',binary=True,stage='function'),
 F('Annotated and unannotated query genes',SETS,['Annotated','Unannotated'],stage='qc'),
 E('Enrichment stability across backgrounds',SETS,stage='validation'),
 M('Term overlap and redundancy context',SETS,SETS[:6],'Supplied overlap fraction',scale='fraction',stage='function')],
'bulk.gsea':[
 P('Complete ranked-universe statistic','Supplied gene rank','Supplied ranking statistic',series=['Primary contrast','Alternative contrast'],stage='qc'),
 F('Set coverage in the ranked universe',SETS,['Ranked','Absent'],stage='qc'),
 E('Normalized enrichment across contrasts',SETS,x='Supplied NES · upstream interval'),
 M('Leading-edge membership across selected terms',SETS,GENES[:6],'Explicit leading-edge membership',scale='fraction',binary=True,stage='function'),
 X('Enrichment concordance across rankings','NES · primary ranking','NES · alternative ranking',identity_reference=True,stage='validation'),
 M('Leading-edge overlap across pathways',SETS,SETS[:6],'Supplied overlap fraction',scale='fraction',stage='validation')],
'bulk.pathway_contrasts':[
 M('Tested pathway scope across contrasts',SETS,['Contrast A','Contrast B','Interaction'],'Explicit tested indicator',scale='fraction',binary=True,stage='qc'),
 E('Prespecified cross-contrast pathway effects',SETS,x='Supplied signed pathway effect · interval',comparison_contexts=['Contrast A','Contrast B']),
 M('Shared and contrast-specific leading edges',GENES,['Contrast A','Contrast B','Interaction'],'Explicit membership',scale='fraction',binary=True,stage='function'),
 X('Pathway concordance between contrasts','NES · contrast A','NES · contrast B',identity_reference=True),
 E('Pathway effects in an independent cohort',SETS,stage='validation')],
'bulk.gene_support':[
 M('Explicit pathway membership',GENES,SETS[:4],'Annotation membership',scale='fraction',binary=True,stage='qc'),
 E('Supporting-gene effect estimates'),
 C('STAT1 donor expression in the selected pathway','Supplied log2 STAT1 expression'),
 M('Gene effects across support contrasts',GENES,['Primary','Secondary','Replication'],'Supplied log2 fold change',stage='function'),
 E('Supporting-gene replication effects',stage='validation')],
'bulk.gsea_multitrack':[
 F('Ranked-universe coverage per selected set',SETS,['Present','Absent'],stage='qc'),
 P('Complete common ranking statistic','Supplied gene rank','Supplied ranking statistic',series=['Primary contrast','Alternative contrast'],stage='qc'),
 E('Selected pathways on a common NES scale',SETS,x='Supplied NES · upstream interval'),
 M('Leading-edge support across the common gene scope',GENES,SETS[:4],'Explicit leading-edge membership',scale='fraction',binary=True,stage='function'),
 X('Prespecified ranking sensitivity','NES · ranking A','NES · ranking B',identity_reference=True,stage='validation')],
'bulk.gsva':[
 F('Gene-set coverage in the measured universe',SETS,['Measured','Absent'],stage='qc'),
 C('Interferon-pathway scores in independent donors','Supplied interferon GSVA score'),
 E('Adjusted donor-level pathway effects',SETS),
 M('GSVA scores across independent donors',SETS,DONORS[:6],'Supplied GSVA score'),
 P('Interferon-pathway response across measured time','Time (days)','Supplied interferon GSVA score',stage='extension'),
 E('Independent-cohort pathway replication',SETS,stage='validation')],
'bulk.tf_activity':[
 F('Regulon target coverage',TFS,['Measured','Absent'],stage='qc'),
 C('STAT1 activity in independent donors','Supplied STAT1 activity score'),
 E('Adjusted TF activity effects',TFS),
 M('Signed TF–target evidence',TFS,GENES[:4],'Supplied signed regulatory prior',stage='function'),
 X('STAT1 activity and expression','Centered log2 STAT1 expression','Supplied STAT1 activity score',point_unit='independent donor',note='These are distinct donor-level channels; association is not direct binding.'),
 E('TF activity across independent cohorts',TFS,stage='validation')],
'bulk.deconvolution':[
 F('Reference coverage within cell identities',TYPES,['Covered','Uncovered'],stage='qc'),
 F('Complete donor mixture estimates',DONORS,TYPES),
 E('Donor-level compositional contrasts',TYPES,x='ln(Treated fraction / Control fraction) · 95% interval',note='Each identity compares its donor-level fraction in Treated versus Control on the natural-log ratio scale; no within-composition reference category.'),
 X('Frozen observed and reconstructed expression','Observed log expression','Reconstructed log expression',identity_reference=True,stage='qc'),
 E('Reference-choice sensitivity of mixture effects',TYPES,stage='validation')],
'bulk.splicing':[
 L('Physical exon and junction support',stage='qc'),
 C('STAT1 illustrative exon-event PSI','Supplied event PSI',scale='fraction'),
 E('Event-level differential splicing',x='Supplied delta PSI · interval',scale='fraction_effect'),
 F('Event coverage and missing donor support',GENES,['Observed','Not observed'],donor_denominator=True,stage='qc'),
 M('Splicing effects across event types',GENES,['SE','A5SS','A3SS'],'Supplied delta PSI',scale='fraction_effect'),
 E('Splicing-event replication',x='Supplied delta PSI · interval',scale='fraction_effect',stage='validation')],
'bulk.dtu':[
 F('Quantifiable transcript support',['STAT1-201','STAT1-202','STAT1-203','IRF7-201','IRF7-202','IRF7-203'],['Quantified','Ambiguous'],stage='qc'),
 F('Within-gene STAT1 transcript usage by donor',DONORS,['STAT1-201','STAT1-202','STAT1-203']),
 E('Prespecified STAT1 transcript-usage changes',['STAT1-201','STAT1-202','STAT1-203'],x='Supplied change in transcript fraction',scale='fraction_effect',explicit_effects=[-.3125,.3125,0],note='Three fictional STAT1 transcripts form the complete within-gene composition; supplied changes sum to zero.'),
 L('STAT1 transcript structure and junction support',series=['STAT1-201','STAT1-202','STAT1-203'],locus_kind='transcript_structure',stage='function'),
 M('Transcript and parent-gene effects',['STAT1-201','STAT1-202','STAT1-203'],['Gene expression','Transcript expression','Usage change'],'Supplied channel-specific standardized effect'),
 E('Transcript-version sensitivity',['STAT1-201','STAT1-202','STAT1-203'],scale='fraction_effect',explicit_effects=[-.3125,.3125,0],stage='validation')],
'bulk.timecourse':[
 M('Donor support across measured times',DONORS[:6],['Day 0','Day 3','Day 7'],'Explicit observation present',scale='fraction',binary=True,stage='qc'),
 A('Paired STAT1 donor response at two time points','Supplied log2 STAT1 expression'),
 P('STAT1 longitudinal predictions','Time (days)','Supplied log2 STAT1 expression',scale='positive'),
 E('Prespecified time-by-condition effects'),
 E('Within-donor model sensitivity',stage='validation')],
'bulk.replication':[
 F('Shared versus unavailable feature coverage',GENES,['Shared','Unavailable'],stage='qc'),
 X('Effect concordance across independent cohorts','Discovery effect','Replication effect',identity_reference=True),
 E('STAT1 independent-cohort effects and uncertainty',['Discovery','Cohort B','Cohort C','Prespecified synthesis'],cohort_synthesis=True),
 M('Direction and magnitude by cohort',GENES,['Discovery','Cohort B','Cohort C'],'Supplied log2 effect'),
 E('Leave-one-cohort sensitivity',['All declared cohorts','Exclude discovery','Exclude cohort B','Exclude cohort C'],explicit_effects=[.58,.595,.58,.565],stage='validation')],
'bulk.survival':[
 F('Endpoint and censoring audit',['Lower score','Higher score'],['Event','Censored'],stage='qc',participant_denominator=True),
 P('Frozen survival curves and confidence intervals','Follow-up time (months)','Survival probability',scale='survival',series=['Lower score','Higher score'],steps=True),
 M('People at risk over follow-up',['Lower score','Higher score'],['0 months','6 months','12 months','18 months'],'Supplied people at risk',scale='risk',stage='qc'),
 E('Adjusted outcome associations',x='Supplied hazard ratio · interval',scale='ratio'),
 P('Proportional-hazards diagnostic residuals','Follow-up time (months)','Supplied scaled residual',stage='qc'),
 P('Calibration from a held-out cohort','Supplied predicted risk','Supplied observed risk',scale='fraction',identity_reference=True,series=['Lower score','Higher score'],stage='validation')],
'bulk.ppi':[
 M('Interaction evidence by source',GENES,['Experimental','Curated','Predicted'],'Supplied evidence score',scale='fraction',stage='qc'),
 F('Protein mapping and coverage',GENES,['Mapped','Ambiguous','Absent'],stage='qc'),
 M('Complete selected interaction weights',GENES,GENES[:6],'Supplied PPI weight',scale='fraction'),
 E('Prespecified node-level response'),
 E('Network evidence across independent sources',stage='validation')],
'bulk.connectivity':[
 F('Query-signature coverage',GENES,['Measured','Absent'],stage='qc'),
 E('Connection scores with supplied uncertainty',['Compound A','Compound B','Compound C','Compound D'],x='Supplied connection score · interval'),
 M('Context and dose specificity',SETS,['Low dose','High dose','Other cell'],'Supplied connection score'),
 P('Prespecified dose-response summaries','Dose (declared unit)','Supplied connection score',stage='extension'),
 E('Signature reversal in independent contexts',SETS,stage='validation')],
'bulk.noncoding':[
 F('RNA-biotype annotation and mapping',GENES,['Mapped','Ambiguous','Absent'],stage='qc'),
 E('Prespecified noncoding RNA effects',['RNA001','RNA002','RNA003','RNA004','RNA005','RNA006']),
 C('RNA001 expression in independent donors','Supplied log2 RNA001 expression'),
 M('RNA–target evidence classes',['RNA001','RNA002','RNA003','RNA004'],['Coexpression','Binding prior','Perturbation'],'Supplied evidence indicator',scale='fraction',binary=True,stage='function'),
 E('Noncoding RNA response replication',stage='validation')],
'bulk.fusions':[
 M('Split-read and spanning-pair support',['Event A','Event B','Event C','Event D'],['Split reads','Spanning pairs'],'Supporting reads',scale='count',stage='qc'),
 L('Breakpoint-flanking transcript support',stage='qc'),
 F('Breakpoint read classes',['Event A','Event B','Event C','Event D'],['Unique','Multi-map','Low quality'],stage='qc'),
 M('Artifact and orthogonal evidence',['Event A','Event B','Event C','Event D'],['Unique mapping','In-frame','Orthogonal assay'],'Explicit evidence indicator',scale='fraction',binary=True),
 E('Event support in independent libraries',['Event A','Event B','Event C','Event D'],x='Supplied log support ratio · interval',stage='validation')],
'single_cell.design':[
 F('Capture contribution within independent donors',segments=['Capture A','Capture B','Capture C'],stage='qc'),
 M('Donor, condition and capture design',['Condition','Batch','Capture'],DONORS[:6],'Declared design code',categorical_design=True,stage='qc'),
 F('Donor balance within annotated identities',TYPES,['Control','Treated'],donor_denominator=True,stage='qc'),
 M('Replicate support across cell identities',TYPES,DONORS[:6],'Supplied cell count',scale='count',stage='qc'),
 E('Donor-level design sensitivity',TYPES,stage='validation')],
'single_cell.barcode':[
 P('Barcode rank across captures','Barcode rank','Supplied log UMI count',scale='positive',series=['Capture A','Capture B'],stage='qc'),
 F('Complete droplet-call categories',['Capture A','Capture B','Capture C'],['Cell','Ambiguous','Background'],stage='qc'),
 B('UMI distributions by droplet class','UMI count',series=['Cell','Ambiguous','Background'],stage='qc'),
 X('Genes and UMIs in declared droplets','Supplied log UMI count (log10)','Supplied log gene count (log10)',scale='positive',stage='qc'),
 P('Cell-call threshold sensitivity','Declared calling threshold','Retained fraction',scale='fraction',stage='validation')],
'single_cell.qc':[
 C('Independent-donor median detected genes','Supplied donor median genes',scale='positive',stage='qc'),
 C('Independent-donor mitochondrial summaries','Supplied donor median mitochondrial fraction',scale='fraction',stage='qc'),
 X('Cell complexity and mitochondrial burden','Supplied log UMI count','Mitochondrial fraction',scale='fraction',point_unit='cell nested within donor',stage='qc'),
 F('Cell-retention audit within each donor',segments=['Retained','Low complexity','High mitochondrial'],stage='qc'),
 M('Retained cell support by donor and identity',TYPES,DONORS[:6],'Supplied retained cells',scale='count',stage='qc'),
 E('Donor-response sensitivity to QC rules',TYPES,stage='validation')],
'single_cell.ambient_doublet':[
 C('Donor-level ambient contamination summaries','Supplied donor ambient fraction',scale='fraction',stage='qc'),
 X('Doublet score and droplet complexity','Supplied log UMI count','Supplied doublet score',scale='fraction',point_unit='droplet nested within donor',stage='qc'),
 F('Reviewed doublet calls by donor',segments=['Singlet','Ambiguous','Doublet'],stage='qc'),
 M('Ambient-profile marker support',GENES,['Soup','Retained cells','Corrected'],'Supplied expression score',stage='qc'),
 E('Biological-response sensitivity to correction',stage='validation')],
'single_cell.integration':[
 A('Donor batch-mixing scores before/after integration','Supplied donor median batch-mixing score',scale='fraction',stage='qc'),
 M('Batch mixing and biological conservation',['Batch mixing','Identity conservation','Donor conservation','Trajectory conservation'],['Before','After'],'Supplied score (0–1)',note='Supplied bounded metrics retain their distinct upstream definitions; this display does not combine them into one quality score.',scale='fraction',stage='qc'),
 F('Batch balance within biological identities',TYPES,['Batch A','Batch B','Batch C'],stage='qc'),
 E('Donor-level biological-effect preservation',TYPES),
 E('Integration-choice sensitivity',TYPES,stage='validation')],
'single_cell.hvg_pca':[
 X('Feature dispersion and mean expression','Supplied mean expression','Supplied dispersion',scale='positive',point_unit='gene',stage='qc'),
 P('Supplied explained variance by PC','Principal component','Variance fraction',scale='fraction',series=['Supplied PCs'],stage='qc'),
 M('Selected genes and principal-component loadings',GENES,['PC1','PC2','PC3'],'Supplied loading'),
 F('Feature support across donors',GENES,['Detected','Not detected'],donor_denominator=True,stage='qc'),
 E('Biological summaries across PC choices',TYPES,stage='validation')],
'single_cell.resolution':[
 M('Donor support at declared resolutions',TYPES,DONORS[:6],'Supplied cell count',scale='count',stage='qc'),
 F('Donor mixture within selected clusters',TYPES,['Donor A','Donor B','Donor C']),
 M('Marker specificity across candidate clusters',GENES,TYPES[:4],'Supplied marker score'),
 E('Supplied resampling stability',TYPES,x='Supplied stability · interval',scale='probability'),
 E('Independent annotation consistency',TYPES,stage='validation')],
'single_cell.annotation':[
 F('Reference-label coverage within donors',segments=['Mapped','Ambiguous','Unmapped'],stage='qc'),
 M('Positive and exclusion marker evidence',GENES,TYPES[:5],'Supplied marker score'),
 C('Donor-level annotation confidence','Supplied donor median confidence',scale='fraction'),
 M('Prediction uncertainty and review decisions',TYPES,['Model A','Model B','Reviewed'],'Supplied confidence',scale='fraction'),
 E('Identity support in independent cohorts',TYPES,stage='validation'),
 F('Discordant calls retained for review',TYPES,['Concordant','Discordant','Unknown'],stage='validation')],
'single_cell.subcluster':[
 M('Parent-lineage donor support',TYPES[:4],DONORS[:6],'Supplied cell count',scale='count',stage='qc'),
 M('Child-state positive and exclusion markers',GENES,['State A','State B','State C'],'Supplied marker score'),
 F('Child-state composition within donors',DONORS,['State A','State B','State C']),
 E('Donor-level child-state response',['State A','State B','State C']),
 E('Child-state reproducibility across choices',['State A','State B','State C'],stage='validation')],
'single_cell.markers':[
 M('Marker detection coverage',GENES,TYPES[:5],'Fraction of cells detected',scale='fraction',stage='qc'),
 M('Marker mean-expression specificity',GENES,TYPES[:5],'Centered mean expression',note='Supplied gene-centered mean expression by identity; negative centered values are not negative molecular counts.'),
 E('Donor-level marker effect estimates'),
 C('STAT1 marker expression in independent donors','Supplied pseudobulk log2 STAT1 expression'),
 E('Marker evidence in independent donors',stage='validation')],
'single_cell.composition':[
 F('Complete donor cell-identity composition',DONORS,TYPES,stage='qc'),
 C('T-cell fractions in independent donors','Supplied T-cell fraction',scale='fraction'),
 E('Prespecified compositional effects',TYPES,x='Supplied log-ratio effect · interval'),
 M('Identity support across donors',TYPES,DONORS[:6],'Supplied cell count',scale='count',stage='qc'),
 E('Composition sensitivity to identity definitions',TYPES,stage='validation')],
'single_cell.abundance':[
 M('Neighborhood support across donors',TYPES,DONORS[:6],'Supplied neighborhood cells',scale='count',stage='qc'),
 E('Donor-aware neighborhood abundance effects',TYPES,x='Supplied log abundance ratio · interval'),
 C('Selected neighborhood N01 donor fractions','Supplied N01 neighborhood fraction',scale='fraction'),
 X('Neighborhood size and abundance effect','Supplied neighborhood size','Supplied abundance effect',point_unit='overlapping neighborhood'),
 E('Neighborhood and model-choice sensitivity',TYPES,stage='validation')],
'single_cell.pseudobulk':[
 M('Cell support for each donor–identity aggregate',TYPES,DONORS[:6],'Supplied aggregate cells',scale='count',stage='qc'),
 C('Independent-donor library-size summaries','Aggregate library size (million UMIs)',scale='positive',stage='qc'),
 E('Donor-level differential-expression effects'),
 C('STAT1 pseudobulk expression in independent donors','Supplied pseudobulk log2 STAT1 expression'),
 M('Celltype-specific differential responses',GENES,TYPES[:5],'Supplied log2 fold change'),
 E('Donor-omission sensitivity of effects',comparison_contexts=['All donors','Omit D01'],stage='validation')],
'single_cell.multi_contrast':[
 M('Independent support across contrast families',TYPES,['Contrast A','Contrast B','Interaction'],'Independent donor count',scale='count',stage='qc'),
 M('Complete signed effect atlas',GENES,TYPES[:5],'Supplied log2 fold change'),
 E('Prespecified identity-by-condition effects',TYPES),
 X('Effect concordance between contrasts','Effect · contrast A','Effect · contrast B',identity_reference=True),
 E('Cross-contrast replication effects',TYPES,stage='validation')],
'single_cell.pathways':[
 F('Measured gene-set support in T-cell aggregates',SETS,['Present','Absent'],stage='qc'),
 M('Celltype-specific normalized enrichment',SETS,TYPES[:5],'Supplied NES'),
 C('Interferon scores in T-cell donor aggregates','Supplied donor interferon-pathway score'),
 E('Donor-level pathway responses',SETS),
 M('Celltype-specific leading-edge support',GENES,TYPES[:5],'Explicit leading-edge membership',scale='fraction',binary=True,stage='function'),
 E('Pathway replication in independent donors',SETS,stage='validation')],
'single_cell.gene_support':[
 M('Pathway membership of selected supporting genes',GENES,SETS[:4],'Explicit membership',scale='fraction',binary=True,stage='qc',gene_membership=True),
 E('Supporting-gene donor-level effects'),
 C('STAT1 pseudobulk expression supporting the pathway','Supplied log2 STAT1 expression'),
 M('Support direction across identities',GENES,TYPES[:5],'Supplied log2 fold change',stage='function'),
 E('Supporting-gene external replication',stage='validation')],
'single_cell.states':[
 F('State-program gene coverage',SETS,['Measured','Absent'],stage='qc'),
 C('Interferon state scores in independent donors','Supplied interferon-state score'),
 E('Donor-level state-program effects',SETS),
 M('State, stress and cycle contexts',SETS,TYPES[:5],'Supplied state score'),
 E('State effects after prespecified cycle adjustment',SETS,stage='validation')],
'single_cell.trajectory':[
 M('Donor support across branches',DONORS[:6],['Root','Branch A','Branch B'],'Supplied cell count',scale='count',stage='qc'),
 P('Interferon program along fixed branches','Supplied pseudotime','Supplied interferon-program score',series=['Branch A','Branch B']),
 C('Branch A occupancy in independent donors','Supplied Branch A fraction',scale='fraction'),
 E('Branch-specific donor-level effects',GENES),
 M('Ordered expression on fixed pseudotime bins',GENES,['Bin 1','Bin 2','Bin 3','Bin 4'],'Supplied scaled expression',stage='function'),
 E('Root and branch-choice sensitivity',GENES,stage='validation')],
'single_cell.velocity':[
 X('STAT1 spliced–unspliced phase support','Supplied normalized spliced counts','Supplied normalized unspliced counts',scale='positive',point_unit='cell nested within donor',stage='qc'),
 C('Donor-level velocity confidence','Supplied donor median confidence',scale='fraction',stage='qc'),
 M('Velocity model support by gene',GENES,['Fit quality','Layer coverage','Phase support'],'Supplied diagnostic',scale='fraction',stage='qc'),
 P('STAT1 response along supplied latent time','Supplied latent time','Supplied normalized STAT1 response'),
 E('Direction stability across model choices',GENES,stage='validation')],
'single_cell.communication':[
 M('Ligand and receptor expression support',LR_GENES,TYPES[:5],'Fraction detected',scale='fraction',stage='qc'),
 M('Outgoing pathway contributions',SIGNALS,TYPES[:5],'Supplied outgoing contribution',scale='fraction'),
 M('Incoming pathway contributions',SIGNALS,TYPES[:5],'Supplied incoming contribution',scale='fraction'),
 E('Donor-aware signaling contrasts',SIGNALS,x='Supplied signaling contrast · interval'),
 X('Changes in outgoing and incoming roles','Supplied outgoing change','Supplied incoming change',point_unit='declared sender or receiver identity',labels=TYPES,series=['Treated minus Control'],identity_points=True,show_labels=True,zero_reference=True),
 F('Ligand–receptor support across donors',LR,['Supported','Not supported'],stage='qc',donor_denominator=True),
 E('Signaling effects in an independent cohort',SIGNALS,stage='validation')],
'single_cell.ligand_target':[
 F('Prior coverage in the receiver context',GENES,['Covered','Absent'],stage='qc'),
 E('Prespecified ligand-activity contrasts',LIGANDS),
 M('Ligand-to-target potential',GENES,LIGANDS[:4],'Supplied target potential',scale='fraction',stage='function'),
 E('Receiver target-gene differential response',x='Receiver gene log2 fold change · supplied 95% interval'),
 E('Ligand-to-target evidence across prior choices',LIGANDS,stage='validation')],
'single_cell.regulons':[
 F('Motif and target coverage by regulon',TFS,['Covered','Absent'],stage='qc'),
 C('STAT1 regulon activity in independent donors','Supplied STAT1 AUCell activity',scale='fraction'),
 E('Donor-level regulon activity effects',TFS),
 M('Regulon specificity across identities',TFS,TYPES[:5],'Supplied specificity',scale='fraction'),
 M('Motif support and signed target priors',TFS,GENES[:4],'Supplied regulatory prior',stage='function'),
 E('Regulon effects in independent donors',TFS,stage='validation')],
'single_cell.cnv':[
 M('Reference-normal support by donor',TYPES,DONORS[:6],'Supplied reference cells',scale='count',stage='qc'),
 P('Genomically ordered CNV summaries','Ordered bin index · fictional reference','Supplied log2 relative CNV',series=['Reference','Clone A','Clone B','Clone C'],reference_zero=True),
 F('Clone composition within each donor',DONORS,['Reference','Clone A','Clone B','Clone C']),
 C('Donor-level CNV burden summaries','Supplied CNV burden',scale='positive'),
 E('Clone-associated donor effects',['Clone A','Clone B','Clone C','Reference']),
 M('Orthogonal genomic support by chromosome',['chr1','chr2','chr3','chr4'],['RNA inferred','DNA assay','Reviewed'],'Explicit support indicator',scale='fraction',binary=True,stage='validation')],
'single_cell.vdj':[
 F('VDJ quality and productive-chain support',DONORS,['Productive','Nonproductive','Unassigned'],stage='qc'),
 B('Frozen clone-size distributions','Clonotype size'),
 F('Clone expansion classes within donors',DONORS,['Singleton','Small clone','Expanded clone']),
 M('Clonotype sharing across sampled compartments',['CD4 T','CD8 T','B cells','Plasma cells'],['Blood','Tissue','Follow-up'],'Supplied overlap fraction',scale='fraction'),
 E('Donor-level diversity contrasts',['CD4 T','CD8 T','B cells','Plasma cells'],x='Supplied diversity contrast · interval'),
 A('Paired clonotype summaries over follow-up','Supplied Shannon diversity score',note='Paired donor Shannon diversity in natural-log units; nonnegative fictional supplied values, not re-estimated during plotting.'),
 E('Repertoire findings in independent donors',['CD4 T','CD8 T','B cells','Plasma cells'],stage='validation')],
'single_cell.splicing':[
 L('T-cell STAT1 E01 physical junction support',stage='qc'),
 M('Event support across donors and identities',GENES,TYPES[:5],'Fraction of supported donors',scale='fraction',stage='qc'),
 C('STAT1 event PSI in T-cell donor aggregates','Supplied event PSI',scale='fraction'),
 E('T-cell donor differential splicing',x='Supplied delta PSI · interval',scale='fraction_effect'),
 M('Splicing-event effects across identities',GENES,TYPES[:5],'Supplied delta PSI',scale='fraction_effect'),
 E('T-cell event replication',x='Supplied delta PSI · interval',scale='fraction_effect',stage='validation')],
'single_cell.perturbseq':[
 F('Complete guide assignment by replicate',DONORS,['Single guide','Multiple','Unassigned'],stage='qc'),
 M('Guide support across donors',GENES,DONORS[:6],'Supplied guide-assigned cells',scale='count',stage='qc'),
 E('STAT1 response by guide and control',['NTC-01','Safe-target-01','STAT1-g01','STAT1-g02','IRF7-g01','IRF7-g02'],explicit_effects=[-.01,.02,-.5,-.45,.36,.41]),
 M('Perturbation program responses',SETS,['Target A','Target B','Control'],'Supplied response'),
 E('Gene responses across independent guide designs',comparison_contexts=['Guide A','Guide B'],stage='validation'),
 E('Perturbation response in independent donors',stage='validation')],
'single_cell.replication':[
 F('Cross-cohort ontology and feature coverage',TYPES,['Matched','Ambiguous','Unavailable'],stage='qc'),
 X('T-cell gene-effect concordance','Discovery effect','Replication effect',identity_reference=True,series=['Common gene scope'],point_unit='gene',named_points=True,annotate=['STAT1','IRF7','COL1A1']),
 E('Independent-cohort donor-level effects',TYPES),
 M('Label-transfer confidence and review',TYPES,['Model A','Model B','Reviewed'],'Supplied confidence',scale='fraction',stage='qc'),
 E('Leave-one-cohort stability',TYPES,comparison_contexts=['Full cohorts','Omit cohort A'],independent_cohorts=False,stage='validation')],
'single_cell.spatial':[
 M('Section and donor support by region',TYPES,DONORS[:6],'Supplied region spots',scale='count',stage='qc'),
 C('Interferon scores in donor region R01','Supplied regional interferon score'),
 E('Donor-aware region contrasts',TYPES),
 M('Region-program evidence',SETS,['R01','R02','R03','R04','R05'],'Supplied region score',stage='function'),
 X('Measured-distance and neighborhood summaries','Supplied tissue distance (µm)','Supplied neighborhood statistic',point_unit='spatial neighborhood nested within section'),
 E('Section and registration-choice sensitivity',TYPES,stage='validation')],
'single_cell.multiome':[
 F('Paired-modality support within donors',DONORS,['Paired','RNA only','ATAC only'],stage='qc'),
 M('RNA and ATAC quality channels',TYPES,['RNA detection','TSS enrichment','Peak fraction'],'Supplied standardized diagnostic',stage='qc'),
 M('Motif and RNA response evidence',GENES,['RNA','Motif activity','Accessibility'],'Supplied standardized effect'),
 E('Prespecified peak–gene association estimates',GENES,x='Peak–gene regression coefficient · supplied 95% interval'),
 L('Frozen peak and gene-locus evidence',stage='function',locus_kind='peak_link'),
 E('Regulatory association in independent donors',stage='validation')]
}

# A common geometry is never permission to erase the method's estimand/unit.
EFFECT_UNITS={
'bulk.design':'STAT1 log2 fold change', 'bulk.filtering':'Log2 fold change',
'bulk.normalization':'Log2 fold change', 'bulk.batch':'Log2 fold change',
'bulk.differential':'Log2 fold change', 'bulk.model_qc':'STAT1 log2 fold change',
'bulk.interaction':'STAT1 log2 response contrast', 'bulk.ora':'Log enrichment odds ratio',
'bulk.programs':'Donor program-score difference', 'bulk.pathway_contrasts':'Signed pathway-score difference',
'bulk.gene_support':'Log2 fold change', 'bulk.gsva':'Donor GSVA-score difference',
'bulk.tf_activity':'Donor TF-activity score difference', 'bulk.deconvolution':'ln(Treated fraction / Control fraction)',
'bulk.splicing':'Delta PSI', 'bulk.dtu':'Transcript-fraction change',
'bulk.timecourse':'Log2 expression change', 'bulk.replication':'Log2 fold change',
'bulk.ppi':'Node-expression log2 fold change', 'bulk.connectivity':'Connection-score difference',
'bulk.noncoding':'Noncoding-RNA log2 fold change',
'single_cell.design':'STAT1 donor log2 fold change',
'single_cell.qc':'STAT1 donor log2 fold change',
'single_cell.ambient_doublet':'Log2 fold change',
'single_cell.integration':'STAT1 donor log2 fold change',
'single_cell.hvg_pca':'STAT1 donor log2 fold change',
'single_cell.resolution':'Label-agreement fraction difference',
'single_cell.annotation':'Label-support fraction difference',
'single_cell.subcluster':'Child-state log abundance ratio',
'single_cell.markers':'Donor marker log2 fold change',
'single_cell.composition':'ln(Treated fraction / Control fraction)',
'single_cell.abundance':'Log neighborhood abundance ratio',
'single_cell.pseudobulk':'Donor log2 fold change',
'single_cell.multi_contrast':'STAT1 donor log2 fold change',
'single_cell.pathways':'Donor pathway-score difference',
'single_cell.gene_support':'Donor log2 fold change',
'single_cell.states':'Donor state-score difference',
'single_cell.trajectory':'Branch-associated log2 fold change',
'single_cell.velocity':'Velocity-direction agreement difference',
'single_cell.communication':'Donor signaling-score difference',
'single_cell.ligand_target':'Donor ligand-activity difference',
'single_cell.regulons':'Donor AUCell-activity difference',
'single_cell.cnv':'Clone log abundance ratio',
'single_cell.vdj':'Shannon-diversity difference',
'single_cell.splicing':'Delta PSI',
'single_cell.perturbseq':'Perturbation-response log2 fold change',
'single_cell.replication':'STAT1 donor log2 fold change',
'single_cell.spatial':'Regional program-score difference',
'single_cell.multiome':'Peak–gene coefficient difference'}
for _chapter,_recipes in RECIPES.items():
    for _r in _recipes:
        if _r['kind']=='effects' and _chapter in ['bulk.ora','bulk.gsea','bulk.gsea_multitrack','bulk.pathway_contrasts']:
            _r['n_label']='Upstream donor n'
        if _r['kind']=='effects' and _r['x_label']=='Effect · supplied 95% interval':
            _r['x_label']=EFFECT_UNITS[_chapter]+' · supplied 95% interval'
            if _chapter in ['bulk.dtu','single_cell.resolution','single_cell.annotation','single_cell.velocity','single_cell.splicing','single_cell.regulons']:_r['scale']='fraction_effect'
        if _chapter=='bulk.noncoding' and _r.get('labels')==GENES:_r['labels']=['RNA001','RNA002','RNA003','RNA004','RNA005','RNA006','RNA007','RNA008','RNA009']
        if _chapter=='single_cell.abundance' and _r.get('labels')==TYPES:_r['labels']=['N'+str(i).zfill(2) for i in range(1,13)]
        if _chapter=='single_cell.splicing' and _r.get('labels')==GENES:_r['labels']=[g+' · E'+str(i+1).zfill(2) for i,g in enumerate(GENES)]
        if _chapter=='single_cell.spatial' and _r.get('labels')==TYPES:_r['labels']=['R'+str(i).zfill(2) for i in range(1,13)]
        if _chapter=='single_cell.multiome' and _r['kind']=='effects':_r['labels']=['P'+str(i+1).zfill(2)+' → '+g for i,g in enumerate(GENES)]

def validate_recipes():
    for chapter,rows in RECIPES.items():
        assert 5<=len(rows)<=9 and len({r['title'] for r in rows})==len(rows),chapter
        assert any(r['stage']=='qc' for r in rows) and any(r['stage']=='validation' for r in rows),chapter
        assert len({r['kind'] for r in rows})>=3,chapter
        assert not any(r['kind']=='effects' and r['x_label'].startswith('Effect ·') for r in rows),chapter
    return len(RECIPES)
