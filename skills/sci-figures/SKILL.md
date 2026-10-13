---
name: sci-figures
description: >-
  Guidelines for Nature-style research figures (main, Extended Data, supplementary) and their legends: planning the
  message and outline, layout, visual conventions, colors, scale bars, export to one PDF per figure with editable Arial
  text, legend writing, and independent layout and legend reviews. Use whenever creating, restyling or assembling a
  paper figure or panel; or writing or revising a figure legend.
---

# Scientific figures and legends

You write the plotting code (matplotlib, seaborn, scanpy); this skill says what the result must achieve. The `scifig` package supplies only the style, a few recurring elements and the export.

Paths starting with `references/` or `examples/` are in this skill's folder; all others (`figures/`, `resources/`, scripts) are in the repository you are working in.

## Principles
- **One message.** A figure makes one point along one story line. The message is the legend's title; every panel advances the story.
- **Visual, not verbal.** The figure conveys its message through visual elements. Minimize text; prefer position, color, marks and direct labels to words.
- **Words before pictures.** Format and outline are agreed with the user before anything is drawn.
- **Reproducible.** One script per figure; it only loads and plots data computed beforehand.
- **A restyle changes the look, not the content.** Keep a method's native encodings (PAGA node size = cell count)
  and make style rules coexist with them.
- **Ask when in doubt** about content, conventions or layout.
- **Precedence:** the user's instructions, then this skill, then Nature's [research figure guide](https://research-figure-guide.nature.com/) and [formatting guide](https://www.nature.com/nature/for-authors/formatting-guide), consulted for anything not covered here.

| File | Covers |
|---|---|
| `references/style.md` | visual conventions and panel layout |
| `references/legends.md` | legend conventions |
| `references/review.md` | the layout and legend reviews |
| `examples/` | two complete figures: outline, script, legend |
| `references/setup.md` | installing scifig, Arial and TeX |

## Workflow

### 1. Plan
Agree the format: main, Extended Data or supplementary; width and approximate height (`references/style.md`, Page). Then iterate on an outline until the user approves it, and save it next to the figure script. When the user points at an earlier figure to build on, first list every block it has, from its code or PDF:
```markdown
**Message:** <one sentence; becomes the legend title>
**Story line:** <how the panels build the message, in order>

**a** <panel name>
- Role: <what it adds to the story line>
- Shows: <data, subset, n>
- Plot: <plot type; x, y; color, size and other encodings>
- Shared: <axes, keys or marks shared with other panels, or "none">
- Source: <script or file producing the plotted data; "to be computed" if not yet>
```
Cut panels that don't advance the message. Resolve open questions (n, tests, subsets), then compute and save all plotted data.

### 2. Build
Find the repo's colors (`references/style.md`, Color and marks) and the conventions of existing figure scripts; see `examples/fig1_moscot.py` (plots and a schematic) and `examples/fig2_spatial.py` (images and spatial data). The recurring elements:
```python
import scanpy as sc  # if used
import scifig as sf
sf.apply_style()                                 # after importing scanpy; never sc.set_figure_params
fig = sf.new_figure(183, 120)                    # mm
ax = sf.add_axes_mm(fig, left, top, w, h)        # mm from the top-left corner
sf.embedding_axes(ax)                            # UMAP1/UMAP2 arrows instead of a frame
sf.colorbar(mappable, cax, label="Expression")   # labelled at its ends
sf.scale_bar(ax, 100, "µm", data_unit_size=px_um)
sf.badge(ax, x, y, color, label="3")             # an entity's mark
sf.panel_letter(fig, "a", left, top, title="...", over=ax)  # title centered over ax
sf.save(fig, "figures/fig2_atlas", legend="figures/fig2_atlas_legend.md")
```
If `scifig`, Arial or LaTeX (for equations) is missing, follow `references/setup.md` or tell the user.

### 3. Check
Go through the layout review's checklist (`references/review.md`) yourself, on the preview and zoomed crops of its dense regions. Fix and repeat.

### 4. Legend
Write the legend following `references/legends.md`, from the plotting code, the data (compute n, never estimate it) and the discussion that led to the figure.

### 5. Review
On a near-final draft, run both reviews in `references/review.md` in parallel; afterwards only when the user asks.

### 6. Present
Whenever you show the user a figure (drafts included), show the PDF, not the preview, with its current legend in the same message. At the end, send the PDF and the legend file with the size and raster resolution `sf.save` prints, and list the review findings you declined, each with its reason.

## Output
- `figures/<name>.pdf`, named `fig<N>_<topic>` with figures numbered in reading order (`fig1_overview` ... `figN_<topic>`), so a discussion can name one: vector, with text as editable Arial, except dense scatters and images, which you rasterize (`rasterized=True`). `sf.save` writes rasters at 1200 dpi, lowered to no less than 300 dpi to keep the PDF within 5 MB.
- `figures/<name>_legend.md`: the legend, next to the PDF (`sf.save(..., legend=)` copies it there if it is kept elsewhere, e.g. next to the script).
- `figures/.preview/<name>.png`: for you and the reviewers only; never show or send it to the user.

In Illustrator, each axes sits in a clipping mask (Object > Clipping Mask > Release). Changes made there are not reproduced by the script; limit them to what the script cannot do (e.g. illustrations) and tell the user which parts they are.
