"""Author bounded, explicitly synthetic scale/layout fixtures for 45 renderers.

Selection is a drawing-fixture operation, never selection of a research result.
Keep complete selected identities and their auxiliary records. A few tiny legacy
examples are expanded using explicitly named display-profile copies, not new
biological units. No inference, density/interval estimation or clustering occurs.
"""
import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan
from prepare_method_upgrades import numeric,provenance


def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def unique(s):return list(dict.fromkeys(s.dropna().tolist()))


def choose(values,level,minimum=2):
    values=list(dict.fromkeys(values));n=len(values)
    count=min(n,max(minimum,math.ceil(n*(level+1)/3)))
    # Spread over the entire supplied domain, retaining both end points.
    if count==1:return values[:1]
    return [values[round(i*(n-1)/(count-1))] for i in range(count)]


def prune(obj,original,data):
    """Update only exact declared identity orders and alias dictionaries."""
    if not isinstance(obj,dict):return
    for k,v in list(obj.items()):
        if isinstance(v,list) and (k.endswith('_order') or k.endswith('_facets') or k in ('labels','order','label_ids')):
            columns=[c for c in original if set(v)==set(original[c].dropna())]
            if columns:obj[k]=[x for x in v if x in set(data[columns[0]].dropna())]
        elif isinstance(v,dict):
            columns=[c for c in original if set(v)==set(original[c].dropna())]
            if columns and k.endswith(('_slots','_aliases')):
                kept=set(data[columns[0]].dropna());obj[k]={x:y for x,y in v.items() if x in kept}
            else:prune(v,original,data)


def selected(data,field,level,strata=None,minimum=2):
    if strata:
        ids=[v for _,part in data.groupby(strata,sort=False) for v in choose(unique(part[field]),level,minimum)]
    else:ids=choose(unique(data[field]),level,minimum)
    return data[data[field].isna()|data[field].isin(ids)].copy()


def copies(data,field):
    import pandas as pd
    parts=[data.copy()]
    for n in (2,3):
        part=data.copy();part[field]=part[field].map(lambda x:f'{x} · display {n}')
        parts.append(part)
    return pd.concat(parts,ignore_index=True)


def tree_segments(count):
    """Authored balanced display tree; no distances or clustering fitted."""
    rows=[];nodes=[(float(i),0.) for i in range(count)];height=1.
    while len(nodes)>1:
        nxt=[]
        for i in range(0,len(nodes),2):
            if i+1==len(nodes):nxt.append(nodes[i]);continue
            (a,ha),(b,hb)=nodes[i:i+2]
            for x0,y0,x1,y1 in [(a,ha,a,height),(b,hb,b,height),(a,height,b,height)]:
                rows.append(dict(record_type='tree',segment_id=f'display-tree-{len(rows)}',x0=x0,y0=y0,x1=x1,y1=y1))
            nxt.append(((a+b)/2,height))
        nodes=nxt;height+=1.
    return rows


