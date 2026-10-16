"""Original general-purpose frozen-table renderers; no statistics are fitted."""
import numpy as np
import pandas as pd
import textwrap
from figure_core import checked, palette_check, canvas, stamp


def text_required(**labels):
    if any(not isinstance(v,str) or not v.strip() for v in labels.values()):
        raise ValueError('Explicit nonempty semantic labels are required')


def plot_xy_points(data,palette,x_label,y_label,*,unit_label,connect_order=False):
    text_required(x=x_label,y=y_label,unit=unit_label)
    d=checked(data,['unit_id','group','x','y'],['x','y'])
    if d.unit_id.duplicated().any(): raise ValueError('One row per independent unit required')
    palette_check(d.group,palette);fig,ax=canvas()
    if type(connect_order) is not bool:raise ValueError('Explicit boolean connection setting required')
    for g in pd.unique(d.group):
        sub=d[d.group==g]
        if connect_order:
            if len(sub)<2 or (np.diff(sub.x)<=0).any():raise ValueError('Connected points need an explicitly increasing input order')
            ax.plot(sub.x,sub.y,color=palette[g],lw=1.2,alpha=.8,zorder=1)
        ax.scatter(sub.x,sub.y,color=palette[g],s=27,alpha=.8,label=g,linewidths=.3,edgecolors='white',zorder=2)
    ax.set(xlabel=x_label,ylabel=y_label);ax.legend(frameon=False)
    return stamp(fig,data,'xy_points',palette=palette,x_label=x_label,y_label=y_label,unit_label=unit_label,
                 connect_order=connect_order,inference='No correlation, fit or p-value computed; connected order is supplied')


def plot_grouped_estimates(data,palette,y_label,*,interval_label):
    text_required(y=y_label,interval=interval_label)
    d=checked(data,['category','group','estimate','lower','upper'],['estimate','lower','upper'])
    if d.duplicated(['category','group']).any() or len(d)!=d.category.nunique()*d.group.nunique():
        raise ValueError('Complete unique category-by-group grid required')
    if ((d.lower>d.estimate)|(d.upper<d.estimate)).any(): raise ValueError('Invalid supplied interval')
    palette_check(d.group,palette);fig,ax=canvas();cats=list(pd.unique(d.category));groups=list(pd.unique(d.group))
    width=.75/len(groups)
    for i,g in enumerate(groups):
        sub=d[d.group==g].set_index('category').loc[cats];x=np.arange(len(cats))+(i-(len(groups)-1)/2)*width
        ax.bar(x,sub.estimate,width*.9,color=palette[g],label=g,zorder=2)
        ax.errorbar(x,sub.estimate,yerr=np.array([sub.estimate-sub.lower,sub.upper-sub.estimate]),
                    fmt='none',ecolor='#344149',capsize=2,linewidth=.8,zorder=3)
    ax.axhline(0,color='#8B949B',linewidth=.6);ax.set_xticks(range(len(cats)),cats)
    ax.set(ylabel=y_label,title=interval_label);ax.legend(frameon=False)
    return stamp(fig,data,'grouped_estimates',palette=palette,y_label=y_label,interval_label=interval_label,
                 baseline=0,ordering='first appearance',statistics='Supplied estimates and intervals; no aggregation')


def plot_binned_distribution(data,palette,x_label,*,denominator_label):
    text_required(x=x_label,denominator=denominator_label)
    d=checked(data,['group','left','right','count'],['left','right','count'])
    if ((d.right<=d.left)|(d['count']<0)|(d['count']%1!=0)).any(): raise ValueError('Positive bin widths and nonnegative integer counts required')
    bins=[]
    for g in pd.unique(d.group):
        sub=d[d.group==g]
        if sub.duplicated(['left','right']).any() or (np.diff(sub.left)<0).any() or (sub.left.to_numpy()[1:]<sub.right.to_numpy()[:-1]).any():
            raise ValueError('Bins must be unique, ordered and non-overlapping within group')
        bins.append(list(zip(sub.left,sub.right)))
    if any(b!=bins[0] for b in bins[1:]): raise ValueError('Comparable groups need identical supplied bins')
    palette_check(d.group,palette);fig,ax=canvas()
    for g in pd.unique(d.group):
        sub=d[d.group==g]
        # Explicit bin boundaries and plateau counts; gaps remain visible as missing spans.
        for j,row in enumerate(sub.itertuples()):
            ax.plot([row.left,row.right],[row.count,row.count],color=palette[g],label=g if j==0 else None,linewidth=1.8)
            if j and row.left==sub.iloc[j-1].right:
                ax.plot([row.left,row.left],[sub.iloc[j-1]['count'],row.count],color=palette[g],linewidth=1.8)
    ax.set(xlabel=x_label,ylabel='Count',ylim=(0,None));ax.legend(title=denominator_label,frameon=False)
    return stamp(fig,data,'binned_distribution',palette=palette,x_label=x_label,denominator_label=denominator_label,
                 binning='Frozen input boundaries; no rebinning, normalization or density fit')


