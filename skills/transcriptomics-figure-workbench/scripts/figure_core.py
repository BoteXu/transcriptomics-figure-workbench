"""Newly authored static transcriptomics renderers; never run biological inference.

Accept reviewed pandas tables. Optional native AnnData APIs are documented separately.
"""
from pathlib import Path
import hashlib
import json
import platform
import re
import os
import shutil
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_rgba
import numpy as np
import pandas as pd

def table_bytes(data):
    """Hash and export exactly the same UTF-8 TSV bytes, including row order."""
    return data.to_csv(sep='\t', index=False, lineterminator='\n').encode('utf-8')

def file_sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''): digest.update(chunk)
    return digest.hexdigest()

def stamp(fig, data, kind, **spec):
    fig._omics_input_sha256 = hashlib.sha256(table_bytes(data)).hexdigest()
    fig._omics_spec = dict(kind=kind, **spec)
    return fig

def effect_reference(effect_scale):
    if effect_scale not in ('difference', 'log_ratio', 'ratio'):
        raise ValueError('Declare effect_scale: difference, log_ratio, or ratio')
    return 1 if effect_scale == 'ratio' else 0

def checked(data, columns, numeric=()):
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise ValueError('Expected nonempty DataFrame')
    if not set(columns).issubset(data.columns):
        raise ValueError('Missing required columns')
    if data[list(columns)].isna().any().any():
        raise ValueError('Missing values: report separately, never silently fill zero')
    for key in numeric:
        if not pd.api.types.is_numeric_dtype(data[key]) or not np.isfinite(data[key]).all():
            raise ValueError(f'Nonfinite/non-numeric: {key}')
    return data.copy()

def palette_check(values, palette):
    if not set(values).issubset(palette):
        raise ValueError('Palette missing categories')
    for color in palette.values():
        to_rgba(color)

def canvas():
    # rc_context avoids altering the caller's global configuration.
    with plt.rc_context({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42}):
        fig, ax = plt.subplots(figsize=(7.1, 4.5), layout='constrained')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(colors='#28323C')
    return fig, ax

def plot_embedding(data, palette, axis_prefix='UMAP'):
    d = checked(data, ['cell_id','x','y','group'], ['x','y'])
    if d.cell_id.duplicated().any():
        raise ValueError('Duplicate cell_id')
    palette_check(d.group, palette)
    fig, ax = canvas()
    for group in pd.unique(d.group):
        sub = d[d.group == group]
        ax.scatter(sub.x, sub.y, s=9, alpha=.85, color=palette[group], label=group, linewidths=0)
    ax.set(xlabel=f'{axis_prefix} 1', ylabel=f'{axis_prefix} 2', aspect='equal')
    ax.legend(loc='upper left', bbox_to_anchor=(1,1), frameon=False, markerscale=2)
    return stamp(fig, data, 'embedding', palette=palette, axis_prefix=axis_prefix)

def plot_samples(data, palette, y_label):
    d = checked(data, ['sample_id','group','value'], ['value'])
    if d.sample_id.duplicated().any():
        raise ValueError('One row per independent unit required')
    palette_check(d.group,palette)
    fig, ax = canvas()
    groups = list(pd.unique(d.group)); rng = np.random.default_rng(1)
    for i,g in enumerate(groups):
        vals = d.loc[d.group==g,'value']
        ax.scatter(i+rng.uniform(-.08,.08,len(vals)), vals, color=palette[g], s=36)
    ax.set_xticks(range(len(groups)),groups); ax.set_ylabel(y_label)
    return stamp(fig, data, 'samples', palette=palette, y_label=y_label)

def plot_forest(data, x_label, interval_label, *, effect_scale):
    d = checked(data,['label','estimate','lower','upper'],['estimate','lower','upper'])
    if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():
        raise ValueError('Duplicate labels or invalid interval')
    null = effect_reference(effect_scale)
    if effect_scale == 'ratio' and (d[['estimate','lower','upper']] <= 0).any().any():
        raise ValueError('Ratio estimates and bounds must be positive')
    fig, ax = canvas(); y = np.arange(len(d))
    ax.axvline(null,color='#929AA1',linestyle='--',linewidth=.7)
    if effect_scale == 'ratio': ax.set_xscale('log')
    ax.errorbar(d.estimate,y,xerr=np.array([d.estimate-d.lower,d.upper-d.estimate]),fmt='o',color='#35618F',capsize=3)
    ax.set_yticks(y,d.label); ax.invert_yaxis()
    ax.set(xlabel=x_label,title=interval_label)
    return stamp(fig, data, 'forest', effect_scale=effect_scale, null_value=null,
                 x_label=x_label, interval_label=interval_label)

