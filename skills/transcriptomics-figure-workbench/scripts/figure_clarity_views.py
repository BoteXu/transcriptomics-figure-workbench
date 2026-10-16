"""Readable frozen-result views; no fitting, testing, binning or model inference."""
import copy
import hashlib
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors, ticker
from matplotlib.patches import Rectangle, Patch
from figure_core import checked
from figure_editorial import _axis, _finish, _order, validate_contract
from figure_package_styles import _bounds, _cmap, _flat_axis
from project_theme import group_palette

INK='#243449'; MUTED='#657587'; TEAL='#218C8D'; CORAL='#C96068'; GRID='#E7EBEF'


def _canvas(t,o,height=4.6):
    with plt.rc_context({'font.family':t['font_family'],'pdf.fonttype':42,'svg.fonttype':'none'}):
        fig=plt.figure(figsize=(6.8,height),facecolor='white')
    fig._editorial_font=t['font_family'];fig._clarity_view=o['_view']
    fig.text(.09,.965,o['title'],fontsize=10.8,color=INK,weight='medium',va='top')
    fig.text(.09,.915,o['subtitle'],fontsize=8,color=MUTED,va='top')
    badge=fig.text(.99,.995,'',fontsize=6.2,ha='right',va='top')
    fig._software_band_artists=[badge]
    return fig


def _note(fig,text,y=.025):
    fig._clarity_notes=getattr(fig,'_clarity_notes',[])+[text]
    caption={
      'profiles':'All vertices retained / original coordinate direction and offsets',
      'contribution':'Colour: supplied feature value / vertical jitter separates marks only',
      'shares':'Supplied shares on one common scale / exact values in the accompanying table',
      'effects':'Teal: stored effects / coral: supplied summary / bars: supplied intervals',
      'membership':'Teal: declared links / strip: member effects / right: supplied term summaries',
      'pixels':'Supplied physical grids and u/v orientation / procedural demonstration, not clinical anatomy',
      'estimation':'Raw observations and supplied effect distribution use separate scales; no new inference',
      'decision':'Stored threshold and benefit vertices / dashed: supplied baseline strategies',
      'precision_recall':'Stored recall and precision vertices / no AP or AUC estimation',
      'rank_stability':'Supplied rank spans, not confidence intervals / NA: unassessed'
    }[fig._clarity_view]
    fig.text(.09,y,'\n'.join(textwrap.wrap(caption,100)),fontsize=8,color=MUTED,va='bottom')


def _jitter(ids,span=.16):
    """Identity-stable row separation, unrelated to any measured quantity."""
    return np.array([(int(hashlib.sha256(str(k).encode()).hexdigest()[:8],16)/0xffffffff-.5)*2*span for k in ids])


def _unique(d,keys):
    if d.duplicated(keys).any():raise ValueError('Duplicate display identity: '+str(keys))


def _profiles(d,t,o):
    d=checked(d,['group','x','y'],['x','y']);names=_order(d.group,o['group_order']);_unique(d,['group','x'])
    if not 1<=len(names)<=8:raise ValueError('Use one to eight profiles')
    if len(o['x_limits'])!=2 or o['x_limits'][0]==o['x_limits'][1]:raise ValueError('Two distinct x limits required')
    _bounds(d.x,sorted(o['x_limits']));_bounds(d.y,o['y_limits'])
    pal=group_palette(t,names);fig=_canvas(t,o,4.8);ax=_axis(fig,[.12,.19,.70,.61]);_flat_axis(ax,'y')
    for name in names:
        q=d[d.group==name];dx=np.diff(q.x)
        if len(q)<2 or not ((dx>0).all() or (dx<0).all()):raise ValueError('Preserve monotonic stored coordinates')
        ax.plot(q.x,q.y,color=pal[name],lw=1.25)
        ax.scatter(q.x,q.y,color=pal[name],s=1.8,linewidths=0,zorder=3)
        ax.annotate(name,(q.x.iloc[-1],q.y.iloc[-1]),xytext=(8,0),textcoords='offset points',fontsize=8.5,color=pal[name],va='center')
    ax.set(xlim=o['x_limits'],ylim=o['y_limits'],xlabel=o['x_label'],ylabel=o['y_label'])
    _note(fig,'Every supplied vertex retained. Fine markers and direct labels; no baseline shift, rescaling or smoothing.')
    return fig


