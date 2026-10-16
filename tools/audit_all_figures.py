"""Bounded, offline export inventory and print-size screening (not aesthetic approval)."""
from pathlib import Path
import argparse, collections, hashlib, json, math, statistics
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inventory():
    rows = []
    base = ROOT / 'examples/gallery'
    for record in json.loads((base/'publication-v030/review-index.json').read_text())['records']:
        paths = {ext: base/record['assets'][ext] for ext in ('png', 'svg', 'pdf', 'meta')}
        rows.append(dict(id=record['id'], collection='atlas', paths=paths,
                         expected_sha256=record['assets']['png_sha256']))
    for folder, collection in [('package-v040', 'package'), ('method-v030', 'method')]:
        base = ROOT/'examples'/folder
        for record in json.loads((base/'manifest.json').read_text())['records']:
            key = record['id']
            paths = {ext: base/key/(key+'.'+('json' if ext == 'meta' else ext))
                     for ext in ('png', 'svg', 'pdf', 'meta')}
            rows.append(dict(id=key, collection=collection, paths=paths,
                             expected_sha256=record['png_sha256']))
    assert len(rows) == len({r['id'] for r in rows}) == 433
    return rows


def examine(row, target_mm):
    paths = row.pop('paths')
    row['assets'] = {k: p.relative_to(ROOT).as_posix() for k, p in paths.items()}
    row['sha256'] = {k: sha(p) for k, p in paths.items()}
    assert row['sha256']['png'] == row.pop('expected_sha256'), row['id']
    with Image.open(paths['png']) as image:
        row['pixels'] = list(image.size)
        row['dpi'] = list(image.info.get('dpi', (0, 0)))
        image.load()
    with paths['pdf'].open('rb') as stream:
        pdf = PdfReader(stream)
        assert len(pdf.pages) == 1, row['id']
        page = pdf.pages[0]
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        row['size_pt'] = [round(width, 3), round(height, 3)]
        spans = []
        def visit(text, cm, tm, font, size):
            if not text.strip(): return
            x=tm[4]*cm[0]+tm[5]*cm[2]+cm[4]
            y=tm[4]*cm[1]+tm[5]*cm[3]+cm[5]
            scale=math.hypot(tm[2]*cm[0]+tm[3]*cm[2], tm[2]*cm[1]+tm[3]*cm[3])
            spans.append(dict(text=text.strip(), x=x, y=y, size=float(size)*scale))
        page.extract_text(visitor_text=visit)
        # Exclude top/bottom page furniture only. This retains small guides and
        # superscripts; small-font flags are advisory, never automated rejection.
        body = [s for s in spans if height*.08 < s['y'] < height*.92]
        sizes = sorted(s['size'] for s in body)
        size = sizes[max(0, math.floor((len(sizes)-1)*.1))] if sizes else None
        scaled = size * (target_mm*72/25.4) / width if size else None
        row['print_screen'] = dict(target_width_mm=target_mm, body_span_count=len(body),
            body_font_p10_pt=round(size, 2) if size else None,
            at_target_p10_pt=round(scaled, 2) if scaled else None,
            minimum_width_for_7pt_mm=round(width/size*7*25.4/72, 1) if size else None,
            status='REFLOW_OR_LARGER_FORMAT' if scaled and scaled < 7 else
                   'REVIEW_AT_TARGET_SIZE' if scaled else 'RASTER_OR_OUTLINED_TEXT')
        row['pdf_baseline_outside_page'] = [s['text'][:90] for s in spans
            if s['x'] < -1 or s['y'] < -1 or s['x'] > width+1 or s['y'] > height+1]
    receipt = json.loads(paths['meta'].read_text(encoding='utf8'))
    row['prior_geometry_issues'] = receipt.get('geometry_audit', {}).get('issues', [])
    row['visual_review'] = dict(status='PENDING', scope=None)
    row['scientific_acceptance'] = False
    return row


def plates(rows, out):
    """Nine bounded previews per plate; never described as native-size proof."""
    out.mkdir(exist_ok=False)
    font = ImageFont.load_default()
    for start in range(0, len(rows), 9):
        canvas = Image.new('RGB', (2100, 1710), '#e9edf1')
        draw = ImageDraw.Draw(canvas)
        for offset, row in enumerate(rows[start:start+9]):
            x, y = (offset % 3)*700, (offset//3)*570
            draw.rectangle((x+5,y+5,x+695,y+565), fill='white')
            draw.text((x+14,y+12), row['id']+' | '+row['collection'], fill='#203040', font=font)
            with Image.open(ROOT/row['assets']['png']) as source:
                source.thumbnail((672, 510))
                tile = source.convert('RGB')
                canvas.paste(tile, (x+14+(672-tile.width)//2, y+40+(510-tile.height)//2))
                tile.close()
            row['overview_plate'] = f'plate-{start//9+1:02d}.jpg'
        canvas.save(out/f'plate-{start//9+1:02d}.jpg', quality=92)
        canvas.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--plates', type=Path)
    parser.add_argument('--target-width-mm', default=178., type=float)
    args=parser.parse_args()
    if not math.isfinite(args.target_width_mm) or not 40 <= args.target_width_mm <= 1000:
        parser.error('target width must be finite and in [40, 1000] mm')
    assert not args.output.exists(), 'Use a fresh audit output'
    rows=[examine(row, args.target_width_mm) for row in inventory()]
    if args.plates: plates(rows, args.plates)
    archived=list((ROOT/'examples').rglob('*.png'))
    report=dict(schema_version=1, scope='433 current atlas, package and legacy method exports; archived sources inventoried separately',
        counts=dict(current_exports=len(rows), unique_current_png=len({r['sha256']['png'] for r in rows}),
                    archived_and_current_png_files=len(archived)),
        automatic_checks='PNG hash/decode, export hashes, PDF text baseline and advisory physical-size screen',
        limitations=['No biological inference or native R package execution',
                     'Font quantiles are an advisory screen, not a perceptual judgment',
                     'Contact plates cannot establish small-label or print-size acceptance'],
        records=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(counts=report['counts'], print_screen=collections.Counter(r['print_screen']['status'] for r in rows),
        pdf_baseline_flags=sum(bool(r['pdf_baseline_outside_page']) for r in rows))))


if __name__ == '__main__': main()
