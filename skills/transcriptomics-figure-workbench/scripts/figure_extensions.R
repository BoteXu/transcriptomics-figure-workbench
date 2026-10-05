# Original layouts consuming frozen tables. Source figure_core.R first.
plot_paired <- function(d,palette,condition_order,y_label) {
  original <- d
  cols_ok(d,c('subject_id','condition','value')); finite_ok(d,'value')
  if(length(condition_order)!=2||anyDuplicated(condition_order)||!setequal(d$condition,condition_order)) stop('Two observed conditions in explicit order required')
  if(anyDuplicated(d[c('subject_id','condition')])||any(table(d$subject_id)!=2)) stop('Each subject needs exactly one observation per condition; report incomplete pairs separately')
  palette_ok(d$condition,palette); need('ggplot2')
  d$condition <- factor(d$condition,levels=condition_order)
  p <- ggplot2::ggplot(d,ggplot2::aes(condition,value,group=subject_id))+
    ggplot2::geom_line(colour='#AAB2BB',alpha=.6,linewidth=.5)+
    ggplot2::geom_point(ggplot2::aes(colour=condition),size=2.3)+
    ggplot2::scale_colour_manual(values=palette,guide='none')+theme_omics()+
    ggplot2::labs(x=NULL,y=y_label,subtitle=paste(length(unique(d$subject_id)),'complete paired subjects'))
  stamp(p,original,'paired',condition_order=condition_order,palette=as.list(palette),y_label=y_label,n_subjects=length(unique(d$subject_id)))
}

plot_effect_matrix <- function(d,effect_label,effect_scale,evidence_cap=6) {
  original <- d; effect_reference(effect_scale)
  cols_ok(d,c('feature','contrast','estimate','lower','upper','padj')); finite_ok(d,c('estimate','lower','upper','padj'))
  if(anyDuplicated(d[c('feature','contrast')])||nrow(d)!=length(unique(d$feature))*length(unique(d$contrast))) stop('Complete unique effect grid required; report unestimable comparisons separately')
  if(any(d$lower>d$estimate|d$upper<d$estimate|d$padj<=0|d$padj>1)) stop('Invalid interval or padj; no implicit zero-p floor')
  if(length(evidence_cap)!=1||!is.finite(evidence_cap)||evidence_cap<=0) stop('Invalid evidence cap')
  if(effect_scale=='ratio' && any(as.matrix(d[c('estimate','lower','upper')])<=0)) stop('Ratio bounds must be positive')
  d$color_value <- if(effect_scale=='ratio') log2(d$estimate) else d$estimate
  d$evidence <- pmin(-log10(d$padj),evidence_cap)
  d$feature <- factor(d$feature,levels=rev(unique(d$feature)))
  d$contrast <- factor(d$contrast,levels=unique(d$contrast))
  extent <- max(abs(d$color_value),1e-9); need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(contrast,feature))+
    ggplot2::geom_point(shape=0,size=5,colour='#D8DDE2')+
    ggplot2::geom_point(ggplot2::aes(colour=color_value,size=evidence))+
    ggplot2::scale_size_area(max_size=6,limits=c(0,evidence_cap),breaks=unique(pmin(c(1,3,evidence_cap),evidence_cap)))+
    ggplot2::scale_colour_gradient2(low='#35618F',mid='#F7F7F5',high='#B84E35',limits=c(-extent,extent))+
    theme_omics()+ggplot2::theme(axis.text.x=ggplot2::element_text(angle=30,hjust=1))+
    ggplot2::labs(x=NULL,y=NULL,colour=if(effect_scale=='ratio')paste('log2 of',effect_label) else effect_label,
                  size=paste0('-log10(FDR)\ncapped at ',evidence_cap))
  stamp(p,original,'effect_matrix',effect_scale=effect_scale,effect_label=effect_label,
        area='min(-log10(padj), evidence_cap)',evidence_cap=evidence_cap,
        empty_square='supplied estimable comparison with zero-sized evidence dot possible')
}

