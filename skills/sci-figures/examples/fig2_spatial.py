"""Example spatial figure on a 10x Xenium lung cancer section: from raw images and transcripts
through segmentation and clustering back to cell types and niches in space. spatialdata-plot
draws the images, polygons, outlines, transcripts and cells into scifig's mm axes; scifig adds
keys, scale bars and letters.

Run fig2_spatial_data.py first, then
    python skills/sci-figures/examples/fig2_spatial.py
with XENIUM_LUNG and SCIFIG_DEMO_DATA as there. Writes figures/fig2_spatial.pdf, its legend and
figures/.preview/fig2_spatial.png.
"""

import os
from pathlib import Path

import anndata as ad
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import spatialdata as sd
import spatialdata_plot  # noqa: F401 (registers sdata.pl)
import yaml
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.text import Annotation
from spatialdata.models import PointsModel, TableModel
from spatialdata.transformations import get_transformation

import scifig as sf

sf.apply_style()  # after importing scanpy

ZARR = Path(os.environ.get("XENIUM_LUNG", "data/xenium_lung/data.zarr"))
DATA = Path(os.environ.get("SCIFIG_DEMO_DATA", "data/fig2_spatial"))
sdata = sd.read_zarr(ZARR)
cells = ad.read_h5ad(DATA / "cells.h5ad")
for name in ("tissue", "niches"):  # sopa's tissue pieces; the niche polygons
    sdata.shapes[name] = sd.read_zarr(DATA / f"{name}.zarr")[name]
MIN_TRANSCRIPTS = 10  # as in fig2_spatial_data.py

conventions = yaml.safe_load((Path(__file__).parent / "resources/figure_conventions.yaml").read_text())["colors"]
stain_colors = conventions["stains"]  # by marker, in the image's channel order
CHANNELS = dict(zip(stain_colors, ["DAPI", "ATP1A1/CD45/E-Cadherin", "AlphaSMA/Vimentin"], strict=True))
MARKS = dict(zip(stain_colors, ["Nuclei", "Membrane", "Cytoplasm"], strict=True))  # what each stain marks
DAPI, MEMBRANE, CYTOPLASM = stain_colors
gene_colors = conventions["transcript_genes"]  # a marker of each major cell type in the region
genes = list(gene_colors)
EXPR_GENES = ["EPCAM", "LTBP2"]  # tumour and stroma, in one plot

# each cell's expression of its dominant gene of EXPR_GENES, under that gene's name (else NaN)
expr = pd.DataFrame(cells[:, EXPR_GENES].X.toarray(), columns=EXPR_GENES, index=cells.obs_names)
for g in EXPR_GENES:
    cells.obs[f"{g}_dominant"] = expr[g].where((expr[g] > 0) & (expr[g] == expr.max(axis=1)))

# the processed table annotates the cell polygons, so spatialdata-plot can color them
cells.obs["region"] = pd.Categorical(["cell_boundaries"] * cells.n_obs)
del cells.uns["spatialdata_attrs"]
sdata.tables["table"] = TableModel.parse(cells, region="cell_boundaries", region_key="region", instance_key="cell_id")

# coordinates: 'global' is in morphology-image pixels; µm per pixel from the shapes' transformation
UM = 1 / get_transformation(sdata["cell_boundaries"], "global").scale[0]


def box(x, y, side):
    """Square region (x0, y0, x1, y1) in global units, from its corner and side in µm."""
    return np.array([x, y, x + side, y + side]) / UM


def crop(b):
    # the full table: filter_table=True drops the colors of categories absent from the crop but
    # keeps the categories, which shifts every later category's color
    return sd.bounding_box_query(
        sdata,
        axes=("x", "y"),
        min_coordinate=b[:2],
        max_coordinate=b[2:],
        target_coordinate_system="global",
        filter_table=False,
    )