def vary(key,data,params,level):
    import pandas as pd
    original=data.copy();p=copy.deepcopy(params);d=data.copy()
    number=int(key[1:3]);definition='Complete selected frozen identities and supplied channels; no inference'
    if number==1:
        keep=set(choose(p['leaf_order'],level));by=d.set_index('node_id')
        for leaf in list(keep):
            node=leaf
            while node!=p['root_id']:
                node=by.loc[node,'parent_id'];keep.add(node)
        d=d[d.node_id.isin(keep)].copy()
        p['leaf_order']=[x for x in p['leaf_order'] if x in keep]
        dimension='tree leaves';quantity=len(p['leaf_order'])
    elif number in (2,6,8,10,13,15,17):
        field={2:'label',6:'feature',8:'category',10:'row_id',13:'object_id',15:'term_id',17:'feature'}[number]
        if level==0:d=selected(d,field,0)
        elif level==2:
            d=copies(d,field);definition='Explicit synthetic display-profile copies; original numerical channels repeated, no new biological units'
            if number==10:
                p['row_slots']={r:p['row_slots'][r.split(' · display ')[0]] for r in unique(d[field])}
        dimension=field;quantity=d[field].nunique()
        if number==15 and level==2:d['description']=d['description']+' / independently named software display copy'
    elif number in (3,42):
        d=selected(d,'gene',level);dimension='gene effects';quantity=len(d)
        if p.get('labels'):p['labels']=[x for x in p['labels'] if x in set(d.gene)]
    elif number in (4,31):
        d=selected(selected(d,'feature',level),'sample',level);dimension='features × samples';quantity=[d.feature.nunique(),d['sample'].nunique()]
    elif number==5:
        d=selected(d,'subject_id',level);dimension='paired display units';quantity=d.subject_id.nunique()
    elif number==7:
        d=selected(d,'unit_id',level,'group');dimension='points';quantity=len(d)
    elif number==9:
        if level<2:
            keep=unique(d.actual)[:2 if level==0 else 3]
            d=d[d.actual.isin(keep)&d.predicted.isin(keep)].copy()
        else:
            labels=unique(d.actual);lookup=d.set_index(['actual','predicted'])['count'];rows=[]
            for i in range(6):
                for j in range(6):rows.append(dict(actual=f'Class {i+1}',predicted=f'Class {j+1}',count=float(lookup.loc[(labels[i%len(labels)],labels[j%len(labels)])])))
            d=pd.DataFrame(rows);definition='Authored six-class software count table using repeated source count profiles; not a reclassified cohort'
        dimension='classes';quantity=d.actual.nunique()
    elif number in (11,12):
        keep=set(choose(p['leaf_order'],level));leaves=d[(d.record_type=='leaf')&d.node_id.isin(keep)].copy();out=[];represent={v:v for v in keep}
        for row in d[d.record_type=='merge'].to_dict('records'):
            a=represent.get(row['left']);b=represent.get(row['right'])
            if a and b:
                row['left']=a;row['right']=b;out.append(row);represent[row['node_id']]=row['node_id']
            elif a or b:represent[row['node_id']]=a or b
        d=pd.concat([leaves,pd.DataFrame(out)],ignore_index=True);p['leaf_order']=[v for v in p['leaf_order'] if v in keep]
        if number==12:p['label_ids']=p['leaf_order']
        definition='Induced supplied display tree; unary branches collapsed, all surviving supplied merge heights unchanged'
        dimension='tree leaves';quantity=len(keep)
    elif number==14:
        d=selected(selected(d,'term_id',level),'column_id',level);dimension='terms × result columns';quantity=[d.term_id.nunique(),d.column_id.nunique()]
    elif number in (16,26):
        d=selected(selected(d,'row',level),'column',level);dimension='matrix rows × columns';quantity=[d.row.nunique(),d.column.nunique()]
    elif number==18:
        d=selected(selected(d,'feature',level),'modality',level);dimension='features × modalities';quantity=[d.feature.nunique(),d.modality.nunique()]
    elif number==19:
        keep=choose(sorted(d.bin_left.unique()),level);d=d[d.bin_left.isin(keep)].copy()
        dimension='supplied calibration bins per model';quantity=len(keep)
        definition='Exact supplied bins spanning the original domain, all model identities retained; no rebinning or interval estimation'
    elif number==20:
        d=selected(d,'feature_id',level,'status');dimension='cross-view feature effects';quantity=len(d)
        p['label_ids']=[x for x in p.get('label_ids',[]) if x in set(d.feature_id)]
    elif number==21:
        d=selected(d,'object_id',level,'group');dimension='objects × coordinate views';quantity=[d.object_id.nunique(),d.view.nunique()]
    elif number==22:
        kind=d.record_type.eq('signal') if 'signal' in set(d.record_type) else d.record_type.eq('bin')
        if kind.any():
            keep=choose(sorted(d.loc[kind,'start'].unique()),level);d=d[~kind|d.start.isin(keep)].copy()
        else:
            tracks=unique(d.track);keep=choose(tracks,level);d=d[d.track.isna()|d.track.isin(keep)].copy();p['track_order']=[v for v in p['track_order'] if v in keep]
        dimension='physical track records';quantity=len(d)
    elif number==23:
        ids=choose(unique(d.loc[d.record_type=='association','variant_id']),level)
        ids=list(dict.fromkeys(ids+[p['ld_reference']]))
        d=d[(d.record_type!='association')|d.variant_id.isin(ids)].copy();dimension='supplied variants';quantity=len(ids)
        p['recombination_unit']='Supplied rate (a.u.)'
    elif number==24:
        keep=choose(sorted(d.x.unique()),level);d=d[d.x.isin(keep)].copy();dimension='stored x vertices per group/coverage';quantity=len(keep)
    elif number==25:
        keep=choose(unique(d.loc[d.record_type=='node','node_id']),level,3)
        d=d[((d.record_type=='node')&d.node_id.isin(keep))|((d.record_type=='edge')&d.source.isin(keep)&d.target.isin(keep))].copy()
        dimension='nodes and all supplied selected-subgraph edges';quantity=[len(keep),int((d.record_type=='edge').sum())]
    elif number==27:
        curve=d.record_type.eq('running');keep=choose(sorted(d.loc[curve,'rank'].unique()),level,8)
        d=d[~curve|d['rank'].isin(keep)].copy();dimension='stored curve vertices';quantity=int(curve.sum()) if not keep else len(keep)
        definition='Selected exact full-domain curve vertices; all supplied hit/auxiliary records retained, no GSEA recomputation'
    elif number==28:
        xs=choose(sorted(d.x.unique()),level,6);ys=choose(sorted(d.y.unique()),level,6);d=d[d.x.isin(xs)&d.y.isin(ys)].copy()
        dimension='supplied rectangular field grid';quantity=[len(xs),len(ys)]
    elif number==29:
        parts=[];stride=[3,2,1][level]
        for kind,part in d.groupby('record_type',sort=False):
            if kind=='surface':
                for _,s in part.groupby('surface_id',sort=False):
                    xs=sorted(s.x.unique())[::stride];ys=sorted(s.y.unique())[::stride];parts.append(s[s.x.isin(xs)&s.y.isin(ys)])
            elif kind=='path':
                for _,s in part.groupby('object_id',sort=False):
                    indices=list(range(0,len(s),stride));indices=sorted(set(indices+[len(s)-1]));parts.append(s.iloc[indices])
            else:parts.append(part)
        d=pd.concat(parts,ignore_index=True);dimension='stored schematic vertices and supplied surface samples';quantity=len(d)
        definition='All nodes, edges, matrix cells, landmarks and counts retained; only exact path/surface sampling density varies'
    elif number==30:
        keep=choose(sorted(d.x.unique()),level,4);d=d[d.x.isin(keep)].copy();dimension='stored curve vertices per model';quantity=len(keep)
    elif number==32:
        labels=choose(p['labels'],level,3);d=d[((d.record_type=='correlation')&d.a.isin(labels)&d.b.isin(labels))|((d.record_type=='mantel')&d.target.isin(labels))].copy();p['labels']=labels
        dimension='variables × supplied specimen sets';quantity=[len(labels),len(p['specimen_order'])]
    elif number==33:
        d=selected(selected(d,'feature',level),'unit_id',level);dimension='features × complete contribution units';quantity=[d.feature.nunique(),d.unit_id.nunique()]
    elif number==34:
        pts=d[d.record_type=='point'];chosen=selected(pts,'unit_id',level,'group')
        d=pd.concat([chosen,d[d.record_type!='point']],ignore_index=True)
        p['ellipse_label']='Supplied reference contours; not refitted for selected points'
        dimension='stored points; all reference contours retained';quantity=len(chosen)
    elif number==35:
        st=d[d.record_type=='state'];keep=[v for _,q in st.groupby('family',sort=False) for v in choose(unique(q.state),level)]
        emb=d[d.record_type=='embedding'];emb=selected(emb,'unit_id',level,'family')
        d=pd.concat([d[(d.record_type!='embedding')&d.state.isin(keep)],emb],ignore_index=True)
        dimension='states and stored embedding points';quantity=[len(keep),len(emb)];p['size']=[12,max(7,3+len(keep)*.24)]
    elif number==36:
        classes=choose(p['class_order'],level,1);d=d[d['class'].isin(classes)].copy();p['class_order']=classes
        p['feature_orders']={c:p['feature_orders'][c] for c in classes}
        dimension='classes with complete contribution and share channels';quantity=len(classes)
    elif number==37:
        atlas=choose(p['atlas_order'],level,4);main=p['main_order'][:[4,8,len(p['main_order'])][level]]
        keep=d.layer.eq('atlas')&d.group.isin(atlas)|d.layer.eq('main')&d.group.isin(main)|d.record_type.isin(['leaf','marker'])&d.group.isin(main)
        if level==2:keep|=d.record_type.eq('tree');d=d[keep].copy()
        else:
            d=d[keep].copy();d=pd.concat([d,pd.DataFrame(tree_segments(len(main)))],ignore_index=True)
        p['atlas_order']=atlas;p['main_order']=main;dimension='atlas categories × main identities';quantity=[len(atlas),len(main)]
        definition='Complete selected point/count/marker identities; smaller examples use an explicitly authored balanced display tree, no clustering'
    elif number==38:
        epochs=choose(sorted(d.epoch.unique()),level,12);epochs=sorted(set(epochs+[p['selected_epoch']]))
        runs=choose(unique(d.loc[d.record_type=='heat','run']),level,3)
        d=d[d.epoch.isin(epochs)&((d.record_type!='heat')|d.run.isin(runs))].copy();dimension='stored epochs × diagnostic runs';quantity=[len(epochs),len(runs)]
    elif number==39:
        rowdata=d[d.record_type=='row'];rows=[v for _,q in rowdata.groupby('group',sort=False) for v in choose(unique(q.row),level,2)]
        columns=choose(p['column_order'],level,4)
        d=d[(d.record_type.isin(['row','matrix'])&d.row.isin(rows)&(d.column.isna()|d.column.isin(columns)))|(d.record_type=='top')&d.column.isin(columns)|(d.record_type=='density')].copy()
        p['row_order']=[v for v in p['row_order'] if v in rows];p['column_order']=columns
        p['column_aliases']={v:p['column_aliases'][v] for v in columns};p['size']=[12,max(8,3.5+len(rows)*.17)]
        dimension='matrix rows × columns';quantity=[len(rows),len(columns)]
    elif number==40:
        rows=choose(p['row_order'],level,4);d=d[d.row.isin(rows)].copy();p['row_order']=rows;p['size']=[13,max(6,2+len(rows)*.28)]
        dimension='outcomes × complete effect panels';quantity=[len(rows),len(p['panel_order'])]
    elif number==41:
        features=choose(p['feature_order'],level,2);windows=choose(p['window_order'],level,2)
        d=d[d.feature.isin(features)&d.window.isin(windows)].copy();p['feature_order']=features;p['window_order']=windows
        dimension='features × windows per complete facet';quantity=[len(features),len(windows)]
    else:raise ValueError('Missing scale contract: '+key)
    prune(p,original,d)
    if 'feature_order' in p and 'feature' in d:p['feature_order']=[v for v in p['feature_order'] if v in set(d.feature.dropna())]
    for name,field in [('object_order','object_id'),('row_order','row_id'),('column_order','column_id'),('term_order','term_id')]:
        if name in p and field in d:
            old=list(p[name]);p[name]=[v for v in old if v in set(d[field].dropna())]
            p[name]+=[v for v in unique(d[field]) if v not in p[name]]
    return d,p,dict(dimension=dimension,quantity=quantity,rows=len(d),preparation=definition)


