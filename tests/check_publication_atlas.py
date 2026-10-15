"""Verify every reviewed export binding and bounded image/PDF header, without analysis."""
from pathlib import Path
import hashlib
import json
import math
import struct
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / 'examples/gallery'
A = G / 'publication-v030'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def png_header(path):
    with path.open('rb') as stream:
        assert stream.read(8) == b'\x89PNG\r\n\x1a\n'
        width = height = dpi = None
        while True:
            n = struct.unpack('>I', stream.read(4))[0]
            kind = stream.read(4)
            if kind == b'IHDR':
                data = stream.read(n)
                width, height = struct.unpack('>II', data[:8])
            elif kind == b'pHYs':
                x, y, unit = struct.unpack('>IIB', stream.read(n))
                assert unit == 1 and x == y == 11811
                dpi = 300
            else:
                stream.seek(n, 1)
            stream.seek(4, 1)
            if kind == b'IEND':
                break
    assert dpi == 300
    return width, height


def main():
    index = json.loads((A / 'review-index.json').read_text(encoding='utf8'))
    plan = json.loads((A / 'source-plan.json').read_text(encoding='utf8'))
    records = index['records']
    assert index['actual_individual_png_inspections'] == len(records) == 400
    by = {r['id']: r for r in records}
    assert len(by) == 400
    assert sum(r['type'] == 'composition' for r in records) == 126
    for source in plan['items']:
        assert sha(ROOT / source['svg']) == source['source_sha256']
        assert sha(ROOT / source['meta']) == source['source_metadata_sha256']
        if source['tsv']:
            assert sha(ROOT / source['tsv']) == source['input_sha256']
    flags = []
    for row in records:
        key, assets = row['id'], row['assets']
        receipt = json.loads((G / assets['meta']).read_text(encoding='utf8'))
        assert receipt['status'] == 'VISUALLY_SELF_REVIEWED'
        assert receipt['visual_acceptance'] and not receipt['scientific_acceptance']
        for name, digest in receipt['output_sha256'].items():
            assert sha(A / key / name) == digest
        assert receipt['visual_review']['png_sha256'] == sha(G / assets['png']) == assets['png_sha256']
        assert not receipt['visual_review']['independent_second_reviewer']
        w, h = png_header(G / assets['png'])
        assert abs(w - receipt['width_pt'] * 300 / 72) < 4.2, key + ': browser CSS-pixel crop rounding exceeds one CSS pixel plus one raster pixel'
        assert abs(h - receipt['height_pt'] * 300 / 72) < 4.2, key + ': browser CSS-pixel crop rounding exceeds one CSS pixel plus one raster pixel'
        assert w * h <= 80_000_000
        reader = PdfReader(G / assets['pdf'])
        assert len(reader.pages) == 1
        page = reader.pages[0]
        assert abs(float(page.mediabox.width) - receipt['width_pt']) < 1.2
        assert abs(float(page.mediabox.height) - receipt['height_pt']) < 1.2
        reader.close()
        if assets.get('tsv'):
            assert sha(G / assets['tsv']) == receipt['input_sha256']
        for component in receipt.get('components', []):
            assert sha(G / by[component['id']]['assets']['svg']) == component['sha256']
        if row['automatic_geometry_issues']:
            assert row['automatic_issue_disposition']
            flags.append(dict(id=key, count=len(row['automatic_geometry_issues'])))
    catalog = json.loads((G / 'catalog.json').read_text(encoding='utf8'))
    assert all(x['current_preview'] == by[x['id']]['assets'] for x in catalog['preserved_examples'])
    print(json.dumps(dict(status='PUBLICATION_ATLAS_BINDINGS_PASS', png=400, single_page_pdf=400,
                         dpi=300, source_bound=True, composition_components_bound=True,
                         geometry_flags_with_visual_disposition=flags, scientific_acceptance=False)))


if __name__ == '__main__':
    main()
