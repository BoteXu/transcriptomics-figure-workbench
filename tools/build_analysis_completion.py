"""Bounded synthetic drawing fixtures for missing network/program companions.

These are authored display coordinates and summaries, not simulated analyses.
All program/cloud/interval values are explicitly fictional upstream fixtures.
"""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/transcriptomics-figure-workbench'
sys.path.insert(0, str(SKILL / 'scripts'))


def build(out):
    import numpy as np
    import pandas as pd
    from figure_core import table_bytes
    from figure_workbench.contracts import read_json
    out.mkdir(parents=True, exist_ok=False)
    old = SKILL / 'assets/wgcna-gallery'
    base = read_json(old / 'WGCNA_ModuleTrait/input/example.spec.json')
    context = copy.deepcopy(base['parameters']['context'])
    context.update(module_version='Illustrative modules v0.9.7', source_version='Fictional frozen display inputs v0.9.7; no WGCNA backend')
    program_context = dict(independent_unit='fictional donors', independent_n=24,
                           method_version='Authored display summaries v0.9.7',
                           source_version='Synthetic result fixtures; no analysis backend',
                           selection='Complete explicitly selected display scope')
    records = []
    base['theme']['group_slots'].update({x: i for i, x in enumerate(['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'Grey'])})
    base['theme']['group_slots'].update({'Control': 0, 'Treated': 1, 'Branch A': 0, 'Branch B': 1})

    def add(key, d, mode, title, chapters, definition, stage, ctx=None, **params):
        folder = out / key; folder.mkdir()
        s = copy.deepcopy(base); raw = table_bytes(d); (folder / 'example.tsv').write_bytes(raw)
        fixture_colors=['#218C8D','#D8795B','#5676A5','#A795BD','#C8A34E','#6EA98C','#BC7E9C','#708694','#A4A757','#8471AD','#BA9472','#7BAFBA']
        if 'module' in d:
            named=list(dict.fromkeys(d.module.dropna()))
            for i,name in enumerate(named):
                if name not in s['theme']['group_slots'] and name not in s['theme'].get('category_colors',{}):
                    if i>=len(fixture_colors):raise ValueError('Author an explicit larger fixture palette')
                    s['theme'].setdefault('category_colors',{})[name]=fixture_colors[i]
        s.update(figure_id=key, renderer='figure_coexpression_evidence.plot_coexpression_evidence',
                 parameters=dict(mode=mode, title=title, context=ctx or context, definition=definition, **params))
        s['input'].update(path='example.tsv', sha256=hashlib.sha256(raw).hexdigest(),
                          numeric_columns=[c for c in d if pd.api.types.is_numeric_dtype(d[c])])
        s['appearance'].update(label_pt=12, tick_pt=11, note_pt=11)
        s['export'].update(target_width_mm=297, minimum_text_pt=7.5, raster_dpi=300, readability_policy='block')
        s['provenance'].update(source='Fictional method display fixtures v0.9.7', model='No network, statistical test, interval, density, layout or analysis fit',
                               interpretation_limit='Software drawing examples only; not biological evidence', synthetic=True)
        (folder / 'example.spec.json').write_text(json.dumps(s, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
        records.append(dict(id=key, spec=key + '/example.spec.json', chapters=chapters,
                            stage=stage, family=mode, variant=False))
        return s

    both = ['bulk.wgcna', 'single_cell.hdwgcna']
    modules = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
    add('Modules_GenePartition', pd.DataFrame(dict(module=modules + ['Grey'], genes=[72,105,180,240,330,480,93], assigned=[1]*6+[0])),
        'module_size', 'Module composition and unassigned genes', both,
        'Complete fictional disjoint gene partition. Grey genes are unassigned, not an inferred module.', 'network')
    nodes = []; edges = []
    for j, module in enumerate(modules[:3]):
        cx = [-2.2, 2.2, 0][j]; cy = [1, 1, -2][j]
        for i in range(9):
            angle = 2 * np.pi * i / 8
            nodes.append(dict(record_type='node', gene=module + '_G' + str(i+1), module=module,
                              x=float(cx if i == 0 else cx + np.cos(angle)), y=float(cy if i == 0 else cy + .85 * np.sin(angle)), kME=float(.96 - .055*i)))
            if i:
                edges.append(dict(record_type='edge', source=module+'_G1', target=module+'_G'+str(i+1), weight=float(.85-.06*i)))
                if i < 8: edges.append(dict(record_type='edge', source=module+'_G'+str(i+1), target=module+'_G'+str(i+2), weight=.22))
    edges.extend([dict(record_type='edge', source='M1_G5', target='M2_G2', weight=.12), dict(record_type='edge', source='M2_G7', target='M3_G3', weight=.10)])
    network = pd.DataFrame(nodes+edges)
    add('Hubs_CoexpressionNeighborhoods', network, 'hub_network', 'Coexpression neighborhoods and hub candidates', both,
        'Frozen fictional TOM edges > 0.05, complete prespecified 27-node subgraph; fixed display coordinates. kME is supplied; no hub selection.', 'interpretation',
        label_genes=['M1_G1','M1_G3','M2_G1','M2_G3','M3_G1','M3_G3'], edge_semantics='Undirected TOM coexpression weight; not physical binding', directed=False)
    counts = [[60,8,4,0],[5,80,10,10],[8,12,130,30],[0,8,22,210]]
    add('Modules_CrossCohortOverlap', pd.DataFrame([dict(reference=modules[i], query='Q'+str(j+1), count=counts[i][j]) for i in range(4) for j in range(4)]),
        'module_overlap', 'Shared genes across two supplied module partitions', both,
        'Complete four-by-four intersection table on the same 597 selected genes; zero is explicit. Flow width is gene count, not Jaccard or significance.', 'validation')
    connectivity = pd.DataFrame([dict(gene='G'+str(i+1).zfill(2), module=modules[i//4], k_reference=20+4*i,
                                     k_query=20+4*i+(-11+i*2), estimate=-11+i*2, lower=-14+i*2, upper=-8+i*2) for i in range(12)])
    add('Connectivity_ReferenceAndChange', connectivity, 'connectivity_change', 'Connectivity change on identical selected genes', both,
        'Upstream degree difference query minus reference; illustrative 95% intervals supplied independently of drawing. Same tested genes, network definition and sample scope.', 'validation',
        value_label='Query − reference degree · supplied 95% interval')
    effects = pd.DataFrame([dict(module=m, contrast=c, estimate=float(.65*np.cos(i*.9+j)), lower=float(.65*np.cos(i*.9+j)-.19), upper=float(.65*np.cos(i*.9+j)+.19), q=[.004,.018,.13,.31,.042,.22][i], n=24) for j,c in enumerate(['Treated − control','Severity · per supplied unit']) for i,m in enumerate(modules)])
    add('Eigengenes_DonorContrasts', effects, 'module_effects', 'Donor-level module effects across prespecified contrasts', both,
        'Fictional donor-level adjusted differences with upstream 95% confidence intervals and BH q over the supplied module/contrast family; oriented module eigengenes.', 'interpretation',
        value_label='Oriented eigengene difference · supplied 95% CI', columns=2)
    terms=['Interferon response','Extracellular matrix','RNA processing','Mitochondrial translation','Cell-cycle regulation']
    enrich=pd.DataFrame([dict(module=m,term=term,overlap=5+(i*3+j*2)%22,query_size=72+i*25,term_size=120+j*24,universe=12000,q=float(10**(-1-((i+j*2)%6)*.52))) for i,m in enumerate(modules[:4]) for j,term in enumerate(terms)])
    add('Modules_FunctionAndGeneSupport', enrich, 'module_enrichment', 'Module functions with explicit supporting gene counts', both,
        'Selected complete fictional module/term scope; ORA using a 12000-gene tested background. BH q supplied; point area encodes overlap/query size, numeral encodes actual overlap. No test recomputation.', 'function')
    expression=[]
    for j,m in enumerate(modules[:2]):
        for u in range(16):
            unit='D'+str(u+1).zfill(2); group='Control' if u<8 else 'Treated'
            for g in range(7):
                expression.append(dict(record_type='gene',module=m,unit=unit,gene='G'+str(j*7+g+1).zfill(2),group=group,value=float(1.3*np.cos((u/8)*np.pi+j*.5)+.5*np.sin(g+u*.8))))
            expression.append(dict(record_type='eigengene',module=m,unit=unit,gene='ME',group=group,value=float(.5*np.cos((u/8)*np.pi+j*.5))))
    add('Modules_ExpressionAndEigengenes',pd.DataFrame(expression),'module_expression','Selected module genes aligned with donor eigengenes',both,
        'Seven prespecified genes per module, supplied row Z scores and separately supplied oriented eigengenes; identical 16 donor columns and group identities. No clustering or scaling.', 'interpretation',
        columns=2,value_limits=[-2,2],value_label='Supplied gene row Z score')
    topo=[];leaves=['G'+str(i+1).zfill(3) for i in range(24)]
    for i,gene in enumerate(leaves):topo.append(dict(record_type='leaf',node_id=gene,module=modules[i//8],dynamic_module=modules[i//8]))
    active=leaves[:];level=0;counter=0
    while len(active)>1:
        level+=1;nxt=[]
        for i in range(0,len(active),2):
            if i+1==len(active):nxt.append(active[i]);continue
            counter+=1;node='Merge'+str(counter);topo.append(dict(record_type='merge',node_id=node,left=active[i],right=active[i+1],height=level*.15));nxt.append(node)
        active=nxt
    topo.extend(dict(record_type='matrix',a=a,b=b,value=1. if i==j else float(.48*np.exp(-abs(i-j)/6)+(.36 if i//8==j//8 else .02))) for i,a in enumerate(leaves) for j,b in enumerate(leaves))
    add('TOM_AlignedHierarchy',pd.DataFrame(topo),'topology','Topological overlap with frozen gene hierarchy and modules',both,
        'Complete fictional symmetric TOM, frozen 24-leaf merge table and module partition. Same genes and supplied order across hierarchy, tracks and matrix. No TOM computation or clustering.', 'network')
    dynamic=pd.DataFrame([dict(module=m,branch=branch,position=float(t),estimate=float(np.sin(t*3+j*.6)+sign*.4*t),lower=float(np.sin(t*3+j*.6)+sign*.4*t-.16),upper=float(np.sin(t*3+j*.6)+sign*.4*t+.16),n=24) for j,m in enumerate(modules[:4]) for branch,sign in [('Branch A',1),('Branch B',-1)] for t in np.linspace(0,1,18)])
    add('Modules_BranchDynamics',dynamic,'module_dynamics','Module programs along supplied branches',both+['single_cell.trajectory'],
        'Frozen branch progression positions, module curves and donor-aware upstream 95% intervals; these are authored drawing fixtures, not fitted trajectories.', 'extension',columns=2,value_label='Oriented module activity · supplied 95% CI')
    stability=pd.DataFrame([dict(module=m,setting=s,estimate=float(.91-.06*i-.028*j),lower=float(.86-.06*i-.028*j),upper=float(.96-.06*i-.028*j),n_resamples=200) for i,m in enumerate(modules[:4]) for j,s in enumerate(['Baseline','Power − 1','Power + 1','Merge 0.15','Merge 0.25'])])
    add('Modules_SensitivityAndStability',stability,'stability','Module stability across prespecified network settings',both,
        'Supplied bootstrap matched-membership Jaccard and 95% intervals from 200 resamples per setting. No resampling, rematching, optimal-setting choice or inference during drawing.', 'validation', value_label='Matched-membership Jaccard · supplied 95% interval')
    trait=pd.DataFrame([dict(module=m,unit='D'+str(u+1).zfill(2),group='Control' if u<12 else 'Treated',trait=float(20+u*1.7),eigengene=float(.04*u*np.cos(j)+.3*np.sin(u*1.8+j))) for j,m in enumerate(modules[:3]) for u in range(24)])
    add('Eigengenes_ContinuousTrait',trait,'trait_scatter','Continuous trait relationships at the donor level',both,
        'Complete 24 donor values; continuous fictional age variable, exact supplied oriented eigengenes and group identities. No regression line, correlation or significance fitted.', 'interpretation',value_label='Fictional age / years')
    projection=pd.DataFrame([dict(module=m,cohort='Validation A',retained_genes=60+i*16,tested_genes=72+i*25,estimate=.72-i*.13,lower=.54-i*.13,upper=.88-i*.13,n=20) for i,m in enumerate(modules[:4])])
    add('Modules_ProjectionSupport',projection,'projection','External module projection: coverage and concordance',both+['bulk.replication','single_cell.replication'],
        'Frozen reference gene set, query retention and independent donor-level score concordance with supplied 95% intervals. Projection concordance is not module preservation or topology reconstruction.', 'validation',value_label='Independent score concordance r · supplied 95% CI')
    attrs=['Density','Connectivity','Coherence','Density retention','Topology retention','Degree concordance','Weight concordance']
    probabilities=pd.DataFrame([dict(module=m,attribute=a,probability=float(10**(-.2-(i+j*2)%8*.47)),permutations=5000) for i,m in enumerate(modules[:5]) for j,a in enumerate(attrs)])
    add('Preservation_Attributes',probabilities,'preservation_attributes','Preservation evidence for each network attribute',both,
        'Seven fictional NetRep-style attribute-wise adjusted probabilities, 5000 declared upstream permutations; correction family is all 35 displayed tests. No averaging p values; these probabilities are not WGCNA Zsummary.', 'validation')

    def profiles(names, unit_count=24, proportion=False):
        d=[]; clouds={}
        for j,m in enumerate(names):
            clouds[m]={}
            for k,group in enumerate(['Control','Treated']):
                center=(.35+.24*k+.03*j) if proportion else (-.38 if k==0 else .38)*np.cos(j*.7)
                spread=.10 if proportion else .30
                vals=[center+spread*np.sin(u*1.7+j*.8) for u in range(unit_count//2)]
                for u,v in enumerate(vals):d.append(dict(module=m,unit='D'+str(u+1+k*(unit_count//2)).zfill(2),group=group,value=float(v)))
                grid=np.linspace(min(vals)-spread*.3,max(vals)+spread*.3,55)
                # An authored bell shape, not a KDE estimated from these values.
                width=np.exp(-.5*((grid-center)/(spread*.7))**2)
                clouds[m][group]=dict(grid=grid.tolist(),width=width.tolist(),n=len(vals),definition='Authored synthetic bell geometry with known center/spread, not an estimated density or biological distribution')
        return pd.DataFrame(d),clouds
    prof,cloud=profiles(modules[:4])
    add('Eigengenes_DonorRainclouds',prof,'program_profile','Donor-level eigengenes: distributions and individual units',both,
        'Frozen donor eigengenes and explicitly authored synthetic cloud geometries; all observed independent units retained. White box summarizes observed values; clouds are display fixtures.', 'interpretation',columns=2,cloud_shapes=cloud,value_label='Supplied oriented eigengene')
    score_names=['Interferon response','Matrix remodeling','Oxidative phosphorylation','Cell-cycle program']
    scores,score_cloud=profiles(score_names)
    add('GSVA_DonorScoreDistributions',scores,'program_profile','Pathway score distributions at the donor level',['bulk.gsva','single_cell.pathways'],
        'Frozen fictional GSVA-like continuous scores and explicitly authored cloud geometries; score method and version belong in real upstream provenance. No GSVA algorithm executed.', 'interpretation',ctx=program_context,columns=2,cloud_shapes=score_cloud,value_label='Supplied pathway score')
    ge=effects.copy();ge['module']=['Interferon signaling','Matrix remodeling','Oxidative metabolism','Cell cycle','RNA processing','Stress response']*2
    add('GSVA_AdjustedPathwayContrasts',ge,'module_effects','Adjusted pathway score effects across contrasts',['bulk.gsva','bulk.pathway_contrasts','single_cell.pathways'],
        'Supplied adjusted continuous pathway-score differences, upstream 95% CI and BH q over the displayed family; not ORA or GSEA NES.', 'interpretation',ctx=program_context,columns=2,value_label='Pathway score difference · supplied 95% CI')
    tf=effects.copy();tf['module']=['IRF1','STAT1','RELA','JUN','ATF4','MYC']*2
    add('TF_ActivityContrasts',tf,'module_effects','Transcription-factor activity effects and uncertainty',['bulk.tf_activity','single_cell.regulons'],
        'Frozen fictional footprint activity differences with upstream donor-level 95% intervals; TF activity is not TF gene expression or physical binding.', 'interpretation',ctx=program_context,columns=2,value_label='Footprint activity difference · supplied 95% CI')
    tfnet=network.copy();tfnet['gene']=tfnet.gene.map(lambda x: x.replace('M1_G1','IRF1').replace('M2_G1','STAT1').replace('M3_G1','RELA') if isinstance(x,str) else x)
    for col in ['source','target']:tfnet[col]=tfnet[col].map(lambda x:x.replace('M1_G1','IRF1').replace('M2_G1','STAT1').replace('M3_G1','RELA') if isinstance(x,str) else x)
    add('Regulons_DirectedTargetEvidence',tfnet,'hub_network','Regulon target support with explicit edge direction',['bulk.tf_activity','single_cell.regulons','single_cell.ligand_target'],
        'Prespecified directed fictional TF-target evidence graph with supplied support weights; fixed display coordinates. Candidate regulatory edges do not establish causality.', 'extension',ctx=program_context,
        label_genes=['IRF1','STAT1','RELA'],edge_semantics='Directed TF-target candidate evidence; no causal inference',directed=True)
    add('PPI_SelectedEvidenceNetwork',network,'hub_network','Selected protein interactions and module context',['bulk.ppi','single_cell.hdwgcna'],
        'Fictional prespecified undirected PPI evidence edges, upstream confidence scores and module membership; node area encodes separately supplied |kME|, not PPI degree. No database retrieval or inferred binding.', 'extension',
        label_genes=['M1_G1','M2_G1','M3_G1'],edge_semantics='Undirected fictional PPI support; differs from coexpression',directed=False)
    psi,psi_cloud=profiles(['Exon inclusion A','Junction usage B','Intron retention C'],proportion=True)
    add('Splicing_DonorPSIDistributions',psi,'program_profile','Splicing events: donor-level inclusion distributions',['bulk.splicing','single_cell.splicing'],
        'Frozen donor-level PSI on [0,1], unrelated independent groups, authored cloud geometry; no event calling, smoothing, pairing or differential splicing test.', 'interpretation',ctx=program_context,
        cloud_shapes=psi_cloud,value_label='Supplied percent-spliced-in / fraction',value_limits=[0,1])
    td=dynamic.copy();td['module']=td.module.map(dict(zip(modules[:4],score_names)))
    add('Trajectory_ProgramProgression',td,'module_dynamics','Gene programs along a supplied progression coordinate',['single_cell.trajectory','single_cell.states','bulk.timecourse'],
        'Upstream fixed progression coordinate, branch identities, program trajectories and donor-aware 95% intervals; no lineage, direction, smoothing or temporal inference performed.', 'extension',ctx=program_context,
        columns=2,value_label='Supplied gene-program score · 95% CI')

    # Re-render the full existing dedicated diagnostic set, preserving exact input bytes.
    for row in read_json(old/'manifest.json')['records']:
        key='Core_'+row['id'];folder=out/key;folder.mkdir();source=old/row['assets']['spec'];s=read_json(source)
        raw=(source.parent/s['input']['path']).read_bytes();(folder/'example.tsv').write_bytes(raw);s['input']['path']='example.tsv';s['figure_id']=key;s['export']['raster_dpi']=300
        if row['id']=='WGCNA_SampleTree':s['parameters']['context']['independent_n']=16
        if row['id']=='hdWGCNA_MetacellQC':s['parameters']['context']['independent_n']=12
        (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        records.append(dict(id=key,spec=key+'/example.spec.json',chapters=['single_cell.hdwgcna'] if row['id'].startswith('hdWGCNA') else both,
                            stage='qc' if any(k in key for k in ['SoftPower','SampleTree','MetacellQC']) else 'network' if any(k in key for k in ['ModuleTree','TOM','EigengeneNetwork']) else 'validation' if 'Preservation' in key else 'interpretation',
                            family=s['parameters']['mode'],variant=key.endswith(('Absolute','Dissimilarity')) or 'EigengeneProfiles' in key,origin='Exact frozen v0.9.1 input retained'))
    source=old/'WGCNA_SoftPower/input/example.spec.json';s=read_json(source);d=pd.read_csv(source.parent/s['input']['path'],sep='\t')
    d['median_connectivity']=d.mean_connectivity*.70;d['max_connectivity']=d.mean_connectivity*2.3;d['slope']=[-.4,-.6,-.8,-1.1,-1.3,-1.45,-1.55,-1.62,-1.68,-1.71,-1.74,-1.78]
    key='SoftPower_CompleteDiagnostics';folder=out/key;folder.mkdir();raw=table_bytes(d);(folder/'example.tsv').write_bytes(raw)
    s['figure_id']=key;s['parameters'].update(title='Soft-power diagnostics across all supplied candidates',diagnostics='complete',columns=2);s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=list(d.columns))
    (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8');records.append(dict(id=key,spec=key+'/example.spec.json',chapters=both,stage='qc',family='soft_threshold',variant=False))
    key='Eigengenes_MergeHierarchy';folder=out/key;folder.mkdir();s=read_json(old/'WGCNA_ModuleTree/input/example.spec.json')
    rr=[dict(record_type='leaf',node_id=m,module=m,dynamic_module=m) for m in modules]
    rr.extend(dict(record_type='merge',node_id=node,left=a,right=b,height=h) for node,a,b,h in [('A','M1','M2',.12),('B','M3','M4',.18),('C','M5','M6',.34),('D','A','B',.74),('E','D','C',1.20)])
    d=pd.DataFrame(rr);raw=table_bytes(d);(folder/'example.tsv').write_bytes(raw);s['figure_id']=key
    s['parameters'].update(title='Oriented eigengene hierarchy and declared merge reference',leaf_order=modules,track_labels=['Input module','Retained identity'],merge_reference=.25)
    s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=['height']);s['provenance']['source']='Authored fictional eigengene dissimilarity hierarchy v0.9.7; no correlation or clustering'
    (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8');records.append(dict(id=key,spec=key+'/example.spec.json',chapters=both,stage='network',family='module_dendrogram',variant=False))
    # Actual different counts and requested layouts, not only alternate gallery thumbnails.
    cases=[('Eigengenes_DonorRainclouds','Layout_OneModule_8Donors',1,['M1'],8),
           ('Eigengenes_DonorRainclouds','Layout_ThreeModules_OneColumn',1,modules[:3],24),
           ('Modules_BranchDynamics','Layout_ThreeModules_ThreeColumns',3,modules[:3],None),
           ('Modules_ExpressionAndEigengenes','Layout_Expression_OneColumn',1,modules[:2],None),
           ('Eigengenes_DonorContrasts','Layout_Contrasts_OneColumn',1,None,None),
           ('Modules_FunctionAndGeneSupport','Layout_Enrichment_12Modules',1,None,None)]
    for source,key,cols,selected,nunits in cases:
        src=out/source;s=read_json(src/'example.spec.json');d=pd.read_csv(src/'example.tsv',sep='\t');params=s['parameters'];params['columns']=cols
        if selected:
            d=d[d.module.isin(selected)].copy();params['module_order']=selected
        if nunits:
            d,cloud=profiles(selected,unit_count=nunits);params['cloud_shapes']=cloud;params['context']['independent_n']=nunits
        elif 'cloud_shapes' in params:
            params['cloud_shapes']={m:v for m,v in params['cloud_shapes'].items() if m in selected}
        if key=='Layout_Enrichment_12Modules':
            d=pd.concat([d.assign(module=d.module.map(lambda x:'M'+str(int(x[1:])+4*j))) for j in range(3)],ignore_index=True)
            s['theme'].setdefault('category_colors',{}).update(dict(zip(['M7','M8','M9','M10','M11','M12'],['#BC7E9C','#708694','#A4A757','#8471AD','#BA9472','#7BAFBA'])))
        folder=out/key;folder.mkdir();raw=table_bytes(d);(folder/'example.tsv').write_bytes(raw);s['figure_id']=key;s['input'].update(sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in d if pd.api.types.is_numeric_dtype(d[c])]);s['parameters']['title']+=' · layout probe'
        if cols==3:s['export']['target_width_mm']=297
        titles={'Layout_OneModule_8Donors':'Eigengene distributions · 8 donors','Layout_ThreeModules_OneColumn':'Eigengene distributions · one-column reading',
                'Layout_ThreeModules_ThreeColumns':'Branch programs · three-column comparison','Layout_Expression_OneColumn':'Module expression · one-column reading',
                'Layout_Contrasts_OneColumn':'Module effects · one-column reading','Layout_Enrichment_12Modules':'Module functions · 12-module comparison'}
        s['parameters']['title']=titles[key]
        (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        original=next(r for r in records if r['id']==source);records.append(dict(id=key,spec=key+'/example.spec.json',chapters=original['chapters'],stage='layout',family=original['family'],variant=True))
    (out/'manifest.json').write_text(json.dumps(dict(version='0.9.7',records=records,analysis_performed=False),indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(dict(synthetic_drawing_fixtures=len(records),analysis_performed=False)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);build(parser.parse_args().output)
