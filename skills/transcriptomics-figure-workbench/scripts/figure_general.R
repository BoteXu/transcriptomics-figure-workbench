# Original frozen-table renderers. Source figure_core.R first; no fitting or installation.
labels_required <- function(...) {
  v <- list(...)
  if(any(vapply(v,function(x)!is.character(x)||length(x)!=1||!nzchar(trimws(x)),TRUE))) stop('Explicit nonempty semantic labels required')
}
plot_xy_points <- function(d,palette,x_label,y_label,unit_label) {
  labels_required(x_label,y_label,unit_label);original <- d
  cols_ok(d,c('unit_id','group','x','y'));finite_ok(d,c('x','y'));palette_ok(d$group,palette)
  if(anyDuplicated(d$unit_id)) stop('One row per independent unit required')
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(x,y,colour=group))+ggplot2::geom_point(size=2,alpha=.8)+
    ggplot2::scale_colour_manual(values=palette)+theme_omics()+ggplot2::labs(x=x_label,y=y_label,colour=NULL)
  stamp(p,original,'xy_points',palette=as.list(palette),x_label=x_label,y_label=y_label,unit_label=unit_label,inference='No correlation, fit or p-value computed')
}
plot_grouped_estimates <- function(d,palette,y_label,interval_label) {
  labels_required(y_label,interval_label);original <- d
  cols_ok(d,c('category','group','estimate','lower','upper'));finite_ok(d,c('estimate','lower','upper'));palette_ok(d$group,palette)
  if(anyDuplicated(d[c('category','group')])||nrow(d)!=length(unique(d$category))*length(unique(d$group))) stop('Complete unique category-by-group grid required')
  if(any(d$lower>d$estimate|d$upper<d$estimate)) stop('Invalid supplied interval')
  d$category <- factor(d$category,levels=unique(d$category));d$group <- factor(d$group,levels=unique(d$group));need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(category,estimate,fill=group,group=group))+
    ggplot2::geom_col(position=ggplot2::position_dodge(.75),width=.65)+
    ggplot2::geom_errorbar(ggplot2::aes(ymin=lower,ymax=upper),position=ggplot2::position_dodge(.75),width=.15,linewidth=.4)+
    ggplot2::geom_hline(yintercept=0,linewidth=.3,colour='grey60')+ggplot2::scale_fill_manual(values=palette)+
    theme_omics()+ggplot2::labs(x=NULL,y=y_label,subtitle=interval_label,fill=NULL)
  stamp(p,original,'grouped_estimates',palette=as.list(palette),y_label=y_label,interval_label=interval_label,baseline=0,statistics='Supplied estimates and intervals; no aggregation')
}
plot_binned_distribution <- function(d,palette,x_label,denominator_label) {
  labels_required(x_label,denominator_label);original <- d
  cols_ok(d,c('group','left','right','count'));finite_ok(d,c('left','right','count'));palette_ok(d$group,palette)
  if(any(d$right<=d$left|d$count<0|d$count%%1!=0)) stop('Positive bin widths and nonnegative integer counts required')
  groups <- unique(d$group);bins <- lapply(groups,function(g) {
    s <- d[d$group==g,]
    if(anyDuplicated(s[c('left','right')])||any(diff(s$left)<0)||any(tail(s$left,-1)<head(s$right,-1))) stop('Ordered non-overlapping unique bins required')
    s[c('left','right')]
  })
  if(any(vapply(bins,function(b)!isTRUE(all.equal(unname(as.matrix(b)),unname(as.matrix(bins[[1]])))),TRUE))) stop('Identical bins required across groups')
  joins <- do.call(rbind,lapply(groups,function(g) {
    s <- d[d$group==g,];if(nrow(s)<2)return(NULL)
    i <- which(tail(s$left,-1)==head(s$right,-1))+1L
    if(!length(i))return(NULL)
    data.frame(group=g,left=s$left[i],count=s$count[i-1L],end_count=s$count[i])
  }))
  need('ggplot2');p <- ggplot2::ggplot(d,ggplot2::aes(colour=group))+
    ggplot2::geom_segment(ggplot2::aes(x=left,xend=right,y=count,yend=count),linewidth=.8)
  if(!is.null(joins))p <- p+ggplot2::geom_segment(data=joins,ggplot2::aes(x=left,xend=left,y=count,yend=end_count),linewidth=.8)
  p <- p+ggplot2::scale_colour_manual(values=palette)+ggplot2::expand_limits(y=0)+theme_omics()+
    ggplot2::labs(x=x_label,y='Count',colour=denominator_label)
  stamp(p,original,'binned_distribution',palette=as.list(palette),x_label=x_label,denominator_label=denominator_label,binning='Frozen boundaries; no rebinning, normalization or density fit')
}
plot_confusion_counts <- function(d,unit_label) {
  labels_required(unit_label);original <- d
  cols_ok(d,c('actual','predicted','count'));finite_ok(d,'count');classes <- unique(d$actual)
  if(!setequal(classes,d$predicted)||anyDuplicated(d[c('actual','predicted')])||nrow(d)!=length(classes)^2) stop('Complete unique square class grid required')
  if(any(d$count<0|d$count%%1!=0)||sum(d$count)<=0) stop('Nonnegative integer counts and positive total required')
  d$actual <- factor(d$actual,levels=rev(classes));d$predicted <- factor(d$predicted,levels=classes);d$ink <- ifelse(d$count>max(d$count)*.6,'white','#243947');need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(predicted,actual,fill=count))+ggplot2::geom_tile()+
    ggplot2::geom_text(ggplot2::aes(label=count,colour=ink),size=3)+ggplot2::scale_colour_identity()+
    ggplot2::scale_fill_gradient(low='#F7FBFF',high='#174570',limits=c(0,max(d$count)))+ggplot2::coord_equal()+
    theme_omics()+ggplot2::labs(x='Predicted class',y='Observed class',fill=paste('Count:',unit_label))
  stamp(p,original,'confusion_counts',unit_label=unit_label,total=sum(d$count),semantics='Rows observed; columns predicted; no model fitting, threshold choice or accuracy calculation')
}
plot_density_ridges <- function(d,palette,x_label,density_label,amplitude=.8) {
  labels_required(x_label,density_label);original <- d
  cols_ok(d,c('group','x','density'));finite_ok(d,c('x','density'));palette_ok(d$group,palette)
  if(any(d$density<0)||length(amplitude)!=1||!is.finite(amplitude)||amplitude<=0||amplitude>1) stop('Nonnegative densities and amplitude in (0,1] required')
  groups <- unique(d$group);grids <- lapply(groups,function(g) {
    s <- d[d$group==g,];if(nrow(s)<2||any(diff(s$x)<=0))stop('Strictly increasing x grids required');s$x
  })
  if(any(vapply(grids,function(x)!identical(x,grids[[1]]),TRUE))) stop('Identical density grids required')
  peak <- max(d$density);if(peak<=0)stop('Positive density peak required')
  d$baseline <- match(d$group,groups)-1;d$display <- d$baseline+d$density/peak*amplitude;need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(x,group=group))+
    ggplot2::geom_ribbon(ggplot2::aes(ymin=baseline,ymax=display,fill=group),alpha=.65)+
    ggplot2::geom_line(ggplot2::aes(y=display,colour=group),linewidth=.45)+
    ggplot2::scale_colour_manual(values=palette,guide='none')+ggplot2::scale_fill_manual(values=palette,guide='none')+
    ggplot2::scale_y_continuous(breaks=seq_along(groups)-1,labels=groups)+theme_omics()+ggplot2::labs(x=x_label,y=density_label)
  stamp(p,original,'density_ridges',palette=as.list(palette),x_label=x_label,density_label=density_label,shared_display_scale=amplitude/peak,density_estimation='Upstream only; no KDE, bandwidth choice or per-group rescaling')
}
