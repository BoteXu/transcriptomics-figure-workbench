"""Build bounded fictional frozen fixtures for every non-network chapter."""
import argparse,copy,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from analysis_companion_recipes import RECIPES,validate_recipes,DONORS
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'

def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def fixture(recipe,large=False,independent_n=None):
    p=copy.deepcopy(recipe);k=p['kind'];scale=p.pop('scale');labels=p.pop('labels')[:9 if large else 6]
    p.pop('stage',None);p.pop('cols',None);p.pop('segments',None);p.pop('series',None);n=independent_n or (24 if large else 12);rows=[]
    series=recipe.get('series',['Control','Treated'])
    base=np.linspace(-.7,.9,len(labels))
    if k=='effects':
        p.update(interval_definition='Illustrative explicitly supplied 95% bounds; not estimated by the renderer',test_family='All selected fictional labels in this specified contrast',reference=1 if scale=='ratio' else 0,effect_scale='ratio' if scale=='ratio' else 'difference')
        if scale=='probability':p['probability']=True
        for i,l in enumerate(labels):
            e=float(base[i]);lo=e-.18;hi=e+.18
            if recipe.get('explicit_effects'):e=recipe['explicit_effects'][i];lo=e-.18;hi=e+.18
            if recipe.get('factorial_gene_effect') and l=='STAT1':e=.53;lo=e-.18;hi=e+.18
            if recipe.get('cohort_synthesis'):e=[.55,.58,.61,.58][i];lo=e-.18;hi=e+.18
            if scale=='fraction_effect':e*=.32;lo=e-.08;hi=e+.08
            if scale=='probability':e=.65+.04*i;lo=e-.06;hi=min(.99,e+.06)
            if scale=='ratio':e,lo,hi=map(math.exp,[e,lo,hi])
            contexts=recipe.get('comparison_contexts')
            for j,c in enumerate(contexts or ['']):
                shift=-.03*j if scale=='probability' else .08*j if scale!='ratio' else .04*j
                if recipe['title']=='Transcript-version sensitivity':shift=[-.02,.02,0][i]*j
                row_n=n//len(contexts) if contexts and recipe.get('independent_cohorts') else n
                if recipe.get('cohort_synthesis'):row_n=n if i==3 else n//3
                if 'subset' in l.lower():row_n=n//2
                if any(word in l.lower() for word in ['complete cases','complete pairs']):row_n=n-2
                if l.lower().startswith(('exclude discovery','exclude cohort')):row_n=2*n//3
                if c.startswith('Omit D'):row_n=n-1
                if c.startswith('Omit cohort'):row_n=2*n//3
                q=.65 if lo+shift<=(1 if scale=='ratio' else 0)<=hi+shift else float(.002+.018*i+.003*j)
                rows.append(dict(label=l+' · '+c if c else l,estimate=e+shift,lower=lo+shift,upper=hi+shift,q=q,n=row_n))
    elif k in ['raincloud','paired']:
        p['cloud_shapes']={} if k=='raincloud' else None
        for j,s in enumerate(series):
            count=n//len(series) if k=='raincloud' else n
            values=np.linspace(-.7,.8,count)+j*.48+.08*np.sin(np.arange(count)*1.9)
            if recipe.get('rle_median'):values=(np.linspace(-.7,.8,count)+.08*np.sin(np.arange(count)*1.9))*(1 if j==0 else .35)
            if scale=='positive':values=(values+1.1)*8
            if 'median genes' in p['y_label']:values*=100
            if scale=='fraction':values=.13+.19*(values+.8)
            if 'GSVA' in p['y_label']:values*=.65
            if k=='paired' and 'diversity score' in p['y_label']:values+=1.2
            for i,v in enumerate(values):rows.append(dict(unit=DONORS[i+(j*count if k=='raincloud' else 0)],series=s,value=float(v)))
            if k=='raincloud':p['cloud_shapes'][s]=dict(grid=np.linspace(values.min(),values.max(),49).tolist(),width=(np.sin(np.linspace(0,np.pi,49))**1.3).tolist(),n=count,definition='Explicit fictional analytic cloud geometry spanning these observations; not a fitted density')
        if k=='paired':p.pop('cloud_shapes')
        if scale=='fraction':p['probability']=True
    elif k=='matrix':
        cols=recipe.get('cols',['Control','Treated','Sensitivity'])
        lo,hi=(-1.4,1.4) if scale=='signed' else (-1,1) if scale=='fraction_effect' else (0,1) if scale=='fraction' else (0,100) if scale in ['count','risk'] else (0,3)
        if recipe.get('categorical_design'):lo,hi=0,3
        if recipe.get('factorial_repeated'):lo,hi=0,n//2
        if 'Independent donor count' in recipe.get('value_label',''):lo,hi=0,n
        p.update(limits=[lo,hi],integer=scale in ['count','risk'] or recipe.get('categorical_design',False))
        for i,l in enumerate(labels):
            for j,c in enumerate(cols):
                v=round((.3 if scale=='fraction_effect' else .75)*math.sin(.8*i+.7*j),2) if scale in ['signed','fraction_effect'] else round(.15+.65*((i+j)%5)/4,2)
                if recipe.get('binary'):v=int((i+j)%3!=0)
                if recipe.get('gene_membership'):
                    memberships={'STAT1':[0],'IRF7':[0],'ISG15':[0],'COL1A1':[1],'NDUFA1':[2],'SRSF1':[3],'MKI67':[],'KLF2':[],'JUN':[0]}
                    v=int(j in memberships.get(l,[]))
                if 'Explicit tested indicator'==recipe.get('value_label'):v=1
                if recipe['title']=='Donor support across measured times':v=1
                if recipe['title']=='Explicit pathway membership' and i==0 and j==0:v=1
                if 'principal-component loadings' in recipe['title']:
                    v=float(math.sqrt(2/len(labels))*math.cos(math.pi*(i+.5)*(j+1)/len(labels)))
                    if abs(v)<1e-12:v=0.0
                if recipe['title']=='Direction and magnitude by cohort' and i==0:v=[.55,.58,.61][j]
                if recipe.get('categorical_design'):v=int(j>=len(cols)//2) if i==0 else j%3+1
                if scale=='count':v=12+(i*7+j*3)%60
                if 'Independent donor count' in recipe.get('value_label',''):v=max(1,n//3+(i+j)%(n//3))
                if recipe.get('factorial_repeated'):v=n//4
                if scale=='risk':v=40-j*(6+i)
                if 'overlap' in recipe.get('value_label','').lower() and l==c:v=1.
                if 'PPI weight' in recipe.get('value_label','') and l==c:v=0.
                rows.append(dict(label=l,series=c,value=v))
        if recipe.get('row_composition'):
            for l in labels:
                subset=[r for r in rows if r['label']==l];total=sum(r['value'] for r in subset)
                for r in subset:r['value']/=total
    elif k=='fraction':
        segments=recipe.get('segments',['Retained','Flagged','Unassigned']);p['denominator_definition']='All explicitly declared observations within each displayed object; fixed complete fractions and denominator'
        for i,l in enumerate(labels):
            counts=np.array([17+(i+j*2)%7 for j in range(len(segments))]);total=int(counts.sum())
            if recipe.get('participant_denominator'):counts=np.array([18+6*i,22-6*i]);total=40
            if recipe.get('donor_denominator'):counts=np.array([n//2+i%(n//2),n-(n//2+i%(n//2))]);total=n
            if recipe['title']=='Donor balance within annotated identities':
                counts=np.array([n//2-i%3,n//2-i%2]);total=int(counts.sum());p['denominator_definition']='Independent donors with observed support for this identity; each condition is bounded by its available n/2 donors'
            if recipe.get('retention'):total=[100,80,70][i];counts=np.array([[80,20],[70,10],[60,10]][i]);p['denominator_definition']='Supplied input count at each processing step; each next input equals the preceding retained count'
            if recipe.get('feature_retention'):counts=np.array([[50,30,20],[40,18,12]][i]);total=int(counts.sum());p['denominator_definition']='Complete feature counts in the same universe; each post-filter category is a subset of its pre-filter category'
            if recipe.get('batch_donors'):total=n//3;counts=np.array([total//2,total-total//2]);p['denominator_definition']='Independent donors within each batch; the three complete batch totals sum to the declared independent n'
            for s,c in zip(segments,counts):rows.append(dict(label=l,series=s,value=float(c/total),denominator=total))
    elif k in ['profile','scatter','embedding']:
        count=28 if large else 18
        if recipe.get('identity_points'):count=len(labels)
        if recipe.get('named_points'):count=len(labels)
        if recipe.get('identity_points'):p['annotate']=labels
        if recipe.get('point_unit')=='independent donor':count=n//len(series)
        if 'ranking statistic' in p['y_label'].lower():count=240 if large else 180
        p.setdefault('point_unit','gene' if 'gene' in p['definition'].lower() else 'supplied observation; independent units are separately declared')
        for j,s in enumerate(series):
            xs=np.linspace(0,1,count)
            for i,x in enumerate(xs):
                y=.5*math.sin(3*x+j*.7)+j*.3;spread=.1
                if scale=='positive':y=1.1+.5*math.sin(3*x+j*.7)+j*.3
                if scale=='quality':x=1+149*x;y=37-j-7*(i/(count-1))**3;spread=.7
                elif scale=='fraction':
                    y=.08+.75*i/(count-1)+.06*j;spread=.045
                    if recipe.get('composition_profile'):
                        weights=[24+4*math.sin(i*.3+z) for z in range(len(series))];y=weights[j]/sum(weights);spread=.012
                elif scale=='survival':x=24*x;y=1-(.55+.16*j)*i/(count-1);spread=.055
                if 'days' in p['x_label']:x*=14
                if recipe.get('factorial_profile'):
                    t=i/(count-1);y=(1.1+.37*t+.12*math.sin(math.pi*t)) if j==0 else (.4+.90*t+.35*math.sin(math.pi*t))
                if 'months' in p['x_label'] and scale!='survival':x*=24
                if 'nt)' in p['x_label'] and scale!='quality':x=1+149*x
                if 'component' in p['x_label']:x=1+i
                if 'bin index' in p['x_label']:x=1+i
                if 'rank' in p['x_label'].lower():x=i+1
                if 'ranking statistic' in p['y_label'].lower():y=1.2-2.4*i/(count-1)+.04*j
                if recipe.get('reference_zero') and s=='Reference':y=0.
                if 'Barcode rank' in p['title']:
                    t=i/(count-1);y=5.2-.65*t-3.1/(1+math.exp(-16*(t-.58)))+.18*j
                if 'explained variance by PC' in p['title']:y=float(np.exp(-i/4)/np.exp(-np.arange(count)/4).sum())
                if 'Adapter content' in p['title']:y=.002+.04*(i/(count-1))**3+j*.005
                if 'retention sensitivity' in p['title'].lower() or 'Cell-call threshold' in p['title']:x=2+18*i/(count-1);y=.95-.7*i/(count-1)-.04*j
                if 'dispersion summaries' in p['title']:x=.2+4*i/(count-1);y=.6/(x+.4)+.06+.03*j
                if k=='scatter':
                    x=float(-1+3*i/(count-1));y=(x*.76+.15*math.sin(i*1.4)+.1*j) if recipe.get('identity_reference') else y+.08*math.sin(i*1.3)
                    if scale=='positive':x=i*.22;y=1.0+.25*x+.25*math.sin(i*.5+j)
                    if 'leverage' in p['x_label'].lower():x=.015+.18*i/(count-1)
                    if 'Unshrunk versus shrunk' in p['title']:y=x*(.70+.08*math.sin(i*1.4)+.04*j)
                    if 'Quantile diagnostics' in p['title']:y=.76*x+.08*math.tanh(2*x)+.10*j
                    if 'Fitted values and residual' in p['title']:y=.35*math.sin(6*math.pi*i/(count-1))+(.06 if j else -.06)
                    if recipe.get('point_unit')=='independent donor':x-=.5
                    if 'log UMI count' in p['x_label']:x=3+2*i/(count-1)
                    if 'log gene count' in p['y_label']:y=2.4+.7*i/(count-1)+.07*math.sin(i*.6+j)
                    if 'neighborhood size' in p['x_label']:x=40+250*i/(count-1)
                    if 'tissue distance' in p['x_label']:x=20+480*i/(count-1)
                r=dict(series=s,label=labels[i%len(labels)]+f' · {i+1}',x=float(x),y=float(y))
                if recipe.get('named_points'):r['label']=labels[i]
                if recipe.get('identity_points'):
                    r.update(label=labels[i],x=float(-.8+1.6*i/(count-1)),y=float(.52*math.sin(i*1.7)-.12))
                interval_ok=scale in ['quality','survival'] or any(word in p['title'].lower() for word in ['prediction','response','progression','calibration'])
                if k=='profile' and interval_ok:
                    lower=y-spread;upper=y+spread
                    if scale in ['fraction','survival']:lower=max(0,lower);upper=min(1,upper);p['probability']=True
                    r.update(lower=float(lower),upper=float(upper));p['interval_definition']='Explicit illustrative frozen bounds; no fit, smoothing or uncertainty estimation'
                rows.append(r)
    elif k=='bins':
        count=20 if large else 12
        xmax=1 if any(w in p['x_label'] for w in ['fraction','P value']) else 20000 if 'UMI count' in p['x_label'] else 150 if 'length' in p['x_label'] else 60
        for j,s in enumerate(series):
            for i in range(count):
                center=count*.4+j
                if 'UMI distributions by droplet class'==p['title']:center=count*{'Cell':.65,'Ambiguous':.32,'Background':.08}[s]
                rows.append(dict(series=s,start=float(i*xmax/count),end=float((i+1)*xmax/count),value=int(round(10+85*math.exp(-((i-center)**2)/(count*.6))))))
    elif k=='locus':
        p.update(coordinate_system='0-based half-open',genome_build='Explicit fictional reference v1; not a human locus',contig='synthetic_contig_1',strand='+')
        peak=recipe.get('locus_kind')=='peak_link'
        if peak:p['link_definition']='Supplied illustrative noncausal peak–gene association weight'
        for j,s in enumerate(series):
            exons=[(100,180),(330,415),(590,690),(820,900)];junctions=[(180,330),(415,590),(690,820)]
            if recipe.get('locus_kind')=='transcript_structure' and j:
                exons=[(100,180),(590,690),(820,900)] if j==1 else [(100,180),(820,900)]
                junctions=[(180,590),(690,820)] if j==1 else [(180,820)]
            for start,end in exons:rows.append(dict(series=s,record_type='peak' if peak else 'exon',start=start,end=end,value=1))
            for i,(start,end) in enumerate(junctions):rows.append(dict(series=s,record_type='link' if peak else 'junction',start=start,end=end,value=.3+.1*i if peak else 18+7*j+4*i))
    else:raise ValueError('No frozen fixture for '+k)
    return p,pd.DataFrame(rows),n

def build(output):
    validate_recipes();output.mkdir(parents=True,exist_ok=False);records=[]
    source=SKILL/'assets/analysis-gallery/Eigengenes_DonorContrasts/input/example.spec.json';base=json.loads(source.read_text(encoding='utf8'))
    actual={r['id'] for r in json.loads((SKILL/'references/transcriptomic-chapters.json').read_text(encoding='utf8'))['chapters']}
    assert set(RECIPES)==actual-{'bulk.wgcna','single_cell.hdwgcna'}
    def save(key,chapter,selected,stage,variant=False,large=False,columns='auto'):
        all_data=[];panels=[];spec=copy.deepcopy(base)
        for i,r in enumerate(selected):
            p,d,n=fixture(r,large,80 if chapter=='bulk.survival' else None);p['id']='p'+str(i+1);d['panel_id']=p['id'];panels.append(p);all_data.append(d)
        data=pd.concat(all_data,ignore_index=True)
        if chapter=='bulk.survival':n=80
        context=dict(independent_unit='fictional participants' if chapter=='bulk.survival' else 'fictional biological donors',independent_n=n,method_version=chapter+' supplied result channels v0.10.0',source_version='Fictional frozen drawing fixtures v0.10.0',selection='All explicitly declared rows in this example; no result selection or model fit during drawing')
        title=selected[0]['title'] if len(selected)==1 else chapter.replace('single_cell.','Single cell · ').replace('bulk.','Bulk · ')+' — complementary evidence'
        definition=' | '.join(r['definition'] for r in selected)
        spec.update(renderer='figure_analysis_evidence.plot_analysis_evidence',figure_id=key,parameters=dict(panels=panels,title=title,context=context,definition=definition,columns=columns))
        for d in all_data:
            if 'series' not in d:continue
            names=list(dict.fromkeys(map(str,d.series)))
            colors=spec['theme']['palette_colors']
            if len(names)>len(colors):
                # Explicit extended identities; never recycle categorical slots.
                extended=colors+['#528147','#D2A1A1']
                if len(names)>len(extended):raise ValueError('Author an explicit colour for every additional identity')
                spec['theme'].setdefault('category_colors',{}).update(dict(zip(names,extended)))
                for name in names:spec['theme']['group_slots'].pop(name,None)
            else:spec['theme']['group_slots'].update({s:i for i,s in enumerate(names)})
        spec['appearance'].update(label_pt=12,tick_pt=11,note_pt=11,title_pt=14)
        # Reading/custom pages retain complete tables and do not promise a journal-column fit.
        spec['export'].update(target_width_mm=210 if len(selected)==1 or columns==1 else 594 if columns==3 else 420,minimum_text_pt=7.5,raster_dpi=300,readability_policy='block')
        if len(selected)==1 and selected[0]['kind']=='matrix' and len(selected[0].get('cols',[]))>=6 and max(map(len,selected[0]['cols']))>14:
            spec['export']['target_width_mm']=240
        spec['provenance'].update(source='Fictional per-analysis drawing fixtures v0.10.0',input_unit='Explicitly typed frozen '+chapter+' channels',experimental_unit=context['independent_unit']+'; cells and reads are nested observations',denominator='Every declared row and stated panel-specific denominator; independent units='+str(n),contrast='Comparisons explicitly named per panel; descriptive QC as declared',model='No scientific model, density, test, enrichment or network fitted',interpretation_limit='Software drawing fixtures only; real methods, units and backend acceptance remain separate',synthetic=True)
        raw=data.to_csv(sep='\t',index=False,lineterminator='\n',float_format='%.17g').encode();dest=output/key;dest.mkdir();(dest/'example.tsv').write_bytes(raw)
        spec['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),numeric_columns=[c for c in data if pd.api.types.is_numeric_dtype(data[c])]);write(dest/'example.spec.json',spec)
        records.append(dict(id=key,spec=key+'/example.spec.json',chapters=[chapter],stage=stage,family=','.join(p['kind'] for p in panels),variant=variant,large_data=large,question=title))
    for chapter,recipes in RECIPES.items():
        stem=chapter.replace('single_cell.','S_').replace('bulk.','B_')
        for i,r in enumerate(recipes):save(stem+'_'+str(i+1).zfill(2),chapter,[r],r['stage'])
        middle=next((r for r in recipes if r['stage'] not in ['qc','validation']),recipes[1]);selection=[recipes[0],middle,recipes[-1]]
        if len({r['title'] for r in selection})<3:selection=[recipes[0],recipes[1],recipes[-1]]
        save(stem+'_Evidence',chapter,selection,'interpretation',columns=2)
        save(stem+'_Layout',chapter,selection,'layout',variant=True,large=True,columns=1)
        if chapter in ['bulk.design','bulk.differential','bulk.gsea','single_cell.annotation','single_cell.communication','single_cell.multiome']:
            save(stem+'_ThreeColumns',chapter,selection,'layout',variant=True,large=True,columns=3)
    write(output/'manifest.json',dict(version='0.10.0',records=records,analysis_performed=False,visual_acceptance=False));print(json.dumps(dict(state='ANALYSIS_COMPANION_INPUTS_PREPARED',chapters=len(RECIPES),figures=len(records))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