def plot_volcano(data, alpha=.05, fc=1):
    d = checked(data,['gene','log2FC','padj'],['log2FC','padj'])
    if d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any():
        raise ValueError('Genes must be unique; padj in (0,1]; zero requires explicit display floor')
    if not (0<alpha<1 and np.isfinite(fc) and fc>0):
        raise ValueError('Invalid thresholds')
    colors = np.where((d.padj<=alpha)&(d.log2FC>=fc),'#B84E35',np.where((d.padj<=alpha)&(d.log2FC<=-fc),'#35618F','#BFC5CB'))
    fig, ax = canvas(); ax.scatter(d.log2FC,-np.log10(d.padj),c=colors,s=16,alpha=.8,linewidths=0)
    ax.axhline(-np.log10(alpha),color='grey',linestyle='--',linewidth=.6)
    for cut in [-fc,fc]: ax.axvline(cut,color='grey',linestyle='--',linewidth=.6)
    ax.set(xlabel='log2 fold change',ylabel='-log10(adjusted p)')
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([],[],marker='o',linestyle='',color=c,label=l) for l,c in [('Up','#B84E35'),('Down','#35618F'),('Other','#BFC5CB')]],frameon=False)
    return stamp(fig, data, 'volcano', alpha=alpha, fc=fc)

def plot_dot(data, value_label, *, value_semantics, denominator_label):
    d = checked(data,['feature','group','fraction','value'],['fraction','value'])
    if d.duplicated(['feature','group']).any() or ((d.fraction<0)|(d.fraction>1)).any():
        raise ValueError('Invalid dot table')
    if value_semantics not in ('mean_all', 'mean_detected', 'scaled', 'signed_effect'):
        raise ValueError('Declare dot color semantics')
    if not isinstance(denominator_label, str) or not denominator_label.strip():
        raise ValueError('A detection denominator label is required')
    groups = list(pd.unique(d.group)); features = list(pd.unique(d.feature))
    fig,ax=canvas()
    color_args = dict(cmap='Blues')
    if value_semantics in ('scaled','signed_effect'):
        extent = max(abs(d.value).max(), 1e-9)
        color_args = dict(cmap='RdBu_r', norm=TwoSlopeNorm(0,-extent,extent))
    dots=ax.scatter([groups.index(g) for g in d.group],[features.index(g) for g in d.feature],s=d.fraction*150,c=d.value,edgecolors='none',**color_args)
    ax.set_xticks(range(len(groups)),groups,rotation=45 if len(groups)>4 else 0,
                  ha='right' if len(groups)>4 else 'center')
    ax.set_yticks(range(len(features)),features)
    fig.colorbar(dots,ax=ax,label=value_label)
    handles=[ax.scatter([],[],s=f*150,color='#35618F',label=f'{f:.0%}') for f in [.25,.5,1]]
    ax.legend(handles=handles,title=denominator_label,loc='upper left',bbox_to_anchor=(1.3,1),frameon=False)
    ax.margins(.2)
    return stamp(fig, data, 'dot', value_label=value_label, value_semantics=value_semantics,
                 denominator_label=denominator_label, area='fraction')

def plot_heatmap(data, value_label, center=0, *, scale_type='signed'):
    d=checked(data,['feature','sample','value'],['value'])
    if d.duplicated(['feature','sample']).any(): raise ValueError('Duplicate matrix cells')
    if len(d)!=d.feature.nunique()*d['sample'].nunique(): raise ValueError('Incomplete heatmap grid')
    features=list(pd.unique(d.feature)); samples=list(pd.unique(d['sample']))
    mat=d.pivot(index='feature',columns='sample',values='value').reindex(index=features,columns=samples)
    fig,ax=canvas(); extent=max(abs(d.value.min()-center),abs(d.value.max()-center),1e-9)
    cmap=LinearSegmentedColormap.from_list('omics',['#35618F','#F7F7F5','#B84E35'])
    if scale_type not in ('signed','sequential'): raise ValueError('Unknown heatmap scale')
    im=ax.imshow(mat,aspect='auto',cmap=cmap if scale_type=='signed' else 'Blues',
                 norm=TwoSlopeNorm(center,center-extent,center+extent) if scale_type=='signed' else None)
    ax.set_xticks(range(len(samples)),samples,rotation=45,ha='right'); ax.set_yticks(range(len(features)),features)
    fig.colorbar(im,ax=ax,label=value_label)
    return stamp(fig, data, 'heatmap', value_label=value_label, scale_type=scale_type, center=center)