plot_annotated_heatmap <- function(d,value_label,group_palette,block_palette,scale_type,column_annotation_label='Column group',row_annotation_label='Feature block') {
  original <- d
  cols_ok(d,c('feature','sample','value','sample_group','feature_block')); finite_ok(d,'value')
  if(anyDuplicated(d[c('feature','sample')])||nrow(d)!=length(unique(d$feature))*length(unique(d$sample))) stop('Complete unique heatmap grid required')
  if(any(vapply(split(d$sample_group,d$sample),function(x)length(unique(x)),1L)!=1)||any(vapply(split(d$feature_block,d$feature),function(x)length(unique(x)),1L)!=1)) stop('Annotation ID mismatch')
  if(length(scale_type)!=1||!scale_type %in% c('signed','sequential')) stop('Declare signed or sequential scale')
  palette_ok(d$sample_group,group_palette); palette_ok(d$feature_block,block_palette)
  need('ggplot2'); need('patchwork')
  rows <- unique(d$feature); cols <- unique(d$sample)
  d$feature <- factor(d$feature,levels=rev(rows)); d$sample <- factor(d$sample,levels=cols)
  top <- d[!duplicated(d$sample),]; side <- d[!duplicated(d$feature),]
  main <- ggplot2::ggplot(d,ggplot2::aes(sample,feature,fill=value))+ggplot2::geom_tile()+theme_omics()+
    ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1))+ggplot2::labs(x=NULL,y=NULL,fill=value_label)
  if(scale_type=='signed') {
    extent <- max(abs(d$value),1e-9)
    main <- main+ggplot2::scale_fill_gradient2(low='#35618F',mid='#F7F7F5',high='#B84E35',limits=c(-extent,extent))
  } else main <- main+ggplot2::scale_fill_gradient(low='#F7FBFF',high='#173F70')
  tp <- ggplot2::ggplot(top,ggplot2::aes(sample,1,fill=sample_group))+ggplot2::geom_tile()+
    ggplot2::scale_fill_manual(values=group_palette)+ggplot2::theme_void()+ggplot2::labs(fill=column_annotation_label)
  sp <- ggplot2::ggplot(side,ggplot2::aes(1,feature,fill=feature_block))+ggplot2::geom_tile()+
    ggplot2::scale_fill_manual(values=block_palette)+ggplot2::theme_void()+ggplot2::labs(fill=row_annotation_label)
  p <- patchwork::wrap_plots(patchwork::plot_spacer(),tp,sp,main,ncol=2,widths=c(.04,1),heights=c(.05,1),guides='collect')
  p <- p & ggplot2::theme(legend.key.height=grid::unit(.28,'cm'),legend.text=ggplot2::element_text(size=8),
                          legend.title=ggplot2::element_text(size=9),legend.spacing.y=grid::unit(.1,'cm'),
                          legend.margin=ggplot2::margin(2,2,2,2))
  stamp(p,original,'annotated_heatmap',value_label=value_label,scale_type=scale_type,
        group_palette=as.list(group_palette),block_palette=as.list(block_palette),
        column_annotation_label=column_annotation_label,row_annotation_label=row_annotation_label,ordering='first appearance; no clustering')
}

plot_score_comparison <- function(d,score_label,condition_labels) {
  original <- d; fields <- c('feature','score_a','score_b','delta','lower_delta','upper_delta')
  cols_ok(d,fields); finite_ok(d,fields[-1])
  if(length(condition_labels)!=2||anyDuplicated(condition_labels)) stop('Two distinct condition labels required')
  if(anyDuplicated(d$feature)||any(as.matrix(d[c('score_a','score_b')])<0|as.matrix(d[c('score_a','score_b')])>1)) stop('Unique features and bounded scores required')
  if(any(abs(d$delta-(d$score_b-d$score_a))>1e-10)) stop('delta must equal score_b - score_a')
  if(any(d$lower_delta>d$delta|d$upper_delta<d$delta|d$lower_delta< -1|d$upper_delta>1)) stop('Invalid supplied delta interval')
  need('ggplot2'); need('patchwork')
  a <- ggplot2::ggplot(d,ggplot2::aes(score_a,score_b))+
    ggplot2::geom_abline(slope=1,intercept=0,linetype=3,colour='grey60')+
    ggplot2::geom_point(colour='#35618F')+ggplot2::geom_text(ggplot2::aes(label=feature),nudge_y=.04,size=2.8)+
    ggplot2::coord_equal(xlim=c(0,1),ylim=c(0,1))+theme_omics()+
    ggplot2::labs(x=paste(condition_labels[1],score_label),y=paste(condition_labels[2],score_label))
  d$feature <- factor(d$feature,levels=rev(d$feature))
  b <- ggplot2::ggplot(d,ggplot2::aes(delta,feature))+
    ggplot2::geom_vline(xintercept=0,linetype=3,colour='grey60')+
    ggplot2::geom_segment(ggplot2::aes(x=lower_delta,xend=upper_delta,yend=feature),colour='#35618F')+
    ggplot2::geom_point(colour='#35618F')+theme_omics()+ggplot2::labs(x=paste(condition_labels[2],'-',condition_labels[1]),y=NULL)
  stamp(patchwork::wrap_plots(a,b,ncol=2),original,'score_comparison',score_label=score_label,conditions=condition_labels,
        uncertainty='supplied delta intervals; never derived from marginal AUC intervals')
}