def _contribution(d,t,o):
    d=checked(d,['unit_id','class','feature','contribution','feature_value'],['contribution','feature_value'])
    names=_order(d.feature,o['feature_order']);_unique(d,['class','feature','unit_id'])
    if set(d['class'])!={o['class_label']} or len(names)>24:raise ValueError('Select one class, preserving all its features')
    norm=_bounds(d.feature_value,o['value_limits']);_bounds(d.contribution,o['effect_limits'])
    feature_cmap=colors.LinearSegmentedColormap.from_list('visible_feature_values',[t['continuous']['diverging'][0],'#9AAEB8',t['continuous']['diverging'][-1]])
    fig=_canvas(t,o,max(5.0,2.0+.23*len(names)));ax=_axis(fig,[.25,.18,.54,.65]);_flat_axis(ax,'x')
    for i,name in enumerate(names):
        q=d[d.feature==name]
        if i%2==0:ax.axhspan(i-.5,i+.5,color='#F5F7F9',zorder=0)
        sc=ax.scatter(q.contribution,i+_jitter(q.unit_id),c=q.feature_value,norm=norm,cmap=feature_cmap,s=7,alpha=.85,linewidths=0,rasterized=True)
    ax.axvline(0,color='#97A6B2',lw=.8);ax.set(xlim=o['effect_limits'],ylim=(len(names)-.5,-.5),xlabel=o['effect_label'])
    ax.set_yticks(range(len(names)),names,fontsize=8);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    cb=fig.colorbar(sc,cax=fig.add_axes([.85,.43,.018,.22]));cb.set_label(o['value_label'],fontsize=8);cb.ax.tick_params(labelsize=8)
    _note(fig,'All selected-class instances retained; row jitter is display-only. No SHAP computation, ranking, feature selection or causal attribution.')
    return fig


def _shares(d,t,o):
    d=checked(d,['class','feature','value'],['value']);rr=_order(d.feature,o['feature_order']);cc=_order(d['class'],o['class_order']);_unique(d,['class','feature'])
    if len(d)!=len(rr)*len(cc) or len(rr)>24 or len(cc)>8:raise ValueError('Complete bounded share matrix required')
    norm=_bounds(d.value,o['share_limits']);fig=_canvas(t,o,max(4.7,2.1+.29*len(rr)))
    ax=fig.add_axes([.28,.23,.47,.53]);ax.set(xlim=(-.5,len(cc)-.5),ylim=(len(rr)-.5,-.5));lookup=d.set_index(['feature','class'])
    for i,r in enumerate(rr):
        for j,c in enumerate(cc):
            v=lookup.loc[r,c].value;ax.add_patch(Rectangle((j-.5,i-.5),1,1,fc=_cmap(t,False)(norm(v)),ec='white',lw=1.5));ax.text(j,i,f'{v:.3f}',ha='center',va='center',fontsize=8,color='white' if norm(v)>.64 else INK)
    ax.set_xticks(range(len(cc)),cc,fontsize=8);ax.set_yticks(range(len(rr)),rr,fontsize=8);ax.tick_params(length=0,pad=7)
    for s in ax.spines.values():s.set_visible(False)
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=_cmap(t,False)),cax=fig.add_axes([.82,.35,.018,.25]));cb.set_label('Supplied share',fontsize=8);cb.ax.tick_params(labelsize=8)
    _note(fig,o['denominator']+'. Upstream shares retained; not recalculated from contribution points. Text rounded; exact values in TSV.')
    return fig


