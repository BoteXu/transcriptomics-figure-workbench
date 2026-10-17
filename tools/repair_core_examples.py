"""Prepare new revisions of explicitly fictional core gallery examples.

Never accepts research tables. Existing inputs and exports are left intact until
the revised artifacts have their own hash-bound visual review.
"""
import argparse,copy,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'

def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def repair(key,s,d):
    p=s['parameters'];panels=p.get('panels',[])
    def edit(index,**kw):panels[index].update(kw)
    def select(index):return d.panel_id==panels[index]['id']
    if key=='bulk.filtering.p1':edit(1,title='Selected gene effects',x_label='Log2 fold change · supplied 95% interval')
    measurements={'bulk.gsva.p1':('GSVA score','GSVA-score difference'),
        'bulk.tf_activity.p1':('Footprint activity score','Footprint-score difference'),
        'bulk.noncoding.p1':('Centered log2 RNA expression','Log2 RNA fold change'),
        'single_cell.states.p1':('State-program score','State-score difference'),
        'single_cell.regulons.p1':('Standardized regulon activity','Standardized activity difference')}
    if key in measurements:
        a,b=measurements[key];edit(0,value_label=a);edit(1,x_label=b+' · supplied 95% interval')
        if key=='bulk.gsva.p1':d.loc[select(0),'value']/=2;edit(0,limits=[-1,1])
    if key=='bulk.dtu.p1':
        edit(0,title='STAT1 within-gene transcript usage',x_label='Fraction of quantified STAT1 transcripts')
        edit(1,title='STAT1 transcript-usage contrasts',x_label='ln(Treated fraction / Control fraction)\nSupplied 95% interval')
        ix=d.index[select(1)];values=np.log([2/3,4/3,1]);d.loc[ix,'x']=values;d.loc[ix,'lower']=values-.18;d.loc[ix,'upper']=values+.18
    if key=='bulk.timecourse.p1':
        edit(0,title='STAT1 longitudinal predictions',y_label='Log2 STAT1 expression')
        edit(1,title='Gene condition-by-time contrasts',x_label='Log2 interaction contrast · 95% interval')
        d.loc[select(0),'series']=d.loc[select(0),'series'].replace({'Program A':'Control','Program B':'Treated'})
    if key in ['bulk.replication.p1','single_cell.replication.p1']:
        edit(0,title='STAT1 effects across cohorts',x_label='STAT1 log2 fold change · 95% interval')
        edit(1,title='Gene effects in the same cohorts',value_label='Log2 fold change')
        m=select(1)&(d.label=='STAT1');d.loc[m,'value']=[.55,.58,.61]
        ix=d.index[select(0)];d.loc[ix,'x']=[.55,.58,.61,.58];d.loc[ix,'lower']=d.loc[ix,'x']-.18;d.loc[ix,'upper']=d.loc[ix,'x']+.18
        p['scope_note']='Fictional donor-level effects · three independent cohorts · STAT1 shown in both panels'
    if key=='bulk.connectivity.p1':edit(1,title='Signed connection scores by context')
    if key=='single_cell.integration.p1':
        edit(1,title='Normalized integration diagnostics',value_label='Supplied normalized score [0,1]',limits=[0,1])
        labels=['Batch mixing','Celltype conservation','Donor conservation']
        vals=[[.28,.82],[.91,.87],[.86,.84]]
        for label,values in zip(labels,vals):d.loc[select(1)&(d.label==label),'value']=values
        p['scope_note']='Fictional frozen coordinates · normalized diagnostics; larger is better within each declared metric'
    if key=='single_cell.hvg_pca.p1':
        edit(0,x_label='Principal component',y_label='Explained variance (%)')
        edit(1,title='Selected ordinary PCA loadings',value_label='Unit-vector loading',limits=[-1,1])
        for j,name in enumerate(['PC1','PC2','PC3']):
            ix=d.index[select(1)&(d.series==name)];vals=np.array([math.cos(math.pi*(i+.5)*(j+1)/len(ix)) for i in range(len(ix))]);d.loc[ix,'value']=vals/np.linalg.norm(vals)
    if key=='Resolution_DonorSupport':
        for panel in panels:panel['value_label']='Cells per donor and cluster';panel['limits']=[0,12]
        d['value']=[3+(i*3)%8 for i in range(len(d))]
    if key=='single_cell.multi_contrast.p1':
        edit(0,title='STAT1 celltype-by-contrast effects',value_label='STAT1 log2 fold change')
        edit(1,title='STAT1 primary contrast by identity',x_label='STAT1 log2 fold change · 95% interval')
        primary=d[select(0)&(d.series=='Contrast A')].set_index('label').value
        for ix in d.index[select(1)]:
            v=primary[d.loc[ix,'label']];d.loc[ix,['x','lower','upper']]=[v,v-.22,v+.22]
    if key in ['single_cell.pathways.complete','single_cell.gene_support.complete']:
        p['title']='T-cell donor pathways across specified contrasts' if 'pathways' in key else 'T-cell pathway-supporting gene responses'
        if 'definition' in p:p['definition']+=' Selected identity: T cells; contrasts refer to independent donor aggregates.'
    if key=='Trajectory_GeneDynamics':
        p['title']='Branch program and gene progression'
        edit(0,title='Interferon-program branch progression',y_label='Supplied interferon-program score')
    if key=='single_cell.velocity.p1':
        edit(1,title='Illustrative STAT1 / IRF7 phase portraits',x_label='Normalized spliced counts',y_label='Normalized unspliced counts')
        d.loc[select(1),'series']=d.loc[select(1),'series'].replace({'Gene A':'STAT1','Gene B':'IRF7'})
        s['theme']['group_slots'].update(STAT1=0,IRF7=1)
    if key=='single_cell.communication.p1':
        edit(0,title='Sender–receiver normalized support',x_label='Receiver',y_label='Sender',value_label='Normalized interaction support',limits=[0,1])
        edit(1,value_label='Normalized LR support',limits=[0,1],size_label='Donor support',fraction_definition='Explicit fraction of fictional donors supporting this ligand–receptor pair')
        d['value']/=2
        d['label']=d.label.replace(dict(zip(['L1 - R1','L2 - R2','L3 - R3','L4 - R4','L5 - R5'],['TGFB1–TGFBR1','CXCL12–CXCR4','IL6–IL6R','VEGFA–KDR','CCL5–CCR5'])))
        p['scope_note']='Fictional normalized evidence scores · neither physical binding nor a measured signaling rate'
    if key=='single_cell.ligand_target.p1':
        coords={'TGFB1':(0,0),'TGFBR1':(1,0),'SMAD3':(2,0),'COL1A1':(3,.7),'SERPINE1':(3,0),'CTGF':(3,-.7)}
        edges=[('TGFB1','TGFBR1'),('TGFBR1','SMAD3'),('SMAD3','COL1A1'),('SMAD3','SERPINE1'),('SMAD3','CTGF')]
        rows=[dict(panel_id=panels[0]['id'],label=a,target=b,series='Candidate direction',x=coords[a][0],y=coords[a][1],target_x=coords[b][0],target_y=coords[b][1],value=.4+i*.1) for i,(a,b) in enumerate(edges)]
        rows.extend(dict(panel_id=panels[1]['id'],label=a+'→'+b,series=c,value=float((i+j)%3==0)) for i,(a,b) in enumerate(edges) for j,c in enumerate(['Prior','Expression','Perturbation']))
        d=pd.DataFrame(rows);edit(0,title='Selected ligand-to-target candidate chain',directed=True,edge_definition='Explicit directed candidate evidence; fixed supplied positions, not demonstrated causal signaling')
        edit(1,title='Evidence mapped to each displayed edge',value_label='Explicit evidence indicator',limits=[0,1]);s['theme']['group_slots']['Candidate direction']=0
    if key=='single_cell.cnv.p1':
        edit(0,value_label='Log2 relative CNV · reference = 0');d.loc[select(0)&(d.series=='Reference'),'value']=0
        additions=[]
        for label in d.loc[select(1),'label'].drop_duplicates():
            q=d[select(1)&(d.label==label)];row=q.iloc[0].to_dict();row.update(series='Clone C',value=.12);additions.append(row)
        d.loc[select(1),'value']*=.88;d=pd.concat([d,pd.DataFrame(additions)],ignore_index=True);s['theme']['group_slots']['Clone C']=3
        p['scope_note']='Fictional ordered bins · log2 reference baseline = 0 · RNA-inferred patterns require genomic validation'
    if key=='single_cell.vdj.p1':
        edit(0,x_label='Fraction of productive clonotype-assigned cells')
        edit(1,x_label='ln(Treated fraction / Control fraction)\nSupplied 95% interval')
        edit(2,value_label='Supplied Jaccard overlap')
        ix=d.index[select(1)];values=np.log([2/3,4/3,1]);d.loc[ix,'x']=values;d.loc[ix,'lower']=values-.18;d.loc[ix,'upper']=values+.18
    if key=='single_cell.splicing.p1':
        edit(0,title='STAT1 fictional locus coverage',x_label='Relative position in declared STAT1 window',y_label='Normalized coverage')
        edit(1,title='STAT1 junction-usage contrasts')
        edit(2,title='STAT1 transcript usage',x_label='Fraction of quantified STAT1 transcripts')
        p['scope_note']='Selected identity: T cells · fictional normalized STAT1 window · no genomic-coordinate claim'
    if key=='single_cell.perturbseq.p1':
        edit(1,title='STAT1 response by guide',x_label='Log2 STAT1 fold change · 95% interval')
        edit(2,value_label='Standardized program-score difference')
    if key=='single_cell.spatial.p1':
        edit(0,title='Supplied tissue positions · section S01',x_label='Tissue x (µm)',y_label='Tissue y (µm)')
        edit(1,title='Interferon-program region contrasts',x_label='Interferon-score difference · 95% interval')
        edit(2,value_label='Standardized program score')
        p['scope_note']='Fictional section S01 positions · donor-level contrast summaries supplied separately'
    if key=='single_cell.multiome.p1':
        edit(1,title='RNA, accessibility and link evidence',value_label='Supplied standardized channel')
        # Only actual peak-to-gene edges, with the declared fixed coordinates.
        mask=select(2);q=d[mask].copy();left=q.label.str.startswith('Peak');right=q.target.str.startswith('Peak');q=q[left^right].copy()
        d=pd.concat([d[~mask],q],ignore_index=True)
        edit(2,title='Selected peak–gene associations',edge_definition='Explicit supplied peak-to-gene association support, not causal regulation')
    if key in ['GSVA_AdjustedPathwayContrasts','TF_ActivityContrasts']:
        crosses=(d.lower<=0)&(d.upper>=0)
        for col in ['q','padj','p_adj','FDR']:
            if col in d:d.loc[crosses,col]=.65
    if key in ['Regulons_DirectedTargetEvidence','PPI_SelectedEvidenceNetwork']:
        p['label_genes']=d.loc[d.record_type=='node','gene'].tolist()
        if key=='Regulons_DirectedTargetEvidence':
            d=d[(d.record_type!='edge')|d.source.isin(['IRF1','STAT1','RELA'])].copy()
            p['title']='Selected TF-to-target candidate support'
            p['edge_semantics']='Explicit fictional directed TF-to-target candidate evidence; supplied scores do not prove direct binding or causal regulation'
    if key in ['single_cell.qc.complete','single_cell.composition.complete']:
        if key=='single_cell.qc.complete':
            metrics=d.metric.drop_duplicates().tolist() if 'metric' in d else ['value'];shapes={}
            for metric in metrics:
                q=d[d.metric==metric] if 'metric' in d else d;shapes[metric]={}
                for name,g in q.groupby('sample',sort=False):
                    vals=g.value.to_numpy();grid=np.linspace(vals.min(),vals.max(),51);shapes[metric][str(name)]=dict(grid=grid.tolist(),width=np.sin(np.linspace(0,np.pi,51)).tolist(),n=len(vals),definition='Authored fictional cloud geometry; not a fitted density')
            p.update(cloud_shapes=shapes,observation_unit='cells nested within donor',title='Cell QC · donor-stratified supplied distributions')
        else:
            p['cloud_shapes']={};p['celltype_palette']={}
            colors=['#218C8D','#D8795B','#5577A7','#A493BB','#C5A24C','#5796AE']
            denom=d.groupby('sample')['count'].transform('sum')
            fractions=d['count']/denom
            for i,identity in enumerate(d.celltype.drop_duplicates()):
                p['celltype_palette'][identity]=colors[i%len(colors)];p['cloud_shapes'][identity]={}
                for group in d.group.drop_duplicates():
                    vals=fractions[(d.celltype==identity)&(d.group==group)].to_numpy()
                    p['cloud_shapes'][identity][group]=dict(grid=np.linspace(vals.min(),vals.max(),51).tolist(),width=np.sin(np.linspace(0,np.pi,51)).tolist(),n=len(vals),definition='Authored fictional geometry, not a density estimate')
    s['parameters']=p
    s['provenance']['source']='Explicit fictional core fixture revision v0.10.0; no analysis backend executed'
    s['provenance']['contrast']='Named comparisons and scales in the supplied panels'
    return s,d

