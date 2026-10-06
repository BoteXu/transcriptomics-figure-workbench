# Newly authored adapters; no third-party implementation is vendored.
# Charts consume reviewed results; no biological inference or installation.
.omics_core_file <- normalizePath(sys.frame(1)$ofile, mustWork=TRUE)
need <- function(pkg) {
  if (!requireNamespace(pkg, quietly=TRUE)) stop('Missing package: ', pkg, call.=FALSE)
}
table_bytes <- function(d) {
  con <- textConnection('lines','w',local=TRUE)
  tryCatch(write.table(d,con,sep='\t',row.names=FALSE,quote=TRUE),finally=close(con))
  charToRaw(enc2utf8(paste0(paste(lines,collapse='\n'),'\n')))
}
sha256_raw <- function(x) { need('digest'); digest::digest(x,algo='sha256',serialize=FALSE) }
stamp <- function(p,d,kind,...) {
  attr(p,'omics_input_sha256') <- sha256_raw(table_bytes(d))
  attr(p,'omics_spec') <- c(list(kind=kind),list(...))
  p
}
effect_reference <- function(effect_scale) {
  if(length(effect_scale)!=1 || !effect_scale %in% c('difference','log_ratio','ratio')) stop('Declare effect_scale: difference, log_ratio, or ratio')
  if(effect_scale=='ratio') 1 else 0
}
cols_ok <- function(d, columns) {
  if (!is.data.frame(d) || !nrow(d)) stop('Expected nonempty data.frame')
  if (!all(columns %in% names(d))) stop('Missing columns: ', paste(setdiff(columns,names(d)),collapse=', '))
  if (anyNA(d[,columns,drop=FALSE])) stop('Missing required values; report missing separately')
}
finite_ok <- function(d, columns) {
  for (s in columns) if (!is.numeric(d[[s]]) || any(!is.finite(d[[s]]))) stop('Nonfinite/non-numeric: ',s)
}
palette_ok <- function(values, palette) {
  if (is.null(names(palette)) || anyDuplicated(names(palette))) stop('Palette must have unique names')
  if (!all(as.character(values) %in% names(palette))) stop('Palette missing categories')
  grDevices::col2rgb(palette)
  invisible(TRUE)
}
theme_omics <- function(size=10, family=getOption('omics.font_family','sans')) {
  need('ggplot2')
  ggplot2::theme_classic(base_size=size, base_family=family) +
    ggplot2::theme(plot.title=ggplot2::element_text(face='bold'),
      axis.text=ggplot2::element_text(colour='#28323C'),
      legend.title=ggplot2::element_text(face='bold'),
      plot.caption=ggplot2::element_text(hjust=0,colour='#46525D'),
      plot.margin=ggplot2::margin(8,12,8,8),strip.background=ggplot2::element_blank())
}
plot_embedding <- function(d,palette,axis_prefix='UMAP') {
  cols_ok(d,c('cell_id','x','y','group')); finite_ok(d,c('x','y'))
  if (anyDuplicated(d$cell_id)) stop('Duplicate cell_id')
  palette_ok(d$group,palette); need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(x,y,colour=group)) +
    ggplot2::geom_point(size=.6,alpha=.85) + ggplot2::coord_equal() +
    ggplot2::scale_colour_manual(values=palette,drop=FALSE) + theme_omics() +
    ggplot2::labs(x=paste0(axis_prefix,' 1'),y=paste0(axis_prefix,' 2'),colour='Identity')
  stamp(p,d,'embedding',palette=as.list(palette),axis_prefix=axis_prefix)
}
plot_sample_points <- function(d,palette,y_label) {
  cols_ok(d,c('sample_id','group','value')); finite_ok(d,'value'); palette_ok(d$group,palette)
  if (anyDuplicated(d$sample_id)) stop('One row per independent unit required')
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(group,value,colour=group)) +
    ggplot2::geom_point(position=ggplot2::position_jitter(width=.08,height=0,seed=1),size=2.5) +
    ggplot2::scale_colour_manual(values=palette,guide='none') + theme_omics() +
    ggplot2::labs(x=NULL,y=y_label)
  stamp(p,d,'samples',palette=as.list(palette),y_label=y_label)
}
plot_forest <- function(d,x_label,interval_label,effect_scale) {
  original <- d; null <- effect_reference(effect_scale)
  cols_ok(d,c('label','estimate','lower','upper')); finite_ok(d,c('estimate','lower','upper'))
  if (anyDuplicated(d$label)) stop('Duplicate row labels')
  if (any(d$lower>d$estimate | d$upper<d$estimate)) stop('Invalid interval bounds')
  if(effect_scale=='ratio' && any(as.matrix(d[c('estimate','lower','upper')])<=0)) stop('Ratio estimates and bounds must be positive')
  need('ggplot2'); d$label <- factor(d$label,levels=rev(unique(d$label)))
  p <- ggplot2::ggplot(d,ggplot2::aes(estimate,label)) +
    ggplot2::geom_vline(xintercept=null,linetype=2,colour='#929AA1') +
    ggplot2::geom_segment(ggplot2::aes(x=lower,xend=upper,yend=label),linewidth=.65,colour='#35618F') +
    ggplot2::geom_point(size=2.6,colour='#35618F') + theme_omics() +
    ggplot2::labs(x=x_label,y=NULL,subtitle=interval_label)
  if(effect_scale=='ratio') p <- p+ggplot2::scale_x_log10()
  stamp(p,original,'forest',effect_scale=effect_scale,null_value=null,x_label=x_label,interval_label=interval_label)
}
plot_volcano <- function(d,alpha=.05,fc=1) {
  original <- d
  cols_ok(d,c('gene','log2FC','padj')); finite_ok(d,c('log2FC','padj'))
  if (anyDuplicated(d$gene) || any(d$padj<0 | d$padj>1)) stop('Invalid genes or adjusted p values')
  if (!is.finite(alpha) || alpha<=0 || alpha>=1 || !is.finite(fc) || fc<=0) stop('Invalid thresholds')
  if (any(d$padj==0)) stop('Zero padj requires an explicitly documented display floor')
  d$status <- ifelse(d$padj<=alpha & abs(d$log2FC)>=fc,ifelse(d$log2FC>0,'Up','Down'),'Other')
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(log2FC,-log10(padj),colour=status)) +
    ggplot2::geom_point(size=1.3,alpha=.8) +
    ggplot2::geom_vline(xintercept=c(-fc,fc),linetype=2,colour='grey65') +
    ggplot2::geom_hline(yintercept=-log10(alpha),linetype=2,colour='grey65') +
    ggplot2::scale_colour_manual(values=c(Up='#B84E35',Down='#35618F',Other='#BFC5CB')) +
    theme_omics() + ggplot2::labs(x='log2 fold change',y='-log10(adjusted p)',colour=NULL)
  stamp(p,original,'volcano',alpha=alpha,fc=fc)
}
plot_dot <- function(d,value_label,value_semantics,denominator_label) {
  cols_ok(d,c('feature','group','fraction','value')); finite_ok(d,c('fraction','value'))
  if (any(d$fraction<0 | d$fraction>1) || anyDuplicated(d[c('feature','group')])) stop('Invalid dot table')
  if(length(value_semantics)!=1 || !value_semantics %in% c('mean_all','mean_detected','scaled','signed_effect')) stop('Declare dot color semantics')
  if(!is.character(denominator_label)||length(denominator_label)!=1||!nzchar(trimws(denominator_label))) stop('Detection denominator label required')
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(group,feature,size=fraction,colour=value)) +
    ggplot2::geom_point() + ggplot2::scale_size_area(max_size=7,limits=c(0,1),breaks=c(.25,.5,1),labels=c('25%','50%','100%')) +
    theme_omics() + ggplot2::labs(x=NULL,y=NULL,size=denominator_label,colour=value_label)
  if(value_semantics %in% c('scaled','signed_effect')) {
    extent <- max(abs(d$value),1e-9)
    p <- p+ggplot2::scale_colour_gradient2(low='#35618F',mid='#F7F7F5',high='#B84E35',limits=c(-extent,extent))
  } else p <- p+ggplot2::scale_colour_gradient(low='#BBCFE3',high='#173F70')
  if(length(unique(d$group))>4) p <- p+ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1))
  stamp(p,d,'dot',value_label=value_label,value_semantics=value_semantics,denominator_label=denominator_label,area='fraction')
}
plot_heatmap <- function(d,value_label,center=0,scale_type='signed',
                         row_field='feature',column_field='sample',value_field='value',
                         row_order=NULL,column_order=NULL,row_aliases=NULL,column_aliases=NULL,
                         missing='error',label_wrap=NULL) {
  cols_ok(d,c(row_field,column_field,value_field)); finite_ok(d,value_field)
  if (anyDuplicated(d[c(row_field,column_field)])) stop('Duplicate matrix cells')
  rows <- unique(d[[row_field]]); cols <- unique(d[[column_field]])
  if (!is.null(row_order)) { if (length(row_order)!=length(unique(row_order)) || !setequal(row_order,rows)) stop('row_order must cover every supplied row'); rows <- row_order }
  if (!is.null(column_order)) { if (length(column_order)!=length(unique(column_order)) || !setequal(column_order,cols)) stop('column_order must cover every supplied column'); cols <- column_order }
  if (!missing %in% c('error','mask')) stop("missing must be 'error' or 'mask'")
  if (nrow(d)!=length(rows)*length(cols) && missing=='error') stop("Incomplete heatmap grid; use missing='mask' to display absent cells")
  need('ggplot2')
  if(!scale_type %in% c('signed','sequential')) stop('Unknown heatmap scale')
  aliases <- function(keys,map,label) {
    out <- as.character(keys)
    if (!is.null(map)) { if (is.null(names(map)) || !setequal(names(map),as.character(keys))) stop(paste0(label,'_aliases must cover every supplied identifier')); out <- as.character(map[as.character(keys)]) }
    if (any(!nzchar(out)) || anyDuplicated(out)) stop(paste0(label,'_aliases must be nonempty and unique'))
    if (!is.null(label_wrap)) out <- vapply(out,function(x) paste(strwrap(x,width=label_wrap),collapse='\n'),character(1))
    out
  }
  d[[row_field]] <- factor(d[[row_field]],levels=rows,labels=aliases(rows,row_aliases,'row'))
  d[[column_field]] <- factor(d[[column_field]],levels=cols,labels=aliases(cols,column_aliases,'column'))
  p <- ggplot2::ggplot(d,ggplot2::aes(.data[[column_field]],.data[[row_field]],fill=.data[[value_field]])) + ggplot2::geom_tile() +
    theme_omics() + ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1)) +
    ggplot2::labs(x=NULL,y=NULL,fill=value_label) + ggplot2::scale_x_discrete(drop=FALSE) + ggplot2::scale_y_discrete(drop=FALSE)
  if(scale_type=='signed') p <- p+ggplot2::scale_fill_gradient2(low='#35618F',mid='#F7F7F5',high='#B84E35',midpoint=center)
  else p <- p+ggplot2::scale_fill_gradient(low='#F7FBFF',high='#173F70')
  stamp(p,d,'heatmap',value_label=value_label,scale_type=scale_type,center=center,row_field=row_field,column_field=column_field,value_field=value_field,row_order=rows,column_order=cols,missing=missing)
}
plot_qc <- function(d,y_label) {
  cols_ok(d,c('cell_id','sample','value')); finite_ok(d,'value'); need('ggplot2')
  if (anyDuplicated(d[c('cell_id','sample')])) stop('Duplicate cells within sample')
  # No automatic cutoff or significance test.
  p <- ggplot2::ggplot(d,ggplot2::aes(sample,value)) +
    ggplot2::geom_boxplot(fill='#CAD9E8',colour='#35618F',width=.55) + theme_omics() +
    ggplot2::labs(x='Capture / sample',y=y_label)
  stamp(p,d,'qc',y_label=y_label)
}
plot_composition <- function(d,palette) {
  cols_ok(d,c('sample','celltype','count')); finite_ok(d,'count'); palette_ok(d$celltype,palette)
  if (any(d$count<0 | d$count!=floor(d$count)) || anyDuplicated(d[c('sample','celltype')])) stop('Invalid counts')
  if (any(tapply(d$count,d$sample,sum)==0)) stop('Zero denominator')
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(sample,count,fill=celltype)) +
    ggplot2::geom_col(position='fill',width=.75) +
    ggplot2::scale_fill_manual(values=palette,drop=FALSE) +
    ggplot2::scale_y_continuous(labels=function(x)paste0(100*x,'%')) + theme_omics() +
    ggplot2::labs(x=NULL,y='Fraction of included cells',fill='Cell type')
  stamp(p,d,'composition',palette=as.list(palette),denominator='all supplied counts per sample')
}
plot_curve <- function(d,kind=c('ROC','PR','calibration')) {
  kind <- match.arg(kind); cols_ok(d,c('model','x','y')); finite_ok(d,c('x','y'))
  if (any(d$x<0|d$x>1|d$y<0|d$y>1)) stop('Curve values must be fractions in [0,1]')
  # Preserve supplied threshold order, including ties. No smoothing/AUC estimation.
  need('ggplot2')
  p <- ggplot2::ggplot(d,ggplot2::aes(x,y,group=model,linetype=model)) +
    ggplot2::geom_path(linewidth=.8,colour='#35618F') + ggplot2::coord_equal(xlim=c(0,1),ylim=c(0,1)) + theme_omics()
  if (kind!='PR') p <- p+ggplot2::geom_abline(slope=1,intercept=0,colour='grey60',linetype=3)
  labels <- switch(kind,ROC=c('False positive rate','True positive rate'),PR=c('Recall','Precision'),calibration=c('Predicted probability','Observed fraction'))
  p <- p + ggplot2::labs(x=labels[1],y=labels[2],linetype='Model')
  stamp(p,d,'curve',curve_kind=kind,threshold_order='input order')
}
export_figure <- function(p,d,out_dir,id,meta,width=7.1,height=4.5,source_file=NULL,expected_source_sha256=NULL) {
  need('ggplot2'); need('jsonlite'); need('svglite'); need('digest')
  if (!grepl('^[A-Za-z][A-Za-z0-9_-]*$',id)) stop('Unsafe figure id')
  required <- c('source','palette','input_unit','experimental_unit','contrast','denominator','model','limits','filtering','uncertainty','interpretation_limit','synthetic')
  if (!all(required %in% names(meta))) stop('Incomplete figure provenance')
  for(key in setdiff(required,c('synthetic','palette'))) if(!is.character(meta[[key]])||length(meta[[key]])!=1||!nzchar(trimws(meta[[key]]))) stop('Empty/non-text metadata: ',key)
  if(!(is.character(meta$palette)||is.list(meta$palette))||!length(meta$palette)||identical(meta$palette,'')) stop('Empty palette metadata')
  if('input_hash' %in% names(meta)) stop('input_hash is computed; use expected_source_sha256')
  if (!is.logical(meta$synthetic) || length(meta$synthetic)!=1 || is.na(meta$synthetic)) stop('synthetic must be logical')
  if (!is.data.frame(d) || !nrow(d)) stop('Empty data')
  if (!is.finite(width)||!is.finite(height)||width<=0||height<=0) stop('Invalid dimensions')
  raw <- table_bytes(d); plotted_hash <- sha256_raw(raw)
  if(!identical(attr(p,'omics_input_sha256'),plotted_hash)) stop('Export table does not match renderer input; use a reviewed adapter')
  spec <- attr(p,'omics_spec'); source_hash <- NULL
  if(!is.null(source_file)) {
    source_file <- normalizePath(source_file,mustWork=TRUE)
    source_hash <- digest::digest(file=source_file,algo='sha256')
  }
  if(!is.null(expected_source_sha256) && (length(expected_source_sha256)!=1||!grepl('^[0-9a-fA-F]{64}$',expected_source_sha256)||!identical(source_hash,tolower(expected_source_sha256)))) stop('Source SHA256 mismatch or missing source file')
  if (meta$synthetic) {
    if(inherits(p,'patchwork')) p <- p+patchwork::plot_annotation(title=paste('SYNTHETIC DEMO -',id),caption='Software test fixture; not biological evidence')
    else p <- p+ggplot2::labs(title=paste('SYNTHETIC DEMO -',id),caption='Software test fixture; not biological evidence')
  }
  dir.create(out_dir,recursive=TRUE,showWarnings=FALSE)
  out_dir <- normalizePath(out_dir,mustWork=TRUE); destination <- file.path(out_dir,id)
  ext <- c('.svg','.pdf','.png','.tsv','.json','_session.txt')
  if(file.exists(destination)||any(file.exists(paste0(file.path(out_dir,id),ext)))) stop('Refusing to overwrite existing v1/v2 outputs')
  lock <- file.path(out_dir,paste0('.',id,'.lock'))
  if(!dir.create(lock,showWarnings=FALSE)) stop('Figure id is locked')
  stage <- NULL
  on.exit({
    # Remove only our uncommitted temp folder and owned lock, never published output.
    if(!is.null(stage) && dir.exists(stage) && identical(normalizePath(dirname(stage)),out_dir) && startsWith(basename(stage),paste0('.',id,'-staging-'))) unlink(stage,recursive=TRUE)
    unlink(lock,recursive=TRUE)
  },add=TRUE)
  # Generate an ASCII basename without asking tempfile to translate a Unicode path.
  stage <- file.path(out_dir,basename(tempfile(pattern=paste0('.',id,'-staging-'))))
  if(!dir.create(stage)) stop('Cannot create staging directory')
  files <- paste0(file.path(stage,id),ext)
  ggplot2::ggsave(files[1],p,device=svglite::svglite,width=width,height=height,bg='white')
  ggplot2::ggsave(files[2],p,device=grDevices::cairo_pdf,width=width,height=height,bg='white')
  ggplot2::ggsave(files[3],p,width=width,height=height,dpi=300,bg='white')
  writeBin(raw,files[4])
  capture.output(sessionInfo(),file=files[6])
  meta$schema_version <- 2; meta$figure_id <- id; meta$status <- 'RENDERED_UNREVIEWED'
  meta$input_hash <- plotted_hash; meta$input_hash_algorithm <- 'SHA256'; meta$input_hash_scope <- 'exact exported TSV bytes'
  meta$source_file <- source_file; meta$source_file_sha256 <- source_hash; meta$figure_spec <- spec
  meta$width_inches <- width; meta$height_inches <- height
  renderers <- list.files(dirname(.omics_core_file),pattern='^figure_.*[.]R$',full.names=TRUE)
  meta$renderer_sha256 <- as.list(setNames(vapply(renderers,function(f)digest::digest(file=f,algo='sha256'),''),basename(renderers)))
  meta$output_sha256 <- as.list(setNames(vapply(files[c(1:4,6)],function(f)digest::digest(file=f,algo='sha256'),''),basename(files[c(1:4,6)])))
  jsonlite::write_json(meta,files[5],auto_unbox=TRUE,pretty=TRUE)
  if(file.exists(destination)||!file.rename(stage,destination)) stop('Cannot publish complete figure bundle')
  invisible(paste0(file.path(destination,id),ext))
}
