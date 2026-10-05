# Synthetic fixtures only. Usage: Rscript style_test.R NEW_OUTPUT PYTHON_OUTPUT/_input
args <- commandArgs(trailingOnly=TRUE)
script <- sub('^--file=','',commandArgs()[grepl('^--file=',commandArgs())][1])
source(file.path(dirname(script),'figure_core.R'))
source(file.path(dirname(script),'figure_styles.R'))
out <- args[1]; inputs <- args[2]
if(file.exists(out)) stop('New output directory required')
dir.create(out,recursive=TRUE)
read <- function(name) read.delim(file.path(inputs,paste0(name,'.tsv')),check.names=FALSE,stringsAsFactors=FALSE)
volcano <- read('volcano'); samples <- read('samples'); composition <- read('composition')
enrichment <- read('enrichment'); nes <- read('nes')
focal <- c('Gene003','Gene018','Gene045','Gene067','Gene120','Gene200')
pal <- c(Control='#35618F',Condition='#B84E35')
types <- unique(composition$celltype)
cellpal <- setNames(c('#35618F','#67A9A2','#B84E35','#C9A64B','#857AA8','#AAB4BD'),types)
meta <- list(source='Deterministic synthetic style_test.py fixtures, seed 260926',
             palette='Explicit renderer maps in figure_spec',input_unit='synthetic reviewed-table schema',
             experimental_unit='synthetic sample IDs; no experimental evidence',contrast='synthetic demonstration only',
             denominator='all supplied rows per declared sample; enrichment 200 query genes for ratio fixture',
             model='none; frozen illustrative numbers',limits='all supplied values displayed',
             filtering='no automatic selection; six named volcano labels only',uncertainty='no CI; distribution rectangle is Q1-Q3',
             interpretation_limit='Software and layout test only; no biological or clinical claim',synthetic=TRUE)
jobs <- list(
  list('a_volcano_basic',volcano,plot_volcano(volcano),7.8,4.8),
  list('b_volcano_editorial',volcano,plot_volcano_editorial(volcano,labels=focal),7.8,4.8),
  list('b2_volcano_marginal',volcano,plot_volcano_marginal(volcano,labels=focal),8.1,7.3),
  list('c_samples_basic',samples,plot_sample_points(samples,pal,'Illustrative log2 CPM'),7.1,4.8),
  list('d_sample_distribution',samples,plot_sample_distribution(samples,pal,'Illustrative log2 CPM'),7.1,4.8),
  list('e_composition_basic',composition,plot_composition(composition,cellpal),8.4,4.8),
  list('f_composition_panels',composition,plot_composition_panels(composition,pal,'synthetic sample',y_max=.5),8.4,6.4),
  list('g_enrichment_ratio',enrichment,plot_enrichment_lollipop(enrichment,'GeneRatio','ORA example | 200 query genes; fixed supplied terms','Overlap genes'),8.4,5.1),
  list('h_enrichment_NES',nes,plot_enrichment_lollipop(nes,'NES','GSEA example | supplied ranking and sets','Leading-edge genes'),8.4,5.1))
for(job in jobs) {
  files <- export_figure(job[[3]],job[[2]],out,job[[1]],meta,width=job[[4]],height=job[[5]])
  stopifnot(length(files)==6,all(file.exists(files)))
  rec <- jsonlite::read_json(file.path(out,job[[1]],paste0(job[[1]],'.json')))
  for(file in names(rec$output_sha256)) stopifnot(identical(digest::digest(file=file.path(out,job[[1]],file),algo='sha256'),rec$output_sha256[[file]]))
}
v <- ggplot2::ggplot_build(plot_volcano_editorial(volcano,labels=focal))
coords <- rbind(v$data[[3]][c('x','y')],v$data[[4]][c('x','y')])
expected <- data.frame(x=volcano$log2FC,y=-log10(volcano$padj))
stopifnot(isTRUE(all.equal(as.matrix(coords[order(coords$x,coords$y),]),as.matrix(expected[order(expected$x,expected$y),]),check.attributes=FALSE)))
stopifnot(all(v$data[[3]]$shape==16),all(v$data[[4]]$shape==16))
m <- plot_volcano_marginal(volcano,labels=focal)
stopifnot(identical(attr(m,'omics_spec')$kind,'volcano_marginal'),
          attr(m,'omics_spec')$point_count==nrow(volcano),
          sum(unlist(attr(m,'omics_spec')$status_counts))==nrow(volcano))
p <- plot_composition_panels(composition,pal,'synthetic sample')
stopifnot(isTRUE(all.equal(p$data$fraction,composition$count/ave(composition$count,composition$sample,FUN=sum))))
small <- plot_sample_distribution(samples[1:3,],pal,'value')
stopifnot(!any(vapply(small$layers,function(x)inherits(x$geom,'GeomRect'),FALSE)))
reject <- function(expr) {
  failed <- FALSE
  tryCatch(force(expr),error=function(e) failed <<- TRUE)
  if(!failed) stop('Invalid input was accepted')
}
reject(plot_volcano_editorial(volcano,labels='missing'))
reject(plot_volcano_editorial(volcano,labels=rep(focal[1],2)))
reject(plot_volcano_editorial(transform(volcano,padj=0)))
reject(plot_volcano_editorial(volcano,fc=0))
reject(plot_enrichment_lollipop(enrichment,'unknown','x','n'))
reject(plot_enrichment_lollipop(transform(enrichment,score=2),'GeneRatio','x','n'))
reject(plot_enrichment_lollipop(transform(enrichment,count=.5),'NES','x','n'))
reject(plot_enrichment_lollipop(enrichment,'NES','','n'))
reject(plot_composition_panels(composition[-1,],pal,'sample'))
reject(plot_composition_panels(transform(composition,count=0),pal,'sample'))
reject(plot_composition_panels(composition,pal,'sample',y_max=.1))
conflict <- composition; conflict$group <- c('Control',rep('Condition',nrow(composition)-1))
reject(plot_composition_panels(conflict,pal,'sample'))
reject(plot_sample_distribution(rbind(samples,samples[1,]),pal,'value'))
reject(plot_sample_distribution(samples,c(Control='#35618F'),'value'))
cat('PASS: 9 style/baseline bundles; 14 rejected inputs; exact volcano coordinates and composition fractions; small-n no-IQR; SHA256 verified\n')
