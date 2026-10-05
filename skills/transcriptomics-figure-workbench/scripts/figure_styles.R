# Optional original layouts; source figure_core.R first. No model fitting.
.style_text <- function(x) {
  if(!is.character(x)||length(x)!=1||is.na(x)||!nzchar(trimws(x))) stop('Explicit nonempty axis/denominator description required')
}
.style_wrap <- function(x,width=30) vapply(as.character(x),function(z)paste(strwrap(z,width=width),collapse='\n'),'')

plot_volcano_editorial <- function(d,labels=character(),alpha=.05,fc=1) {
  original <- d
  cols_ok(d,c('gene','log2FC','padj')); finite_ok(d,c('log2FC','padj')); need('ggplot2')
  if(anyDuplicated(d$gene)||any(d$padj<=0|d$padj>1)) stop('Unique genes and padj in (0,1] required')
  if(length(alpha)!=1||length(fc)!=1||!is.finite(alpha)||alpha<=0||alpha>=1||!is.finite(fc)||fc<=0) stop('Invalid thresholds')
  if(anyDuplicated(labels)||!all(labels %in% d$gene)||any(nchar(labels)>24)) stop('Unique, explicit existing labels of at most 24 characters required')
  d$evidence <- -log10(d$padj)
  d$status <- ifelse(d$padj<=alpha & d$log2FC>=fc,'Up',ifelse(d$padj<=alpha & d$log2FC<=-fc,'Down','Below cutoffs'))
  chosen <- d[d$gene %in% labels,,drop=FALSE]
  if(any(table(chosen$log2FC<0)>6)) stop('At most six labels per side; use a companion table for more')
  extent <- max(abs(d$log2FC),fc*1.3); top <- max(d$evidence,-log10(alpha))*1.18
  pal <- c(Down='#35618F',Up='#B84E35','Below cutoffs'='#BFC5CB')
  status_order <- c('Below cutoffs','Down','Up')
  counts <- table(factor(d$status,levels=status_order))
  p <- ggplot2::ggplot(d,ggplot2::aes(log2FC,evidence)) +
    ggplot2::geom_vline(xintercept=c(-fc,fc),colour='#929AA1',linetype=2,linewidth=.4) +
    ggplot2::geom_hline(yintercept=-log10(alpha),colour='#929AA1',linetype=2,linewidth=.4) +
    ggplot2::geom_point(data=d[d$status=='Below cutoffs',],ggplot2::aes(colour=status,shape=status),alpha=.45,size=1.3) +
    ggplot2::geom_point(data=d[d$status!='Below cutoffs',],ggplot2::aes(colour=status,shape=status),alpha=.9,size=1.8) +
    ggplot2::scale_colour_manual(values=pal,breaks=status_order,labels=paste0(status_order,' (',counts,')'),drop=FALSE) +
    ggplot2::scale_shape_manual(values=c('Below cutoffs'=16,Down=16,Up=16),breaks=status_order,labels=paste0(status_order,' (',counts,')'),drop=FALSE) +
    ggplot2::scale_x_continuous(limits=c(-extent*1.75,extent*1.75),breaks=seq(-extent,extent,length.out=5),labels=function(x)sprintf('%.1f',x)) +
    ggplot2::scale_y_continuous(limits=c(-top*.02,top)) + theme_omics() +
    ggplot2::theme(legend.position='top',legend.text=ggplot2::element_text(size=8)) +
    ggplot2::labs(x='log2 fold change',y='-log10(adjusted p)',colour=NULL,shape=NULL,
      subtitle=paste0('Labels supplied explicitly | FDR <= ',alpha,'; |log2FC| >= ',fc))
  for(sign in c(-1,1)) {
    z <- chosen[(chosen$log2FC<0)==(sign<0),,drop=FALSE]
    if(!nrow(z)) next
    z <- z[order(z$evidence),,drop=FALSE]
    z$label_y <- if(nrow(z)==1) top*.44 else seq(top*.44,top*.88,length.out=nrow(z))
    z$label_x <- sign*extent*1.17
    p <- p+ggplot2::geom_segment(data=z,ggplot2::aes(xend=label_x,yend=label_y),colour='#B8C1C7',linewidth=.3) +
      ggplot2::geom_point(data=z,shape=1,size=2.8,colour='#B8C1C7') +
      ggplot2::geom_text(data=z,ggplot2::aes(x=label_x,y=label_y,label=gene),hjust=if(sign<0)1 else 0,size=3,colour='#28323C')
  }
  stamp(p,original,'volcano_editorial',alpha=alpha,fc=fc,labels=labels,palette=as.list(pal),
        label_layout='fixed side lanes; points unchanged',point_count=nrow(d),status_counts=as.list(counts))
}

