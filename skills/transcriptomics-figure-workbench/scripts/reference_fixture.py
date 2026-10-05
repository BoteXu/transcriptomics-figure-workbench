"""Synthetic software fixtures for reference-style rendering, never research results.

Generation is deliberately separate from adapters. Densities, fits, intervals,
centroids, proportions and trees are frozen here before rendering. This generator
is not an analysis backend and its invented values cannot validate a study.
"""
import numpy as np
import pandas as pd
import matplotlib.colors as mc
from figure_reference_palettes import category_map, load_palettes

def _table(rows): return pd.DataFrame(rows)
def _r(kind,**row): return dict(record_type=kind,**row)

def reference_fixtures():
    rng=np.random.default_rng(20261005); examples={}
    def add(id,rows,func,**params): examples[id]=dict(data=_table(rows),function=func,params=params)
    # 01 and 02 intentionally share the exact same data and different palettes.
    cats='NX QH GS SN XZ YN GZ SC CQ HI GX GD HN HB HA SD JX FJ AH ZJ JS SH HL JL LN IM SX HE TJ BJ XJ'.split()
    profile=[]
    for j,s in enumerate(['2020','2010','2000']):
        for i,c in enumerate(cats):
            value=2900+950*np.sin(i*.31-j*.9)+460*np.cos(i*.79+j)+350*j
            profile.append(_r('profile',category=c,series=s,value=float(value),area=float(1900+1000*np.sin(i*.41)**2+170*i+300*j)))
    for id,pal in [('R01','radar_bright'),('R02','radar_soft')]:
        add(id,profile,'plot_annular_profile',palette=category_map(pal,['2020','2010','2000']),value_label='Primary value\n(original units)',area_label='Secondary value',value_max=7000,area_scale=.022,connect_categories=True,curve_mode='smooth_display')
    # 03: common state IDs align independent evidence and score matrices.
    fams=['Block A','Block B','Block C','Block D']; states=[]; emb=[]; row=[]
    for f,fam in enumerate(fams):
        for i in range(7): states.append(f'{f+1}.{i+1} state {i+1}'); row.append(_r('state',state=states[-1],family=fam,order=f*7+i))
        for i in range(400):
            center=np.array([[0,1],[1,0],[0,-1],[-1,0]])[f]; xy=center+rng.normal(0,.38,2)
            emb.append(_r('embedding',unit_id=f'e{f}_{i}',family=fam,x=xy[0],y=xy[1]))
    row+=emb; conds=['Level 1','Level 2','Level 3']
    for s in states:
        for c in conds: row.append(_r('effect',state=s,condition=c,value=rng.uniform(-2,2),evidence=rng.uniform(0,22)))
        for f in ['Program A','Program B','Program C','Program D','Program E']: row.append(_r('mean',state=s,feature=f,value=rng.uniform(0,1)))
        for f in ['Score 1','Score 2','Score 3','Score 4','Score 5','Score 6','Score 7']: row.append(_r('program',state=s,feature=f,value=rng.uniform(-1,1)))
    statecolors={s:mc.to_hex(mc.hsv_to_rgb([(i*.618)%1,.6,.75])) for i,s in enumerate(states)}
    add('R03',row,'plot_state_dashboard',palette=statecolors,family_order=fams,condition_order=conds,mean_label='Supplied mean value',program_label='Supplied signed score')
    # 04: 70 groups on the circular panel, 16 on the aligned lower panels.
    atlas=[f'Type {i+1:02d}' for i in range(70)]; main=[f'Class {i+1:02d}' for i in range(16)]
    palette={g:mc.to_hex(mc.hsv_to_rgb([(i*.618)%1,.38+(i%3)*.15,.64+(i%4)*.07])) for i,g in enumerate(atlas)}; palette.update(category_map('atlas_cells',main))
    rows=[]; stack={f'Segment {i+1}':c for i,c in enumerate(['#407CA5','#D52C28','#62A743','#E8CD46'])}
    for k,g in enumerate(atlas):
        center=rng.uniform(-.8,.8,2)
        for i in range(45):
            xy=center+rng.normal(0,.055,2); rows.append(_r('point',unit_id=f'a{k}_{i}',layer='atlas',group=g,x=xy[0],y=xy[1]))
        for s in stack: rows.append(_r('count',layer='atlas',group=g,segment=s,value=float(rng.integers(0,24))))
    for k,g in enumerate(main):
        angle=k*2*np.pi/len(main); center=[np.cos(angle)*2.5,np.sin(angle)*2]
        for i in range(140):
            xy=np.array(center)+rng.normal(0,.22,2); rows.append(_r('point',unit_id=f'm{k}_{i}',layer='main',group=g,x=xy[0],y=xy[1]))
        rows.append(_r('count',layer='main',group=g,segment='total',value=float(rng.integers(300,2300))))
        rows.append(_r('leaf',group=g,order=k))
        for j,f in enumerate([f'Feature {i+1}' for i in range(9)]):
            high=(j==k%9); rows.append(_r('marker',group=g,feature=f,fraction=rng.uniform(.5,.95) if high else rng.uniform(0,.12),value=rng.uniform(1.6,3) if high else rng.uniform(0,.25)))
    segid=0
    # Frozen illustrative balanced tree; this does not claim a learned hierarchy.
    nodes=[(float(i),0) for i in range(16)]
    for level in range(1,5):
        nxt=[]
        for i in range(0,len(nodes),2):
            a,b=nodes[i:i+2]; c=((a[0]+b[0])/2,float(level))
            for u,v in [(a,(a[0],c[1])),(b,(b[0],c[1])),((a[0],c[1]),(b[0],c[1]))]:
                rows.append(_r('tree',segment_id=f't{segid}',x0=u[0],y0=u[1],x1=v[0],y1=v[1])); segid+=1
            nxt.append(c)
        nodes=nxt
    add('R04',rows,'plot_embedding_atlas',palette=palette,stack_palette=stack,atlas_order=atlas,main_order=main,marker_label='Supplied mean',count_label='Recorded counts',fraction_label='Fraction of units',radial_count_max=90)
    # 05 numeric r labels visible in the reference, transcribed as a visual fixture.
    labels=list('ABCDEFG'); lower=[[-.85],[-.85,-.90],[-.78,-.83,.79],[-.68,-.70,-.71,-.45],[-.87,-.78,.89,.66,-.71],[-.42,-.59,-.43,-.71,.29,-.37]]
    rows=[_r('correlation',a=labels[j],b=labels[i+1],r=v) for i,line in enumerate(lower) for j,v in enumerate(line)]
    add('R05',rows,'plot_ellipse_correlation',labels=labels)
    names='CD300LG ITGA7 HEPN1 DGAT2 LEP PEAR1 PDE2A CIDEC CRYAB KANK3 PLIN4 NPR1 RBP4 S100B GPD1 TUSC5 CA4 TIMP4'.split()
    rows=[_r('node',node=n,order=i) for i,n in enumerate(names)]
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            if rng.uniform()<.28: rows.append(_r('edge',a=names[i],b=names[j],r=float(rng.choice([-1,1])*rng.uniform(.25,.95))))
    add('R06',rows,'plot_signed_network')
    names='N P K Ca Mg S Al Fe Mn Zn Mo Variable12 Variable13 pH'.split(); specs=[f'Set {i+1}' for i in range(4)]; rows=[]
    for i in range(len(names)):
        for j in range(i+1,len(names)): rows.append(_r('correlation',a=names[i],b=names[j],r=rng.uniform(-.8,.8),p=float(rng.choice([.0001,.008,.035,.3]))))
    for s in specs:
        for n in names: rows.append(_r('mantel',specimen=s,target=n,r=rng.uniform(.02,.58),p=float(rng.choice([.005,.035,.4],p=[.15,.15,.7]))))
    add('R07',rows,'plot_mantel_matrix',labels=names,specimen_order=specs,p_type='raw',pearson_p_type='adjusted')
    # Marginal and contour calculations below belong to this software fixture only.
    def joint(id,groups,pal,means,scales,limit,mode,identity=False,fit=False,boxes=False):
        rows=[]; cols=category_map(pal,groups); xmin,xmax=limit[0]; ymin,ymax=limit[1]
        for k,g in enumerate(groups):
            n=180 if id!='R12' else 420; x=rng.normal(means[k][0],scales[k][0],n); y=means[k][1]+scales[k][1]*(x-means[k][0])+rng.normal(0,scales[k][2],n)
            x=np.clip(x,xmin+.05,xmax-.05); y=np.clip(y,ymin+.05,ymax-.05)
            for i,(a,b) in enumerate(zip(x,y)): rows.append(_r('point',unit_id=f'{g}_{i}',group=g,x=a,y=b))
            for axis,arr,bounds in [('x',x,limit[0]),('y',y,limit[1])]:
                if mode=='bins':
                    heights,edges=np.histogram(arr,bins=18,range=bounds)
                    for h,l,r in zip(heights,edges[:-1],edges[1:]): rows.append(_r('marginal',group=g,axis=axis,coordinate=(l+r)/2,left=l,right=r,value=float(h)))
                else:
                    coords=np.linspace(*bounds,120); std=float(np.std(arr)); den=np.exp(-.5*((coords-np.mean(arr))/std)**2)/(std*np.sqrt(2*np.pi))
                    for c,h in zip(coords,den): rows.append(_r('marginal',group=g,axis=axis,coordinate=c,value=h))
            if id=='R08':
                for gx in np.linspace(xmin,xmax,35):
                    for gy in np.linspace(ymin,ymax,35):
                        z=np.exp(-.5*((gx-means[k][0])/scales[k][0])**2-.5*((gy-(means[k][1]+scales[k][1]*(gx-means[k][0])))/scales[k][2])**2)
                        rows.append(_r('density2d',group=g,x=gx,y=gy,value=z))
                rows.append(_r('annotation',group=g,x=.03,y=.96-k*.14,text=f'{g}\nSupplied rho / p: DEMO'))
            if fit:
                for gx in np.linspace(xmin,xmax,50):
                    gy=means[k][1]+scales[k][1]*(gx-means[k][0]); rows.append(_r('fit',group=g,x=gx,y=gy,lower=gy-.35,upper=gy+.35))
                rows.append(_r('annotation',group=g,x=.03 if k==0 else .55,y=.96 if k==0 else .22,text=f'{g}\ny = {scales[k][1]:.2f}x + supplied intercept\nR², p, RMSE, MAE: synthetic fixture'))
            if boxes:
                residual=y-x; q1,med,q3=np.quantile(residual,[.25,.5,.75]); rows.append(_r('box',group=g,q1=q1,median=med,q3=q3,low=float(residual.min()),high=float(residual.max())))
        if boxes:
            rows.append(_r('bracket',a=groups[0],b=groups[1],text='supplied **'))
        add(id,rows,'plot_joint_reference',palette=cols,x_label='Measurement X',y_label='Measurement Y',limits=limit,marginal_mode=mode,identity=identity,residual_label='Supplied Y − X summaries' if boxes else None)
    joint('R08',['Group 1','Group 2','Group 3'],'joint_pastel',[(.5,8.55),(-.5,8.2),(0,8.4)],[(.22,.5,.11),(.3,-.1,.1),(.3,.12,.10)],[[-1.5,1.2],[7.7,9.3]],'bins')
    joint('R12',['Group A','Group B','Group C'],'agreement_groups',[(20,21),(0,1),(-20,-18)],[(18,1,4),(20,1,7),(18,1,9)],[[-70,70],[-70,70]],'density',identity=True,boxes=True)
    joint('R13',['Series 1','Series 2'],'day_night',[(21,23),(21,23)],[(3.3,.93,1.7),(3.5,.95,1.8)],[[10,35],[10,35]],'density',fit=True)
    dims=['learning_rate','max_depth','min_samples_split','n_estimators','heldout_score']; ranges={'learning_rate':[.05,.45],'max_depth':[5,12],'min_samples_split':[5,12],'n_estimators':[50,290],'heldout_score':[.73,.88]}; rows=[]
    for i in range(150):
        score=rng.uniform(.73,.88); vals=[float(rng.choice(np.arange(.05,.451,.05))),float(rng.integers(5,13)),float(rng.integers(5,13)),float(rng.choice(np.arange(50,291,30))),score]
        for dim,v in zip(dims,vals): rows.append(_r('trial',trial_id=f'T{i}',dimension=dim,value=v,score=score))
    add('R09',rows,'plot_parallel_trials',axis_order=dims,axis_ranges=ranges,score_label='Supplied held-out score',score_limits=[.73,.88])
    features=['Feature A','Feature B','Feature C','Feature D','Feature E','Feature F','Feature G','Feature H','A × F','B × F','D × F','C × F','Feature I','E × F','G × F','Feature J','H × F','I × F','J × F']; rows=[]
    for k,f in enumerate(features):
        for i in range(200):
            v=rng.uniform(); effect=(v-.5)*.13*np.exp(-k*.42)+rng.normal(0,.008*np.exp(-k*.35)); effect=np.clip(effect,-.062,.076)
            rows.append(_r('contribution',unit_id=f'u{i}',feature=f,contribution=effect,feature_value=v))
    add('R10',rows,'plot_contribution_swarm',feature_order=features,contribution_label='Supplied prediction contribution',limits=[-.065,.08])
    classes=[f'Class {i}' for i in range(5)]; feats=[f'Variable {i+1:02d}' for i in range(19)]; shares_feats=feats[:9]; rows=[]; orders={}
    for k,c in enumerate(classes):
        order=list(np.roll(feats,k*3)); orders[c]=order
        for j,f in enumerate(order):
            for i in range(70):
                v=rng.uniform(); effect=np.clip((v-.5)*1.7*np.exp(-j*.18)+rng.normal(0,.05),-.82,.82); rows.append(_r('contribution',unit_id=f'u{i}',**{'class':c},feature=f,contribution=effect,feature_value=v))
        weights=rng.dirichlet(np.ones(len(shares_feats))*2)
        for f,w in zip(shares_feats,weights): rows.append(_r('share',**{'class':c},feature=f,value=w))
    add('R11',rows,'plot_multiclass_contributions',palette=dict(zip(shares_feats,load_palettes()['shap_reference_rainbow']['colors']+['#74CFB7','#196189'])),class_order=classes,feature_orders=orders,limits=[-.85,.85])
    # Recorded training/activity arrays, not actual model training.
    rows=[]; epochs=np.arange(1,121)
    for series,c in [('Train',0),('Validation',1)]:
        vals=1.35*np.exp(-epochs/28)+.16+c*(.08+np.maximum(epochs-75,0)*.0025)+rng.normal(0,.008,len(epochs))
        for e,v in zip(epochs,vals): rows.append(_r('loss',series=series,epoch=float(e),value=v,lower=v-.04,upper=v+.04))
    for run in range(1,29):
        for e in epochs: rows.append(_r('heat',run=f'Run{run}',epoch=float(e),value=float(rng.uniform(0,.14)+e/120*.07)))
    for e in epochs:
        v=.64*np.exp(-e/36)+.07+.03*np.sin(e/5); rows.append(_r('gradient',epoch=float(e),value=v,lower=v*.78,upper=v*1.25)); rows.append(_r('reference',epoch=float(e),value=float(np.exp(-e/45))))
    add('R14',rows,'plot_training_dashboard',palette=category_map('training_categories',['Train','Validation']),selected_epoch=91,selection_label='Selected epoch supplied by upstream record; illustrative fixture only',loss_label='Recorded loss',heat_label='Recorded diagnostic',gradient_label='Positive gradient norm')
    rowids=[f'Row{i:03d}' for i in range(150)]; colids=[f'Column{i+1:02d}' for i in range(44)]; groups=[f'Module {i+1}' for i in range(5)]; rows=[]
    for i,r in enumerate(rowids):
        k=i//30; rows.append(_r('row',row=r,group=groups[k]))
        for j,c in enumerate(colids): rows.append(_r('matrix',row=r,column=c,value=float(rng.uniform(0,.4)+(.8+rng.uniform(0,.8) if j//9==k else 0))))
    for j,c in enumerate(colids): rows.append(_r('top',column=c,bar=float(rng.uniform(.7,1)),line=float(.75+.14*np.sin(j*.5))))
    for k,g in enumerate(groups):
        for x in np.linspace(0,2,100): rows.append(_r('density',group=g,coordinate=x,value=float(np.exp(-x*4)+.18*np.exp(-((x-1.2)/.4)**2))))
    add('R15',rows,'plot_activity_dashboard',palette=category_map('training_categories',groups),row_order=rowids,column_order=colids,value_label='Supplied matrix value',bar_label='Recorded bar',line_label='Recorded line')
    rows=[]; outcomes=[f'Outcome {i+1:02d}' for i in range(26)]; panels=['Metric A','Metric B']
    for k,p in enumerate(panels):
        for i,r in enumerate(outcomes):
            mu=float(rng.normal(0,.5 if k==0 else .25)); width=float(rng.uniform(.12,.45)); pval=.003 if abs(mu)>width else .3
            rows.append(_r('summary',panel=p,row=r,value=mu,lower=mu-width,upper=mu+width,count_text=f'{40+i*12}({8+i})',p=pval))
            for j in range(50+i*3): rows.append(_r('effect',effect_id=f'{r}_{j}',panel=p,row=r,value=float(np.clip(rng.normal(mu,.55),-3.8,3.8))))
    add('R16',rows,'plot_effect_distribution_forest',row_order=outcomes,panel_order=panels,panel_labels={'Metric A':'Supplied effect A','Metric B':'Supplied effect B'},limits=[-4,4],interval_label='Supplied interval',count_label='n(k) labels are fixture values; meanings must be supplied',p_type='raw')
    rows=[]; groups=['1','2','3','4']
    for k,g in enumerate(groups):
        values=np.r_[rng.normal(-.55,.48,240),rng.normal(.8,.38,170)] if k==1 else rng.normal(0,.65,480)
        if k>1: values=np.r_[values,rng.exponential(1,65)]
        values=np.clip(values,-3.4,4.4)
        rows.extend(_r('observation',unit_id=f'{g}_{i}',group=g,value=float(v)) for i,v in enumerate(values)); rows.append(_r('summary',group=g,value=float(values.mean())))
    add('R17',rows,'plot_group_beeswarm',palette=category_map('swarm_four',groups),group_order=groups,value_label='Supplied observation',summary_label='Supplied arithmetic mean',limits=[-3.5,4.5])
    # 18/19 reuse identical coordinates, centroids and ellipses.
    rows=[]; groups=['Group 1','Group 2']
    for k,g in enumerate(groups):
        xy=rng.normal(size=(180,2))*[.65 if k==0 else 1.6,1.05]+[1.3 if k==0 else -1.1,0]
        xy[:,0]=np.clip(xy[:,0],-6.4,4); xy[:,1]=np.clip(xy[:,1],-3.4,3.4)
        rows.extend(_r('point',unit_id=f'{g}_{i}',group=g,x=x,y=y) for i,(x,y) in enumerate(xy))
        center=xy.mean(axis=0); rows.append(_r('centroid',group=g,x=center[0],y=center[1])); rows.append(_r('ellipse',group=g,x=center[0],y=center[1],width=2.5 if k==0 else 5.5,height=4.2,angle=0))
    for id,spider,landscape in [('R18',True,False),('R19',False,True)]:
        add(id,rows,'plot_pca_reference',palette=category_map('pca_two',groups),group_order=groups,axis_labels=['PC1 (supplied 38.0%)','PC2 (supplied 14.8%)'],limits=[[-6.7,4.4],[-3.6,3.6]],ellipse_label='Supplied illustrative dispersion ellipse; no confidence claim',spider=spider,landscape=landscape)
    rows=[]; rf=['Condition A','Condition B']; cf=['Set 1','Set 2','Set 3']; features=['Feature A','Feature B','Feature C','Feature D','Feature E','Feature F','Feature G','Feature H']; windows=[15,30,45,60,75,90,105,120]
    for i,a in enumerate(rf):
        for j,b in enumerate(cf):
            for k,f in enumerate(features):
                for t,w in enumerate(windows): rows.append(_r('association',row_facet=a,column_facet=b,feature=f,window=float(w),r=float(np.clip((-.28 if k in (0,5,6) else .25 if k in (1,3,7) else .03)*(1 if i==0 else .4)*(1 if j<2 else .3)+rng.normal(0,.045),-.5,.5))))
    add('R20',rows,'plot_facet_bubble_matrix',row_facets=rf,column_facets=cf,feature_order=features,window_order=windows,value_label='Supplied signed association')
    rows=[]; panels=['Panel 1','Panel 2']; contrasts=['A','B','C','D']
    for p in panels:
        for c in contrasts:
            for i in range(1200): rows.append(_r('effect',feature=f'F{i}',panel=p,contrast=c,value=float(np.clip(rng.normal(0,3),-11,11)),padj=float(rng.uniform(0,.08)),jitter=float(rng.uniform(-.41,.41))))
    add('R21',rows,'plot_strip_effects',palette=dict(zip(contrasts,['#F8BA3E','#64BAD7','#F45439','#2CC379'])),panel_order=panels,contrast_order=contrasts,eligibility_label='Displayed eligible feature records; all input records retained in TSV')
    # 22: neutral category/track naming, no domain assumption.
    cats=[f'C{i+1:02d}' for i in range(45)]; tracks=['Track A','Track B','Track C']; mats=['Matrix A','Matrix B']; blocks=['Block 1','Block 2','Block 3']; rows=[]
    for i,c in enumerate(cats):
        rows.append(_r('category',category=c,block=blocks[0 if i<15 else 1 if i<36 else 2]))
        for t in tracks: rows.append(_r('count',track=t,category=c,value=float(rng.integers(0,11))))
        for m in mats:
            for r in ['Comparison 1','Comparison 2','Comparison 3']: rows.append(_r('matrix',matrix=m,row=r,category=c,value=float(rng.uniform(.7,.88) if m=='Matrix A' else rng.uniform(.05,.30))))
    add('R22',rows,'plot_aligned_tracks',palette=dict(zip(tracks,['#5376D8','#862953','#E78E56'])),category_order=cats,track_order=tracks,matrix_order=mats,block_order=blocks,matrix_labels={'Matrix A':'Supplied similarity','Matrix B':'Supplied proportion'},matrix_limits={'Matrix A':[.7,.9],'Matrix B':[.05,.3]},count_label='Recorded counts')
    # 23: synthetic regular grid. No interpolation performed by adapter.
    rows=[]
    for y in np.linspace(-3000,3000,65):
        for x in np.linspace(-3000,3000,65):
            z=285*np.exp(-((x-y*.22)/800)**2-((y+200)/2400)**2)-.032*x+15*np.sin(x/190)*np.cos(y/240)
            rows.append(_r('grid',x=x,y=y,z=float(z)))
    add('R23',rows,'plot_surface_grid',axis_labels=['X (supplied units)','Y (supplied units)'],value_label='Z (supplied units)',limits=[-180,330])
    from process_fixture import process_fixture
    examples['R24']=process_fixture()
    return examples
