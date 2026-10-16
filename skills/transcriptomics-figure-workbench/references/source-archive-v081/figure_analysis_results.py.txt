"""Original frozen analysis-result views: no inference or engine execution."""
import textwrap
import numpy as np
import pandas as pd
from matplotlib.path import Path
from matplotlib.patches import PathPatch,Rectangle,Patch
from matplotlib.lines import Line2D
from figure_core import checked
from figure_method_extensions import _new,_axis,_finish,_unique
from figure_biomni_views import _order,_declared
from project_theme import group_palette


def plot_splice_tracks(data,theme,*,sample_order,transcript_order,region,coordinate_definition,
                       coverage_definition,junction_definition,width_per_count=.045,title=''):
    if 'record_type' not in data or set(data.record_type)-{'coverage','junction','exon'}:raise ValueError('Use coverage, junction and exon records')
    cov=checked(data[data.record_type=='coverage'],['sample_id','group','start','end','value'],['start','end','value'])
    junction=checked(data[data.record_type=='junction'],['sample_id','start','end','count','lane'],['start','end','count','lane'])
    exon=checked(data[data.record_type=='exon'],['transcript_id','exon_id','start','end'],['start','end'])
    samples=_order(cov.sample_id,sample_order);transcripts=_order(exon.transcript_id,transcript_order)
    _unique(cov,['sample_id','start','end']);_unique(junction,['sample_id','start','end']);_unique(exon,['transcript_id','exon_id'])
    if len(region)!=2 or not np.isfinite(region).all() or region[0]>=region[1] or not np.isfinite(width_per_count) or width_per_count<=0:raise ValueError('Finite region and positive junction-width scale required')
    _declared(coordinate_definition,coverage_definition,junction_definition)
    for q in (cov,junction,exon):
        if ((q.start<region[0])|(q.end>region[1])|(q.start>=q.end)).any():raise ValueError('Every interval must be inside the declared physical region')
    if (cov.value<0).any() or ((junction['count']<0)|(junction['count']%1!=0)|(junction.lane<1)|(junction.lane%1!=0)).any() or set(junction.sample_id)-set(samples):raise ValueError('Nonnegative coverage and integer counts/positive lanes required')
    if (cov.groupby('sample_id').group.nunique()!=1).any():raise ValueError('Each sample has one explicit group')
    pal=group_palette(theme,list(pd.unique(cov.group)))
    for sample in samples:
        q=cov[cov.sample_id==sample].sort_values('start')
        if (q.start.to_numpy()[1:]<q.end.to_numpy()[:-1]).any():raise ValueError('Coverage bins overlap; aggregate in the upstream analysis')
    gene_height=max(.58,len(transcripts)*.23);figure_height=1.9+len(samples)*1.65+gene_height
    fig=_new(theme,(10,figure_height));axes=[]
    maxcov=max(float(cov.value.max()),1e-8);zero=[]
    for i,sample in enumerate(samples):
        base=.92+gene_height+.22+(len(samples)-1-i)*1.65
        a=_axis(fig,[.14,base/figure_height,.62,.78/figure_height]);arcs=fig.add_axes([.14,(base+.84)/figure_height,.62,.50/figure_height]);arcs.set_axis_off()
        if axes:a.sharex(axes[0]);arcs.sharex(axes[0])
        else:arcs.sharex(a)
        axes.append(a);q=cov[cov.sample_id==sample];color=pal[q.group.iloc[0]]
        for r in q.itertuples():a.fill_between([r.start,r.end],r.value,0,color=color,alpha=.6,lw=0)
        a.set(xlim=region,ylim=(0,maxcov*1.1),ylabel=sample+'\ncoverage');a.tick_params(labelbottom=False)
        z=junction[junction.sample_id==sample];arcs.set(xlim=region,ylim=(0,float(z.lane.max() if len(z) else 1)*1.3))
        for r in z.itertuples():
            if r.count==0:zero.append([sample,float(r.start),float(r.end)]);continue
            path=Path([(r.start,0),((r.start+r.end)/2,2*r.lane),(r.end,0)],[Path.MOVETO,Path.CURVE3,Path.CURVE3])
            patch=PathPatch(path,fill=False,color=color,lw=r.count*width_per_count);patch.set_gid('junction:'+sample+':'+str(r.start)+':'+str(r.end));arcs.add_patch(patch)
            arcs.text((r.start+r.end)/2,r.lane+.12,str(int(r.count)),ha='center',fontsize=8)
    genes=_axis(fig,[.14,.92/figure_height,.62,gene_height/figure_height]);genes.sharex(axes[0]);genes.set(ylim=(-.6,len(transcripts)-.4),yticks=range(len(transcripts)),yticklabels=transcripts,xlabel='Supplied genomic position');genes.spines[['left','top','right']].set_visible(False)
    for i,t in enumerate(transcripts):
        q=exon[exon.transcript_id==t].sort_values('start');genes.plot([q.start.min(),q.end.max()],[i,i],c=theme['roles']['border'],lw=.8)
        for r in q.itertuples():genes.add_patch(Rectangle((r.start,i-.20),r.end-r.start,.4,fc=theme['roles']['primary'],lw=0))
    fig.text(.14,.96,title,fontsize=11,weight='bold');fig.text(.80,.82,'Arc width = supplied count\n'+f'{width_per_count:g} pt per count\nArc lane = layout only',fontsize=8)
    fig.text(.14,.14/figure_height,textwrap.fill(coordinate_definition+'; '+coverage_definition+'; '+junction_definition,120),fontsize=8)
    return _finish(fig,data,theme,'splice_tracks',sample_order=samples,transcript_order=transcripts,region=region,coordinate_definition=coordinate_definition,coverage_definition=coverage_definition,junction_definition=junction_definition,width_per_count=width_per_count,title=title,zero_junctions=zero,inference='none; input bins/counts/annotation retained, no BAM parsing or differential splicing')