# the region (below its frame in a, so the zoom lines are short) and the zoom into its stains
# (inside the tissue, near the region's edge facing the zoom images)
ROI, ZOOM = box(1000, 2150, 300), box(1225, 2240, 60)
roi, zoom = crop(ROI), crop(ZOOM)
# the region's transcripts as counted into the cells' matrix: panel genes decoded at quality >= 20,
# without the control and unassigned codewords
tx = roi["transcripts"].compute()
tx = tx[(tx["qv"] >= 20) & tx["feature_name"].astype(str).isin(cells.var_names)]
roi.points["transcripts"] = PointsModel.parse(
    tx,
    coordinates={"x": "x", "y": "y"},
    feature_key="feature_name",
    transformations=get_transformation(roi["transcripts"], get_all=True),
)
print(f"{len(tx)} transcripts in the region")

ct_colors = dict(zip(cells.obs["cell_type"].cat.categories, cells.uns["cell_type_colors"], strict=True))
cl_colors = dict(zip(cells.obs["leiden"].cat.categories, cells.uns["leiden_colors"], strict=True))
niche_colors = dict(zip(cells.obs["niche"].cat.categories, cells.uns["niche_colors"], strict=True))
LW, ZOOM_LW = sf.LINEWIDTHS["axis"], sf.LINEWIDTHS["data"]
HALO = [pe.withStroke(linewidth=ZOOM_LW + 1.0, foreground="white")]  # zooms: black, white-edged, for any background


def show(render, ax, b):
    """Draw a spatialdata-plot rendering into ``ax`` without its own title, keys or frame, view
    ``b``, dense layers rasterized."""
    render.pl.show(ax=ax, title="", coordinate_systems="global", frameon=False, colorbar=False, legend_loc=None)
    for child in ax.get_children():  # the second legend drawn for outlines colored by a column
        if isinstance(child, Legend):
            child.remove()
    ax.set_xlim(b[0], b[2])  # the element's extent otherwise; cells crossing the crop widen it
    ax.set_ylim(b[3], b[1])  # image orientation: y down
    for c in ax.collections:
        c.set_rasterized(True)


def stains(markers, q=99.5):
    """render_images arguments for ``markers``: each scaled from zero to its ``q``th percentile in
    the region and colored black to its color, as in the composite."""
    img = roi["morphology_focus"]["scale0"].image
    return {
        "channel": [CHANNELS[m] for m in markers],
        "palette": [stain_colors[m] for m in markers],
        "norm": [Normalize(0, np.percentile(img.sel(c=CHANNELS[m]).values, q)) for m in markers],
        "scale": "scale0",
    }


def zoom_lines(src, b, dst, more=()):
    """Frame region ``b`` on ``src`` and the zoom ``dst`` (and the zooms ``more`` beside it) showing
    it, and join the two nearest corners of frame and ``dst``."""
    x0, y0, x1, y1 = b
    src.add_patch(
        Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="black", lw=ZOOM_LW, zorder=10, path_effects=HALO)
    )
    for ax in (dst, *more):
        ax.add_patch(
            Rectangle(
                (0, 0),
                1,
                1,
                transform=ax.transAxes,
                fill=False,
                ec="black",
                lw=ZOOM_LW,
                clip_on=False,
                zorder=10,
                path_effects=HALO,
            )
        )
    a_data = np.array([(x0, y0), (x1, y0), (x0, y1), (x1, y1)])
    b_axes = np.array([(0, 0), (1, 0), (0, 1), (1, 1)])
    a, d = src.transData.transform(a_data), dst.transAxes.transform(b_axes)  # display, y up
    shift = d.mean(0) - a.mean(0)
    axis = int(abs(shift[1]) > abs(shift[0]))  # 0: side by side, 1: one above the other
    facing_a = np.argsort(a[:, axis] * np.sign(shift[axis]))[-2:]  # the corners facing the other
    facing_d = np.argsort(d[:, axis] * np.sign(shift[axis]))[:2]
    for i, j in zip(
        facing_a[np.argsort(a[facing_a, 1 - axis])], facing_d[np.argsort(d[facing_d, 1 - axis])], strict=True
    ):
        fig.add_artist(
            ConnectionPatch(
                a_data[i],
                b_axes[j],
                coordsA=src.transData,
                coordsB=dst.transAxes,
                color="black",
                lw=ZOOM_LW,
                path_effects=HALO,
            )
        )


