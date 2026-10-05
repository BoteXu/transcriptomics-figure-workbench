"""Original reference-led layouts; render frozen inputs without biological analysis."""
import numpy as np
import textwrap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.mlab import GaussianKDE
from figure_core import checked, palette_check, stamp, effect_reference

PAPER_COLORS = {'orange':'#E98B2A','purple':'#7562A5','teal':'#2D9C95','blue':'#4B88B5'}
SIGNED = LinearSegmentedColormap.from_list('paper_signed',['#7562A5','#FAF8F3','#E98B2A'])
SEQUENTIAL = LinearSegmentedColormap.from_list('paper_seq',['#FAF8F3','#AFD6CE','#258D85'])

def paper_axis(ax, grid=False):
    ax.spines[['top','right']].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set(color='#AEB5BC',linewidth=.7)
    ax.tick_params(colors='#49515A',width=.6,length=3,labelsize=9)
    if grid: ax.grid(axis='y',color='#E9ECEF',lw=.5,zorder=0)

def plot_publication_curve(data,palette,*,curve_type,labels,title='',prevalence=None):
    d=checked(data,['model','x','y'],['x','y']);palette_check(d.model,palette)
    if curve_type not in ('ROC','PR') or ((d[['x','y']]<0)|(d[['x','y']]>1)).any().any(): raise ValueError('Invalid curve')
    if set(d.model)!=set(labels): raise ValueError('Supply one frozen label per model')
    if curve_type=='PR' and (prevalence is None or not 0<prevalence<1): raise ValueError('PR needs included prevalence')
    fig,ax=plt.subplots(figsize=(5.9,5.8));fig.subplots_adjust(left=.14,right=.96,bottom=.27,top=.90)
    steps={}
    for i,m in enumerate(dict.fromkeys(d.model)):
        z=d[d.model==m];diff=np.diff(z.x)
        if (curve_type=='ROC' and (diff<0).any()) or ((diff<0).any() and (diff>0).any()): raise ValueError('Threshold x order must be monotonic')
        step='post' if curve_type=='ROC' or (diff<0).any() else 'pre'
        steps[m]=step
        ax.step(z.x,z.y,where=step,color=palette[m],lw=1.9,ls=['-','--','-.',':'][i%4],label=labels[m])
    if curve_type=='ROC':ax.plot([0,1],[0,1],ls='--',color='#B8BEC5',lw=1,zorder=0)
    else:ax.axhline(prevalence,ls='--',color='#B8BEC5',lw=1,zorder=0)
    ax.set(xlim=(-.015,1.015),ylim=(-.015,1.025),xlabel='False-positive rate' if curve_type=='ROC' else 'Recall',ylabel='True-positive rate' if curve_type=='ROC' else 'Precision',title=title)
    ax.set_xticks(np.linspace(0,1,6));ax.set_yticks(np.linspace(0,1,6));ax.set_aspect('equal');paper_axis(ax)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncol=2,frameon=False,fontsize=8.5,handlelength=2.7,columnspacing=1.7)
    return stamp(fig,data,'publication_curve',curve_type=curve_type,labels=labels,palette=palette,step_by_model=steps,prevalence=prevalence)

