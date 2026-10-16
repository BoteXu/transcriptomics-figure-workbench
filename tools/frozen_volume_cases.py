"""Declared software-fixture selections, never selection of a research result."""
import copy, math

FIELDS = {
 'heatmap':'feature','dot-matrix':'feature','forest':'label','volcano':'gene','enrichment-summary':'term',
 'term-circle':'term_id','paired':'subject_id','point-interval':'sample_id','raincloud':'sample_id',
 'box':'cell_id','violin':'group','embedding':'cell_id','feature-embedding':'cell_id','scatter':'sample_id',
 'ribbon':'time','profile':'group','bars':'display_cluster','stacked':'sample','donut':'group',
 'histogram':'group','ridges':'group','roc':'model','precision-recall':'model','calibration':'model',
 'membership-links':'term_id','flow':'path_id','upset':'object_id','venn':'object_id','joint':'group',
 'rank':'group','gating':'unit_id','annular':'category','contribution':'feature','effect-distribution':'effect_id',
 'spatial':'object_id','slice':'view','interval-tracks':'start','field':'object_id','state-matrix':'cluster',
 'scores':'feature','decision':'series','maps':'polygon_id','geographic-links':'path_id','radar':'category',
 'object-schematic':'object_id','ma':'feature_id','radial-effects':'feature_id','ranked-effects':'feature_id',
 'mosaic':'group','horizon':'series','connected-scatter':'step','mirrored-bars':'category','rainfall':'variant_id',
 'qq':'group','residual-diagnostics':'unit_id','dashboards':'sample','residue-confidence':'residue',
 'reference-parallel-trials':'trial_id','reference-group-beeswarm':'group','reference-strip-effects':'feature',
 'reference-aligned-tracks':'category','distribution-ecdf':'group','covariate-balance':'covariate',
 'bland-altman-supplied':'object_id','swimmer-followup':'object_id','specification-curve':'spec_id',
 'supplied-vector-field':'object_id','ternary-composition':'object_id','genome-association-overview':'variant_id',
 'funnel-supplied-results':'study_id','feature-correlation-projection':'feature_id','mass-spectrum-mirror':'peak_id',
 'pathway-quantity-overlay':'node_id','variant-posteriors':'variant_id','contribution-waterfall':'component_id',
 'sequence-logo':'position_id','contact-tracks':'bin_id',
}


def _select(values, level, minimum=1):
    values=list(dict.fromkeys(values)); n=len(values)
    count=min(n,max(minimum,math.ceil(n*(level+1)/3)))
    return values[:count]


def _prune_parameters(obj, data, original):
    """Only prune explicit order/mapping fields whose IDs actually disappeared."""
    if not isinstance(obj,dict):return
    for key,value in list(obj.items()):
        if (key.endswith('_order') or key=='order') and isinstance(value,list):
            candidates=[c for c in original if len(original[c].dropna()) and set(value)==set(original[c].dropna())]
            if candidates:
                c=candidates[0];kept=set(data[c].dropna());obj[key]=[v for v in value if v in kept]
        elif isinstance(value,dict):
            if key.endswith(('_aliases','_blocks')):
                for c in original:
                    if set(value)==set(original[c].dropna()):
                        kept=set(data[c].dropna());obj[key]={k:v for k,v in value.items() if k in kept};break
            else:_prune_parameters(value,data,original)
        elif isinstance(value,list):
            for part in value:_prune_parameters(part,data,original)


