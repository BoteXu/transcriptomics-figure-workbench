# Original layouts for frozen tables. Source figure_core.R first.
theme_publication <- function() {
  theme_omics(10) + ggplot2::theme(axis.line=ggplot2::element_line(colour='#AEB5BC',linewidth=.3),
    axis.ticks=ggplot2::element_line(colour='#AEB5BC',linewidth=.3),
    plot.title=ggplot2::element_text(face='plain',size=12),
    legend.position='bottom',legend.title=ggplot2::element_blank())
}
plot_publication_curve <- function(d,palette,curve_type,labels,title='',prevalence=NULL) {
  original <- d; cols_ok(d,c('model','x','y'));finite_ok(d,c('x','y'));palette_ok(d$model,palette)
  if(!curve_type %in% c('ROC','PR') || any(as.matrix(d[c('x','y')])<0|as.matrix(d[c('x','y')])>1)) stop('Invalid curve')
  if(!setequal(unique(d$model),names(labels))) stop('Supply one frozen label per model')
  if(curve_type=='PR' && (is.null(prevalence)||length(prevalence)!=1||!is.finite(prevalence)||prevalence<=0||prevalence>=1)) stop('PR needs prevalence')
  for(m in unique(d$model)) {
    dx <- diff(d$x[d$model==m]); if((curve_type=='ROC'&&any(dx<0))||(any(dx<0)&&any(dx>0)))stop('Non-monotonic threshold x order')
  }
  model_order<-unique(d$model)
  paths<-lapply(model_order,function(m){
    z<-d[d$model==m,];if(nrow(z)<2)return(z)
    out<-z[1,,drop=FALSE]
    for(i in seq_len(nrow(z)-1)) {
      bridge<-z[i,,drop=FALSE]
      post<-curve_type=='ROC'||any(diff(z$x)<0)
      if(post)bridge$x<-z$x[i+1] else bridge$y<-z$y[i+1]
      out<-rbind(out,bridge,z[i+1,,drop=FALSE])
    };out
  })
  d<-do.call(rbind,paths);d$model<-factor(d$model,levels=model_order);need('ggplot2')
  # geom_step sorts by x; explicit vertices and geom_path preserve PR threshold order.
  p<-ggplot2::ggplot(d,ggplot2::aes(x,y,colour=model,linetype=model,group=model))+
    ggplot2::geom_path(linewidth=.7)+
    ggplot2::scale_colour_manual(values=palette,labels=labels,drop=FALSE)+
    ggplot2::scale_linetype_manual(values=rep(c('solid','dashed','dotdash','dotted'),length.out=length(unique(d$model))),labels=labels)+
    ggplot2::coord_fixed(xlim=c(0,1),ylim=c(0,1),clip='off')+theme_publication()+
    ggplot2::labs(x=if(curve_type=='ROC')'False-positive rate' else 'Recall',y=if(curve_type=='ROC')'True-positive rate' else 'Precision',title=title)+
    ggplot2::guides(colour=ggplot2::guide_legend(nrow=2),linetype=ggplot2::guide_legend(nrow=2))
  if(curve_type=='ROC')p<-p+ggplot2::geom_abline(slope=1,intercept=0,colour='#B8BEC5',linetype=2,linewidth=.35)
  else p<-p+ggplot2::geom_hline(yintercept=prevalence,colour='#B8BEC5',linetype=2,linewidth=.35)
  stamp(p,original,'publication_curve',curve_type=curve_type,palette=as.list(palette),labels=as.list(labels),step='ROC post; PR ascending pre or descending post',prevalence=prevalence)
}
plot_aligned_matrix <- function(d,value_label,limits,signed=TRUE,center=0,geometry='tile',block_palette=NULL,count_label='Supplied count',title='') {
  original<-d;cols_ok(d,c('feature','sample','value'));finite_ok(d,'value')
  if(anyDuplicated(d[c('feature','sample')])||nrow(d)!=length(unique(d$feature))*length(unique(d$sample)))stop('Complete matrix required')
  if(length(limits)!=2||any(!is.finite(limits))||limits[1]>=limits[2]||min(d$value)<limits[1]||max(d$value)>limits[2])stop('Limits must include all values')
  if(!geometry %in% c('tile','bubble')||(signed&&!(limits[1]<center&&center<limits[2])))stop('Invalid scale/geometry')
  for(field in intersect(c('feature_block','row_count'),names(d))) {
    cols_ok(d,field);if(any(vapply(split(d[[field]],d$feature),function(z)length(unique(z)),numeric(1))!=1))stop('Row annotation mismatch')
  }
  has_count<-'row_count'%in%names(d);has_block<-'feature_block'%in%names(d)
  if(has_count){finite_ok(d,'row_count');if(any(d$row_count<0|d$row_count%%1!=0))stop('Invalid count')}
  if(has_block)palette_ok(d$feature_block,block_palette)
  rows<-unique(d$feature);cols<-unique(d$sample);d$feature<-factor(d$feature,levels=rev(rows));d$sample<-factor(d$sample,levels=cols)
  need('ggplot2');need('patchwork')
  p<-ggplot2::ggplot(d,ggplot2::aes(sample,feature))
  if(geometry=='tile')p<-p+ggplot2::geom_tile(ggplot2::aes(fill=value),colour='white',linewidth=.25)
  else p<-p+ggplot2::geom_point(ggplot2::aes(fill=value),shape=21,size=4,stroke=0)
  if(signed)p<-p+ggplot2::scale_fill_gradient2(low='#7562A5',mid='#FAF8F3',high='#E98B2A',midpoint=center,limits=limits)
  else p<-p+ggplot2::scale_fill_gradientn(colours=c('#FAF8F3','#AFD6CE','#258D85'),limits=limits)
  p<-p+theme_publication()+ggplot2::theme(axis.line=ggplot2::element_blank(),axis.ticks=ggplot2::element_blank(),axis.text.x=ggplot2::element_text(angle=35,hjust=1),legend.title=ggplot2::element_text(size=9))+ggplot2::labs(x=NULL,y=NULL,fill=value_label)
  parts<-list();widths<-numeric();side<-d[!duplicated(d$feature),]
  if(has_block) {
    strip<-ggplot2::ggplot(side,ggplot2::aes(1,feature,fill=feature_block))+ggplot2::geom_tile()+ggplot2::scale_fill_manual(values=block_palette)+ggplot2::theme_void()+ggplot2::guides(fill='none')
    parts<-c(parts,list(strip));widths<-c(widths,.08)
  }
  parts<-c(parts,list(p));widths<-c(widths,max(2,length(cols)*.5))
  if(has_count) {
    upper<-max(side$row_count,1)
    bars<-ggplot2::ggplot(side,ggplot2::aes(row_count,feature))+ggplot2::geom_col(fill='#BEC5CC',width=.72)+
      ggplot2::geom_text(ggplot2::aes(label=row_count),hjust=-.15,size=2.8,colour='#58626D')+ggplot2::scale_x_continuous(limits=c(0,upper*1.42))+theme_publication()+
      ggplot2::theme(axis.text.y=ggplot2::element_blank(),axis.ticks.y=ggplot2::element_blank(),axis.line.y=ggplot2::element_blank())+ggplot2::labs(x=count_label,y=NULL)
    parts<-c(parts,list(bars));widths<-c(widths,1.6)
  }
  combined<-patchwork::wrap_plots(parts,nrow=1,widths=widths,guides='collect')+patchwork::plot_annotation(title=title,theme=theme_publication())
  stamp(combined,original,'publication_aligned_matrix',limits=limits,center=center,signed=signed,value_label=value_label,geometry=geometry,bubble_area='constant_not_detection',row_order=rows,column_order=cols,count_label=count_label,block_palette=as.list(block_palette),clustering='none_frozen_input_order')
}
plot_publication_forest <- function(d,palette,x_label,interval_label,effect_scale,title='') {
  original<-d;cols_ok(d,c('label','group','estimate','lower','upper'));finite_ok(d,c('estimate','lower','upper'));palette_ok(d$group,palette);null<-effect_reference(effect_scale)
  if(anyDuplicated(d$label)||any(d$lower>d$estimate|d$upper<d$estimate))stop('Invalid interval')
  if(effect_scale=='ratio'&&any(as.matrix(d[c('estimate','lower','upper')])<=0))stop('Ratio must be positive')
  d$pos<-seq_len(nrow(d))+cumsum(c(0,as.numeric(head(d$group,-1)!=tail(d$group,-1))*.45))
  need('ggplot2');p<-ggplot2::ggplot(d,ggplot2::aes(estimate,-pos,colour=group))+
    ggplot2::geom_vline(xintercept=null,colour='#B8BEC5',linetype=2,linewidth=.35)+
    ggplot2::geom_segment(ggplot2::aes(x=lower,xend=upper,yend=-pos),linewidth=.7)+ggplot2::geom_point(size=2.7)+
    ggplot2::scale_y_continuous(breaks=-d$pos,labels=d$label)+ggplot2::scale_colour_manual(values=palette,guide='none')+
    theme_publication()+ggplot2::labs(x=x_label,y=NULL,title=title,caption=interval_label)
  if(effect_scale=='ratio')p<-p+ggplot2::scale_x_log10()
  stamp(p,original,'publication_grouped_forest',palette=as.list(palette),effect_scale=effect_scale,interval_label=interval_label,group_gaps=.45)
}
plot_feature_facets <- function(d,value_label,limits,title='',ncols=3,point_size=.35) {
  original<-d;cols_ok(d,c('cell_id','x','y','feature','value'));finite_ok(d,c('x','y','value'))
  if(anyDuplicated(d[c('cell_id','feature')])||nrow(d)!=length(unique(d$cell_id))*length(unique(d$feature)))stop('Complete cell-feature grid required')
  for(k in c('x','y'))if(any(vapply(split(d[[k]],d$cell_id),function(z)length(unique(z)),numeric(1))!=1))stop('Coordinates mismatch')
  if(length(limits)!=2||any(!is.finite(limits))||limits[1]!=0||limits[2]<=0||min(d$value)<0||max(d$value)>limits[2])stop('Invalid common limits')
  d$feature<-factor(d$feature,levels=unique(d$feature));need('ggplot2')
  p<-ggplot2::ggplot(d,ggplot2::aes(x,y))+
    ggplot2::geom_point(data=d[d$value==0,],colour='#D8DDE2',size=point_size)+
    ggplot2::geom_point(data=d[d$value>0,],ggplot2::aes(colour=value),size=point_size)+
    ggplot2::scale_colour_viridis_c(option='magma',limits=limits)+ggplot2::coord_fixed()+ggplot2::facet_wrap(~feature,ncol=ncols)+
    ggplot2::theme_void()+ggplot2::theme(strip.text=ggplot2::element_text(size=10),legend.position='right')+
    ggplot2::labs(title=title,colour=value_label)
  stamp(p,original,'publication_stored_feature_facets',limits=limits,value_label=value_label,coordinates='unchanged',draw_order='zeros_then_positive_original_order',point_size=point_size,cmap='magma',point_layers_rasterized=FALSE)
}
plot_raincloud <- function(d,palette,y_label,unit_label,title='',density_min_n=20) {
  original<-d;cols_ok(d,c('sample_id','group','value'));finite_ok(d,'value');palette_ok(d$group,palette)
  if(anyDuplicated(d$sample_id))stop('One row per declared observation unit required')
  if(!nzchar(trimws(unit_label))||density_min_n<20)stop('Declare unit and conservative density screen')
  groups<-unique(d$group);if(length(groups)>8)stop('Split more than8 groups')
  clouds<-list();cloud_groups<-character();counts<-table(factor(d$group,levels=groups));boxes<-list();points<-list()
  for(i in seq_along(groups)) {
    g<-groups[i];v<-d$value[d$group==g];n<-length(v)
    if(n>=density_min_n&&length(unique(v))>=5) {
      den<-stats::density(v,bw='nrd0',from=min(v),to=max(v),n=256)
      clouds[[g]]<-data.frame(group=g,x=c(i-den$y/max(den$y)*.32,rep(i,256)),y=c(den$x,rev(den$x)));cloud_groups<-c(cloud_groups,g)
    }
    points[[g]]<-data.frame(group=g,x=i+.23+(((seq_along(v)-1)*.61803398875)%%1-.5)*.13,value=v)
    if(n>=5){qq<-quantile(v,c(.25,.5,.75),type=7);iqr<-qq[3]-qq[1];good<-v[v>=qq[1]-1.5*iqr&v<=qq[3]+1.5*iqr]
      boxes[[g]]<-data.frame(group=g,x=i+.065,ymin=min(good),lower=qq[1],middle=qq[2],upper=qq[3],ymax=max(good))}
  }
  need('ggplot2');p<-ggplot2::ggplot()
  if(length(clouds))p<-p+ggplot2::geom_polygon(data=do.call(rbind,clouds),ggplot2::aes(x,y,fill=group,colour=group,group=group),alpha=.35,linewidth=.25)
  p<-p+ggplot2::geom_point(data=do.call(rbind,points),ggplot2::aes(x,value,colour=group),size=.8,alpha=.6)
  if(length(boxes))p<-p+ggplot2::geom_boxplot(data=do.call(rbind,boxes),ggplot2::aes(x=x,ymin=ymin,lower=lower,middle=middle,upper=upper,ymax=ymax,colour=group),stat='identity',width=.1,fill='white',linewidth=.35)
  p<-p+ggplot2::scale_colour_manual(values=palette,guide='none')+ggplot2::scale_fill_manual(values=palette,guide='none')+
    ggplot2::scale_x_continuous(breaks=seq_along(groups),labels=paste0(groups,'\nn=',as.integer(counts)),limits=c(.45,length(groups)+.5))+
      theme_publication()+ggplot2::labs(x=NULL,y=y_label,title=title,caption=paste(strwrap(paste('Points:',unit_label,'| density only n>=',density_min_n,'and>=5 distinct values'),width=80),collapse='\n'))
  stamp(p,original,'publication_raincloud',palette=as.list(palette),unit_label=unit_label,y_label=y_label,density_groups=cloud_groups,density_min_n=density_min_n,
    density='R nrd0 Gaussian KDE restricted to observed min/max; per-group visual normalization',box='Type7 Q1/Q3/median; whiskers observations within1.5IQR; raw points all retained',point_offsets='deterministic input-order sequence',sampling='none')
}