def plot_aligned_matrix(data,*,value_label,limits,signed=True,center=0,geometry='tile',block_palette=None,count_label='Supplied count',title='',continuous_colors=None):
    d=checked(data,['feature','sample','value'],['value']);rows=list(dict.fromkeys(d.feature));cols=list(dict.fromkeys(d['sample']))
    if d.duplicated(['feature','sample']).any() or len(d)!=len(rows)*len(cols):raise ValueError('Complete matrix required')
    if len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1] or d.value.min()<limits[0] or d.value.max()>limits[1]:raise ValueError('Limits must include every supplied value')
    if geometry not in ('tile','bubble') or (signed and not limits[0]<center<limits[1]):raise ValueError('Invalid matrix scale/geometry')
    for field in ['feature_block','row_count']:
        if field in d and (d[field].isna().any() or (d.groupby('feature')[field].nunique()!=1).any()):raise ValueError('Row annotation mismatch')
    has_count='row_count' in d;has_block='feature_block' in d
    if has_count and ((d.row_count<0)|(d.row_count%1!=0)).any():raise ValueError('Counts must be nonnegative integers')
    if has_block:palette_check(d.feature_block,block_palette or {})
    mat=d.pivot(index='feature',columns='sample',values='value').reindex(index=rows,columns=cols).to_numpy()
    fig=plt.figure(figsize=(max(6.8,len(cols)*.44+4),max(3.8,len(rows)*.27+1.8)))
    ratios=([.10] if has_block else [])+[max(2,len(cols)*.55)]+([1.8] if has_count else [])+[.13]
    gs=fig.add_gridspec(1,len(ratios),width_ratios=ratios,wspace=.18)
    fig.subplots_adjust(left=.27,right=.91,top=.88,bottom=.20)
    k=0;annot=d.drop_duplicates('feature').set_index('feature').loc[rows]
    if has_block:
        strip=fig.add_subplot(gs[0,k]);k+=1
        for i,r in enumerate(annot.itertuples()):strip.add_patch(Rectangle((0,i-.5),1,1,color=block_palette[r.feature_block],lw=0))
        strip.set(xlim=(0,1),ylim=(len(rows)-.5,-.5));strip.axis('off')
    ax=fig.add_subplot(gs[0,k]);k+=1
    norm=TwoSlopeNorm(center,limits[0],limits[1]) if signed else Normalize(*limits)
    cmap=LinearSegmentedColormap.from_list('project_matrix',continuous_colors) if continuous_colors is not None else SIGNED if signed else SEQUENTIAL
    if geometry=='tile':im=ax.imshow(mat,norm=norm,cmap=cmap,aspect='auto',interpolation='nearest')
    else:
        xx,yy=np.meshgrid(np.arange(len(cols)),np.arange(len(rows)));im=ax.scatter(xx.ravel(),yy.ravel(),c=mat.ravel(),norm=norm,cmap=cmap,s=105,edgecolors='none');ax.set(xlim=(-.5,len(cols)-.5),ylim=(len(rows)-.5,-.5))
    ax.set_xticks(np.arange(len(cols)),cols,rotation=35,ha='right');ax.set_yticks(np.arange(len(rows)),rows);ax.tick_params(length=0,labelsize=9,pad=5)
    if has_block: ax.tick_params(axis='y',pad=28)
    for spine in ax.spines.values():spine.set_visible(False)
    if geometry=='tile':
        ax.set_xticks(np.arange(len(cols)+1)-.5,minor=True);ax.set_yticks(np.arange(len(rows)+1)-.5,minor=True);ax.grid(which='minor',color='white',linewidth=.8);ax.tick_params(which='minor',length=0)
    if has_count:
        side=fig.add_subplot(gs[0,k],sharey=ax);k+=1;side.barh(np.arange(len(rows)),annot.row_count,color='#BEC5CC',height=.72)
        upper=max(float(annot.row_count.max()),1);side.set(xlim=(0,upper*1.42),xlabel=count_label);side.tick_params(axis='y',left=False,labelleft=False)
        for i,v in enumerate(annot.row_count):side.text(v+upper*.035,i,f'{int(v):,}',va='center',fontsize=8,color='#58626D')
        paper_axis(side)
    cb=fig.add_subplot(gs[0,k]);fig.colorbar(im,cax=cb,label=value_label);cb.tick_params(labelsize=8);cb.set_box_aspect(20)
    fig.suptitle(title,x=.27,ha='left',fontsize=12,y=.97)
    return stamp(fig,data,'publication_aligned_matrix',limits=list(limits),center=center,signed=signed,value_label=value_label,geometry=geometry,bubble_area='constant_not_detection',row_order=rows,column_order=cols,count_label=count_label,block_palette=block_palette,continuous_colors=continuous_colors,clustering='none_frozen_input_order')

