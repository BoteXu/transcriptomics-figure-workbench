"""Executable within-method companions, reusing frozen public inputs and renderers."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))

def build(out,base_spec,chapters=None):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    from full_layout_cases import cases
    out.mkdir(parents=True,exist_ok=False);base=json.loads(base_spec.read_text(encoding='utf8'));records=[]
    def add(k,d,renderer,params,chapters,theme=None):
        folder=out/k;folder.mkdir();s=copy.deepcopy(base);raw=table_bytes(d);(folder/'example.tsv').write_bytes(raw)
        s.update(figure_id=k,renderer=renderer,parameters=params);s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in d if pd.api.types.is_numeric_dtype(d[c])]);s['export'].update(target_width_mm=297,minimum_text_pt=7.5,raster_dpi=300,readability_policy='block');s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        if theme:s['theme']=copy.deepcopy(theme)
        s['provenance'].update(source='Fictional frozen method-depth display inputs v0.9.1',model='No analysis, graph inference, model fit or significance calculation',synthetic=True)
        (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8');records.append(dict(id=k,spec=k+'/example.spec.json',assay='method_depth',chapters=chapters,title=params.get('title',k),renderer=renderer))
    levels=['Resolution 0.2','Resolution 0.5','Resolution 0.8'];base['theme']['group_slots'].update({x:i for i,x in enumerate(levels)});base['theme']['group_slots'].update({'Root state':0,'Branch A':1,'Branch B':2})
    nodes=[('A',levels[0],0,120),('B',levels[0],2,120),('A1',levels[1],-.4,70),('A2',levels[1],.8,50),('B1',levels[1],2,120),('A1a',levels[2],-.7,45),('A1b',levels[2],.1,40),('A2a',levels[2],1,35),('B1a',levels[2],1.8,70),('B1b',levels[2],2.8,50)]
    edges=[('A','A1',70),('A','A2',50),('B','B1',120),('A1','A1a',45),('A1','A1b',25),('A2','A1b',15),('A2','A2a',35),('B1','B1a',70),('B1','B1b',50)]
    cluster=pd.DataFrame([dict(record_type='node',node=k,level=l,x=x,n=n) for k,l,x,n in nodes]+[dict(record_type='edge',source=a,target=b,n=n) for a,b,n in edges])
    for cols in [2,1]:add('ClusterFlow_'+str(cols)+'Column',cluster,'figure_lineage_views.plot_lineage_view',dict(mode='cluster_tree',title='Resolution changes · cell flows and cluster sizes',definition='Fictional complete cell counts, adjacent-resolution flows and frozen layout; no cluster stability inference',level_order=levels,columns=cols),['single_cell.resolution'])
    rr=[]
    for i in range(240):
        t=i/239;branch='Root state' if t<.35 else 'Branch A' if i%2 else 'Branch B';x=4*t;y=0 if branch=='Root state' else (1 if branch=='Branch A' else -1)*(t-.35)*2
        rr.append(dict(record_type='cell',cell='C'+str(i),branch=branch,x=x+.04*np.sin(i*1.3),y=y+.07*np.cos(i*.9),pseudotime=t,donor='D'+str(i%12+1)))
    rr.extend(dict(record_type='node',node=k,x=x,y=y) for k,x,y in [('Root',0,0),('Fork',1.4,0),('A',4,1.3),('B',4,-1.3)]);rr.extend(dict(record_type='edge',source=a,target=b) for a,b in [('Root','Fork'),('Fork','A'),('Fork','B')]);trajectory=pd.DataFrame(rr)
    for cols in [2,1]:add('Trajectory_'+str(cols)+'Column',trajectory,'figure_lineage_views.plot_lineage_view',dict(mode='trajectory',title='Branch identity and progression · shared frozen graph',definition='Fictional rooted graph and pseudotime; no trajectory or lineage inference',root_id='Root',value_limits=[0,1],columns=cols),['single_cell.trajectory'])
    if chapters:
        for chapter,key,excluded in [('single_cell.trajectory','Trajectory_GeneDynamics',{'embedding'}),('single_cell.resolution','Resolution_DonorSupport',{'network'})]:
            p=chapters/chapter/'example.spec.json';s=json.loads(p.read_text(encoding='utf8'));params=copy.deepcopy(s['parameters']);params['panels']=[q for q in params['panels'] if q['kind'] not in excluded];params['title']='Gene progression on supplied branches' if chapter.endswith('trajectory') else 'Cluster support by donor';params['columns']='auto';d=pd.read_csv(p.parent/s['input']['path'],sep='\t');d=d[d.panel_id.isin([q['id'] for q in params['panels']])].copy()
            if chapter.endswith('resolution'):
                d['value']=[24+int(i%7)*8 for i in range(len(d))];params['panels'][0].update(value_label='Supplied cell count per donor',limits=[0,80])
            add(key,d,s['renderer'],params,[chapter],s['theme'])
    base['theme']['group_slots'].update({'Selected HVG':0,'Other features':2})
    hvg=pd.DataFrame([dict(panel_id='P1',series='Selected HVG' if i%5==0 else 'Other features',x=float(i/50),y=float(.4+.12*(i/50)**2+(.7 if i%5==0 else .12)*abs(np.sin(i*.57)))) for i in range(400)])
    add('HVG_MeanDispersion',hvg,'figure_chapter_views.plot_transcriptomic_chapter',dict(title='Variable features · supplied mean and normalized dispersion',scope_note='Fictional frozen feature selection · no HVG estimation',panels=[dict(id='P1',kind='points',title='Full supplied feature scope',x_label='Supplied mean expression',y_label='Supplied normalized dispersion',point_unit='Gene')],columns=1),['single_cell.hvg_pca'])
    wanted={'figure_analysis_results.plot_splice_tracks':['bulk.splicing','single_cell.splicing','bulk.dtu'],
      'figure_multiomics_views.plot_diagnostic_panel':['bulk.model_qc'],
      'figure_gsea.plot_gsea_leading_edge':['bulk.gsea','single_cell.pathways'],
      'figure_network_extensions.plot_upset':['bulk.differential','bulk.ora','single_cell.multi_contrast'],
      'figure_method_extensions.plot_gene_term_chord':['bulk.gene_support','single_cell.gene_support'],
      'figure_network_extensions.plot_alluvial':['single_cell.annotation','single_cell.vdj'],
      'figure_method_extensions.plot_vector_field':['single_cell.velocity']}
    seen=set()
    for row in cases(include_all=True):
        if row.get('adapter') not in wanted or row['route']!='native':continue
        key=(row['adapter'],row['parameters'].get('mode',''))
        if key in seen:continue
        seen.add(key);params=copy.deepcopy(row['parameters']);k='Method_'+row['example']
        # Reuse exact input parsing from its frozen typed specification.
        from render_frozen_table import load_table
        d=load_table(ROOT/row['table'],row['adapter'],params,params.get('set_columns',[]))
        if row['adapter']=='figure_multiomics_views.plot_diagnostic_panel':params['title']='Frozen model check · '+params['mode'].replace('_',' ')
        add(k,d,row['adapter'],params,wanted[row['adapter']],row['theme'])
    (out/'manifest.json').write_text(json.dumps(dict(records=records,analysis_performed=False),indent=2)+'\n',encoding='utf8');print(json.dumps(dict(method_depth_figures=len(records),actual_analysis=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--base-spec',required=True,type=Path);p.add_argument('--chapters',type=Path);a=p.parse_args();build(a.output,a.base_spec,a.chapters)
