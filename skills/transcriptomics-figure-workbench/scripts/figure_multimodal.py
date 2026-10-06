"""Original frozen-table renderers for computational biology; no analysis or fitting.

Python-only additive API. Existing R/Python interfaces are unchanged.
"""
from functools import wraps
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from figure_core import checked, stamp, palette_check, effect_reference

CATEGORY = ['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9']
SIGNED = LinearSegmentedColormap.from_list('omics_signed',['#0072B2','#FAFAF7','#D55E00'])
THEME = {'font.family':'Arial','font.size':9,'axes.labelsize':9,
         'axes.titlesize':10,'xtick.labelsize':8,'ytick.labelsize':8,
         'legend.fontsize':8,'axes.edgecolor':'#9CA6AE','axes.linewidth':.6,
         'text.color':'#27323C','axes.labelcolor':'#27323C',
         'xtick.color':'#49545E','ytick.color':'#49545E',
         'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'}

def themed(fn):
    @wraps(fn)
    def call(*args,**kwargs):
        with plt.rc_context(THEME):
            return fn(*args,**kwargs)
    return call

def axis(ax,grid=False):
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(length=3,width=.6)
    if grid: ax.grid(axis='y',color='#E7EBEE',lw=.5,zorder=0)

def required_text(**values):
    if any(not isinstance(v,str) or not v.strip() for v in values.values()):
        raise ValueError('Explicit nonempty semantic labels required')

def bounds(d):
    if ((d.lower>d.estimate)|(d.upper<d.estimate)).any():
        raise ValueError('Interval must contain supplied estimate')

@themed
def plot_cohort_intervals(data,palette,*,effect_scale,effect_label,interval_label,title=''):
    """Complete cohort x feature grid, comparable contrast/effect units, no pooling."""
    required_text(effect_label=effect_label,interval_label=interval_label)
    d=checked(data,['feature','cohort','estimate','lower','upper'],['estimate','lower','upper'])
    bounds(d);palette_check(d.cohort,palette);null=effect_reference(effect_scale)
    rows=list(dict.fromkeys(d.feature));cohorts=list(dict.fromkeys(d.cohort))
    if len(rows)>16 or len(cohorts)>6 or d.duplicated(['feature','cohort']).any() or len(d)!=len(rows)*len(cohorts):
        raise ValueError('Complete unique grid, max16 features/6 cohorts; split incompatible cohorts')
    if effect_scale=='ratio' and (d[['estimate','lower','upper']]<=0).any().any():
        raise ValueError('Ratio bounds must be positive')
    fig,ax=plt.subplots(figsize=(7.1,max(3.6,len(rows)*.55+1.6)))
    fig.subplots_adjust(left=.29,right=.97,bottom=.25,top=.86)
    ax.axvline(null,color='#AEB7BF',ls='--',lw=.8)
    offsets=np.linspace(-.27,.27,len(cohorts)) if len(cohorts)>1 else [0]
    for i,c in enumerate(cohorts):
        z=d[d.cohort==c].set_index('feature').loc[rows];yy=np.arange(len(rows))+offsets[i]
        ax.errorbar(z.estimate,yy,xerr=np.array([z.estimate-z.lower,z.upper-z.estimate]),
                    fmt=['o','s','D','^','v','P'][i],ms=4,color=palette[c],lw=1,capsize=2,label=c)
    ax.set_yticks(range(len(rows)),[textwrap.fill(str(x),25) for x in rows]);ax.invert_yaxis()
    if effect_scale=='ratio':ax.set_xscale('log')
    ax.set(xlabel=effect_label,title=title)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=min(3,len(cohorts)),frameon=False)
    axis(ax)
    return stamp(fig,data,'cohort_intervals',effect_scale=effect_scale,effect_label=effect_label,
                 interval_label=interval_label,null_value=null,palette=palette,pooling='none',cohort_order=cohorts)

