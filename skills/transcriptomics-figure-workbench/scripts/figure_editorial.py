"""Rebuilt figure grammar: proportion, hierarchy and supplied-data semantics first."""
import textwrap
import copy
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors,ticker
from matplotlib.lines import Line2D
from matplotlib.legend import Legend
from figure_core import checked,stamp,effect_reference
from project_theme import group_palette

KINDS=('volcano','rank','paired','roc','forest','matrix')
INK='#273540'
MUTED='#637381'
GRID='#E6EBEF'


def _canvas(theme,size,title):
    from figure_workbench.responsive import canvas_budget
    canvas_budget(*size)
    with plt.rc_context({'font.family':theme['font_family'],'font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'}):
        fig=plt.figure(figsize=size,facecolor='white')
    fig.text(.10,1-.18/size[1],title,ha='left',va='top',fontsize=10.5,fontweight='normal',color=INK,fontfamily=theme['font_family'])
    badge=fig.text(.985,.992,'',ha='right',va='top',fontsize=6.2,color=MUTED,fontfamily=theme['font_family'])
    fig._software_band_artists=[badge]
    return fig


def _axis(fig,bounds):
    ax=fig.add_axes(bounds)
    ax.spines[['top','right']].set_visible(False)
    for side in ['left','bottom']:ax.spines[side].set(color='#687681',linewidth=.65)
    ax.tick_params(labelsize=8.3,length=3,width=.6,color='#687681',labelcolor=INK,pad=3)
    ax.xaxis.label.set(size=9,color=INK);ax.yaxis.label.set(size=9,color=INK)
    ax.set_axisbelow(True)
    return ax


def _finish(fig,data,kind,contract,options,theme):
    for ax in fig.axes:
        for obj in [*ax.get_xticklabels(),*ax.get_yticklabels(),ax.xaxis.label,ax.yaxis.label,*ax.texts]:
            obj.set_fontfamily(fig._editorial_font)
    from matplotlib.text import Text
    factor=theme['design']['label_pt']/10
    for obj in fig.findobj(Text):
        obj.set_fontsize(obj.get_fontsize()*factor)
        obj.set_fontfamily(theme['font_family'])
    line_factor=theme['line_width']/1.4
    for ax in fig.axes:
        for line in ax.lines:line.set_linewidth(line.get_linewidth()*line_factor)
    from figure_layout import optimize_guide_layout
    fig._omics_spec={}
    fig=optimize_guide_layout(fig)
    guide_layout=fig._omics_spec.get('guide_layout')
    text_audit=audit_text_geometry(fig)
    if text_audit['issues']:
        plt.close(fig)
        raise ValueError('Text layout needs repair: '+str(text_audit['issues']))
    return stamp(fig,data,'editorial_rebuild',kind_mode=kind,contract=contract,options=options,
                 visual_acceptance=False,scientific_analysis='none; frozen inputs only',
                 design_system='editorial-v3-candidate',synthetic_only=False,text_geometry=text_audit,guide_layout=guide_layout,project_theme=copy.deepcopy(theme),
                 project_theme_sha256=hashlib.sha256(json.dumps(theme,sort_keys=True,separators=(',',':')).encode()).hexdigest())


def _order(actual,requested):
    actual=list(dict.fromkeys(actual))
    if requested is None:return actual
    if len(requested)!=len(set(requested)) or set(requested)!=set(actual):raise ValueError('Display order must preserve all identities')
    return list(requested)


def validate_contract(contract):
    if not isinstance(contract,dict) or any(not isinstance(contract.get(k),str) or not contract[k].strip() for k in
        ['source_definition','independent_unit','denominator','value_definition','uncertainty_definition']):
        raise ValueError('Explicit frozen-input and unit contract required')
    if type(contract.get('synthetic')) is not bool:
        raise ValueError('Declare whether the supplied values are synthetic')