def plot_confusion_counts(data,*,unit_label,label_order=None,label_aliases=None,label_wrap=None,figsize=None):
    text_required(unit=unit_label)
    d=checked(data,['actual','predicted','count'],['count'])
    labels=list(pd.unique(d.actual))
    if label_order is not None:
        labels=list(label_order)
        if len(labels)!=len(set(labels)) or set(labels)!=set(d.actual): raise ValueError('label_order must cover every observed class exactly once')
    if set(labels)!=set(d.predicted) or d.duplicated(['actual','predicted']).any() or len(d)!=len(labels)**2:
        raise ValueError('Complete unique square class grid required')
    if ((d['count']<0)|(d['count']%1!=0)).any() or d['count'].sum()==0: raise ValueError('Nonnegative integer counts and positive total required')
    matrix=d.pivot(index='actual',columns='predicted',values='count').loc[labels,labels]
    if label_wrap is not None and (type(label_wrap) is not int or label_wrap<1): raise ValueError('label_wrap must be a positive integer or None')
    shown=[str((label_aliases or {}).get(x,x)) for x in labels]
    if len(set(shown))!=len(shown) or any(not x.strip() for x in shown): raise ValueError('label_aliases must be nonempty and unique')
    shown=[textwrap.fill(x,label_wrap) if label_wrap else x for x in shown]
    if figsize is None: figsize=(max(5.4,len(labels)*.55+3.2),max(4.3,len(labels)*.46+1.8))
    if not isinstance(figsize,(tuple,list)) or len(figsize)!=2 or any(float(x)<=0 for x in figsize): raise ValueError('figsize must be a positive (width, height) pair')
    fig,ax=canvas(); fig.set_layout_engine(None); fig.set_size_inches(float(figsize[0]),float(figsize[1])); image=ax.imshow(matrix,cmap='Blues',vmin=0,aspect='equal')
    for i,row in enumerate(matrix.to_numpy()):
        for j,n in enumerate(row): ax.text(j,i,str(int(n)),ha='center',va='center',color='white' if n>matrix.to_numpy().max()*.6 else '#243947')
    ax.set_xticks(range(len(labels)),shown,rotation=45,ha='right');ax.set_yticks(range(len(labels)),shown)
    fig.subplots_adjust(left=min(.42,max(.12,.12+max(len(x.replace('\n','')) for x in shown)*.004)),bottom=.25,right=.84)
    ax.set(xlabel='Predicted class',ylabel='Observed class');fig.colorbar(image,ax=ax,label='Count: '+unit_label)
    return stamp(fig,data,'confusion_counts',unit_label=unit_label,total=int(d['count'].sum()),label_order=labels,label_aliases=dict(zip(labels,shown)),figsize=list(map(float,figsize)),
                 semantics='Rows observed, columns predicted; no model fitting, threshold choice or accuracy calculation')


def plot_density_ridges(data,palette,x_label,*,density_label,amplitude=.8,height_scale=None,title=''):
    text_required(x=x_label,density=density_label)
    d=checked(data,['group','x','density'],['x','density']);palette_check(d.group,palette)
    if (d.density<0).any() or not np.isfinite(amplitude) or not 0<amplitude<=1:
        raise ValueError('Nonnegative densities and amplitude in (0,1] required')
    grids=[]
    for g in pd.unique(d.group):
        sub=d[d.group==g]
        if len(sub)<2 or (np.diff(sub.x)<=0).any(): raise ValueError('Strictly increasing x grid required in each group')
        grids.append(sub.x.to_list())
    if any(grid!=grids[0] for grid in grids[1:]): raise ValueError('Identical density grids required')
    peak=d.density.max()
    if peak<=0: raise ValueError('Positive density peak required')
    scale=amplitude/peak if height_scale is None else height_scale
    if not np.isfinite(scale) or scale<=0 or scale*peak>.95:raise ValueError('Common density height scale must fit between baselines')
    fig,ax=canvas();groups=list(pd.unique(d.group))
    for i,g in enumerate(groups):
        sub=d[d.group==g];y=i+sub.density.to_numpy()*scale
        ax.fill_between(sub.x,i,y,color=palette[g],alpha=.45);ax.plot(sub.x,y,color=palette[g],linewidth=1.2)
    ax.set_yticks(range(len(groups)),groups);ax.set(xlabel=x_label,ylabel=density_label,title=title)
    return stamp(fig,data,'density_ridges',palette=palette,x_label=x_label,density_label=density_label,
                 shared_display_scale=float(scale),density_estimation='Upstream only; no KDE, bandwidth choice or per-group rescaling',demo_label_style='compact')