@themed
def plot_association_matrix(data,*,value_label,method_label,alpha=.05,title='',
                            row_field='feature',column_field='modality',row_order=None,column_order=None,
                            row_aliases=None,column_aliases=None,cell_width=.7,cell_height=.36,label_rotation=25):
    """Frozen signed correlation with supplied FDR marks; missing entries hatch."""
    required_text(value_label=value_label,method_label=method_label)
    d=checked(data,[row_field,column_field,'status'])
    d=d.rename(columns={row_field:'feature',column_field:'modality'})
    if not {'value','q','n'}.issubset(d.columns) or not set(d.status).issubset({'estimable','unavailable'}):
        raise ValueError('Require status, value, q and matched n')
    rows=list(pd.unique(d.feature));cols=list(pd.unique(d.modality))
    if row_order is not None:
        row_order=list(row_order)
        if len(row_order)!=len(set(row_order)) or set(row_order)!=set(rows):raise ValueError('row_order must cover every row')
        rows=row_order
    if column_order is not None:
        column_order=list(column_order)
        if len(column_order)!=len(set(column_order)) or set(column_order)!=set(cols):raise ValueError('column_order must cover every column')
        cols=column_order
    if d.duplicated(['feature','modality']).any() or len(d)!=len(rows)*len(cols):
        raise ValueError('Explicit complete grid required')
    z=d[d.status=='estimable'];checked(z,['value','q','n'],['value','q','n'])
    if not 0<alpha<1 or ((z.value.abs()>1)|(z.q<0)|(z.q>1)|(z.n<3)|(z.n%1!=0)).any():
        raise ValueError('Correlation [-1,1], FDR [0,1], integer matched n>=3 required')
    if d.loc[d.status=='unavailable',['value','q','n']].notna().any().any():
        raise ValueError('Unavailable values must remain missing, never zero')
    fig,ax=plt.subplots(figsize=(max(5.5,len(cols)*float(cell_width)+2.8),max(3.6,len(rows)*float(cell_height)+1.8)))
    fig.subplots_adjust(left=.30,right=.86,bottom=.27,top=.85)
    values=d.pivot(index='feature',columns='modality',values='value').reindex(index=rows,columns=cols).to_numpy(dtype=float)
    im=ax.imshow(np.ma.masked_invalid(values),cmap=SIGNED,norm=TwoSlopeNorm(0,-1,1),aspect='auto')
    from matplotlib.patches import Rectangle
    for r in d.itertuples():
        i=rows.index(r.feature);j=cols.index(r.modality)
        if r.status=='unavailable':ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor='#F0F1F2',edgecolor='#AEB7BF',hatch='///',lw=.4))
        else:
            rgb=np.asarray(im.cmap(im.norm(r.value)))[:3]
            linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
            luminance=float(np.dot(linear,[.2126,.7152,.0722]))
            ink='white' if 1.05/(luminance+.05)>(luminance+.05)/.0556 else '#111111'
            label=f'{r.value:+.2f}' if len(rows)<=12 and len(cols)<=8 else ('+' if r.value>0 else '−' if r.value<0 else '0')
            ax.text(j,i,label,ha='center',va='center',fontsize=8,color=ink)
            if r.q<=alpha:ax.text(j+.30,i-.27,'•',ha='center',va='center',fontsize=8,color=ink)
    xlabels=[str((column_aliases or {}).get(x,x)) for x in cols];ylabels=[str((row_aliases or {}).get(x,x)) for x in rows]
    if len(set(xlabels))!=len(xlabels) or len(set(ylabels))!=len(ylabels):raise ValueError('Axis aliases must be unique')
    ax.set_xticks(range(len(cols)),[textwrap.fill(x,13) for x in xlabels],rotation=label_rotation,ha='right' if label_rotation else 'center')
    ax.set_yticks(range(len(rows)),[textwrap.fill(x,25) for x in ylabels]);ax.tick_params(length=0)
    for s in ax.spines.values():s.set_visible(False)
    ax.set_title(title,pad=12);fig.colorbar(im,ax=ax,fraction=.04,pad=.04,label=value_label)
    fig.text(.30,.09,f'• supplied FDR ≤ {alpha:g}; hatching = unavailable\n{method_label}; matched n in source table',fontsize=8)
    return stamp(fig,data,'association_matrix',value_label=value_label,method_label=method_label,
                 limits=[-1,1],alpha=alpha,missing='explicit_hatched_not_zero',statistics='frozen_no_fit',
                 row_field=row_field,column_field=column_field,row_order=rows,column_order=cols,
                 row_aliases=dict(zip(rows,ylabels)),column_aliases=dict(zip(cols,xlabels)),
                 label_rotation=label_rotation)