plot_volcano_marginal <- function(d,labels=character(),alpha=.05,fc=1,x_bins=42L,y_bins=36L) {
  original <- d
  cols_ok(d,c('gene','log2FC','padj')); finite_ok(d,c('log2FC','padj'))
  need('ggplot2'); need('patchwork')
  if(anyDuplicated(d$gene)||any(d$padj<=0|d$padj>1)) stop('Unique genes and padj in (0,1] required')
  if(length(alpha)!=1||length(fc)!=1||!is.finite(alpha)||alpha<=0||alpha>=1||!is.finite(fc)||fc<=0) stop('Invalid thresholds')
  if(anyDuplicated(labels)||!all(labels %in% d$gene)||length(labels)>6||any(nchar(labels)>24)) stop('At most six unique, explicit short labels required')
  if(length(x_bins)!=1||length(y_bins)!=1||!is.finite(x_bins)||!is.finite(y_bins)||
     x_bins!=as.integer(x_bins)||y_bins!=as.integer(y_bins)||x_bins<8||x_bins>200||y_bins<8||y_bins>200) stop('Histogram bins must be integers in [8,200]')
  d$evidence <- -log10(d$padj)
  d$status <- ifelse(d$padj<=alpha & d$log2FC>=fc,'Up',ifelse(d$padj<=alpha & d$log2FC<=-fc,'Down','Below cutoffs'))
  order <- c('Below cutoffs','Down','Up')
  d$status <- factor(d$status,levels=order)
  pal <- c('Below cutoffs'='#92999D',Down='#9AC65B',Up='#E58B7D')
  extent <- max(abs(d$log2FC))*1.08; extent <- max(extent,fc*1.3)
  top <- max(max(d$evidence)*1.04,-log10(alpha)*1.3)
  make_bars <- function(values,edges) {
    idx <- findInterval(values,edges,rightmost.closed=TRUE)
    bins <- length(edges)-1L
    counts <- matrix(0L,nrow=bins,ncol=length(order),dimnames=list(NULL,order))
    for(i in seq_along(order)) counts[,i] <- tabulate(idx[d$status==order[i]],nbins=bins)
    stopifnot(sum(counts)==nrow(d))
    z <- do.call(rbind,lapply(seq_along(order),function(i) {
      lower <- if(i==1) rep(0,bins) else rowSums(counts[,seq_len(i-1),drop=FALSE])
      data.frame(lo=edges[-length(edges)],hi=edges[-1],base=lower,tip=lower+counts[,i],status=order[i])
    }))
    z$status <- factor(z$status,levels=order)
    z
  }
  xbars <- make_bars(d$log2FC,seq(-extent,extent,length.out=x_bins+1L))
  ybars <- make_bars(d$evidence,seq(0,top,length.out=y_bins+1L))
  main <- ggplot2::ggplot(d,ggplot2::aes(log2FC,evidence)) +
    ggplot2::geom_vline(xintercept=c(-fc,fc),linetype=2,colour='#8C9398',linewidth=.4) +
    ggplot2::geom_hline(yintercept=-log10(alpha),linetype=2,colour='#8C9398',linewidth=.4) +
    ggplot2::geom_point(ggplot2::aes(colour=status),shape=16,size=1,alpha=.65) +
    ggplot2::scale_colour_manual(values=pal,breaks=order,labels=paste0(order,'  ',format(table(d$status),big.mark=',')),drop=FALSE) +
    ggplot2::scale_x_continuous(limits=c(-extent,extent),expand=c(0,0)) +
    ggplot2::scale_y_continuous(limits=c(0,top),expand=c(0,0)) +
    ggplot2::labs(x='log2 fold change',y='-log10(adjusted p)',colour=NULL) + theme_omics() +
    ggplot2::theme(legend.position='none',panel.grid.major=ggplot2::element_line(colour='#E8EBED',linewidth=.25),
      axis.line=ggplot2::element_line(colour='#8C9398'))
  chosen <- d[d$gene %in% labels,,drop=FALSE]
  if(nrow(chosen)) main <- main +
    ggplot2::geom_point(data=chosen,shape=1,size=2.8,stroke=.45,colour='#B8C1C7') +
    ggplot2::geom_text(data=chosen,ggplot2::aes(label=gene),hjust=-.12,vjust=-.55,
                       size=3,colour='#52616C',check_overlap=TRUE)
  upper <- ggplot2::ggplot(xbars) +
    ggplot2::geom_rect(ggplot2::aes(xmin=lo,xmax=hi,ymin=base,ymax=tip,fill=status),
                       colour='#BBC3C8',linewidth=.18) +
    ggplot2::scale_fill_manual(values=pal,breaks=order,drop=FALSE) +
    ggplot2::scale_x_continuous(limits=c(-extent,extent),expand=c(0,0)) +
    ggplot2::scale_y_continuous(expand=c(0,0)) + theme_omics() +
    ggplot2::theme(axis.title=ggplot2::element_blank(),axis.text=ggplot2::element_blank(),
      axis.ticks=ggplot2::element_blank(),legend.position='none')
  right <- ggplot2::ggplot(ybars) +
    ggplot2::geom_rect(ggplot2::aes(xmin=base,xmax=tip,ymin=lo,ymax=hi,fill=status),
                       colour='#BBC3C8',linewidth=.18) +
    ggplot2::scale_fill_manual(values=pal,breaks=order,drop=FALSE) +
    ggplot2::scale_y_continuous(limits=c(0,top),expand=c(0,0)) +
    ggplot2::scale_x_continuous(expand=c(0,0)) + theme_omics() +
    ggplot2::theme(axis.title=ggplot2::element_blank(),axis.text=ggplot2::element_blank(),
      axis.ticks=ggplot2::element_blank(),legend.position='none')
  key_data <- data.frame(status=factor(order,levels=order),x=0,y=c(3,2,1),
                         label=paste0(order,'  ',format(table(d$status),big.mark=',')))
  key <- ggplot2::ggplot(key_data,ggplot2::aes(x,y,colour=status)) +
    ggplot2::geom_point(shape=16,size=2.8) +
    ggplot2::geom_text(ggplot2::aes(x=.18,y=y,label=label),inherit.aes=FALSE,
                       hjust=0,size=2.8,colour='#52616C') +
    ggplot2::scale_colour_manual(values=pal,guide='none') +
    ggplot2::coord_cartesian(xlim=c(-.08,1.7),ylim=c(.5,3.5),clip='off') +
    ggplot2::theme_void() + ggplot2::theme(plot.margin=ggplot2::margin(4,2,4,2))
  p <- patchwork::wrap_plots(upper,key,main,right,ncol=2,
                            widths=c(5.2,1.25),heights=c(1.15,5.2))
  stamp(p,original,'volcano_marginal',alpha=alpha,fc=fc,labels=labels,palette=as.list(pal),
        point_marker='circle',point_count=nrow(d),status_counts=as.list(table(d$status)),
        histogram_universe='all displayed genes; stacked categories',
        x_histogram_bins=x_bins,y_histogram_bins=y_bins,x_limits=c(-extent,extent),y_limits=c(0,top))
}