def bar(ax, length, anchor=(1, 0), loc="upper right"):
    """Scale bar (µm) in ``ax``'s data units, anchored outside the image (default: under its
    lower-right corner), off the data."""
    sf.scale_bar(
        ax,
        length,
        "µm",
        data_unit_size=UM,
        loc=loc,
        bbox_to_anchor=anchor,
        bbox_transform=ax.transAxes,
        borderpad=0,
        pad=0.2,
    )


def key(ax, colors, title=None, anchor=(1.03, 1), italic=False, marker="o", labels=None, **kw):
    """Categorical key with its upper-left corner at ``anchor`` (axes fraction)."""
    size = 3.5  # pt
    handles = [
        Line2D([], [], marker=marker, ls="", color=c, markeredgecolor="none", markersize=size) for c in colors.values()
    ]
    leg = Legend(
        ax,
        handles,
        labels or list(colors),
        title=title,
        loc="upper left",
        bbox_to_anchor=anchor,
        borderaxespad=0,
        borderpad=0,
        alignment="left",
        handlelength=size / sf.SIZES["text"],
        **kw,
    )
    if italic:
        for t in leg.get_texts():
            t.set_fontstyle("italic")
    ax.add_artist(leg)
    return leg


def ylabel(ax, text, left):
    """Y label whose left edge sits at ``left`` mm, flush with the panel letter."""
    p, fw = ax.get_position(), fig.get_figwidth() / sf.MM
    ax.set_ylabel(text, va="top")
    ax.yaxis.set_label_coords((left / fw - p.x0) / p.width, 0.5)


# --- layout (mm): one row per step. A letter's column holds only vertical text, so images start
# IND right of their letter; panels 4.5 mm apart ---
W, HA, S, S4, IND = 183, 33, 30, 26, 2.5  # width; heights of the section and the images (rows 2, 4)
yc, ha = 9800, 51187 * HA / (W - 1 - IND - 1)  # the section's centre and height in global units
SECTION = np.array([0, yc - ha / 2, 51187, yc + ha / 2])  # the Xenium image's full width
R2 = 5 + HA + 3  # tops of rows 2 to 4
R3 = R2 + 4 + S + 10
R4 = R3 + 47  # under i's 14 cluster rows
fig = sf.new_figure(W, R4 + 37.5)  # row 4 ends with the profiles' axis labels
ax_sec = sf.add_axes_mm(fig, 1 + IND, 5, W - 2 - IND, HA)
col = [1 + i * (IND + S + 4.5) for i in range(5)]  # letters of b to f
ax_he, ax_tx, ax_stain, ax_cells, ax_nuc = (sf.add_axes_mm(fig, x + IND, R2 + 4, S, S) for x in col)
ax_qc = [sf.add_axes_mm(fig, 10 + j * 27, R3 + 5 + i * 21, 21, 13) for i in range(2) for j in range(2)]
ax_umap = sf.add_axes_mm(fig, 67, R3 + 5, 33, 33)
COL4 = [1, 33.5, 79]  # letters of j, k and l
ax_types = sf.add_axes_mm(fig, COL4[0] + IND, R4 + 7.5, S4, S4)
ax_expr = sf.add_axes_mm(fig, COL4[1] + IND, R4 + 7.5, S4, S4)
ax_niche = sf.add_axes_mm(fig, COL4[2] + IND, R4 + 7.5, S4, S4)
# the niche profiles right of l's map: per niche (rows), its cell-type composition and geometry
PROFILE = {"comp": (136.5, 11), "area": (150.5, 8), "roundness": (161, 8), "depth": (172, 9)}  # left, width (mm)
ax_prof = {k: sf.add_axes_mm(fig, x, R4 + 7.5, w, 20) for k, (x, w) in PROFILE.items()}

