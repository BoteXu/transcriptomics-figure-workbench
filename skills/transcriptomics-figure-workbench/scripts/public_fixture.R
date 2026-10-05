# Small public-data renderer validation. Input download is explicit and separate.
# SOURCE: huayc09/SeuratExtend commit c917a47e20cab9fb3399ff7ed078d3e8139339f0/data/pbmc.rda
# Data license: CC0, per upstream README. Example sample/condition labels are not verified donors.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=2||dir.exists(args[2])) stop('Usage: public_fixture.R PINNED_PBMC_RDA NEW_OUTPUT_DIR')
script <- sub('^--file=','',grep('^--file=',commandArgs(),value=TRUE)[1])
source(file.path(dirname(normalizePath(script)),'figure_core.R'))
source(file.path(dirname(normalizePath(script)),'figure_extensions.R'))
need('SeuratObject'); need('Matrix')
expected <- 'f2fecfcbc8a6360362ac45d2a68c9cd798e0ceb2e95768b2311000c71dc9ebda'
stopifnot(digest::digest(file=args[1],algo='sha256')==expected)
e <- new.env(); load(args[1],envir=e); pbmc <- e$pbmc
stopifnot(ncol(pbmc)==500,all(c('cluster') %in% colnames(pbmc@meta.data)))
coord <- SeuratObject::Embeddings(pbmc,'umap'); md <- pbmc@meta.data
stopifnot(identical(rownames(coord),rownames(md)))
tab <- data.frame(cell_id=rownames(coord),x=coord[,1],y=coord[,2],group=as.character(md$cluster),row.names=NULL)
groups <- unique(tab$group)
palette <- setNames(grDevices::hcl.colors(length(groups),'Dark 3'),groups)
meta <- list(source='SeuratExtend CC0 PBMC example, pinned c917a47e20cab9fb3399ff7ed078d3e8139339f0',
 palette=as.list(palette),input_unit='stored PBMC example cells',experimental_unit='descriptive cells; no verified donor inference',
 contrast='none; public renderer fixture',denominator='500 cells in the published subset; within-cluster denominators for marker summaries',
 model='none; stored coordinates and arithmetic summaries only',limits='no display clipping',
 filtering='all 500 published subset cells; predeclared marker list for marker panels',
 uncertainty='not estimated; descriptive validation',interpretation_limit='Public example, not project evidence; example sample and condition labels are not verified biological replicates',synthetic=FALSE)
save_public <- function(p,d,id) {
  spec <- attr(p,'omics_spec'); input_hash <- attr(p,'omics_input_sha256')
  if(inherits(p,'patchwork')) p <- p+patchwork::plot_annotation(title='PUBLIC PBMC EXAMPLE',caption='Renderer validation only; not project evidence')
  else p <- p+ggplot2::labs(title='PUBLIC PBMC EXAMPLE',caption='Renderer validation only; not project evidence')
  # Restore the verified adapter stamp after adding display-only labels.
  attr(p,'omics_spec') <- spec; attr(p,'omics_input_sha256') <- input_hash
  export_figure(p,d,args[2],id,meta,source_file=args[1],expected_source_sha256=expected,width=9,height=5.8)
}
save_public(plot_embedding(tab,palette),tab,'public_embedding')
genes <- c('CD3D','IL7R','CD8A','MS4A1','CD79A','CD14','FCGR3A','GNLY')
counts <- SeuratObject::GetAssayData(pbmc,assay='RNA',slot='counts')[genes,,drop=FALSE]
expr <- SeuratObject::GetAssayData(pbmc,assay='RNA',slot='data')[genes,,drop=FALSE]
stopifnot(all(is.finite(expr@x)))
dot <- do.call(rbind,lapply(groups,function(g){
  cells <- which(tab$group==g)
  data.frame(feature=genes,group=g,fraction=Matrix::rowMeans(counts[,cells,drop=FALSE]>0),
             value=Matrix::rowMeans(expr[,cells,drop=FALSE]),n_cells=length(cells),row.names=NULL)
}))
save_public(plot_dot(dot,'Mean stored RNA data across all cluster cells','mean_all','All cells in cluster'),dot,'public_dot')
heat <- data.frame(feature=dot$feature,sample=dot$group,value=dot$value,
                   sample_group=dot$group,feature_block=rep(c('T marker','T marker','T marker','B marker','B marker','Myeloid marker','Myeloid marker','NK marker'),length(groups)))
blocks <- c('T marker'='#8172B2','B marker'='#55A868','Myeloid marker'='#C99442','NK marker'='#B85C88')
save_public(plot_annotated_heatmap(heat,'Mean stored RNA data',palette,blocks,'sequential',column_annotation_label='Cell type'),heat,'public_annotated_heatmap')
cat('PASS: 500 public cells; stored UMAP; 8 predeclared markers; 3 descriptive figure bundles; verified source SHA256\n')
