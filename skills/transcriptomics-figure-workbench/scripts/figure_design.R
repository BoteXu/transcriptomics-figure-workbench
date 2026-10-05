# Original optional ggplot2 appearance layer; source figure_core.R first.
# Physical canvas dimensions still belong to export_figure(width=...,height=...).
apply_design <- function(p,font_family=NULL,label_pt=10,tick_pt=9,title_pt=11,
                         spine_mode='keep',grid='keep',x_tick_rotation=NULL,legend_position='right') {
  hash <- attr(p,'omics_input_sha256');spec <- attr(p,'omics_spec')
  if(is.null(hash)||is.null(spec))stop('A stamped renderer plot is required')
  if(!spine_mode %in% c('keep','minimal','boxed')||!grid %in% c('keep','none','x','y','both'))stop('Unknown spine/grid mode')
  if(any(!is.finite(c(label_pt,tick_pt,title_pt)))||any(c(label_pt,tick_pt,title_pt)<=0))stop('Positive font sizes required')
  if(!is.null(x_tick_rotation)&&(!is.finite(x_tick_rotation)||abs(x_tick_rotation)>90))stop('Rotation within -90..90 required')
  if(!legend_position %in% c('right','left','top','bottom','inside'))stop('Use a named legend position; hiding semantic guides is unsupported')
  need('ggplot2');before <- ggplot2::ggplot_build(p)$data
  t <- ggplot2::theme(axis.title=ggplot2::element_text(size=label_pt),axis.text=ggplot2::element_text(size=tick_pt),
                       plot.title=ggplot2::element_text(size=title_pt),legend.text=ggplot2::element_text(size=tick_pt),
                       legend.title=ggplot2::element_text(size=label_pt),legend.position=legend_position)
  if(!is.null(font_family))t <- t+ggplot2::theme(text=ggplot2::element_text(family=font_family))
  if(!is.null(x_tick_rotation))t <- t+ggplot2::theme(axis.text.x=ggplot2::element_text(angle=x_tick_rotation,hjust=if(x_tick_rotation==0).5 else 1))
  if(grid!='keep') {
    t <- t+ggplot2::theme(panel.grid=ggplot2::element_blank())
    if(grid %in% c('x','both'))t <- t+ggplot2::theme(panel.grid.major.x=ggplot2::element_line(colour='#DCE1E4',linewidth=.3))
    if(grid %in% c('y','both'))t <- t+ggplot2::theme(panel.grid.major.y=ggplot2::element_line(colour='#DCE1E4',linewidth=.3))
  }
  if(spine_mode=='minimal')t <- t+ggplot2::theme(panel.border=ggplot2::element_blank(),axis.line=ggplot2::element_line(linewidth=.35))
  if(spine_mode=='boxed')t <- t+ggplot2::theme(panel.border=ggplot2::element_rect(fill=NA,linewidth=.35),axis.line=ggplot2::element_blank())
  result <- p+t
  if(!identical(before,ggplot2::ggplot_build(result)$data))stop('Appearance changed built data; discard plot')
  spec$design <- list(font_family=font_family,label_pt=label_pt,tick_pt=tick_pt,title_pt=title_pt,spine_mode=spine_mode,
                      grid=grid,x_tick_rotation=x_tick_rotation,legend_position=legend_position)
  attr(result,'omics_input_sha256') <- hash;attr(result,'omics_spec') <- spec;result
}