# a: the section in H&E (the Xenium image's width), with the tissue pieces sopa contoured from it,
# one color each, keyed with their areas; the analysed piece (1, the largest) bolder, in outline and
# key. Frame, the region of b-d and j-l. Scale bar and key on the bright slide
tissue = sdata.shapes["tissue"]
area = (tissue.area * UM**2 / 1e6).set_axis(tissue["piece"].astype(str)).sort_index()  # mm², by piece
pieces = list(area.index)
piece_colors = dict(zip(pieces, conventions["tissue_pieces"], strict=False))
piece_lw = {p: 2 * ZOOM_LW if p == "1" else ZOOM_LW for p in pieces}
analysed = (tissue["piece"].astype(str) == "1").to_numpy()
sdata.shapes["tissue_other"], sdata.shapes["tissue_analysed"] = tissue[~analysed], tissue[analysed]
render = sdata.pl.render_images("he_image", scale="scale2")
for name, lw in [("tissue_other", ZOOM_LW), ("tissue_analysed", 2 * ZOOM_LW)]:
    render = render.pl.render_shapes(
        name,
        color="piece",
        palette=piece_colors,
        fill_alpha=0,
        outline_color="piece",
        outline_alpha=1,
        outline_width=lw,
        method="matplotlib",
    )
show(render, ax_sec, SECTION)
sf.scale_bar(ax_sec, 1, "mm", data_unit_size=UM / 1000, loc="upper left")
key_left, key_top = 21 / (W - 2 - IND), 1 - 1.0 / HA  # axes fraction, right of the scale bar
label = ax_sec.text(key_left, key_top, "Tissue pieces (sopa; mm²):", transform=ax_sec.transAxes, va="top")
fig.canvas.draw()
label_w = label.get_window_extent().width / ax_sec.get_window_extent().width
leg = Legend(
    ax_sec,
    [Line2D([], [], color=piece_colors[p], lw=piece_lw[p]) for p in pieces],
    [f"{area[p]:.2f}" + (", analysed" if p == "1" else "") for p in pieces],
    ncols=len(pieces),
    loc="upper left",
    bbox_to_anchor=(key_left + label_w + 0.008, key_top),
    borderaxespad=0,
    borderpad=0,
    handlelength=1.2,
    columnspacing=0.8,
)
leg.get_texts()[0].set_fontweight("bold")
ax_sec.add_artist(leg)

# b: the region's H&E; c: its transcripts, those of four marker genes in color; d: its stains, one
# color each, with the zoom of e and f framed
show(roi.pl.render_images("he_image", scale="scale0"), ax_he, ROI)
zoom_lines(ax_sec, ROI, ax_he)
bar(ax_he, 50)
show(
    roi.pl.render_points("transcripts", color="#cccccc", size=0.05, method="matplotlib").pl.render_points(
        "transcripts", color="feature_name", groups=genes, palette=gene_colors, size=0.3, method="matplotlib"
    ),
    ax_tx,
    ROI,
)
key(ax_tx, gene_colors, anchor=(3.2 / S, -0.04), italic=True, ncols=2, columnspacing=1.0)
ax_tx.text(
    0, -0.04 - 2.6 / S, "Gene", rotation=90, transform=ax_tx.transAxes, ha="left", va="center"
)  # at the image's edge
show(roi.pl.render_images("morphology_focus", **stains(stain_colors)), ax_stain, ROI)
key(
    ax_stain,
    stain_colors,
    anchor=(0, -0.04),
    marker="s",
    ncols=3,
    columnspacing=1.2,
    labels=[f"{MARKS[m]} ({m})" for m in stain_colors],
)  # one line, under d to f

