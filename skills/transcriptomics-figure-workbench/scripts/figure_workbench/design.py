"""Question-led, attractive-first design choices; standard library only, no inference."""
import csv
import math
from pathlib import Path
from .contracts import local_path, hash_value
from .registry import digest, resolve, source_identity

# These are display alternatives, not new scientific algorithms. A candidate is
# usable only when its required frozen channels are explicitly mapped.
ROUTES = {
 'differential_expression': [
   ('figure_integrated_views.plot_integrated_view','volcano',['label','effect','adjusted_probability','record_type','bin_left','bin_right','bin_count'],'Volcano with stacked marginal distributions','Prefer complete checked marginal counts and a count/proportion key; retain the same effects, probabilities and thresholds.'),
   ('package_style', 'volcano', ['label','effect','adjusted_probability'], 'Sparse labelled volcano', 'Use restrained direction colours and selected labels; retain every point.'),
   ('editorial', 'forest', ['label','effect','lower','upper'], 'Effect and interval', 'Prefer for a short, declared gene set when effect magnitudes matter.')],
 'enrichment': [
   ('figure_enrichment_story.plot_enrichment_story','ora',['label','count','denominator','adjusted_probability','membership','gene_effect','theme','tested_universe'],'ORA themes with linked gene evidence','Use exact query/background and hit counts; ORA does not encode signed activity. Pair selected themes with complete selected gene membership and supplied effects.'),
   ('figure_enrichment_story.plot_enrichment_story','gsea_comparison',['row','column','effect','adjusted_probability','membership','gene_effect','support_contrast','ranked_universe'],'NES contrasts with gene support','Keep a common NES scale and explicitly named support contrast; do not infer enrichment curves from summaries.'),
   ('refined','gsea_strip',['rank','running_score','rank_metric','membership','leading_edge'],'Compact aligned enrichment tracks','Prefer a gradient single pathway or aligned pathway facets when the complete ranked universe is supplied; preserve ES and all hits.'),
   ('package_style','nes',['row','column','effect','adjusted_probability','size'],'Aligned NES dot matrix','Separate effect colour, set-size area and test status.'),
   ('package_style','gsea',['rank','running_score','rank_metric','membership','leading_edge'],'ES tracks with hit barcode','Use genuine supplied ES curves; a term-summary table is insufficient.'),
   ('package_style','ora',['label','count','denominator','adjusted_probability'],'Term lollipop','Wrap full pathway names and place statistics in a clear guide lane.')],
 'effects': [
   ('editorial','forest',['label','effect','lower','upper'],'Point and interval forest','Use a common reference and align labels and interval endpoints.'),
   ('publication_plus','halfeye',['label','x','density','effect','lower','upper'],'Half-eye with supplied intervals','Show the supplied distribution shape without estimating a new density.')],
 'matrix': [
   ('publication_plus','split_matrix',['row','column','value','row_group','column_group'],'Split annotated heatmap','Use aligned group strips, generous gaps and one explicit colour range.'),
   ('package_style','dot',['row','column','value','fraction'],'Expression dot matrix','Colour encodes supplied expression and area encodes an explicit fraction.'),
   ('editorial','matrix',['row','column','value'],'Ordered heatmap','Keep supplied row/column order; do not invent a dendrogram.')],
 'embedding': [
   ('figure_integrated_views.plot_integrated_view','pca',['x','y','group','record_type','ellipse_width','ellipse_height','ellipse_angle','bin_count'],'PCA with supplied ellipses and marginal proportions','Prefer when the ellipse definition and complete reference geometry/bins exist; never invent a confidence region.'),
   ('figure_integrated_views.plot_integrated_view','annotation_atlas',['x','y','group','record_type','marker','fraction','expression','annotation_block'],'Subpopulation and marker atlas','Prefer labelled subpopulations, annotated marker specificity and shared-coordinate representative-gene maps when complete channels exist.'),
   ('package_style','embedding',['x','y','group'],'Restrained embedding','Use supplied coordinates, a stable categorical map and a compact key.')],
 'network': [
   ('package_style','network',['source','target','weight','x','y'],'Sparse supplied network','Use only declared edges and coordinates; label nodes directly.'),
   ('editorial','matrix',['row','column','value'],'Adjacency matrix','Prefer for dense graphs whose edge crossings obscure comparisons.')],
 'overlap': [
   ('upset',None,['set','membership'],'Aligned UpSet','Prefer an aligned intersection matrix to a many-set Venn.'),
   ('editorial','matrix',['row','column','value'],'Membership matrix','Prefer when readers need the identities of individual shared members.')],
 'paired': [
   ('editorial','paired',['unit','group','value'],'Paired observations','Light connecting lines retain subject identity; do not connect unrelated samples.')],
 'contributions': [
   ('clarity','contribution',['unit','group','label','effect','value'],'Class-specific contribution detail','Export complete selected classes separately; preserve per-instance contribution and feature-value colour.')],
 'imaging': [
   ('clarity','pixels',['x','y','value'],'Compact physical pixel panels','Use complete registered grids, declared orientation and unchanged intensity scales; no registration or segmentation.')],
 'estimation': [
   ('clarity','estimation',['unit','group','value','effect','lower','upper','density','x'],'Observations and supplied effect distribution','Separate raw observations from upstream effect/density; no bootstrap or inference.')],
 'model_evaluation': [
   ('clarity','precision_recall',['series','x','value'],'Precision and recall','Preserve upstream evaluation cohort and positive-class definitions; no AP or threshold optimisation.'),
   ('clarity','decision',['series','x','value'],'Decision curves','Use precomputed net benefit, declared baseline strategies, population and outcome units.')],
 'rank_stability': [
   ('clarity','rank_stability',['label','group','rank','lower','upper','status'],'Cross-export rank spans','Retain declared feature order and explicit unassessed states; rank spans are not automatically confidence intervals.')],
 'profiles': [
   ('publication_plus','profile',['category','series','value','area'],'Aligned linear profiles','Prefer common linear scales and visible category rows to overlapping radial fills.')],
 'survival': [
   ('package_style','survival',['time','survival','lower','upper','at_risk','group'],'Survival with risk table','Use a shared time scale, supplied intervals and explicit risk conventions.')],
 'curves': [
   ('refined','ribbon',['series','x','effect','lower','upper'],'Curve with supplied interval ribbons','Use fine curves, quiet interval bands and a separate key; no smoothing or new uncertainty estimation.')],
 'score_comparison': [
   ('refined','score_shift',['label','score_a','score_b','effect','lower','upper'],'Scores plus difference forest','Separate the two score positions from the supplied difference interval; a feature connection is not a biological pair.')],
 'associations': [
   ('refined','association',['source','target','value','record_type'],'Association matrices without crossing edges','Keep pairwise and Mantel summaries on separate guides; preserve raw probabilities in the exact table.')],
 'uncertainty': [
   ('publication_plus','halfeye',['label','x','density','effect','lower','upper'],'Half-eye and interval','Prefer a restrained slab to a decorative violin; preserve density and interval definitions.'),
   ('editorial','forest',['label','effect','lower','upper'],'Interval forest','Use when no density profile was supplied.')]
}