def build(inventory,review,output):
    output.mkdir(parents=True,exist_ok=False);by={r['id']:r for r in read(review)['records']};records=[]
    for row in read(inventory):
        key=row['id']
        if by[key]['state']!='NEEDS_REVISION':continue
        original=Path(row['png']).parent/'input/example.spec.json';s=read(original)
        if s['provenance'].get('synthetic') is not True:raise ValueError('Only explicit fictional fixtures can be revised')
        data=pd.read_csv(original.parent/s['input']['path'],sep='\t');s,data=repair(key,copy.deepcopy(s),data)
        dest=output/key;dest.mkdir();raw=data.to_csv(sep='\t',index=False,lineterminator='\n',float_format='%.17g').encode();(dest/'example.tsv').write_bytes(raw)
        s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in data if pd.api.types.is_numeric_dtype(data[c])]);write(dest/'example.spec.json',s)
        records.append(dict(id=key,spec=key+'/example.spec.json',chapters=row['chapters'],public_folder=Path(row['png']).parent.relative_to(SKILL).as_posix(),original_sha256=hashlib.sha256(original.read_bytes()).hexdigest()))
    write(output/'manifest.json',dict(version='0.10.0',records=records,analysis_performed=False));print(json.dumps(dict(prepared=len(records),research_analysis=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inventory',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.inventory,a.review,a.output)