# e, f: the zoom, with the stains each segmentation is drawn from (marked as in d's key, by the
# titles): cells from the membrane and cytoplasm stains, nuclei from DAPI
outlines = {
    "fill_alpha": 0,
    "outline_alpha": 1,
    "outline_color": "white",
    "outline_width": 0.5,
    "method": "matplotlib",
}
CELL_STAINS, NUCLEUS_STAINS = [MEMBRANE, CYTOPLASM], [DAPI]
show(
    zoom.pl.render_images("morphology_focus", **stains(CELL_STAINS)).pl.render_shapes("cell_boundaries", **outlines),
    ax_cells,
    ZOOM,
)
show(
    zoom.pl.render_images("morphology_focus", **stains(NUCLEUS_STAINS)).pl.render_shapes(
        "nucleus_boundaries", **outlines
    ),
    ax_nuc,
    ZOOM,
)
zoom_lines(ax_stain, ZOOM, ax_cells, more=[ax_nuc])
bar(ax_nuc, 10, anchor=(1, -0.04 - 2.6 / S))  # on the key's second line, clear of d's key

# g: segmentation QC over the cells of the analysed piece; the transcript threshold for clustering marked
qc = cells.obs[(cells.obs["tissue_piece"] == "1").to_numpy()]
for ax, (column, label, bins) in zip(
    ax_qc,
    [
        ("transcript_counts", "Transcripts per cell", np.arange(0, 301, 10)),
        ("n_genes", "Genes per cell", np.arange(0, 121, 4)),
        ("cell_area", "Cell area (µm²)", np.arange(0, 301, 10)),
        ("nucleus_fraction", "Nucleus area / cell area", np.linspace(0, 1, 26)),
    ],
    strict=True,
):
    v = np.clip(qc[column].dropna().to_numpy(), bins[0], bins[-1])  # the last bin holds larger values
    if column == "transcript_counts":
        ax.hist(v[v < MIN_TRANSCRIPTS], bins, color="#d3d3d3")
        ax.hist(v[v >= MIN_TRANSCRIPTS], bins, color="#808080")
    else:
        ax.hist(v, bins, color="#808080")
    ax.set_xlim(bins[0], bins[-1])
    ax.set_xlabel(label, labelpad=1)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y / 1000:g}")
ax_qc[3].set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
ylabel(ax_qc[0], "Cells (thousands)", 1)  # one label for both rows, centered on them
p0, p2 = ax_qc[0].get_position(), ax_qc[2].get_position()
ax_qc[0].yaxis.label.set_y(((p0.y1 + p2.y0) / 2 - p0.y0) / p0.height)

# h: UMAP of the analysed cells (passing QC, on piece 1) by Leiden cluster, each labelled by its
# badge, outlined to stand out from its own cluster
kept = cells[cells.obs["analysed"].to_numpy()].copy()
sc.pl.embedding(kept, "umap", color="leiden", ax=ax_umap, show=False, legend_loc=None, title="", size=0.5)
ax_umap.collections[0].set_rasterized(True)
sf.embedding_axes(ax_umap)
umap = pd.DataFrame(kept.obsm["X_umap"], index=kept.obs_names).groupby(kept.obs["leiden"].to_numpy()).median()
for cl, (x, y) in umap.iterrows():
    mark, _ = sf.badge(ax_umap, x, y, cl_colors[cl], label=cl)
    mark.set_markeredgecolor("white")
    mark.set_markeredgewidth(LW)

