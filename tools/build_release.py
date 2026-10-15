"""Package the checked public skill and overviews in a fresh directory."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
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
    shutil.copy2(SKILL/'assets/figure-studio.html',studio);assets.append(studio)
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
    (output/f'SHA256SUMS-v{version}.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in assets),encoding='utf8')
    print(json.dumps(dict(status='PUBLIC_RELEASE_ARCHIVE_VERIFIED',version=version,unique_archive_entries=len(files),assets=[dict(name=p.name,bytes=p.stat().st_size) for p in assets])))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.output)
