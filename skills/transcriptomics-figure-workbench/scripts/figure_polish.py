"""Additive publication layouts for frozen dense matrices and recorded-count evidence.

No feature selection, statistics, clustering, inference or external I/O.
"""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,TwoSlopeNorm,LinearSegmentedColormap
from matplotlib.patches import Rectangle,Patch
from figure_core import checked,stamp,palette_check
from figure_multimodal import themed,axis,required_text,SIGNED

BLUE='#35618F';AMBER='#B87822';GREY='#7A838B'
SEQ=LinearSegmentedColormap.from_list('polished_magnitude',['#FAFAF7','#C1D8E6',BLUE])

def display_map(keys,mapping):
    result={k:str((mapping or {}).get(k,k)) for k in keys}
    if any(not v.strip() for v in result.values()) or len(set(result.values()))!=len(keys):
        raise ValueError('Display aliases must be nonempty and unique within axis')
    return result

def contiguous_blocks(keys,mapping):
    if mapping is None:return [('All',keys)]
    if set(mapping)!=set(keys):raise ValueError('Block map must cover exactly all axis IDs')
    result=[]
    for key in keys:
        label=mapping[key]
        if not isinstance(label,str) or not label.strip():raise ValueError('Nonempty block labels required')
        if not result or label!=result[-1][0]:result.append((label,[key]))
        else:result[-1][1].append(key)
    if len(set(x[0] for x in result))!=len(result):raise ValueError('Blocks must be contiguous; no hidden reorder')
    return result

@themed
def plot_polished_matrix(data,*,value_label,limits,signed,row_aliases=None,
                         column_aliases=None,row_blocks=None,column_blocks=None,
                         layout='matrix',width_mm=180,font_size=8.5,title='',note='',sign_marks=True):
    """All values/order retained; layout matrix, blocks or transpose; exact alias mapping."""
    required_text(value_label=value_label)
    if type(sign_marks) is not bool:raise ValueError('sign_marks must be boolean')
    d=checked(data,['feature','sample','value'],['value'])
    rows=list(dict.fromkeys(d.feature));cols=list(dict.fromkeys(d['sample']))
    if d.duplicated(['feature','sample']).any() or len(d)!=len(rows)*len(cols):raise ValueError('Complete unique matrix required')
    if len(rows)>100 or len(cols)>100:raise ValueError('Split oversized matrices without filtering')
    if layout not in ('matrix','blocks','transpose') or not 150<=width_mm<=240 or not 8<=font_size<=11:raise ValueError('Unsupported layout or final-size geometry')
    if len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1] or d.value.min()<limits[0] or d.value.max()>limits[1]:raise ValueError('Limits must contain every value')
    if type(signed) is not bool or (signed and not limits[0]<0<limits[1]):raise ValueError('Declare signed zero-centered or sequential scale')
    ra=display_map(rows,row_aliases);ca=display_map(cols,column_aliases)
    rb=contiguous_blocks(rows,row_blocks);cb=contiguous_blocks(cols,column_blocks)
    mat=d.pivot(index='feature',columns='sample',values='value').reindex(index=rows,columns=cols).to_numpy()
    norm=TwoSlopeNorm(0,*limits) if signed else Normalize(*limits)
    cmap=SIGNED if signed else SEQ
    if layout=='transpose':
        shown=mat.T;ykeys=cols;xkeys=rows;ylab=ca;xlab=ra
        groups=[('All',xkeys)]
        horizontal_blocks=cb
    else:
        shown=mat;ykeys=rows;xkeys=cols;ylab=ra;xlab=ca
        groups=cb if layout=='blocks' else [('All',xkeys)]
        horizontal_blocks=rb
    height=max(4.4,len(ykeys)*.215+2.15)
    fig=plt.figure(figsize=(width_mm/25.4,height))
    gs=fig.add_gridspec(1,len(groups),width_ratios=[len(k) for _,k in groups],wspace=.10 if layout=='blocks' else .0)
    fig.subplots_adjust(left=.22,right=.97,bottom=1.65/height,top=1-.75/height)
    axes=[];images=[];offset=0
    for i,(block,keys) in enumerate(groups):
        ax=fig.add_subplot(gs[0,i],sharey=axes[0] if axes else None);axes.append(ax)
        positions=[xkeys.index(x) for x in keys]
        values=shown[:,positions]
        im=ax.pcolormesh(np.arange(len(keys)+1)-.5,np.arange(len(ykeys)+1)-.5,values,norm=norm,cmap=cmap,shading='flat',rasterized=False);images.append(im)
        ax.set_xlim(-.5,len(keys)-.5);ax.set_ylim(len(ykeys)-.5,-.5)
        if signed and sign_marks:
            for row,col in np.argwhere(values<0):ax.text(col,row,'−',ha='center',va='center',fontsize=font_size,color='#27323C')
        ax.set_xticks(range(len(keys)),[xlab[k] for k in keys],rotation=90 if len(xkeys)>20 else 40,ha='center' if len(xkeys)>20 else 'right')
        ax.set_yticks(range(len(ykeys)),[ylab[k] for k in ykeys]);ax.tick_params(length=0,labelsize=font_size,pad=4)
        if i:ax.tick_params(labelleft=False)
        for s in ax.spines.values():s.set_visible(False)
        ax.set_xticks(np.arange(len(keys)+1)-.5,minor=True)
        ax.set_yticks(np.arange(len(ykeys)+1)-.5,minor=True)
        ax.grid(which='minor',color='white',lw=.25);ax.tick_params(which='minor',length=0)
        y=0
        for label,items in horizontal_blocks[:-1]:
            y+=len(items);ax.axhline(y-.5,color='white',lw=1.8)
        if layout=='blocks':
            ax.set_title(block,fontsize=font_size,pad=8)
        elif layout=='matrix' and column_blocks:
            cursor=0
            for label,items in cb:
                length=len(items)
                ax.add_patch(Rectangle((cursor-.5,1.01),length,.075,transform=ax.get_xaxis_transform(),
                                      facecolor='#EAF0F3',edgecolor='white',lw=1,clip_on=False))
                ax.text(cursor+(length-1)/2,1.047,label,transform=ax.get_xaxis_transform(),
                        ha='center',va='center',fontsize=font_size-0.5,clip_on=False)
                cursor+=length
        offset+=len(keys)
    cax=fig.add_axes([.30,.82/height,.59,.10/height])
    colorbar=fig.colorbar(images[0],cax=cax,orientation='horizontal')
    if colorbar.solids is not None:
        colorbar.solids.set_rasterized(False)
        colorbar.solids.set_edgecolor('face')
    colorbar.set_label(value_label,fontsize=font_size,labelpad=3);colorbar.ax.tick_params(labelsize=font_size-0.5,length=2,width=.5)
    fig.text(.22,1-.12/height,title,fontsize=11,weight='bold',va='top')
    if note:fig.text(.22,.08/height,textwrap.fill(note,90),fontsize=8,va='bottom')
    return stamp(fig,data,'polished_matrix',layout=layout,limits=list(limits),signed=signed,
                 value_label=value_label,sign_marks=bool(signed and sign_marks),palette={'low':'#0072B2','center':'#FAFAF7','high':'#D55E00'} if signed else {'low':'#FAFAF7','middle':'#C1D8E6','high':BLUE},row_aliases=ra,column_aliases=ca,row_blocks=row_blocks,
                 column_blocks=column_blocks,row_order=rows,column_order=cols,
                 width_mm=width_mm,font_size=font_size,selection='all supplied rows; no reorder or transform')

