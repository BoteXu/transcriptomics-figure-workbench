"""Bind the complete public display inventory; never regenerate research results."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import textwrap
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
G=ROOT/'examples/gallery'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):return json.loads(Path(p).read_text(encoding='utf8'))


def label(spec,role):
    title=spec.get('title') or (spec.get('panel_specs') or [{}])[0].get('title')
    if title:return title
    kind=re.sub(r'^(?:publication|reference|stored|frozen|multi_group)_','',spec.get('kind',''))
    kind=re.sub(r'^(?:publication|reference|stored|frozen)_','',kind)
    return kind.replace('_',' ').capitalize() if kind else ('Reference palette' if role=='palette' else 'Frozen result')


def palette_svg(id,meta):
    colors=meta['colors'];count=len(colors);columns=count if count<=6 else min(6,(count+1)//2)
    rows=(count+columns-1)//columns;width=max(350,columns*73+36);height=rows*100+100
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}pt" height="{height}pt" viewBox="0 0 {width} {height}"><g id="figure_1">']
    for i,color in enumerate(colors):
        x=18+(i%columns)*73;y=10+(i//columns)*100
        rgb=[int(color[j:j+2],16) for j in [1,3,5]]
        parts.extend([f'<rect x="{x}" y="{y}" width="65" height="59" rx="3" fill="{color}"/>',
          f'<text x="{x}" y="{y+73}" font-size="8.5" font-family="Arial" fill="#273540">{escape(color.upper())}</text>',
          f'<text x="{x}" y="{y+86}" font-size="7.3" font-family="Arial" fill="#637381">{", ".join(map(str,rgb))}</text>'])
    notes=[meta.get('title',id)+' · '+meta.get('semantic','declared color scale')]
    if meta.get('author'):notes.append('Attribution: '+meta['author'])
    if id=='C02':notes.append('Printed RGB conflicts with Hex; the declared Hex is retained.')
    notes.append('Exact color values; continuous/categorical semantics remain as declared.')
    y=rows*100+8
    for note in notes:
        for line in textwrap.wrap(note,90):
            parts.append(f'<text x="18" y="{y}" font-size="7.3" font-family="Arial" fill="#273540">{escape(line)}</text>');y+=12
    parts.append('</g></svg>');return ''.join(parts)


def main(output):
    generated=G/'publication-inputs-v030';generated.mkdir(exist_ok=True)
    catalog=read(G/'catalog.json');recipes=read(ROOT/'skills/transcriptomics-figure-workbench/references/combination-recipes.json')
    items=[]
    def add(id,svg,meta,tsv=None,role='figure',prefix=None):
        m=read(meta);spec=m.get('figure_spec',{});ctx=dict(id=id,role=role,kind=spec.get('kind',role),
          synthetic=m.get('synthetic',False),axes=m.get('layout_geometry',[]),preserve_text_colors=role=='palette',title_en=label(spec,role))
        item=dict(id=id,svg=svg.relative_to(ROOT).as_posix(),meta=meta.relative_to(ROOT).as_posix(),
          tsv=tsv.relative_to(ROOT).as_posix() if tsv else None,source_sha256=sha(svg),
          input_sha256=sha(tsv) if tsv else None,source_metadata_sha256=sha(meta),context=ctx)
        if prefix:item['source_bundle_prefix']=prefix
        if id in ['P03','AUX_estimate_forest','AUX_delta_estimate']:
            native=G/('publication-inputs-v030/native-'+id+'.svg');nm=native.with_suffix('.json')
            item.update(svg=native.relative_to(ROOT).as_posix(),meta=nm.relative_to(ROOT).as_posix(),source_sha256=sha(native),source_metadata_sha256=sha(nm))
            ctx['title_en']='Within-unit change' if id in ['P03','AUX_paired'] else 'Supplied effect intervals'
        if id=='M04':item['patch']={'foreground_axis_text':True}
        if id in ['AUX_estimate_forest','AUX_delta_estimate']:item['patch']={'notes':['Fixed illustrative demo bounds; not a research confidence interval.']}
        if id=='E01':item['patch']={'guide_axis_ids':['axes_4','axes_5','axes_6']}
        if id=='R03':ctx['title_en']='State and marker overview'
        if id=='P05':ctx['title_en']='Raincloud distribution'
        if id=='P02':ctx['title_en']='Sample quality control'
        if id=='R22':item['patch']={'axis_moves':{'axes_2':[0,12],'axes_3':[0,24],**{f'axes_{j}':[0,36] for j in range(4,9)}}}
        if id=='T02':item['patch']={'body_bounds':[5,40,472,310]}
        if id=='R24':item['patch']={'axis_moves':{'axes_5':[-320,145],'axes_6':[-280,145]},
          'group_moves':{'legend_1':[-50,60],**{f'patch_{j}':[0,35] for j in list(range(15,20))+list(range(32,37))},**{f'line2d_{j}':[0,35] for j in range(8,13)},**{f'text_{j}':[0,35] for j in range(12,17)}},
          'text_moves':{'c  Supplied object geometries with direct labels':[0,-50]}}
        if id=='R02':item['patch']={'color_map':{'#edf7ec':'#6f9580'}}
        if id=='ALT_E41_vertical':item['patch']={'axis_moves':{'axes_2':[0,30],'axes_3':[0,60]}}
        if id=='ALT_E42_vertical':item['patch']={'axis_moves':{'axes_2':[0,30],'axes_3':[0,60],'axes_4':[0,90],'axes_5':[0,90]}}
        if id in ['NEW_A01','NEW_A04']:item['patch']={'guide_position':'top'}
        if role=='protein':
            ctx['title_en']={'S01':'Structure cartoon','S02':'Molecular surface','S03':'Ligand context'}[id]
            dims=re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',svg.read_text()).groups()
            item['patch']={'body_bounds':[0,0,float(dims[0]),float(dims[1])]}
        if role=='palette':ctx['title_en']='Reference palette · '+id
        items.append(item)
    for row in catalog['preserved_examples']:
        if row['role']=='combination':continue
        m=read(G/row['meta']);svg=G/row['svg'] if row.get('svg') else None
        if row['role']=='palette':
            svg=generated/(row['id']+'.svg');svg.write_text(palette_svg(row['id'],m),encoding='utf8')
        if row['role']=='protein':
            raw=(G/row['png']).read_bytes();w=int.from_bytes(raw[16:20],'big');h=int.from_bytes(raw[20:24],'big')
            from PIL import Image, ImageChops
            from io import BytesIO
            with Image.open(BytesIO(raw)) as im:
                rgb=im.convert('RGB');bounds=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).convert('L').point(lambda v:255 if v>12 else 0).getbbox()
            x0,y0,x1,y1=bounds;x0=max(0,x0-25);y0=max(0,y0-25);x1=min(w,x1+25);y1=min(h,y1+25)
            vw=280;factor=vw/(x1-x0);vh=(y1-y0)*factor
            svg=generated/(row['id']+'.svg');svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}"><g id="figure_1"><svg width="{vw}" height="{vh}" viewBox="{x0} {y0} {x1-x0} {y1-y0}" overflow="hidden"><image width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(raw).decode()}"/></svg></g></svg>',encoding='utf8')
        add(row['id'],svg,G/row['meta'],G/row['tsv'] if row.get('tsv') else None,row['role'],row.get('svg','').removesuffix('.svg'))
    for row in recipes['supplemental_components']:
        prefix=row['prefix'];add('AUX_'+row['id'],G/(prefix+'.svg'),G/row['metadata'],G/(prefix+'.tsv'),'component',prefix)
    for directory in sorted((ROOT/'examples/qc-de').iterdir()):
        if directory.is_dir() and (directory/(directory.name+'.svg')).exists():
            add(directory.name,directory/(directory.name+'.svg'),directory/(directory.name+'.json'),directory/(directory.name+'.tsv'),'qc_de')
    for directory in sorted((ROOT/'examples/aesthetic-v030').iterdir()):
        if re.fullmatch('[AB]0[1-6]',directory.name):add('NEW_'+directory.name,directory/(directory.name+'.svg'),directory/(directory.name+'.json'),directory/(directory.name+'.tsv'),'new_mode')
    arrangements=read(G/'layout_review/manifest.json')
    extra=[]
    for row in arrangements['records']:
        if row['id'].startswith('K'):continue
        for alt in row['alternatives']:
            id='ALT_'+row['id']+'_'+alt['orientation'];add(id,G/alt['svg'],G/alt['meta'],None,'image_arrangement')
            extra.append(id)
    lookup={i.get('source_bundle_prefix'):i['id'] for i in items if i.get('source_bundle_prefix')}
    composites=[]
    for recipe in recipes['recipes']:
        components=[lookup[b['prefix']] for b in recipe['bundles']]
        for orientation in ['default','horizontal','vertical']:
            composites.append(dict(id=recipe['id'] if orientation=='default' else 'ALT_'+recipe['id']+'_'+orientation,
              source_id=recipe['id'],title=recipe['layout'].get('title',recipe['title']),orientation=orientation,
              components=components,layout=recipe['layout'],relationship=recipe['relation']))
    plan=dict(schema_version=1,scope='Complete historical atlas, auxiliary panels, all saved alternatives, QC/DE and new modes',
      counts=dict(base_sources=260,auxiliary=32,saved_alternatives=88,qc_de=8,new_modes=12,total=400),
      items=items,compositions=composites,scientific_analysis=False)
    assert len(items)==274 and len(composites)==126 and len({i['id'] for i in items+composites})==400
    output=Path(output);output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'FULL_DISPLAY_INVENTORY_BOUND','single_entries':len(items),'composition_entries':len(composites),'total':400}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);a=parser.parse_args();main(a.output)
