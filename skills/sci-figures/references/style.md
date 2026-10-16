# Visual conventions

(Nature) marks rules from Nature's research figure guide. What the figure shows versus what the legend says: `legends.md`, Figure and legend.

## Page
- Width 89 mm (one column) or 183 mm (two) for main figures; 180 mm for Extended Data, narrower only when the user asks. Height at most 170 mm, leaving room for the legend (Nature), and no more than the content needs.
- Panels and their letters line up: within a row always, within a column where possible.
- Little whitespace. Find the element that fixes the figure's extent and size the others to fill what it leaves; likewise within a panel (e.g. a key column taller than its plot). Empty space beside a squeezed element is a layout error.
- Spacing encodes grouping: elements that belong together sit closer than elements that don't.
- Elements of one kind (text, key markers, points, lines) share one size across the figure unless there is a reason to differ.

## Panels
- Each panel is a box with its letter at the top-left corner. Nothing of the panel, text included, lies left of or above its letter or outside its box.
- The letter's row holds only the panel title, on the letter's line and centered over the plot or plots it titles (`sf.panel_letter(title=, over=)`); without a title it stays empty. Labels of the individual plots within a panel (e.g. each image's gene) sit below that line, never on it. The letter's column holds only vertical text, such as the leftmost y-axis label, whose left edge lines up with the letter's left edge. Nothing else, text or graphics (images included), enters either band: an image starts right of its letter's column.
- Give a title only when the panel isn't self-explanatory, case by case (if in doubt, ask while planning), and then to every panel of its row. A title says specifically what is shown, and how where that is the point ("Segmented cells", not "Cells"; "CellCharter niches as polygons", not "Cellular niches"); an overview panel's title may introduce the data (tissue, technology, setting).
- A panel shows one step or comparison; split one whose parts would be referred to separately.
- What a panel is about is emphasized (full color, thicker lines); context drawn with it is faded.
- A panel's keys (legends, colorbars, size keys, scale bars) form one block: aligned on one edge, equally spaced, filling the space the layout gives them. A key aligns with the plot it belongs to, not with the panel letter.

## Sharing
- Plots showing the same quantity share one axes where possible; otherwise they use the same limits. Within a panel only the outer axes are labelled; each lettered panel labels its own.
- A shared key is drawn once, with the first panel (in reading order) that uses it.
- One key per encoding (color, shape, size), labelled with what it shows ("Cell type") where space allows, rather than repeating it in a title.

## Text
- Arial, embedded as editable TrueType. Panel letters 8 pt, bold, lowercase; all other text 7 pt (Nature: "please use 7-pt text"). Where density forces smaller text (e.g. a heatmap's gene names, badge IDs), shrink that role throughout the figure, to no less than 5 pt. `sf.apply_style` sets these.
- Nothing below 5 pt, superscripts included (mathtext shrinks them; LaTeX at 7 pt keeps them at 5).
- Black only: color goes on a mark or key, never on text (Nature: "Avoid coloured text").
- Sentence case, no final periods; units in parentheses ("Runtime (min)").
- Gene names italic, following species conventions (mouse *Tbx5*, human *TBX5*); proteins upright.
- Label a few groups directly, next to their line or cluster, rather than with a key.
- Break long tick labels over lines ("Pre-\ngastrulation") rather than abbreviating.
- Symbols missing from Arial are drawn as markers, not typed.

## Equations
- Typeset by LaTeX: `usetex=True` on the equation's text only (needs TeX, `README.md`). One equation is one string, never assembled from pieces.
- Variables italic, names and operators upright (`\mathrm{FGW}`, `\min`). A label containing a symbol is typeset by LaTeX too, so it matches.
- Label terms in the equation, at 7 pt (`\underbrace{D\nabla^2 c}_{\textstyle\text{diffusion}}`). Keep the maths apart from the illustration, which labels the symbols it shows.
- Each symbol means one thing, is defined where it first appears, and is the same in equation, illustration and legend; a drawn result is named in its equation (`P^* = \arg\min ...`). Check every equation against the code and its source.
- Equations on one line are joined by a connector stating their relation: a comma when they stand side by side, an arrow or "where" when one builds on the other.

## Connections
- A zoom is joined to its source: a frame on the source, the same frame around the zoom, and lines joining the two nearest corners of each (a zoom below its source: the frame's bottom corners to the zoom's top corners). `ax.indicate_inset_zoom` joins matching corners instead; draw the lines with `ConnectionPatch`. Choose the region and the zoom's position so the lines are short and cross little data, with the frame entirely inside the tissue. Lines keep clear of panel letters and titles; curve them (`connectionstyle="arc3,rad=..."`) where a straight line would pass one, and then curve all zoom lines of the figure, or none. Overview and zoom each get their own scale bar.
- A zoom's frames and lines share one color and the data line width (`sf.LINEWIDTHS["data"]`), and contrast with everything under them, overlays included (not white over white outlines). All zooms of a figure share one style; black with a thin white edge (`patheffects.withStroke`) reads on any background.
- A frame on an image is explained in the figure itself (e.g. as the source of a zoom), not only in the legend.
- Elements shown in two places are tied visually: the same mark on both (`sf.badge`) or a line between them. Where a panel shows a subset of another panel's items, highlight that subset there (e.g. bold gene names). Where an overview shows several objects (e.g. tissue pieces) and the later panels use one, mark that one there (e.g. bolder) and keep the later panels to it.
- A label points to part of an illustration with an arrow from outside it; arrows are as thick as data lines and end exactly at their target.
- Process arrows are horizontal by default. A quantity used further along is labelled where it is drawn and referred to by its symbol, not reached by a long arrow.

## Axes
- Left and bottom spines, outward ticks, no grid, no background.
- 3 to 5 ticks at round numbers; bar charts start at 0.
- Time axes are metrically faithful (weeks 2, 3, 4, 6 on a linear axis), never categorical.
- A metric with a better direction ends its axis label with an arrow (↑ or ↓), defined once in the legend, rather than "higher is better" text. On a y label rotated to read upwards the glyph turns too: write → for up and ← for down.

## Plot types
- **Embeddings:** `sf.embedding_axes`; when the same embedding repeats, its indicator appears once.
- **Spatial plots and images:** no axes, equal aspect, a scale bar instead of a magnification. Each image identifies exactly what it shows, stains and overlays, including an image under an overlay ("Cell types over DAPI"), by title, key or a color tied to a key; stains are named by what they mark and by their markers ("Membrane (ATP1A1/CD45/E-cadherin)"). A segmentation is shown over the stains it was computed from.
- **Categorical keys:** key marks match the plot's marks.
- **Continuous color:** viridis; where most values are near zero (e.g. dot plots), a light-to-dark single hue (e.g. `Reds`); diverging values (correlations, fold changes) RdBu_r centered at 0. `sf.colorbar`, vertical by default; numeric ends are exact values.
- **Background cells:** light grey (#d3d3d3), drawn first.
- **Bars:** solid, no edges; thin black error bars without caps.
- **Box plots:** thin black lines and median, individual points overlaid, no fliers.
- **Replicates:** one point per replicate plus median and interquartile range; no lines connecting time points.
- **Heatmaps:** genes as rows with italic labels; groups annotated by color bars rather than text.
- **Expression trends:** one line per lineage in its color, shaded uncertainty band.
- **Schematics:** drawn in the script where possible; an empty dashed frame where an illustration will be added in Illustrator. A schematic visualizes the flow of what it depicts (a computation from inputs to output, data from generation to processing, events in time), its steps tied together visually (arrows, braces, alignment); the arrangement is free. It shows the real steps with intuition rather than worked numbers; made-up data get generic names (cell types A, B, C) and colors that can't be mistaken for those of real data. Before designing one, look at how high-impact method papers draw comparable ideas (their PDFs, read as page images).

## Color and marks
- Each entity keeps one mark across the paper: its color, plus an ID if it has one (e.g. its cluster number in a circle, `sf.badge`), wherever it appears (row labels, titles, keys, small multiples). Different kinds of entity (e.g. the clusters of two annotations) may differ in shape (`sf.badge(marker=)`). A mark drawn over data stands out from it, e.g. an outlined badge over points of its own color. A color mark ties a label to a plot only if the plot is drawn in that color. Regions of one kind that repeat (e.g. niches) are identified by color and key, not by a badge at one centroid. Separate objects of one kind drawn together (e.g. tissue pieces) get distinct colors and a key.
- Conventions are defined once per repo, in `resources/figure_conventions.yaml` (git-tracked; ask before creating or extending it), one section per kind: `colors` for objects without an `adata.uns` home, such as methods; `markers` for the shape of each kind of entity or role; others as the repo needs.
- Colors come, in this order, from `adata.uns[f"{key}_colors"]` for categorical observations; the conventions file; scanpy's defaults for new variables, then stored in `adata.uns` (tell the user to save the AnnData). On a clash, recolor the object without a canonical home.
- Different variables get distinct colors from an accessible palette. Above about ten categories, group them or label them directly.

## Scale bars
A wrong scale bar is a scientific error.
- Derive `data_unit_size` for `sf.scale_bar` from the dataset's metadata (µm per pixel, image scale factors such as Visium `tissue_hires_scalef`, SpatialData transformations), never by eye.
- An image and the points drawn on it share one coordinate system, also when the image is downsampled or cropped.
- One bar may stand for several images only if they share one scale; otherwise each image or zoom gets its own.
- A bar sits on the image only over empty, uniform background where it reads easily (e.g. a bright slide); otherwise outside the image, never over data.
- In Illustrator, scale an image only together with its bar and only uniformly; then compare the bar with the length `sf.save` printed.