plot_enrichment_lollipop <- function(d,score_type,denominator_label,count_label) {
  original <- d; need('ggplot2')
  cols_ok(d,c('term','score','padj','count')); finite_ok(d,c('score','padj','count'))
  .style_text(denominator_label); .style_text(count_label)
  if(length(score_type)!=1||!score_type %in% c('NES','GeneRatio')) stop('score_type must be NES or GeneRatio')
  if(anyDuplicated(d$term)||nrow(d)>20) stop('Unique terms, at most 20 per panel; explicitly subset upstream')
  if(any(d$padj<=0|d$padj>1)||any(d$count<1|d$count!=floor(d$count))) stop('padj in (0,1] and positive integer counts required')
  if(score_type=='GeneRatio'&&any(d$score<0|d$score>1)) stop('GeneRatio must be a fraction')
  d$term <- factor(d$term,levels=rev(unique(d$term)))
  d$evidence <- -log10(d$padj)
  breaks <- unique(round(seq(min(d$count),max(d$count),length.out=3)))
  p <- ggplot2::ggplot(d,ggplot2::aes(score,term)) +
    ggplot2::geom_vline(xintercept=0,colour='#929AA1',linewidth=.4) +
    ggplot2::geom_segment(ggplot2::aes(x=0,xend=score,yend=term),colour='#D9E1E7',linewidth=1) +
    ggplot2::geom_point(ggplot2::aes(size=count,fill=evidence),shape=21,colour='#28323C',stroke=.3) +
    ggplot2::scale_size_area(max_size=7,limits=c(0,max(d$count)),breaks=breaks) +
    ggplot2::scale_fill_gradientn(colours=c('#CAD9E8','#3F7CA6','#173F70'),limits=c(0,max(d$evidence,1e-9))) +
    ggplot2::scale_y_discrete(labels=function(x).style_wrap(x,31)) + theme_omics() +
    ggplot2::theme(panel.grid.major.x=ggplot2::element_line(colour='#EDF0F2',linewidth=.3)) +
    ggplot2::labs(x=score_type,y=NULL,fill='-log10(FDR)',size=count_label,subtitle=denominator_label)
  if(score_type=='GeneRatio') p <- p+ggplot2::scale_x_continuous(limits=c(0,max(d$score)*1.15+.001),labels=function(x)paste0(round(x*100),'%'))
  stamp(p,original,'enrichment_lollipop',score_type=score_type,denominator_label=denominator_label,
        count_label=count_label,color='-log10(FDR); sequential; zero included',area='count; zero anchored',
        selection='all supplied rows; first appearance order',score_baseline=0)
}

