"""Original palette application plates from frozen panel tables.

This is a visual review surface: no article images, fits or inferred statistics.
All panel types can be used with different palettes without changing table values.
"""
import numpy as np
import pandas as pd
import textwrap
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.patches import Polygon, Ellipse, Rectangle, Circle, FancyArrowPatch
from matplotlib.lines import Line2D
from figure_core import checked,palette_check,stamp
from figure_reference import _new,_ax,_records,_types,_unique,_grid,_intervals
from figure_reference_palettes import get_palette

def plot_palette_plate(data,*,palette_name,panel_specs,size=(10,13),font_family='DejaVu Sans',layout='plate'):
    """C01–C07 original application examples. panel_specs records exact mappings.

    Requires the full composite table. Empty panels and unsupported types fail.
    No geographic data are downloaded by this renderer.
    """
    allowed=['point','line','bar','matrix','share','ellipse','density','box','radar','land','flow','schematic','arrow','annotation','volcano','row_tree','column_tree']
    _types(data,allowed); checked(data,['panel']); palettes=get_palette(palette_name,semantic='categorical'); colors=palettes['colors']
    if len(panel_specs)>8 or len(panel_specs)<1 or set(data.panel)!={s['id'] for s in panel_specs}: raise ValueError('Panel specification mismatch')
    if layout not in ('plate','panel') or (layout=='panel' and len(panel_specs)!=1): raise ValueError('Standalone mode requires exactly one panel')
    ncols=2; nrows=int(np.ceil(len(panel_specs)/2)); fig=_new(size)
    if layout=='plate':
        fig.text(.05,.935,palette_name+'  |  palette application reproduction',fontsize=16,weight='bold')
        for i,c in enumerate(colors):
            x=.05+i*.90/len(colors); fig.patches.append(Rectangle((x,.065),.88/len(colors),.035,fc=c,ec='white',transform=fig.transFigure))
            fig.text(x+.44/len(colors),.056,c,ha='center',fontsize=7)
    for k,spec in enumerate(panel_specs):
        panel=spec['id']; typ=spec['type']; src=data[data.panel==panel]; left=.08+(k%2)*.47; height=.74/nrows; bottom=.16+(nrows-1-k//2)*height
        # The standalone layout reserves a right-hand lane for all semantic guides.
        bounds=([.24,.18,.55,.55] if typ=='clustered_matrix' else [.15,.26,.61,.57] if typ=='bubble_matrix' else [.15,.27,.68,.50] if typ=='world_map' else [.15,.18,.61,.66] if typ in ('scatter','embedding','bubble','pca','donut','line','spectrum','bar','stacked','radar','volcano') else [.15,.18,.68,.66]) if layout=='panel' else spec.get('bounds',[left,bottom,.36,height*.72])
        if typ=='world_map':
            ax=fig.add_axes(bounds,projection='mollweide'); ax.tick_params(labelsize=6)
        elif typ=='radar': ax=fig.add_axes(bounds,projection='polar'); ax.tick_params(labelsize=6)
        else: ax=_ax(fig,bounds)
        ax.set_title(spec['title'],loc='left',fontsize=9,pad=6,weight='bold')
        supported_records={
            'scatter':['point','ellipse','line'],'embedding':['point','ellipse','line'],'flow_gate':['point','ellipse','line'],'bubble':['point','ellipse','line'],'pca':['point','ellipse','line'],
            'line':['line'],'spectrum':['line'],'bar':['bar'],'stacked':['bar'],'matrix':['matrix'],'clustered_matrix':['matrix','row_tree','column_tree'],'bubble_matrix':['matrix'],'donut':['share'],
            'violin':['box','density'],'box':['box'],'radar':['radar'],'world_map':['land','matrix'],'regional_map':['land','matrix'],'map_flows':['land','flow'],'volcano':['volcano'],'schematic':['schematic','arrow']}
        if typ not in supported_records or not set(src.record_type)<=set(supported_records[typ]+['annotation']): raise ValueError('Panel contains unsupported/unrendered record types')
        if typ in ('scatter','embedding','flow_gate','bubble','pca'):
            pts=_records(src,'point',['unit_id','group','x','y'],['x','y']); _unique(pts,['unit_id'])
            groups=list(pd.unique(pts.group)); pal=spec.get('group_palette',dict(zip(groups,colors)))
            palette_check(pts.group,pal)
            if typ=='bubble': checked(pts,['area'],['area'])
            if typ=='bubble' and (pts.area<0).any(): raise ValueError('Negative bubble area')
            for g in groups:
                sub=pts[pts.group==g]
                if typ=='flow_gate' or spec.get('continuous_color',False):
                    checked(sub,['color_value'],['color_value']); cmap=plt.get_cmap('turbo') if typ=='flow_gate' else LinearSegmentedColormap.from_list('plate',colors)
                    cmap=LinearSegmentedColormap.from_list('panel_continuous',spec['continuous_colors']) if 'continuous_colors' in spec else cmap
                    dots=ax.scatter(sub.x,sub.y,s=2 if typ=='flow_gate' else 5,c=sub.color_value,cmap=cmap,norm=Normalize(*spec['color_limits']),lw=0,alpha=.8)
                else: ax.scatter(sub.x,sub.y,s=sub.area*spec.get('area_scale',.3) if typ=='bubble' else 8,color=pal[g],alpha=.85,lw=.4,ec='white' if typ=='pca' else 'none',label=g)
            ell=_records(src,'ellipse',['group','x','y','width','height','angle'],['x','y','width','height','angle'],optional=True)
            for e in ell.itertuples():
                if e.width<=0 or e.height<=0 or e.group not in pal: raise ValueError('Invalid ellipse')
                ax.add_patch(Ellipse((e.x,e.y),e.width,e.height,angle=e.angle,fc=pal[e.group],alpha=.12,ec=pal[e.group],lw=1,ls='--'))
            fit=_records(src,'line',['group','x','y','lower','upper'],['x','y','lower','upper'],optional=True)
            if not fit.empty:
                _intervals(fit,'y')
                for g,sub in fit.groupby('group',sort=False):
                    sub=sub.sort_values('x'); ax.plot(sub.x,sub.y,color='#66717B',lw=1); ax.fill_between(sub.x,sub.lower,sub.upper,color='#BCC4C9',alpha=.3)
            if typ=='flow_gate':
                if (pts[['x','y']]<=0).any().any() or spec['gate_x']<=0 or spec['gate_y']<=0: raise ValueError('Log gate coordinates must be positive')
                ax.set_xscale('log'); ax.set_yscale('log'); ax.axvline(spec['gate_x'],color='#68737B',lw=.7); ax.axhline(spec['gate_y'],color='#68737B',lw=.7)
            elif not spec.get('continuous_color',False): ax.legend(loc='upper left' if layout=='panel' else 'best',bbox_to_anchor=(1.03,1) if layout=='panel' else None,frameon=False,fontsize=6,handlelength=1)
            if typ=='bubble':
                handles=[Line2D([],[],ls='',marker='o',color='#91989E',ms=np.sqrt(v*spec.get('area_scale',.3)),label=str(v)) for v in [50,100,200]]
                previous=ax.get_legend()
                if previous: ax.add_artist(previous)
                ax.legend(handles=handles,title=spec.get('area_label','Supplied area'),loc='upper left',bbox_to_anchor=(1.01,.55),frameon=False,fontsize=6,title_fontsize=6)
            if spec.get('continuous_color',False) or typ=='flow_gate': fig.colorbar(dots,ax=ax,fraction=.035,pad=.03,label=spec.get('color_label','Supplied density value')).ax.tick_params(labelsize=6)
        elif typ in ('line','spectrum'):
            d=_records(src,'line',['group','x','y','lower','upper'],['x','y','lower','upper']); _unique(d,['group','x']); _intervals(d,'y'); groups=list(pd.unique(d.group)); pal=spec.get('group_palette',dict(zip(groups,colors))); palette_check(d.group,pal)
            for g in groups:
                sub=d[d.group==g].sort_values('x'); ax.plot(sub.x,sub.y,color=pal[g],lw=1.4,marker=spec.get('markers',{}).get(g,'o' if len(sub)<30 else None),ms=3,label=g)
                if typ!='spectrum': ax.fill_between(sub.x,sub.lower,sub.upper,color=pal[g],alpha=.17)
            ax.legend(frameon=False,fontsize=6,ncols=1,loc='upper left' if layout=='panel' else 'best',bbox_to_anchor=(1.03,1) if layout=='panel' else None)
        elif typ in ('bar','stacked'):
            d=_records(src,'bar',['category','group','value','lower','upper'],['value','lower','upper']); _unique(d,['category','group']); _intervals(d)
            cats=list(pd.unique(d.category)); groups=list(pd.unique(d.group)); pal=spec.get('group_palette',dict(zip(groups,colors))); palette_check(d.group,pal)
            if len(d)!=len(cats)*len(groups): raise ValueError('Incomplete bars')
            if typ=='stacked' and not np.allclose(d.groupby('category').value.sum(),1): raise ValueError('Stacked fractions must sum to 1')
            bottom_values=np.zeros(len(cats)); width=.80/len(groups)
            for j,g in enumerate(groups):
                sub=d[d.group==g].set_index('category').reindex(cats)
                if typ=='bar': ax.bar(np.arange(len(cats))+(j-(len(groups)-1)/2)*width,sub.value,width=width,color=pal[g],yerr=[sub.value-sub.lower,sub.upper-sub.value],capsize=2,error_kw=dict(lw=.6),label=g)
                else: ax.bar(range(len(cats)),sub.value,bottom=bottom_values,width=.7,color=pal[g],label=g); bottom_values+=sub.value.to_numpy()
            ax.set_xticks(range(len(cats)),cats,fontsize=7); ax.legend(frameon=False,fontsize=6,ncols=1 if layout=='panel' else min(3,len(groups)),loc='upper left' if layout=='panel' else 'best',bbox_to_anchor=(1.03,1) if layout=='panel' else None)
        elif typ in ('matrix','bubble_matrix','clustered_matrix'):
            row_field=spec.get('row_field','row'); column_field=spec.get('column_field','column'); value_field=spec.get('value_field','value')
            d=_records(src,'matrix',[row_field,column_field,value_field],[value_field]); mat,rs,cs=_grid(d,row_field,column_field,value_field)
            row_order=spec.get('row_order'); column_order=spec.get('column_order')
            if row_order is not None:
                row_order=list(row_order)
                if len(row_order)!=len(set(row_order)) or set(row_order)!=set(rs): raise ValueError('row_order must cover every matrix row')
                rs=row_order; mat=mat.reindex(index=rs)
            if column_order is not None:
                column_order=list(column_order)
                if len(column_order)!=len(set(column_order)) or set(column_order)!=set(cs): raise ValueError('column_order must cover every matrix column')
                cs=column_order; mat=mat.reindex(columns=cs)
            lo,hi=spec['color_limits']
            if ((d[value_field]<lo)|(d[value_field]>hi)).any(): raise ValueError('Clipped matrix values')
            cmap=LinearSegmentedColormap.from_list('plate_signed',spec.get('continuous_colors',[spec.get('negative',colors[0]),spec.get('neutral','#FFFFFF'),spec.get('positive',colors[-1])]))
            if typ in ('matrix','clustered_matrix'): im=ax.imshow(mat,cmap=cmap,vmin=lo,vmax=hi,aspect='auto')
            else:
                im=ax.scatter([cs.index(c) for c in d[column_field]],[rs.index(r) for r in d[row_field]],s=d[value_field].abs()*180,c=d[value_field],cmap=cmap,vmin=lo,vmax=hi,lw=0); ax.set(xlim=(-.5,len(cs)-.5),ylim=(len(rs)-.5,-.5)); ax.grid(color='#E5E8EB',lw=.4); ax.set_axisbelow(True)
            row_aliases=spec.get('row_aliases',{}); column_aliases=spec.get('column_aliases',{})
            if set(row_aliases)!=set(rs) or set(column_aliases)!=set(cs):
                if row_aliases or column_aliases: raise ValueError('Matrix aliases must cover every displayed row and column')
            xlabels=[str(column_aliases.get(x,x)) for x in cs]; ylabels=[str(row_aliases.get(x,x)) for x in rs]
            if len(set(xlabels))!=len(xlabels) or len(set(ylabels))!=len(ylabels): raise ValueError('Matrix aliases must be unique')
            wrap_x=spec.get('column_label_wrap'); wrap_y=spec.get('row_label_wrap')
            if wrap_x is not None and (type(wrap_x) is not int or wrap_x<1): raise ValueError('column_label_wrap must be a positive integer or None')
            if wrap_y is not None and (type(wrap_y) is not int or wrap_y<1): raise ValueError('row_label_wrap must be a positive integer or None')
            xlabels=[textwrap.fill(x,wrap_x) if wrap_x else x for x in xlabels]; ylabels=[textwrap.fill(x,wrap_y) if wrap_y else x for x in ylabels]
            rotation=spec.get('label_rotation',90 if len(cs)>12 else 45)
            ax.set_xticks(range(len(cs)),xlabels,rotation=rotation,ha='right' if rotation else 'center',fontsize=spec.get('label_fontsize',6)); ax.set_yticks(range(len(rs)),ylabels,fontsize=spec.get('label_fontsize',6))
            cb=fig.colorbar(im,ax=ax,fraction=.035,pad=.04); cb.set_label(spec['color_label'],fontsize=7); cb.ax.tick_params(labelsize=6)
            if typ=='bubble_matrix' and layout=='panel':
                levels=[max(abs(lo),abs(hi))*f for f in (.2,.5,1)]
                handles=[Line2D([],[],ls='',marker='o',color='#91989E',ms=np.sqrt(v*180),label=f'{v:g}') for v in levels]
                fig.legend(handles=handles,title='Absolute value (area)',loc='lower center',bbox_to_anchor=(.45,.07),ncols=3,frameon=False,fontsize=7,title_fontsize=7)
            if typ=='clustered_matrix':
                pos=ax.get_position(); rt=_records(src,'row_tree',['x0','y0','x1','y1'],['x0','y0','x1','y1']); ct=_records(src,'column_tree',['x0','y0','x1','y1'],['x0','y0','x1','y1'])
                if ((rt[['y0','y1']]<-.5)|(rt[['y0','y1']]>len(rs)-.5)).any().any() or ((ct[['x0','x1']]<-.5)|(ct[['x0','x1']]>len(cs)-.5)).any().any(): raise ValueError('Supplied tree coordinates outside indexed matrix')
                lefttree=fig.add_axes([pos.x0-(.18 if layout=='panel' else .11),pos.y0,.08,pos.height]); toptree=fig.add_axes([pos.x0,pos.y1+.02,pos.width,.09])
                for r in rt.itertuples(): lefttree.plot([r.x0,r.x1],[r.y0,r.y1],color='#647582',lw=.8)
                for r in ct.itertuples(): toptree.plot([r.x0,r.x1],[r.y0,r.y1],color='#647582',lw=.8)
                lefttree.set_ylim(len(rs)-.5,-.5); lefttree.invert_xaxis(); toptree.set_xlim(-.5,len(cs)-.5); lefttree.axis('off'); toptree.axis('off'); ax.set_title('',loc='left'); toptree.set_title(spec['title'],loc='left',fontsize=9,pad=5)
        elif typ=='donut':
            d=_records(src,'share',['group','value'],['value']); _unique(d,['group'])
            if (d.value<0).any() or not np.isclose(d.value.sum(),1): raise ValueError('Invalid donut fractions')
            pal=spec.get('group_palette',dict(zip(d.group,colors))); palette_check(d.group,pal)
            ax.pie(d.value,colors=[pal[g] for g in d.group],startangle=90,wedgeprops=dict(width=.40,edgecolor='white'),autopct='%1.0f%%',textprops=dict(fontsize=7)); ax.text(0,0,'Total\n100%',ha='center',va='center',fontsize=9)
            ax.legend(handles=[Line2D([],[],ls='',marker='o',color=pal[g],label=g) for g in d.group],loc='upper left',bbox_to_anchor=(1,.9),frameon=False,fontsize=6)
        elif typ in ('violin','box'):
            boxes=_records(src,'box',['group','q1','median','q3','low','high'],['q1','median','q3','low','high']); _unique(boxes,['group']); groups=boxes.group.tolist(); pal=spec.get('group_palette',dict(zip(groups,colors))); palette_check(boxes.group,pal)
            if ((boxes.low>boxes.q1)|(boxes.q1>boxes['median'])|(boxes['median']>boxes.q3)|(boxes.q3>boxes.high)).any(): raise ValueError('Invalid box summaries')
            if typ=='violin':
                density=_records(src,'density',['group','coordinate','value'],['coordinate','value']); _unique(density,['group','coordinate'])
                if set(density.group)!=set(groups) or (density.value<0).any(): raise ValueError('Density mismatch')
                for i,g in enumerate(groups):
                    sub=density[density.group==g].sort_values('coordinate'); m=sub.value.max()
                    if m<=0: raise ValueError('Degenerate violin')
                    width=sub.value/m*.38; ax.fill_betweenx(sub.coordinate,i-width,i+width,color=pal[g],alpha=.8)
            stats=[dict(label=b.group,q1=b.q1,med=b.median,q3=b.q3,whislo=b.low,whishi=b.high,fliers=[]) for b in boxes.itertuples()]; art=ax.bxp(stats,positions=range(len(groups)),widths=.13 if typ=='violin' else .55,showfliers=False,patch_artist=True,medianprops={'color':'#384957','linewidth':1})
            for patch,g in zip(art['boxes'],groups): patch.set_facecolor('white' if typ=='violin' else pal[g]); patch.set_edgecolor('#65717A')
            ax.set_xticks(range(len(groups)),groups,fontsize=7)
        elif typ=='radar':
            d=_records(src,'radar',['group','category','value'],['value']); _unique(d,['group','category']); cats=list(pd.unique(d.category)); groups=list(pd.unique(d.group)); pal=spec.get('group_palette',dict(zip(groups,colors))); palette_check(d.group,pal)
            if len(d)!=len(cats)*len(groups): raise ValueError('Incomplete radar table')
            th=np.linspace(0,2*np.pi,len(cats),endpoint=False); ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
            for g in groups:
                vals=d[d.group==g].set_index('category').reindex(cats).value; ax.plot(np.r_[th,th[0]],np.r_[vals,vals.iloc[0]],color=pal[g],lw=1.2,label=g); ax.fill(np.r_[th,th[0]],np.r_[vals,vals.iloc[0]],color=pal[g],alpha=.10)
            ax.set_xticks(th,cats); ax.set_ylim(*spec['radial_limits'])
            ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(1.18,1),fontsize=6)
        elif typ in ('world_map','regional_map','map_flows'):
            land=_records(src,'land',['polygon_id','order','x','y'],['order','x','y']); _unique(land,['polygon_id','order'])
            if typ!='map_flows':
                d=_records(src,'matrix',['x','y','value'],['x','y','value']); mat,ys,xs=_grid(d,'y','x','value'); cm=LinearSegmentedColormap.from_list('map',spec['map_colors']); norm=Normalize(*spec['color_limits']); xx,yy=np.meshgrid(xs,ys)
                if typ=='world_map': xx=np.deg2rad(xx); yy=np.deg2rad(yy)
                im=ax.pcolormesh(xx,yy,mat.to_numpy(),cmap=cm,norm=norm,shading='auto',rasterized=True,antialiased=False); cb=fig.colorbar(im,ax=ax,orientation='horizontal' if typ=='world_map' else 'vertical',fraction=.045,pad=.10 if typ=='world_map' else .03,label=spec.get('color_label','Supplied value')); cb.ax.tick_params(labelsize=6)
            for _,poly in land.groupby('polygon_id',sort=False):
                xy=poly.sort_values('order')[['x','y']].to_numpy()
                if typ=='world_map': xy=np.deg2rad(xy)
                ax.add_patch(Polygon(xy,fc='#CACED1',ec='#9CA4AA',lw=.3))
            if typ=='map_flows':
                flow=_records(src,'flow',['path_id','order','x','y','value'],['order','x','y','value']); _unique(flow,['path_id','order']); norm=Normalize(*spec['color_limits']); cm=LinearSegmentedColormap.from_list('flow',spec.get('continuous_colors',colors))
                for _,sub in flow.groupby('path_id',sort=False):
                    sub=sub.sort_values('order'); ax.plot(sub.x,sub.y,color=cm(norm(sub.value.iloc[0])),lw=.5,alpha=.7); ax.scatter([sub.x.iloc[0],sub.x.iloc[-1]],[sub.y.iloc[0],sub.y.iloc[-1]],s=10,c=[sub.value.iloc[0]]*2,cmap=cm,norm=norm,lw=0)
                from matplotlib.cm import ScalarMappable
                fig.colorbar(ScalarMappable(norm=norm,cmap=cm),ax=ax,fraction=.035,pad=.04,label=spec.get('color_label','Supplied path value'))
            if typ!='world_map': ax.set(xlim=spec['x_limits'],ylim=spec['y_limits'])
            else: ax.grid(color='#AEB7BF',lw=.3,alpha=.4)
        elif typ=='volcano':
            d=_records(src,'volcano',['unit_id','x','y','group'],['x','y']); _unique(d,['unit_id']); pal=spec['group_palette']; palette_check(d.group,pal)
            for g,sub in d.groupby('group',sort=False): ax.scatter(sub.x,sub.y,color=pal[g],s=3,lw=0,label=g)
            ax.axhline(spec['threshold_y'],color='#8D969D',ls='--',lw=.6)
            for v in [-spec['threshold_x'],spec['threshold_x']]: ax.axvline(v,color='#8D969D',ls='--',lw=.6)
            ax.legend(frameon=False,fontsize=6,loc='upper left' if layout=='panel' else 'best',bbox_to_anchor=(1.03,1) if layout=='panel' else None)
        elif typ=='schematic':
            d=_records(src,'schematic',['object_id','group','x','y','radius'],['x','y','radius']); _unique(d,['object_id']); pal=spec['group_palette']; palette_check(d.group,pal)
            for o in d.itertuples():
                if o.radius<=0: raise ValueError('Invalid schematic radius')
                ax.add_patch(Circle((o.x,o.y),o.radius,fc=pal[o.group],ec='#8FADB9',lw=.6))
            arrows=_records(src,'arrow',['x0','y0','x1','y1'],['x0','y0','x1','y1'],optional=True)
            for a in arrows.itertuples(): ax.add_patch(FancyArrowPatch((a.x0,a.y0),(a.x1,a.y1),arrowstyle='->',mutation_scale=12,color=colors[-2],lw=1.3,connectionstyle='arc3,rad=.25'))
            ax.set(xlim=spec['x_limits'],ylim=spec['y_limits']); ax.set_aspect('equal'); ax.axis('off')
        else: raise ValueError('Unsupported panel type: '+typ)
        annotations=_records(src,'annotation',['x','y','text'],['x','y'],optional=True)
        for a in annotations.itertuples(): ax.text(a.x,a.y,a.text,fontsize=7,ha='center',va='bottom')
        if typ not in ('radar','donut','schematic','world_map'):
            ax.set_xlabel(spec.get('x_label',''),fontsize=8); ax.set_ylabel(spec.get('y_label',''),fontsize=8)
        if 'x_limits' in spec and typ not in ('world_map','radar'): ax.set_xlim(spec['x_limits'])
        if 'y_limits' in spec and typ not in ('world_map','radar'): ax.set_ylim(spec['y_limits'])
    for text in fig.findobj(match=lambda t:isinstance(t,plt.Text)): text.set_fontfamily(font_family)
    return stamp(fig,data,'reference_palette_plate',palette=palettes,panel_specs=panel_specs,analysis='none; all panel values supplied',font_family=font_family,layout=layout,adapter_version=2)

def plot_palette_panel(data,*,palette_name,panel_spec,size=(6.7,5.1),font_family='Arial'):
    """One reusable scientific panel. No palette poster or automatic composition."""
    return plot_palette_plate(data,palette_name=palette_name,panel_specs=[panel_spec],size=size,font_family=font_family,layout='panel')
