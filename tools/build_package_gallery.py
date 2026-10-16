"""Prepare synthetic display fixtures, then render frozen tables. No scientific engines.

Curves, effects, probabilities, densities and coordinates below are illustrative
display constants/geometry, never outputs of GSEA, DESeq2, UMAP or other analysis.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan,META_FIELDS
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest
from figure_workbench.methods import prepare_method_spec,catalog_methods


def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def table(p,rows):
    columns=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,delimiter='\t');w.writeheader();w.writerows(rows)


def fixtures():
    cases=[]
    def add(rows,**options):cases.append((rows,options))
    names=['Interferon response','Oxidative metabolism','Matrix organization','RNA processing']
    # Display geometry only, deliberately hand-shaped curves. Not valid for inference.
    knots=[[0,.12,.27,.43,.57,.64,.61,.57,.50,.44,.36,.29,.20,.12,.05,0],
           [0,-.04,-.09,-.16,-.23,-.30,-.39,-.47,-.56,-.64,-.70,-.61,-.44,-.26,-.10,0],
           [0,.07,.18,.29,.37,.45,.49,.46,.42,.36,.28,.23,.16,.08,.03,0]]
    curves=[]
    for k in range(3):
        for i in range(240):
            pos=i*15/239;at=min(int(pos),14);fraction=pos-at
            # Linear construction of a synthetic display fixture, never of real results.
            val=knots[k][at]*(1-fraction)+knots[k][at+1]*fraction + (0 if i in [0,239] else .008*((i%5)-2))
            curves.append(dict(kind='curve',pathway=names[k],rank=i+1,value=round(val,6)))
        hits=([5,9,14,18,23,28,34,39,43,48,54,59,64,69,76,83,91,104,121,139,161,184,210,231] if k!=1 else [12,32,54,70,86,104,122,141,151,159,167,173,179,184,189,194,199,205,211,217,222,228,234,239])
        for j,r in enumerate(hits):curves.append(dict(kind='hit',pathway=names[k],rank=r,gene=(['STAT1','IRF7','ISG15','MX1'][j] if j<4 and k==0 else 'DEMO_'+str(k)+'_'+str(j)),leading_edge=int((r<=83) if k!=1 else (r>=167))))
        curves.append(dict(kind='summary',pathway=names[k],NES=[1.92,-1.76,1.53][k],padj=[.0008,.003,.014][k],set_size=len(hits)))
    curves.extend(dict(kind='metric',rank=i+1,value=round(4.2-8.4*i/239+.15*math.sin(i*.04),5)) for i in range(240))
    shared=dict(ranked_universe=240,metric_label='Rank metric',contrast='Illustrative condition B versus A',gene_set_version='Synthetic gene sets v2 (not MSigDB)')
    for selection,mode in [([0],'classic'),([0,1],'overlay'),([0,1,2],'facets'),([1],'classic')]:
        chosen=[names[i] for i in selection];q=[r for r in curves if r.get('pathway') in chosen or r['kind']=='metric']
        add(q,**shared,curve_order=chosen,mode=mode,title='Gene set enrichment' if mode=='classic' else 'Enrichment programmes · '+mode,gene_labels=['STAT1','ISG15'] if selection==[0] else [])
    contrasts=['B versus A','C versus A','D versus A','E versus A'];terms=names+['Cell cycle','Vesicle transport','DNA repair','Lipid metabolism']
    values=[[1.92,1.32,-.6,1.1],[-1.76,-1.2,.9,-1.5],[1.53,.2,1.8,.6],[-.8,1.1,.4,-.7],[.5,1.7,-1.5,1.1],[1.2,-.6,.7,1.6],[-1.4,.6,1.1,-.2],[.7,-1.8,None,1.4]]
    add([dict(pathway=t,contrast=c,status='not_tested' if values[i][j] is None else 'reported',NES=values[i][j],padj=None if values[i][j] is None else [.003,.018,.12,.038][(i+j)%4],set_size=None if values[i][j] is None else [42,68,27,53][i%4]) for i,t in enumerate(terms) for j,c in enumerate(contrasts)],pathway_order=terms,contrast_order=contrasts,nes_limits=[-2,2],size_max=80,title='Enrichment across contrasts')
    genes=['STAT1','IRF7','ISG15','MX1','NDUFA1','COX5A','ATP5F1','COL1A1','FN1','MMP2','SRSF1','DDX5']
    add([dict(pathway=p,gene=g,member=int(j//3==i or (i+j)%7==0),leading_edge=int((j//3==i or (i+j)%7==0) and j%3!=2),value=[1.4,1.1,.9,1.6,-.9,-1.2,-.7,1.3,.6,1.1,.7,-.6][j]) for i,p in enumerate(names) for j,g in enumerate(genes)],pathway_order=names,gene_order=genes,value_limits=[-2,2],value_label='Supplied log2 effect',title='Leading-edge membership')
    ora_terms=['Interferon signalling','Extracellular matrix','Oxidative phosphorylation','RNA splicing','Vesicle-mediated transport','DNA repair','Lipid biosynthesis','Cell-cycle transition']
    ora=[dict(term=t,count=n,query_size=180,padj=p) for t,n,p in zip(ora_terms,[48,42,36,31,27,23,18,14],[.00001,.00008,.0004,.001,.006,.013,.026,.09])]
    for mode in ['bubble','lollipop']:add(ora,term_order=ora_terms,background_definition='Synthetic universe n=1,000',ratio_max=.32,significance_max=5,mode=mode,title='Over-represented programmes')
    density=[]
    profiles=[[0,0,.02,.08,.20,.45,.72,.88,.77,.53,.25,.09,.02,0,0,0,0], [0,0,0,.01,.04,.12,.30,.58,.81,.89,.70,.41,.18,.05,.01,0,0], [0,.01,.05,.15,.38,.65,.83,.75,.51,.26,.10,.03,0,0,0,0,0], [0,0,0,0,.01,.04,.13,.31,.57,.79,.87,.71,.43,.19,.05,.01,0], [0,.03,.12,.32,.61,.80,.78,.55,.29,.11,.03,0,0,0,0,0,0]]
    for p,profile in zip(ora_terms,profiles):
        for j in range(129):
            position=j/8;at=min(int(position),15);mix=(1-math.cos(math.pi*(position-at)))/2
            density.append(dict(group=p,x=-4+j/16,density=round(profile[at]*(1-mix)+profile[at+1]*mix,6)))
    add(density,density_label='Illustrative frozen core-gene density profiles',x_label='Supplied gene-level statistic',title='Core enrichment distributions')
    def network(kind):
        if kind=='gene_term':
            labels=['Interferon','Matrix','Metabolism','STAT1','IRF7','ISG15','FN1','COL1A1','MMP2','NDUFA1','COX5A','ATP5F1'];positions=[(-1.2,.9),(1.2,.9),(0,-1.0),(-1.9,.25),(-1.6,-.3),(-.9,.05),(1.9,.25),(1.65,-.3),(.95,.05),(-.65,-1.55),(0,-1.75),(.65,-1.55)];groups=['Programmes']*3+['Response']*3+['Matrix']*3+['Energy']*3;edges=[(0,3),(0,4),(0,5),(1,6),(1,7),(1,8),(2,9),(2,10),(2,11),(0,6),(1,5)]
        elif kind=='similarity':
            labels=['Interferon','Antiviral','Cytokine','Matrix','Adhesion','Motility','Respiration','ATP synthesis','Lipid usage'];positions=[(-1.5,.8),(-.85,1.2),(-.65,.45),(1.15,.85),(1.8,.35),(1.0,-.1),(-.8,-1.1),(-.1,-1.6),(.5,-.85)];groups=['Immune']*3+['Matrix']*3+['Energy']*3;edges=[(0,1),(0,2),(1,2),(3,4),(3,5),(4,5),(6,7),(6,8),(7,8),(2,3),(5,8)]
        elif kind=='module':
            labels=['STAT1','IRF7','ISG15','MX1','OAS1','IFI6','GBP1','IFIT1','IFIT3','DDX58','SOCS1','IRF9'];positions=[(math.cos(i*math.tau/12),math.sin(i*math.tau/12)) for i in range(12)];groups=['Response']*6+['Regulation']*6;edges=[(i,(i+1)%12) for i in range(12)]+[(0,3),(0,5),(0,8),(3,7),(3,10),(5,9),(7,11)]
        else:
            labels=['Endothelial','Fibroblast','Myeloid','T cells','Cardiomyocyte'];positions=[(math.cos(math.pi/2-i*math.tau/5),math.sin(math.pi/2-i*math.tau/5)) for i in range(5)];groups=labels;edges=[(0,1),(0,2),(1,0),(1,4),(2,0),(2,1),(2,3),(3,2),(4,0)]
        rows=[dict(kind='node',node_id='n'+str(i),label=label,entity_type='term' if kind in ['gene_term','similarity'] and i< (3 if kind=='gene_term' else 9) else 'cell' if kind=='communication' else 'gene',group=groups[i],x=round(x,5),y=round(y,5),area=100 if kind!='gene_term' or i<3 else 48,label_dx=0,label_dy=.19 if kind!='module' else (.16 if y>=0 else -.16),label_align='center') for i,(label,(x,y)) in enumerate(zip(labels,positions))]
        rows.extend(dict(kind='edge',source='n'+str(a),target='n'+str(b),weight=[.35,.55,.8][i%3],sign=1) for i,(a,b) in enumerate(edges))
        return rows
    add(network('gene_term'),relation_semantics='membership',edge_label='Explicit gene-to-programme membership',node_area_label='Fixed display area',network_style='gene_term',title='Genes connecting biological programmes')
    add(network('similarity'),relation_semantics='overlap',edge_label='Supplied gene-set similarity',node_area_label='Fixed display area',network_style='similarity',title='Enrichment map · selected programmes')
    samples=['A1','A2','A3','A4','B1','B2','B3','B4'];annotation={s:('Condition A' if s[0]=='A' else 'Condition B') for s in samples}
    def heat(features,factor=1):return [dict(feature=f,sample=s,value=round(factor*((1 if j>=4 else -1)*[.65,.40,-.70,.55,-.45,.3,.8,-.6][i%8]+[.12,-.08,.06,-.04,.10,-.10,.04,-.06][j]),3)) for i,f in enumerate(features) for j,s in enumerate(samples)]
    add(heat(terms),row_order=terms,column_order=samples,column_groups=annotation,limits=[-1,1],scale_type='signed',y_label='GSVA score (demo)',title='Pathway scores across samples',subtitle='Illustrative frozen GSVA score matrix / no z-scaling')
    def volcano(protein=False):
        rows=[]
        for i in range(520):
            x=round(3.6*math.sin(i*2.39996)*((i%19+1)/20),4);strength=round(.10+(abs(x)**1.35)*(.35+(i%13)/9)+.4*(.5+.5*math.cos(i*1.7)),4)
            rows.append(dict(gene=('Protein_' if protein else 'Gene_')+str(i+1).zfill(3),log2FC=x,padj=10**(-strength)))
        for g,x,p in [('STAT1',2.8,1e-7),('ISG15',1.8,8e-6),('IRF7',3.2,2e-5),('COX5A',-2.7,3e-7),('NDUFA1',-1.7,4e-5)]:rows.append(dict(gene=g,log2FC=x,padj=p))
        return rows
    add(volcano(),title='Transcriptome response',subtitle='Illustrative DESeq2 result export / condition B versus A',label_genes=['STAT1','ISG15','IRF7','COX5A','NDUFA1'],effect_cutoff=1,alpha=.05)
    effects=[('STAT1',1.6,1.1,2.1),('IRF7',1.25,.72,1.78),('ISG15',1.1,.63,1.57),('FN1',.8,.25,1.35),('SRSF1',.32,-.15,.79),('COX5A',-.9,-1.4,-.4),('NDUFA1',-1.3,-1.85,-.75),('ATP5F1',-1.6,-2.18,-1.02)]
    add([dict(label=l,group='Higher' if v>0 else 'Lower',estimate=v,lower=lo,upper=hi) for l,v,lo,hi in effects],title='Gene-level differential effects',interval_label='Illustrative limma export / supplied 95% confidence intervals',x_label='log2 fold change',effect_scale='difference')
    add(volcano(True),title='Protein abundance response',subtitle='Illustrative MSstats result export / fixed protein-level effects',label_genes=['STAT1','COX5A','IRF7'],effect_cutoff=.75,alpha=.05)
    celltypes=['Endothelial','Fibroblast','Myeloid','T cells','Cardiomyocyte'];markers=['PECAM1','VWF','KDR','COL1A1','DCN','LUM','LYZ','CD68','CSF1R','CD3D','CD3E','TRAC','TNNT2','MYH6','ACTN2']
    add([dict(feature=g,group=c,fraction=round(.15+.72*((i//3)==j)+.04*((i+j)%3),2),value=round(.25+2.7*((i//3)==j)+.14*((i+j)%4),2)) for i,g in enumerate(markers) for j,c in enumerate(celltypes)],row_order=markers,column_order=celltypes,value_semantics='mean_all',denominator_label='Fraction denominator: all displayed cells in each identity (synthetic)',limits=[0,3.5],value_label='Mean expression',title='Marker expression by cell identity')
    centers=[(-2,1.3),(.0,2),(2.0,.7),(1.5,-1.8),(-1.3,-1.5)];coordinates=[]
    for k,(name,(cx,cy)) in enumerate(zip(celltypes,centers)):
        for i in range(160):
            angle=i*2.399963;radius=math.sqrt((i+.5)/160)
            coordinates.append(dict(cell_id='cell_'+str(k)+'_'+str(i),group=name,x=round(cx+.80*radius*math.cos(angle)+.18*radius*math.sin(angle*2),5),y=round(cy+.54*radius*math.sin(angle),5)))
    for package in ['Seurat','Scanpy']:add(coordinates,label_positions={n:[x,y+.72] for n,(x,y) in zip(celltypes,centers)},title='Cell identities · '+package,subtitle='Illustrative frozen embedding geometry / not a fitted UMAP',point_size=5.5,axis_prefix='UMAP')
    modules=['ME turquoise','ME blue','ME brown','ME yellow','ME green','ME red'];traits=['Phenotype','Age','Severity','Response'];association=[[.78,.12,.64,-.55],[-.68,.16,-.56,.61],[.31,.54,.22,-.16],[-.22,-.43,-.35,.17],[.45,.08,.51,-.42],[-.12,.38,.15,.09]]
    add([dict(row_id=r,column_id=c,association=association[i][j],pvalue=[.0003,.03,.12,.41][(i+j)%4]) for i,r in enumerate(modules) for j,c in enumerate(traits)],row_order=modules,column_order=traits,association_limits=[-1,1],association_definition='Illustrative donor-level module–trait correlation matrix',probability_definition='Parentheses: supplied unadjusted probabilities (demo)',title='Module–trait relationships')
    add(network('module'),relation_semantics='correlation',edge_label='Selected weighted co-expression edges',node_area_label='Fixed display area',network_style='module',title='Co-expression module · response genes')
    add(network('communication'),relation_semantics='predicted communication',edge_label='Supplied aggregate communication weight',node_area_label='Fixed display area',network_style='communication',directed=True,title='Predicted cell–cell communication')
    tfs=['STAT1','IRF7','NFKB1','JUN','FOXO1','MYC','HIF1A','PPARG']
    add(heat(tfs,2.5),row_order=tfs,column_order=samples,column_groups=annotation,limits=[-2.5,2.5],scale_type='signed',y_label='Activity score',title='Transcription factor activity',subtitle='Illustrative decoupleR export / supplied signed activity scores')
    paths=['JAK–STAT','NF-kB','MAPK','PI3K','TGF-beta','VEGF','Hypoxia','p53']
    add(heat(paths,2),row_order=paths,column_order=samples,column_groups=annotation,limits=[-2,2],scale_type='signed',y_label='Pathway activity',title='Signalling pathway activity',subtitle='Illustrative PROGENy export / fixed score units and sample order')
    survival=[]
    for name,vals,risks in [('Condition A',[1,.98,.95,.92,.88,.84,.80,.76,.72,.68,.64,.60,.56],[100,90,79,65,49,33,18]),('Condition B',[1,.99,.98,.96,.94,.91,.88,.85,.82,.79,.76,.73,.70],[100,94,85,73,60,44,27])]:
        for i,v in enumerate(vals):survival.append(dict(kind='step',group=name,time=i*2,survival=v,lower=max(0,v-.012-i*.006),upper=min(1,v+.012+i*.006)))
        for i,n in enumerate(risks):survival.append(dict(kind='risk',group=name,time=i*4,at_risk=n))
        for i in [3,6,9]:survival.append(dict(kind='censor',group=name,time=i*2+1,survival=vals[i]))
    add(survival,risk_convention='start_of_period',interval_definition='Illustrative supplied 95% confidence bands',time_label='Follow-up (months)',title='Survival over follow-up',subtitle='Synthetic outcome curves / no patient data or survival fitting')
    roc=[]
    for name,xy in [('Combined model',[(0,0),(.02,.22),(.05,.42),(.10,.59),(.16,.72),(.26,.82),(.4,.9),(.58,.96),(.8,.99),(1,1)]),('Clinical model',[(0,0),(.04,.16),(.10,.31),(.18,.47),(.3,.63),(.43,.75),(.59,.84),(.75,.92),(.9,.97),(1,1)])]:roc.extend(dict(group=name,x=x,y=y) for x,y in xy)
    add(roc,order=['Combined model','Clinical model'],title='Model discrimination',subtitle='Illustrative held-out ROC coordinates / no model training',auc_labels={'Combined model':'AUC text: 0.85 (illustrative)','Clinical model':'AUC text: 0.74 (illustrative)'})
    assert len(cases)==25
    return cases


def build(output,start=1):
    from project_theme import create_theme
    output.mkdir(parents=True,exist_ok=False);inputs=output/'inputs';inputs.mkdir();records=[]
    entries=catalog_methods()
    contract=dict(synthetic=True,source_definition='Original deterministic display fixtures; no scientific engine executed',independent_unit='No biological replicates; software display geometry only',denominator='Complete selected synthetic display grid or universe; explicit per-view channels',value_definition='Frozen illustrative effects, scores, probabilities, curves, coordinates and topology',uncertainty_definition='Supplied illustrative intervals only; no inference or interval estimation')
    for i,((rows,options),entry) in enumerate(zip(fixtures(),entries)):
        if i+1<start:continue
        key='PKG'+str(i+1).zfill(2);groups=[]
        for r in rows:
            for field in ['group','pathway']:
                if r.get(field) and r[field] not in groups:groups.append(r[field])
        if 'column_groups' in options:groups+=list(options['column_groups'].values())
        if entry['publication_view']=='dot':groups+=options['column_order']
        slots={g:j for j,g in enumerate(dict.fromkeys(groups or ['Display']))}
        if entry['publication_view']=='gsea':slots={'Interferon response':0,'Oxidative metabolism':1,'Matrix organization':2}
        theme=create_theme('synthetic-package-'+key,'package_editorial',slots,font_family='DejaVu Sans')
        # Existing named categorical palette remains source-bound. Continuous
        # colours are an original restrained teal/ivory/coral display ramp.
        theme['continuous']['diverging']=['#327D9F','#F7F7F4','#D8795B'];theme['continuous']['sequential']=['#E2EFEB','#6DB3A7','#1C6C70']
        provenance={k:'Synthetic display fixture only; not biological evidence' for k in META_FIELDS};provenance.update(synthetic=True,source=contract['source_definition'],contrast=options.get('contrast',options.get('subtitle','Illustrative software display')))
        p=inputs/(key+'.tsv');table(p,rows)
        template=dict(schema_version=1,figure_id=key,renderer='package_style',input=dict(path=p.name,sha256=digest(p)),parameters=dict(contract=contract,options=options),theme=theme,provenance=provenance,appearance=dict(preset='paper'))
        spec=prepare_method_spec(entry['id'],template,inputs,inputs/(key+'.spec.json'));write(inputs/(key+'.spec.json'),spec)
        try:render_plan(make_plan(spec,inputs),output)
        except Exception as exc:print(key+': '+str(exc),flush=True);raise
        receipt=output/key/(key+'.json');meta=json.loads(receipt.read_text());meta['source_file']='inputs/'+p.name;write(receipt,meta)
        records.append(dict(id=key,entry=entry['id'],view=entry['publication_view'],png_sha256=digest(output/key/(key+'.png')),source_sha256=digest(p),status='RENDERED_UNREVIEWED'))
        write(output/'manifest.json',dict(schema_version=1,records=records,scientific_acceptance=False,native_packages_executed=False));print(key+' '+entry['id']+' rendered',flush=True)
    cards=[]
    for r in records:
        k=r['id'];cards.append('<article id="'+k+'"><h2>'+r['entry']+'</h2><a href="'+k+'/'+k+'.svg"><img loading="lazy" src="'+k+'/'+k+'.png" alt="'+r['entry']+' synthetic example"></a><p>'+ ' · '.join('<a href="'+k+'/'+k+'.'+e+'">'+e.upper()+'</a>' for e in ['svg','pdf','tsv','json'])+' · <a href="inputs/'+k+'.spec.json">FigureSpec</a></p></article>')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Package figure gallery</title><style>body{font:16px/1.6 system-ui;color:#243449;background:#f2f5f6;max-width:1200px;margin:auto;padding:24px}article{background:white;margin:24px 0;padding:24px;border-radius:12px}img{display:block;max-width:100%;max-height:850px;margin:auto}a{color:#217f80}</style><h1>25 package-specific publication examples</h1><p>Original synthetic frozen display fixtures. No native package or scientific analysis executed. <a href="self-review.json">Individual visual review</a>; <a href="../../docs/package-styles-v040.md">Design and source references</a>.</p>'+''.join(cards),encoding='utf8')
    print(json.dumps(dict(status='PACKAGE_DISPLAYS_RENDERED',count=len(records),visual_acceptance=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--start',type=int,default=1);a=p.parse_args();build(a.output,a.start)