plot_composition_panels <- function(d,palette,unit_label,y_max=1) {
  original <- d; need('ggplot2'); .style_text(unit_label)
  cols_ok(d,c('sample','group','celltype','count')); finite_ok(d,'count'); palette_ok(d$group,palette)
  if(anyDuplicated(d[c('sample','celltype')])||any(d$count<0|d$count!=floor(d$count))) stop('Unique sample/celltype rows and nonnegative integer counts required')
  if(any(vapply(split(d$group,d$sample),function(z)length(unique(z)),0L)!=1)) stop('Sample group assignment is inconsistent')
  types <- unique(d$celltype); groups <- unique(d$group)
  if(nrow(d)!=length(unique(d$sample))*length(types)) stop('Explicit complete sample x celltype grid required, including zeros')
  if(length(types)>12||length(groups)>4) stop('Split large panels explicitly; do not hide categories')
  denom <- ave(d$count,d$sample,FUN=sum)
  if(any(denom<=0)) stop('Zero denominator')
  d$fraction <- d$count/denom
  if(length(y_max)!=1||!is.finite(y_max)||y_max<=0||y_max>1||y_max<max(d$fraction)) stop('Shared y_max must include all fractions and be in (0,1]')
  offsets <- numeric(); n <- integer()
  for(g in groups) {
    s <- unique(d$sample[d$group==g]); n[g] <- length(s)
    offsets <- c(offsets,setNames(if(length(s)>1)seq(-.13,.13,length.out=length(s)) else 0,s))
  }
  d$display_x <- match(d$group,groups)+offsets[d$sample]
  d$celltype <- factor(d$celltype,levels=types)
  p <- ggplot2::ggplot(d,ggplot2::aes(display_x,fraction,colour=group,shape=group)) +
    ggplot2::geom_point(size=2.2,alpha=.9) +
    ggplot2::facet_wrap(~celltype,ncol=min(3,length(types))) +
    ggplot2::scale_colour_manual(values=palette,guide='none') +
    ggplot2::scale_shape_manual(values=setNames(c(16,15,17,18)[seq_along(groups)],groups),guide='none') +
    ggplot2::scale_x_continuous(limits=c(.5,length(groups)+.5),breaks=seq_along(groups),labels=paste0(.style_wrap(groups,12),'\nn=',n[groups])) +
    ggplot2::scale_y_continuous(limits=c(0,y_max*1.04),breaks=seq(0,y_max,length.out=5),labels=function(x)paste0(format(100*x,trim=TRUE,scientific=FALSE),'%'),expand=ggplot2::expansion(mult=c(0,.01))) +
    theme_omics() + ggplot2::theme(panel.grid.major.y=ggplot2::element_line(colour='#E8EDF1',linewidth=.3),
      axis.text.x=ggplot2::element_text(size=8),strip.text=ggplot2::element_text(face='bold')) +
    ggplot2::labs(x=NULL,y='Fraction of all supplied cells per sample',subtitle=paste('Each point =',unit_label))
  stamp(p,original,'composition_panels',palette=as.list(palette),unit_label=unit_label,
        denominator='all supplied celltype counts per sample; no pooling',shared_y_max=y_max,
        sample_n=as.list(n),inference='none',sample_order_offsets=as.list(offsets))
}