# i: marker genes per cluster (dot plot), clusters grouped by the cell type they are annotated as;
# the genes of k in bold
markers = {
    "Epithelial": ["EPCAM", "KRT7"],
    "Fibroblasts": ["LTBP2", "PDGFRA"],
    "Smooth muscle": ["MYH11"],
    "Endothelial": ["VWF"],
    "T cells": ["CD3E", "TRAC"],
    "B cells": ["MS4A1"],
    "Plasma cells": ["MZB1"],
    "Macrophages": ["CD68", "MRC1"],
    "Ciliated": ["SNTN", "FOXJ1"],
}
dot_genes = [g for gs in markers.values() for g in gs]
annot = kept.obs.groupby("leiden", observed=True)["cell_type"].first()
order = sorted(annot.index, key=lambda cl: (list(ct_colors).index(annot[cl]), int(cl)))
X = pd.DataFrame(kept[:, dot_genes].X.toarray(), columns=dot_genes, index=kept.obs["leiden"].to_numpy())
mean = X.groupby(level=0).mean().loc[order]
frac = (X > 0).groupby(level=0).mean().loc[order]
scaled = (mean - mean.min()) / (mean.max() - mean.min())  # per gene
pitch = 2.2  # mm between rows and columns
n_r, n_c = len(order), len(dot_genes)
ax_dot = sf.add_axes_mm(fig, 111, R3 + 14, n_c * pitch, n_r * pitch)  # gene names above
smax = (0.9 * pitch / 25.4 * 72) ** 2  # pt², a dot for 100% of cells
yy, xx = np.meshgrid(np.arange(n_r), np.arange(n_c), indexing="ij")
dots = ax_dot.scatter(
    xx.ravel(),
    yy.ravel(),
    s=frac.to_numpy().ravel() * smax,
    c=scaled.to_numpy().ravel(),
    cmap="Reds",
    vmin=0,
    vmax=1,
    lw=0,
)
ax_dot.set_xlim(-0.5, n_c - 0.5)
ax_dot.set_ylim(n_r - 0.5, -0.5)
ax_dot.xaxis.tick_top()
ax_dot.set_xticks(range(n_c), dot_genes, rotation=90, fontstyle="italic")
for tick, g in zip(ax_dot.xaxis.get_major_ticks(), dot_genes, strict=True):
    tick.label2.set_fontweight("bold" if g in EXPR_GENES else "normal")
ax_dot.tick_params(length=0, pad=1)
ax_dot.set_yticks([])
for s in ax_dot.spines.values():
    s.set_visible(False)
for i, cl in enumerate(order):
    sf.badge(ax_dot, -1.1, i, cl_colors[cl], label=cl, diameter=2.1)
# the annotation: a color bar per cell type over its clusters, named on its right
for ct, rows in pd.Series(range(n_r), index=[annot[cl] for cl in order]).groupby(level=0, sort=False):
    ax_dot.add_patch(
        Rectangle(
            (n_c - 0.5 + 0.35, rows.min() - 0.45),
            0.5,
            rows.max() - rows.min() + 0.9,
            color=ct_colors[ct],
            clip_on=False,
            lw=0,
        )
    )
    ax_dot.text(n_c - 0.5 + 1.15, (rows.min() + rows.max()) / 2, ct, va="center_baseline", ha="left", clip_on=False)
cax = sf.add_axes_mm(fig, 169, R3 + 14, 1.2, 10)
sf.colorbar(dots, cax, label="Mean\nexpression")
size_ax = sf.add_axes_mm(fig, 169, R3 + 30, 6, 10)
size_ax.axis("off")
size_ax.scatter([0.2] * 3, [2, 1, 0], s=np.array([0.25, 0.5, 1]) * smax, color="black", lw=0, clip_on=False)
for y, t in zip([2, 1, 0], ["25", "50", "100"], strict=True):
    size_ax.text(0.9, y, t, va="center_baseline", ha="left")
size_ax.set_xlim(0, 1)
size_ax.set_ylim(-0.5, 2.5)
size_ax.set_title("Cells (%)", loc="left", fontsize=sf.SIZES["text"], pad=2)

