"""Measure essential text at a declared physical width; no data changes."""
import math


def print_readability(fig, export):
    from matplotlib.text import Text
    width_mm=export.get('target_width_mm',fig.get_figwidth()*25.4)
    floor=export.get('minimum_text_pt',7.)
    factor=width_mm/(fig.get_figwidth()*25.4)
    excluded=set(getattr(fig,'_software_band_artists',[]))
    samples=[]
    for text in fig.findobj(Text):
        if not text.get_visible() or not text.get_text().strip() or text in excluded:continue
        # Provenance footers remain in the figure; exclude only figure-level
        # furniture from this essential-label metric, not axis labels or guides.
        if text in fig.texts and text.get_position()[1]<.06:continue
        samples.append(dict(text=text.get_text()[:160],native_pt=float(text.get_fontsize()),
                            target_pt=float(text.get_fontsize()*factor)))
    small=[s for s in samples if s['target_pt']+1e-6<floor]
    sizes=sorted(s['target_pt'] for s in samples)
    return dict(target_width_mm=width_mm,native_width_mm=fig.get_figwidth()*25.4,
        minimum_required_pt=floor,essential_text_count=len(samples),
        smallest_pt=min(sizes) if sizes else None,
        p10_pt=sizes[math.floor((len(sizes)-1)*.1)] if sizes else None,
        below_threshold=small,state='NEEDS_SIZE_REVIEW' if small else 'MEASUREMENT_PASS',
        scope='Declared Matplotlib font sizes scaled to target width; provenance footers excluded. Not a perceptual or print proof.',
        visual_acceptance=False)