def recorded_evidence_table(therapy,comedication):
    """Reversible union of exact input columns; table_kind identifies each source."""
    if 'table_kind' in therapy or 'table_kind' in comedication:raise ValueError('Reserved table_kind column')
    return pd.concat([therapy.assign(table_kind='therapy'),comedication.assign(table_kind='comedication')],ignore_index=True,sort=False)

def evidence_checked(data):
    d=checked(data,['table_kind','cluster','denominator'],['denominator'])
    if set(d.table_kind)!=set(['therapy','comedication']):raise ValueError('Both source tables required')
    t=d[d.table_kind=='therapy'].copy();c=d[d.table_kind=='comedication'].copy()
    fields=['single_complete_nonnegative_pair','missing_multiple_invalid_or_negative_dates','no_linked_therapy']
    checked(t,['cluster']+fields,fields)
    if t.cluster.duplicated().any() or ((t.denominator<=0)|(t.denominator%1!=0)).any():raise ValueError('One therapy row per cluster, positive integer n')
    if ((t[fields]<0)|(t[fields]%1!=0)).any().any() or not np.array_equal(t[fields].sum(axis=1),t.denominator):raise ValueError('Categories must exhaust the exact denominator')
    checked(c,['comedication','status'])
    rows=list(t.cluster);drugs=list(dict.fromkeys(c.comedication))
    if len(rows)>30 or len(drugs)>8 or c.duplicated(['cluster','comedication']).any() or set(c.cluster)!=set(rows) or len(c)!=len(rows)*len(drugs):raise ValueError('Complete unique cluster/drug grid required')
    denom=t.set_index('cluster').denominator
    if ((c.denominator<=0)|(c.denominator%1!=0)).any() or not all(r.denominator==denom[r.cluster] for r in c.itertuples()):raise ValueError('Matched denominators required')
    if not set(c.status).issubset({'recorded_field_count','index_drug_not_comedication','unavailable'}):raise ValueError('Unknown source status')
    z=c[c.status=='recorded_field_count'];checked(z,['any_role','suspect_role'],['any_role','suspect_role'])
    if ((z.suspect_role<0)|(z.any_role<z.suspect_role)|(z.any_role>z.denominator)|(z.any_role%1!=0)|(z.suspect_role%1!=0)).any():raise ValueError('Integer 0<=suspect<=any<=n required')
    if c.loc[c.status!='recorded_field_count',['any_role','suspect_role']].notna().any().any():raise ValueError('Unavailable/index-drug counts must be missing, never zero')
    return t,c,rows,drugs,fields

