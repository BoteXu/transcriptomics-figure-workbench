pkgs <- c('ggplot2','jsonlite','svglite','digest','systemfonts','patchwork','ComplexHeatmap','Seurat','SeuratExtend','SCpubr','enrichplot','clusterProfiler','hdWGCNA','CellChat','nichenetr','ggraph','ComplexUpset','pROC')
cat('R:',R.version.string,'\nLibraries:',paste(.libPaths(),collapse='; '),'\n')
for (p in pkgs) {
  ok <- requireNamespace(p,quietly=TRUE)
  cat(p,if(ok)as.character(utils::packageVersion(p)) else 'NOT_AVAILABLE_IN_THIS_R',sep='\t'); cat('\n')
}