# j: cell types in the region (cells failing QC grey), at 60% opacity over DAPI; k: per cell, the
# normalized expression of whichever of two genes of c dominates, each in its transcripts' color (light to full), on one
# scale; cells with neither only outlined. Colorbars and the scale bar of j-l in one key column
show(
    roi.pl.render_images(
        "morphology_focus", **stains([DAPI])
    ).pl.render_shapes(  # in its color from d, marked by j's title
        "cell_boundaries",
        color="cell_type",
        table_name="table",
        na_color="#d3d3d3",
        fill_alpha=0.6,
        outline_width=0.1,
        outline_color="white",
        outline_alpha=1,
        method="matplotlib",
    ),
    ax_types,
    ROI,
)
norm = Normalize(0, 3)
gene_cmaps = {
    g: LinearSegmentedColormap.from_list(g, [0.85 + 0.15 * np.array(to_rgb(gene_colors[g])), gene_colors[g]])
    for g in EXPR_GENES
}
render = roi.pl.render_shapes(
    "cell_boundaries", fill_alpha=0, outline_alpha=1, outline_color="#d3d3d3", outline_width=0.1, method="matplotlib"
)
for g in EXPR_GENES:
    render = render.pl.render_shapes(
        "cell_boundaries",
        color=f"{g}_dominant",
        table_name="table",
        cmap=gene_cmaps[g],
        norm=norm,
        na_color=None,
        method="matplotlib",
    )
show(render, ax_expr, ROI)
key_x = COL4[1] + IND + S4 + 3  # mm
for i, g in enumerate(EXPR_GENES):
    cax = sf.add_axes_mm(fig, key_x, R4 + 7.5 + i * 14, 1.2, 7)
    sf.colorbar(ScalarMappable(norm, gene_cmaps[g]), cax, label=None, ends=("0", "3"))
    cax.set_title(g, loc="left", fontsize=sf.SIZES["text"], fontstyle="italic", pad=sf.SIZES["text"] * 0.6 + 2)
bar(ax_expr, 50, anchor=(1 + 3 / S4, 0), loc="lower left")  # bottom of the key column; also j and l

# l: the CellCharter niches as polygons (the union of their cells' polygons) over the region's cells,
# which are colored as in j but faded: polygons filled at 45% opacity and outlined in their color.
# Right, per niche (rows, its badge and name): cell-type composition, the area and roundness of its
# polygons (averaged over the niche's area) and the median depth of its cells in the tissue
show(
    roi.pl.render_shapes(
        "cell_boundaries",
        color="cell_type",
        table_name="table",
        na_color="#d3d3d3",
        fill_alpha=0.3,
        method="matplotlib",
    ).pl.render_shapes(
        "niches",
        color="niche",
        palette=niche_colors,
        fill_alpha=0.45,
        outline_color="niche",
        outline_alpha=1,
        outline_width=0.9,
        method="matplotlib",
    ),
    ax_niche,
    ROI,
)
names = list(niche_colors)
rows = range(len(names))
comp = pd.crosstab(kept.obs["niche"], kept.obs["cell_type"], normalize="index").loc[names, list(ct_colors)] * 100
left = np.zeros(len(comp))
for ct in comp.columns:
    ax_prof["comp"].barh(rows, comp[ct], left=left, color=ct_colors[ct], height=0.75, lw=0)
    left += comp[ct].to_numpy()
