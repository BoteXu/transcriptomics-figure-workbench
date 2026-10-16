"""Package the checked public skill and overviews in a fresh directory."""
from pathlib import Path
import argparse,base64,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'


def main(output):
    output.mkdir(parents=True,exist_ok=False)
    version=(ROOT/'VERSION').read_text().strip()
    assert version==(SKILL/'VERSION').read_text().strip()
    files={p.relative_to(SKILL).as_posix():p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert all(not p.is_symlink() for p in files.values())
    for name in ('LICENSE','requirements.txt','requirements-review.txt'):
        if name in files:assert files[name].read_bytes()==(ROOT/name).read_bytes(),'Conflicting package file: '+name
        else:files[name]=ROOT/name
    archive=output/f'transcriptomics-figure-workbench-v{version}.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,path in sorted(files.items()):z.write(path,'transcriptomics-figure-workbench/'+name)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(set(z.namelist()))==len(files)
        assert not z.testzip()
        for name,path in files.items():assert z.read('transcriptomics-figure-workbench/'+name)==path.read_bytes()
    assets=[archive]
    for source,name in [('visualization-overview.pdf','visualization-overview.pdf'),('source-archive-v021.pdf','all-previews.pdf'),('new-result-modes-v024.jpg','new-result-modes-v024.jpg')]:
        destination=output/name;shutil.copy2(ROOT/'examples/overview'/source,destination);assets.append(destination)
    studio=output/f'figure-studio-v{version}.html'
    page=(SKILL/'assets/figure-studio.html').read_text(encoding='utf8')
    for key in ['BulkMain','SingleCellMain']:
        prefix='study-gallery/'+key+'.jpg'
        page=page.replace(prefix,'data:image/jpeg;base64,'+base64.b64encode((SKILL/'assets/study-gallery'/(key+'.jpg')).read_bytes()).decode())
        page=page.replace('study-gallery/index.html#'+key,'https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v'+version+'/examples/validated-v090/index.html#'+key)
    # The single-file download embeds only public synthetic preview pixels.
    # Full editable bundles remain available in the separately checked ZIP.
    for row in json.loads((ROOT/'examples/package-v040/manifest.json').read_text())['records']:
        key=row['id'];prefix='package-gallery/'+key+'/'+key
        preview=ROOT/'examples/package-v040'/key/(key+'.png')
        page=page.replace(prefix+'.png','data:image/png;base64,'+base64.b64encode(preview.read_bytes()).decode())
        for ext in ['svg','pdf','tsv','json']:
            page=page.replace(prefix+'.'+ext,'https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v'+version+'/examples/package-v040/'+key+'/'+key+'.'+ext)
        page=page.replace('package-gallery/inputs/'+key+'.spec.json','https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v'+version+'/examples/package-v040/inputs/'+key+'.spec.json')
        page=page.replace('package-gallery/index.html#'+key,'https://github.com/BoteXu/transcriptomics-figure-workbench/tree/v'+version+'/examples/package-v040#'+key)
    for row in json.loads((ROOT/'examples/design-v050/manifest.json').read_text())['records']:
        key=row['id'];prefix='design-gallery/'+key+'/'+key
        page=page.replace(prefix+'.png','data:image/png;base64,'+base64.b64encode((ROOT/'examples/design-v050'/key/(key+'.png')).read_bytes()).decode())
        page=page.replace('design-gallery/index.html#'+key,'https://github.com/BoteXu/transcriptomics-figure-workbench/tree/v'+version+'/examples/design-v050#'+key)
    for row in json.loads((ROOT/'examples/refined-v060/manifest.json').read_text())['records']:
        key=row['id'];prefix='refined-gallery/'+key+'/'+key
        page=page.replace(prefix+'.png','data:image/png;base64,'+base64.b64encode((ROOT/'examples/refined-v060'/key/(key+'.png')).read_bytes()).decode())
        page=page.replace('refined-gallery/index.html#'+key,'https://github.com/BoteXu/transcriptomics-figure-workbench/tree/v'+version+'/examples/refined-v060#'+key)
    for row in json.loads((ROOT/'examples/clarity-v070/manifest.json').read_text())['records']:
        key=row['id'];prefix='clarity-gallery/'+key+'/'+key
        page=page.replace(prefix+'.png','data:image/png;base64,'+base64.b64encode((ROOT/'examples/clarity-v070'/key/(key+'.png')).read_bytes()).decode())
        page=page.replace('clarity-gallery/index.html#'+key,'https://github.com/BoteXu/transcriptomics-figure-workbench/tree/v'+version+'/examples/clarity-v070#'+key)
    for form in json.loads((SKILL/'references/form-catalog.json').read_text(encoding='utf8'))['forms']:
        key=form['default']
        page=page.replace('forms-gallery/'+key+'.jpg','data:image/jpeg;base64,'+base64.b64encode((SKILL/'assets/forms-gallery'/(key+'.jpg')).read_bytes()).decode())
        page=page.replace('forms-gallery/index.html#'+form['id'],'https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v'+version+'/examples/forms-v080/index.html#'+form['id'])
    studio.write_text(page,encoding='utf8');assets.append(studio)
    package_examples=output/f'package-examples-v{version}.zip'
    with zipfile.ZipFile(package_examples,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted((ROOT/'examples/package-v040').rglob('*')):
            if file.is_file():
                name='package-examples/'+file.relative_to(ROOT/'examples/package-v040').as_posix()
                if file.name=='index.html':archive.writestr(name,file.read_text(encoding='utf8').replace('../../docs/package-styles-v040.md','../docs/package-styles-v040.md'))
                else:archive.write(file,name)
        for name in ['package-styles-v040.md','package-styles-v040.jpg']:
            file=ROOT/'docs'/name
            if name.endswith('.md'):archive.writestr('docs/'+name,file.read_text(encoding='utf8').replace('../examples/package-v040/index.html','../package-examples/index.html'))
            else:archive.write(file,'docs/'+name)
    assets.append(package_examples)
    for source,name in [(ROOT/'examples/overview/package-styles-v040.pdf','package-figures-v040.pdf'),(ROOT/'docs/package-styles-v040.jpg','package-figures-v040.jpg')]:
        destination=output/name;shutil.copy2(source,destination);assets.append(destination)
    previews=output/f'workbench-previews-v{version}.zip'
    with zipfile.ZipFile(previews,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted((ROOT/'examples/aesthetic-v030').rglob('*')):
            if file.is_file():archive.write(file,file.relative_to(ROOT/'examples/aesthetic-v030').as_posix())
    assets.append(previews)
    atlas=output/f'reviewed-atlas-v{version}.zip'
    # The optional atlas contains final exports, not duplicated historical pixels.
    # Its standalone index rewrites source links to the versioned public repository.
    with zipfile.ZipFile(atlas,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        folder=ROOT/'examples/gallery/publication-v030'
        for file in sorted(folder.rglob('*')):
            if file.is_file() and file.name!='index.html':
                archive.write(file,'reviewed-atlas/'+file.relative_to(folder).as_posix())
        page=(folder/'index.html').read_text(encoding='utf8')
        start=page.index('const rows=')+len('const rows=')
        rows,length=json.JSONDecoder().raw_decode(page[start:])
        for row in rows:
            for key in ('png','svg','pdf','meta'):row[key]=row[key].removeprefix('../publication-v030/')
            source,_,fragment=row['original'].partition('#')
            source=(folder/source).resolve().relative_to(ROOT).as_posix()
            row['original']='https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v'+version+'/'+source+('#'+fragment if fragment else '')
        page=page[:start]+json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')+page[start+length:]
        page=page.replace('href="../index.html"','href="https://github.com/BoteXu/transcriptomics-figure-workbench/tree/v'+version+'"')
        archive.writestr('reviewed-atlas/index.html',page)
        for file in sorted((ROOT/'examples/method-v030').rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts:
                    archive.write(file,'reviewed-atlas/methods/'+file.relative_to(ROOT/'examples/method-v030').as_posix())
        archive.writestr('reviewed-atlas/README.txt','Open index.html for 400 reviewed exports; open methods/index.html for 8 GSEA/ORA displays. Original source files and source-plan paths refer to the versioned public repository. Self-review is not scientific acceptance.\n')
    assets.append(atlas)
    full_pdf=output/'full-atlas-v030.pdf';shutil.copy2(ROOT/'examples/overview/full-atlas-v030.pdf',full_pdf);assets.append(full_pdf)
    # Self-contained current browser with the exact paths its offline links use.
    # The historical atlas remains a separate immutable download above.
    review=output/f'figure-review-library-v{version}.zip'
    with zipfile.ZipFile(review,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        paths=set()
        report=json.loads((ROOT/'examples/forms-v080/manifest.json').read_text(encoding='utf8'))
        for row in report['records']:
            paths.update(row['assets'].values());paths.update(row.get('previous_assets',{}).values())
        for folder in ['examples/validated-v090','examples/responsive-v081','examples/forms-v080','examples/layout-v080','examples/review-v070','examples/clarity-v070','examples/review-v060','examples/refined-v060','examples/reading-v060','examples/design-v050','examples/gallery/repairs-v050','examples/gallery/repairs-v060','examples/package-v040/inputs','examples/method-v030/inputs','docs/screens-v050']:
            paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for relative in sorted(paths):archive.write(ROOT/relative,relative)
        archive.writestr('README.txt','Open examples/validated-v090/index.html for 803 hash-bound screen-reviewed pages, including 25 coherent study figures and eight custom main layouts. The study-manifests and selected input specifications are portable; main-figure print scope is recorded per artifact. Open examples/forms-v080/index.html for 90 consolidated base entries and all 458 earlier exports. Exact previous assets and historical size warnings remain attached. Source files are in the versioned public repository. Screen review is not calibrated paper-proof, independent review or scientific acceptance.\n')
    assets.append(review)
    contact=output/'design-alternatives-v050.jpg';shutil.copy2(ROOT/'docs/design-alternatives-v050.jpg',contact);assets.append(contact)
    contact=output/'refined-alternatives-v060.jpg';shutil.copy2(ROOT/'docs/refined-alternatives-v060.jpg',contact);assets.append(contact)
    contact=output/'clarity-comparison-v070.jpg';shutil.copy2(ROOT/'docs/clarity-comparison-v070.jpg',contact);assets.append(contact)
    extra=output/f'clarity-examples-v{version}.zip'
    with zipfile.ZipFile(extra,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted((ROOT/'examples/clarity-v070').rglob('*')):
            if file.is_file():archive.write(file,'clarity-examples/'+file.relative_to(ROOT/'examples/clarity-v070').as_posix())
    assets.append(extra)
    for volume in json.loads((ROOT/'examples/reading-v060/reading-index.json').read_text())['volumes']:
        destination=output/volume['file'];shutil.copy2(ROOT/'examples/reading-v060'/volume['file'],destination);assets.append(destination)
    (output/f'SHA256SUMS-v{version}.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in assets),encoding='utf8')
    print(json.dumps(dict(status='PUBLIC_RELEASE_ARCHIVE_VERIFIED',version=version,unique_archive_entries=len(files),assets=[dict(name=p.name,bytes=p.stat().st_size) for p in assets])))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.output)