@themed
def plot_calibration_counts(data,palette,*,interval_label,evaluation_label,title=''):
    """Frozen reliability curve + actual bin counts; no rebinning or calibration fit."""
    required_text(interval_label=interval_label,evaluation_label=evaluation_label)
    d=checked(data,['model','bin_left','bin_right','predicted','estimate','lower','upper','n'],
              ['bin_left','bin_right','predicted','estimate','lower','upper','n'])
    bounds(d);palette_check(d.model,palette)
    prob=['bin_left','bin_right','predicted','estimate','lower','upper']
    if ((d[prob]<0)|(d[prob]>1)).any().any() or ((d.n<=0)|(d.n%1!=0)|(d.bin_left>=d.bin_right)|(d.predicted<d.bin_left)|(d.predicted>d.bin_right)).any():
        raise ValueError('Invalid probability bin, bound or count')
    models=list(dict.fromkeys(d.model))
    if len(models)>4:raise ValueError('Split more than four models')
    for m in models:
        z=d[d.model==m]
        if z.duplicated(['bin_left','bin_right']).any() or (np.diff(z.bin_left)<0).any() or (z.bin_left.to_numpy()[1:]<z.bin_right.to_numpy()[:-1]).any():
            raise ValueError('Sorted nonoverlapping bins required')
    fig,(ax,bx)=plt.subplots(2,1,figsize=(6.1,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1],'hspace':.12})
    fig.subplots_adjust(left=.15,right=.96,bottom=.20,top=.86)
    ax.plot([0,1],[0,1],ls='--',lw=.8,color='#AEB7BF')
    for i,m in enumerate(models):
        z=d[d.model==m];ls=['-','--','-.',':'][i]
        ax.errorbar(z.predicted,z.estimate,yerr=np.array([z.estimate-z.lower,z.upper-z.estimate]),
                    fmt=['o','s','D','^'][i],ls=ls,color=palette[m],ms=4,lw=1,capsize=2,label=m)
        for r in z.itertuples():bx.plot([r.bin_left,r.bin_left,r.bin_right,r.bin_right],[0,r.n,r.n,0],color=palette[m],ls=ls,lw=1)
    ax.set(xlim=(0,1),ylim=(0,1),ylabel='Observed event fraction',title=title)
    bx.set(xlabel='Mean predicted probability',ylabel='Bin n');ax.legend(frameon=False,loc='upper left')
    axis(ax);axis(bx)
    fig.text(.15,.075,textwrap.fill(f'{evaluation_label}; {interval_label}. Counts are within each model, not summed.',85),fontsize=8)
    return stamp(fig,data,'calibration_counts',palette=palette,interval_label=interval_label,
                 evaluation_label=evaluation_label,binning='frozen',count_semantics='within_model_evaluation_units')

@themed
def plot_interval_tracks(data,palette,*,assembly,chromosome,region,value_label,
                         coordinate_system='zero_based_half_open',title=''):
    """Prebinned disjoint intervals only, no BAM/bigWig parsing or invented genes."""
    required_text(assembly=assembly,chromosome=chromosome,value_label=value_label)
    d=checked(data,['track','start','end','value'],['start','end','value']);palette_check(d.track,palette)
    if coordinate_system!='zero_based_half_open' or len(region)!=2 or not np.isfinite(region).all() or region[0]<0 or region[0]>=region[1] or any(float(x)%1 for x in region):
        raise ValueError('Explicit integer zero-based half-open region required')
    if ((d.start<region[0])|(d.end>region[1])|(d.start>=d.end)|(d.start%1!=0)|(d.end%1!=0)).any():
        raise ValueError('Intervals must be valid and wholly inside region')
    tracks=list(dict.fromkeys(d.track))
    if len(tracks)>8:raise ValueError('Split more than eight tracks')
    for t in tracks:
        z=d[d.track==t]
        if (np.diff(z.start)<0).any() or (z.start.to_numpy()[1:]<z.end.to_numpy()[:-1]).any():raise ValueError('Sorted disjoint intervals required')
    fig,axs=plt.subplots(len(tracks),1,figsize=(7.1,max(3.2,len(tracks)*.9+1.5)),sharex=True,squeeze=False)
    fig.subplots_adjust(left=.21,right=.97,bottom=.23,top=.85,hspace=.32)
    lo=min(0,float(d.value.min()));hi=max(0,float(d.value.max()));pad=max((hi-lo)*.08,.01)
    for ax,t in zip(axs[:,0],tracks):
        for r in d[d.track==t].itertuples():ax.fill_between([r.start,r.end],[r.value,r.value],0,color=palette[t],alpha=.72,lw=0)
        ax.set(ylim=(lo-pad,hi+pad),ylabel=textwrap.fill(str(t),17));axis(ax)
    axs[-1,0].set(xlim=region,xlabel=f'{assembly} {chromosome} position (bp; 0-based half-open)')
    axs[-1,0].ticklabel_format(axis='x',style='plain',useOffset=False)
    axs[0,0].set_title(title,loc='left')
    fig.text(.21,.075,textwrap.fill(f'{value_label}; common y scale; unprovided intervals are gaps, not zeros',90),fontsize=8)
    return stamp(fig,data,'interval_tracks',assembly=assembly,chromosome=chromosome,region=list(region),
                 coordinate_system=coordinate_system,value_label=value_label,palette=palette,y_limits=[lo-pad,hi+pad],gap='unmeasured_not_zero')

