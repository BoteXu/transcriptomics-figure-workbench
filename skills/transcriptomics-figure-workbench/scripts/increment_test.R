# Synthetic execution and rejection checks; use inputs created by increment_test.py.
args <- commandArgs(trailingOnly=TRUE)
script_arg <- grep('^--file=',commandArgs(),value=TRUE)
scripts <- dirname(normalizePath(sub('^--file=','',script_arg),mustWork=TRUE))
source(file.path(scripts,'figure_core.R'));source(file.path(scripts,'figure_general.R'));source(file.path(scripts,'figure_design.R'))
root <- normalizePath(args[1],mustWork=TRUE);out <- file.path(root,'r')
if(file.exists(out))stop('Fresh R output required');dir.create(out)
palette <- c('Group A'='#35618F','Group B'='#C45A2D','Group C'='#67A9A2')
tables <- setNames(lapply(33:37,function(i)read.delim(file.path(root,'inputs',paste0('P',i,'.tsv')),check.names=FALSE)),paste0('P',33:37))
calls <- list(P33=function(d)plot_xy_points(d,palette,'Supplied X','Supplied Y','Demo independent unit'),
 P34=function(d)plot_grouped_estimates(d,palette,'Supplied estimate','Supplied illustrative interval'),
 P35=function(d)plot_binned_distribution(d,palette,'Frozen bin boundaries','Demo units per group'),
 P36=function(d)plot_confusion_counts(d,'Demo held-out units'),P37=function(d)plot_density_ridges(d,palette,'Supplied score','Precomputed demo density'))
meta <- list(source='Synthetic fixture 20261005',palette=as.list(palette),input_unit='Supplied fixture rows',
 experimental_unit='No biological units; software fixture',contrast='Illustrative groups',denominator='All supplied fixture rows',
 model='No fitted model',limits='Explicit renderer semantics',filtering='No selection',uncertainty='Illustrative supplied intervals',
 interpretation_limit='Synthetic demonstration only',synthetic=TRUE)
for(id in names(tables)) {
 d <- tables[[id]];original <- d;p <- calls[[id]](d);hash <- attr(p,'omics_input_sha256')
 p <- apply_design(p,spine_mode='minimal',grid='none',legend_position='right')
 stopifnot(identical(hash,attr(p,'omics_input_sha256')),identical(d,original))
 export_figure(p,d,out,id,meta,width=180/25.4,height=115/25.4)
}
rejects <- function(f) {ok <- FALSE;tryCatch(f(),error=function(e)ok <<- TRUE);if(!ok)stop('Invalid input accepted')}
rejects(function()calls$P33(rbind(tables$P33,tables$P33[1,])))
rejects(function()calls$P34(tables$P34[-1,]))
bad <- tables$P34;bad$lower[1] <- 100;rejects(function()calls$P34(bad))
bad <- tables$P35;bad$left[2] <- .5;rejects(function()calls$P35(bad))
bad <- tables$P35;bad$count[1] <- -1;rejects(function()calls$P35(bad))
rejects(function()calls$P36(tables$P36[-1,]))
bad <- tables$P36;bad$count[1] <- .5;rejects(function()calls$P36(bad))
bad <- tables$P37;bad$x[2] <- bad$x[1];rejects(function()calls$P37(bad))
rejects(function()apply_design(calls$P33(tables$P33),label_pt=-2))
jsonlite::write_json(list(status='SYNTHETIC_PASS',r_bundles=5,invalid_input_checks=9,
 appearance_invariance='ggplot_build layer data and exact input stamp unchanged',limits='No R bbox/glyph auditor or Python manual named-layout parity'),file.path(root,'r_test_receipt.json'),auto_unbox=TRUE,pretty=TRUE)
cat('SYNTHETIC_PASS: 5 R bundles and 9 rejection checks\n')
