"""Plan coherent figure sets from selected, frozen transcriptomic results.

No expression analysis, cell annotation, enrichment, fitting or file discovery.
The host interprets the research question; this bounded vocabulary covers common
requests and binds every selected panel to an actual FigureSpec and source.
"""
import re
from pathlib import Path
from .contracts import read_json, local_path, make_plan, hash_value, write_new, check_plan


STAGES = {
    'bulk': {
        'overview': [('study_overview', False)],
        'qc': [('qc_distribution', True), ('sample_embedding', True), ('sample_correlation', True), ('library_summary', False), ('design_map', False)],
        'differential': [('differential_expression', True), ('differential_heatmap', True), ('effect_intervals', False), ('ma', False), ('gene_expression', False)],
        'pathways': [('enrichment_summary', True), ('gsea_curves', False), ('enrichment_contrasts', False), ('pathway_gene_support', False)],
    },
    'single_cell': {
        'overview': [('study_overview', False)],
        'qc': [('qc_distribution', True), ('donor_summary', True), ('batch_embedding', False), ('design_map', False)],
        'markers': [('celltype_embedding', True), ('marker_dot', True), ('marker_features', True), ('marker_heatmap', False), ('marker_subgroup', False), ('condition_embedding', False)],
        'composition': [('donor_composition', True), ('donor_summary', False), ('donor_cell_support', False)],
        'differential': [('donor_differential', True), ('effect_intervals', False), ('differential_heatmap', False), ('ma', False)],
        'pathways': [('enrichment_summary', True), ('gsea_curves', False), ('enrichment_contrasts', False), ('pathway_gene_support', False)],
    },
}

INTENTS = [
    ('qc', r'质控|质量|\bqc\b|quality'),
    ('markers', r'标记|注释|细胞类型|亚群|子群|markers?|annotation'),
    ('composition', r'组成|比例|composition|proportion'),
    ('differential', r'差异|差別|differential|pseudobulk'),
    ('pathways', r'通路|富集|pathway|enrich|gsea'),
]


def select_stages(assay, request):
    if not isinstance(request, str) or not request.strip():
        raise ValueError('State the requested comparison or figure set')
    if re.search(r'文章|论文|全套|整套|完整|一套|成套|整体|全部|overview|manuscript|whole|complete', request, re.I):
        return list(STAGES[assay])
    selected=[stage for stage, pattern in INTENTS if re.search(pattern, request, re.I)]
    return [s for s in STAGES[assay] if s in selected]