def _effects(d,t,o):
    d=checked(d,['record_type','panel','row','value'],['value']);rr=_order(d.row,o['row_order']);pp=_order(d.panel,o['panel_order'])
    if set(d.record_type)!={'effect','summary'} or len(pp)!=2 or not 1<=len(rr)<=30:raise ValueError('Two panels with summaries and instances required')
    s=checked(d[d.record_type=='summary'],['lower','upper','p','count_text'],['lower','upper','p']);e=checked(d[d.record_type=='effect'],['effect_id'])
    _unique(s,['panel','row']);_unique(e,['panel','row','effect_id'])
    if len(s)!=2*len(rr) or set(zip(s.panel,s.row))!={(p,r) for p in pp for r in rr}:raise ValueError('Complete unique summary grid required')
    if ((s.lower>s.value)|(s.value>s.upper)|(s.p<0)|(s.p>1)).any():raise ValueError('Invalid intervals or raw probabilities')
    _bounds(np.r_[d.value,s.lower,s.upper],o['limits']);fig=_canvas(t,o,max(6,2.1+.26*len(rr)));axes=[]
    for k,p in enumerate(pp):
        ax=_axis(fig,[.21+k*.38,.18,.23,.64]);axes.append(ax);_flat_axis(ax,'x');ax.set(xlim=o['limits'],ylim=(len(rr)-.5,-.5),xlabel=o['panel_labels'][p]);ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
        ax.set_yticks(range(len(rr)),rr if k==0 else ['']*len(rr),fontsize=8);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False);ax.axvline(0,color='#A1AFBB',lw=.7,ls=(0,(3,3)))
        ax.set_title(p,loc='left',fontsize=9,pad=24,color=INK)
        ax.text(1.05,1.025,'Count / raw p',transform=ax.transAxes,fontsize=8,ha='left')
        for i,r in enumerate(rr):
            if i%2==0:ax.axhspan(i-.5,i+.5,color='#F5F7F9',zorder=0)
            q=e[(e.panel==p)&(e.row==r)];z=s[(s.panel==p)&(s.row==r)].iloc[0]
            ax.scatter(q.value,i+_jitter(q.effect_id,.14),s=3,color=TEAL,alpha=.45,linewidths=0,rasterized=True,zorder=2)
            ax.hlines(i,z.lower,z.upper,color=INK,lw=1.2,zorder=3);ax.scatter(z.value,i,s=17,color=CORAL,edgecolor='white',lw=.5,zorder=4)
            ax.text(1.05,i,str(z.count_text)+' / '+f'{z.p:.3g}',transform=ax.get_yaxis_transform(),fontsize=8,va='center')
    _note(fig,o['interval_definition']+'. '+o['count_definition']+'. All instance values and summary bounds retained; row jitter is display-only. No pooling or new significance tests.')
    return fig


def _membership(d,t,o):
    d=checked(d,['record_type']);m=checked(d[d.record_type=='member'],['member_id','effect'],['effect']);q=checked(d[d.record_type=='term'],['term_id','label','block','ratio','padj','count'],['ratio','padj','count']);e=checked(d[d.record_type=='link'],['member_id','term_id'])
    if set(d.record_type)!={'member','term','link'}:raise ValueError('Unknown membership record type')
    mm=_order(m.member_id,o['member_order']);tt=_order(q.term_id,o['term_order']);_unique(m,['member_id']);_unique(q,['term_id']);_unique(e,['member_id','term_id'])
    if not 1<=len(mm)<=30 or not 1<=len(tt)<=16 or not set(e.member_id)<=set(mm) or not set(e.term_id)<=set(tt):raise ValueError('Bounded declared membership identities required')
    if ((q.ratio<0)|(q.ratio>1)|(q.padj<=0)|(q.padj>1)|(q['count']<0)|(q['count']%1!=0)).any():raise ValueError('Invalid term summaries')
    norm=_bounds(m.effect,o['effect_limits'],True);fig=_canvas(t,o,max(5.2,2.6+.25*len(tt)));ax=fig.add_axes([.32,.34,.40,.42]);ax.set(xlim=(-.5,len(mm)-.5),ylim=(len(tt)-.5,-.5));lookup=q.set_index('term_id');links=set(zip(e.member_id,e.term_id))
    for i,r in enumerate(tt):
        for j,c in enumerate(mm):ax.add_patch(Rectangle((j-.5,i-.5),1,1,fc=TEAL if (c,r) in links else '#F2F5F7',ec='white',lw=1))
        z=lookup.loc[r];ax.text(-.10,i,z.label,transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=8)
        ax.text(1.05,i,f'{z.block}  {z.ratio:.2f}  {int(z["count"])}  {z.padj:.3g}',transform=ax.get_yaxis_transform(),va='center',fontsize=8)
    ax.text(1.05,1.04,'Block / ratio / n / FDR',transform=ax.transAxes,fontsize=8)
    ax.set_xticks(range(len(mm)),mm,rotation=90,fontsize=8);ax.set_yticks([]);ax.tick_params(length=0)
    for s in ax.spines.values():s.set_visible(False)
    strip=fig.add_axes([.32,.23,.40,.04]);vals=m.set_index('member_id').loc[mm].effect.to_numpy();strip.imshow(vals[None,:],cmap=_cmap(t),norm=norm,aspect='auto',interpolation='nearest');strip.set_axis_off()
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=_cmap(t)),cax=fig.add_axes([.32,.17,.40,.018]),orientation='horizontal');cb.ax.tick_params(labelsize=8);cb.set_label('Supplied member effect',fontsize=8)
    _note(fig,o['denominator']+'. Teal = declared link; grey = no declared link in this complete input. No pruning, enrichment or clustering.')
    return fig


