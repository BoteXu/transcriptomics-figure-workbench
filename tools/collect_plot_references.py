"""Read bounded public author code as inert text; never install or execute it."""
from pathlib import Path
import argparse,base64,concurrent.futures,hashlib,json,subprocess,time

# Repository, exact preferred source paths, and the relevant presentation idea.
SOURCES = [
('matplotlib/matplotlib',['galleries/examples/subplots_axes_and_figures/gridspec_customization.py'],'Physical guide lanes and unequal panel proportions'),
('mwaskom/seaborn',['examples/many_facets.py','seaborn/axisgrid.py'],'Data-count-driven facet wrapping and shared guides'),
('thomasp85/patchwork',['R/plot_layout.R'],'Explicit layout areas, guide collection and spanning panels'),
('wilkelab/cowplot',['R/align_plots.R'],'Align actual plotting regions rather than outer image boxes'),
('slowkow/ggrepel',['R/geom-text-repel.R'],'Bounded label separation with source-point leader lines'),
('mjskay/ggdist',['R/geom_slabinterval.R'],'Separate supplied density, point and uncertainty channels'),
('eclarke/ggbeeswarm',['R/geom-beeswarm.R'],'Display-only point separation without hiding observations'),
('RainCloudPlots/RainCloudPlots',['tutorial_python/raincloud_tutorial_python.ipynb','README.md'],'Half-distribution, observations and intervals in a balanced lane'),
('krassowski/complex-upset',['R/upset.R'],'Aligned intersection matrix and independent count axes'),
('jokergoo/ComplexHeatmap',['R/Heatmap-layout.R'],'Measured annotation allocation and split matrix spacing'),
('jokergoo/circlize',['R/chordDiagram.R'],'Explicit sector order, gaps and readable outer labels'),
('jokergoo/EnrichedHeatmap',['R/EnrichedHeatmap.R'],'Aligned profile annotations and matrix scales'),
('junjunlab/GseaVis',['R/gseaNb.R'],'Compact multi-track enrichment and pathway annotations'),
('YuLab-SMU/enrichplot',['R/gseaplot.R'],'Aligned enrichment score, hits and ranked metric'),
('kevinblighe/EnhancedVolcano',['R/EnhancedVolcano.R'],'Selected labels, quiet background and explicit thresholds'),
('enblacar/SCpubr',['R/do_FeaturePlot.R'],'Consistent embedding extent, legends and split panels'),
('samuel-marsh/scCustomize',['R/Plotting_Seurat.R'],'Point visibility, rasterization and explicit expression scales'),
('dzhang32/ggtranscript',['R/geom_range.R'],'Aligned exons, introns and complete transcript identities'),
('kassambara/survminer',['R/ggsurvplot_core.R'],'Survival and at-risk table alignment with common time'),
('NightingaleHealth/ggforestplot',['R/forestplot.R'],'Effect intervals and aligned row-wise annotation columns'),
('LSYS/forestplot',['forestplot/plot.py'],'Flexible forest labels, annotations and row spacing'),
('thomasp85/ggraph',['R/geom_edge_link.R'],'Quiet edges, readable nodes and explicit graph direction'),
('thomasp85/ggforce',['R/facet_wrap_paginate.R'],'Complete facet pagination with explicit page coverage'),
('paleolimbot/ggspatial',['R/annotation-scale.R'],'Physical spatial scale guides and declared coordinates'),
('has2k1/plotnine',['plotnine/facets/facet_wrap.py'],'Panel-count-derived rows, columns and edge labels'),
('nanxstats/ggsci',['R/discrete-npg.R'],'Discrete palette capacity and stable identity mapping'),
('garrettj403/SciencePlots',['src/scienceplots/styles/science.mplstyle'],'Restrained line, font and export defaults'),
]


def api(endpoint):
    failure=None
    for attempt in range(2):
        p=subprocess.run(['gh','api',endpoint],capture_output=True,timeout=40)
        if p.returncode==0:
            if len(p.stdout)>8_000_000:raise ValueError('Public reference response exceeds bounded budget')
            return json.loads(p.stdout)
        failure=p.stderr.decode(errors='replace')[-200:]
        if '404' in failure:break
        time.sleep(.5)
    raise ValueError(failure)


def collect(source,out):
    repo,paths,idea=source;folder=out/repo.replace('/','--');folder.mkdir()
    record=dict(repository=repo,url='https://github.com/'+repo,idea=idea,execution='NEVER_EXECUTED',vendored=False,status='UNREAD')
    try:
        meta=api('repos/'+repo)
        record['license_spdx']=(meta.get('license') or {}).get('spdx_id','UNRESOLVED')
        record['author']=meta['owner']['login']
        commit=api('repos/'+repo+'/commits/HEAD')['sha'];record['commit']=commit
        content=None
        for path in paths:
            try:content=api('repos/'+repo+'/contents/'+path+'?ref='+commit);break
            except ValueError:continue
        if not content or 'content' not in content:raise ValueError('Preferred code path unavailable; manual source selection required')
        payload=base64.b64decode(content['content']);assert len(payload)<=600_000,'Source text exceeds bounded review size'
        text=payload.decode('utf-8');assert '\x00' not in text
        (folder/'source.txt').write_bytes(payload)
        record.update(status='SOURCE_RETRIEVED_REVIEW_PENDING',source_path=path,source_url='https://github.com/'+repo+'/blob/'+commit+'/'+path,source_sha256=hashlib.sha256(payload).hexdigest(),source_bytes=len(payload),lines=len(text.splitlines()),code_redistribution='Not copied into the skill; inspect licence before any later reuse')
    except Exception as e:record.update(status='SOURCE_GAP',gap=str(e)[:250])
    (folder/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def main(out):
    out.mkdir(parents=True,exist_ok=False);records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(collect,s,out) for s in SOURCES]
        for f in concurrent.futures.as_completed(futures):
            r=f.result();records.append(r);print(r['repository']+' '+r['status'],flush=True)
            (out/'manifest.json').write_text(json.dumps(dict(records=records,read_only_public_sources=True,code_executed=False),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.output)