@themed
def plot_recorded_evidence(data,*,row_aliases=None,layout='aligned',width_mm=180,
                           font_size=8.5,title='Recorded evidence',note=''):
    """Preserve zero, N/A and overlapping report-unit denominators; no risk estimates."""
    t,c,rows,drugs,fields=evidence_checked(data)
    if layout not in ('aligned','split','table') or not 150<=width_mm<=240 or not 8<=font_size<=11:raise ValueError('Invalid print geometry/layout')
    aliases=display_map(rows,row_aliases)
    height=len(rows)*.34+2.25
    if layout=='split':
        height=len(rows)*.68+3.4
        fig,(a,b)=plt.subplots(2,1,figsize=(width_mm/25.4,height),gridspec_kw={'hspace':.35})
        fig.subplots_adjust(left=.25,right=.96,bottom=1.0/height,top=1-1.15/height)
    else:
        fig,(a,b)=plt.subplots(1,2,figsize=(width_mm/25.4,height),sharey=True,
                              gridspec_kw={'width_ratios':[1.0,1.3],'wspace':.17})
        fig.subplots_adjust(left=.27,right=.98,bottom=1.05/height,top=1-1.15/height)
    colors=[BLUE,AMBER,GREY];yy=np.arange(len(rows))
    z=t.set_index('cluster').loc[rows]
    if layout=='table':
        for j,(field,col) in enumerate(zip(fields,colors)):
            for i,value in enumerate(z[field]):
                a.text(j,i,str(int(value)),ha='center',va='center',fontsize=font_size,color=col if value else '#525D66',weight='bold' if value else 'normal')
        a.set(xlim=(-.5,2.5));a.set_xticks(range(3),['Complete','Dates\nunresolved','No linked\nrecord'])
        a.tick_params(axis='x',length=0,labelsize=font_size)
        for spine in a.spines.values():spine.set_visible(False)
    else:
        left=np.zeros(len(rows))
        for j,(field,col) in enumerate(zip(fields,colors)):
            a.barh(yy,z[field],left=left,height=.60,color=col,edgecolor='white',lw=.4,hatch=['','///','..'][j])
            left+=z[field].to_numpy()
        high=float(z.denominator.max());a.set_xlim(0,high*1.55)
        for i,r in enumerate(z.itertuples()):
            values=[int(getattr(r,f)) for f in fields]
            a.text(r.denominator+high*.04,i,' / '.join(map(str,values)),fontsize=font_size-0.5,va='center')
        a.set_xlabel('Recorded counts',fontsize=font_size);axis(a,False)
        a.grid(axis='x',color='#ECF0F2',lw=.4,zorder=0)
    labels=[aliases[k]+' ; n='+str(int(z.loc[k,'denominator'])) for k in rows]
    a.set_yticks(yy,labels);a.set_ylim(len(rows)-.5,-.5);a.tick_params(axis='y',length=0,labelsize=font_size,pad=5)
    for r in c.itertuples():
        i=rows.index(r.cluster);j=drugs.index(r.comedication)
        unavailable=r.status!='recorded_field_count'
        nonzero=not unavailable and r.any_role>0
        b.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor='#E7EFF5' if nonzero else '#F3F4F5' if unavailable else 'white',
                             edgecolor='#D7DEE4',lw=.4,hatch='///' if unavailable else ''))
        text='N/A' if r.status=='index_drug_not_comedication' else '?' if unavailable else f'{int(r.suspect_role)} / {int(r.any_role)}'
        b.text(j,i,text,ha='center',va='center',fontsize=font_size,color='#27323C' if nonzero else '#525D66',weight='bold' if nonzero else 'normal')
    b.set(xlim=(-.5,len(drugs)-.5),ylim=(len(rows)-.5,-.5))
    b.set_xticks(range(len(drugs)),[textwrap.fill(x,12) for x in drugs],rotation=35,ha='right')
    b.set_yticks(yy)
    if layout=='split':b.set_yticklabels(labels)
    else:b.tick_params(labelleft=False)
    b.tick_params(length=0,labelsize=font_size)
    for s in b.spines.values():s.set_visible(False)
    a.set_title('A  Linked therapy',loc='left',fontsize=10,pad=9)
    b.set_title('B  Co-recorded medication',loc='left',fontsize=10,pad=9)
    fig.text(.27 if layout!='split' else .25,1-.12/height,title,fontsize=11,weight='bold',va='top')
    handles=[Patch(facecolor=col,edgecolor='white',hatch=h,label=label) for col,h,label in zip(colors,['','///','..'],['Complete pair','Dates unresolved','No linked record'])]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.25,1-.38/height),ncol=3,frameon=False,fontsize=8,handlelength=1.2,columnspacing=.9)
    fig.text(.27 if layout!='split' else .25,1-.82/height,'A counts: complete / dates unresolved / none.  B cells: suspect / any.',fontsize=8)
    foot='N/A = index drug; ? = unavailable. Zero = not recorded; co-recording is not simultaneous exposure.'
    if note:foot+=' '+note
    fig.text(.27 if layout!='split' else .25,.08/height,textwrap.fill(foot,90),fontsize=8,va='bottom')
    return stamp(fig,data,'recorded_evidence',layout=layout,row_aliases=aliases,cluster_order=rows,
                 medication_order=drugs,denominator='per-cluster n displayed once; rows may overlap',
                 zero='explicit 0 / 0',missing='N/A or ? with hatching',fields=fields,
                 width_mm=width_mm,font_size=font_size,palette={'complete':BLUE,'unresolved':AMBER,'none':GREY},inference='none')