geometry = pd.read_csv(DATA / "niche_geometry.csv", index_col=0)
geometry.index = geometry.index.astype(str)
geometry = geometry.loc[names].assign(area=lambda g: g["area"] / 1e6)  # mm²
for key, values, top, label in [
    ("area", geometry["area"], 0.4, "Area\n(mm²)"),
    ("roundness", geometry["roundness"], 0.3, "Round-\nness"),
    ("depth", geometry["depth"], 500, "Depth\n(µm)"),
    ("comp", None, 100, "Cell types\n(%)"),
]:
    ax = ax_prof[key]
    if values is not None:
        ax.barh(rows, values, color=[niche_colors[n] for n in names], height=0.75, lw=0)
    ax.set_xlim(0, top)
    ax.set_xticks([0, top], ["0", f"{top:g}"])
    lo, hi = ax.get_xticklabels()  # inwards, so neighbouring charts' labels stay apart
    lo.set_horizontalalignment("left")
    hi.set_horizontalalignment("right")
    ax.set_ylim(len(names) - 0.5, -0.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(label, labelpad=1)
row_label = ax_prof["comp"].get_yaxis_transform()  # x in axes fraction, y in rows
comp_left, comp_w = PROFILE["comp"]
for i, n in enumerate(names):
    sf.badge(
        ax_prof["comp"],
        (113.5 - comp_left) / comp_w,
        i,
        niche_colors[n],
        label=n,
        marker="D",
        diameter=2.6,
        transform=row_label,
    )
    ax_prof["comp"].text(
        (116 - comp_left) / comp_w, i, cells.uns["niche_names"][n], transform=row_label, va="center_baseline", ha="left"
    )
ax_prof["comp"].text(
    (108.8 - comp_left) / comp_w,
    (len(names) - 1) / 2,
    "Niche",
    rotation=90,
    transform=row_label,
    ha="left",
    va="center",
)

# letters and panel titles; only a panel's title shares its letter's line. e, f and j title the
# marks of their stains from d's key
fig.canvas.draw()
col_h = ax_umap.get_tightbbox().x0 / fig.dpi * 25.4  # h's leftmost text (UMAP2)
letters = {
    letter: sf.panel_letter(fig, letter, left, top, title=title, over=over)
    for letter, left, top, title, over in [
        (
            "a",
            1,
            1,
            "Human lung cancer (FFPE section): 377 genes profiled in situ by 10x Xenium (v1 chemistry), then H&E "
            "staining",
            ax_sec,
        ),
        ("b", col[0], R2, "H&E of the region", ax_he),
        ("c", col[1], R2, "Detected transcripts", ax_tx),
        ("d", col[2], R2, "Morphology stains", ax_stain),
        ("e", col[3], R2, None, None),
        ("f", col[4], R2, None, None),
        ("g", 1, R3, "Segmentation quality", ax_qc[:2]),
        ("h", col_h, R3, "Leiden clusters", ax_umap),
        ("i", 104, R3, "Marker genes and cluster annotation", ax_dot),
        ("j", COL4[0], R4, None, None),
        ("k", COL4[1], R4, "Expression per cell", ax_expr),
        ("l", COL4[2], R4, "CellCharter niches as polygons: cell types and geometry", [ax_niche, ax_prof["depth"]]),
    ]
}
titles = [
    (letters["e"], ax_cells, "Segmented cells", CELL_STAINS),
    (letters["f"], ax_nuc, "Segmented nuclei", NUCLEUS_STAINS),
    (letters["j"], ax_types, "Cell types over DAPI", [DAPI]),
]
anns = [
    fig.add_artist(Annotation(s, xy=(0.5, 0), xycoords=(ax, t), ha="center", va="bottom")) for t, ax, s, _ in titles
]
fig.canvas.draw()
for ann, (*_, marks) in zip(anns, titles, strict=True):
    bb = ann.get_window_extent()
    for k, m in enumerate(reversed(marks)):  # squares left of the title, as in d's key
        x, y = fig.transFigure.inverted().transform((bb.x0 - (1.6 + 1.8 * k) * sf.MM * fig.dpi, (bb.y0 + bb.y1) / 2))
        fig.add_artist(
            Line2D(
                [x],
                [y],
                marker="s",
                ls="",
                color=stain_colors[m],
                markeredgecolor="none",
                markersize=3.5,
                transform=fig.transFigure,
            )
        )
sf.save(fig, "figures/fig2_spatial", legend=Path(__file__).with_name("fig2_spatial_legend.md"))
plt.close(fig)