def audit_text_geometry(fig):
    """Final-size label bounds/collisions only; this is not aesthetic acceptance."""
    fig.canvas.draw();renderer=fig.canvas.get_renderer();objects=list(fig.texts)
    for ax in fig.axes:
        objects.extend(ax.texts)
        if ax.axison:
            objects.extend([ax.xaxis.label,ax.yaxis.label,ax.title,ax.xaxis.get_offset_text(),ax.yaxis.get_offset_text()])
            for positions,labels,limits in [(ax.get_xticks(),ax.get_xticklabels(),ax.get_xlim()),
                                             (ax.get_yticks(),ax.get_yticklabels(),ax.get_ylim())]:
                lo,hi=sorted(limits)
                objects.extend(label for value,label in zip(positions,labels) if lo-1e-9<=value<=hi+1e-9)
    for legend in fig.findobj(Legend):
        if legend.get_visible():objects.extend(legend.get_texts());objects.append(legend.get_title())
    shown=[];issues=[];seen=set();canvas=fig.bbox
    for obj in objects:
        if id(obj) in seen or not obj.get_visible() or not obj.get_text().strip():continue
        seen.add(id(obj));box=obj.get_window_extent(renderer)
        if box.width<=0 or box.height<=0:continue
        text=obj.get_text()[:80]
        if box.x0<canvas.x0-1 or box.y0<canvas.y0-1 or box.x1>canvas.x1+1 or box.y1>canvas.y1+1:
            issues.append({'kind':'text_outside_canvas','label':text})
        for other,ob in shown:
            width=min(box.x1,ob.x1)-max(box.x0,ob.x0);height=min(box.y1,ob.y1)-max(box.y0,ob.y0)
            if width>1 and height>1 and width*height>.08*min(box.width*box.height,ob.width*ob.height):
                issues.append({'kind':'text_collision','labels':[other,text]})
        shown.append((text,box))
    return {'status':'TEXT_GEOMETRY_ONLY','issues':issues,'labels_checked':len(shown),
            'scope':'Visible labels, annotations, ticks and legends at current physical size; no perceptual or scientific acceptance'}


def _paired_display_offsets(values, ax):
    """Shared pair offsets avoid endpoint collisions; measured Y values never move."""
    ax.figure.canvas.draw();xy=ax.transData.transform(np.column_stack([np.zeros(len(values)),values[:,0]]))
    yy=ax.transData.transform(np.column_stack([np.ones(len(values)),values[:,1]]))[:,1]
    dx=float(ax.transData.transform((1,0))[0]-ax.transData.transform((0,0))[0])
    gap=5.7*ax.figure.dpi/72
    candidates=[0.]+[sign*.035*k for k in range(1,6) for sign in [1,-1]]
    offsets=[]
    for i in range(len(values)):
        for offset in candidates:
            if all((dx*(offset-prev))**2+(xy[i,1]-xy[j,1])**2>=gap**2 and
                   (dx*(offset-prev))**2+(yy[i]-yy[j])**2>=gap**2 for j,prev in enumerate(offsets)):
                offsets.append(offset);break
        else:raise ValueError('Paired endpoints too dense at this size; use declared facets')
    return np.asarray(offsets)


