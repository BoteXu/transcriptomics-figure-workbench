"""At-use layout controls. Imports plotting dependencies only during rendering."""
import math


def canvas_budget(width,height):
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<v<=100 for v in [width,height]) or width*height>600:raise ValueError('Canvas resource HOLD: paginate complete panels or use a bounded server render')
    return width,height


def grid_shape(count, columns='auto', rows=None, *, preferred_width=4.2, canvas_width=None):
    if type(count) is not int or not 1<=count<=500:raise ValueError('Select 1 to 500 complete panels')
    if columns=='auto':
        if rows is not None:
            if type(rows) is not int or rows<1:raise ValueError('Positive integer rows required')
            columns=math.ceil(count/rows)
        else:columns=max(1,int(canvas_width/preferred_width)) if canvas_width else max(1,round(math.sqrt(count*1.35)))
        columns=min(columns,count)
    if type(columns) is not int or not 1<=columns<=64:raise ValueError('Positive integer columns or auto required')
    required=math.ceil(count/columns)
    if rows is None:rows=required
    if type(rows) is not int or rows<required:raise ValueError('Requested rows cannot contain all panels; expand or paginate')
    return rows,columns


def validate_layout(request):
    if request is None:return {}
    if not isinstance(request,dict) or set(request)-{'width_inches','height_inches','columns','rows','panel_width_inches','panel_height_inches','wrap_labels','axis_groups','size_policy'}:raise ValueError('Unknown native layout field')
    if request.get('size_policy','grow') not in {'grow','block'}:raise ValueError('Use grow or block size policy')
    for k in ['width_inches','height_inches','panel_width_inches','panel_height_inches']:
        v=request.get(k)
        if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or not .5<=v<=100):raise ValueError('Finite positive physical layout size required')
    for k in ['columns','rows','wrap_labels']:
        v=request.get(k)
        if v is not None and not (k=='columns' and v=='auto') and (type(v) is not int or not 1<=v<=100):raise ValueError('Invalid layout count')
    if 'axis_groups' in request and not isinstance(request['axis_groups'],list):raise ValueError('Declare complete axis groups')
    return dict(request)


def apply_native_layout(fig,request):
    """Resize or reflow whole declared axes groups, preserving quantitative artists."""
    request=validate_layout(request)
    if not request:return fig
    import numpy as np
    from matplotlib.transforms import Bbox
    from figure_design import geometry_signature,audit_layout
    from figure_layout import optimize_guide_layout
    import textwrap
    fig.canvas.draw();before=geometry_signature(fig)
    if request.get('wrap_labels'):
        for ax in fig.axes:
            xlim,ylim=ax.get_xlim(),ax.get_ylim()
            ax.set_xticks(ax.get_xticks(),['\n'.join(textwrap.wrap(t.get_text(),request['wrap_labels'],break_long_words=False)) for t in ax.get_xticklabels()])
            ax.set_yticks(ax.get_yticks(),['\n'.join(textwrap.wrap(t.get_text(),request['wrap_labels'],break_long_words=False)) for t in ax.get_yticklabels()])
            ax.set_xlim(xlim);ax.set_ylim(ylim)
    groups=request.get('axis_groups')
    if groups:
        flat=[i for g in groups for i in g]
        if any(type(i) is not int for i in flat) or sorted(flat)!=list(range(len(fig.axes))):raise ValueError('Axis groups must cover every axis exactly once, including colour bars/insets')
        if any(not g for g in groups):raise ValueError('Empty axis group')
        # Figure-level scientific annotations require explicit source normalization.
        # A native group reflow cannot safely guess their ownership.
        if any(t.get_visible() and t.get_text().strip() for t in fig.texts):raise ValueError('Use complete SVG panels when figure-level annotations lack group ownership')
        rows,cols=grid_shape(len(groups),request.get('columns','auto'),request.get('rows'))
        pw=request.get('panel_width_inches',4.5);ph=request.get('panel_height_inches',3.5)
        width=request.get('width_inches',cols*pw);height=request.get('height_inches',rows*ph)
        fig.set_layout_engine(None);boxes=[Bbox.union([fig.axes[i].get_position() for i in g]) for g in groups]
        fig.set_size_inches(*canvas_budget(width,height))
        for k,(group,box) in enumerate(zip(groups,boxes)):
            row,col=divmod(k,cols);rect=[(col+.12)/cols,(rows-row-1+.14)/rows,.76/cols,.72/rows]
            for i in group:
                ax=fig.axes[i];b=ax.get_position();ax.set_axes_locator(None)
                ax.set_position([rect[0]+(b.x0-box.x0)/box.width*rect[2],rect[1]+(b.y0-box.y0)/box.height*rect[3],b.width/box.width*rect[2],b.height/box.height*rect[3]])
    else:
        if 'columns' in request or 'rows' in request:raise ValueError('This renderer needs native facet controls or complete axis_groups; no ignored row/column request')
        width=request.get('width_inches',fig.get_figwidth());height=request.get('height_inches',fig.get_figheight())
        fig.set_size_inches(*canvas_budget(width,height))
    fig=optimize_guide_layout(fig)
    if request.get('size_policy')=='block' and any(request.get(k) is not None and abs(v-request[k])>.02 for k,v in zip(['width_inches','height_inches'],fig.get_size_inches())):raise ValueError('Requested exact canvas cannot contain readable guides; expand size or reflow')
    if before!=geometry_signature(fig):raise ValueError('Responsive layout changed quantitative geometry')
    fig._omics_spec['responsive_layout']={'request':request,'actual_size_inches':list(fig.get_size_inches()),'quantitative_geometry_sha256':before,'visual_review':'REQUIRED_AFTER_EACH_LAYOUT','automated_layout':audit_layout(fig)}
    return fig


