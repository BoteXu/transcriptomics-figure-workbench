"""Record inspected originals and connect design decisions to runnable examples.

This ledger records the actual inspection scope. It does not assert that every
reference depicts the same chart or that a journal rank proves visual quality.
No source image or third-party code is redistributed.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'skills/transcriptomics-figure-workbench/references'


def main():
    sources=[]
    def add(id,title,url,forms,adopt,reject,images=(),year=None,scope='same_chart_or_component',license_note='No image or code copied; original implementation'):
        sources.append(dict(id=id,title=title,url=url,forms=forms.split(),inspection='original_pixels_and_context',image_urls=list(images),year=year,reference_scope=scope,adopt=adopt,reject=reject,license_boundary=license_note))
    def paper(id,title,doi,figure,forms,adopt,reject,year=2025):
        add(id,title,'https://www.nature.com/articles/'+doi+'/figures/'+str(figure),forms,adopt,reject,year=year)
    paper('bonsai','Bonsai / Nature Biotechnology','s41587-026-03220-2',3,'hierarchy embedding feature-embedding dashboards','Whole-tree overview linked to a named local focus; persistent identity colours.','Do not refit a hyperbolic embedding or imply original tree coordinates.',2026)
    paper('droplet-hic','Droplet Hi-C / Nature Biotechnology','s41587-024-02447-1',2,'contact-tracks interval-tracks heatmap violin box profile','Physical coordinate alignment across contact, insulation and gene tracks; separate units.','Tiny enrichment labels and crowded ten-panel pages. Online 2024; 2025 issue is not a 2025 publication date.',2024)
    paper('migraine-finemap','Migraine fine mapping / Nature Communications','s41467-025-64880-3',2,'variant-posteriors genome-association-overview interval-tracks','Full-width locus context above aligned source-specific posterior tracks on a common physical x axis.','Do not derive a causal posterior or new credible set from a drawing.')
    paper('cytometric-gating','Automated cytometric gating / Nature Communications','s41467-025-56622-2',4,'gating scatter box point-interval','Stored gates over full density and common comparison axes; show observations beside summaries.','Overpacked comparison pages and long tiny tilted labels; no gating engine called.')
    paper('ms2crossion','MS2DeepScore cross-ion / Nature Communications','s41467-026-69083-y',3,'network mass-spectrum-mirror structures object-schematic joint','Network overview with readable local detail; mirror spectra around zero with explicit spectrum identity.','Do not copy the study edge threshold, infer peak matches or use tiny linked structures.',2026)
    paper('retina-rna-atac','Human retina RNA and ATAC / Nature Genetics','s41588-025-02454-1',5,'heatmap correlation interval-tracks reference-aligned-tracks feature-embedding','Block identities and physically aligned coverage, peaks and genes.','Overcompressed labels and rainbow dendrogram decoration. DOI year recorded; publication date not inferred.')
    paper('cortical-grn','Cortical cell-fate regulatory networks / Nature','s41586-025-09997-7',5,'dot-matrix stacked composition reference-strip-effects bars','Aligned marker-fraction/mean matrix and identity-count sidebars; separate species and culture conditions.','Repeated tiny UMAPs and an overpacked ten-panel page; cells do not replace donors.')
    paper('temporal-fields','Temporal tissue dynamics / Nature','s41586-025-09876-1',2,'supplied-vector-field field reference-surface-grid','Common scenario coordinates and visible vector heads; distinguish stable and unstable symbols.','No inferred streamlines, nullclines or fitted dynamics. Viewed publisher 685-pixel original preview; fine print not assessed.')
    paper('apobec-rainfall','APOBEC3 mutagenesis / Nature Genetics / Extended Data 3','s41588-025-02187-1',8,'rainfall donut swimmer-followup','Shared genomic position, log inter-event distance, restrained background events, distinct event classes.','Do not infer clusters from appearance or carry mutation distances across chromosomes; whole figure is too dense for reuse.')
    add('circular-bars','Tobias Stadler / circular bar example','https://r-graph-gallery.com/web-circular-barplot-with-R-and-ggplot2.html','annular radial-effects term-circle radar','Keep a central hole, restrained colour, direct external labels and explicit secondary quantity.','Prefer aligned linear effects for precise comparisons; do not make radial area represent an unlabelled statistic.',images=['https://r-graph-gallery.com/web-circular-barplot-with-R-and-ggplot2_files/figure-html/unnamed-chunk-8-1.png'],year=2020)
    base='https://clauswilke.com/dataviz/'
    restrictive='Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.'
    def book(id,title,page,forms,adopt,reject,images):
        add(id,'Claus O. Wilke / '+title,base+page+'.html',forms,adopt,reject,[base+x for x in images],2019,license_note=restrictive)
    book('wilke-distributions','Boxplots and violins','boxplots-violins','box violin raincloud scatter point-interval ridges reference-group-beeswarm','Retain individual observations; categorical displacement changes no measurement; shared density x scale.','Do not estimate a new density or distribution from a polished contour.',['boxplots_violins_files/figure-html/lincoln-temp-sina-1.png','boxplots_violins_files/figure-html/temp-ridgeline-1.png'])
    book('wilke-ecdf','ECDF and quantile comparisons','ecdf-qq','distribution-ecdf qq histogram residual-diagnostics','Related density and ECDF share a horizontal range; QQ uses an identity reference and complete tails.','A reference line does not establish normality; no automatic tail clipping.',['visualizing_distributions_II_files/figure-html/county-populations-log-1.png','visualizing_distributions_II_files/figure-html/county-populations-qq-1.png'])
    book('wilke-uncertainty','Uncertainty displays','visualizing-uncertainty','forest point-interval effect-distribution ribbon funnel-supplied-results waffle','Nested intervals have an explicit hierarchy; retain estimates, reference values and exact count cells.','Do not fabricate intervals or a density; funnel usage borrows interval hierarchy, not a same-chart exemplar.',['visualizing_uncertainty_files/figure-html/confidence-visualizations-1.png','visualizing_uncertainty_files/figure-html/probability-waffle-1.png'])
    book('wilke-proportions','Proportion comparisons','visualizing-proportions','stacked composition donut bars','Small multiples share a 0–100% scale with a pale full denominator.','Author-labelled bad stacked-middle-category example is a rejection example, not a recommendation.',['visualizing_proportions_files/figure-html/marketshare-stacked-1.png','visualizing_proportions_files/figure-html/marital-vs-age-proportions-1.png'])
    book('wilke-time','Time series and connected scatter','time-series','profile ribbon rank connected-scatter horizon reference-parallel-trials','Name line endpoints directly; sparse milestones retain a traceable order.','Do not smooth stored vertices or treat an arbitrary order as time; parallel/horizon borrowing is related label design only.',['time_series_files/figure-html/bio-preprints-direct-label-1.png','time_series_files/figure-html/house-price-path-1.png'])
    book('wilke-nested','Nested proportions','nested-proportions','mosaic flow hierarchy membership-links','Mosaic width retains denominators; conserved bands and ordered labelled nodes reduce lookup.','Author-labelled ugly parallel-sets plot is rejected. Do not inflate small or zero paths.',['nested_proportions_files/figure-html/bridges-mosaic-1.png','nested_proportions_files/figure-html/bridges-parallel-sets2-1.png','nested_proportions_files/figure-html/bridges-parallel-sets3-1.png'])
    book('wilke-associations','Associations','visualizing-associations','correlation paired rank scores feature-correlation-projection ma ranked-effects','Explicit signed colour/area scales; direct slope endpoints; fixed comparison axes.','A projection is not causal evidence. MA borrowing concerns precise Cartesian comparisons, not a same-chart example.',['visualizing_associations_files/figure-html/forensic-correlations2-1.png','visualizing_associations_files/figure-html/CO2-slopegraph-three-year-1.png'])
    book('wilke-maps','Geospatial displays','geospatial-data','maps geographic-links','A restrained ordered scale and clearly declared coordinate/projection context.','Avoid aspect distortion; raw longitude/latitude links are not geodesics.',['geospatial_data_files/figure-html/median-income-counties-binned-1.png'])
    book('wilke-panels','Multi-panel figures','multi-panel-figures','composition dashboards state-matrix registration slice structures palettes object-schematic decision reference-aligned-tracks','Weighted panel spans follow the question; persistent colours and one clear reading order; retain full standalone reading views.','Do not infer a shared cohort, axis or legend from mere adjacency. These are related layout references, not identical chart exemplars.',['multi-panel_figures_files/figure-html/athletes-composite-good-1.png'])
    add('logomaker','Ammar Tareen and Justin B. Kinney / Logomaker examples','https://logomaker.readthedocs.io/en/latest/examples.html','sequence-logo','Separate probability, bits and signed enrichment; explicit zero reference and highlighted supplied positions.','Do not replace a supplied height definition with information content or enable signed heights without an explicit contract.',images=['https://logomaker.readthedocs.io/en/latest/_images/ss_probability_logo.png','https://logomaker.readthedocs.io/en/latest/_images/ars_enrichment_logo.png'],year=2026)
    add('shap-beeswarm','SHAP authors / beeswarm example','https://shap.readthedocs.io/en/stable/example_notebooks/api_examples/plots/beeswarm.html','contribution','Complete individual signed contributions, zero reference and separate supplied feature-value scale.','Do not silently sum unnamed features, refit a model or calculate attribution.',images=['https://shap.readthedocs.io/en/stable/_images/example_notebooks_api_examples_plots_beeswarm_3_0.png'])
    add('shap-waterfall','SHAP authors / waterfall example','https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/plots/waterfall.html','contribution-waterfall','Exact signed component labels and explicit baseline-to-total accounting.','No new SHAP calculation, feature ranking or unlabelled residual term.',images=['https://shap.readthedocs.io/en/latest/_images/example_notebooks_api_examples_plots_waterfall_3_0.png'])
    add('complex-upset','Michał Krassowski / ComplexUpset examples','https://krassowski.github.io/complex-upset/articles/Examples_R.html','upset venn','Align exact intersection counts, binary membership and inclusive set totals; separate rows with faint bands.','Do not imply Venn circle areas are proportional; do not discard all-zero objects.',images=['https://krassowski.github.io/complex-upset/articles/Examples_R_files/Examples_R_12_0.png','https://krassowski.github.io/complex-upset/articles/Examples_R_files/Examples_R_24_0.png'])
    add('cobalt-love','Noah Greifer / cobalt Love plot','https://ngreifer.r-universe.dev/cobalt/doc/love.plot.html','covariate-balance','Complete covariate names, declared thresholds, redundant shapes for adjustment stage and shared x scale.','Do not connect unrelated covariates as a continuous measurement, or declare balance from threshold alone.',year=2026)
    add('swimplot','Jessica Weiss / Creating swimmer plots with ease','https://mirror.metanet.ch/cran/web/packages/swimplot/vignettes/Introduction.to.swimplot.html','swimmer-followup','Individual follow-up rows, explicit event symbols and complete guides; stratification can replace a dense page.','No manufactured response duration, treatment segments or ongoing arrows; source uses example data.')
    add('circlize','Zuguang Gu / advanced chord diagram labels and gaps','https://jokergoo.github.io/circlize_book/book/advanced-usage-of-chorddiagram.html','chord','Separate sectors with controlled gaps, allow label room and retain an explicit weight key.','Do not infer direction or causality from ribbons; avoid red/green-only identity distinction.',images=['https://jokergoo.github.io/circlize_book/book/15-chord-diagram-advanced-usage_files/figure-html/chord-grouped4-1.png'])
    add('sklearn-pr','scikit-learn authors / precision-recall examples','https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html','precision-recall','Explicit staircase vertices, positive-class definition and a separately declared prevalence baseline.','Fold AP mean plus standard deviation is not a confidence interval. No AUC or curve fitting is performed.',images=['https://scikit-learn.org/stable/_images/sphx_glr_plot_precision_recall_003.png'])
    add('sklearn-roc','scikit-learn authors / multiclass ROC examples','https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html','roc calibration','Unit-square comparison axes, chance/identity guide and redundant model line styles.','Do not invent AUC, micro/macro averaging or uncertainty. Calibration borrows axis design, not the same statistic.',images=['https://scikit-learn.org/stable/_images/sphx_glr_plot_roc_003.png'])
    add('statsmodels-agreement','statsmodels authors / mean-difference plot','https://www.statsmodels.org/stable/generated/statsmodels.graphics.agreement.mean_diff_plot.html','bland-altman-supplied','Separate labelled bias and agreement-limit guides over complete observations.','Agreement limits are not confidence intervals of the mean. Retain supplied bounds without estimation.',images=['https://www.statsmodels.org/stable/_images/graphics-mean_diff_plot.png'])
    add('mpltern-axes','Yuji Ikeda / mpltern three coloured axes','https://mpltern.readthedocs.io/en/stable/gallery/axis_and_tick/98.colored_axes.html','ternary-composition','Readable 0 to 1 ticks on all three component axes and faint guides.','Do not infer a trajectory from unrelated example points; avoid strong coloured grids.',images=['https://mpltern.readthedocs.io/en/stable/_images/sphx_glr_98.colored_axes_001.svg'])
    add('ggtranscript-junction','Dylan Zhang and collaborators / ggtranscript junction example','https://github.com/dzhang32/ggtranscript','splice-tracks','Shared physical coordinates, named transcript lanes and supplied junction counts.','Do not shorten gaps without declaring a transformed axis or infer strand/isoform abundance.',images=['https://github.com/dzhang32/ggtranscript/raw/master/man/figures/README-geom-junction-pub-1.png'])
    add('specification-original','Simonsohn et al. / specification curve original Figure 2','https://www.nature.com/articles/s41562-020-0912-z/figures/2','specification-curve','Strict alignment of effect positions and declared model-decision cells.','Reject significance-coloured backgrounds and unreadable hundreds of labels. Viewed publisher original; screenshot edge truncation limits fine-print review.',images=['https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41562-020-0912-z/MediaObjects/41562_2020_912_Fig2_HTML.png'],year=2020)
    add('fold-confidence','Severe deviation in protein fold prediction / Scientific Reports Figure 1','https://www.nature.com/articles/s41598-025-89516-w/figures/1','residue-confidence','Explicit 0 to 100 local confidence scale and separate structural comparisons.','This source shows structure colouring and PAE, not an identical residue-profile chart. Local confidence is not domain-orientation or binding evidence.',year=2025,scope='related_confidence_scale_and_structure_comparison',images=['https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41598-025-89516-w/MediaObjects/41598_2025_89516_Fig1_HTML.png'])
    add('pathview-original','Weijun Luo and Cory Brouwer / Pathview Figure 1','https://pmc.ncbi.nlm.nih.gov/articles/PMC3702256/','pathway-quantity-overlay','Keep physical map identity, a separate quantitative key and explicit edge meanings.','Reject unreadable tiny nodes and red/green-only contrast. A coloured abundance map does not establish flux or activation.',images=['https://cdn.ncbi.nlm.nih.gov/pmc/blobs/71de/3702256/8b8cda485b9c/btt285f1p.jpg'],year=2013)
    prior=json.loads((REF/'journal-design-v092.json').read_text(encoding='utf8'))['sources']
    all_sources=prior+sources
    forms=json.loads((REF/'form-catalog.json').read_text(encoding='utf8'))['forms']
    inputs=json.loads((ROOT/'examples/source-v093-inputs-complete/manifest.json').read_text(encoding='utf8'))['records']
    calls={r['base_form']:r['adapter'] for r in inputs if '__' not in r['form']}
    decisions={r['form']:r for r in json.loads((REF/'journal-form-review-v092.json').read_text(encoding='utf8'))['records']}
    proof_path=ROOT/'examples/source-v093/review-ledger.json'
    proof=json.loads(proof_path.read_text(encoding='utf8')) if proof_path.is_file() else None
    reviewed={r['scope']+'/'+r['id']:r for r in proof['records']} if proof else {}
    sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
    from figure_workbench.registry import resolve
    records=[]
    for f in forms:
        matched=[s['id'] for s in all_sources if f['id'] in s.get('forms',[])]
        related=[s for s in all_sources if s['id'] in matched]
        example=f['id'] if f['id'] in calls or f['id'] in ['palettes','structures'] else 'Layout01_balanced-page-01'
        scope='single' if f['id']!='composition' else 'layout'
        review=reviewed.get(scope+'/'+example)
        records.append(dict(form=f['id'],title=f['title'],original_source_ids=matched,design_decision=decisions[f['id']]['decision'],
            adopted_designs=[dict(source=s['id'],adopt=s['adopt'],reject=s['reject']) for s in related],
            implementation=calls.get(f['id'],'fixed reference or complete-SVG layout'),
            implementation_file=('scripts/'+resolve(calls[f['id']])['module']+'.py') if f['id'] in calls else ('scripts/figure_workbench/layout.py' if f['id']=='composition' else 'tools/package_source_audit.py'),
            example=example,example_scope=scope,
            example_bundle=('assets/source-gallery/'+example) if scope=='single' else 'examples/source-v093/layout/Layout01_balanced',
            portable_spec=('assets/source-gallery/'+example+'/example.spec.json') if f['id'] in calls else None,
            reference_scope='Inspect each source note: some concern related layout or rejected alternatives, not an identical chart',
            implementation_state='DRAWING_CODE_AND_EXAMPLE_RENDERED' if f['id'] in calls else 'COMPLETE_PANEL_LAYOUT_EXPORTED' if f['id']=='composition' else 'DECLARED_FIXED_REFERENCE_LAYOUT',
            visual_review=review['decision'] if review else 'PENDING_EXACT_EXPORT_REVIEW',
            reviewed_png_sha256=review['png_sha256'] if review else None,scientific_acceptance=False))
    report=dict(schema_version=1,review_date='2026-10-17',new_sources=sources,prior_sources='journal-design-v092.json',forms=records,
                counts=dict(base_forms=len(forms),with_inspected_reference=sum(bool(r['original_source_ids']) for r in records)),
                limitations=['No universal beauty guarantee','No new scientific analysis','Publication prestige is not a quality test','Search-only or inaccessible images are not counted'],
                copied_source_images=False,copied_third_party_code=False,
                visual_review_scope='Exact current 405 PNGs; no calibrated paper proof, independent review or biomedical acceptance')
    (REF/'source-design-v093.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# 原图参考到代码与实际示例 · v0.9.3','',
        '90个合并图型均有实际查看过的原图或作者示例参考。新增34条来源，连同上一版8条图形记录共42条；一条来源可能包含数幅图。优先近两年的研究图，必要时采用更早且解释清楚的作者示例。相关组件、尺度或反面例子的借鉴不冒充同图型原图。','',
        '本轮96个单图视图、261个三档数据量变体、48个完整面板布局共405份最终PNG已经逐张自检。单图中的87种原生图型、7个同型扩展、2个固定参考图，加上组图布局构成90个基础条目。没有增加90套算法。保留已有优点的画法也重新出图检查，不为凑数量改写。','',
        '[当前完整单图与可运行配置](../assets/source-gallery/index.html) · [精确验收边界](validation-v093.md) · [90项机器可读映射](source-design-v093.json)','',
        '## 使用顺序','',
        '先判断研究问题、独立单位和现有结果字段，再选图型与一个必要扩展；随后明确顺序、尺度、颜色语义和物理布局。原生示例目录中的 `example.spec.json` 可以经统一 `plan`、`render` 接口复现。三档数据量示例和48种布局在仓库 `examples/source-v093/`，其参数及输入同样可检查。','',
        '对密集带符号网络优先矩阵，明确遮罩未报告单元；小网络保留圆形扩展。二维完整网格优先于遮挡的三维曲面。组成分面对比保留统一100%分母；ROC/PR可用分面和供应区间，示例供应界限不是置信区间。径向图不替代精确的线性效应比较。单图或组图换数据、标签、尺寸、行列后重新审图。','',
        '## 每种图的实现与实例','',
        '| 基础图型 | 已查看来源编号 | 实际实现 | 完整示例 |','|---|---|---|---|']
    for r in records:
        example=('[打开](../assets/source-gallery/'+r['example']+'/'+r['example']+'.svg)') if r['example_scope']=='single' else '[组图实例](https://github.com/BoteXu/transcriptomics-figure-workbench/tree/main/examples/source-v093/layout)'
        code=r['implementation_file'];link=('../'+code) if code.startswith('scripts/') else 'https://github.com/BoteXu/transcriptomics-figure-workbench/blob/main/'+code
        lines.append('| '+r['title']+' · `'+r['form']+'` | '+', '.join('['+x+'](#'+x+')' for x in r['original_source_ids'])+' | ['+r['implementation']+']('+link+') | '+example+' |')
    lines+=['','## 来源、采用和舍弃','']
    for s in all_sources:
        lines+=['<a id="'+s['id']+'"></a>','', '### '+s['title'],'',
            '[原始来源]('+s.get('figure_url',s['url'])+')','',
            '- 采用：'+s['adopt'],'- 舍弃或边界：'+s['reject'],
            '- 审阅范围：'+s.get('reference_scope','Original figure and caption; related components require contextual interpretation'),
            '- 代码与图片：'+s.get('license_boundary','No image or code copied; independently authored implementation'), '']
    (REF/'source-design-v093.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf8')
    print(json.dumps(report['counts']));print('Uncovered: '+', '.join(r['form'] for r in records if not r['original_source_ids']))


if __name__=='__main__':main()