def volume(case, original, level):
    """Return a frozen selected display fixture and an explicit volume receipt."""
    import pandas as pd
    form=case['form'];params=copy.deepcopy(case['parameters']);data=original.copy(deep=True)
    method='Complete selected identity records; auxiliary supplied display records retained'
    field=FIELDS.get(form)
    if form=='waffle':
        data['count']=data['count']*(level+1);field='count';metric=int(data['count'].sum());method='Declared illustrative event-count multiplier before freezing'
    elif form in ['registration','reference-surface-grid']:
        xs=sorted(data.x.unique()) if 'x' in data else sorted(data.u.unique());ys=sorted(data.y.unique()) if 'y' in data else sorted(data.v.unique());x='x' if 'x' in data else 'u';y='y' if 'y' in data else 'v'
        data=data[data[x].isin(xs[::3-level])&data[y].isin(ys[::3-level])].copy();field='supplied_regular_grid';metric=len(data);method='Exact supplied regular-grid points at declared stride; no interpolation'
    elif form=='gsea':
        options=params['options'];n=options['ranked_universe'];keep=max(10,math.ceil(n*(level+1)/3));data=data[data['rank'].isna()|(data['rank']<=keep)].copy()
        # These are newly declared software curves, not truncated research GSEA.
        data.loc[(data.kind=='curve')&(data['rank']==keep),'value']=0
        options['ranked_universe']=keep;options['gene_set_version']+=' / software fixture universe '+str(keep)
        for pathway in data.loc[data.kind=='summary','pathway']:
            data.loc[(data.kind=='summary')&(data.pathway==pathway),'set_size']=len(data[(data.kind=='hit')&(data.pathway==pathway)])
        field='ranked_universe';metric=keep;method='Declared complete shorter software-ranked universe; supplied ES/NES are illustrative constants, not recomputed enrichment'
    elif form=='network':
        nodes=data.loc[data.record_type=='node','node'].dropna().tolist();keep=_select(nodes,level,minimum=3)
        data=data[((data.record_type=='node')&data.node.isin(keep))|((data.record_type=='edge')&data.a.isin(keep)&data.b.isin(keep))].copy();field='node';metric=len(keep)
    elif form=='chord':
        keep=list(dict.fromkeys(_select(data.source,level)+_select(data.target,level)));data=data[data.source.isin(keep)&data.target.isin(keep)].copy();params['order']=[k for k in params['order'] if k in keep];field='sector';metric=len(keep)
    elif form=='correlation':
        keep=_select(params['labels'],level,minimum=3);data=data[data.a.isin(keep)&data.b.isin(keep)].copy();params['labels']=keep;field='correlation_labels';metric=len(keep)
    elif form=='hierarchy':
        parents=set(data.parent_id.dropna())-set(['']);leaves=[v for v in data.node_id if v not in parents];keep=set(_select(leaves,level,minimum=1));by=data.set_index('node_id')
        for node in list(keep):
            current=node
            while pd.notna(by.loc[current,'parent_id']) and by.loc[current,'parent_id'] not in ['','ROOT'] and by.loc[current,'parent_id'] in by.index:
                current=by.loc[current,'parent_id'];keep.add(current)
        data=data[data.node_id.isin(keep)].copy()
        for _ in range(len(data)):
            for node in data.node_id:
                children=data[data.parent_id==node]
                if len(children):data.loc[data.node_id==node,'value']=children['value'].sum()
        def rectangles(node,rect,depth=0):
            data.loc[data.node_id==node,['x0','y0','x1','y1']]=rect
            children=data[data.parent_id==node];total=children['value'].sum();at=rect[depth%2]
            for child in children.itertuples():
                nxt=at+(rect[depth%2+2]-rect[depth%2])*child.value/total
                sub=list(rect);sub[depth%2]=at;sub[depth%2+2]=nxt
                rectangles(child.node_id,sub,depth+1);at=nxt
        rectangles(params['root_id'],[0.,0.,1.,1.])
        field='display_tree_nodes';metric=len(data);method='Complete selected tree leaves plus ancestors; illustrative parent quantities regenerated before freezing'
    elif form=='decision':
        xs=sorted(data.x.unique());keep=xs[::3-level];data=data[data.x.isin(keep)].copy();field='supplied_thresholds';metric=len(keep);method='Selected supplied thresholds with both baseline strategies retained; no threshold optimisation'
    elif form in ['survival','splice-tracks']:
        field='group' if form=='survival' else 'sample_id';values=list(data[field].dropna().unique());count=level+1
        if count<=len(values):data=data[data[field].isna()|data[field].isin(values[:count])].copy()
        else:
            clone=data[data[field]==values[-1]].copy();new=str(values[-1])+' / display replica';clone[field]=new;data=pd.concat([data,clone],ignore_index=True)
            if form=='splice-tracks':params['sample_order']=values+[new]
        metric=count;method='Complete curve/track identities; an additional explicitly named synthetic display replica at large volume'
    elif field:
        values=data[field].dropna().drop_duplicates().tolist();keep=_select(values,level,minimum=3 if form=='radar' else 1)
        strata=next((c for c in ['group','chromosome','spectrum'] if c in data and c!=field and field.endswith('_id')),None)
        if strata:
            keep=list(dict.fromkeys(v for _,part in data.groupby(strata,sort=False) for v in _select(part[field].dropna(),level)))
        data=data[data[field].isna()|data[field].isin(keep)].copy();metric=len(keep)
        if form=='pathway-quantity-overlay':data=data[data.record_type!='edge'].copy() if not len(data[data.record_type=='edge']) else data[(data.record_type!='edge')|(data.source.isin(keep)&data.target.isin(keep))].copy()
        if form=='contact-tracks':data=data[(data.record_type!='contact')|(data.bin_i.isin(keep)&data.bin_j.isin(keep))].copy()
        if form=='donut':
            data['value']=data['value']/data['value'].sum();method='New illustrative composition fixture normalized before freezing; no research normalization'
        if form=='contribution-waterfall':params['total']=params['baseline']+float(data.contribution.sum())
    else:raise ValueError('No declared quantity dimension for '+form)
    _prune_parameters(params,data,original)
    if form=='profile':
        span=max(float(data.y.max()-data.y.min()),.1)
        params['options']['y_limits']=[float(data.y.min()-.1*span),float(data.y.max()+.1*span)]
        method+='; explicit full selected-profile display extent'
    if form=='residual-diagnostics':
        data['ordered_residual']=sorted(data.standard_residual)
    if params.get('label_ids') and 'variant_id' in data:params['label_ids']=[v for v in params['label_ids'] if v in set(data.variant_id)]
    if form=='slice':params['axis_labels']={k:v for k,v in params['axis_labels'].items() if k in set(data.view)}
    if form=='volcano' and params.get('labels'):params['labels']=[v for v in params['labels'] if v in set(data.gene)]
    if form=='slice':params['arrangement']='vertical' if level==1 else 'horizontal'
    if level==1 and field in ['label','term','feature','category','display_cluster','covariate']:
        mapping={v:str(v)+' / long display identity' for v in data[field].dropna().unique()}
        data[field]=data[field].map(lambda v:mapping.get(v,v))
        def rename(obj):
            if isinstance(obj,dict):return {mapping.get(k,k):(v if k in ['id','type','layout','palette_name'] else rename(v)) for k,v in obj.items()}
            if isinstance(obj,list):return [rename(v) for v in obj]
            if isinstance(obj,str):return mapping.get(obj,obj)
            return obj
        params=rename(params);case['parameters']=params
        method+='; explicit long display identities in the medium software fixture'
    case=copy.deepcopy(case);case['parameters']=params
    receipt=dict(level=['small','medium','large'][level],quantity_dimension=field,quantity=metric,input_rows=len(data),preparation=method,scientific_validity='Synthetic display test only; no inference or biological acceptance')
    return case,data,receipt
