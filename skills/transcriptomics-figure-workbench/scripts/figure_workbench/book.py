"""Complete chapter recipes and source-bound, multiple-scope figure books.

Plot implementation and availability of a project's result table are separate.
Every shipped chapter has an executable synthetic example, including extensions.
"""
import copy,re
from pathlib import Path
from .contracts import read_json,make_plan,check_plan,hash_value,write_new

SKILL=Path(__file__).resolve().parents[2]
CATALOG=SKILL/'references/transcriptomic-chapters.json'

def chapters(assay='',search=''):
    doc=read_json(CATALOG)
    if assay and assay not in ['bulk','single_cell']:raise ValueError('Choose bulk or single_cell')
    query=search.casefold()
    return [r for r in doc['chapters'] if (not assay or r['assay']==assay) and query in str(r).casefold()]

def chapter_template(entry,output):
    row=next((r for r in chapters() if r['id']==entry),None)
    if row is None:raise ValueError('Choose a shipped chapter ID')
    source=SKILL/row['example'];spec=read_json(source)
    from .contracts import local_path
    table=local_path(spec['input']['path'],source.parent)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    # Export only the explicitly selected public template, never scan a project.
    (output/'example.tsv').write_bytes(table.read_bytes())
    spec['input']['path']='example.tsv';write_new(output/'example.spec.json',spec)
    write_new(output/'chapter.json',row)
    return dict(state='EXECUTABLE_TEMPLATE_EXPORTED',chapter=entry,analysis_performed=False)

def book_plan(manifest,base):
    required={'schema_version','assay','title','chapters','results'}
    if not isinstance(manifest,dict) or set(manifest)!=required or manifest['schema_version']!=1:raise ValueError('Use the documented ChapterBookManifest')
    if manifest['assay'] not in ['bulk','single_cell'] or not isinstance(manifest['title'],str) or not manifest['title'].strip():raise ValueError('Explicit book assay and title required')
    catalog={r['id']:r for r in chapters(manifest['assay'])};selected=manifest['chapters']
    if selected=='all':selected=list(catalog)
    if not isinstance(selected,list) or not selected or len(selected)!=len(set(selected)) or set(selected)-set(catalog):raise ValueError('Select explicit unique chapter IDs or all')
    rows=manifest['results']
    if not isinstance(rows,list) or len(rows)>500:raise ValueError('Select at most 500 explicit result specifications')
    sections={k:dict(chapter=k,title=catalog[k]['title'],plot_capability=catalog[k]['plot_capability'],template=catalog[k]['example'],required_results=catalog[k]['required_results'],scopes=[],project_input_state='INPUT_REQUIRED') for k in selected}
    ids=set();scopes=set();panels=[];bindings={}
    from .contracts import local_path
    for row in rows:
        needed={'id','chapter','scope','spec','frozen_results','upstream_qc'}
        if not isinstance(row,dict) or not needed<=set(row) or set(row)-needed-{'view'} or row['chapter'] not in sections or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',row['id']) or row['id'] in ids:raise ValueError('Explicit unique safe result ID and selected chapter required')
        ids.add(row['id']);scope=row['scope']
        if not isinstance(scope,dict) or set(scope)!={'contrast','cell_type','cohort','independent_unit','denominator'} or any(not isinstance(x,str) or not x.strip() for x in scope.values()):raise ValueError('Complete contrast, celltype, cohort, independent unit and denominator required; use explicit not-applicable where appropriate')
        view=row.get('view','main')
        if not isinstance(view,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',view):raise ValueError('Use a safe explicit view or reading-page identifier')
        identity=(row['chapter'],hash_value(scope),view)
        if identity in scopes:raise ValueError('Ambiguous duplicate chapter/scope/view; name each complementary view or reading page explicitly')
        scopes.add(identity)
        if row['frozen_results'] is not True or row['upstream_qc']!='reviewed':raise ValueError('A project result requires frozen inputs and actual reviewed upstream design/QC')
        if scope['independent_unit'].casefold() in ['cell','cells','spot','spots','unknown','细胞','?']:raise ValueError('Name biological independent units; cell displays also need donor/experimental context')
        path=local_path(row['spec'],base);spec=read_json(path);plan=make_plan(spec,path.parent)
        if spec['provenance'].get('synthetic') is not True and scope['contrast']!=spec['provenance']['contrast']:raise ValueError('Scope contrast must match frozen result provenance')
        for name,slot in spec['theme']['group_slots'].items():
            color=spec['theme']['palette_colors'][slot]
            if name in bindings and bindings[name]!=color:raise ValueError('Identity colours must remain stable throughout a book')
            bindings[name]=color
        panels.append(dict(id=row['id'],chapter=row['chapter'],view=view,scope=copy.deepcopy(scope),spec_sha256=hash_value(spec),plan=plan))
        sections[row['chapter']]['scopes'].append(row['id']);sections[row['chapter']]['project_input_state']='RESULTS_SELECTED'
    return dict(schema_version=1,state='CHAPTER_BOOK_PLANNED',title=manifest['title'],assay=manifest['assay'],manifest_sha256=hash_value(manifest),catalog_sha256=hash_value(read_json(CATALOG)),sections=list(sections.values()),panels=panels,
        implemented_chapters=len(selected),result_figures=len(panels),analysis_performed=False,visual_acceptance=False,scientific_acceptance=False,
        layout='Complete chapter companions; multiple contrasts, celltypes and cohorts retain separate scoped identities. Compose selected panels using layout-plan.',
        project_input_requirement='INPUT_REQUIRED describes a project table only. Every chapter drawing recipe and synthetic example is implemented.')

def render_book(plan,output):
    if plan.get('state')!='CHAPTER_BOOK_PLANNED' or plan.get('catalog_sha256')!=hash_value(read_json(CATALOG)):raise ValueError('Replan against the exact current chapter catalogue')
    panels=plan.get('panels',[])
    if not panels:raise ValueError('Select explicit project results or export a chosen synthetic chapter template')
    if len(panels)>500 or len({p.get('id') for p in panels})!=len(panels):raise ValueError('Unique bounded chapter result identities required')
    allowed={r['id'] for r in chapters(plan.get('assay',''))}
    for p in panels:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',p.get('id','')) or p.get('chapter') not in allowed:raise ValueError('Unknown or unsafe chapter output identity')
        check_plan(p['plan'])
        if p['spec_sha256']!=p['plan']['spec_sha256']:raise ValueError('Changed chapter source binding')
    from .pipeline import render_plan
    output=Path(output);output.mkdir(parents=True,exist_ok=False);completed=[]
    try:
        for p in panels:
            result=render_plan(p['plan'],output/p['id']);completed.append(dict(id=p['id'],chapter=p['chapter'],scope=p['scope'],result=result));print('CHAPTER_RENDERED '+p['id'],flush=True)
    except Exception:
        write_new(output/'partial-receipt.json',dict(state='PARTIAL_FAILED',completed=completed,automatic_retry=False));raise
    receipt=dict(state='RENDERED_REVIEW_REQUIRED',plan_sha256=hash_value(plan),completed=completed,analysis_performed=False,visual_acceptance=False,scientific_acceptance=False)
    write_new(output/'book-receipt.json',receipt);return receipt