def plot_variant_posteriors(data,theme,*,signal_order,region,coordinate_definition,posterior_definition,label_ids=None,title=''):
    d=checked(data,['signal','variant_id','position','pip','credible_set'],['position','pip']);_unique(d,['signal','variant_id'])
    signals=_order(d.signal,signal_order);_declared(coordinate_definition,posterior_definition)
    if len(region)!=2 or not np.isfinite(region).all() or region[0]>=region[1] or ((d.position<region[0])|(d.position>region[1])|(d.pip<0)|(d.pip>1)).any():raise ValueError('Complete region and PIPs in [0,1] required')
    if d.groupby('variant_id').position.nunique().max()!=1 or any(set(d[d.signal==s].variant_id)!=set(d.variant_id) for s in signals):raise ValueError('Every signal must retain the same variant IDs and physical positions')
    label_ids=[] if label_ids is None else list(label_ids)
    if len(label_ids)!=len(set(label_ids)) or set(label_ids)-set(d.variant_id):raise ValueError('Label IDs must be an explicit subset of actual variants')
    pal=group_palette(theme,signals);fig=_new(theme,(9,2+len(signals)*1.6));axes=[]
    for i,s in enumerate(signals):
        ax=_axis(fig,[.13,.18+(len(signals)-1-i)*.67/len(signals),.63,.52/len(signals)])
        if axes:ax.sharex(axes[0])
        axes.append(ax);q=d[d.signal==s]
        ax.vlines(q.position,0,q.pip,color=pal[s],alpha=.6,lw=1)
        for credible,marker in [(False,'o'),(True,'D')]:
            z=q[(q.credible_set!='none')==credible];ax.scatter(z.position,z.pip,s=22,c=pal[s],marker=marker,ec='white',lw=.3)
        for r in q[q.variant_id.isin(label_ids)].itertuples():ax.annotate(r.variant_id,(r.position,r.pip),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8)
        ax.set(xlim=region,ylim=(0,1.12),ylabel=s+'\nPIP');ax.tick_params(labelbottom=i==len(signals)-1)
    axes[-1].set_xlabel('Supplied genomic position');fig.text(.13,.94,title,weight='bold',fontsize=11)
    fig.legend(handles=[Line2D([],[],ls='',marker='D',color=theme['roles']['border'],label='Given credible-set member'),Line2D([],[],ls='',marker='o',color=theme['roles']['border'],label='Outside given sets')],loc='upper left',bbox_to_anchor=(.79,.80),frameon=False)
    fig.text(.13,.055,textwrap.fill(coordinate_definition+'; '+posterior_definition,105),fontsize=8)
    return _finish(fig,data,theme,'variant_posteriors',signal_order=signals,region=region,coordinate_definition=coordinate_definition,posterior_definition=posterior_definition,label_ids=label_ids,title=title,inference='none; multi-signal PIPs need not sum to one; overlapping PIPs do not establish colocalization')


def plot_contribution_waterfall(data,theme,*,component_order,baseline,total,quantity_definition,contribution_definition,title=''):
    d=checked(data,['component_id','label','contribution'],['contribution']);_unique(d,['component_id']);order=_order(d.component_id,component_order)
    _declared(quantity_definition,contribution_definition)
    if not np.isfinite([baseline,total]).all() or not np.isclose(baseline+d.contribution.sum(),total,rtol=1e-10,atol=1e-10):raise ValueError('Supplied baseline plus complete contributions must equal supplied total')
    d=d.set_index('component_id').loc[order];fig=_new(theme,(max(8,2+len(order)*.65),5.3));ax=_axis(fig,[.12,.29,.72,.55]);level=float(baseline);records=[]
    ax.bar(0,abs(baseline),bottom=min(0,baseline),color=theme['roles']['neutral'],width=.7)
    for j,(id_,r) in enumerate(d.iterrows(),1):
        end=level+float(r.contribution);color=theme['roles']['positive' if r.contribution>=0 else 'negative']
        if r.contribution:ax.bar(j,abs(r.contribution),bottom=min(level,end),color=color,width=.7)
        else:ax.plot([j-.35,j+.35],[level,level],c=theme['roles']['neutral'],lw=1)
        ax.plot([j-.65,j-.35],[level,level],c=theme['roles']['border'],ls=':',lw=.7)
        records.append(dict(component=id_,start=level,end=end,contribution=float(r.contribution)));level=end
    ax.bar(len(order)+1,abs(total),bottom=min(0,total),color=theme['roles']['primary'],width=.7);ax.axhline(0,color=theme['roles']['border'],lw=.6)
    ax.set(xticks=range(len(order)+2),xticklabels=['Baseline']+[textwrap.fill(str(x),13) for x in d.label]+['Total'],ylabel=quantity_definition,title=title)
    ax.tick_params(axis='x',labelrotation=30);fig.text(.12,.06,textwrap.fill(contribution_definition,110),fontsize=8)
    fig.legend(handles=[Patch(color=theme['roles']['positive'],label='Positive contribution'),Patch(color=theme['roles']['negative'],label='Negative contribution')],loc='upper left',bbox_to_anchor=(.86,.84),frameon=False)
    return _finish(fig,data,theme,'contribution_waterfall',component_order=order,baseline=baseline,total=total,quantity_definition=quantity_definition,contribution_definition=contribution_definition,title=title,levels=records,inference='none; additive inputs required, no attribution or mechanistic decomposition calculated')
