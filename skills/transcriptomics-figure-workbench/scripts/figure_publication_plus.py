"""Attractive alternatives with explicit frozen channels and no upstream analysis."""
import copy
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from figure_core import checked
from figure_editorial import _finish, _axis, _order, validate_contract
from figure_package_styles import _new, _foot, _flat_axis
from project_theme import group_palette

INK='#243449'; GRID='#E7EBEF'; TEAL='#218C8D'; CORAL='#D8795B'


def _halfeye(data,theme,o):
    d=checked(data,['record_type','label'])
    if not set(d.record_type)<={'density','summary'}:raise ValueError('Only density and summary records are accepted')
    names=_order(d.label,o['order']);pal=group_palette(theme,names)
    if not 1<=len(names)<=12:raise ValueError('Use 1 to 12 named distributions')
    curves=checked(d[d.record_type=='density'],['x','density'],['x','density'])
    summaries=checked(d[d.record_type=='summary'],['estimate','lower','upper','inner_lower','inner_upper'],['estimate','lower','upper','inner_lower','inner_upper'])
    if not isinstance(o['interval_definition'],str) or not o['interval_definition'].strip():raise ValueError('Define the supplied intervals')
    if (curves.density<0).any() or len(summaries)!=len(names) or summaries.label.duplicated().any() or set(summaries.label)!=set(names):raise ValueError('Nonnegative curves and exactly one summary per label required')
    for row in summaries.itertuples():
        if not row.lower<=row.inner_lower<=row.estimate<=row.inner_upper<=row.upper:raise ValueError('Supplied intervals must be nested around the estimate')
    if type(o['reference']) not in [int,float] or not np.isfinite(o['reference']):raise ValueError('Finite reference required')
    maximum=float(curves.density.max())
    if maximum<=0:raise ValueError('Positive supplied density required')
    for name in names:
        q=curves[curves.label==name]
        if len(q)<8 or (np.diff(q.x)<=0).any() or q.density.max()<=0:raise ValueError('Preserve increasing, nonempty supplied density coordinates')
    height=max(3.7,1.7+.63*len(names));fig=_new(theme,o['title'],o['subtitle'],size=(6.8,height))
    ax=_axis(fig,[.29,.19,.49,.60]);_flat_axis(ax,'x')
    for i,name in enumerate(names):
        q=curves[curves.label==name];s=summaries[summaries.label==name].iloc[0]
        ax.fill_between(q.x,i,i+.60*q.density/maximum,color=pal[name],alpha=.56,lw=0)
        ax.plot(q.x,i+.60*q.density/maximum,color=pal[name],lw=1.1)
        ax.plot([s.lower,s.upper],[i-.12,i-.12],c=pal[name],lw=1.1,solid_capstyle='round')
        ax.plot([s.inner_lower,s.inner_upper],[i-.12,i-.12],c=pal[name],lw=3.3,solid_capstyle='round')
        ax.scatter([s.estimate],[i-.12],s=24,c=INK,edgecolors='white',lw=.65,zorder=4)
        ax.text(1.045,i+.05,f'{s.estimate:+.2f}\n[{s.lower:+.2f}, {s.upper:+.2f}]',transform=ax.get_yaxis_transform(),fontsize=7.1,color=INK,va='center',linespacing=1.5)
    ax.axvline(o['reference'],c='#A8B2BB',lw=.7,ls=(0,(3,3)),zorder=0)
    ax.set_yticks(range(len(names)),['\n'.join(textwrap.wrap(n,21)) for n in names]);ax.tick_params(axis='y',length=0,pad=9,labelsize=8)
    ax.set(ylim=(-.6,len(names)-.15),xlabel=o['x_label']);ax.spines['left'].set_visible(False)
    _foot(fig,o['interval_definition']+'; common density height scale, supplied curves and summaries. No KDE or interval estimation.')
    return fig


