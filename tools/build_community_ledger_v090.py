"""Publish selected source identities and design decisions, never source code."""
import argparse,json
from pathlib import Path
DECISIONS={
'matplotlib/matplotlib':('3-12, 17-26','Reserve explicit panel and guide regions','Reject fixed example row counts as a universal design'),
'mwaskom/seaborn':('Selected facet setup windows','Keep scales and identity consistent across facets','Do not fit distributions or regressions merely for styling'),
'thomasp85/patchwork':('111-120, 130-139','Explicit spans, column weights and layout constraints','Do not infer shared guides from appearance'),
'wilkelab/cowplot':('46-55, 104-113','Align complete plot regions and their surrounding guides','Do not crop labels to force alignment'),
'slowkow/ggrepel':('177-186, 226-235','Sparse selected labels and restrained connectors','Do not label every point or discard data to resolve overlap'),
'mjskay/ggdist':('238-255','Separate supplied distribution and interval channels','Do not estimate density or uncertainty inside a style adapter'),
'eclarke/ggbeeswarm':('96-104','Separate mark placement from quantitative values','Do not move the quantitative axis or imply pairing'),
'RainCloudPlots/RainCloudPlots':('Selected notebook source windows','Combine observations, supplied distribution and summaries','A decorative cloud cannot replace independent observations'),
'krassowski/complex-upset':('977-994','Align intersection identity with counts and membership matrix','Do not equate inclusive and exclusive intersections'),
'jokergoo/ComplexHeatmap':('93-102, 106-115','Reserve annotation and guide lanes around the full matrix','Do not cluster or rescale silently'),
'jokergoo/circlize':('1090-1103','Use explicit unique names for group identity','Prefer an aligned linear extension for crowded comparisons'),
'jokergoo/EnrichedHeatmap':('694-708','Make annotation extent part of the layout','Do not infer biological alignment from visual alignment'),
'junjunlab/GseaVis':('117-126, 811-820','Coordinate ES, hit tracks and ranked metric','Do not reconstruct missing GSEA curves or substitute NES for ES'),
'YuLab-SMU/enrichplot':('80-95','Keep enrichment channels and plot modes explicit','Do not treat all enrichment plot types as interchangeable analyses'),
'kevinblighe/EnhancedVolcano':('890-905','Use selective labels with restrained connectors','Do not change thresholds for a more dramatic volcano'),
'enblacar/SCpubr':('56-65, 172-181','Stable feature-map identity and consistent presentation','Do not infer cell labels or recompute an embedding'),
'samuel-marsh/scCustomize':('566-581','Control point visibility, raster policy and facet columns','Do not inherit a fixed point size across sparse and dense inputs'),
'dzhang32/ggtranscript':('81-96','Separate exon, CDS and intron channels and coordinates','Do not invent strand or transcript structure'),
'kassambara/survminer':('305-320','Keep risk-table height and curve guides explicit','Do not refit survival curves or derive tests for appearance'),
'NightingaleHealth/ggforestplot':('249-264','Keep supplied intervals, estimates and shape meaning distinct','Do not synthesize intervals from significance'),
'LSYS/forestplot':('63-72, 114-123','Align label, interval and numerical columns','Do not collapse incompatible effect scales'),
'thomasp85/ggraph':('219-239','Keep source, target and edge semantics explicit','Do not prune inconvenient edges or infer mechanism'),
'thomasp85/ggforce':('76-100','Paginate full facets with explicit coverage','Do not approve a page that silently drops facets'),
'paleolimbot/ggspatial':('299-318','Bind a physical scale to projection and units','A map scale is not universally accurate over a projection'),
'has2k1/plotnine':('298-333','Derive capacity from data and reject undersized grids','Do not silently ignore custom row or column requests'),
'nanxstats/ggsci':('23-32, 57-66','Keep named palette identity and capacity explicit','Do not cycle a palette through too many categories'),
'garrettj403/SciencePlots':('Complete selected style file','Quiet lines, whitespace and restrained legends','Reject a fixed canvas, mandatory LaTeX or mandatory serif font'),
}


def build(source,out):
    rows=[]
    for path in sorted(source.glob('*/receipt.json')):
        r=json.loads(path.read_text(encoding='utf8'));repo=r['repository']
        if repo not in DECISIONS or not r.get('source_sha256'):continue
        scope,adopt,reject=DECISIONS[repo]
        rows.append(dict(repository=repo,author=r.get('author'),url=r['url'],commit=r['commit'],source_path=r['source_path'],source_url=r['source_url'],source_sha256=r['source_sha256'],declared_license=r.get('declared_license',r.get('license_spdx','UNRESOLVED')),inspection_scope=scope,adopted_design=adopt,rejected_or_bounded=reject,implementation='Independent frozen-table implementation or retained design principle; no third-party code copied',native_package_executed=False,redistributed_source=False))
    if len(rows)!=27:raise ValueError('Expected all 27 pinned source identities')
    out.mkdir(parents=True,exist_ok=True)
    (out/'community-sources-v090.json').write_text(json.dumps(dict(sources=rows,scope='Selected read-only source passages; not a full source/security/license audit',native_backend_validation=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    text=['# Community source review and design decisions','',
        'Twenty-seven primary author repositories were retrieved as inert text and inspected in the stated limited scope. No source was executed or copied into this skill. These are design references, not 27 installed backends or 27 new plot methods. Unknown or restrictive licences remain a barrier to copying code. Existing algorithms and authors retain their attribution.','',
        'The [machine-readable ledger](community-sources-v090.json) pins each commit, selected path and exact source hash. Line ranges refer to that pinned file; a selected-window review is not a full implementation audit.','',
        '| Author source | Inspected scope | Adopted design | Rejected or bounded |','|---|---|---|---|']
    for r in rows:text.append('| ['+r['repository']+']('+r['source_url']+') | '+r['inspection_scope']+' | '+r['adopted_design']+' | '+r['rejected_or_bounded']+' |')
    text+=['','## Practical changes','',
        'The workbench applies these principles through complete panel guide lanes, measured caption separation, adaptive point visibility, explicit category colours, long-label linear profile extensions, flexible facets, full SVG reflow and source-bound study figure sets. Supplied effect, uncertainty, membership, coordinate and denominator channels remain distinct.','',
        'Synthetic tests and a small CC0 Palmer Penguins example assess drawing, quantity coverage and layout. They do not validate a biomedical analysis backend, statistical method or scientific conclusion. See the release validation record for the actual visual scope.']
    (out/'community-designs-v090.md').write_text('\n'.join(text)+'\n',encoding='utf8');print(json.dumps(dict(sources=len(rows),code_copied=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.source_dir,a.output)
