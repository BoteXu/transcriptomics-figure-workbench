"""Community-inspired, independently implemented displays of frozen channels."""
import copy,textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors,ticker
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from figure_core import checked
from figure_editorial import _axis,_finish,_order,validate_contract
from figure_gsea import _gsea_input
from figure_package_styles import _new,_foot,_flat_axis,_cmap
from project_theme import group_palette

INK='#243449';MUTED='#738091';GRID='#E7EBEF';TEAL='#218C8D';CORAL='#D8795B'

def _gsea(d,t,o):
    c,h,m,s,names=_gsea_input(d,o['curve_order'],o['ranked_universe'])
    if o['line_encoding'] not in ['pathway','rank_metric'] or o['line_encoding']=='rank_metric' and len(names)!=1:raise ValueError('Gradient metric lines require one selected pathway')
    for key in ['metric_label','contrast','gene_set_version']:
        if not isinstance(o[key],str) or not o[key].strip():raise ValueError('State the contrast, metric and gene-set version')
    if len(names)>1:
        from figure_workbench.responsive import gsea_facets
        return gsea_facets(c,h,m,s,names,t,o)
    v=m.value.to_numpy();limit=max(abs(v.min()),abs(v.max()))
    if not limit>0:raise ValueError('Nonzero supplied ranked metric required')
    norm=colors.TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit)
    pal=group_palette(t,names);n=len(names);fig=_new(t,o['title'],o['contrast']+' / exact supplied enrichment tracks',size=(6.8,4.5+.75*(n-1)))
    left=.13;width=.65;total=.48;gap=.035
    for i,name in enumerate(names):
        bottom=.30+(n-i-1)*total/n;ax=_axis(fig,[left,bottom,width,total/n-gap]);q=c[c.pathway==name];hits=h[h.pathway==name]
        ax.fill_between(q['rank'],0,q.value,color=pal[name],alpha=.07)
        if o['line_encoding']=='rank_metric':
            points=np.column_stack([q['rank'],q.value]);segments=np.stack([points[:-1],points[1:]],axis=1)
            # A fine neutral underlay preserves the curve at the ramp's pale zero.
            # Both layers use exactly the supplied vertices; no smoothing.
            ax.add_collection(LineCollection(segments,colors='#89949E',linewidths=2.25))
            lc=LineCollection(segments,cmap=_cmap(t),norm=norm,linewidths=1.8);lc.set_array(v[:-1]);ax.add_collection(lc);ax.autoscale_view()
            hit_values=q.set_index('rank').loc[hits['rank'],'value'].to_numpy();ax.vlines(hits['rank'],0,hit_values,color='#AAB5BE',lw=.5,alpha=.34)
        else:ax.plot(q['rank'],q.value,color=pal[name],lw=1.65)
        ax.axhline(0,color='#ABB5BE',lw=.6);ax.set_xlim(1,o['ranked_universe']);ax.set_ylabel('ES',fontsize=8);ax.yaxis.set_major_locator(ticker.MaxNLocator(3));_flat_axis(ax,None)
        ax.tick_params(axis='x',labelbottom=False)
        peak=q.loc[q.value.abs().idxmax()];leading=hits[hits.leading_edge==1]
        ax.scatter([peak['rank']],[peak.value],s=18,color=pal[name],ec='white',lw=.5,zorder=5)
        ax.axvline(peak['rank'],color=pal[name],lw=.6,ls=(0,(3,3)),alpha=.45)
        ax.text(1.04,.90,'\n'.join(textwrap.wrap(name,17))+'\n'+f'NES {s.loc[name,"NES"]:+.2f}\nFDR {s.loc[name,"padj"]:.2g}\n{int(s.loc[name,"set_size"])} hits / {o["ranked_universe"]} genes\nLeading edge: {len(leading)}',transform=ax.transAxes,va='top',fontsize=7.5,color=pal[name],linespacing=1.45)
        rug=fig.add_axes([left,bottom-.023,width,.016]);rug.set(xlim=(1,o['ranked_universe']),ylim=(0,1));rug.axis('off')
        rug.vlines(hits['rank'],0,1,color=pal[name],lw=.55,alpha=.45);rug.vlines(hits.loc[hits.leading_edge==1,'rank'],0,1,color=pal[name],lw=1.3)
    strip=fig.add_axes([left,.18,width,.035])
    strip.imshow(v[np.newaxis,:],aspect='auto',cmap=_cmap(t),norm=colors.TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),extent=(.5,o['ranked_universe']+.5,0,1),interpolation='nearest');strip.set(yticks=[],xlabel='Rank in the complete ordered list');strip.xaxis.set_major_locator(ticker.MaxNLocator(5,integer=True));strip.tick_params(labelsize=8)
    for sp in strip.spines.values():sp.set_visible(False)
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=colors.TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),cmap=_cmap(t)),cax=fig.add_axes([.84,.16,.015,.11]));cb.ax.tick_params(labelsize=7.4);cb.set_ticks([-limit,0,limit]);cb.set_label(o['metric_label'],fontsize=7.5)
    _foot(fig,'Hit rugs retain exact ranks; bold hits are supplied leading edge. '+o['gene_set_version']+'. No ES, NES, FDR or membership recomputation.')
    return fig

