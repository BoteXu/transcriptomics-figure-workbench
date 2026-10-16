"""Verify exact reviewed responsive examples without running a plotting backend."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.layout import inspect_layout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / 'examples/responsive-v081'
    singles = json.loads((base / 'manifest.json').read_text())['records']
    review = json.loads((base / 'screen-review.json').read_text())
    reviewed = {row['id']: row for row in review['records']}
    assert len(singles) == len({r['id'] for r in singles}) == 14
    assert len(reviewed) == review['actual_complete_screen_views'] == 20
    for row in singles:
        key = row['id']
        assert row['screen_review'] == 'SCREEN_REVIEWED'
        assert row['automated_layout']['issues'] == []
        assert sha(base / (key + '.tsv')) == row['input_sha256']
        for ext in ['svg', 'png']:
            file = base / (key + '.' + ext)
            assert sha(file) == row['output_sha256'][file.name] == reviewed[key][ext + '_sha256']
        assert not row['target_size_assessed'] and not row['scientific_acceptance']
    compositions = base / 'compositions'
    pages = json.loads((compositions / 'manifest.json').read_text())['records']
    assert len(pages) == 6 and sum(len(r['panels']) for r in pages) == 19
    for name in {r['id'] for r in pages}:
        result = inspect_layout(compositions / name)
        assert result['status'] == 'LAYOUT_INSPECTED' and not result['issues'], result
    for row in pages:
        svg = compositions / row['file']
        assert row['screen_review'] == 'SCREEN_REVIEWED'
        for ext in ['svg', 'png', 'pdf']:
            assert sha(svg.with_suffix('.' + ext)) == row['sha256'][ext]
        for ext in ['svg', 'png']:
            assert row['sha256'][ext] == reviewed[row['file']][ext + '_sha256']
    print(json.dumps(dict(status='RESPONSIVE_RELEASE_BINDINGS_PASS', single_figures=14,
                          composition_pages=6, complete_panel_uses=19,
                          target_size_assessed=False, scientific_acceptance=False)))


if __name__ == '__main__':
    main()