def plot_qc(data,y_label):
    d=checked(data,['cell_id','sample','value'],['value'])
    if d.duplicated(['cell_id','sample']).any(): raise ValueError('Duplicate cells within sample')
    groups=list(pd.unique(d['sample'])); fig,ax=canvas()
    ax.boxplot([d.loc[d['sample']==g,'value'] for g in groups],tick_labels=groups,patch_artist=True,boxprops={'facecolor':'#CAD9E8','edgecolor':'#35618F'})
    ax.set(xlabel='Capture / sample',ylabel=y_label)
    return stamp(fig, data, 'qc', y_label=y_label)

def plot_composition(data,palette,*,y_label='Fraction of included cells'):
    d=checked(data,['sample','celltype','count'],['count'])
    if d.duplicated(['sample','celltype']).any() or ((d['count']<0)|(d['count']%1!=0)).any(): raise ValueError('Invalid counts')
    palette_check(d.celltype,palette)
    # Fill absent cell types only in this explicitly count-based composition table.
    matrix=d.pivot(index='sample',columns='celltype',values='count').fillna(0)
    if (matrix.sum(axis=1)==0).any(): raise ValueError('Zero denominator')
    prop=matrix.div(matrix.sum(axis=1),axis=0); fig,ax=canvas(); bottom=np.zeros(len(prop))
    for celltype in prop.columns:
        ax.bar(prop.index,prop[celltype],bottom=bottom,color=palette[celltype],label=celltype,width=.75)
        bottom+=prop[celltype].to_numpy()
    if not isinstance(y_label,str) or not y_label.strip():raise ValueError('Explicit denominator label required')
    ax.set_ylim(0,1); ax.set_ylabel(y_label)
    ax.legend(loc='upper left',bbox_to_anchor=(1,1),frameon=False)
    return stamp(fig, data, 'composition', palette=palette, denominator='all supplied counts per sample',y_label=y_label)

def plot_curve(data,kind='ROC'):
    if kind not in ['ROC','PR','calibration']: raise ValueError('Unknown curve kind')
    d=checked(data,['model','x','y'],['x','y'])
    if ((d[['x','y']]<0)|(d[['x','y']]>1)).any().any(): raise ValueError('Curve values outside [0,1]')
    fig,ax=canvas()
    styles=['-','--','-.',':']
    if d.model.nunique()>len(styles): raise ValueError('Too many curves; use facets')
    for i,m in enumerate(pd.unique(d.model)):
        sub=d[d.model==m]; ax.plot(sub.x,sub.y,color='#35618F',linestyle=styles[i],label=m)
    if kind!='PR': ax.plot([0,1],[0,1],':',color='grey')
    labels={'ROC':('False positive rate','True positive rate'),'PR':('Recall','Precision'),'calibration':('Predicted probability','Observed fraction')}
    ax.set(xlim=(0,1),ylim=(0,1),xlabel=labels[kind][0],ylabel=labels[kind][1],aspect='equal'); ax.legend(frameon=False)
    return stamp(fig, data, 'curve', curve_kind=kind, threshold_order='input order')