def gsea_facets(curve,hit,metric,summary,names,theme,options):
    """Complete per-pathway enrichment facets with data-driven rows and columns."""
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    from project_theme import group_palette
    import textwrap
    rows,cols=grid_shape(len(names),options.get('ncols','auto'),options.get('nrows'))
    pw=options.get('panel_width',4.2);ph=options.get('panel_height',3.6)
    if min(pw,ph)<2 or max(pw,ph)>20:raise ValueError('Choose readable bounded panel dimensions')
    palette=group_palette(theme,names)
    fig=plt.figure(figsize=canvas_budget(pw*cols,ph*rows+.55),facecolor='white',layout='constrained')
    outer=fig.add_gridspec(rows,cols,hspace=.16,wspace=.12)
    for k,name in enumerate(names):
        grid=outer[k//cols,k%cols].subgridspec(3,1,height_ratios=[3.2,.45,1],hspace=.06)
        ax=fig.add_subplot(grid[0]);rug=fig.add_subplot(grid[1],sharex=ax);bottom=fig.add_subplot(grid[2],sharex=ax)
        q=curve[curve.pathway==name];h=hit[hit.pathway==name];s=summary.loc[name];color=palette[name]
        ax.plot(q['rank'],q.value,color=color,lw=1.5);ax.fill_between(q['rank'],0,q.value,color=color,alpha=.07)
        ax.axhline(0,color='#AAB5BE',lw=.6);ax.set_ylabel('Running ES',fontsize=8)
        ax.set_title('\n'.join(textwrap.wrap(str(name),32,break_long_words=False))+'\n'+f'NES {s.NES:+.2f}   FDR {s.padj:.2g}   n={int(s.set_size)}',loc='left',fontsize=8.5,pad=8)
        ax.tick_params(axis='x',labelbottom=False);ax.yaxis.set_major_locator(MaxNLocator(4))
        rug.vlines(h['rank'],0,1,color=color,lw=.6,alpha=.6)
        if options.get('show_leading_edge',True):rug.vlines(h.loc[h.leading_edge==1,'rank'],0,1,color=color,lw=1.5)
        rug.set_ylim(0,1);rug.axis('off')
        bottom.plot(metric['rank'],metric.value,color='#718392',lw=.6)
        bottom.fill_between(metric['rank'],0,metric.value,where=metric.value>=0,color=theme['roles']['positive'],alpha=.35)
        bottom.fill_between(metric['rank'],0,metric.value,where=metric.value<0,color=theme['roles']['negative'],alpha=.35)
        bottom.set(xlabel='Rank in complete ordered list',ylabel=options['metric_label'],xlim=(1,options['ranked_universe']))
        bottom.xaxis.set_major_locator(MaxNLocator(4,integer=True));bottom.yaxis.set_major_locator(MaxNLocator(2))
        for a in [ax,bottom]:
            a.spines[['top','right']].set_visible(False);a.tick_params(labelsize=7);a.grid(axis='y',color='#EDF0F2',lw=.5)
    caption=options['contrast']+' · '+options['gene_set_version']
    fig.suptitle(options.get('title','Gene set enrichment')+'\n'+textwrap.fill(caption,max(28,int(cols*pw*7)),break_long_words=False)+'\nBold hits = supplied leading edge',fontsize=10)
    fig._editorial_font=theme['font_family'];fig._responsive_facets={'rows':rows,'columns':cols,'panels':len(names),'complete_rank_tracks':True}
    return fig
