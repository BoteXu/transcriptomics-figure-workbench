"""Check installable-package paths and exclusion of untracked local content."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from current_release import DOCUMENTS, PREFIX, check_document_links, portable_document, public_files


def main():
    version = (ROOT / 'VERSION').read_text('utf8').strip()
    files = public_files()
    members = set(files) | set(DOCUMENTS) | {'LICENSE', 'requirements.txt', 'requirements-review.txt', 'RELEASE_SOURCE.json'}
    docs = {name: portable_document((ROOT / name).read_text('utf8'), name, version, members) for name in DOCUMENTS}
    count = check_document_links(docs, members)
    assert 'python scripts/workbench.py visual-template' in docs['README.md']
    assert 'python ' + PREFIX + 'scripts/workbench.py' not in docs['README.md']
    assert '](' + 'assets/method-scale-gallery/' in docs['README.md']
    assert 'blob/v' + version + '/examples/gallery/index.html' in docs['README.md']
    assert '](../README.md)' in docs['docs/readme-history-before-overview.md']
    links = '[remote](https://example.org/x#part) [anchor](#part)'
    assert portable_document(links, 'THIRD_PARTY.md', version, members) == links
    try:
        check_document_links({'broken.md': '[missing](missing.tsv)'}, set())
        raise AssertionError('Missing package data link was accepted')
    except ValueError:
        pass
    try:
        portable_document('[escape](../../outside.tsv)', 'README.md', version, members)
        raise AssertionError('Repository escape link was accepted')
    except ValueError:
        pass
    # A clean-looking private/ignored file beside a public file must never be
    # included just because a packaging command traversed the skill directory.
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        skill = root / PREFIX
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('Public fixture', encoding='utf8')
        (skill / 'VERSION').write_text(version, encoding='utf8')
        subprocess.run(['git', 'add', '--', PREFIX], cwd=root, check=True)
        (skill / 'untracked-local.txt').write_text('Excluded local fixture', encoding='utf8')
        (skill / 'private').mkdir()
        (skill / 'private/session.json').write_text('{}', encoding='utf8')
        assert set(public_files(root)) == {'SKILL.md', 'VERSION'}
        subprocess.run(['git', 'add', '--', PREFIX + 'private/session.json'], cwd=root, check=True)
        try:
            public_files(root)
            raise AssertionError('Committed private member was accepted')
        except ValueError:
            pass
    print(json.dumps(dict(status='PORTABLE_RELEASE_DOCUMENTS_PASS', local_links=count,
                          committed_only_inventory=True, private_member_rejected=True)))


if __name__ == '__main__':
    main()