def design_plan(brief, base):
    fields={'schema_version','question','structure','input','roles','context','target'}
    if not isinstance(brief,dict) or set(brief)!=fields or brief['schema_version']!=1:
        raise ValueError('DesignBrief needs the documented exact fields and schema_version 1')
    if not isinstance(brief['question'],str) or not brief['question'].strip():
        raise ValueError('State the intended comparison in one question')
    if brief['structure'] not in ROUTES: raise ValueError('Unknown data structure')
    inp=brief['input']
    if not isinstance(inp,dict) or set(inp)!={'path','sha256'}:
        raise ValueError('Bind one selected TSV and its expected SHA256')
    path=local_path(inp['path'],base)
    if path.stat().st_size>5*1024**2 or digest(path)!=inp['sha256']:
        raise ValueError('Input changed or exceeds the 5 MiB design budget')
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.reader(stream,delimiter='\t');header=next(reader,[])
        if not header or len(header)!=len(set(header)) or any(not h for h in header) or len(header)>250:
            raise ValueError('Unique, nonempty table fields required')
        rows=0
        for record in reader:
            rows+=1
            if len(record)!=len(header) or rows>20000:raise ValueError('Ragged or oversized table')
    if not rows or digest(path)!=inp['sha256']:raise ValueError('Input empty or changed during reading')
    roles=brief['roles']
    allowed={r for candidates in ROUTES.values() for c in candidates for r in c[2]}
    if not isinstance(roles,dict) or set(roles)-allowed or any(not isinstance(v,str) or v not in header for v in roles.values()):
        raise ValueError('Explicit semantic roles must name actual selected columns')
    context=brief['context']
    expected={'frozen_results','independent_unit','denominator','uncertainty','upstream_qc','selection','missingness'}
    if not isinstance(context,dict) or set(context)!=expected or context['frozen_results'] is not True:
        raise ValueError('Declare frozen results and complete context')
    if context['upstream_qc'] not in ['reviewed','unknown','failed']:
        raise ValueError('Use reviewed, unknown or failed for upstream QC')
    if any(not isinstance(context[k],str) or not context[k].strip() for k in expected-{'frozen_results'}):
        raise ValueError('Context cannot be empty; use explicit not-applicable definitions')
    target=brief['target']
    if not isinstance(target,dict) or set(target)!={'width_mm','minimum_text_pt','medium'} or target['medium'] not in ['paper','presentation','screen']:
        raise ValueError('Declare target width, minimum text and medium')
    for name,low,high in [('width_mm',40,1000),('minimum_text_pt',5,30)]:
        v=target[name]
        if type(v) not in [int,float] or not math.isfinite(v) or not low<=v<=high:raise ValueError('Invalid design target')
    candidates=[]
    for alias,view,required,title,rationale in ROUTES[brief['structure']]:
        resolve(alias)
        missing=sorted(set(required)-set(roles))
        candidates.append(dict(renderer=alias,view=view,title=title,rationale=rationale,
            missing_roles=missing,state='NEEDS_CHANNELS' if missing else 'CANDIDATE',
            renderer_contract_check_required=True))
    available=[c for c in candidates if c['state']=='CANDIDATE']
    state='DESIGN_CANDIDATES' if available and context['upstream_qc']=='reviewed' else 'HOLD'
    blockers=[]
    if context['upstream_qc']!='reviewed':blockers.append('Upstream QC is not declared reviewed')
    if not available:blockers.append('No candidate has the necessary declared frozen channels')
    for field in ['independent_unit','denominator','uncertainty','missingness']:
        if context[field].strip().casefold() in {'unknown','unassessed','tbd','?'}:
            blockers.append('Unresolved context: '+field)
    if blockers:state='HOLD'
    return dict(schema_version=1,state=state,brief=brief,brief_sha256=hash_value(brief),
        source_identity=source_identity(),input_sha256=inp['sha256'],rows=rows,columns=header,
        preference='Prefer the most informative polished compatible extension. A bare scatter is a documented fallback when extra scientific channels are absent or the user requests simplicity.',
        fallback_reasons=[dict(view=c['view'],missing_roles=c['missing_roles']) for c in candidates[:candidates.index(available[0])] if c['state']=='NEEDS_CHANNELS'] if available else [],
        preferred=available[0] if available and state!='HOLD' else None,candidates=candidates,blocking_reasons=blockers,
        next_steps=['Review actual examples and select one candidate',
                    'Map the selected renderer exact contract into a FigureSpec',
                    'Use plan and render, with the declared target width and readability policy',
                    'Inspect the final PNG and vector export; bind only checks actually performed'],
        cautions=['Role availability does not establish numerical or biological validity',
                  'Candidate view names are guidance, not executable parameters for every renderer',
                  'No clustering, density estimation, enrichment or statistical test was run'],
        inference_performed=False,visual_acceptance=False,scientific_acceptance=False)
