"""Dependency-free publication checks; no research code or external tools executed."""
from pathlib import Path
from urllib.parse import unquote
import ast, collections, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/transcriptomics-figure-workbench'
GALLERY = ROOT/'examples/gallery'
TEXT_SUFFIXES = {'.md','.py','.R','.json','.yaml','.yml','.txt','.tsv','.html','.svg'}
PRIVATE = re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|(?<![:A-Za-z0-9./])/(?:home|Users)/[^/\s]+/|wxid_[a-z0-9_]+|viewer-file:[/]{2}|https?://(?:localhost|127\.0\.0\.1):876[67])')
SECRET = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{40,})\b')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def checked_path(relative, root=GALLERY):
    path = (root/relative).resolve()
    assert root.resolve() in path.parents, 'Path escapes package'
    assert path.is_file(), 'Missing asset: '+relative
    return path

def main():
    assert (SKILL/'SKILL.md').is_file()
    entry=(SKILL/'SKILL.md').read_text(encoding='utf8')
    assert entry.startswith('---\n') and 'name: transcriptomics-figure-workbench' in entry
    assert (ROOT/'LICENSE').is_file() and (SKILL/'references/colorbrewer-license.txt').is_file()
    assert (ROOT/'VERSION').read_text().strip()==(SKILL/'VERSION').read_text().strip()=='0.2.0'
    files=[p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and 'dist' not in p.parts]
    for p in files:
        assert p.stat().st_size < 100_000_000, 'GitHub file size exceeded'
        assert not p.is_symlink(), 'Symlink in publication package'
        if p.suffix in TEXT_SUFFIXES:
            text=p.read_text(encoding='utf8')
            assert not PRIVATE.search(text), 'Private path candidate: '+str(p.relative_to(ROOT))
            assert not SECRET.search(text), 'Credential candidate'
        if p.suffix=='.py': ast.parse(p.read_text(encoding='utf8'),filename=p.name)
        if p.suffix=='.json': json.loads(p.read_text(encoding='utf8'))
    catalog=json.loads((GALLERY/'catalog.json').read_text(encoding='utf8'))
    items=catalog['preserved_examples']; groups=catalog['general_entries']
    assert len(items)==236 and len(groups)==45
    ids=[i['id'] for i in items]; assert len(ids)==len(set(ids))
    flattened=[id_ for g in groups for id_ in g['members']]
    assert sorted(flattened)==sorted(ids), 'Lost or duplicate catalog member'
    assert {'P05','P10','P20a','R05','R25','K07','K15','C15','S03','T43','N12'} <= set(ids)
    for g in groups: assert g['default'] in g['members']
    counts=collections.Counter(i['role'] for i in items)
    assert counts['palette']==15 and counts['protein']==3 and counts['combination']==36
    assert sum(i['curation']['decision']=='recommended' for i in items)==177
    by_id={i['id']:i for i in items}
    for item in items:
        assert item['curation']['canonical'] in by_id
        assert by_id[item['curation']['canonical']]['curation']['decision']=='recommended'
    baseline=json.loads((ROOT/'docs/baseline-preservation-v020.json').read_text(encoding='utf8'))
    assert len(baseline['ids'])==168
    for old in baseline['ids']:
        now=by_id[old['id']]
        assert now['png_sha256']==old['png_sha256'], 'Original preview removed or changed'
        if old['pdf_sha256']: assert now['pdf_sha256']==old['pdf_sha256']
    ledger=json.loads((SKILL/'references/catalog-audit.json').read_text(encoding='utf8'))['entries']
    assert sorted(x['id'] for x in ledger)==sorted(ids)
    for row in ledger:
        assert row['png_sha256']==by_id[row['id']]['png_sha256']
        assert row['decision']==by_id[row['id']]['curation']['decision']
    assets=set()
    for item in items:
        assert item['reference'] is None, 'Original reference pixels included'
        for key in ['input_shape','data_required','expression','how_to_draw','aesthetic_controls','limitations']:
            assert isinstance(item[key],str) and item[key].strip()
        for field in ['png','pdf','svg','tsv','style','meta']:
            if item.get(field):
                path=checked_path(item[field]); assets.add(item[field])
                if field in ['png','pdf']: assert sha(path)==item[field+'_sha256'], 'Asset version mismatch'
        for relative in item.get('component_tables',[]):
            checked_path(relative); assets.add(relative)
        meta=json.loads(checked_path(item['meta']).read_text(encoding='utf8'))
        assert meta['example_id']==item['id']
        if item['role']=='protein':
            assert meta['synthetic'] is False and meta['structure_source']['pdb_id']=='1EMA'
        elif item['role']!='palette': assert meta['synthetic'] is True
    recipes=json.loads((SKILL/'references/combination-recipes.json').read_text(encoding='utf8'))
    assert len(recipes['recipes'])==36 and len(recipes['supplemental_components'])==22
    assert {r['id'] for r in recipes['recipes']}=={i['id'] for i in items if i['role']=='combination'}
    for recipe in recipes['recipes']:
        item=by_id[recipe['id']]
        assert len(recipe['bundles'])==len(recipe['layout']['panels'])==len(item['component_links'])
        for index,bundle in enumerate(recipe['bundles']):
            assert sha(checked_path(bundle['prefix']+'.tsv'))==bundle['table_sha256']==sha(checked_path(item['component_tables'][index]))
            metadata=json.loads(checked_path(bundle['metadata']).read_text(encoding='utf8'))
            for ext in ('.png','.pdf','.svg','.tsv'):
                file=checked_path(bundle['prefix']+ext)
                assert sha(file)==metadata['output_sha256'][file.name]
        for component in item['component_links']:
            if component['url'].startswith('#'): assert component['url'][1:] in by_id
            else:checked_path(component['url'])
    html=(GALLERY/'index.html').read_text(encoding='utf8')
    start=html.index('<script>const items=')+len('<script>const items=')
    inline=json.JSONDecoder().raw_decode(html[start:])[0]
    assert inline==items, 'Gallery and manifest diverge'
    marker=re.search(r'const\s+groups\s*=\s*',html)
    assert marker and json.JSONDecoder().raw_decode(html[marker.end():])[0]==groups, 'Navigation groups diverge'
    assert 'figure-workbench-public-v0.1-notes' in html
    assert not list(GALLERY.glob('references/*')), 'Private source pictures bundled'
    for p in ROOT.rglob('*.md'):
        if '.git' in p.parts or 'dist' in p.parts: continue
        text=p.read_text(encoding='utf8')
        for link in re.findall(r'\[[^\]\n]+\]\(([^\)\n]+)\)',text):
            link=link.split('#',1)[0].split('?',1)[0]
            if not link or re.match(r'[a-zA-Z]+:',link) or link.startswith('//'): continue
            link=unquote(link.strip('<>'))
            # Only exact file references; recipe placeholders are not claimed as bundled inputs.
            if any(x in link for x in ['{','}','<','>','*']): continue
            target=(p.parent/link).resolve()
            assert target.exists(), 'Broken document link: '+str(p.relative_to(ROOT))+' -> '+link
    overview=ROOT/'examples/overview'
    for name in ['all-previews.png','all-previews.jpg','all-previews.pdf','general-patterns.png','general-patterns.jpg','index.tsv']:
        assert (overview/name).is_file()
    lines=(overview/'index.tsv').read_text(encoding='utf8').splitlines()
    assert len(lines)==237
    for line in lines[1:]: checked_path('overview/'+line.split('\t')[-1],ROOT/'examples')
    plots={}
    for p in (SKILL/'scripts').glob('figure_*.py'):
        tree=ast.parse(p.read_text(encoding='utf8'))
        plots[p.name]=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('plot_')]
    result={'status':'PACKAGE_STRUCTURE_AND_COVERAGE_PASS','version':(ROOT/'VERSION').read_text().strip(),'groups':len(groups),'examples':len(items),'roles':dict(counts),'catalog_assets_checked':len(assets),'plot_functions':sum(len(v) for v in plots.values()),'plot_functions_by_module':{k:len(v) for k,v in plots.items() if v},'files_scanned':len(files),'limitations':'Static structure, paths and hashes do not prove scientific validity or all dependency runtimes.'}
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__': main()
