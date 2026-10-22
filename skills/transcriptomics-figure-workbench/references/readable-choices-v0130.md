# v0.13 · Readable alternatives and coordinated inspection

Use this extension when choosing a compatible form or inspecting linked objects.
All classic and historical renderers remain available. The three choices below
are display modes of the existing inspector, not three new scientific methods.

## Choose from the same frozen result

| View `kind` | Prefer when | Required channels | Actual example |
|---|---|---|---|
| `scatter` (default) | Many objects, geometry or overlap matters | `x`, `y`, identity and group | [144 objects / six groups / missing pairs](../assets/connected-examples/longlabels/index.html) |
| `labels` | A small, explicitly selected scope needs visible identities | Same channels; at most 30 complete pairs | [12 labelled objects](../assets/connected-examples/labels/index.html) |
| `interval` | Effect magnitude and supplied uncertainty matter | `x`, `y`, `x_lower`, `x_upper`, `interval_label` | [Six effects with exact supplied bounds](../assets/connected-examples/intervals/index.html) |

All modes preserve shared selection, named filters, full register, missing pairs
and stable axis domains. `y` in the interval example is a declared source-order
display row; it is not another measured outcome. Its adjacent labelled panel
demonstrates an alternative form, not an additional independent analysis.
Intervals are not inferred from points. Missing either bound makes that interval
pair unavailable, rather than dropping the bound or substituting zero. Bounds
must contain the supplied estimate. Shared x columns include the full endpoint
range in every view. Interval meanings need explicit text; bounds do not become
95% confidence intervals merely through this display.

### Invocation

From the installed skill root, use a fresh destination:

```sh
python scripts/workbench.py linked-views --request assets/connected-examples/longlabels/request.json --output outputs/linked-six-groups
python scripts/workbench.py linked-views --request assets/connected-examples/labels/request.json --output outputs/linked-labels
python scripts/workbench.py linked-views --request assets/connected-examples/intervals/request.json --output outputs/linked-intervals
```

Existing v1 requests remain valid. Add `kind: "labels"` to a compatible view,
or add the following fields to an interval view:

```json
{"kind":"interval", "x_lower":"lower", "x_upper":"upper",
 "interval_label":"Supplied illustrative bounds; not recalculated"}
```

## Layout and readability decisions

- Keep words intact when wrapping titles and unit-bearing axis labels; long
  unbroken identifiers may wrap by character. Adapt axis margins and panel height.
- Requested columns are a maximum constrained by available panel width. A
  single remaining panel can span the last two-column row. Avoid squeezing a
  three-column layout into a narrow requested canvas.
- The SVG is redrawn at the requested export width and panel height. A phone
  viewport must not change export columns, text scale or geometry. Titles,
  guides, missing counts, interval meanings and source context remain present.
- Every group has a named legend filter, complete input count and consistent
  colour/shape. Six shapes repeat for more than six groups, explicitly disclosed;
  use named filters and the register for identity. This is not a claim that 20
  overlapping categories are equally distinguishable or fully accessible.
- One point per panel enters the Tab sequence. Arrow keys browse source order;
  Home/End jump and Enter/Space select. Focus and selection are separate. The
  table exposes exact parsed numeric values rather than four-digit display
  rounding; the original exact TSV bytes are also retained.
- Full labels are optional for small scopes. Larger scopes use point selection;
  do not truncate the dataset to make a label mode pass. Dense label placement
  still needs visual review with the actual identifiers and selected scope.

These are screen-oriented inspection views. Formal print size, PDF accessibility,
screen-reader usability and scientific acceptance require their own assessment.

## Sources reviewed through SciSpace and primary records

Search date: 2026-10-22. The search question asked about multi-panel biomedical
figures, raincloud/forest alternatives, categorical colour and dense linked views.
SciSpace discovery and generated methods summaries were checked against the
following primary records. A repository supplement and two preprint records are
not separate empirical studies.

| Source | Evidence and adopted idea | Limit |
|---|---|---|
| [Jambor, 2024 preprint](https://arxiv.org/abs/2408.16007) | Biological-figure checklist; match the task, colour and layout. Applied to explicit choice rules and final-size inspection. | Guidance is not an experiment proving every complex form superior. Preprint and later journal version are linked versions. |
| [Ramsey & Schroeder, 2025](https://doi.org/10.1021/acs.chas.4c00141) | Commentary on accessible scientific figures; add structural and textual cues alongside colour. Implemented shapes, named legends and readable text. | Not an empirical aesthetics trial or a full WCAG certificate for this workbench. The indexed `.s004` DOI is supporting material. |
| [Fitzgerald et al., 2025](https://doi.org/10.1017/rsm.2025.4) | Randomized comparison of revised MARC with other meta-analysis displays; choice depends on audience/task. Retain raincloud and forest alternatives. | Studied communication of meta-analysis to non-research audiences; does not prove rainclouds best for expression QC, nor authorize estimating densities/intervals while styling. |
| [W3C colour guidance](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html), [keyboard guidance](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) | Colour is supplemented; Tab moves between components, arrows within them. Independently implemented linked navigation. | Guidance and automated tests are not a complete assistive-technology audit. |

All implementation and fixtures are original. No article figures, scripts,
fonts or external package code are copied or redistributed. Existing numerical
coordinates and intervals come from this package's published synthetic fixtures.
Authored group labels, source-order rows and explicit NA substitutions test
display behaviour; they are not biological results.
