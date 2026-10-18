"""Explicit complete-study binding, with scoped analysis companions and aliases.

This selects supplied frozen FigureSpecs. It never discovers private project
files, exports catalogue placeholders as research results, or fits an analysis.
"""
import copy,re
from pathlib import Path
from .contracts import hash_value,check_plan,write_new

STAGES={'qc','network','interpretation','function','validation','extension','layout','chapter'}

def drawing_identity(plan):
    """Only exact content/style/context equality may remove a repeated export."""
    spec=copy.deepcopy(plan['spec']);spec.pop('figure_id',None)
    spec['input']['path']='<explicit frozen input with the bound hash>'
    return hash_value(spec)

def plan_bundle(manifest,request,base):
    from .study import study_plan,select_stages
    from .analysis_suites import named_analysis_chapters
    from .book import book_plan
    required={'schema_version','study_id','routine','analysis_book','result_stages','variants'}
    if not isinstance(manifest,dict) or set(manifest)!=required or manifest['schema_version']!=2:
        raise ValueError('Use the explicit version-2 study bundle')
    if not isinstance(manifest['study_id'],str) or not manifest['study_id'].strip():raise ValueError('A stable study identity is required')
    routine=manifest['routine'];book=copy.deepcopy(manifest['analysis_book']);assay=routine.get('assay')
    if routine.get('schema_version')!=1 or book.get('schema_version')!=1 or book.get('assay')!=assay:
        raise ValueError('Routine and analysis book must declare the same assay')
    supplied=book.get('results',[]);ids=[r.get('id') for r in supplied]
    if len(ids)!=len(set(ids)) or len(ids)>250:raise ValueError('Unique bounded explicit analysis results required')
    stages=manifest['result_stages'];variants=manifest['variants']
    if not isinstance(stages,dict) or set(stages)!=set(ids) or set(stages.values())-STAGES:
        raise ValueError('Every analysis result needs exactly one declared evidence stage')
    if not isinstance(variants,list) or len(variants)!=len(set(variants)) or set(variants)-set(ids):raise ValueError('Explicit known layout/alternative identities required')
    if not isinstance(request,str) or not request.strip():raise ValueError('State the requested figures')
    named=named_analysis_chapters(assay,request)
    whole=bool(re.search(r'整套|全套|全部|成套|whole|complete study|完整.*(?:结果|研究)',request,re.I))
    # Validate the routine contract even for a request restricted to one named
    # analysis. A malformed/failed upstream study must not bypass the gates.
    validated_routine=study_plan(routine,'整套图',base)
    selected_stages=select_stages(assay,request)
    include_variants=bool(re.search(r'自定义|替代|布局|layout|variant',request,re.I))
    chapter_roles={
        'qc':{'design','reads','alignment','filtering','normalization','batch','model_qc','barcode','qc','ambient_doublet','integration','hvg_pca','resolution'},
        'markers':{'annotation','subcluster','markers'},'composition':{'composition','abundance','deconvolution'},
        'differential':{'differential','interaction','pseudobulk','multi_contrast','programs'},
        'pathways':{'ora','gsea','gsea_multitrack','pathway_contrasts','gene_support','pathways','gsva'}}
    selected=[]
    for row in supplied:
        if row['id'] in variants and not include_variants:continue
        suffix=row['chapter'].split('.',1)[1]
        if whole or row['chapter'] in named or (not named and any(suffix in chapter_roles.get(k,set()) and (k!='qc' or stages[row['id']]=='qc') for k in selected_stages)):
            selected.append(row)
    blockers=[]
    available={r['chapter'] for r in supplied}
    if set(named)-available:blockers.append('Requested frozen analyses were not supplied: '+', '.join(sorted(set(named)-available)))
    regular=None
    if not named or whole:
        regular=validated_routine if whole else study_plan(routine,request,base)
        blockers+=regular['blocking_reasons']
    elif routine['upstream_qc']!='reviewed':blockers.append('Actual upstream study design/QC must be reviewed')
    declared=book.get('chapters',[])
    if declared=='all':raise ValueError('A study bundle needs explicit applicable chapters')
    if whole and set(declared)-available:blockers.append('Declared analyses have no supplied result binding: '+', '.join(sorted(set(declared)-available)))
    book['results']=selected;book['chapters']=list(dict.fromkeys(r['chapter'] for r in selected))
    analysis=book_plan(book,base) if selected else None
    panels=[];by={};aliases=[]
    candidates=[]
    if regular:
        for p in regular['panels']:
            identity='routine_'+p.get('id',p['role'])
            candidates.append(dict(id=identity,chapter=assay+'.routine',stage=p['stage'],scope=dict(contrast=routine['contrast'],independent_unit=routine['independent_unit'],denominator=routine['denominator'],cohort=manifest['study_id'],cell_type='not-applicable' if assay=='bulk' else 'mixed; per-spec scope retained'),plan=p['plan']))
    if analysis:
        for p in analysis['panels']:candidates.append(dict(p,stage=stages[p['id']]))
    candidate_ids=[p['id'] for p in candidates]
    if len(candidate_ids)!=len(set(candidate_ids)):raise ValueError('Routine and analysis outputs need distinct identities')
    colour_bindings={}
    for p in candidates:
        theme=p['plan']['spec']['theme']
        for name,slot in theme['group_slots'].items():
            color=theme['palette_colors'][slot]
            if name in colour_bindings and colour_bindings[name]!=color:raise ValueError('Identity colours must agree across the complete study')
            colour_bindings[name]=color
        # Caller scope is part of the scientific identity even when two toy
        # result tables or visual encodings happen to be byte-identical.
        key=hash_value(dict(drawing=drawing_identity(p['plan']),scope=p['scope']))
        if key in by:
            aliases.append(dict(id=p['id'],canonical_id=by[key]['id'],reason='Exact frozen input, context, parameters, theme and output settings'))
            by[key]['alias_ids'].append(p['id']);continue
        p['alias_ids']=[];by[key]=p;panels.append(p)
    if not panels:blockers.append('No compatible explicitly supplied results match this request')
    return dict(schema_version=2,state='HOLD' if blockers else 'STUDY_BUNDLE_PLANNED',study_id=manifest['study_id'],assay=assay,request=request,
                manifest_sha256=hash_value(manifest),routine_plan=regular,analysis_plan=analysis,panels=panels,aliases=aliases,
                analysis_coverage=[dict(chapter=c,results=[r['id'] for r in selected if r['chapter']==c],stages=sorted({stages[r['id']] for r in selected if r['chapter']==c})) for c in book['chapters']],
                blocking_reasons=blockers,scope='All and only the explicitly bound applicable frozen results; layouts selected separately',
                analysis_performed=False,visual_acceptance=False,scientific_acceptance=False)

