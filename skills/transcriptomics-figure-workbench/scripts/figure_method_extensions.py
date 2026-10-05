"""Original frozen-result layouts, selected by data shape rather than subject.

No enrichment, model fitting, survival estimation or velocity inference occurs here.
Table schemas, orders, scales and missing states are explicit and exportable.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm, to_rgb
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
from matplotlib.patches import Rectangle, Circle, Wedge
from figure_core import checked, stamp, effect_reference
from project_theme import validate_theme, group_palette, apply_project_style


def _unique(d,keys):
    if d.duplicated(keys).any(): raise ValueError('Duplicate key: '+', '.join(keys))

def _records(data,kind,columns,numeric=(),optional=False):
    d=data.loc[data.record_type==kind]
    if optional and d.empty:return d.copy()
    return checked(d,columns,numeric)

def _types(data,kinds):
    checked(data,['record_type'])
    if set(data.record_type)-set(kinds): raise ValueError('Unknown record type')

def _limits(values,limits,*,signed=False):
    if len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1]:raise ValueError('Explicit finite ordered limits required')
    if len(values) and (min(values)<limits[0] or max(values)>limits[1]):raise ValueError('Limits exclude supplied values')
    if signed and not limits[0]<0<limits[1]:raise ValueError('Signed limits must straddle zero')
    return TwoSlopeNorm(0,*limits) if signed else Normalize(*limits)

def _cmap(theme,signed=False):
    return LinearSegmentedColormap.from_list('project_result',theme['continuous']['diverging' if signed else 'sequential'])

def _new(theme,size=(8,5)):
    validate_theme(theme)
    with plt.rc_context({'font.family':theme['font_family']}):return plt.figure(figsize=size)

def _axis(fig,rect):
    a=fig.add_axes(rect);a.spines[['top','right']].set_visible(False);a.tick_params(length=3,width=.6);return a

def _finish(fig,data,theme,kind,**spec):
    stamp(fig,data,kind,scientific_analysis='none; supplied results only',demo_label_style='compact',**spec)
    return apply_project_style(fig,theme)

def plot_enrichment_grid(data,theme,*,significance_limits,ratio_max,block_slots,column_order,term_order,title=''):
    """Full term x group/cell-class grid; tested absence and untested are distinct."""
    d=checked(data,['term_id','term_label','block','column_id','group','cell_class','status'])
    _unique(d,['term_id','column_id'])
    if len(term_order)!=len(set(term_order)) or set(term_order)!=set(d.term_id) or len(column_order)!=len(set(column_order)) or set(column_order)!=set(d.column_id):raise ValueError('Explicit complete orders required')
    if len(d)!=len(term_order)*len(column_order):raise ValueError('Complete grid required, with explicit not_tested states')
    if not set(d.status)<=set(['reported','tested_absent','not_tested']):raise ValueError('Unknown tested state')
    for field in ['term_label','block']:
        if (d.groupby('term_id')[field].nunique()!=1).any():raise ValueError('Inconsistent term annotation')
    for field in ['group','cell_class']:
        if (d.groupby('column_id')[field].nunique()!=1).any():raise ValueError('Inconsistent column annotation')
    z=checked(d[d.status=='reported'],['padj','gene_ratio'],['padj','gene_ratio'])
    if ((z.padj<=0)|(z.padj>1)|(z.gene_ratio<=0)|(z.gene_ratio>ratio_max)).any() or not 0<ratio_max<=1:raise ValueError('Positive adjusted p and gene ratios within declared max required')
    other=d[d.status!='reported']
    if other[['padj','gene_ratio']].notna().any().any():raise ValueError('Absent/untested cells cannot contain fabricated metrics')
    scores=-np.log10(z.padj);norm=_limits(scores,significance_limits)
    groups=list(pd.unique(d.group));pal=group_palette(theme,groups)
    if len(groups)>2:raise ValueError('Split more than two group-specific scales into panels to keep all guides separate')
    blocks=list(pd.unique(d.block));bp=group_palette(theme,list(block_slots.values()))
    if set(blocks)!=set(block_slots):raise ValueError('Explicit block slots required')
    cellclasses=list(pd.unique(d.cell_class));cp=group_palette(theme,cellclasses)
    height=max(5.2,len(term_order)*.27+1.7);fig=_new(theme,(11.6,height))
    ax=_axis(fig,[.055,.15,.27,.68]);labelax=fig.add_axes([.345,.15,.385,.68]);strip=fig.add_axes([.055,.837,.27,.068]);guide=fig.add_axes([.78,.12,.19,.80]);guide.axis('off')
    labels=d.drop_duplicates('term_id').set_index('term_id').loc[term_order];cols=d.drop_duplicates('column_id').set_index('column_id').loc[column_order]
    ax.set(xlim=(-.5,len(column_order)-.5),ylim=(len(term_order)-.5,-.5));ax.set_xticks(range(len(column_order)),cols.cell_class,rotation=0);ax.set_yticks([])
    ax.set_xticks(np.arange(len(column_order)+1)-.5,minor=True);ax.set_yticks(np.arange(len(term_order)+1)-.5,minor=True);ax.grid(which='minor',color='#E5E9ED',ls='--',lw=.55);ax.tick_params(which='minor',length=0)
    shapes=['*','P','D','o'];xmap={x:i for i,x in enumerate(column_order)};ymap={x:i for i,x in enumerate(term_order)};scales={}
    from matplotlib.markers import MarkerStyle
    def filled_area(shape):
        marker=MarkerStyle(shape);path=marker.get_path().transformed(marker.get_transform())
        polygons=path.to_polygons();return sum(abs(np.dot(p[:-1,0],p[1:,1])-np.dot(p[:-1,1],p[1:,0]))/2 for p in polygons)
    shape_areas={s:filled_area(s) for s in shapes}
    for j,g in enumerate(groups):
        scales[g]=LinearSegmentedColormap.from_list('group_'+str(j),['#F5F8F8',pal[g]])
        q=z[z.group==g];ax.scatter(q.column_id.map(xmap),q.term_id.map(ymap),s=95*q.gene_ratio/ratio_max/shape_areas[shapes[j]],c=-np.log10(q.padj),norm=norm,cmap=scales[g],marker=shapes[j],edgecolors='none',zorder=3)
    for r in other.itertuples():
        if r.status=='tested_absent':ax.scatter(xmap[r.column_id],ymap[r.term_id],s=10,c='#B6BFC6',marker='.',zorder=3)
        else:ax.scatter(xmap[r.column_id],ymap[r.term_id],s=18,c='#9CA7B0',marker='x',lw=.6,zorder=3)
    labelax.set(xlim=(0,1),ylim=(len(term_order)-.5,-.5));labelax.axis('off')
    for i,r in enumerate(labels.itertuples()):
        labelax.add_patch(Rectangle((0,i-.45),.014,.9,fc=bp[block_slots[r.block]],lw=0));labelax.text(.04,i,f'{r.Index}: {r.term_label}',va='center',fontsize=8.5)
    strip.set(xlim=(-.5,len(column_order)-.5),ylim=(0,2));strip.axis('off')
    for i,r in enumerate(cols.itertuples()):
        strip.add_patch(Rectangle((i-.5,0),1,1,fc=cp[r.cell_class],ec='white',lw=.6));strip.text(i,.5,r.cell_class,ha='center',va='center',fontsize=8)
    for g in groups:
        positions=[i for i,r in enumerate(cols.itertuples()) if r.group==g]
        if positions!=list(range(min(positions),max(positions)+1)):raise ValueError('Group strip requires contiguous column blocks')
        strip.add_patch(Rectangle((min(positions)-.5,1),len(positions),1,fc=pal[g],ec='white',lw=.6));strip.text(np.mean(positions),1.5,g,ha='center',va='center',fontsize=8)
    shape_guide=guide.legend(handles=[Line2D([],[],marker=shapes[j],color=pal[g],ls='',markersize=10,label=g) for j,g in enumerate(groups)],title='Group shape',loc='upper left',frameon=False);guide.add_artist(shape_guide)
    for j,g in enumerate(groups):
        cax=fig.add_axes([.80,.62-j*.155,.115,.018]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=scales[g]),cax=cax,orientation='horizontal');cax.set_title(g+'  -log10(adjusted p)',fontsize=8,loc='left')
    guide.legend(handles=[Line2D([],[],marker='o',ls='',mfc='#586672',mec='none',markersize=np.sqrt(95*r/ratio_max/shape_areas['o']),label=f'{r:g}') for r in [ratio_max*.25,ratio_max*.5,ratio_max]],title='Gene ratio (filled area)',loc='lower left',bbox_to_anchor=(0,.13),frameon=False)
    guide.text(0,.035,'dot: tested, not reported\nx: not tested',fontsize=8)
    fig.text(.055,.94,title,fontsize=11,weight='bold');fig.text(.055,.065,'All group scales use the same limits; missing tests remain explicit.',fontsize=8)
    return _finish(fig,data,theme,'multi_group_enrichment_grid',significance_limits=list(significance_limits),ratio_max=ratio_max,column_order=column_order,term_order=term_order,group_shapes=dict(zip(groups,shapes)),marker_polygon_areas=shape_areas,size_definition='Filled glyph area proportional to gene ratio, polygon area normalization across shapes',block_slots=block_slots,absence_policy='tested_absent dot; not_tested x; no imputation')

def plot_term_effect_circle(data,theme,*,term_order,effect_limits,zscore_limits,significance_max,zscore_definition,effect_label,title=''):
    """Inner p-height/z-score colour; outer individual gene-effect positions."""
    _types(data,['term','member'])
    t=_records(data,'term',['term_id','padj','zscore'],['padj','zscore']);m=_records(data,'member',['term_id','gene_id','effect'],['effect'])
    _unique(t,['term_id']);_unique(m,['term_id','gene_id'])
    if not 2<=len(t)<=16 or len(term_order)!=len(set(term_order)) or set(term_order)!=set(t.term_id) or set(m.term_id)!=set(t.term_id):raise ValueError('Provide 2-16 complete terms and explicit memberships/order')
    if ((t.padj<=0)|(t.padj>1)).any() or not zscore_definition.strip() or not effect_label.strip():raise ValueError('Valid adjusted p and metric definitions required')
    en=_limits(m.effect,effect_limits,signed=True);zn=_limits(t.zscore,zscore_limits,signed=True);score=-np.log10(t.padj)
    if not np.isfinite(significance_max) or significance_max<=0 or score.max()>significance_max:raise ValueError('Explicit significance height maximum required')
    fig=_new(theme,(7.1,6.9));ax=fig.add_axes([.07,.25,.72,.62],projection='polar');ax.set_theta_zero_location('N');ax.set_theta_direction(-1);ax.set_ylim(0,2.5);ax.set_axis_off()
    width=2*np.pi/len(t)*.85;cmap=_cmap(theme,True);lookup=t.set_index('term_id');starts=np.arange(len(t))*2*np.pi/len(t)
    for a,term in zip(starts,term_order):
        row=lookup.loc[term];h=-np.log10(row.padj)/significance_max*.56
        ax.bar(a,h,width=width,bottom=.40,color=cmap(zn(row.zscore)),ec='#75828D',lw=.6)
        aa=np.linspace(a-width/2,a+width/2,60)
        for value in np.linspace(effect_limits[0],effect_limits[1],3):ax.plot(aa,np.full(60,1.20+en(value)*.79),color='#CCD4DB',lw=.45,zorder=0)
        ax.fill_between(aa,1.15,2.04,color='#EDF1F4',alpha=.8,zorder=-1)
        members=m[m.term_id==term];angles=np.linspace(a-width*.35,a+width*.35,len(members))
        ax.scatter(angles,1.20+en(members.effect.to_numpy())*.79,c=members.effect,cmap=cmap,norm=en,s=19,ec='white',lw=.35,zorder=3)
        rotation=np.degrees(-a)%360
        if 90<rotation<270:rotation=(rotation+180)%360
        ax.text(a,2.23,term,ha='center',va='center',rotation=rotation,fontsize=8)
    fig.text(.80,.75,'Inner height\n-log10(adjusted p)\n0 to '+f'{significance_max:g}',fontsize=8)
    fig.text(.80,.55,'Outer radius\n'+effect_label+'\n'+f'{effect_limits[0]:g} to {effect_limits[1]:g}',fontsize=8)
    for rect,norm,label in [([.11,.12,.30,.023],zn,'Supplied term direction score'),([.53,.12,.30,.023],en,effect_label)]:
        cb=fig.add_axes(rect);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cb,orientation='horizontal');cb.set_title(label,fontsize=8,loc='left')
    fig.text(.06,.93,title,fontsize=11,weight='bold');fig.text(.06,.035,'Each outer point is a named member; angular spacing is layout only.',fontsize=8)
    return _finish(fig,data,theme,'term_effect_circle',term_order=term_order,effect_limits=list(effect_limits),zscore_limits=list(zscore_limits),significance_max=significance_max,zscore_definition=zscore_definition,effect_label=effect_label,inner_height='-log10(adjusted p)',outer_radius='linear supplied effect',angular_order='input member order; layout only')

def plot_term_key(data,theme,*,title=''):
    d=checked(data,['term_id','description']);_unique(d,['term_id'])
    if max(d.description.str.len())>130:raise ValueError('Split long descriptions into an accompanying text table')
    fig=_new(theme,(7.0,max(2.3,len(d)*.38+1.2)));ax=fig.add_axes([.025,.15,.95,.65]);ax.axis('off')
    table=ax.table(cellText=d[['term_id','description']].to_numpy(),colLabels=['ID','Description'],colWidths=[.22,.78],cellLoc='left',loc='center')
    table.auto_set_font_size(False);table.set_fontsize(9);table.scale(1,1.45)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_facecolor('#E7EDF2' if r==0 else '#F4F7F9' if r%2 else 'white')
        if r==0:cell.set_text_props(weight='bold')
    fig.text(.03,.88,title,fontsize=11,weight='bold')
    return _finish(fig,data,theme,'term_key',columns=['term_id','description'],order=list(d.term_id))

def plot_two_set_overlap(data,theme,*,set_columns,unit_label,title=''):
    d=checked(data,['object_id']+set_columns,set_columns);_unique(d,['object_id'])
    if len(set_columns)!=2 or len(set(set_columns))!=2 or not set(d[set_columns].to_numpy().ravel())<=set([0,1]):raise ValueError('Two explicit binary membership columns required')
    pal=group_palette(theme,set_columns);a,b=set_columns
    if ((d[a]+d[b])==0).any():raise ValueError('Input must contain the selected union; all-zero objects belong in a separately declared universe')
    vals=[int(((d[a]==1)&(d[b]==0)).sum()),int(((d[a]==1)&(d[b]==1)).sum()),int(((d[a]==0)&(d[b]==1)).sum())]
    fig=_new(theme,(6.9,4.6));ax=fig.add_axes([.06,.15,.88,.66]);ax.axis('off');ax.set_aspect('equal');ax.set(xlim=(-1.8,1.8),ylim=(-1.18,1.18))
    for x,g in [(-.55,a),(.55,b)]:ax.add_patch(Circle((x,0),1,fc=pal[g],ec=pal[g],alpha=.36,lw=1.3));ax.text(x,1.12,g,ha='center',fontsize=10)
    for x,v in zip([-.95,0,.95],vals):ax.text(x,0,f'{v:,}\n({v/len(d)*100:.1f}%)',ha='center',va='center',fontsize=11)
    fig.text(.06,.91,title,fontsize=11,weight='bold');fig.text(.06,.08,f'{unit_label}; percentages use union n={len(d)}. Circle areas are schematic.',fontsize=8)
    return _finish(fig,data,theme,'two_set_overlap',set_columns=set_columns,exclusive_counts=vals,denominator=len(d),area_encoding='none; schematic equal circles',unit_label=unit_label)

def plot_gene_term_chord(data,theme,*,gene_order,term_order,effect_limits,effect_label,title=''):
    from figure_network_extensions import _ribbon
    d=checked(data,['gene_id','term_id','effect'],['effect']);_unique(d,['gene_id','term_id'])
    if len(gene_order)!=len(set(gene_order)) or set(gene_order)!=set(d.gene_id) or len(term_order)!=len(set(term_order)) or set(term_order)!=set(d.term_id):raise ValueError('Explicit complete gene and term orders required')
    if not 2<=len(term_order)<=8 or not 2<=len(gene_order)<=24 or (d.groupby('gene_id').effect.nunique()!=1).any() or set(gene_order)&set(term_order):raise ValueError('Use disjoint IDs, 2-8 terms and 2-24 genes with one supplied effect per gene')
    norm=_limits(d.effect,effect_limits,signed=True);cmap=_cmap(theme,True);fig=_new(theme,(8.3,6.6));ax=fig.add_axes([.055,.19,.72,.70]);ax.set_aspect('equal');ax.axis('off');ax.set(xlim=(-1.30,1.30),ylim=(-1.3,1.3))
    gene_a=np.linspace(np.pi*.58,np.pi*1.42,len(gene_order));term_a=np.linspace(-np.pi*.40,np.pi*.40,len(term_order));angles=dict(zip(gene_order,gene_a));angles.update(dict(zip(term_order,term_a)))
    radius=.92;width=min(.055,.70/max(d.gene_id.value_counts().max(),d.term_id.value_counts().max()));offset={k:0 for k in angles}
    for g,a in zip(gene_order,gene_a):
        v=float(d.loc[d.gene_id==g,'effect'].iloc[0]);ax.add_patch(Wedge((0,0),1,np.degrees(a)-2.1,np.degrees(a)+2.1,width=.075,fc=cmap(norm(v)),ec='white',lw=.5));ax.text(1.13*np.cos(a),1.13*np.sin(a),g,ha='center',va='center',fontsize=8)
    for t,a in zip(term_order,term_a):
        ax.add_patch(Wedge((0,0),1,np.degrees(a)-3,np.degrees(a)+3,width=.075,fc=theme['roles']['primary'],ec='white',lw=.5));ax.text(1.13*np.cos(a),1.13*np.sin(a),t,ha='center',va='center',fontsize=8)
    def pt(a):return (radius*np.cos(a),radius*np.sin(a))
    degrees=d.gene_id.value_counts().to_dict()|d.term_id.value_counts().to_dict()
    for r in d.itertuples():
        a=angles[r.gene_id]+(offset[r.gene_id]-(degrees[r.gene_id]-1)/2)*width;b=angles[r.term_id]+(offset[r.term_id]-(degrees[r.term_id]-1)/2)*width
        _ribbon(ax,pt(a-width*.35),pt(a+width*.35),pt(b+width*.35),pt(b-width*.35),cmap(norm(r.effect)),.32);offset[r.gene_id]+=1;offset[r.term_id]+=1
    cb=fig.add_axes([.81,.31,.025,.33]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cb,label=effect_label)
    fig.text(.055,.93,title,fontsize=11,weight='bold');fig.text(.055,.065,'Ribbons encode membership; equal ribbon width does not encode strength.',fontsize=8)
    return _finish(fig,data,theme,'gene_term_membership_chord',gene_order=gene_order,term_order=term_order,effect_limits=list(effect_limits),effect_label=effect_label,ribbon_width='constant binary membership; no weight or causal direction')

def plot_distribution_result(data,theme,*,mode,x_label,y_label,title='',reference_distribution=None):
    """One curve/point engine for frozen ECDF steps or matched QQ coordinates."""
    d=checked(data,['group','x','y'],['x','y']);_unique(d,['group','x']);pal=group_palette(theme,list(pd.unique(d.group)))
    if mode not in ['ecdf','qq']:raise ValueError('Mode must be ecdf or qq')
    fig=_new(theme,(7.5,4.7));ax=_axis(fig,[.12,.19,.63,.65])
    for g,q in d.groupby('group',sort=False):
        if (np.diff(q.x)<0).any() or (np.diff(q.y)<0).any():raise ValueError('Frozen quantiles/CDF must be monotonically ordered')
        if mode=='ecdf':
            if ((q.y<0)|(q.y>1)).any():raise ValueError('CDF probabilities outside [0,1]')
            ax.step(q.x,q.y,where='post',color=pal[g],label=g,lw=1.8)
        else:ax.scatter(q.x,q.y,color=pal[g],label=g,s=24,ec='white',lw=.4)
    if mode=='qq':
        if not reference_distribution:raise ValueError('Declare reference distribution; no normal fit is inferred')
        lo=min(d.x.min(),d.y.min());hi=max(d.x.max(),d.y.max());ax.plot([lo,hi],[lo,hi],ls='--',color=theme['roles']['neutral'],lw=1)
    else:ax.set_ylim(-.02,1.03)
    ax.set(xlabel=x_label,ylabel=y_label,title=title);fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.77,.84),frameon=False)
    return _finish(fig,data,theme,'distribution_'+mode,mode=mode,x_label=x_label,y_label=y_label,reference_distribution=reference_distribution,step='post' if mode=='ecdf' else None,fit='none')

def plot_balance(data,theme,*,stage_order,threshold,metric_definition,title=''):
    d=checked(data,['covariate','group','smd'],['smd']);_unique(d,['covariate','group']);rows=list(pd.unique(d.covariate));pal=group_palette(theme,stage_order)
    if set(stage_order)!=set(d.group) or len(d)!=len(rows)*len(stage_order) or not 0<threshold<1 or not metric_definition:raise ValueError('Full covariate x stage grid and explicit SMD definition/threshold required')
    fig=_new(theme,(8,max(3.7,len(rows)*.32+1.3)));ax=_axis(fig,[.25,.19,.49,.64])
    for i,c in enumerate(rows):
        q=d[d.covariate==c].set_index('group').loc[stage_order];ax.plot(q.smd,[i]*len(q),color='#D0D7DC',lw=.9,zorder=1)
        for g in stage_order:ax.scatter(q.loc[g,'smd'],i,c=pal[g],s=34,zorder=3)
    for t in [-threshold,threshold]:ax.axvline(t,color=theme['roles']['border'],ls='--',lw=.8)
    ax.axvline(0,color='#CFD6DC',lw=.7);ax.set(yticks=range(len(rows)),yticklabels=rows,xlabel='Supplied standardized mean difference',title=title);ax.invert_yaxis()
    fig.legend(handles=[Line2D([],[],marker='o',color=pal[g],ls='',label=g) for g in stage_order],loc='upper left',bbox_to_anchor=(.77,.82),frameon=False)
    fig.text(.25,.06,'Diagnostic threshold = '+str(threshold)+'; not a causal validity test.',fontsize=8)
    return _finish(fig,data,theme,'covariate_balance',stage_order=stage_order,threshold=threshold,metric_definition=metric_definition)

def plot_agreement(data,theme,*,bias,loa,unit_label,difference_definition,title=''):
    d=checked(data,['object_id','group','mean','difference'],['mean','difference']);_unique(d,['object_id']);pal=group_palette(theme,list(pd.unique(d.group)))
    if not isinstance(loa,(list,tuple,np.ndarray)) or len(loa)!=2:raise ValueError('Two supplied agreement limits required')
    if not np.isfinite([bias,*loa]).all() or not loa[0]<=bias<=loa[1] or not unit_label or not difference_definition:raise ValueError('Supplied bias, ordered agreement limits and unit/direction required')
    fig=_new(theme,(8,4.8));ax=_axis(fig,[.12,.20,.59,.63])
    for g,q in d.groupby('group',sort=False):ax.scatter(q['mean'],q.difference,c=pal[g],s=27,ec='white',lw=.4,label=g,alpha=.8)
    for v,ls in [(bias,'-'),(loa[0],'--'),(loa[1],'--')]:ax.axhline(v,color=theme['roles']['border'],ls=ls,lw=1)
    ax.set(xlabel='Supplied paired mean',ylabel=difference_definition,title=title)
    fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.75,.85),frameon=False)
    fig.text(.76,.47,f'Bias {bias:g}\nAgreement limits\n[{loa[0]:g}, {loa[1]:g}]',fontsize=9);fig.text(.12,.07,unit_label+'; supplied summary, no new agreement fit.',fontsize=8)
    return _finish(fig,data,theme,'bland_altman_supplied',bias=bias,loa=list(loa),unit_label=unit_label,difference_definition=difference_definition,summary='provided, not re-estimated')

def plot_survival_result(data,theme,*,time_label,risk_convention,interval_definition,title=''):
    _types(data,['step','risk','censor'])
    s=_records(data,'step',['group','time','survival','lower','upper'],['time','survival','lower','upper']);r=_records(data,'risk',['group','time','at_risk'],['time','at_risk']);c=_records(data,'censor',['group','time','survival'],['time','survival'],True)
    _unique(s,['group','time']);_unique(r,['group','time']);groups=list(pd.unique(s.group));pal=group_palette(theme,groups)
    if risk_convention not in ['start_of_period','end_of_period'] or not interval_definition or not time_label:raise ValueError('Explicit risk convention, time and interval definitions required')
    if (s.time<0).any() or ((s[['survival','lower','upper']]<0)|(s[['survival','lower','upper']]>1)).any().any() or ((s.lower>s.survival)|(s.upper<s.survival)).any():raise ValueError('Invalid survival step or interval')
    if set(r.group)!=set(groups) or (r.at_risk<0).any() or (r.at_risk%1!=0).any() or (r.time<0).any():raise ValueError('Complete supplied integer at-risk counts required')
    times=list(pd.unique(r.time))
    if len(r)!=len(groups)*len(times) or times!=sorted(times) or min(times)<s.time.min() or max(times)>s.time.max():raise ValueError('Complete ordered group x risk-time grid inside displayed follow-up required')
    fig=_new(theme,(8,6.0));ax=_axis(fig,[.12,.43,.61,.41]);risk=fig.add_axes([.12,.135,.61,.13]);risk.set_xlim(*[s.time.min(),s.time.max()]);risk.set_ylim(-.5,len(groups)-.5);risk.axis('off')
    for i,g in enumerate(groups):
        q=s[s.group==g]
        if (np.diff(q.time)<=0).any() or (np.diff(q.survival)>1e-12).any():raise ValueError('Survival must be ordered and non-increasing')
        ax.step(q.time,q.survival,where='post',c=pal[g],label=g);ax.fill_between(q.time,q.lower,q.upper,step='post',color=pal[g],alpha=.17)
        risk.text(-.05,len(groups)-i-1,g,transform=risk.get_yaxis_transform(),ha='right',va='center',color=pal[g],fontsize=9)
        rr=r[r.group==g]
        if (np.diff(rr.at_risk)>0).any():raise ValueError('At-risk table must be non-increasing for this non-reentry adapter')
        for v in rr.itertuples():risk.text(v.time,len(groups)-i-1,str(int(v.at_risk)),ha='center',va='center',fontsize=9)
    if not c.empty:
        if set(c.group)-set(groups) or ((c.survival<0)|(c.survival>1)|(c.time<s.time.min())|(c.time>s.time.max())).any():raise ValueError('Invalid supplied censor markers')
        for g,q in c.groupby('group'):
            steps=s[s.group==g];idx=np.searchsorted(steps.time.to_numpy(),q.time.to_numpy(),side='right')-1
            if (idx<0).any() or (q.time>steps.time.max()).any() or not np.allclose(q.survival,steps.survival.to_numpy()[idx],rtol=0,atol=1e-10):raise ValueError('Censor coordinates must lie on the given group post-step curve')
            ax.scatter(q.time,q.survival,marker='|',s=40,color=pal[g])
    ax.set(xlabel=time_label,ylabel='Supplied survival probability',ylim=(0,1.04),xlim=(s.time.min(),s.time.max()),title=title);fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.77,.84),frameon=False)
    fig.text(.12,.326,'At risk ('+risk_convention.replace('_',' ')+')',fontsize=9)
    for v in times:risk.text(v,len(groups)-.1,f'{v:g}',ha='center',va='bottom',fontsize=8,color='#586672')
    fig.text(.12,.07,interval_definition+'; no Kaplan-Meier fit or log-rank test is performed.',fontsize=8)
    return _finish(fig,data,theme,'survival_steps_at_risk',risk_convention=risk_convention,interval_definition=interval_definition,time_label=time_label,censoring='explicit supplied markers only',step='post')

def plot_swimmer(data,theme,*,time_label,event_shapes,object_order,title=''):
    _types(data,['interval','event']);s=_records(data,'interval',['object_id','group','start','end'],['start','end']);e=_records(data,'event',['object_id','time','event'],['time'],True)
    _unique(s,['object_id','start','end']);groups=list(pd.unique(s.group));pal=group_palette(theme,groups)
    if set(object_order)!=set(s.object_id) or len(object_order)!=len(set(object_order)) or (s.start<0).any() or (s.end<=s.start).any() or (s.groupby('object_id').group.nunique()!=1).any():raise ValueError('Explicit objects, valid intervals and stable identities required')
    for _,q in s.groupby('object_id'):
        q=q.sort_values('start')
        if len(q)>1 and (q.start.to_numpy()[1:]<q.end.to_numpy()[:-1]).any():raise ValueError('Overlapping intervals require another adapter')
    if not e.empty:
        if set(e.event)-set(event_shapes) or set(e.object_id)-set(object_order):raise ValueError('Unknown event or object')
        for v in e.itertuples():
            q=s[s.object_id==v.object_id]
            if not ((q.start<=v.time)&(q.end>=v.time)).any():raise ValueError('Event outside declared follow-up intervals')
    fig=_new(theme,(8,max(4,len(object_order)*.31+1.5)));ax=_axis(fig,[.14,.20,.56,.64]);ym={x:i for i,x in enumerate(object_order)}
    for v in s.itertuples():ax.plot([v.start,v.end],[ym[v.object_id]]*2,color=pal[v.group],lw=5,solid_capstyle='butt')
    for v in e.itertuples():
        marker=event_shapes[v.event];kwargs=dict(ec='white',lw=.3) if MarkerStyle(marker).is_filled() else dict(lw=1.1)
        ax.scatter(v.time,ym[v.object_id],marker=marker,color=theme['roles']['border'],s=32,zorder=4,**kwargs)
    ax.set(yticks=range(len(object_order)),yticklabels=object_order,xlabel=time_label,title=title);ax.invert_yaxis()
    fig.legend(handles=[Line2D([],[],color=pal[g],lw=4,label=g) for g in groups]+[Line2D([],[],color=theme['roles']['border'],marker=m,ls='',label=k) for k,m in event_shapes.items()],loc='upper left',bbox_to_anchor=(.75,.83),frameon=False)
    return _finish(fig,data,theme,'swimmer_followup',time_label=time_label,event_shapes=event_shapes,object_order=object_order,interval_semantics='provided follow-up; disconnected intervals retained')

def plot_specification_curve(data,theme,*,spec_order,decision_order,effect_scale,interval_definition,title=''):
    _types(data,['estimate','decision']);s=_records(data,'estimate',['spec_id','estimate','lower','upper'],['estimate','lower','upper']);m=_records(data,'decision',['spec_id','decision','included'],['included'])
    _unique(s,['spec_id']);_unique(m,['spec_id','decision']);null=effect_reference(effect_scale)
    if len(spec_order)!=len(set(spec_order)) or set(spec_order)!=set(s.spec_id) or set(decision_order)!=set(m.decision) or len(decision_order)!=len(set(decision_order)) or len(m)!=len(s)*len(decision_order) or set(m.spec_id)!=set(s.spec_id):raise ValueError('Complete supplied specification and decision grid required')
    if not set(m.included)<=set([0,1]) or ((s.lower>s.estimate)|(s.upper<s.estimate)).any() or not interval_definition:raise ValueError('Invalid interval or binary decision')
    if effect_scale=='ratio' and (s[['estimate','lower','upper']]<=0).any().any():raise ValueError('Positive ratio intervals required')
    fig=_new(theme,(9,6.1));ax=_axis(fig,[.14,.48,.80,.35]);grid=fig.add_axes([.14,.17,.80,.21]);q=s.set_index('spec_id').loc[spec_order];xx=np.arange(len(q))
    for i,r in enumerate(q.itertuples()):ax.plot([i,i],[r.lower,r.upper],color=theme['roles']['primary'],lw=.9);ax.scatter(i,r.estimate,color=theme['roles']['primary'],s=20)
    ax.axhline(null,ls='--',color=theme['roles']['neutral'],lw=.8);ax.set(xticks=[],ylabel='Supplied estimate',title=title,xlim=(-.5,len(q)-.5))
    if effect_scale=='ratio':ax.set_yscale('log')
    mat=m.pivot(index='decision',columns='spec_id',values='included').reindex(index=decision_order,columns=spec_order).to_numpy()
    cmap=LinearSegmentedColormap.from_list('decision',['#F1F4F6',theme['roles']['primary']]);grid.imshow(mat,cmap=cmap,vmin=0,vmax=1,interpolation='nearest',aspect='auto');grid.set(xticks=xx,xticklabels=spec_order,yticks=range(len(decision_order)),yticklabels=decision_order,xlabel='Reviewed specification order');grid.tick_params(axis='x',rotation=60,length=0,labelsize=8);grid.tick_params(axis='y',length=0)
    fig.text(.14,.06,interval_definition+'; this display does not perform joint multiverse inference.',fontsize=8)
    return _finish(fig,data,theme,'specification_curve',spec_order=spec_order,decision_order=decision_order,effect_scale=effect_scale,interval_definition=interval_definition,joint_inference='not performed')

def plot_vector_field(data,theme,*,arrow_scale,vector_definition,coordinate_definition,title=''):
    d=checked(data,['object_id','group','x','y','vx','vy'],['x','y','vx','vy']);_unique(d,['object_id']);pal=group_palette(theme,list(pd.unique(d.group)))
    if not np.isfinite(arrow_scale) or arrow_scale<=0 or not vector_definition or not coordinate_definition:raise ValueError('Declare coordinates, vector units and positive scale')
    fig=_new(theme,(8,5.6));ax=_axis(fig,[.10,.18,.59,.65])
    for g,q in d.groupby('group',sort=False):ax.scatter(q.x,q.y,c=pal[g],s=21,alpha=.52,ec='white',lw=.2,label=g)
    ax.quiver(d.x,d.y,d.vx,d.vy,angles='xy',scale_units='xy',scale=arrow_scale,color=theme['roles']['border'],width=.0024,headwidth=3.5,zorder=3)
    ax.set_aspect('equal');ax.set(xlabel='Supplied coordinate 1',ylabel='Supplied coordinate 2',title=title);ax.margins(.12);fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.75,.84),frameon=False)
    fig.text(.74,.38,'Frozen vectors\nScale '+f'{arrow_scale:g}'+'\nNo smoothing or\nstream integration',fontsize=9)
    return _finish(fig,data,theme,'supplied_vector_field',arrow_scale=arrow_scale,vector_definition=vector_definition,coordinate_definition=coordinate_definition,projection='already supplied; no velocity inference')

def plot_bivariate_tiles(data,theme,*,x_breaks,y_breaks,x_label,y_label,title=''):
    d=checked(data,['row','column','metric_x','metric_y'],['metric_x','metric_y']);_unique(d,['row','column']);rows=list(pd.unique(d.row));cols=list(pd.unique(d.column))
    if len(d)!=len(rows)*len(cols):raise ValueError('Complete finite cell grid required')
    for field,b in [('metric_x',x_breaks),('metric_y',y_breaks)]:
        if len(b)!=4 or not np.isfinite(b).all() or (np.diff(b)<=0).any() or d[field].min()<b[0] or d[field].max()>b[-1]:raise ValueError('Three explicit ordered bins must cover every value')
    c0=np.array(to_rgb('#F2F5F8'));cx=np.array(to_rgb(theme['roles']['negative']));cy=np.array(to_rgb(theme['roles']['positive']));cxy=(cx+cy)*.40;colors={}
    for i in range(3):
        for j in range(3):
            x=i/2;y=j/2;colors[(i,j)]=c0*(1-x)*(1-y)+cx*x*(1-y)+cy*y*(1-x)+cxy*x*y
    fig=_new(theme,(8.5,5.4));ax=fig.add_axes([.13,.23,.53,.57]);key=fig.add_axes([.76,.30,.17,.27]);xm={x:i for i,x in enumerate(cols)};ym={x:i for i,x in enumerate(rows)}
    for r in d.itertuples():
        i=min(2,int(np.searchsorted(x_breaks,r.metric_x,side='right')-1));j=min(2,int(np.searchsorted(y_breaks,r.metric_y,side='right')-1));ax.add_patch(Rectangle((xm[r.column],ym[r.row]),1,1,fc=colors[(i,j)],ec='white',lw=.8))
    ax.set(xlim=(0,len(cols)),ylim=(len(rows),0),xticks=np.arange(len(cols))+.5,xticklabels=cols,yticks=np.arange(len(rows))+.5,yticklabels=rows,title=title);ax.tick_params(length=0);ax.spines[:].set_visible(False)
    for i in range(3):
        for j in range(3):key.add_patch(Rectangle((i,j),1,1,fc=colors[(i,j)],ec='white',lw=.7))
    key.set(xlim=(0,3),ylim=(0,3),xticks=[.5,1.5,2.5],xticklabels=['L','M','H'],yticks=[.5,1.5,2.5],yticklabels=['L','M','H'],xlabel=x_label,ylabel=y_label);key.tick_params(length=0,labelsize=8);key.spines[:].set_visible(False)
    fig.text(.13,.08,'Bounded bins, left-closed; final upper edge included. Two metrics share a 2D legend.',fontsize=8)
    return _finish(fig,data,theme,'bivariate_tiles',x_breaks=list(x_breaks),y_breaks=list(y_breaks),x_label=x_label,y_label=y_label,color_provenance='original blend of project semantic roles; not a source colour card',bin_policy='left closed; final upper edge inclusive',legend_colors={str(k):v.tolist() for k,v in colors.items()})
