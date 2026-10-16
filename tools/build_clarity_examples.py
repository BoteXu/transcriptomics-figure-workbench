"""Build actual frozen-table examples for the next clarity iteration."""
from pathlib import Path
import argparse,copy,csv,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest
from project_theme import create_theme

def read(p):
    with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def build(output,selected=None):
    output.mkdir(exist_ok=False,parents=True);inputs=output/'inputs';inputs.mkdir();cases=[]
    def source(k):return ROOT/'examples/gallery/figures'/k/(k+'.tsv')
    def meta(k):return json.loads((ROOT/'examples/gallery/metadata'/(k+'.json')).read_text(encoding='utf8'))['figure_spec']
    p=source('T35');r=read(p);cases.append(('CLR01','profiles',r,dict(group_order=list(dict.fromkeys(x['group'] for x in r)),x_limits=[1800,1000],y_limits=[.9,5.9],x_label='Coordinate',y_label='Supplied value',title='Stored profiles with a lighter touch',subtitle='All 1,080 supplied vertices / original direction and offsets'),p,'all rows'))
    p=source('R16');m=meta('R16');cases.append(('CLR02','effects',read(p),dict(row_order=m['row_order'],panel_order=m['panel_order'],panel_labels=m['panel_labels'],limits=m['limits'],interval_definition='Supplied display bounds; not computed here',count_definition='Count labels have the fixture-defined n(k) form',title='Effect distributions and supplied summaries',subtitle='All 26 rows in each metric / exact points, bounds, counts and raw p'),p,'all rows'))
    p=source('R11');m=meta('R11');r=read(p)
    for i,c in enumerate(m['class_order']):
        q=[x for x in r if x['record_type']=='contribution' and x['class']==c]
        cases.append((f'CLR{i+3:02d}','contribution',q,dict(class_label=c,feature_order=m['feature_orders'][c],value_limits=[0,1],effect_limits=m['limits'],effect_label='Supplied contribution',value_label='Supplied feature value',title=c+' | contribution detail',subtitle='All 19 features and 1,330 instances / original feature order'),p,'all contribution rows for '+c+'; other classes exported separately; shares exported as CLR08'))
    q=[x for x in r if x['record_type']=='share'];cases.append(('CLR08','shares',q,dict(class_order=m['class_order'],feature_order=list(dict.fromkeys(x['feature'] for x in q)),share_limits=[0,.4],denominator='Upstream declared absolute-contribution shares for the nine supplied features',title='Contribution shares on a common scale',subtitle='All 45 supplied shares / replaces five rings and pie insets'),p,'all share rows; contribution points exported as CLR03..CLR07'))
    p=source('E34');m=meta('E34');cases.append(('CLR09','membership',read(p),dict(member_order=m['member_order'],term_order=m['term_order'],effect_limits=m['effect_limits'],denominator=m['ratio_definition'],title='Membership without crossing ribbons',subtitle='All 47 links, 20 member effects and eight term summaries'),p,'all rows'))
    for key,old,mode in [('CLR10','E41','slices'),('CLR11','E42','registration')]:
        p=source(old);m=meta(old);o=dict(mode=mode,view_order=m.get('view_order',[]),label_names={'1':'Label 1','2':'Label 2'} if mode=='slices' else {},intensity_limits=m['intensity_limits'],difference_limits=m.get('difference_limits',[-.15,.15]),tile_pixels=m.get('tile_pixels',4),coordinate_labels=['u (mm)','v (mm)'],orientation_definition='Declared u/v direction; procedural grids, not clinical anatomy.',title='Frozen slice labels' if mode=='slices' else 'Registered image comparison',subtitle='Three complete physical grids / fixed label identities' if mode=='slices' else 'One shared grid / fixed and registered intensity scales')
        pixel_rows=read(p)
        if mode=='slices':pixel_rows=[{('label_id' if k=='label' else k):v for k,v in row.items()} for row in pixel_rows]
        cases.append((key,'pixels',pixel_rows,o,p,'all rows; label column renamed label_id for the typed pixel contract' if mode=='slices' else 'all rows'))
    # Literal original software fixtures; these are supplied display channels,
    # not results obtained by analyzing the demonstration observations.
    rows=[dict(record_type='observation',unit_id=f'A{i+1}',group='Control',value=v) for i,v in enumerate([1.4,1.7,1.9,2.0,2.1,2.2,2.3,2.5,2.6,2.8])]
    rows += [dict(record_type='observation',unit_id=f'B{i+1}',group='Exposure',value=v) for i,v in enumerate([2.0,2.2,2.6,2.7,2.8,3.0,3.3,3.4,3.5,4.0])]
    rows += [dict(record_type='summary',value=.8,lower=.3,upper=1.3)]
    rows += [dict(record_type='density',x=x,density=y) for x,y in zip([-.2,-.1,0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8],[0,.01,.03,.06,.12,.22,.38,.58,.78,.94,1,.94,.78,.58,.38,.22,.12,.06,.03,.01,0])]
    cases.append(('EXT01','estimation',rows,dict(group_order=['Control','Exposure'],value_limits=[1,4.2],effect_limits=[-.4,2],value_label='Supplied observation (a.u.)',effect_label='Supplied mean difference (a.u.)',interval_definition='Illustrative supplied interval and density; not inferred from the points',title='Observations beside effect uncertainty',subtitle='Estimation display / independent groups, separate scales'),None,'complete literal original software fixture; no bootstrap or fit'))
    curves=[('Model A',[.235,.201,.174,.148,.118,.086,.054,.022]),('Model B',[.222,.192,.159,.127,.096,.064,.031,-.004]),('Treat all',[.21052631578947367,.16666666666666666,.11764705882352941,.0625,0,-.07142857142857142,-.15384615384615385,-.25]),('Treat none',[0,0,0,0,0,0,0,0])]
    rows=[dict(series=k,x=x,value=y) for k,ys in curves for x,y in zip([.05,.10,.15,.20,.25,.30,.35,.40],ys)]
    cases.append(('EXT02','decision',rows,dict(series_order=[k for k,_ in curves],reference_series=['Treat all','Treat none'],x_limits=[.05,.4],y_limits=[-.4,.28],x_label='Threshold probability',y_label='Supplied net benefit',evaluation_definition='Illustrative stored benefit curves; one declared evaluation cohort',title='Decision curves with explicit baselines',subtitle='All precomputed points / no threshold optimisation'),None,'complete literal original software fixture; benefits are not calculated from predictions'))
    curves=[('Model A',[.97,.95,.92,.87,.80,.69,.53,.31]),('Model B',[.96,.92,.88,.81,.71,.60,.45,.31])]
    rows=[dict(series=k,x=x,value=y) for k,ys in curves for x,y in zip([.02,.10,.25,.40,.55,.70,.85,1.0],ys)]
    cases.append(('EXT03','precision_recall',rows,dict(series_order=[k for k,_ in curves],x_limits=[0,1],y_limits=[0,1],x_label='Recall',y_label='Precision',evaluation_definition='Illustrative stored precision and recall; positive class and evaluation cohort declared upstream',title='Precision and recall across stored thresholds',subtitle='Exact supplied vertices / a distinct view from ROC'),None,'complete literal original software fixture; no threshold, AP or AUC estimation'))
    rows=[];features=['Feature '+x for x in 'ABCDEFGH'];cohorts=['Discovery','Validation A','Validation B']
    for cohort,ranks in zip(cohorts,[[1,2,3,4,5,6,7,8],[2,1,4,3,6,5,8,7],[1,3,2,5,4,7,None,None]]):
        for feature,rank in zip(features,ranks):rows.append(dict(feature=feature,cohort=cohort,status='reported' if rank else 'unassessed',rank=rank,lower_rank=max(1,rank-1) if rank else None,upper_rank=min(8,rank+1) if rank else None))
    cases.append(('EXT04','rank_stability',rows,dict(feature_order=features,cohort_order=cohorts,rank_limits=[.5,8.5],interval_definition='Illustrative supplied rank spans; not inferential confidence intervals',title='Rank spans across stored exports',subtitle='All eight features / explicit unassessed states'),None,'complete literal original rank display fixture; no ranking or stability calculation'))
    template=json.loads((ROOT/'examples/design-v050/inputs/VIS02.spec.json').read_text(encoding='utf8'));records=[]
    for key,view,rows,o,src,selection in cases:
        if selected and key not in selected:continue
        p=inputs/(key+'.tsv');cols=list(dict.fromkeys(k for r in rows for k in r))
        with p.open('x',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=cols,delimiter='\t');w.writeheader();w.writerows(rows)
        spec=copy.deepcopy(template);spec.update(figure_id=key,renderer='clarity',input=dict(path=p.name,sha256=digest(p)))
        contract=dict(source_definition='Frozen public synthetic table: '+(src.relative_to(ROOT).as_posix() if src else 'original literal fixture '+key),independent_unit='Synthetic identity only; no biological sample or scientific inference',denominator=selection,value_definition='All plotted channels supplied explicitly; exact units and source selection in FigureSpec',uncertainty_definition='Supplied display intervals or explicitly not applicable; never estimated by this renderer',synthetic=True)
        spec['parameters']=dict(view=view,options=o,contract=contract)
        cats=o.get('group_order',o.get('cohort_order',o.get('series_order',list(o.get('label_names',{}).values())))) or ['Supplied channels']
        spec['theme']=create_theme('synthetic-clarity-'+key,'package_editorial',{g:i for i,g in enumerate(cats)},font_family='DejaVu Sans')
        spec['theme']['continuous'].update(diverging=['#327D9F','#F7F7F4','#C96068'],sequential=['#F0F4F6','#436C87'])
        spec['provenance'].update(source=contract['source_definition'],filtering=selection,input_unit=contract['independent_unit'],experimental_unit=contract['independent_unit'],denominator=selection,uncertainty=contract['uncertainty_definition'],model='Frozen synthetic software example; no scientific model or native package execution',limits='Declared view options')
        spec['export']=dict(target_width_mm=178,minimum_text_pt=7.5,readability_policy='block');write(inputs/(key+'.spec.json'),spec)
        render_plan(make_plan(spec,inputs),output);receipt=output/key/(key+'.json');v=json.loads(receipt.read_text(encoding='utf8'));v['source_file']='inputs/'+p.name;write(receipt,v)
        records.append(dict(id=key,view=view,source=src.relative_to(ROOT).as_posix() if src else None,source_sha256=digest(src) if src else None,selection=selection,input_sha256=digest(p),png_sha256=digest(output/key/(key+'.png')),status='RENDERED_UNREVIEWED'))
        write(output/'manifest.json',dict(version='0.7.0',records=records,scientific_acceptance=False));print(key+' rendered',flush=True)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Clarity and extension examples</title><style>body{font:16px/1.6 system-ui;max-width:1050px;padding:24px;margin:auto;background:#edf1f3;color:#243449}article{background:white;padding:28px;margin:24px 0;border-radius:8px}img{width:100%;display:block}a{color:#176b70}.links{display:flex;gap:18px;flex-wrap:wrap}</style><h1>Clarity and extension examples</h1><p>15 frozen synthetic examples; individual sources, exact tables and explicit selection. No underlying analysis runs. Browser scaling is not a calibrated paper proof.</p>'
    for r in records:
        k=r['id'];page+='<article id="'+k+'"><h2>'+k+' · '+r['view']+'</h2><img loading="lazy" src="'+k+'/'+k+'.png" alt="'+r['view']+'"><p>'+r['selection']+'</p><div class="links">'+''.join('<a href="'+k+'/'+k+'.'+e+'">'+e.upper()+'</a>' for e in ['png','svg','pdf','tsv','json'])+'<a href="inputs/'+k+'.spec.json">SPEC</a></div></article>'
    (output/'index.html').write_text(page+'</html>',encoding='utf8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--only',nargs='+');a=p.parse_args();build(a.output,a.only)
