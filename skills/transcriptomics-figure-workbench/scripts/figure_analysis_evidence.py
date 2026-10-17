"""Question-specific companions from frozen results; no statistical estimation.

One shared drawing grammar supports explicitly typed scientific channels. The
method recipe, units, independent-unit context and full displayed scope remain
part of each FigureSpec. Geometry reuse does not imply interchangeable methods.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Arc
from figure_core import checked, stamp
from project_theme import apply_project_style, group_palette

KINDS=('profile','scatter','effects','raincloud','paired','matrix','fraction','bins','locus','embedding')

def _wrap(x,n=27):
    return '\n'.join(textwrap.wrap(str(x),n,break_long_words=False))

def _names(values):return list(dict.fromkeys(map(str,values)))

def _numeric(d,cols):return checked(d,list(cols),list(cols))

def _draw(ax,data,p,theme,table_axis=None):
    k=p['kind'];d=data.copy();positive=theme['roles']['positive'];negative=theme['roles']['negative']
    ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,width=.65)
    ax.set_title(_wrap(p['title'],22 if k=='effects' else 48),loc='left',fontsize=12,fontweight='bold',pad=16)
    ax.set(xlabel=p.get('x_label',''),ylabel=p.get('y_label',''))
    ax.grid(axis='y',color='#E6ECEE',lw=.55);ax.set_axisbelow(True)
    if k in ['profile','scatter','embedding']:
        d=checked(d,['series','x','y'],['x','y']);names=_names(d.series);pal=group_palette(theme,names)
        for name in names:
            q=d[d.series==name];c=pal[name]
            if k=='profile':
                if q.x.duplicated().any():raise ValueError('Unique frozen curve positions required')
                q=q.sort_values('x')
                if {'lower','upper'}<=set(q) and q[['lower','upper']].notna().any().any():
                    q=_numeric(q,['lower','upper'])
                    if not p.get('interval_definition') or ((q.lower>q.y)|(q.y>q.upper)).any():raise ValueError('Valid supplied intervals and definition required')
                    ax.fill_between(q.x,q.lower,q.upper,color=c,alpha=.13,lw=0,step='post' if p.get('steps') else None)
                ax.plot(q.x,q.y,color=c,lw=1.9,label=name,drawstyle='steps-post' if p.get('steps') else 'default')
            else:
                if not p.get('point_unit'):raise ValueError('Declare the observation represented by each point')
                ax.scatter(q.x,q.y,color=c,s=23 if len(d)<200 else 12,alpha=.72,ec='white',lw=.35,rasterized=True,label=name)
                if p.get('annotate'):
                    if 'label' not in q:raise ValueError('Explicit point labels required')
                    for r in q[q.label.isin(p['annotate'])].itertuples():ax.annotate(_wrap(r.label,18),(r.x,r.y),xytext=(4,6),textcoords='offset points',fontsize=9,color=c)
        if p.get('identity_reference'):
            lo=min(d.x.min(),d.y.min());hi=max(d.x.max(),d.y.max());ax.plot([lo,hi],[lo,hi],ls=(0,(3,3)),color='#95A8B1',lw=.8,zorder=0)
        if p.get('zero_reference'):
            ax.axhline(0,color='#95A8B1',lw=.8,ls=(0,(3,3)),zorder=0)
            ax.axvline(0,color='#95A8B1',lw=.8,ls=(0,(3,3)),zorder=0)
            ax.margins(x=.16,y=.16)
        if k=='embedding':ax.set_aspect('equal',adjustable='box')
        if k=='profile' and p.get('probability'):
            if ((d.y<0)|(d.y>1)).any():raise ValueError('Probability outside [0,1]')
            if p.get('steps') and any((g.sort_values('x').y.diff().dropna()>0).any() for _,g in d.groupby('series')):raise ValueError('Survival cannot increase')
            if p.get('steps'):ax.set_ylim(0,1.04)
        if k=='profile' and p.get('composition_profile'):
            if d.duplicated(['series','x']).any() or len(d)!=d.series.nunique()*d.x.nunique() or not np.allclose(d.groupby('x').y.sum(),1,rtol=0,atol=1e-8):raise ValueError('Complete base-composition profiles must sum to one at every position')
        if p.get('x_scale')=='log':
            if (d.x<=0).any():raise ValueError('Log coordinates must be positive')
            ax.set_xscale('log')
        band= k=='profile' and {'lower','upper'}<=set(d) and d[['lower','upper']].notna().any().any()
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),ncols=4 if len(names)==4 and max(map(len,names))<12 else min(3,len(names)),frameon=False,fontsize=9,handlelength=1.4,title=p.get('interval_label','Shading: supplied range') if band else None,title_fontsize=9)
    elif k=='effects':
        d=checked(d,['label','estimate','lower','upper'],['estimate','lower','upper'])
        if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.estimate>d.upper)).any() or not p.get('interval_definition'):raise ValueError('Unique effects and explicitly supplied valid intervals required')
        if p.get('probability') and ((d[['estimate','lower','upper']]<0)|(d[['estimate','lower','upper']]>1)).any().any():raise ValueError('Probability estimates and bounds must stay in [0,1]')
        if 'q' in d:
            d=_numeric(d,['q'])
            if ((d.q<0)|(d.q>1)).any() or not p.get('test_family'):raise ValueError('Define complete adjusted-probability family')
        if 'n' in d:
            d=_numeric(d,['n'])
            if (d.n<=0).any() or (d.n!=np.floor(d.n)).any():raise ValueError('Positive integer independent n required')
        ref=p.get('reference',0);ratio=p.get('effect_scale')=='ratio'
        if ratio:
            if ref!=1 or (d[['estimate','lower','upper']]<=0).any().any():raise ValueError('Ratios require positive values and reference one')
            ax.set_xscale('log')
        y=np.arange(len(d));colours=[positive if e>=ref else negative for e in d.estimate]
        for i,r in enumerate(d.itertuples()):
            if i%2==0:ax.axhspan(i-.46,i+.46,color='#F2F6F6',zorder=0)
            ax.plot([r.lower,r.upper],[i,i],c=colours[i],lw=2,zorder=2);ax.scatter(r.estimate,i,c=colours[i],s=43,ec='white',lw=.65,zorder=3)
        ax.axvline(ref,c='#94A8B1',lw=.8,ls=(0,(3,3)));ax.set_yticks(y,[_wrap(x,24) for x in d.label]);ax.set_ylim(len(d)-.35,-.8)
        ax.margins(x=.13);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(axis='x',color='#E6ECEE',lw=.55)
        if table_axis is None:raise ValueError('Effect tables need a dedicated aligned layout lane')
        table_axis.axis('off');table_axis.set_ylim(ax.get_ylim());table_axis.set_xlim(0,1)
        # A real sibling axis prevents outside text from collapsing other panels.
        for i,r in enumerate(d.itertuples()):
            fmt='.2f';text=format(r.estimate,fmt)+' ['+format(r.lower,fmt)+', '+format(r.upper,fmt)+']'
            if 'q' in d:text+=f'  {r.q:.2g}'
            if 'n' in d and d.n.nunique()>1:text+=f'  n={int(r.n)}'
            table_axis.text(.04,i,text,va='center',fontsize=9,color='#45616D',linespacing=1.35)
        n_label=p.get('n_label','Independent n')
        if not isinstance(n_label,str) or not n_label.strip() or len(n_label)>32:raise ValueError('A concise explicit support-count label is required')
        header='Estimate [interval]'+(' · q' if 'q' in d else '')
        if 'n' in d and d.n.nunique()==1:header+='\n'+n_label+' = '+str(int(d.n.iloc[0]))
        table_axis.set_title(header,loc='left',fontsize=10,fontweight='bold',pad=16)
        ax._analysis_effect_table=True
    elif k in ['raincloud','paired']:
        d=checked(d,['unit','series','value'],['value']);names=_names(d.series);pal=group_palette(theme,names)
        if d.duplicated(['unit','series']).any():raise ValueError('One observation per independent unit and group required')
        if p.get('probability') and ((d.value<0)|(d.value>1)).any():raise ValueError('Fractions must stay in [0,1]')
        if k=='paired':
            if len(names)!=2 or d.groupby('unit').size().ne(2).any():raise ValueError('Every paired unit must occur in both declared groups')
            for unit,q in d.groupby('unit',sort=False):
                q=q.set_index('series').reindex(names);ax.plot([0,1],q.value,color='#B4C7CE',lw=.9,zorder=1)
            for i,n in enumerate(names):ax.scatter(np.repeat(i,sum(d.series==n)),d.loc[d.series==n,'value'],s=31,c=pal[n],ec='white',lw=.5,zorder=3)
        else:
            from figure_raincloud_geometry import draw_supplied_raincloud
            if d.unit.duplicated().any():raise ValueError('Repeated units require an explicitly paired view')
            if set(p.get('cloud_shapes',{}))!=set(names):raise ValueError('Provide frozen cloud geometry for every group; no KDE during plotting')
            for i,n in enumerate(names):draw_supplied_raincloud(ax,i,d.loc[d.series==n,'value'],pal[n],p['cloud_shapes'][n],point_size=31)
        ax.set_xticks(range(len(names)),[_wrap(n,17)+'\nn='+str(sum(d.series==n)) for n in names]);ax.set_xlim(-.55,len(names)-.45)
    elif k=='matrix':
        d=checked(d,['label','series','value'],['value']);rows=_names(d.label);cols=_names(d.series)
        if d.duplicated(['label','series']).any() or len(d)!=len(rows)*len(cols):raise ValueError('Complete explicit matrix required; missing is not zero')
        lo,hi=p['limits']
        if lo>=hi or d.value.min()<lo-1e-9 or d.value.max()>hi+1e-9:raise ValueError('Declared scale cannot clip frozen values')
        signed=lo<0<hi;cmap=LinearSegmentedColormap.from_list('evidence',theme['continuous']['diverging' if signed else 'sequential'])
        norm=TwoSlopeNorm(vmin=lo,vcenter=0,vmax=hi) if signed else plt.Normalize(lo,hi)
        a=d.pivot(index='label',columns='series',values='value').reindex(index=rows,columns=cols).to_numpy();art=ax.imshow(a,cmap=cmap,norm=norm,aspect='auto',interpolation='nearest')
        if p.get('integer') and (d.value!=np.floor(d.value)).any():raise ValueError('Integer count matrix required')
        if p.get('binary') and not d.value.isin([0,1]).all():raise ValueError('Binary membership must contain explicit zero or one')
        if p.get('row_composition') and not np.allclose(a.sum(axis=1),1,atol=1e-8,rtol=0):raise ValueError('Complete variance components must sum to one by feature')
        if len(rows)*len(cols)<=64:
            for i in range(len(rows)):
                for j in range(len(cols)):
                    rgba=cmap(norm(a[i,j]));lum=sum(w*v for w,v in zip([.2126,.7152,.0722],rgba[:3]));ax.text(j,i,format(a[i,j],'.0f' if p.get('integer') else '.2g'),ha='center',va='center',fontsize=9,color='white' if lum<.45 else '#294B58')
        angle=25 if len(cols)<=4 or max(map(len,cols))>8 else 0
        ax.set_xticks(range(len(cols)),[_wrap(v,13) for v in cols],rotation=angle,ha='right' if angle else 'center');ax.set_yticks(range(len(rows)),[_wrap(v,24) for v in rows]);ax.grid(False);ax.spines[:].set_visible(False);ax.tick_params(length=0)
        cb=ax.figure.colorbar(art,ax=ax,fraction=.042,pad=.035,shrink=.85);cb.set_label(p['value_label'],fontsize=10);cb.ax.tick_params(labelsize=9)
    elif k=='fraction':
        d=checked(d,['label','series','value','denominator'],['value','denominator']);labels=_names(d.label);names=_names(d.series);pal=group_palette(theme,names)
        if d.duplicated(['label','series']).any() or len(d)!=len(labels)*len(names) or (d.value<0).any() or (d.denominator<=0).any() or not p.get('denominator_definition'):raise ValueError('Complete nonnegative counts/fractions and denominators required')
        totals=d.groupby('label',sort=False).value.sum()
        if not np.allclose(totals,1,rtol=0,atol=1e-8) or d.groupby('label').denominator.nunique().gt(1).any():raise ValueError('Frozen fractions must sum to one with consistent denominators')
        bottom=np.zeros(len(labels))
        for n in names:
            q=d[d.series==n].set_index('label').reindex(labels);ax.barh(range(len(labels)),q.value,left=bottom,height=.66,color=pal[n],ec='white',lw=.6,label=n);bottom+=q.value.to_numpy()
        for i,l in enumerate(labels):ax.text(1.025,i,'total='+format(d[d.label==l].denominator.iloc[0],'.0f'),va='center',fontsize=9,color='#58717C')
        ax.set_yticks(range(len(labels)),[_wrap(v,22) for v in labels]);ax.set_xlim(0,1);ax.invert_yaxis();ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),ncols=min(3,len(names)),frameon=False,fontsize=9)
    elif k=='bins':
        d=checked(d,['series','start','end','value'],['start','end','value']);names=_names(d.series);pal=group_palette(theme,names)
        if (d.start>=d.end).any() or (d.value<0).any():raise ValueError('Valid frozen bin bounds and nonnegative quantities required')
        for n in names:
            q=d[d.series==n].sort_values('start')
            if not np.allclose(q.start.iloc[1:].to_numpy(),q.end.iloc[:-1].to_numpy(),rtol=0,atol=1e-9):raise ValueError('Supply contiguous nonoverlapping bins, including explicit empty bins')
            edges=np.r_[q.start.to_numpy(),q.end.iloc[-1]]
            ax.stairs(q.value,edges,color=pal[n],fill=True,alpha=.10,lw=0)
            ax.stairs(q.value,edges,color=pal[n],fill=False,alpha=1,lw=1.6,label=n)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),ncols=min(3,len(names)),frameon=False,fontsize=9)
    elif k=='locus':
        d=checked(d,['series','record_type','start','end','value'],['start','end','value']);names=_names(d.series);pal=group_palette(theme,names)
        if p.get('coordinate_system')!='0-based half-open' or not p.get('genome_build') or not p.get('contig') or p.get('strand') not in ['+','-'] or (d.start>=d.end).any() or (d.value<0).any() or not set(d.record_type)<={'exon','junction','peak','link'}:raise ValueError('Explicit genomic build, contig, strand, ordered intervals and track types required')
        for i,n in enumerate(names):
            q=d[d.series==n];y=i*1.6
            for r in q.itertuples():
                if r.record_type in ['exon','peak']:ax.add_patch(Rectangle((r.start,y-.08),r.end-r.start,.16,color=pal[n],alpha=.8))
                else:
                    if r.record_type=='link' and not p.get('link_definition'):raise ValueError('Declare what the supplied genomic link means')
                    ax.add_patch(Arc(((r.start+r.end)/2,y),r.end-r.start,.9,theta1=0,theta2=180,color=pal[n],lw=1.1+min(r.value,60)/40));ax.text((r.start+r.end)/2,y+.52,format(r.value,'.2f' if r.record_type=='link' else '.0f'),ha='center',fontsize=9,color=pal[n])
        ax.set(xlim=(d.start.min()-30,d.end.max()+30),ylim=(-.5,len(names)*1.6),yticks=[i*1.6 for i in range(len(names))],yticklabels=names);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(False)
    for field,axis in [('x_limits','x'),('y_limits','y')]:
        if field in p:
            bounds=p[field]
            if len(bounds)!=2 or not np.isfinite(bounds).all() or bounds[0]>=bounds[1]:raise ValueError('Increasing finite coordinate bounds required')
            extent=ax.dataLim.intervalx if axis=='x' else ax.dataLim.intervaly
            if np.isfinite(extent).all() and (extent.min()<bounds[0]-1e-9 or extent.max()>bounds[1]+1e-9):raise ValueError('Coordinate bounds may not discard observations or intervals')
            getattr(ax,'set_'+axis+'lim')(bounds)
    return d

def plot_analysis_evidence(data,theme,*,panels,title,context,definition,columns='auto',rows=None):
    """Render complementary typed result views with explicit method context and layout."""
    needed={'independent_unit','independent_n','method_version','source_version','selection'}
    if not isinstance(context,dict) or set(context)!=needed or any(not str(v).strip() for v in context.values()):raise ValueError('Complete independent-unit and source context required')
    if type(context['independent_n']) is not int or context['independent_n']<1:raise ValueError('Positive independent-unit support required')
    if not title or not definition or not isinstance(panels,list) or not 1<=len(panels)<=12:raise ValueError('Explicit title, method definition and one to twelve panels required')
    ids=[p['id'] for p in panels]
    if len(ids)!=len(set(ids)) or set(data.panel_id)!=set(ids) or any(p.get('kind') not in KINDS or not p.get('definition') or not p.get('title') for p in panels):raise ValueError('Every supplied panel and its scientific definition must match exactly')
    for p in panels:
        d=data[data.panel_id==p['id']]
        if 'n' in d and d.n.notna().any() and d.n.dropna().max()>context['independent_n']:raise ValueError('Effective independent n exceeds declared support')
        if p['kind'] in ['raincloud','paired'] and d.unit.nunique()>context['independent_n']:raise ValueError('Displayed independent units exceed declared n')
    if rows is not None and (type(rows) is not int or not 1<=rows<=12):raise ValueError('Positive explicit rows required')
    cols=(math.ceil(len(panels)/rows) if rows else min(2,len(panels))) if columns=='auto' else columns
    if type(cols) is not int or not 1<=cols<=4:raise ValueError('Columns must be auto or one to four')
    nr=rows or math.ceil(len(panels)/cols)
    if nr*cols<len(panels):raise ValueError('Requested grid cannot retain all panels')
    longest=max([len(str(x)) for p in panels for x in data.loc[data.panel_id==p['id'],'label'].dropna()] or [12]) if 'label' in data else 12
    catcounts=[data.loc[data.panel_id==p['id'],'label'].nunique() if p['kind'] in ['effects','matrix','fraction'] and 'label' in data else 6 for p in panels]
    # Tall effect tables must not stretch unrelated clouds/profiles to that height.
    panel_heights=[max(3.5,1.9+n*.28) for n in catcounts]
    row_heights=[max(panel_heights[r*cols:min((r+1)*cols,len(panels))] or [3.5]) for r in range(nr)]
    effect=any(p['kind']=='effects' for p in panels);cell_w=9.2 if effect else 6.0
    matrix_cols=max([data.loc[data.panel_id==p['id'],'series'].nunique() for p in panels if p['kind']=='matrix'] or [0])
    if matrix_cols>4:cell_w=max(cell_w,matrix_cols*1.12)
    if longest>38:cell_w+=.7
    fig=plt.figure(figsize=(cell_w*cols,sum(row_heights)+1.25),layout='constrained')
    from figure_workbench.responsive import facet_slots
    slots=facet_slots(fig,len(panels),nr,cols,height_ratios=row_heights)
    for i,p in enumerate(panels):
        table=None
        if p['kind']=='effects':
            sub=slots[i].subgridspec(1,2,width_ratios=[1.05,1],wspace=.035)
            ax=fig.add_subplot(sub[0]);table=fig.add_subplot(sub[1],sharey=ax)
        else:ax=fig.add_subplot(slots[i])
        _draw(ax,data[data.panel_id==p['id']],p,theme,table)
        if len(panels)>1:ax.text(-.11,1.14,chr(65+i),transform=ax.transAxes,color='#26747A',fontsize=14,fontweight='bold')
    if len(panels)>1:fig.suptitle(_wrap(title,max(58,round(60*cols))),fontsize=14,fontweight='bold')
    fig.get_layout_engine().set(h_pad=.18,w_pad=.23,hspace=.24,wspace=.18)
    for ax in fig.axes:ax._explicit_guide_layout=True
    stamp(fig,data,'analysis_evidence',panels=panels,title=title,context=context,definition=definition,columns=columns,rows=rows,analysis_performed=False)
    return apply_project_style(fig,theme)