def plot_publication_forest(data,palette,*,x_label,interval_label,effect_scale,title='',compact=True,decimals=2):
    d=checked(data,['label','group','estimate','lower','upper'],['estimate','lower','upper']);palette_check(d.group,palette);null=effect_reference(effect_scale)
    if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():raise ValueError('Invalid interval')
    if effect_scale=='ratio' and (d[['estimate','lower','upper']]<=0).any().any():raise ValueError('Ratio must be positive')
    if type(decimals) is not int or not 0<=decimals<=5:raise ValueError('Decimals must be an integer from 0 to 5')
    if compact:
        from matplotlib.ticker import LogLocator, FuncFormatter
        height=max(3.0,len(d)*.31+1.28)
        fig=plt.figure(figsize=(8.2,height))
        labels=fig.add_axes([.04,.19,.28,.62]);ax=fig.add_axes([.35,.19,.34,.62]);numbers=fig.add_axes([.73,.19,.25,.62])
        yy=np.arange(len(d)); limits=(len(d)-.45,-.8)
        for a in [labels,ax,numbers]: a.set_ylim(*limits)
        for i,r in enumerate(d.itertuples()):
            if i%2==0:
                for a in [labels,ax,numbers]: a.axhspan(i-.45,i+.45,color='#F3F6F8',zorder=0,lw=0)
            labels.text(.02,i,r.label,va='center',fontsize=9,color=palette[r.group])
            ax.plot([r.lower,r.upper],[i,i],color=palette[r.group],lw=1.5)
            ax.scatter(r.estimate,i,s=40,marker='D',color=palette[r.group],edgecolor='white',linewidth=.6,zorder=3)
            numbers.text(.02,i,f'{r.estimate:.{decimals}f} [{r.lower:.{decimals}f}, {r.upper:.{decimals}f}]',va='center',fontsize=9)
        labels.set_xlim(0,1);numbers.set_xlim(0,1);labels.axis('off');numbers.axis('off')
        ax.axvline(null,color='#8593A0',ls='--',lw=.9,zorder=1)
        if effect_scale=='ratio':
            ax.set_xscale('log');ax.xaxis.set_major_locator(LogLocator(base=10,subs=(1,2,5)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'));ax.xaxis.set_minor_formatter(FuncFormatter(lambda x,pos:''))
        ax.set_yticks([]);ax.set_xlabel(x_label);paper_axis(ax)
        labels.text(.02,1.06,'Comparison',transform=labels.transAxes,weight='bold',fontsize=9)
        numbers.text(.02,1.06,'Estimate [interval]',transform=numbers.transAxes,weight='bold',fontsize=9)
        fig.text(.04,.91,title,fontsize=11,weight='bold');fig.text(.04,.065,interval_label,fontsize=8,color='#586672')
        return stamp(fig,data,'publication_grouped_forest',palette=palette,effect_scale=effect_scale,interval_label=interval_label,
                     x_label=x_label,compact=True,decimals=decimals,display_values='estimate and full supplied interval',demo_label_style='compact')
    yy=[];last=None;gap=0
    for i,g in enumerate(d.group):
        if last is not None and g!=last:gap+=.45
        yy.append(i+gap);last=g
    fig,ax=plt.subplots(figsize=(8.6,max(3.8,len(d)*.38+1.6)));fig.subplots_adjust(left=.32,right=.86,bottom=.20,top=.87)
    ax.axvline(null,color='#B8BEC5',ls='--',lw=.8)
    for y,r in zip(yy,d.itertuples()):
        ax.plot([r.lower,r.upper],[y,y],color=palette[r.group],lw=1.5)
        ax.scatter(r.estimate,y,s=42,color=palette[r.group],edgecolor='white',linewidth=.7,zorder=3)
        ax.text(1.03,y,f'{r.estimate:.3f}',transform=ax.get_yaxis_transform(),va='center',fontsize=9,color=palette[r.group])
    if effect_scale=='ratio':ax.set_xscale('log')
    ax.set(yticks=yy,yticklabels=d.label,xlabel=x_label,title=title);ax.invert_yaxis();paper_axis(ax)
    fig.text(.32,.055,interval_label,color='#707A84',fontsize=8)
    return stamp(fig,data,'publication_grouped_forest',palette=palette,effect_scale=effect_scale,interval_label=interval_label,group_gaps=.45)

def plot_feature_facets(data,*,value_label,limits,title='',ncols=3,point_size=2,continuous_colors=None):
    d=checked(data,['cell_id','x','y','feature','value'],['x','y','value'])
    if d.duplicated(['cell_id','feature']).any() or len(d)!=d.cell_id.nunique()*d.feature.nunique():raise ValueError('Complete cell-feature grid required')
    if (d.groupby('cell_id')[['x','y']].nunique()>1).any().any():raise ValueError('Coordinates must match across features')
    if len(limits)!=2 or limits[0]!=0 or not np.isfinite(limits).all() or limits[1]<=0 or (d.value<0).any() or d.value.max()>limits[1]:raise ValueError('Explicit nonnegative common limits must include all values')
    feats=list(dict.fromkeys(d.feature));nrows=int(np.ceil(len(feats)/ncols));fig,axs=plt.subplots(nrows,ncols,figsize=(ncols*2.5,nrows*2.6),squeeze=False,layout='constrained')
    norm=Normalize(*limits);artist=None
    cmap=LinearSegmentedColormap.from_list('project_features',continuous_colors) if continuous_colors is not None else 'magma'
    for ax,f in zip(axs.ravel(),feats):
        z=d[d.feature==f];zero=z[z.value==0];pos=z[z.value>0]
        ax.scatter(zero.x,zero.y,s=point_size,c='#D8DDE2',lw=0,rasterized=True)
        artist=ax.scatter(pos.x,pos.y,c=pos.value,s=point_size,cmap=cmap,norm=norm,lw=0,rasterized=True)
        dx=max(float(d.x.max()-d.x.min()),1)*.03;dy=max(float(d.y.max()-d.y.min()),1)*.03
        ax.set(xlim=(d.x.min()-dx,d.x.max()+dx),ylim=(d.y.min()-dy,d.y.max()+dy),title=f,aspect='equal');ax.set_axis_off()
    for ax in axs.ravel()[len(feats):]:ax.set_axis_off()
    fig.colorbar(artist,ax=list(axs.ravel()),fraction=.02,pad=.025,label=value_label);fig.suptitle(title,fontsize=12)
    return stamp(fig,data,'publication_stored_feature_facets',limits=list(limits),value_label=value_label,coordinates='unchanged',draw_order='zeros_then_positive_original_order',point_size=point_size,cmap=continuous_colors if continuous_colors is not None else 'magma',point_layers_rasterized=True)

def plot_raincloud(data,palette,*,y_label,unit_label,title='',density_min_n=20):
    d=checked(data,['sample_id','group','value'],['value']);palette_check(d.group,palette)
    if d.sample_id.duplicated().any():raise ValueError('One row per declared observation unit required')
    if not unit_label.strip() or density_min_n<20:raise ValueError('Declare unit; density screen cannot be lower than 20 in this template')
    groups=list(dict.fromkeys(d.group))
    if len(groups)>8:raise ValueError('Split more than 8 groups into panels')
    fig,ax=plt.subplots(figsize=(max(6,len(groups)*1.05),4.8));fig.subplots_adjust(left=.14,right=.97,bottom=.20,top=.86)
    clouds=[];counts={}
    for i,g in enumerate(groups):
        z=d[d.group==g];v=z.value.to_numpy();counts[g]=len(v)
        if len(v)>=density_min_n and len(np.unique(v))>=5:
            grid=np.linspace(v.min(),v.max(),256);kde=GaussianKDE(v,bw_method='scott')(grid);w=kde/max(kde)*.32
            ax.fill_betweenx(grid,i-w,i,color=palette[g],alpha=.35,lw=.7,edgecolor=palette[g]);clouds.append(g)
        # All raw observations are retained; deterministic visual offsets, not fitted beeswarm.
        offset=.23+((np.arange(len(v))*0.61803398875)%1-.5)*.13
        ax.scatter(i+offset,v,c=palette[g],s=14 if len(v)>200 else 25,alpha=.4 if len(v)>200 else .8,lw=0,rasterized=len(v)>1000)
        if len(v)>=5:
            bp=ax.boxplot([v],positions=[i+.065],widths=.10,manage_ticks=False,showfliers=False,patch_artist=True,
                boxprops={'facecolor':'white','edgecolor':palette[g],'linewidth':.9},medianprops={'color':palette[g],'linewidth':1.2},
                whiskerprops={'color':'#B8BEC5','linewidth':.9},capprops={'color':'#B8BEC5','linewidth':.9})
    ax.set(xticks=np.arange(len(groups)),xticklabels=[f'{g}\nn={counts[g]:,}' for g in groups],ylabel=y_label,title=title,xlim=(-.55,len(groups)-.5));paper_axis(ax)
    caption=f'Points: {unit_label} | cloud only n >= {density_min_n} and >= 5 distinct values'
    fig.text(.14,.035,textwrap.fill(caption,width=max(48,int(fig.get_figwidth()*12))),fontsize=8,color='#7A838C',va='bottom')
    return stamp(fig,data,'publication_raincloud',palette=palette,unit_label=unit_label,y_label=y_label,density_groups=clouds,density_min_n=density_min_n,
        density='Scott Gaussian KDE restricted to observed min/max; area visually normalized within group',box='Q1/Q3 linear, median; whiskers at observations within1.5IQR; all raw points retained',counts=counts,point_offsets='deterministic input-order sequence',sampling='none')