def plot_editorial(data,theme,*,kind,contract,options=None):
    """Six rebuilt frozen-result modes. Candidate aesthetics require actual review."""
    if kind not in KINDS:raise ValueError('Choose a rebuilt visual grammar')
    validate_contract(contract)
    options={} if options is None else dict(options)
    allowed={'title','x_label','y_label','order','alpha','effect_cutoff','effect_scale','interval_label','limits','scale_type','row_order','column_order'}
    if set(options)-allowed:raise ValueError('Unknown editorial display option')
    title=options.get('title',kind.replace('_',' ').title())
    if not isinstance(title,str) or not title.strip():raise ValueError('Display title required')

    if kind=='volcano':
        d=checked(data,['gene','log2FC','padj'],['log2FC','padj'])
        if d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any():raise ValueError('Unique genes and adjusted P in (0,1] required')
        alpha=options.get('alpha',.05);cut=options.get('effect_cutoff',1.)
        if not 0<alpha<1 or not np.isfinite(cut) or cut<=0:raise ValueError('Declare valid display thresholds')
        fig=_canvas(theme,(4.4,3.55),title);ax=_axis(fig,[.145,.17,.79,.64])
        y=-np.log10(d.padj);up=(d.log2FC>cut)&(d.padj<alpha);down=(d.log2FC<-cut)&(d.padj<alpha)
        palette={'Unselected':'#A9B1BA','Lower':theme['roles']['negative'],'Higher':theme['roles']['positive']}
        for label,mask,area,opacity in [('Unselected',~(up|down),9,.5),('Lower',down,13,.88),('Higher',up,13,.88)]:
            ax.scatter(d.loc[mask,'log2FC'],y[mask],s=area,c=palette[label],alpha=opacity,linewidths=0,rasterized=True,zorder=3)
        ax.axhline(-np.log10(alpha),ls=(0,(3,3)),color='#AAB4BC',lw=.65,zorder=1)
        for x in [-cut,cut]:ax.axvline(x,ls=(0,(3,3)),color='#AAB4BC',lw=.65,zorder=1)
        ax.set(xlabel=options.get('x_label',r'$\log_2$ fold change'),ylabel=options.get('y_label',r'$-\log_{10}$ adjusted P'))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(5));ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
        handles=[Line2D([],[],marker='o',ls='',ms=4,color=palette[k],label=k) for k in ['Lower','Unselected','Higher']]
        fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.125,.895),ncol=3,frameon=False,fontsize=7.5,handletextpad=.45,columnspacing=1.4)
    elif kind=='rank':
        d=checked(data,['group','stage','rank'],['rank'])
        if d.duplicated(['group','stage']).any() or ((d['rank']<1)|(d['rank']%1!=0)).any():raise ValueError('Unique stored integer ranks required in this mode')
        stages=_order(d.stage,options.get('order'));groups=list(dict.fromkeys(d.group));pal=group_palette(theme,groups)
        if len(d)!=len(stages)*len(groups) or len(groups)>8:raise ValueError('Complete rank grid with at most eight groups required')
        if d.loc[d.stage==stages[-1],'rank'].duplicated().any():raise ValueError('Tied endpoint ranks need an explicitly faceted design')
        fig=_canvas(theme,(4.6,3.05),title);ax=_axis(fig,[.12,.18,.67,.62]);markers=['o','s','D','^','v','P','X','h']
        for index,g in enumerate(groups):
            sub=d[d.group==g].set_index('stage').loc[stages]
            ax.plot(range(len(stages)),sub['rank'],color=pal[g],lw=1.4,marker=markers[index],ms=4,mec='white',mew=.5)
            end=float(sub['rank'].iloc[-1]);ax.annotate(str(g),xy=(len(stages)-1,end),xytext=(10,0),textcoords='offset points',
                color=INK,fontsize=8.3,ha='left',va='center',annotation_clip=False)
        maximum=int(d['rank'].max());ax.set_ylim(maximum+.28,.72)
        if maximum<=12:ax.set_yticks(range(1,maximum+1))
        else:ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True,nbins=6))
        ax.set_xticks(range(len(stages)),stages);ax.set_ylabel(options.get('y_label','Rank (1 = highest)'))
        ax.grid(axis='y',color=GRID,lw=.6);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
    elif kind=='paired':
        d=checked(data,['subject_id','condition','value'],['value']);conditions=_order(d.condition,options.get('order'))
        if len(conditions)!=2 or d.duplicated(['subject_id','condition']).any() or (d.groupby('subject_id').size()!=2).any():raise ValueError('Exact complete pairs required')
        pal=group_palette(theme,conditions);fig=_canvas(theme,(3.55,3.25),title);ax=_axis(fig,[.18,.19,.72,.61])
        values=d.pivot(index='subject_id',columns='condition',values='value').loc[:,conditions]
        if len(values)>40:raise ValueError('Use facets for more than forty complete pairs')
        span=float(values.to_numpy().max()-values.to_numpy().min());pad=max(span*.06,.05)
        ax.set_xlim(-.25,1.25);ax.set_ylim(values.to_numpy().min()-pad,values.to_numpy().max()+pad)
        offsets=_paired_display_offsets(values.to_numpy(),ax)
        for row,offset in zip(values.to_numpy(),offsets):ax.plot([offset,1+offset],row,color='#AFBBC5',lw=.7,alpha=.65,zorder=1)
        for i,g in enumerate(conditions):ax.scatter(i+offsets,values[g],s=23,color=pal[g],edgecolors='white',linewidths=.55,zorder=3)
        ax.set_xticks([0,1],conditions);ax.set_xlim(-.25,1.25);ax.set_ylabel(options.get('y_label','Measurement (demo units)'))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(5));ax.grid(axis='y',color=GRID,lw=.55)
        fig.text(.18,.855,str(len(values))+' complete pairs',color=MUTED,fontsize=7.5)
    elif kind=='roc':
        d=checked(data,['model','x','y'],['x','y']);groups=_order(d.model,options.get('order'));pal=group_palette(theme,groups)
        if ((d[['x','y']]<0)|(d[['x','y']]>1)).any().any() or len(groups)>4:raise ValueError('Stored probability coordinates and at most four curves required')
        fig=_canvas(theme,(4.3,3.55),title);ax=_axis(fig,[.14,.2,.55,.64]);styles=['-','--','-.',':']
        for i,g in enumerate(groups):
            sub=d[d.model==g]
            if (np.diff(sub.x)<0).any() or (np.diff(sub.y)<0).any():raise ValueError('Preserve monotonic stored ROC threshold order on both axes')
            ax.step(sub.x,sub.y,where='post',color=pal[g],ls=styles[i],lw=1.6,label=g,zorder=3)
        ax.plot([0,1],[0,1],color='#AFBAC3',lw=.75,ls=(0,(3,3)),zorder=1)
        ax.set(xlim=(0,1),ylim=(0,1),aspect='equal',xlabel='False-positive rate',ylabel='True-positive rate')
        ax.set_xticks([0,.25,.5,.75,1]);ax.set_yticks([0,.25,.5,.75,1]);ax.grid(color=GRID,lw=.45)
        ax.legend(loc='upper left',bbox_to_anchor=(1.035,1),frameon=False,fontsize=7.5,handlelength=1.8,borderaxespad=0,labelspacing=.8)
    elif kind=='forest':
        d=checked(data,['label','group','estimate','lower','upper'],['estimate','lower','upper'])
        if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():raise ValueError('Unique labels and valid supplied intervals required')
        scale=options.get('effect_scale','difference');null=effect_reference(scale)
        if scale=='ratio' and (d[['estimate','lower','upper']]<=0).any().any():raise ValueError('Ratio intervals must be positive')
        groups=list(dict.fromkeys(d.group));pal=group_palette(theme,groups)
        stride=max(.31,max(len(textwrap.wrap(str(s),28)) for s in d.label)*.16)
        height=max(3.0,stride*len(d)+1.5)
        fig=_canvas(theme,(6.3,height),title);bottom=.45/height;top=1-1.05/height
        left=fig.add_axes([.035,bottom,.31,top-bottom]);ax=_axis(fig,[.36,bottom,.37,top-bottom]);right=fig.add_axes([.755,bottom,.23,top-bottom])
        y=np.arange(len(d));bounds=(len(d)-.48,-.65)
        for a in [left,ax,right]:a.set_ylim(*bounds)
        for a in [left,right]:a.set(xlim=(0,1));a.axis('off')
        if scale=='ratio':ax.set_xscale('log')
        for i,row in enumerate(d.itertuples()):
            left.text(.04,i,'\n'.join(textwrap.wrap(str(row.label),28)),va='center',fontsize=8.3,color=INK)
            ax.errorbar(row.estimate,i,xerr=[[row.estimate-row.lower],[row.upper-row.estimate]],fmt='o',ms=4.6,color=pal[row.group],
                ecolor=pal[row.group],elinewidth=1.15,capsize=2.1,capthick=.75,mec='white',mew=.45,zorder=3)
            right.text(.025,i,f'{row.estimate:.2f}  [{row.lower:.2f}, {row.upper:.2f}]',va='center',fontsize=8.0,color=INK)
        ax.axvline(null,color='#83939F',ls=(0,(3,3)),lw=.8,zorder=1);ax.set_yticks([]);ax.spines[['left','right','top']].set_visible(False)
        ax.set_xlabel(options.get('x_label','Effect size'),fontsize=8.5,labelpad=4)
        if scale!='ratio':ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
        left.text(.04,1.025,'Comparison',transform=left.transAxes,fontsize=7.5,color=MUTED)
        right.text(.025,1.025,'Estimate [interval]',transform=right.transAxes,fontsize=7.5,color=MUTED)
    else:
        d=checked(data,['feature','sample','value'],['value'])
        rows=_order(d.feature,options.get('row_order'));columns=_order(d['sample'],options.get('column_order'))
        if d.duplicated(['feature','sample']).any() or len(d)!=len(rows)*len(columns):raise ValueError('Complete matrix required; missing is not zero')
        limits=options.get('limits')
        if not isinstance(limits,(list,tuple)) or len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1]:raise ValueError('Explicit common color limits required')
        if ((d.value<limits[0])|(d.value>limits[1])).any():raise ValueError('Color limits would clip supplied values')
        if options.get('scale_type','signed') not in ('signed','sequential'):raise ValueError('Unknown matrix scale')
        signed=options.get('scale_type','signed')=='signed'
        if signed and not limits[0]<0<limits[1]:raise ValueError('Signed scale must straddle zero')
        width=max(3.8,len(columns)*.34+1.95);height=max(2.65,len(rows)*.28+1.0)
        fig=_canvas(theme,(width,height),title);ax=fig.add_axes([.28,.23,.51,.57]);cax=fig.add_axes([.83,.23,.018,.57])
        matrix=d.pivot(index='feature',columns='sample',values='value').loc[rows,columns]
        cmap=colors.LinearSegmentedColormap.from_list('editorial_matrix',theme['continuous']['diverging' if signed else 'sequential'])
        norm=colors.TwoSlopeNorm(vmin=limits[0],vcenter=0,vmax=limits[1]) if signed else colors.Normalize(*limits)
        image=ax.pcolormesh(np.arange(len(columns)+1),np.arange(len(rows)+1),matrix.to_numpy(),cmap=cmap,norm=norm,
            edgecolors='white',linewidth=.6 if len(d)<100 else .15,rasterized=True)
        ax.set_xticks(np.arange(len(columns))+.5,columns,rotation=40,ha='right');ax.set_yticks(np.arange(len(rows))+.5,rows)
        ax.set_ylim(len(rows),0);ax.tick_params(length=0,labelsize=8.0,pad=5,colors=INK)
        for spine in ax.spines.values():spine.set_visible(False)
        cbar=fig.colorbar(image,cax=cax);cbar.outline.set_visible(False);cbar.ax.tick_params(labelsize=7.5,length=2,width=.5)
        cbar.set_label(options.get('y_label','Signed score'),fontsize=8,labelpad=6)
    fig._editorial_font=theme['font_family']
    fig=_finish(fig,data,kind,contract,options,theme)
    if kind=='paired':
        fig._omics_spec['pair_display_layout']={'subject_order':list(map(str,values.index)),
            'horizontal_offsets':offsets.tolist(),'y_values_unchanged':True,
            'definition':'Deterministic shared offset per complete pair to separate glyphs; no data-axis Y displacement'}
    return fig