def study_plan(manifest, request, base):
    required={'schema_version','assay','title','contrast','independent_unit','denominator','frozen_results','upstream_qc','results'}
    if not isinstance(manifest, dict) or set(manifest)!=required or manifest['schema_version']!=1:
        raise ValueError('Use the complete documented StudyFigureManifest')
    assay=manifest['assay']
    if assay not in STAGES or manifest['frozen_results'] is not True:
        raise ValueError('Choose bulk or single_cell and explicitly frozen results')
    for field in ['title','contrast','independent_unit','denominator']:
        if not isinstance(manifest[field], str) or not manifest[field].strip():
            raise ValueError('Complete study identity, contrast, unit and denominator required')
    if manifest['upstream_qc'] not in ['reviewed','unknown','failed']:
        raise ValueError('Declare actual upstream QC state')
    results=manifest['results'];allowed={r for stages in STAGES.values() for roles in stages.values() for r,_ in roles}
    if not isinstance(results,list) or len(results)>50:
        raise ValueError('Select at most fifty explicit result specifications')
    by={};identities=set()
    for result in results:
        if not isinstance(result,dict) or not {'role','spec'}<=set(result) or set(result)-{'role','spec','id'} or result['role'] not in allowed:
            raise ValueError('One selected FigureSpec per known result role; no ambiguous duplicate')
        role=result['role'];identity=result.get('id',role)
        if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',identity) or identity in identities:
            raise ValueError('Each selected result requires a unique safe output identity')
        if role!='marker_subgroup' and (role in by or 'id' in result):
            raise ValueError('Only explicit per-subgroup marker pages may repeat a result role')
        if role=='marker_subgroup' and 'id' not in result:
            raise ValueError('Give each per-subgroup marker page an explicit safe id')
        identities.add(identity);path=local_path(result['spec'],base)
        by.setdefault(role,[]).append((identity,path))
        if role=='marker_subgroup':
            s=read_json(path)
            if s['renderer']!='figure_annotation_views.plot_annotation_evidence' or s['parameters'].get('mode')!='subgroup':
                raise ValueError('A subgroup companion must render the explicit multi-marker subgroup contract')
    focus_groups=[read_json(p)['parameters'].get('focus_group') for _,p in by.get('marker_subgroup',[])]
    if len(focus_groups)!=len(set(focus_groups)):
        raise ValueError('One explicit default marker companion per selected focus group')
    stages=select_stages(assay,request);blocking=[];missing=[];panels=[];sections=[];seen=set();slots={}
    if not stages:blocking.append('Request does not match a documented figure-set intent; the host must clarify the comparison')
    if manifest['upstream_qc']!='reviewed' and stages!=['qc']:blocking.append('Upstream design and QC are not declared reviewed')
    if manifest['independent_unit'].strip().casefold() in ['unknown','cell','cells','spot','spots','细胞','未确定','?'] and 'differential' in stages:
        blocking.append('Differential inference requires an explicit biological independent unit; cells or spots alone are insufficient')
    for stage in stages:
        keys=[]
        for role,mandatory in STAGES[assay][stage]:
            if role not in by:
                missing.append({'stage':stage,'role':role,'required':mandatory,'state':'NOT_SUPPLIED'})
                if mandatory:blocking.append('Missing required frozen result: '+role)
                continue
            for identity,path in by[role]:
                keys.append(identity)
                if identity in seen:continue
                seen.add(identity);spec=read_json(path);plan=make_plan(spec,path.parent)
                colours={label:spec['theme']['palette_colors'][slot] for label,slot in spec['theme']['group_slots'].items()}
                colours.update(spec['theme'].get('category_colors',{}))
                for label,color in colours.items():
                    if label in slots and slots[label]!=color:raise ValueError('Inconsistent category colour across the selected figure set: '+label)
                    slots[label]=color
                panel={'role':role,'stage':stage,'spec_sha256':hash_value(spec),'plan':plan}
                if identity!=role:panel['id']=identity
                panels.append(panel)
        sections.append({'stage':stage,'panels':keys})
    presentation_decisions=[]
    for panel in panels:
        spec=panel['plan']['spec'];renderer=spec['renderer'];mode=spec['parameters'].get('mode')
        rich=renderer in ['figure_integrated_views.plot_integrated_view','figure_enrichment_story.plot_enrichment_story','figure_annotation_views.plot_annotation_evidence'] or spec['parameters'].get('presentation')=='integrated'
        comparison=panel['role']
        important=comparison in ['sample_embedding','celltype_embedding','differential_expression','donor_differential','marker_dot','study_overview','enrichment_summary']
        presentation_decisions.append(dict(role=comparison,renderer=renderer,mode=mode,
            state='RICH_PRESENTATION_SELECTED' if rich else 'COMPARE_POLISHED_EXTENSIONS' if important else 'CHECK_COMPLEMENTARY_INFORMATION',
            review='Compare compatible ellipse/marginal/marker-atlas extensions before accepting a basic fallback; record missing channels or explicit user preference' if important and not rich else 'Inspect actual information hierarchy and final exports'))
        if comparison in ['qc_distribution','gene_expression']:
            params=spec['parameters'];clouds=params.get('cloud_shapes') or any(p.get('cloud_shapes') for p in params.get('panels',[]))
            presentation_decisions[-1].update(state='RAINCLOUD_SELECTED' if clouds else 'COMPARE_RAINCLOUD_EXTENSION',
                review='Inspect supplied half-cloud, every observation, narrow box/median and explicit count units' if clouds else 'Prefer a raincloud when frozen density geometry is supplied; otherwise disclose the missing density and retain all observation points. Do not invent a cloud or silently call a boxplot the preferred default.')
    return {'schema_version':1,'state':'HOLD' if blocking else 'FIGURE_SET_PLANNED',
        'assay':assay,'title':manifest['title'],'request':request,'contrast':manifest['contrast'],
        'independent_unit':manifest['independent_unit'],'denominator':manifest['denominator'],
        'manifest_sha256':hash_value(manifest),'sections':sections,'panels':panels,
        'missing_results':missing,'blocking_reasons':blocking,'category_colours':slots,
        'presentation':'Question-led sections; complete individual figures, then an explicitly sized composition or paginated reading edition',
        'review_requirements':['Inspect every single figure and every composition page at the actual target size',
            'Review hierarchy, complementary information, redundant panels, scale/units, colour meaning, labels and balance',
            'Missing upstream results remain missing; an attractive export never certifies the analysis'],
        'presentation_decisions':presentation_decisions,
        'analysis_performed':False,'visual_acceptance':False,'scientific_acceptance':False}


def render_study(plan, output):
    if plan.get('state')!='FIGURE_SET_PLANNED':raise ValueError('Resolve every figure-set HOLD before rendering')
    assay=plan.get('assay');panels=plan.get('panels')
    if assay not in STAGES or not isinstance(panels,list) or not 1<=len(panels)<=50:raise ValueError('A selected supported figure set is required')
    seen=set()
    for p in panels:
        identity=p.get('id',p.get('role'))
        if p.get('stage') not in STAGES[assay] or p.get('role') not in {r for r,_ in STAGES[assay][p['stage']]} or not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',identity) or identity in seen:raise ValueError('Unknown, duplicate or unsafe figure-set panel identity')
        if 'id' in p and p['role']!='marker_subgroup':raise ValueError('Only scoped marker companions may override the default output identity')
        seen.add(identity);check_plan(p['plan'])
        if p.get('spec_sha256')!=p['plan']['spec_sha256']:raise ValueError('Figure-set source binding changed')
    from .pipeline import render_plan
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rows=[]
    try:
        for panel in plan['panels']:
            identity=panel.get('id',panel['role']);result=render_plan(panel['plan'],output/identity)
            rows.append({'role':panel['role'],'id':identity,'stage':panel['stage'],'result':result})
            print('FIGURE_SET_PANEL '+identity,flush=True)
    except Exception:
        write_new(output/'partial-receipt.json',{'state':'PARTIAL_FAILED','completed':rows,'automatic_retry':False})
        raise
    receipt={'state':'RENDERED_REVIEW_REQUIRED','assay':plan['assay'],'request':plan['request'],
        'plan_sha256':hash_value(plan),'panels':rows,'missing_results':plan['missing_results'],
        'analysis_performed':False,'visual_acceptance':False,'scientific_acceptance':False}
    write_new(output/'figure-set-receipt.json',receipt)
    return receipt
