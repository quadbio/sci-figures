**Format:** main figure, 183 mm wide, about 170 mm high.
**Message:** Segmented Xenium transcripts resolve the cell types and niches of a lung cancer section in space.
**Story line:** a standard spatial workflow, one step per row: the section and its tissue (a); raw data of one region (b–d) and its segmentation (e, f); segmentation quality, clustering and annotation of the segmented counts (g–i); the cell types back in space, supported by marker expression per cell, and the niches they form, annotated by composition and geometry (j–l).
**Source** (ref. 1 in the legend)**:** 10x Genomics, FFPE human lung cancer with Xenium multimodal cell segmentation (Xenium Onboard Analysis 2.0.0; CC BY 4.0), in the SpatialData sandbox conversion (https://s3.embl.de/spatialdata/spatialdata-sandbox/xenium_2.0.0_io_spatialdata_0.7.1.zip). Data computed by `fig2_spatial_data.py`.

**a** Section
- Role: what the data are (title: tissue, technology, chemistry, staining), and where the region lies
- Shows: H&E of the section, cropped to the Xenium image; the tissue outline from sopa's tissue segmentation
- Plot: image with the tissue pieces outlined, one color each, keyed by area; the analysed piece bolder in outline and key, and g–l restricted to its cells; scale bar and key on the bright slide; frame on the region, joined to b by its two nearest corners (zoom style of the figure: straight, black with a white edge)
- Shared: the region (b–d, j–l)

**b** H&E
- Role: morphology of the region
- Plot: image; 50 µm scale bar below

**c** Transcripts
- Role: the raw molecular data, with hand-picked genes
- Plot: the transcripts counted into the cells (panel genes, quality ≥ 20) light grey, four marker genes in color (key, its title beside its two rows)
- Shared: genes and their marks with i (bold) and k

**d** Stains
- Role: the images segmentation starts from
- Plot: composite on black, one color per stain; key in one line, each stain by what it marks and its markers; grey frame on the zoom of e and f, inside the tissue
- Shared: stain colors with e and f

**e** Segmented cells
- Role: cell segmentation, from the membrane and interior stains
- Plot: zoom; membrane and cytoplasm stains in their colors (their marks from d's key beside the title), cell outlines white

**f** Segmented nuclei
- Role: nuclear segmentation; introduces the nucleus area used in g
- Plot: zoom; DAPI in its color (its mark beside the title), nucleus outlines white; 10 µm scale bar below

**g** Segmentation quality
- Role: the standard metrics to judge the segmentation, on the analysed piece of a, and the filter applied before clustering
- Plot: histograms of transcripts per cell (cells below 10 light grey), genes per cell, cell area, nucleus-to-cell area ratio

**h** Leiden clusters
- Plot: UMAP colored by cluster, each labelled by its outlined badge
- Shared: cluster badges with i

**i** Marker genes
- Role: what each cluster is, and the resulting cell types
- Plot: dot plot, clusters (badges) by genes; color, scaled mean expression; size, fraction expressing; genes of c bold; a color bar per cell type over its clusters, named (the cell type key)
- Shared: cell type colors with j

**j** Cell types over DAPI
- Plot: cell polygons colored by cell type at 60% opacity over DAPI in its color from d (its mark beside the title); cells failing QC grey

**k** Expression per cell
- Role: supports j with the data it rests on
- Plot: one map of two genes of c: each cell filled by the expression of its dominant gene, in that gene's transcript color (light to full), one scale; cells expressing neither outlined; two colorbars titled by the genes and the scale bar of j–l in one key column

**l** CellCharter niches as polygons: cell types and geometry
- Role: the higher-order structure the cell types form, annotated; larger polygons colored with fill and outline opacity
- Shows: six CellCharter niches (reproducible fit), drawn as the union of their cells' polygons (every cell inside its own niche; sopa's centroid-based vectorize_niches put only half of them there) in the region; per niche, composition and geometry
- Plot: left, niche polygons (fill 45%, 0.9 pt outlines) over the region's cells colored as in j, faded; right, one row per niche (badge, name; "Niche" label): stacked cell-type composition, then the area and roundness of its polygons (averaged over its area) and the median depth of its cells in the tissue, as bars in the niche's color
- Shared: cell type colors with i and j; niche badges and colors between map and rows
