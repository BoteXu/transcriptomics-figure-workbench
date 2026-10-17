"""Dedicated frozen WGCNA display inputs; no WGCNA computation or inference."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))

def build(out,base_spec):
    import numpy as np,pandas as pd
    from figure_core import table_bytes
    rng=np.random.default_rng(9194);out.mkdir(parents=True,exist_ok=False);base=json.loads(base_spec.read_text(encoding='utf8'));records=[]
    modules=['M1','M2','M3','M4','M5','M6'];colours=['#218C8D','#D8795B','#5676A5','#A795BD','#C8A34E','#6EA98C']
    base['theme']['group_slots'].update({x:i for i,x in enumerate(modules)});base['theme']['group_slots'].update({'Control':0,'Treated':1,'T cells':0,'B cells':1,'Myeloid':2})
    base['theme'].setdefault('category_colors',{}).update({'M1a':'#64AAA7','M1b':'#A6CECA','M2a':'#DFA08A','M2b':'#ECC6B9','M3a':'#7695BE','M3b':'#B5C6DD','M4a':'#AB95BF','M4b':'#D2C1DF'})
    context=dict(network_type='signed',correlation_method='Pearson',independent_unit='fictional donors',independent_n=24,module_version='Illustrative modules v0.9.1',source_version='Fictional frozen summaries; no WGCNA backend',selection='Complete explicitly selected fixture scope; no hub selection or inference during drawing')
    def add(k,data,mode,title,**params):
        folder=out/k;folder.mkdir();s=copy.deepcopy(base);raw=table_bytes(data);(folder/'example.tsv').write_bytes(raw)
        s.update(figure_id=k,renderer='figure_wgcna_views.plot_wgcna_view',parameters=dict(mode=mode,title=title,context=context,**params));s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[x for x in data if pd.api.types.is_numeric_dtype(data[x])]);s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11);s['export'].update(target_width_mm=297,minimum_text_pt=7.5,raster_dpi=300,readability_policy='block')
        s['provenance'].update(source='Fictional frozen WGCNA plotting fixture v0.9.1; no network analysis',model='No correlation, power selection, module/TOM fit or hub screening performed',interpretation_limit='Exact supplied fixture scope; example values are not scientific evidence',synthetic=True)
        (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8');records.append(dict(id=k,spec=k+'/example.spec.json',assay='WGCNA/hdWGCNA',family=mode))
    powers=np.arange(1,13)
    add('WGCNA_SoftPower',pd.DataFrame(dict(power=powers,signed_fit=[.15,.31,.48,.63,.74,.81,.84,.86,.87,.87,.88,.88],mean_connectivity=[180,124,88,63,47,36,28,22,18,15,12,10])),'soft_threshold','Soft power · topology and connectivity',selected_power=6,fit_reference=.8)
    def tree(n,samples=False):
        leaves=['D'+str(i+1).zfill(2) if samples else 'G'+str(i+1).zfill(3) for i in range(n)];rr=[]
        for i,g in enumerate(leaves):rr.append(dict(record_type='leaf',node_id=g,module='Control' if samples and i<n/2 else 'Treated' if samples else 'M'+str(i//(n//4)+1),dynamic_module='Batch 1' if samples and i%2==0 else 'Batch 2' if samples else 'M'+str(i//(n//4)+1)+('a' if i%(n//4)<n//8 else 'b')))
        active=leaves[:];level=0;counter=0
        while len(active)>1:
            nxt=[];level+=1
            for i in range(0,len(active),2):
                if i+1==len(active):nxt.append(active[i]);continue
                counter+=1;node='Merge'+str(counter);rr.append(dict(record_type='merge',node_id=node,left=active[i],right=active[i+1],height=level*.15+.01*(i%3)));nxt.append(node)
            active=nxt
        return pd.DataFrame(rr),leaves
    d,order=tree(16,True);add('WGCNA_SampleTree',d,'sample_tree','Samples · frozen clustering and design tracks',leaf_order=order,track_labels=['Batch','Condition'])
    d,order=tree(64);add('WGCNA_ModuleTree',d,'module_dendrogram','Gene hierarchy · dynamic and merged modules',leaf_order=order)
    traits=['Condition','Age','Severity'];rr=[];rvals=[[.62,.12,-.31],[-.48,.25,.53],[.20,-.42,.16],[.70,.09,.51],[-.22,.44,-.35],[.10,-.16,.12]];qvals=[[.008,.80,.25],[.04,.50,.02],[.60,.08,.70],[.002,.85,.03],[.60,.07,.20],[.85,.75,.80]]
    for i,m in enumerate(modules):
        for j,t in enumerate(traits):rr.append(dict(module=m,trait=t,r=rvals[i][j],probability=qvals[i][j],n=24))
    add('WGCNA_ModuleTrait',pd.DataFrame(rr),'module_trait','Module–trait associations · coefficient, q and effective n',module_order=modules,probability_kind='adjusted')
    rr=[]
    for j,m in enumerate(modules[:3]):
        for i in range(100):
            mm=-.9+1.8*i/99;gs=float(np.clip(mm*(.35+j*.20)+.17*np.sin(i*1.8),-.98,.98));rr.append(dict(gene=m+'_G'+str(i+1).zfill(3),module=m,kME=mm,GS=gs))
    membership=pd.DataFrame(rr);add('WGCNA_MM_GS',membership,'membership_significance','Module membership and gene–trait association',module_order=modules[:3],coefficient_semantics='signed')
    absolute=membership.copy();absolute[['kME','GS']]=absolute[['kME','GS']].abs();add('WGCNA_MM_GS_Absolute',absolute,'membership_significance','Upstream absolute MM and GS · separate declared convention',module_order=modules[:3],coefficient_semantics='absolute')
    names=['G'+str(i+1).zfill(3) for i in range(24)];rr=[]
    for i,a in enumerate(names):
        for j,b in enumerate(names):rr.append(dict(a=a,b=b,value=1. if i==j else float(.72*np.exp(-abs(i-j)/7)+(.20 if i//6==j//6 else .01))))
    tom=pd.DataFrame(rr);add('WGCNA_TOM',tom,'tom','Topological overlap · complete selected frozen matrix',leaf_order=names,matrix_definition='TOM');dist=tom.copy();dist['value']=1-dist.value;add('WGCNA_TOM_Dissimilarity',dist,'tom','Topological dissimilarity · explicitly 1 − TOM',leaf_order=names,matrix_definition='1 - TOM')
    me=pd.DataFrame([dict(a=a,b=b,value=1. if i==j else float(.7*np.cos(i-j)/(1+abs(i-j)))) for i,a in enumerate(modules) for j,b in enumerate(modules)]);add('WGCNA_EigengeneNetwork',me,'eigengene_network','Relationships among oriented module eigengenes',leaf_order=modules)
    prof=pd.DataFrame([dict(unit='D'+str(i+1).zfill(2),module=m,group='Control' if i<12 else 'Treated',value=float((.35 if i>=12 else -.35)*np.cos(j)+.3*np.sin(i*1.7+j))) for j,m in enumerate(modules[:4]) for i in range(24)]);add('WGCNA_EigengeneProfiles',prof,'eigengene_profiles','Donor-level module eigengenes · all units retained',module_order=modules[:4],columns=2)
    hubs=pd.DataFrame([dict(gene=m+'_Hub'+str(i+1),module=m,kWithin=40-i*5+j*3,kME=.95-i*.04) for j,m in enumerate(modules[:3]) for i in range(3)]);add('WGCNA_HubConnectivity',hubs,'hub_connectivity','Prespecified hub candidates · connectivity and membership')
    pres=pd.DataFrame(dict(module=modules,size=[72,105,180,240,330,480],Zsummary=[1.1,3.4,6.8,11.2,14.3,8.5],medianRank=[5.8,4.2,3.1,2.0,1.2,2.8]));add('WGCNA_Preservation',pres,'preservation','External module preservation · size, Zsummary and medianRank',preservation_guides=[2,10])
    mc=pd.DataFrame([dict(metacell='MC'+str(d*6+i),donor='D'+str(d+1).zfill(2),celltype=['T cells','B cells','Myeloid'][i%3],n_cells=20+(i+d)%11,n_shared=(i+d)%5) for d in range(12) for i in range(6)]);add('hdWGCNA_MetacellQC',mc,'metacell_qc','Metacell support · donors, celltypes and overlap')
    coords=[(-2+2*(i//80)+.70*np.sin(i*1.73)*(1+(i%7)/12),(.8 if i//80==1 else -.5)+.65*np.cos(i*.91)*(1+(i%11)/17)) for i in range(240)]
    activity=pd.DataFrame([dict(cell='C'+str(i),module=m,x=float(coords[i][0]),y=float(coords[i][1]),value=float(2.5*np.cos((i//80-j)*1.7)+.35*np.sin(i*.4))) for j,m in enumerate(modules[:4]) for i in range(240)]);add('hdWGCNA_ModuleActivity',activity,'module_activity','Module activity · identical cells, coordinates and scale',module_order=modules[:4],columns=2)
    (out/'manifest.json').write_text(json.dumps(dict(records=records,analysis_performed=False),indent=2)+'\n');print(json.dumps(dict(wgcna_views=len(records),analysis_performed=False)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--base-spec',required=True,type=Path);a=p.parse_args();build(a.output,a.base_spec)