def _ribbon(d,t,o):
    d=checked(d,['series','x','estimate','lower','upper'],['x','estimate','lower','upper'])
    names=_order(d.series,o['series_order'])
    if len(names)>4 or d.duplicated(['series','x']).any():raise ValueError('One to four unique ordered curves required')
    if ((d.lower>d.estimate)|(d.estimate>d.upper)).any():raise ValueError('Supplied ribbon bounds must contain the estimate')
    inner='inner_lower' in d or 'inner_upper' in d
    if inner:
        d=checked(d,['inner_lower','inner_upper'],['inner_lower','inner_upper'])
        if ((d.lower>d.inner_lower)|(d.inner_lower>d.estimate)|(d.estimate>d.inner_upper)|(d.inner_upper>d.upper)).any():raise ValueError('Supplied ribbon bounds must be nested')
    for name in names:
        if len(d[d.series==name])<3 or (np.diff(d.loc[d.series==name,'x'])<=0).any():raise ValueError('Curve coordinates must be increasing; no sorting or interpolation')
    if not isinstance(o['interval_definition'],str) or not o['interval_definition'].strip():raise ValueError('Define interval meanings')
    pal=group_palette(t,names);fig=_new(t,o['title'],o['subtitle'],size=(6.8,4.2));ax=_axis(fig,[.13,.20,.62,.54]);_flat_axis(ax,'y')
    for name in names:
        q=d[d.series==name];ax.fill_between(q.x,q.lower,q.upper,color=pal[name],alpha=.14,lw=0)
        if inner:ax.fill_between(q.x,q.inner_lower,q.inner_upper,color=pal[name],alpha=.24,lw=0)
        ax.plot(q.x,q.estimate,color=pal[name],lw=1.7,label=name)
    ax.set(xlabel=o['x_label'],ylabel=o['y_label']);ax.legend(loc='upper left',bbox_to_anchor=(1.03,1),frameon=False,fontsize=8)
    _foot(fig,o['interval_definition']+'. Supplied curves and '+('nested bounds' if inner else 'interval bounds')+'; no model fit, smoothing or interval estimation.')
    return fig

def _shift(d,t,o):
    d=checked(d,['feature','score_a','score_b','delta','lower_delta','upper_delta'],['score_a','score_b','delta','lower_delta','upper_delta'])
    names=_order(d.feature,o['feature_order'])
    if d.feature.duplicated().any() or len(names)>24 or len(names)<1:raise ValueError('One row per selected feature required')
    if not np.allclose(d.score_b-d.score_a,d.delta,rtol=1e-7,atol=1e-10) or ((d.lower_delta>d.delta)|(d.delta>d.upper_delta)).any():raise ValueError('Supplied differences and intervals disagree')
    pal=group_palette(t,[o['label_a'],o['label_b']]);a_color,b_color=pal[o['label_a']],pal[o['label_b']]
    d=d.set_index('feature').loc[names];fig=_new(t,o['title'],o['subtitle'],size=(6.8,max(4.1,2+.23*len(names))));left=_axis(fig,[.18,.21,.31,.53]);right=_axis(fig,[.64,.21,.25,.53]);y=np.arange(len(names))
    for ax in [left,right]:
        _flat_axis(ax,'x');ax.set_ylim(len(names)-.5,-.5);ax.set_yticks(y,names if ax is left else ['']*len(names));ax.tick_params(axis='y',length=0,labelsize=8);ax.spines['left'].set_visible(False)
        for k in y[::2]:ax.axhspan(k-.5,k+.5,color='#F4F7F9',zorder=0)
    left.hlines(y,d.score_a,d.score_b,color='#C0CBD4',lw=1.1);left.scatter(d.score_a,y,c=a_color,s=25,zorder=3,label=o['label_a']);left.scatter(d.score_b,y,c=b_color,s=25,zorder=3,label=o['label_b']);left.set_xlabel(o['score_label']);left.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=2,frameon=False,fontsize=7.5)
    right.axvline(0,c='#AAB5BE',lw=.7,ls=(0,(3,3)));right.hlines(y,d.lower_delta,d.upper_delta,colors='#738DA7',lw=1.3);right.scatter(d.delta,y,c='#4B70A6',s=24,zorder=3);right.set_xlabel(o['difference_label'])
    _foot(fig,o['interval_definition']+'. Connections identify the same feature, not paired biological subjects. Supplied differences and bounds retained.')
    return fig