def _pixels(d,t,o):
    fields=['intensity','label_id'] if o['mode']=='slices' else ['fixed','registered']
    d=checked(d,['u','v']+fields,['u','v']+fields)
    if o['mode'] not in ['slices','registration']:raise ValueError('Use slices or registration')
    if o['mode']=='slices':
        checked(d,['view']);names=_order(d.view,o['view_order'])
        if len(names)!=3:raise ValueError('Three declared slice views required')
        if (d.label_id%1!=0).any() or (d.label_id<0).any() or set(d.label_id.astype(int))-{0}-set(map(int,o['label_names'])):raise ValueError('Exact nonnegative label key required')
        _bounds(d.intensity,o['intensity_limits'])
    else:
        names=['Fixed','Registered','Checkerboard','Registered minus fixed'];_bounds(np.r_[d.fixed,d.registered],o['intensity_limits'])
        if type(o['tile_pixels']) is not int or o['tile_pixels']<1:raise ValueError('Positive checkerboard tile size required')
    fig=_canvas(t,o,6.8);axes=[];last=None;intensity=None
    for i,name in enumerate(names):
        ax=_axis(fig,[.12+(i%2)*.41,.57-(i//2)*.33,.30,.23]);axes.append(ax)
        q=d[d.view==name] if o['mode']=='slices' else d;_unique(q,['u','v']);xx=np.sort(q.u.unique());yy=np.sort(q.v.unique())
        if len(xx)<2 or len(yy)<2 or len(q)!=len(xx)*len(yy) or not np.allclose(np.diff(xx),np.diff(xx)[0]) or not np.allclose(np.diff(yy),np.diff(yy)[0]):raise ValueError('Complete regular physical pixel grid required')
        table=q.set_index(['v','u']);grid=lambda f:np.array([[table.loc[y,x][f] for x in xx] for y in yy]);extent=(xx[0]-(xx[1]-xx[0])/2,xx[-1]+(xx[1]-xx[0])/2,yy[0]-(yy[1]-yy[0])/2,yy[-1]+(yy[1]-yy[0])/2)
        values=grid('intensity' if o['mode']=='slices' else 'fixed');cm='gray';lo,hi=o['intensity_limits']
        if o['mode']=='registration':
            b=grid('registered')
            if i==1:values=b
            elif i==2:
                iy,ix=np.indices(values.shape);values=np.where(((ix//o['tile_pixels']+iy//o['tile_pixels'])%2)==0,values,b)
            elif i==3:
                values=b-values;_bounds(values.ravel(),o['difference_limits'],True);lo,hi=o['difference_limits'];cm=_cmap(t)
        sc=ax.imshow(values,origin='lower',extent=extent,cmap=cm,vmin=lo,vmax=hi,interpolation='nearest',aspect='equal')
        if i==0:intensity=sc
        last=sc
        if o['mode']=='slices':
            labels=grid('label_id');rgba=np.zeros(labels.shape+(4,));pal=group_palette(t,list(o['label_names'].values()))
            for key,label in o['label_names'].items():rgba[labels==int(key)]=colors.to_rgba(pal[label],.58)
            ax.imshow(rgba,origin='lower',extent=extent,interpolation='nearest',aspect='equal')
        ax.set_title(name,loc='left',fontsize=9,pad=8,color=INK);ax.set(xlabel=o['coordinate_labels'][0],ylabel=o['coordinate_labels'][1]);ax.xaxis.set_major_locator(ticker.MaxNLocator(4));ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    if o['mode']=='slices':
        guide=fig.add_axes([.56,.20,.30,.23]);guide.axis('off');guide.legend(handles=[Patch(fc=pal[label],label=label) for label in o['label_names'].values()],loc='upper left',frameon=False,fontsize=8)
        guide.text(0,.28,'Supplied label overlays\nNo segmentation / no resampling',fontsize=8,color=MUTED)
    cb=fig.colorbar(intensity,cax=fig.add_axes([.12,.115,.28,.014]),orientation='horizontal');cb.set_label('Supplied intensity',fontsize=8);cb.ax.tick_params(labelsize=8)
    if o['mode']=='registration':
        cb=fig.colorbar(last,cax=fig.add_axes([.54,.115,.28,.014]),orientation='horizontal');cb.set_label('Registered minus fixed',fontsize=8);cb.ax.tick_params(labelsize=8)
    _note(fig,o['orientation_definition']+' Pixel centres and intensity ranges retained. No registration, interpolation or diagnostic inference.',y=.006)
    return fig


def _estimation(d,t,o):
    d=checked(d,['record_type']);p=checked(d[d.record_type=='observation'],['unit_id','group','value'],['value']);s=checked(d[d.record_type=='summary'],['value','lower','upper'],['value','lower','upper']);z=checked(d[d.record_type=='density'],['x','density'],['x','density'])
    if set(d.record_type)!={'observation','summary','density'} or len(s)!=1 or len(z)<3 or len(p)>1000:raise ValueError('Observations, one supplied effect and density coordinates required')
    groups=_order(p.group,o['group_order']);_unique(p,['group','unit_id'])
    if len(groups)!=2 or (np.diff(z.x)<=0).any() or (z.density<0).any() or z.density.max()<=0 or not s.lower.iloc[0]<=s.value.iloc[0]<=s.upper.iloc[0]:raise ValueError('Invalid estimation channels')
    _bounds(p.value,o['value_limits']);_bounds(np.r_[z.x,s.lower,s.upper],o['effect_limits']);pal=group_palette(t,groups);fig=_canvas(t,o,4.9)
    ax=_axis(fig,[.13,.23,.36,.55]);_flat_axis(ax,'y')
    for i,name in enumerate(groups):
        q=p[p.group==name];ax.scatter(i+_jitter(q.unit_id,.12),q.value,s=19,c=pal[name],alpha=.8,edgecolors='white',lw=.5)
    ax.set(xlim=(-.5,1.5),ylim=o['value_limits'],ylabel=o['value_label']);ax.set_xticks([0,1],groups,fontsize=8)
    bx=_axis(fig,[.69,.23,.19,.55]);_flat_axis(bx,'y');q=s.iloc[0];bx.fill_betweenx(z.x,0,z.density/z.density.max()*.4,color=TEAL,alpha=.25);bx.plot(z.density/z.density.max()*.4,z.x,color=TEAL,lw=1);bx.vlines(-.08,q.lower,q.upper,color=INK,lw=1.5);bx.scatter(-.08,q.value,c=CORAL,s=30,zorder=4);bx.axhline(0,color='#A1AFBB',lw=.7,ls=(0,(3,3)));bx.set(xlim=(-.2,.48),ylim=o['effect_limits'],ylabel=o['effect_label']);bx.set_xticks([]);bx.spines['bottom'].set_visible(False)
    _note(fig,o['interval_definition']+'. Independent groups; raw units are not connected. Density and effect supplied upstream; no bootstrap, KDE, testing or effect estimation.')
    return fig


def _performance(d,t,o):
    d=checked(d,['series','x','value'],['x','value']);names=_order(d.series,o['series_order']);_unique(d,['series','x'])
    if not 1<=len(names)<=6:raise ValueError('Use one to six complete curves')
    _bounds(d.x,o['x_limits']);_bounds(d.value,o['y_limits']);
    if ((d.x<0)|(d.x>1)).any():raise ValueError('Probability positions must lie in zero to one')
    pal=group_palette(t,names);fig=_canvas(t,o,4.8);ax=_axis(fig,[.13,.22,.58,.56]);_flat_axis(ax,'y')
    for name in names:
        q=d[d.series==name]
        if len(q)<2 or (np.diff(q.x)<=0).any():raise ValueError('Preserve increasing supplied curve positions')
        baseline=name in o.get('reference_series',[])
        ax.plot(q.x,q.value,lw=1.25 if baseline else 1.65,color='#77838E' if baseline else pal[name],ls='--' if baseline else '-',label=name)
        ax.scatter(q.x,q.value,s=4 if baseline else 6,color='#77838E' if baseline else pal[name],linewidths=0)
    ax.set(xlim=o['x_limits'],ylim=o['y_limits'],xlabel=o['x_label'],ylabel=o['y_label']);ax.legend(loc='upper left',bbox_to_anchor=(1.03,1),frameon=False,fontsize=8)
    _note(fig,o['evaluation_definition']+'. Line joins are display-only. No threshold selection, benefit, AP or AUC calculation.')
    return fig


def _ranks(d,t,o):
    d=checked(d,['feature','cohort','status']);rr=_order(d.feature,o['feature_order']);cc=_order(d.cohort,o['cohort_order']);_unique(d,['feature','cohort'])
    if len(d)!=len(rr)*len(cc) or len(rr)>20 or not 1<=len(cc)<=4 or not set(d.status)<={'reported','unassessed'}:raise ValueError('Complete bounded rank grid with explicit unassessed states required')
    z=checked(d[d.status=='reported'],['rank','lower_rank','upper_rank'],['rank','lower_rank','upper_rank'])
    if ((z.lower_rank>z['rank'])|(z['rank']>z.upper_rank)).any() or d.loc[d.status=='unassessed',['rank','lower_rank','upper_rank']].notna().any().any():raise ValueError('Invalid rank spans or fabricated missing ranks')
    _bounds(np.r_[z['rank'],z.lower_rank,z.upper_rank],o['rank_limits']);fig=_canvas(t,o,max(4.8,2+.29*len(rr)));pal=group_palette(t,cc)
    for k,c in enumerate(cc):
        ax=_axis(fig,[.24+k*.68/len(cc),.24,.55/len(cc),.53]);_flat_axis(ax,'x');ax.set(xlim=o['rank_limits'],ylim=(len(rr)-.5,-.5),xlabel='Supplied rank');ax.set_yticks(range(len(rr)),rr if k==0 else ['']*len(rr),fontsize=8);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False);ax.xaxis.set_major_locator(ticker.MaxNLocator(3,integer=True));ax.set_title(c,fontsize=9,loc='left',pad=10)
        lo,hi=int(np.ceil(o['rank_limits'][0])),int(np.floor(o['rank_limits'][1]));ax.set_xticks(sorted(set([lo,(lo+hi)//2,hi])))
        for i,r in enumerate(rr):
            q=d[(d.cohort==c)&(d.feature==r)].iloc[0]
            if i%2==0:ax.axhspan(i-.5,i+.5,color='#F5F7F9',zorder=0)
            if q.status=='unassessed':ax.text(.5,i,'NA',transform=ax.get_yaxis_transform(),ha='center',va='center',fontsize=8,color=MUTED)
            else:ax.hlines(i,q.lower_rank,q.upper_rank,color=pal[c],lw=1.4);ax.scatter(q['rank'],i,c=pal[c],s=23,zorder=3)
    _note(fig,o['interval_definition']+'. NA means unassessed, not last rank. Exact supplied ranks and feature order retained; no re-ranking, pooling or stability estimation.')
    return fig


def plot_clarity_views(data,theme,*,view,contract,options):
    """Fine profiles, readable dense panels, imaging and supplied evaluation views."""
    validate_contract(contract)
    base='title subtitle '
    routes={
        'profiles':(_profiles,'group_order x_limits y_limits x_label y_label'),
        'contribution':(_contribution,'class_label feature_order value_limits effect_limits effect_label value_label'),
        'shares':(_shares,'class_order feature_order share_limits denominator'),
        'effects':(_effects,'row_order panel_order panel_labels limits interval_definition count_definition'),
        'membership':(_membership,'member_order term_order effect_limits denominator'),
        'pixels':(_pixels,'mode view_order label_names intensity_limits difference_limits tile_pixels coordinate_labels orientation_definition'),
        'estimation':(_estimation,'group_order value_limits effect_limits value_label effect_label interval_definition'),
        'rank_stability':(_ranks,'feature_order cohort_order rank_limits interval_definition'),
        'decision':(_performance,'series_order reference_series x_limits y_limits x_label y_label evaluation_definition'),
        'precision_recall':(_performance,'series_order x_limits y_limits x_label y_label evaluation_definition')}
    if view not in routes or not isinstance(options,dict) or set(options)!=set((base+routes[view][1]).split()):raise ValueError('Use exact documented clarity-view options')
    for key in ['title','subtitle']:
        if not isinstance(options[key],str) or not options[key].strip():raise ValueError('Declare title and subtitle')
    previous=set(plt.get_fignums())
    try:
        if view=='decision' and (not isinstance(options['reference_series'],list) or len(options['reference_series'])!=2 or len(set(options['reference_series']))!=2 or not set(options['reference_series'])<=set(options['series_order'])):raise ValueError('Declare both supplied baseline strategies')
        if view=='precision_recall' and ((data.value<0)|(data.value>1)).any():raise ValueError('Precision must lie in zero to one')
        selected=copy.deepcopy(options);selected['_view']=view
        fig=routes[view][0](data,theme,selected);fig=_finish(fig,data,'clarity_'+view,contract,options,theme)
        fig._omics_spec['display_notes']=fig._clarity_notes
        return fig
    except Exception:
        for n in set(plt.get_fignums())-previous:plt.close(n)
        raise