@themed
def plot_availability_counts(data,*,row_aliases=None,title='Record availability',width_mm=180):
    """Two frozen counts and exact absence arithmetic; keep all literature zeroes explicit."""
    d=checked(data,['display_cluster','reports','any_therapy_rows','nonempty_literature_reference'],
              ['reports','any_therapy_rows','nonempty_literature_reference'])
    if d.display_cluster.duplicated().any() or ((d.reports<=0)|(d.any_therapy_rows<0)|(d.any_therapy_rows>d.reports)|(d.nonempty_literature_reference<0)|(d.nonempty_literature_reference>d.reports)|(d[['reports','any_therapy_rows','nonempty_literature_reference']]%1!=0).any(axis=1)).any():
        raise ValueError('Unique IDs and integer counts within n required')
    if not 150<=width_mm<=240:raise ValueError('Print width must be150-240mm')
    rows=list(d.display_cluster);aliases=display_map(rows,row_aliases)
    fig,ax=plt.subplots(figsize=(width_mm/25.4,max(3.5,len(rows)*.28+1.8)))
    fig.subplots_adjust(left=.27,right=.95,bottom=.17,top=.84)
    y=np.arange(len(d));missing=d.reports-d.any_therapy_rows
    ax.barh(y,d.any_therapy_rows,color=BLUE,height=.60)
    ax.barh(y,missing,left=d.any_therapy_rows,color=AMBER,hatch='///',edgecolor='white',lw=.4,height=.60)
    maximum=float(d.reports.max())
    for i,r in enumerate(d.itertuples()):
        ax.text(r.reports+maximum*.04,i,f'{int(r.any_therapy_rows)} / {int(r.reports)}',va='center',fontsize=8.5)
        ax.text(maximum*1.43,i,str(int(r.nonempty_literature_reference)),va='center',ha='center',fontsize=8.5)
    ax.set(xlim=(0,maximum*1.60),ylim=(len(d)-.5,-.5),xlabel='Reports in each overlapping cluster')
    ax.set_yticks(y,[aliases[r] for r in rows]);ax.tick_params(axis='y',length=0,labelsize=8.5)
    axis(ax);ax.grid(axis='x',lw=.4,color='#ECF0F2')
    ax.text(maximum*1.43,1.025,'LIT_REF',transform=ax.get_xaxis_transform(),ha='center',fontsize=8)
    fig.text(.27,.96,title,fontsize=11,weight='bold',va='top')
    fig.legend(handles=[Patch(facecolor=BLUE,label='Any therapy row'),Patch(facecolor=AMBER,hatch='///',label='No therapy row')],loc='upper left',bbox_to_anchor=(.25,.915),frameon=False,ncol=2,fontsize=8)
    fig.text(.27,.025,'Availability, not assigned target-drug duration. Reports are not patients; clusters overlap.\nNo risk estimate or confidence interval. All returned clusters and literature zeroes retained.',fontsize=8)
    return stamp(fig,data,'availability_counts',row_aliases=aliases,count_fields=['reports','any_therapy_rows','nonempty_literature_reference'],
                 zero='retained',width_mm=width_mm,palette={'recorded':BLUE,'absent':AMBER},inference='none')
