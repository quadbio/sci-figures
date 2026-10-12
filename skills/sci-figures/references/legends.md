# Legend conventions

Legends follow Nature's copy-edited style, whatever the target journal; one legend per figure (`SKILL.md`, Output). At most 400 words (markup excluded), a deliberate departure from Nature's 300: brief method facts are welcome, since the author reads legends as a summary of how a figure was made.

## Figure and legend
- The figure alone conveys the message: axis labels, the marks of `style.md` (Color and marks), and keys for every encoding the message depends on, however simple. (Nature prefers keys in the legend "where possible"; for keys the message depends on, it isn't.)
- The legend gives technical details and the exact definition of every visual element: n, tests, selection rules, omitted groups and why, and conventional elements recognised without a key (median and IQR lines, whiskers, error bars).
- It states what the plot hides. Check the code and data for non-linear or broken axes and color scales (and where they change), values beyond the axis limits or colorbar ends, capped marker sizes, jitter, and scales shared or not.
- The legend adds precision, not repetition: where a key says it fully, don't repeat it; where it gives the gist ("Canonical gene"), give the definition.
- Counts go in the legend; a definition central to the message (e.g. a score's genes) in the figure.
- Never describe a filter or masking rule that removed nothing; state the actual range.
- Simulated data are fine, stated as such.
- No interpretation: conclusions belong in the main text.

## Structure
```markdown
**Fig. 2 | <Title>.**
**a**, <Panel description, statistics included>. **b**,**c**, <Shared description>; <b-specific> (**b**) and <c-specific> (**c**). **d**, <...>, shown as in **b**. <Abbreviations>. <Attributions>.
```

## Title
A declarative result in bold, present tense: "Moscot faithfully reconstructs atlas-scale developmental trajectories." Overview and Extended Data figures may be descriptive: "Overview of CITE-seq data and mapped annotations."

## Panel descriptions
- One self-contained description per panel, statistics included (Nature: "a short description of each panel and the symbols used"). Later panels refer back in bold, without parentheses ("shown as in **b**"), never forward. Schematics need no color explanation.
- State the data with numbers computed from it and the dataset citation at first mention: "UMAP of 31,029 embryoid body cells<sup>32</sup>".
- Panel letters bold with a comma (**a**,). Grouped panels (**b**,**c**,) are told apart by tags: "(**b**)", "(**c**, left)". Sub-panels by position: "Top, <...>. Bottom, <...>."
- Scale bars: "Scale bar, 100 µm."
- Never add references to Methods or Supplementary items; the author adds them.

## Statistics (in each quantitative panel's description)
- n and what it counts: "n = 36 genes".
- Error bars and bands: "Error bars denote the 95% confidence interval across n = 10 random seeds."
- Box plots (matplotlib and seaborn defaults; check `whis` in the code): "Box plots show the median (center line) and interquartile range (box); whiskers extend to the most extreme values within 1.5× the interquartile range of the box; points denote individual <units>."
- Tests: name, sidedness, multiple-testing correction, and P values or where they are shown: "two-sided Wilcoxon rank-sum test, Benjamini–Hochberg corrected".
- Correlations: type and what each point is.

## Abbreviations, citations, attributions
- One closing sentence defines the abbreviations shown in the figure, in order of first appearance reading panel by panel: "CR, Cajal–Retzius cell; fibro, fibroblast; ..." Abbreviations used only in the legend text are defined in the main text; if the main text does not, add them here.
- Gene names italic (`*Tbx5*`), as in the figure.
- Citations as superscripts (`<sup>7</sup>`); "(refs. 16,17)" where a superscript would be ambiguous, e.g. after "CellRank 2".
- Attributions last: "Panel **a** was created using BioRender (https://www.biorender.com)."

## Language
- Sentences parse one way only. Frame first, so a list can't bind to its last item. Ambiguous: "Expression of cell-cycle genes, lineage markers and genes expected to be silent in each progenitor and its daughter cell types". Clear: "For each progenitor, expression of cell-cycle genes, lineage markers and genes expected to be silent, in the progenitor and in its daughter cell types."
- Parallel facts in parallel form: "n = 4,210/18,377 (HSC/progeny), 1,906/9,452 (CMP/progeny)".
- Plain, precise sentences; no em dashes; en dashes for ranges (E8.0–E8.25); terms consistent with the main text; each fact once.

## Example (Klein et al., Nature 2025, Fig. 4; Methods and Supplementary references added by the authors)

**Fig. 4 | Inference of spatiotemporal dynamics with moscot.** **a**, Schematic of spatiotemporal trajectory inference of mouse embryogenesis. **b**, Accuracy of curated transitions across developmental stages (Methods and Supplementary Table 5) for the temporal and spatiotemporal application of moscot compared with TOME<sup>7</sup>. **c**, Mapping heart cells across time points (bottom) and ground-truth annotation of the heart lineage (top). **d**, Heart-lineage driver genes found by interfacing moscot with CellRank 2 (refs. 16,17). Top, *Tbx20* encodes a TF known to have various fundamental roles in cardiovascular development. Bottom, *Myl7* encodes a protein related to metabolism and heart regeneration (Supplementary Table 7). **e**, Transferring high-resolution cell-type annotations only provided in the latest time point (E16.5) to earlier time points. **f**, Pearson's correlations of gene expression with neuronal (*x* axis) and fibroblast (*y* axis) fate probabilities. Annotated genes are among the top 20 driver genes and were previously associated with fibroblasts and neuronal lineage (Supplementary Tables 7 and 8). **g**, Spatial visualization of sample neuronal-driver genes, *Neurod2* and *Sox11* (Supplementary Table 8). Cere gran NeuB, cerebellar granule neuroblast; corti, cortical; CR, Cajal–Retzius cell; fibro, fibroblast; die, diencephalon; dors, dorsal; endo, endothelial; ery, erythrocyte; Fb, forebrain; Glu, glutamatergic; neu, neuron; Hb, hindbrain; hypo, hypothalamus; Mb, midbrain; VH, ventromedial hypothalamus. Panel **a** was created using BioRender (https://www.biorender.com).
