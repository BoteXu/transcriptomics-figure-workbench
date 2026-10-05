"""Frozen multi-view displays: identity, measurement and model outputs stay explicit.

These functions do not integrate, infer networks, identify compounds, fit factors
or register images. Input mappings and geometries are reviewed upstream results.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
from figure_core import checked
from project_theme import group_palette
from figure_method_extensions import _unique,_records,_types,_new,_axis,_finish,_cmap,_limits


def plot_cross_effects(data,theme,*,x_label,y_label,comparison_definition,alpha=.05,label_ids=(),title=''):
    d=checked(data,['feature_id','status','effect_x','effect_y'],['effect_x','effect_y']);_unique(d,['feature_id'])
    states=['Neither','X only','Y only','Both']
    if set(d.status)-set(states) or not comparison_definition or not 0<alpha<1:raise ValueError('Declared matched contrast and explicit four evidence states required')
    z=checked(d,['q_x','q_y'],['q_x','q_y'])
    if ((z[['q_x','q_y']]<0)|(z[['q_x','q_y']]>1)).any().any():raise ValueError('Supplied adjusted probabilities outside [0,1]')
    expected=np.where((d.q_x<=alpha)&(d.q_y<=alpha),'Both',np.where(d.q_x<=alpha,'X only',np.where(d.q_y<=alpha,'Y only','Neither')))
    if not np.array_equal(expected,d.status):raise ValueError('Evidence-state labels disagree with supplied q and threshold')
    if set(label_ids)-set(d.feature_id) or len(label_ids)>12:raise ValueError('Explicit available labels, max12')
    pal=group_palette(theme,states);fig=_new(theme,(8.2,5.6));ax=_axis(fig,[.13,.21,.60,.62])
    for name in states:
        q=d[d.status==name];ax.scatter(q.effect_x,q.effect_y,c=pal[name],s=25,ec='white',lw=.3,label=name,alpha=.82)
    ax.axvline(0,c=theme['roles']['border'],lw=.7);ax.axhline(0,c=theme['roles']['border'],lw=.7)
    for row in d[d.feature_id.isin(label_ids)].itertuples():ax.annotate(row.feature_id,(row.effect_x,row.effect_y),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set(xlabel=x_label,ylabel=y_label,title=title);fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.76,.84),loc='upper left',frameon=False)
    fig.text(.13,.07,'Matched mapped features; axis signs refer to their declared contrasts.',fontsize=8)
    return _finish(fig,data,theme,'cross_layer_effects',x_label=x_label,y_label=y_label,comparison_definition=comparison_definition,alpha=alpha,label_ids=list(label_ids),state_rule='supplied q compared to declared alpha; no testing')


def plot_aligned_views(data,theme,*,view_order,coordinate_definition,draw_links=True,title=''):
    d=checked(data,['object_id','group','view','x','y'],['x','y']);_unique(d,['object_id','view'])
    if not 2<=len(view_order)<=3 or len(view_order)!=len(set(view_order)) or set(view_order)!=set(d.view) or not coordinate_definition:raise ValueError('Two or three explicit coordinate views required')
    if (d.groupby('object_id').group.nunique()!=1).any():raise ValueError('Object identities change between views')
    sets=[set(d.loc[d.view==v,'object_id']) for v in view_order]
    if draw_links and (any(s!=sets[0] for s in sets) or len(sets[0])>100):raise ValueError('Link views only for <=100 exact matched objects; unpaired views must disable links')
    pal=group_palette(theme,list(pd.unique(d.group)));fig=_new(theme,(10.5,5.5));axes=[];w=.75/len(view_order)
    for j,view in enumerate(view_order):
        ax=_axis(fig,[.07+j*w,.22,w-.05,.58]);q=d[d.view==view]
        for g in pal:
            z=q[q.group==g];ax.scatter(z.x,z.y,c=pal[g],s=20,ec='white',lw=.3,label=g)
        ax.set(title=view,xlabel='Supplied component 1',ylabel='Supplied component 2' if j==0 else '');axes.append(ax)
    fig.canvas.draw()
    if draw_links:
        for j in range(len(axes)-1):
            a=d[d.view==view_order[j]].set_index('object_id');b=d[d.view==view_order[j+1]].set_index('object_id').loc[a.index]
            for id_ in a.index:
                pa=fig.transFigure.inverted().transform(axes[j].transData.transform([a.loc[id_,'x'],a.loc[id_,'y']]));pb=fig.transFigure.inverted().transform(axes[j+1].transData.transform([b.loc[id_,'x'],b.loc[id_,'y']]))
                # Connect only in the gutter; do not draw through either point cloud.
                left=axes[j].get_position().x1;right=axes[j+1].get_position().x0
                fig.add_artist(Line2D([left,right],[pa[1],pb[1]],transform=fig.transFigure,color=pal[a.loc[id_,'group']],alpha=.20,lw=.45))
    fig.legend(*axes[0].get_legend_handles_labels(),bbox_to_anchor=(.86,.82),loc='upper left',frameon=False);fig.text(.07,.92,title,fontsize=11,weight='bold');fig.text(.07,.075,'Gutter links identify the same objects; separate view axes are not a shared metric space.',fontsize=8)
    return _finish(fig,data,theme,'aligned_coordinate_views',view_order=view_order,coordinate_definition=coordinate_definition,draw_links=draw_links,matching='explicit object IDs; no matching or integration computed')


def plot_loading_projection(data,theme,*,x_label,y_label,projection_definition,title=''):
    d=checked(data,['feature_id','group','x','y'],['x','y']);_unique(d,['feature_id'])
    if not projection_definition or (np.hypot(d.x,d.y)>1+1e-9).any() or len(d)>30:raise ValueError('<=30 supplied feature correlations inside unit circle required')
    pal=group_palette(theme,list(pd.unique(d.group)));fig=_new(theme,(7.7,5.8));ax=_axis(fig,[.11,.20,.61,.65]);ax.add_patch(Circle((0,0),1,fc='none',ec=theme['roles']['neutral'],lw=.8))
    for r in d.itertuples():ax.plot([0,r.x],[0,r.y],c=pal[r.group],lw=.6,alpha=.4);ax.scatter([r.x],[r.y],c=pal[r.group],s=25,ec='white',lw=.35);ax.annotate(r.feature_id,(r.x,r.y),xytext=(3,3),textcoords='offset points',fontsize=7)
    ax.axhline(0,c='#CFD6DD',lw=.6);ax.axvline(0,c='#CFD6DD',lw=.6);ax.set(xlim=(-1.15,1.15),ylim=(-1.15,1.15),xlabel=x_label,ylabel=y_label,title=title);ax.set_aspect('equal')
    fig.legend(handles=[Line2D([],[],marker='o',ls='none',c=pal[g],label=g) for g in pal],bbox_to_anchor=(.77,.83),loc='upper left',frameon=False);fig.text(.11,.07,'Supplied feature-component correlations; radius is not a p-value or causal strength.',fontsize=8)
    return _finish(fig,data,theme,'feature_correlation_projection',x_label=x_label,y_label=y_label,projection_definition=projection_definition)


def plot_mass_spectrum(data,theme,*,spectrum_order,mass_definition,intensity_definition,normalization_definition,mirror=False,label_peak_ids=(),title=''):
    d=checked(data,['peak_id','spectrum','mz','intensity'],['mz','intensity']);_unique(d,['spectrum','peak_id'])
    if len(spectrum_order)!=len(set(spectrum_order)) or set(spectrum_order)!=set(d.spectrum) or not 1<=len(spectrum_order)<=4 or (mirror and len(spectrum_order)!=2) or ((d.mz<=0)|(d.intensity<0)).any() or not all([mass_definition,intensity_definition,normalization_definition]):raise ValueError('Explicit spectra, positive m/z, nonnegative intensities and normalization required')
    if set(label_peak_ids)-set(d.peak_id) or len(label_peak_ids)>12:raise ValueError('Explicit labels, max12')
    pal=group_palette(theme,spectrum_order);fig=_new(theme,(9,5.4));axes=[]
    for j,name in enumerate(spectrum_order):
        rect=[.11,.22,.61,.61] if mirror else [.11,.22+(len(spectrum_order)-j-1)*.61/len(spectrum_order),.61,.54/len(spectrum_order)]
        ax=axes[0] if mirror and j else _axis(fig,rect);axes.append(ax)
        q=d[d.spectrum==name];sign=-1 if mirror and j else 1;ax.vlines(q.mz,0,sign*q.intensity,colors=pal[name],lw=1)
        for r in q[q.peak_id.isin(label_peak_ids)].itertuples():ax.annotate(r.peak_id,(r.mz,sign*r.intensity),xytext=(0,5*sign),textcoords='offset points',ha='center',va='bottom' if sign>0 else 'top',fontsize=8)
        ax.axhline(0,c=theme['roles']['border'],lw=.6);ax.set(ylabel=intensity_definition)
        if not mirror:ax.text(.01,.86,name,transform=ax.transAxes,fontsize=9)
    axes[-1].set_xlabel(mass_definition);axes[0].set_title(title)
    fig.legend(handles=[Line2D([],[],c=pal[g],label=g) for g in pal],bbox_to_anchor=(.77,.83),loc='upper left',frameon=False);fig.text(.11,.065,'No peak matching, compound identification, rescaling or deconvolution performed.',fontsize=8)
    return _finish(fig,data,theme,'mass_spectrum_mirror' if mirror else 'mass_spectrum_sticks',spectrum_order=spectrum_order,mass_definition=mass_definition,intensity_definition=intensity_definition,normalization_definition=normalization_definition,mirror=mirror,label_peak_ids=list(label_peak_ids))


def plot_genomic_links(data,theme,*,track_order,region,assembly,chromosome,coordinate_definition,value_definition,link_definition,title=''):
    _types(data,['signal','link']);s=_records(data,'signal',['track','start','end','value'],['start','end','value']);l=_records(data,'link',['link_id','start','end','score'],['start','end','score']);_unique(s,['track','start']);_unique(l,['link_id']);lo,hi=region
    if set(track_order)!=set(s.track) or len(track_order)!=len(set(track_order)) or not 1<=len(track_order)<=5 or not all([assembly,chromosome,coordinate_definition,value_definition,link_definition]) or hi<=lo:raise ValueError('Explicit region, track identities and evidence definition required')
    if ((s.start<lo)|(s.end>hi)|(s.end<=s.start)|(s.value<0)).any() or ((l.start<lo)|(l.end>hi)|(l.end<=l.start)|(l.score<0)|(l.score>1)).any():raise ValueError('Invalid frozen spans or bounded link score')
    for _,q in s.groupby('track',sort=False):
        q=q.sort_values('start')
        if (q.start.iloc[1:].to_numpy()<q.end.iloc[:-1].to_numpy()).any():raise ValueError('Signal bins overlap')
    pal=group_palette(theme,track_order);fig=_new(theme,(9,6.4));arc=_axis(fig,[.14,.66,.60,.19]);arc.set(xlim=region,ylim=(0,1),yticks=[],xticks=[],title=title);arc.spines[['left','bottom']].set_visible(False)
    for r in l.itertuples():
        # Bezier height is purely layout; score affects alpha only with stated key.
        from matplotlib.path import Path
        from matplotlib.patches import PathPatch
        height=.20+.65*(r.end-r.start)/(hi-lo);mid=(r.start+r.end)/2
        arc.add_patch(PathPatch(Path([(r.start,0),(mid,2*height),(r.end,0)],[Path.MOVETO,Path.CURVE3,Path.CURVE3]),fc='none',ec=theme['roles']['primary'],alpha=.25+.65*r.score,lw=1.2))
    vmax=max(float(s.value.max()),1e-12);n=len(track_order)
    for j,track in enumerate(track_order):
        ax=_axis(fig,[.14,.21+(n-j-1)*.38/n,.60,.31/n]);q=s[s.track==track];ax.bar(q.start,q.value,width=q.end-q.start,align='edge',fc=pal[track],ec='none');ax.set(xlim=region,ylim=(0,vmax),ylabel=track)
        if j<n-1:ax.set_xticks([])
        else:ax.set_xlabel(chromosome+' / '+coordinate_definition)
    fig.text(.78,.75,'Link alpha\n0.25 + 0.65 score\nArc height: layout\nNo direction inferred',fontsize=8);fig.text(.14,.075,assembly+'; '+value_definition,fontsize=8)
    return _finish(fig,data,theme,'genomic_links_and_signal',track_order=track_order,region=list(region),assembly=assembly,chromosome=chromosome,coordinate_definition=coordinate_definition,value_definition=value_definition,link_definition=link_definition,arrowheads='none; supplied association links are not regulatory proof')


def plot_pathway_overlay(data,theme,*,node_limits,node_value_definition,edge_definition,title=''):
    _types(data,['node','edge']);n=_records(data,'node',['node_id','label','x','y','value'],['x','y','value']);e=_records(data,'edge',['source','target','direction'],[]);_unique(n,['node_id']);_unique(e,['source','target'])
    if len(n)>25 or not node_value_definition or not edge_definition or set(e.direction)-set(['known','association']):raise ValueError('Explicit small pathway, node quantity and edge evidence required')
    if (set(e.source)|set(e.target))-set(n.node_id):raise ValueError('Unknown pathway endpoint')
    lookup=n.set_index('node_id');norm=_limits(n.value,node_limits,signed=True);cm=_cmap(theme,True);fig=_new(theme,(9,6));ax=fig.add_axes([.07,.18,.64,.67]);ax.axis('off')
    xrange=max(n.x.max()-n.x.min(),1);yrange=max(n.y.max()-n.y.min(),1);w=xrange*.17;h=yrange*.13
    for r in e.itertuples():
        a=lookup.loc[r.source];b=lookup.loc[r.target];ax.add_patch(FancyArrowPatch((a.x,a.y),(b.x,b.y),arrowstyle='->' if r.direction=='known' else '-',mutation_scale=9,color=theme['roles']['border'],lw=.8,shrinkA=26,shrinkB=26,zorder=0))
    for r in n.itertuples():ax.add_patch(Rectangle((r.x-w/2,r.y-h/2),w,h,fc=cm(norm(r.value)),ec='white',lw=.8));ax.text(r.x,r.y,r.label,ha='center',va='center',fontsize=8)
    ax.set(xlim=(n.x.min()-w,n.x.max()+w),ylim=(n.y.min()-h,n.y.max()+h));cb=fig.add_axes([.79,.39,.024,.36]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=cb,label=node_value_definition)
    fig.text(.07,.92,title,fontsize=11,weight='bold');fig.text(.07,.07,'Known-map arrows encode supplied topology; node abundance does not encode flux.',fontsize=8)
    return _finish(fig,data,theme,'pathway_quantity_overlay',node_limits=node_limits,node_value_definition=node_value_definition,edge_definition=edge_definition,positions='supplied reviewed map; no layout optimization',edge_width='constant; no flux invented')


def plot_diagnostic_panel(data,theme,*,mode,model_definition,reference_definition,cook_area_scale=180,title=''):
    d=checked(data,['unit_id','group','fitted','residual','standard_residual','leverage','cook','reference_quantile','ordered_residual'],['fitted','residual','standard_residual','leverage','cook','reference_quantile','ordered_residual']);_unique(d,['unit_id'])
    if mode not in ['residual','qq','scale_location','influence'] or not model_definition or not reference_definition or ((d.leverage<0)|(d.leverage>1)|(d.cook<0)).any() or not np.isfinite(cook_area_scale) or cook_area_scale<=0:raise ValueError('Explicit diagnostics of one supplied model, valid leverage/Cook and area scale required')
    if (np.diff(d.reference_quantile)<=0).any() or (np.diff(d.ordered_residual)<0).any() or not np.allclose(np.sort(d.standard_residual),d.ordered_residual):raise ValueError('Provided ordered residuals must match the same observations')
    fig=_new(theme,(7.8,5.2));ax=_axis(fig,[.12,.22,.60,.61]);pal=group_palette(theme,list(pd.unique(d.group)))
    if mode=='qq':
        ax.scatter(d.reference_quantile,d.ordered_residual,c=theme['roles']['primary'],s=23,ec='white',lw=.35);lo=min(d.reference_quantile.min(),d.ordered_residual.min());hi=max(d.reference_quantile.max(),d.ordered_residual.max());ax.plot([lo,hi],[lo,hi],c=theme['roles']['border'],ls='--',lw=.8);ax.set(xlabel='Supplied reference quantile',ylabel='Supplied ordered standardized residual')
    else:
        x=d.leverage if mode=='influence' else d.fitted;y=np.sqrt(abs(d.standard_residual)) if mode=='scale_location' else d.standard_residual if mode=='influence' else d.residual
        for g in pal:
            ix=d.group==g;areas=15+cook_area_scale*d.loc[ix,'cook'] if mode=='influence' else 25;ax.scatter(x[ix],y[ix],c=pal[g],s=areas,ec='white',lw=.35,label=g,alpha=.8)
        if mode!='scale_location':ax.axhline(0,c=theme['roles']['border'],lw=.7)
        ax.set(xlabel='Supplied leverage' if mode=='influence' else 'Supplied fitted response',ylabel='Supplied standardized residual' if mode=='influence' else 'sqrt(abs(supplied standardized residual))' if mode=='scale_location' else 'Supplied residual');fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.77,.83),loc='upper left',frameon=False)
        if mode=='influence':fig.text(.77,.50,'Area (pt2)\n15 + '+str(cook_area_scale)+' Cook\nGiven Cook distance\nNo exclusion rule',fontsize=8)
    ax.set_title(title);fig.text(.12,.07,'Frozen diagnostics; no fitting, LOWESS, normality test or automatic case exclusion.',fontsize=8)
    return _finish(fig,data,theme,'model_diagnostic_'+mode,mode=mode,model_definition=model_definition,reference_definition=reference_definition,cook_area_scale=cook_area_scale,model_fit='none; one frozen diagnostic table reused by all modes')