def _association(d,t,o):
    d=checked(d,['record_type','r','p'],['r','p'])
    if not set(d.record_type)=={'correlation','mantel'} or ((d.r<-1)|(d.r>1)|(d.p<0)|(d.p>1)).any():raise ValueError('Valid declared correlation and Mantel summaries required')
    c=checked(d[d.record_type=='correlation'],['a','b']);m=checked(d[d.record_type=='mantel'],['specimen','target']);names=o['variable_order'];sets=_order(m.specimen,o['specimen_order'])
    if not isinstance(names,list) or len(names)!=len(set(names)) or set(c.a)|set(c.b)!=set(names) or set(m.target)!=set(names):raise ValueError('Exact declared variables required')
    n=len(names)
    if not 2<=n<=24 or not 1<=len(sets)<=8 or (c.a==c.b).any() or len(c)!=n*(n-1)//2 or c.apply(lambda r:tuple(sorted([r.a,r.b])),axis=1).duplicated().any():raise ValueError('Complete unique unordered correlation pairs required')
    if len(m)!=n*len(sets) or m.duplicated(['specimen','target']).any():raise ValueError('Complete unique Mantel grid required')
    fig=_new(t,o['title'],o['subtitle'],size=(6.8,6.0));norm=colors.TwoSlopeNorm(vmin=-1,vcenter=0,vmax=1);cm=_cmap(t)
    ax=fig.add_axes([.16,.44,.59,.34]);ax.set(xlim=(-.5,n-.5),ylim=(n-.5,-.5));ax.set_xticks(range(n),names,rotation=90,ha='center',fontsize=7.5);ax.set_yticks(range(n),names,fontsize=7.5);ax.tick_params(length=0)
    for row in c.itertuples():
        a,b=names.index(row.a),names.index(row.b)
        if a<b:a,b=b,a
        ax.add_patch(Rectangle((b-.5,a-.5),1,1,facecolor=cm(norm(row.r)),edgecolor='white',lw=.35))
    for sp in ax.spines.values():sp.set_visible(False)
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.84,.60,.018,.14]));cb.set_label(o['correlation_label'],fontsize=7.5);cb.ax.tick_params(labelsize=7.5)
    ax2=fig.add_axes([.16,.20,.59,.13]);lookup=m.set_index(['specimen','target']);ax2.set(xlim=(-.5,n-.5),ylim=(len(sets)-.5,-.5));ax2.set_xticks(range(n),names,rotation=90,ha='center',fontsize=7.5);ax2.set_yticks(range(len(sets)),sets,fontsize=7.5);ax2.tick_params(length=0)
    for i,s in enumerate(sets):
        for j,v in enumerate(names):
            row=lookup.loc[s,v];ax2.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=cm(norm(row.r)),edgecolor='white',lw=.35))
    for sp in ax2.spines.values():sp.set_visible(False)
    cb2=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.84,.20,.018,.13]));cb2.set_label('Mantel r',fontsize=7.5);cb2.ax.tick_params(labelsize=7.5)
    _foot(fig,'Two distinct association measures, separate guides; all supplied pairs retained. Raw p-values remain in the exact table; no testing, thresholding or causal arrows.')
    return fig

def plot_refined_views(data,theme,*,view,contract,options):
    """Compact GSEA, supplied nested ribbon, score shifts and association matrices."""
    validate_contract(contract)
    routes={'gsea_strip':(_gsea,'curve_order ranked_universe metric_label contrast gene_set_version line_encoding title'),
        'ribbon':(_ribbon,'series_order interval_definition x_label y_label title subtitle'),
        'score_shift':(_shift,'feature_order label_a label_b score_label difference_label interval_definition title subtitle'),
        'association':(_association,'variable_order specimen_order correlation_label title subtitle')}
    extra={'ncols','nrows','panel_width','panel_height'} if view=='gsea_strip' else set()
    if view not in routes or not isinstance(options,dict) or set(options)-extra!=set(routes[view][1].split()):raise ValueError('Use the documented refined-view options')
    previous=set(plt.get_fignums())
    try:
        fig=routes[view][0](data,theme,copy.deepcopy(options));return _finish(fig,data,'refined_'+view,contract,options,theme)
    except Exception:
        for n in set(plt.get_fignums())-previous:plt.close(n)
        raise