def prepare(out,methods=None):
    import pandas as pd
    from render_frozen_table import load_table
    out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    gallery=SKILL/'assets/method-upgrade-gallery';base=[r for r in read(gallery/'manifest.json')['records'] if not r['variant']]
    if methods:base=[r for r in base if r['id'] in methods]
    records=[]
    for row in base:
        source=gallery/row['assets']['spec'];original=read(source);table=source.parent/original['input']['path']
        data=load_table(table,original['renderer'],original['parameters'],original['input']['numeric_columns'])
        variants=[]
        for level,name in enumerate(['Small','Medium','Large']):
            if row['id'].startswith('H'):
                d,p,volume=vary(row['id'],data,original['parameters'],level)
            else:
                d=data.copy();p=copy.deepcopy(original['parameters'])
                if row['id']=='D01_Scatter3D':
                    d=selected(d,'object_id',level,'group');volume=dict(dimension='stored XYZ objects',quantity=len(d),rows=len(d),preparation='Complete selected original coordinate records; no embedding fit')
                elif row['id']=='D02_Volume':
                    n=[8,16,24][level];extent=4.025;rows=[]
                    for i in range(n):
                        for j in range(n):
                            for k in range(n):
                                x,y,z=[-extent+2*extent*v/(n-1) for v in [i,j,k]]
                                value=math.exp(-((x+1.1)**2/2+(y-.1)**2/3+(z+.5)**2/1.2))+.68*math.exp(-((x-1.25)**2/1.1+(y+.45)**2/1.9+(z-.8)**2/2.2))
                                rows.append(dict(x=x,y=y,z=z,value=value))
                    d=pd.DataFrame(rows);volume=dict(dimension='uniform grid with identical physical extent',quantity=[n,n,n],rows=len(d),preparation='Authored analytic drawing field sampled before freezing; not measured anatomy or resampled private data')
                    p['transfer']=[dict(value=v,color=c,opacity=a) for v,c,a in [(0,'#FFFFFF',0),(.15,'#D7EBEE',.015),(.35,'#71B7C7',.08),(.65,'#2691AA',.24),(.92,'#365BA1',.55),(1.2,'#804B8D',.85)]]
                    p.update(camera_views=[[25,-55]],views=['z+'],slice_axes=['y'])
                else:
                    frames=p['frame_order'][:[6,12,24][level]];p['frame_order']=frames
                    d=d[d.record_type.eq('bond')|d.frame_id.isin(frames)].copy()
                    volume=dict(dimension='complete atom frames',quantity=[len(frames),int(d.loc[d.record_type=='atom','atom_id'].nunique())],rows=len(d),preparation='Complete original frames, explicit topology and unaltered physical time')
            if row['id']=='H34_pca_reference':p['spider']=False;p['landscape']=True
            if row['id']=='H28_contour_field':p['label_contrast']='halo'
            if row['id']=='H29_process_dashboard':p.update(presentation='reading',columns=3,width=14.5)
            if row['id']=='H36_multiclass_contributions':p.update(presentation='reading',columns='auto')
            variants.append((name,d,p,volume))
        name,d,p,volume=copy.deepcopy(variants[-1]);name='Custom'
        layout=dict(width_inches=[9.75,14.25,11.75][len(records)//4%3])
        if row['id']=='H21_aligned_views':p.update(columns=1,rows=3,width=9);layout=None
        elif row['id']=='H29_process_dashboard':p.update(columns=2,width=11.75);layout=None
        elif row['id']=='H36_multiclass_contributions':p.update(columns=2,size=[12,9]);layout=None
        elif row['id']=='H15_term_key':p.update(width=10.5);layout=None
        if row['id']=='D01_Scatter3D':p.update(views=[[18,-55],[30,35],[65,-80]],columns=3,rows=2,width=14,panel_height=3.6);layout=None
        elif row['id']=='D02_Volume':p.update(camera_views=[[25,-55],[18,30]],views=['z+','x-'],slice_axes=['x','y','z'],columns=2,rows=4,width=11.5);layout=None
        elif row['id']=='D03_Trajectory':p.update(key_frames=p['frame_order'][::4],columns=3,rows=2,width=14.5,view=[35,-45],panel_height=2.65);layout=None
        variants.append((name,d,p,volume))
        for name,d,p,volume in variants:
            key='Scale_'+row['id']+'_'+name;folder=out/key;folder.mkdir();table=folder/'example.tsv'
            d.to_csv(table,sep='\t',index=False,lineterminator='\n')
            spec=copy.deepcopy(original);spec.update(figure_id=key,parameters=p,provenance=provenance())
            if row['id'] in ('H05_paired','H27_running_enrichment'):
                # Two named identities get an explicit contrasting identity
                # palette. This does not declare biological effect direction.
                spec['theme']['category_colors']=dict(spec['theme'].get('category_colors',{}),G1='#467E9D',G2='#CF7E68')
            spec['provenance']['source']='Public authored drawing fixture; '+volume['preparation']
            spec['input']=dict(path=table.name,sha256=sha(table),numeric_columns=numeric(table),max_rows=100000,max_bytes=20*1024**2)
            spec['export']=dict(raster_dpi=300,readability_policy='warn')
            spec.pop('layout',None)
            if name=='Custom' and layout:spec['layout']=layout
            make_plan(spec,folder);write(folder/'example.spec.json',spec)
            records.append(dict(id=key,renderer=spec['renderer'],form=row['form'],method_id=row['id'],variant=name,title=row['title'],volume=volume,spec=key+'/example.spec.json',input_sha256=sha(table)))
        print(row['id']+' FROZEN',flush=True)
    write(out/'manifest.json',dict(records=records,methods=len(base),native_examples=len(records),scientific_acceptance=False))
    print(json.dumps(dict(state='METHOD_SCALE_INPUTS_FROZEN',methods=len(base),examples=len(records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--methods',nargs='*');a=p.parse_args();prepare(a.output,a.methods)
