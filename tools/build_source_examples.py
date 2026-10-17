"""Replay the complete form scope with authored presentation extensions.

Inputs are existing public frozen software fixtures. This is plotting QA, not
research analysis; no third-party source code or article pixels are copied.
"""
import argparse,copy,json,hashlib,sys
from pathlib import Path
from full_layout_cases import cases,ROOT,SKILL


def prepare(output):
    import pandas as pd
    output=output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    rows=copy.deepcopy([c for c in cases() if c['route']=='native'])
    for c in rows:
        # A single coherent colour language, with explicit identity bindings.
        from project_theme import create_theme
        known=list(c['theme']['group_slots'])
        for field in ['palette','group_palette','stack_palette']:
            if isinstance(c['parameters'].get(field),dict):known+=list(c['parameters'][field])
        known=list(dict.fromkeys(known))
        frame=pd.read_csv(ROOT/c['table'],sep='\t',dtype=str,keep_default_na=False)
        references=set(frame.to_numpy().ravel())
        def referenced(obj):
            if isinstance(obj,dict):
                for k,v in obj.items():references.add(str(k));referenced(v)
            elif isinstance(obj,list):
                for v in obj:referenced(v)
            else:references.add(str(obj))
        referenced(c['parameters'])
        known=[g for g in known if g in references] or known[:1]
        if c['form']=='flow':
            frame=pd.read_csv(ROOT/c['table'],sep='\t')
            known=list(dict.fromkeys(str(v) for column in c['parameters']['stage_columns'] for v in frame[column]))
        if len(known)<=24:
            c['theme']=create_theme('synthetic-source-review','package_editorial' if len(known)<=10 else 'atlas_cells',{g:i for i,g in enumerate(known)},font_family='DejaVu Sans',roles={'positive':'#D8795B','negative':'#4477AA'})
            c['theme']['continuous']['sequential']=['#DFE7EA','#326B8D']
            c['theme']['continuous']['diverging']=['#4477AA','#F7F7F7','#D8795B']
        c['theme']['font_family']='DejaVu Sans'
        c['fixture_definition']='Existing public frozen software fixture; no research inference'
        if c['form']=='contribution':c['parameters']['options']['subtitle']=f'All {frame.feature.nunique():,} features and {len(frame):,} contribution records / original feature order'
        if c['form']=='network':c['parameters']['view']='auto'
        if c['form']=='reference-surface-grid':c['parameters'].update(projection='map',center=0)
        if c['form']=='geographic-links':c['parameters']['size']=[10,5.4]
        if c['form'] in ['roc','precision-recall','calibration']:
            models=['Model A','Model B','Model C']
            c['theme']=create_theme('synthetic-model-comparison','package_editorial',{g:i for i,g in enumerate(models)},font_family='DejaVu Sans')
            c['parameters']['palette']={g:c['theme']['palette_colors'][i] for i,g in enumerate(models)}
            if c['form']=='precision-recall':c['parameters'].update(prevalence=.2,interpolation='steps-post')
        if c['form'] in ['ma','radial-effects','ranked-effects']:
            source=SKILL/'assets/study-gallery/study/BulkMA/BulkMA.tsv'
            d=pd.read_csv(source,sep='\t');d=d[d.record_type=='ma'][['feature_id','effect','status','average']].copy()
            if c['form']=='radial-effects':
                d=pd.concat([d[d.status==s].head(4) for s in ['down','other','up']],ignore_index=True)
                c['parameters']['order']=list(d.feature_id)
            if c['form']=='ranked-effects':
                d=d.sort_values('effect',kind='stable').reset_index(drop=True);d['rank']=range(1,len(d)+1)
            name=c['form']+'.tsv';d.to_csv(output/name,sep='\t',index=False,lineterminator='\n')
            c['table']=(output/name).relative_to(ROOT).as_posix()
            c['parameters']['title']={'ma':'Mean expression and differential effects','radial-effects':'Declared effect signature','ranked-effects':'Complete effect landscape'}[c['form']]
            c['fixture_definition']='Fictional v0.9.1 gene effects; explicit complete or first-four-per-status scope; synthetic effect ranks frozen before plotting'
    # Additional views extend existing forms. They are not independent chart IDs.
    extra=[]
    def extend(form,suffix,params):
        c=copy.deepcopy(next(c for c in rows if c['form']==form));c['form']=form+'__'+suffix;c['parameters'].update(params);extra.append(c)
    extend('network','circular',{'view':'circular'})
    extend('ma','marginals',{})
    extra[-1]['adapter']='figure_integrated_views.plot_integrated_view'
    extra[-1]['table']=(SKILL/'assets/study-gallery/study/BulkMA/BulkMA.tsv').relative_to(ROOT).as_posix()
    extra[-1]['parameters']={'mode':'ma','title':'Mean expression, effects and complete marginal counts'}
    extra[-1]['fixture_definition']='Complete fictional gene effects and matching pre-frozen marginal counts; no inference or rebinning'
    extend('reference-surface-grid','surface',{'projection':'surface','center':None})
    extend('stacked','facets',{'mode':'facets','ncols':3})
    for form in ['roc','precision-recall']:
        extend(form,'supplied-bounds',{'interval_label':'Illustrative supplied bounds; not confidence intervals',
                                     'mode':'facets','ncols':2})
        d=pd.read_csv(ROOT/extra[-1]['table'],sep='\t');d['lower']=(d.y-.06).clip(0,1);d['upper']=(d.y+.06).clip(0,1)
        name=form+'-bounds.tsv';d.to_csv(output/name,sep='\t',index=False,lineterminator='\n')
        extra[-1]['table']=(output/name).relative_to(ROOT).as_posix()
        extra[-1]['fixture_definition']='Existing fictional curve vertices plus declared illustrative +/-0.06 bounds clipped to [0,1]; no interval estimation'
    dot=next(c for c in rows if c['form']=='dot-matrix')
    source=pd.read_csv(ROOT/dot['table'],sep='\t');groups=list(dict.fromkeys(source['group']))
    extend('dot-matrix','identity-support',{'row_field':'group','column_field':'feature','row_order':groups,'column_order':list(dict.fromkeys(source.feature)),
           'row_counts':dict(zip(groups,[240,220,210,230])), 'count_label':'Synthetic cells','denominator_label':'synthetic cells in each identity','label_rotation':55})
    extra[-1]['fixture_definition']='Existing fictional mean/fraction matrix with separately declared illustrative identity counts; counts are software input constants, not inferred support'
    rows+=extra
    (output/'manifest.json').write_text(json.dumps({'schema_version':1,'records':rows,'scientific_acceptance':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'inputs':len(rows),'base_forms':87,'extensions':len(extra)}))


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--volume',choices=['small','medium','large']);p.add_argument('--width',type=float);p.add_argument('--forms',nargs='*');a=p.parse_args()
    sys.path.insert(0,str(SKILL/'scripts'))
    a.inputs=a.inputs.resolve()
    if not a.inputs.exists():prepare(a.inputs)
    if a.output:
        from render_full_layout_audit import render_cases
        records=json.loads((a.inputs/'manifest.json').read_text(encoding='utf8'))['records']
        if a.volume:records=[c for c in records if '__' not in c['form']]
        if a.forms:records=[c for c in records if c['form'] in a.forms]
        render_cases(a.output,level=['small','medium','large'].index(a.volume) if a.volume else None,case_rows=records,
                     layout_override={'width_inches':a.width} if a.width else None,include_all=True)


if __name__=='__main__':main()