def render_bundle(plan,output):
    if plan.get('state')!='STUDY_BUNDLE_PLANNED' or not plan.get('panels'):raise ValueError('Resolve the explicit bundle HOLD before rendering')
    panels=plan['panels'];ids=[p['id'] for p in panels]
    if len(ids)>300 or len(ids)!=len(set(ids)) or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',i) for i in ids):raise ValueError('Unique bounded safe output identities required')
    for p in panels:check_plan(p['plan'])
    from .pipeline import render_plan
    output=Path(output);output.mkdir(parents=True,exist_ok=False);completed=[]
    for p in panels:
        try:
            result=render_plan(p['plan'],output/p['id'])
            row=dict(id=p['id'],chapter=p['chapter'],stage=p['stage'],scope=p['scope'],alias_ids=p['alias_ids'],result=result)
            completed.append(row);write_new(output/(p['id']+'.receipt.json'),row)
            print('STUDY_BUNDLE_DRAWN '+p['id'],flush=True)
        except Exception as exc:
            write_new(output/'partial-receipt.json',dict(state='PARTIAL_FAILED',completed=completed,failed_id=p['id'],error=str(exc),automatic_retry=False));raise
    receipt=dict(state='RENDERED_REVIEW_REQUIRED',study_id=plan['study_id'],plan_sha256=hash_value(plan),panels=completed,aliases=plan['aliases'],analysis_performed=False,visual_acceptance=False,scientific_acceptance=False)
    write_new(output/'figure-set-receipt.json',receipt);return receipt
