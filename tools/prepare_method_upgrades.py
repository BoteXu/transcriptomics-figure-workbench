"""Migrate 42 actual frozen recipes and author 3D drawing fixtures; no inference."""
import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(S/'scripts'))
from figure_workbench.contracts import make_plan
from full_layout_cases import cases


def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def provenance():
    return dict(source='Frozen public software fixture; all objects and values are illustrative',
        input_unit='Explicit display records with declared physical or synthetic units',
        experimental_unit='No real biological independent units; no scientific inference',
        contrast='Declared illustrative comparison; preserve original values and complete selected scope',
        denominator='Every row of the exact frozen selected input table',model='No scientific model fitted',
        limits='Software and visual demonstration, not biomedical evidence',filtering='No filtering while drawing',
        uncertainty='Only supplied uncertainty channels; no interval estimation',
        interpretation_limit='Review new data, units, layout and intended display size separately',synthetic=True)


IDENTITY=set('record_type kind panel frame_id atom_id element chain source_id target_id object_id group id label gene feature sample cell_id sample_id unit_id feature_id term term_id gene_id category series condition source target node_id chromosome transcript_id track track_id family'.split())
def numeric(path):
    with path.open(encoding='utf8',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;rows=list(reader)
    result=[]
    for c in fields:
        if c in IDENTITY or c.endswith('_id'):continue
        vals=[r[c] for r in rows if r[c]]
        if not vals:continue
        try:
            for v in vals:float(v)
        except ValueError:continue
        result.append(c)
    return result


def table(p,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)


def prepare(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    registry=read(S/'references/renderer-registry.json');aliases=registry['aliases']
    baseline=S/'references/historical-upgrade-baseline.json'
    routes=cases(include_all=True)
    if not baseline.is_file():
        previous=read(S/'assets/visual-library/manifest.json')['renderer_coverage'];records=[]
        for item in previous:
            if item['state']!='HISTORICAL_RECIPE':continue
            route=next(r for r in routes if aliases.get(r.get('adapter'),{}).get('renderer',r.get('adapter'))==item['renderer'])
            records.append(dict(renderer=item['renderer'],original_id=route['example'],base_form=route['base_form'],input_sha256=sha(ROOT/route['table'])))
        if len(records)!=42:raise ValueError('Freeze the original 42-recipe inventory before rebuilding coverage')
        write(baseline,dict(records=records,source_state='HISTORICAL_RECIPE',expected_count=42))
    records=[]
    def emit(key,renderer,params,theme,form,source=None,rows=None,variant=False,layout=None,original=None):
        folder=out/key;folder.mkdir();p=folder/'example.tsv'
        if source:p.write_bytes(source.read_bytes())
        else:table(p,rows)
        spec=dict(schema_version=1,figure_id=key,renderer=renderer,
                  input=dict(path='example.tsv',sha256=sha(p),numeric_columns=numeric(p),max_rows=100000,max_bytes=20*1024**2),
                  parameters=params,theme=theme,provenance=provenance(),export=dict(raster_dpi=300,readability_policy='warn'))
        if layout:spec['layout']=layout
        if renderer=='figure_reference.plot_activity_dashboard':spec['appearance']=dict(preset='compact')
        make_plan(spec,folder);write(folder/'example.spec.json',spec)
        records.append(dict(id=key,renderer=renderer,form=form,title=key.replace('_',' '),variant=variant,
                            upgraded_from=original,source_sha256=sha(p),spec=key+'/example.spec.json'))
    for i,b in enumerate(read(baseline)['records']):
        route=next(r for r in routes if r['example']==b['original_id']);source=ROOT/route['table']
        if sha(source)!=b['input_sha256']:raise ValueError('Historical frozen source changed')
        name=f'H{i+1:02d}_'+b['renderer'].split('.')[-1].removeprefix('plot_')
        theme=copy.deepcopy(route['theme']);theme['font_family']='DejaVu Sans'
        params=copy.deepcopy(route['parameters'])
        if b['renderer']=='figure_core.plot_forest':params['presentation']='table'
        if b['renderer']=='figure_linked_evidence.plot_radial_hierarchy':params.update(numeric_guides=True,label_ids=params['leaf_order'])
        if b['renderer']=='figure_multiomics_views.plot_aligned_views':params['guide_clearance_pt']=28
        if b['renderer']=='figure_network_extensions.plot_contour_field':params['label_contrast']='clear'
        if b['renderer'] in ['figure_reference.plot_state_dashboard','figure_reference.plot_multiclass_contributions','figure_reference.plot_embedding_atlas','figure_reference.plot_effect_distribution_forest']:params['numeric_guides']=True
        if b['renderer']=='figure_reference.plot_training_dashboard':params['presentation']='balanced'
        if b['renderer']=='figure_reference.plot_activity_dashboard':
            # A 150-row reading page keeps every row ID legible. Column aliases
            # are declared one-to-one labels, never changes to source IDs/data.
            params.update(size=[12,36],column_label_rotation=90,row_strip_left=.015,column_aliases={c:c.replace('Column','C') for c in params['column_order']})
        # The old generic theme lacked named identities used by several
        # explicit palettes. Bind the source's own names and colours exactly;
        # do not infer identities from artist order or recolour by row index.
        for field in ['palette','stack_palette','group_palette','celltype_palette']:
            if isinstance(params.get(field),dict):
                theme.setdefault('category_colors',{}).update(params[field])
        emit(name,b['renderer'],params,theme,b['base_form'],source=source,original=b['original_id'])
        # Caller-controlled physical width changes; the complete data remain
        # byte-identical. A separate SVG composition exercises rows/columns.
        custom=copy.deepcopy(params)
        if b['renderer']=='figure_reference.plot_activity_dashboard':custom.update(size=[13.5,9.5],row_label_mode='none')
        layout=dict(width_inches=11.5)
        if b['renderer']=='figure_general.plot_confusion_counts':layout['height_inches']=8.5
        if b['renderer']=='figure_publication.plot_publication_curve':layout.update(width_inches=8.5,height_inches=8.5)
        emit(name+'_Custom',b['renderer'],custom,theme,b['base_form'],source=source,variant=True,
             layout=layout,original=b['original_id'])
    from project_theme import create_theme
    theme=create_theme('synthetic-three-dimensional','package_editorial',{'State A':0,'State B':1,'State C':2},font_family='DejaVu Sans')
    # Coordinates and fields are authored drawing fixtures, not inferred PCs,
    # estimated biological volumes, generated conformers or an MD simulation.
    scatter=[]
    for g in range(3):
        for j in range(48):
            t=j*.47;scatter.append(dict(object_id=f'Obj{g+1}_{j+1:03d}',group=f'State {chr(65+g)}',x=2.1*g+math.cos(t)*(.4+j*.009),y=math.sin(t)*.8+.15*g,z=(j-24)*.045+math.sin(t*.6)*.35))
    scatter_p=dict(axis_labels=['X','Y','Z'],coordinate_unit='a.u.',coordinate_definition='Authored frozen point coordinates; no embedding or fit',title='Three-dimensional state geometry')
    emit('D01_Scatter3D','figure_three_dimensional.plot_scatter3d',scatter_p,theme,'scatter3d',rows=scatter)
    emit('D01_Scatter3D_Custom','figure_three_dimensional.plot_scatter3d',dict(scatter_p,columns=1,views=[[28,-35]],include_projections=True),theme,'scatter3d',rows=scatter,variant=True)
    emit('D01_Scatter3D_Small','figure_three_dimensional.plot_scatter3d',dict(scatter_p,views=[[16,35],[28,-65]],include_projections=False,columns=2),theme,'scatter3d',rows=[r for i,r in enumerate(scatter) if i%6==0],variant=True)
    volume=[];n=24
    for i in range(n):
        for j in range(n):
            for k in range(n):
                x,y,z=[(v-(n-1)/2)*.35 for v in [i,j,k]]
                value=math.exp(-((x+1.1)**2/2.0+(y-.1)**2/3.0+(z+.5)**2/1.2))+.68*math.exp(-((x-1.25)**2/1.1+(y+.45)**2/1.9+(z-.8)**2/2.2))
                volume.append(dict(x=x,y=y,z=z,value=value))
    vp=dict(coordinate_unit='mm',value_label='Illustrative scalar (a.u.)',value_limits=[0,1.2],opacity_unit_distance=.35,
            transfer=[dict(value=0,color='#F4F6F8',opacity=0),dict(value=.12,color='#C2D5DE',opacity=.005),dict(value=.45,color='#6A9FB2',opacity=.09),dict(value=.85,color='#297F8B',opacity=.26),dict(value=1.2,color='#D98665',opacity=.55)],
            volume_definition='Complete authored regular grid; not measured tissue or segmented anatomy',title='Volume structure and declared opacity')
    emit('D02_Volume','figure_three_dimensional.plot_volume_rendering',vp,theme,'volume-rendering',rows=volume)
    emit('D02_Volume_Custom','figure_three_dimensional.plot_volume_rendering',dict(vp,views=['z-','x+'],slice_axes=['z','x'],columns=1),theme,'volume-rendering',rows=volume,variant=True)
    small=[r for i,r in enumerate(volume) if (i//(n*n))%2==0 and (i//n)%2==0 and i%2==0]
    emit('D02_Volume_Small','figure_three_dimensional.plot_volume_rendering',dict(vp,views=['y-'],columns=2),theme,'volume-rendering',rows=small,variant=True)
    trajectory=[];frames=[f'F{i:02d}' for i in range(24)]
    for f,frame in enumerate(frames):
        phase=2*math.pi*f/len(frames)
        for a in range(24):
            theta=a*.59;trajectory.append(dict(record_type='atom',frame_id=frame,time=f*.5,atom_id=f'A{a+1:02d}',element=['C','C','N','C','O','C'][a%6],chain='A',x=a*.37-4.2,y=1.3*math.cos(theta)+.24*math.sin(phase+a*.13),z=1.3*math.sin(theta)+.32*math.cos(phase+a*.11)))
    for a in range(23):trajectory.append(dict(record_type='bond',source_id=f'A{a+1:02d}',target_id=f'A{a+2:02d}'))
    tp=dict(frame_order=frames,coordinate_unit='Å',time_unit='ps',topology_definition='Explicit fictional chain and connectivity, not an identified protein',
            coordinate_definition='Authored stored coordinate frames; no MD or conformer generation',periodic_boundary_handling='Fictional nonperiodic coordinates; no reimaging applied',title='Stored molecular frames · fixed camera')
    emit('D03_Trajectory','figure_three_dimensional.plot_molecular_trajectory',tp,theme,'molecular-trajectory',rows=trajectory)
    emit('D03_Trajectory_Custom','figure_three_dimensional.plot_molecular_trajectory',dict(tp,key_frames=frames[::4],columns=2,view=[18,-95]),theme,'molecular-trajectory',rows=trajectory,variant=True)
    emit('D03_Trajectory_Small','figure_three_dimensional.plot_molecular_trajectory',dict(tp,frame_order=frames[:6],key_frames=frames[:2],columns=1,animation_fps=6),theme,'molecular-trajectory',rows=[r for r in trajectory if r['record_type']=='bond' or r['frame_id'] in frames[:6]],variant=True)
    write(out/'manifest.json',dict(records=records,baseline_recipes=42,new_methods=3,scientific_acceptance=False))
    print(json.dumps(dict(state='FROZEN_UPGRADES_PREPARED',figures=len(records),output=str(out))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();prepare(a.output)
