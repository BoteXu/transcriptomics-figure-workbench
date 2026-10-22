"""Build a source-bound current skill ZIP with portable, checked documentation."""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import hashlib
import json
import posixpath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'skills/transcriptomics-figure-workbench/'
PACKAGE = 'transcriptomics-figure-workbench/'
REPOSITORY = 'https://github.com/BoteXu/transcriptomics-figure-workbench'
DOCUMENTS = {'README.md': 'README.md', 'THIRD_PARTY.md': 'SOURCE_ATTRIBUTION.md',
             'docs/readme-history-before-overview.md': 'docs/readme-history-before-overview.md',
             'docs/release-v0110.md': 'docs/release-v0110.md',
             'docs/release-v0120.md': 'docs/release-v0120.md',
             'docs/release-v0130.md': 'docs/release-v0130.md',
             'docs/release-v0140.md': 'docs/release-v0140.md'}
LINK = re.compile(r'(\[[^\]\n]+\]\()([^\)\n]+)(\))')


def digest(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        result.update(block)
    return result.hexdigest()


def file_digest(path):
    with path.open('rb') as stream:
        return digest(stream)


def public_files(root=ROOT):
    """Select committed skill files; ignored local extras never enter the ZIP."""
    raw = subprocess.check_output(['git', 'ls-files', '-z', '--', PREFIX], cwd=root)
    files = {}
    for name in filter(None, raw.decode('utf8').split('\0')):
        relative = name.removeprefix(PREFIX)
        parts = PurePosixPath(relative).parts
        if not name.startswith(PREFIX) or {'private', 'profiles', '.env', '__pycache__'} & set(parts):
            raise ValueError('Non-public path in committed skill inventory')
        path = root / name
        if path.is_symlink() or not path.is_file() or root.resolve() not in path.resolve().parents:
            raise ValueError('Invalid public skill member')
        files[relative] = path
    if 'SKILL.md' not in files or 'VERSION' not in files:
        raise ValueError('A committed public skill is required')
    return files


def portable_document(text, source, version, members):
    """Resolve repository links before moving a document into the skill root."""
    def replace(match):
        target = match.group(2).strip('<>')
        split = urlsplit(target)
        if split.scheme or split.netloc or not split.path:
            return match.group(0)
        original = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(split.path)))
        if original.startswith(('../', '/')):
            raise ValueError('Document link escapes the public repository')
        candidate = DOCUMENTS.get(original, original.removeprefix(PREFIX))
        if original == 'examples/studio/index.html':
            candidate = 'assets/figure-studio.html'
        if candidate in members:
            destination = DOCUMENTS.get(source, source)
            rewritten = posixpath.relpath(candidate, posixpath.dirname(destination) or '.')
        else:
            rewritten = REPOSITORY + '/blob/v' + version + '/' + original
        if split.query:
            rewritten += '?' + split.query
        if split.fragment:
            rewritten += '#' + split.fragment
        return match.group(1) + rewritten + match.group(3)

    text = LINK.sub(replace, text)
    if source == 'README.md':
        text = text.replace(PREFIX + 'scripts/', 'scripts/')
        text = text.replace('**仓库根目录**', '**解压后的 skill 根目录**')
        notice = ('\n> 安装包说明：本页由同版本仓库 README 生成，命令从解压后的 skill 根目录执行。'
                  '当前图库、图片和输入表在包内；仓库专有历史页面使用固定版本的 GitHub 链接。\n')
        heading, rest = text.split('\n', 1)
        text = heading + '\n' + notice + rest
    return text


def check_document_links(documents, members):
    checked = 0
    for name, text in documents.items():
        for match in LINK.finditer(text):
            target = urlsplit(match.group(2).strip('<>'))
            if target.scheme or target.netloc or not target.path:
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(target.path)))
            if resolved not in members:
                raise ValueError('Broken packaged documentation link: ' + name + ' -> ' + target.path)
            checked += 1
    return checked


def build_current_release(output):
    if subprocess.call(['git', 'diff', '--quiet', 'HEAD', '--'], cwd=ROOT) != 0:
        raise ValueError('Commit the reviewed source before building a source-bound release')
    version = (ROOT / 'VERSION').read_text('utf8').strip()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('A semantic release version is required')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files = public_files()
    committed_count = len(files)
    if (files['VERSION'].read_text('utf8').strip() != version):
        raise ValueError('Skill and repository versions differ')
    for name in ('LICENSE', 'requirements.txt', 'requirements-review.txt'):
        if name in files and file_digest(files[name]) != file_digest(ROOT / name):
            raise ValueError('Conflicting dependency or license document: ' + name)
        files[name] = ROOT / name
    members = set(files) | set(DOCUMENTS.values()) | {'RELEASE_SOURCE.json'}
    documents = {destination: portable_document((ROOT / name).read_text('utf8'), name, version, members)
                 for name, destination in DOCUMENTS.items()}
    local_links = check_document_links(documents, members)
    provenance = dict(schema_version=1, version=version, tag='v' + version, source_commit=source,
                      repository=REPOSITORY, repository_readme_sha256=file_digest(ROOT / 'README.md'),
                      packaged_readme_sha256=hashlib.sha256(documents['README.md'].encode('utf8')).hexdigest(),
                      package_members=len(members), committed_skill_files=committed_count,
                      documentation='Repository README adapted only for package paths and fixed-version source links',
                      contents='Public skill, exact frozen examples and documentation; no local profiles or runtime files')
    extras = {name: text.encode('utf8') for name, text in documents.items()}
    extras['RELEASE_SOURCE.json'] = (json.dumps(provenance, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    if set(files) & set(extras):
        raise ValueError('Ambiguous generated package document')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    archive = output / ('transcriptomics-figure-workbench-v' + version + '.zip')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for number, (name, path) in enumerate(sorted(files.items()), 1):
            bundle.write(path, PACKAGE + name)
            if number % 2000 == 0:
                print('Public package files written: ' + str(number), flush=True)
        for name, content in extras.items():
            bundle.writestr(PACKAGE + name, content)
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or set(names) != {PACKAGE + name for name in members}:
            raise ValueError('Archive member coverage differs from public source')
        for number, (name, path) in enumerate(sorted(files.items()), 1):
            with bundle.open(PACKAGE + name) as stream:
                if digest(stream) != file_digest(path):
                    raise ValueError('Archive differs from reviewed public file: ' + name)
            if number % 2000 == 0:
                print('Archive member hashes verified: ' + str(number), flush=True)
        for name, content in extras.items():
            if bundle.read(PACKAGE + name) != content:
                raise ValueError('Generated documentation differs inside archive')
    source_file = output / 'RELEASE_SOURCE.json'
    source_file.write_bytes(extras['RELEASE_SOURCE.json'])
    assets = [archive, source_file]
    checksum = output / ('SHA256SUMS-v' + version + '.txt')
    checksum.write_bytes(''.join(file_digest(path) + '  ' + path.name + '\n' for path in assets).encode('utf8'))
    print(json.dumps(dict(status='PUBLIC_CURRENT_RELEASE_ARCHIVE_VERIFIED', version=version,
                          source_commit=source, archive_members=len(members), package_local_links=local_links,
                          assets=[dict(name=p.name, bytes=p.stat().st_size, sha256=file_digest(p))
                                  for p in assets + [checksum]])), flush=True)