plot_sample_distribution <- function(d,palette,y_label) {
  original <- d; need('ggplot2'); .style_text(y_label)
  cols_ok(d,c('sample_id','group','value')); finite_ok(d,'value'); palette_ok(d$group,palette)
  if(anyDuplicated(d$sample_id)) stop('One row per independent unit required')
  groups <- unique(d$group)
  if(length(groups)>6) stop('Split more than six groups into panels')
  d$display_x <- match(d$group,groups); summary <- list(); n <- integer()
  for(i in seq_along(groups)) {
    idx <- which(d$group==groups[i]); n[groups[i]] <- length(idx)
    d$display_x[idx] <- i+if(length(idx)>1)seq(-.15,.15,length.out=length(idx)) else 0
    if(length(idx)>=5) {
      qs <- quantile(d$value[idx],c(.25,.5,.75),type=7,names=FALSE)
      summary[[length(summary)+1]] <- data.frame(group=groups[i],x=i,lower=qs[1],median=qs[2],upper=qs[3])
    }
  }
  p <- ggplot2::ggplot(d,ggplot2::aes(display_x,value)) +
    ggplot2::geom_point(ggplot2::aes(colour=group),size=2.3,alpha=.9) +
    ggplot2::scale_colour_manual(values=palette,guide='none') +
    ggplot2::scale_x_continuous(limits=c(.5,length(groups)+.6),breaks=seq_along(groups),labels=paste0(.style_wrap(groups,18),'\nn=',n[groups])) +
    theme_omics() + ggplot2::theme(panel.grid.major.y=ggplot2::element_line(colour='#EDF0F2',linewidth=.3)) +
    ggplot2::labs(x=NULL,y=y_label,subtitle='All observations + median / IQR (summary only when n >= 5)')
  if(length(summary)) {
    s <- do.call(rbind,summary)
    p <- p+ggplot2::geom_rect(data=s,ggplot2::aes(xmin=x+.25,xmax=x+.41,ymin=lower,ymax=upper,fill=group),inherit.aes=FALSE,alpha=.2,colour='#28323C') +
      ggplot2::geom_segment(data=s,ggplot2::aes(x=x+.23,xend=x+.43,y=median,yend=median),inherit.aes=FALSE,colour='#28323C',linewidth=.8) +
      ggplot2::scale_fill_manual(values=palette,guide='none')
  }
  stamp(p,original,'sample_distribution',palette=as.list(palette),y_label=y_label,
        summary='median and Q1-Q3; linear quantiles; only n>=5; not CI',
        offsets='deterministic horizontal first-appearance offsets; not a density estimate',sample_n=as.list(n),inference='none')
}