def _split_matrix(data,theme,o):
    d=checked(data,['row','column','value','row_group','column_group'],['value'])
    rows=_order(d.row,o['row_order']);cols=_order(d.column,o['column_order'])
    if len(rows)>40 or len(cols)>24 or len(d)!=len(rows)*len(cols) or d.duplicated(['row','column']).any():raise ValueError('Complete bounded grid required; missing cells are not zero')
    if (d.groupby('row').row_group.nunique()!=1).any() or (d.groupby('column').column_group.nunique()!=1).any():raise ValueError('One consistent supplied group per row and column required')
    rg=d.drop_duplicates('row').set_index('row').loc[rows].row_group.tolist();cg=d.drop_duplicates('column').set_index('column').loc[cols].column_group.tolist()
    for groups in [rg,cg]:
        blocks=[g for i,g in enumerate(groups) if i==0 or g!=groups[i-1]]
        if len(blocks)!=len(set(blocks)):raise ValueError('Declared group slices must be contiguous in the supplied order')
    limits=o['limits']
    if len(limits)!=2 or not np.isfinite(limits).all() or not limits[0]<0<limits[1] or (d.value<limits[0]).any() or (d.value>limits[1]).any():raise ValueError('Explicit signed limits must include all values')
    names=list(dict.fromkeys(rg+cg));pal=group_palette(theme,names);norm=TwoSlopeNorm(vmin=limits[0],vcenter=0,vmax=limits[1])
    cm=LinearSegmentedColormap.from_list('publication_diverging',theme['continuous']['diverging'])
    xx=np.arange(len(cols),dtype=float);yy=np.arange(len(rows),dtype=float)
    for i in range(1,len(cols)):xx[i:]+=.30 if cg[i]!=cg[i-1] else 0
    for i in range(1,len(rows)):yy[i:]+=.34 if rg[i]!=rg[i-1] else 0
    fig=_new(theme,o['title'],o['subtitle'],size=(6.8,max(4.1,1.9+.20*len(rows))))
    ax=fig.add_axes([.25,.24,.51,.51]);lookup=d.set_index(['row','column']).value
    for i,r in enumerate(rows):
        for j,c in enumerate(cols):ax.add_patch(Rectangle((xx[j]-.5,yy[i]-.5),1,1,facecolor=cm(norm(lookup.loc[r,c])),edgecolor='white',lw=.5))
        ax.add_patch(Rectangle((-.88,yy[i]-.5),.15,1,facecolor=pal[rg[i]],edgecolor='none',clip_on=False))
    for j,c in enumerate(cols):ax.add_patch(Rectangle((xx[j]-.5,-.92),1,.16,facecolor=pal[cg[j]],edgecolor='none',clip_on=False))
    ax.set(xlim=(-.5,xx[-1]+.5),ylim=(yy[-1]+.5,-.5));ax.set_xticks(xx,cols,rotation=40,ha='right',fontsize=7.4);ax.set_yticks(yy,rows,fontsize=7.8);ax.tick_params(length=0,pad=5);ax.tick_params(axis='y',pad=18)
    for sp in ax.spines.values():sp.set_visible(False)
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.84,.58,.018,.15]));cb.set_label(o['value_label'],fontsize=7.5);cb.ax.tick_params(labelsize=7)
    fig.legend(handles=[Line2D([],[],marker='s',ls='',mfc=pal[n],mec='none',label=n) for n in names],loc='upper left',bbox_to_anchor=(.80,.49),frameon=False,fontsize=7.1)
    _foot(fig,'Order and slice memberships supplied unchanged; no clustering, scaling, imputation or significance selection.')
    return fig


def _profile(data,theme,o):
    d=checked(data,['record_type','category','series','value','area'])
    if set(d.record_type)!={'profile'}:raise ValueError('Profile rows required')
    d=checked(d,['value','area'],['value','area']);rows=_order(d.category,o['category_order']);series=_order(d.series,o['series_order'])
    if len(series)>4 or len(rows)>40 or len(d)!=len(rows)*len(series) or d.duplicated(['category','series']).any() or (d.area<0).any():raise ValueError('Complete bounded profiles and nonnegative supplied areas required')
    if type(o['area_max']) not in [int,float] or not np.isfinite(o['area_max']) or o['area_max']<=0 or (d.area>o['area_max']).any():raise ValueError('Explicit common area scale must include all values')
    limits=o['value_limits']
    if len(limits)!=2 or not np.isfinite(limits).all() or not limits[0]<=0<limits[1] or (d.value<limits[0]).any() or (d.value>limits[1]).any():raise ValueError('Declare a shared range including zero and all values')
    pal=group_palette(theme,series);height=max(4.0,1.6+.18*len(rows));fig=_new(theme,o['title'],o['subtitle'],size=(6.9,height))
    n=len(series);w=.70/n
    for j,name in enumerate(series):
        ax=_axis(fig,[.12+j*w,.14,w-.035,.66]);q=d[d.series==name].set_index('category').loc[rows];y=np.arange(len(rows))
        for i in y[::2]:ax.axhspan(i-.5,i+.5,color='#F5F7F9',zorder=0)
        ax.hlines(y,0,q.value,color='#C7D0D8',lw=.65)
        ax.scatter(q.value,y,s=65*q.area/o['area_max'],color=pal[name],alpha=.86,edgecolors='white',lw=.45,zorder=3)
        ax.set(xlim=limits,ylim=(len(rows)-.5,-.5),xlabel=o['value_label']);ax.set_title(name,fontsize=9.1,color=pal[name],pad=12)
        ax.set_yticks(y,rows if j==0 else ['']*len(rows));ax.tick_params(axis='y',length=0,labelsize=7.1);ax.tick_params(axis='x',labelsize=7.1);ax.spines['left'].set_visible(False)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',mfc='#8799A8',mec='white',markersize=np.sqrt(65*k),label=f'{o["area_max"]*k:g}') for k in [.25,.5,1]],title=o['area_label'],loc='upper left',bbox_to_anchor=(.84,.69),frameon=False,fontsize=7,title_fontsize=7)
    _foot(fig,'Same categories, values and area quantities as the annular source; linear axes and common area scale. No smoothing.')
    return fig


def plot_publication_plus(data,theme,*,view,contract,options):
    """Frozen half-eye, split annotated matrix and aligned profile alternatives."""
    validate_contract(contract)
    routes={'halfeye':(_halfeye,'order interval_definition reference x_label'),
            'split_matrix':(_split_matrix,'row_order column_order limits value_label'),
            'profile':(_profile,'category_order series_order area_max area_label value_limits value_label')}
    if view not in routes or not isinstance(options,dict):raise ValueError('Choose an implemented publication alternative')
    fn,keys=routes[view];required=set(keys.split())|{'title','subtitle'}
    if set(options)!=required:raise ValueError('Use the complete documented options for the selected view')
    fig=fn(data,theme,copy.deepcopy(options))
    return _finish(fig,data,'publication_plus_'+view,contract,options,theme)