@themed
def plot_frozen_dynamics(data,palette,*,time_label,value_label,unit_label,interval_label,title=''):
    """Supplied trajectory summaries/bounds, no smoothing, block averaging or simulation."""
    required_text(time_label=time_label,value_label=value_label,unit_label=unit_label,interval_label=interval_label)
    d=checked(data,['series','time','estimate','lower','upper'],['time','estimate','lower','upper'])
    bounds(d);palette_check(d.series,palette);names=list(dict.fromkeys(d.series))
    if len(names)>6 or d.duplicated(['series','time']).any():raise ValueError('Unique series/time required (max6 series)')
    if any((np.diff(d[d.series==s].time)<=0).any() for s in names):raise ValueError('Time order must be strictly increasing')
    fig,ax=plt.subplots(figsize=(7.1,4.1));fig.subplots_adjust(left=.14,right=.96,bottom=.25,top=.86)
    for i,s in enumerate(names):
        z=d[d.series==s];ax.fill_between(z.time,z.lower,z.upper,color=palette[s],alpha=.13,lw=0)
        ax.plot(z.time,z.estimate,color=palette[s],ls=['-','--','-.',':','-','--'][i],lw=1.5,label=s)
    ax.set(xlabel=time_label,ylabel=value_label,title=title);axis(ax,True);ax.legend(frameon=False)
    fig.text(.14,.085,textwrap.fill(f'{unit_label}; {interval_label}; frozen summaries, no smoothing.',95),fontsize=8)
    return stamp(fig,data,'frozen_dynamics',palette=palette,time_label=time_label,value_label=value_label,
                 unit_label=unit_label,interval_label=interval_label,smoothing='none',inference='none')

@themed
def plot_residue_confidence(data,*,sequence_label,title=''):
    """Supplied per-residue pLDDT: predicted local confidence, not flexibility/affinity."""
    required_text(sequence_label=sequence_label)
    d=checked(data,['residue','plddt'],['residue','plddt'])
    if ((d.residue<1)|(d.residue%1!=0)|(d.plddt<0)|(d.plddt>100)).any() or (np.diff(d.residue)<=0).any():
        raise ValueError('Sorted unique 1-based residues and pLDDT 0..100 required')
    fig,ax=plt.subplots(figsize=(7.1,3.5));fig.subplots_adjust(left=.12,right=.96,bottom=.28,top=.84)
    for a,b,c in [(0,50,'#F3F3F3'),(50,70,'#FAF6E9'),(70,90,'#EEF6FA'),(90,100,'#E3EFF6')]:ax.axhspan(a,b,color=c,zorder=0)
    for chunk in np.split(np.arange(len(d)),np.where(np.diff(d.residue)>1)[0]+1):
        z=d.iloc[chunk];ax.plot(z.residue,z.plddt,color='#0072B2',lw=1.3,marker='.' if len(z)<3 else None)
    ax.set(ylim=(0,100),xlabel='Residue (1-based)',ylabel='pLDDT (0–100)',title=title);axis(ax)
    fig.text(.12,.09,textwrap.fill(f'{sequence_label}. Predicted local confidence; not experimental B-factor, dynamics, binding affinity or domain orientation.',100),fontsize=8)
    return stamp(fig,data,'residue_confidence',sequence_label=sequence_label,scale=[0,100],
                 missing_residues='gaps_not_connected',interpretation='predicted_local_confidence_only')