def export_figure(fig,data,out_dir,figure_id,meta, *, source_file=None, expected_source_sha256=None):
    """Publish a complete per-figure directory by one rename on the same filesystem.

    v2 layout: out_dir/figure_id/figure_id.{svg,pdf,png,tsv,json}, *_session.txt.
    Hashes identify bytes, not validity of upstream statistics. Native plots need
    their own reviewed adapter/stamp; arbitrary untracked figures are rejected.
    """
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',figure_id): raise ValueError('Unsafe figure id')
    required={'source','palette','input_unit','experimental_unit','contrast','denominator','model','limits','filtering','uncertainty','interpretation_limit','synthetic'}
    if not required.issubset(meta): raise ValueError('Incomplete figure provenance')
    for key in required-{'synthetic','palette'}:
        if not isinstance(meta[key],str) or not meta[key].strip(): raise ValueError(f'Empty/non-text metadata: {key}')
    if not isinstance(meta['palette'],(str,dict)) or not meta['palette']: raise ValueError('Empty palette metadata')
    if 'input_hash' in meta: raise ValueError('input_hash is computed; use expected_source_sha256 for source verification')
    if type(meta['synthetic']) is not bool: raise ValueError('synthetic must be bool')
    if not isinstance(data,pd.DataFrame) or data.empty: raise ValueError('Empty data')
    raw=table_bytes(data); plotted_hash=hashlib.sha256(raw).hexdigest()
    if getattr(fig,'_omics_input_sha256',None)!=plotted_hash:
        raise ValueError('Export table does not match the renderer input; use a reviewed adapter')
    source_hash=None
    if source_file is not None:
        source_file=Path(source_file).resolve(strict=True)
        source_hash=file_sha256(source_file)
    if expected_source_sha256 is not None:
        if not re.fullmatch('[0-9a-fA-F]{64}',expected_source_sha256) or source_hash!=expected_source_sha256.lower():
            raise ValueError('Source SHA256 mismatch or missing source file')
    out=Path(out_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    dest=out/figure_id; lock=out/('.'+figure_id+'.lock'); stage=None
    extensions=['.svg','.pdf','.png','.tsv','.json','_session.txt']
    if dest.exists() or any((out/(figure_id+ext)).exists() for ext in extensions):
        raise FileExistsError('Refusing to overwrite existing v1/v2 outputs')
    # Exclusive lock prevents two exporters claiming the same figure id.
    handle=lock.open('x',encoding='utf-8')
    try:
        with handle: handle.write(str(os.getpid()))
        if dest.exists(): raise FileExistsError('Destination appeared during export')
        stage=Path(tempfile.mkdtemp(prefix='.'+figure_id+'-staging-',dir=out))
        files=[stage/(figure_id+ext) for ext in extensions]
        if meta['synthetic']:
            if fig._omics_spec.get('demo_label_style') == 'compact':
                # A separate reserved band preserves the scientific title and guides.
                fig.text(.02,.987,'SYNTHETIC DEMO | '+figure_id,fontsize=8,
                         va='top',color='#66727D',fontfamily=fig._omics_spec.get('project_theme',{}).get('font_family','sans-serif'))
                fig.text(.02,.008,'Software test fixture; not biological evidence',fontsize=7,
                         va='bottom',color='#66727D',fontfamily=fig._omics_spec.get('project_theme',{}).get('font_family','sans-serif'))
            else:
                fig.suptitle('SYNTHETIC DEMO - '+figure_id,weight='bold')
                fig.supxlabel('Software test fixture; not biological evidence',fontsize=8)
        with plt.rc_context({'svg.fonttype':'none','pdf.fonttype':42}):
            for file in files[:3]: fig.savefig(file,dpi=300,facecolor='white')
        files[3].write_bytes(raw)
        files[5].write_text(f'Python {platform.python_version()}\nmatplotlib {matplotlib.__version__}\npandas {pd.__version__}\nnumpy {np.__version__}\n',encoding='utf-8')
        receipt=dict(meta,schema_version=2,figure_id=figure_id,status='RENDERED_UNREVIEWED',
                     input_hash=plotted_hash,input_hash_algorithm='SHA256',input_hash_scope='exact exported TSV bytes',
                     source_file=str(source_file) if source_file else None,source_file_sha256=source_hash,
                     figure_spec=fig._omics_spec,width_inches=float(fig.get_figwidth()),height_inches=float(fig.get_figheight()))
        receipt['renderer_sha256']={p.name:file_sha256(p) for p in
                                   Path(__file__).parent.glob('figure_*.py')}
        receipt['output_sha256']={p.name:file_sha256(p) for p in files[:4]+files[5:]}
        files[4].write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        if dest.exists(): raise FileExistsError('Destination appeared before publish')
        stage.rename(dest)
        stage=None
        return [dest/(figure_id+ext) for ext in extensions]
    finally:
        # Only remove our own uncommitted temporary directory, never user outputs.
        try:
            if stage is not None and stage.parent==out and stage.name.startswith('.'+figure_id+'-staging-'):
                shutil.rmtree(stage)
        finally:
            handle.close()
            lock.unlink(missing_ok=True)
