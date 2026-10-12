"""Data for the spatial demo figure (fig2_spatial.py): segmentation QC, normalization,
clustering, cluster annotation and cellular niches of a 10x Xenium human lung cancer section.

    python skills/sci-figures/examples/fig2_spatial_data.py
Reads the SpatialData conversion of the public dataset (fig2_spatial_outline.md, Source) from
XENIUM_LUNG (default data/xenium_lung/data.zarr) and writes to SCIFIG_DEMO_DATA (default
data/fig2_spatial):
- cells.h5ad: all cells with raw counts, QC metrics, tissue piece and log-normalized expression;
  UMAP, Leiden clusters, cell types and niches for the analysed cells (passing QC, on the largest
  piece)
- tissue.zarr: the tissue pieces contoured from the H&E by sopa, numbered by area
- niches.zarr: the niches as polygons, the union of their cells' polygons closed by 2 µm
- niche_geometry.csv: per niche, the number of its polygons, their area (µm²) and roundness averaged
  over the niche's area, and the median depth of its cells in the tissue (µm)
"""

import os
from pathlib import Path

import cellcharter as cc
import geopandas as gpd
import lightning
import numpy as np
import pandas as pd
import scanpy as sc
import shapely
import sopa
import spatialdata as sd
import squidpy as sq
import torch
from spatialdata.models import ShapesModel
from spatialdata.transformations import get_transformation

ZARR = Path(os.environ.get("XENIUM_LUNG", "data/xenium_lung/data.zarr"))
OUT = Path(os.environ.get("SCIFIG_DEMO_DATA", "data/fig2_spatial"))
MIN_TRANSCRIPTS = 10  # per cell, to keep a cell
LEIDEN_RESOLUTION = 1.0
N_NICHES = 6  # a demo choice; cc.tl.ClusterAutoK picks the number by stability

# cell type of each Leiden cluster, from its top-ranked genes (printed below). Clusters 5 and 9 are
# both macrophages, 9 also with epithelial transcripts (EPCAM in 61% of its cells)
ANNOTATION = {
    "0": "T cells",
    "1": "B cells",
    "2": "Plasma cells",
    "3": "Endothelial",
    "4": "Fibroblasts",
    "5": "Macrophages",
    "6": "Epithelial",
    "7": "Epithelial",
    "8": "Epithelial",
    "9": "Macrophages",
    "10": "Epithelial",
    "11": "Epithelial",
    "12": "Ciliated",
    "13": "Smooth muscle",
}
# cell type colors, apart from the Leiden clusters' scanpy defaults
CELL_TYPE_COLORS = {
    "Epithelial": "#d95f02",
    "Fibroblasts": "#1b9e77",
    "Smooth muscle": "#66a61e",
    "Endothelial": "#e7298a",
    "T cells": "#7570b3",
    "B cells": "#1f78b4",
    "Plasma cells": "#a6cee3",
    "Macrophages": "#e6ab02",
    "Ciliated": "#a6761d",
}
# niche names, from their cell-type composition and geometry (printed below): the tumour niches
# differ by tumour cell state (Leiden clusters 8 and 11 in the large, deep niche 1, 7 and 6 in
# niche 2, all four in the fragments of niche 3) and by macrophages (niche 4)
NICHE_NAMES = {
    "1": "Tumour core",
    "2": "Tumour",
    "3": "Tumour, mixed",
    "4": "Tumour, myeloid",
    "5": "Stroma",
    "6": "Immune",
}
# niche colors (Tol's muted set): warm for the epithelial niches, cool for the others
NICHE_COLORS = ["#882255", "#cc6677", "#ddcc77", "#88ccee", "#999933", "#332288"]

adata = sd.read_zarr(ZARR, selection=("tables",)).tables["table"]
adata.obs_names = adata.obs["cell_id"].astype(str).to_numpy()
adata.layers["counts"] = adata.X.copy()
shapes = sd.read_zarr(ZARR, selection=("shapes",))
to_global = get_transformation(shapes["cell_circles"], get_all=True)  # µm (the centroids' unit) to pixels
um = 1 / to_global["global"].scale[0]  # µm per pixel

# tissue pieces, contoured from the H&E by sopa on an in-memory copy (nothing is written to ZARR):
# unexpanded, holes filled, at a resolution that separates the tumour from the airway wall; pieces
# outside the Xenium image (fewer than 100 cells) are dropped
he = sd.SpatialData(images={"he_image": sd.read_zarr(ZARR, selection=("images",))["he_image"]})
sopa.segmentation.tissue(
    he,
    image_key="he_image",
    mode="saturation",
    level=3,
    expand_radius_ratio=0,
    allow_holes=False,
    drop_threshold=0.002,
    key_added="tissue",
)
tissue = sd.transform(he["tissue"], to_coordinate_system="global").reset_index(drop=True)  # pixels
xy = adata.obsm["spatial"] / um
hit = gpd.sjoin(
    gpd.GeoDataFrame(geometry=gpd.points_from_xy(xy[:, 0], xy[:, 1])), tissue[["geometry"]], predicate="within"
)
n_cells = hit["index_right"].value_counts()
tissue = tissue[tissue.index.isin(n_cells.index[n_cells >= 100])]
# numbered by area; the largest, the tumour, is the one analysed
pieces = [str(i + 1) for i in range(len(tissue))]
tissue["piece"] = pd.Categorical(
    tissue.area.rank(ascending=False, method="first").astype(int).astype(str), categories=pieces
)
OUT.mkdir(parents=True, exist_ok=True)
sd.SpatialData(shapes={"tissue": ShapesModel.parse(tissue)}).write(OUT / "tissue.zarr", overwrite=True)
hit = hit[hit["index_right"].isin(tissue.index)]
piece = pd.Series(tissue.loc[hit["index_right"], "piece"].to_numpy(), index=hit.index)  # by cell position
adata.obs["tissue_piece"] = pd.Categorical(piece.reindex(range(adata.n_obs)).to_numpy(), categories=pieces)

# segmentation QC; areas in µm², from the vendor's segmentation
adata.obs["n_genes"] = np.asarray((adata.X > 0).sum(1)).ravel()
adata.obs["nucleus_fraction"] = adata.obs["nucleus_area"] / adata.obs["cell_area"]
adata.obs["qc_pass"] = adata.obs["transcript_counts"] >= MIN_TRANSCRIPTS
# analysed: the cells passing QC on the largest piece
on_piece = (adata.obs["tissue_piece"] == "1").to_numpy()
adata.obs["analysed"] = adata.obs["qc_pass"].to_numpy() & on_piece
print(
    f"{on_piece.sum()} of {adata.n_obs} cells on piece 1, {(on_piece & ~adata.obs['qc_pass']).sum()} of them below "
    f"{MIN_TRANSCRIPTS} transcripts"
)

# per-cell normalization, for all cells (the figure shows expression in every segmented cell)
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)

# clustering of the analysed cells; a targeted panel, so all genes
cells = adata[adata.obs["analysed"]].copy()
sc.pp.pca(cells, n_comps=30, random_state=0)
sc.pp.neighbors(cells, random_state=0)
sc.tl.umap(cells, random_state=0)
sc.tl.leiden(cells, resolution=LEIDEN_RESOLUTION, flavor="igraph", n_iterations=2, random_state=0)
sc.tl.rank_genes_groups(cells, "leiden", method="wilcoxon")
top = pd.DataFrame(cells.uns["rank_genes_groups"]["names"]).head(8).T
top.insert(0, "n", cells.obs["leiden"].value_counts().reindex(top.index))
with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(top)

cells.obs["cell_type"] = pd.Categorical(cells.obs["leiden"].map(ANNOTATION), categories=list(CELL_TYPE_COLORS))
cells.uns["cell_type_colors"] = list(CELL_TYPE_COLORS.values())
cells.uns["leiden_colors"] = sc.pl.palettes.default_20[: len(cells.obs["leiden"].cat.categories)]

# cellular niches (CellCharter): each cell's expression (the 30 principal components) concatenated
# with its means over 3 layers of spatial neighbours (Delaunay graph without its longest 1% of
# links), clustered by a Gaussian mixture; numbered from epithelial to immune
sq.gr.spatial_neighbors(cells, coord_type="generic", delaunay=True, spatial_key="spatial")
cc.gr.remove_long_links(cells)
cc.gr.aggregate_neighbors(cells, n_layers=3, use_rep="X_pca", out_key="X_cellcharter")
# random_state alone leaves the Gaussian mixture irreproducible (two fits agree at ARI 0.70); seeded
# generators, one thread and deterministic kernels make it exact, also across runs
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
lightning.seed_everything(0, workers=True)
model = cc.tl.Cluster(n_clusters=N_NICHES, random_state=0)
model.fit(cells, use_rep="X_cellcharter")
niche = pd.Series(np.asarray(model.predict(cells, use_rep="X_cellcharter")), index=cells.obs_names)
composition = pd.crosstab(niche, cells.obs["cell_type"], normalize="index")
order = (composition["Epithelial"] - composition["T cells"]).sort_values(ascending=False).index
names = [str(i + 1) for i in range(N_NICHES)]
cells.obs["niche"] = pd.Categorical(niche.map(dict(zip(order, names, strict=False))), categories=names)
cells.uns["niche_colors"] = NICHE_COLORS
with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(pd.crosstab(cells.obs["niche"], cells.obs["cell_type"], normalize="index").round(2))

# the niches as polygons: the union of their cells' segmentation polygons (µm), closed by 2 µm to
# bridge the gaps between neighbouring cells, so each cell lies in its own niche. sopa's
# vectorize_niches joins centroids by Delaunay triangles: its outlines cut through boundary cells
# and skip strips one or two cells wide, leaving about half of these fine-grained niches' cells
# outside a polygon of their own niche. Growing each cell before the union, rather than the union
# itself, gives the same areas (within 0.04%) in a third of the time
cell_polygons = shapely.make_valid(shapes["cell_boundaries"].loc[cells.obs["cell_id"].astype(str)].geometry.values)
union = (
    gpd.GeoDataFrame({"niche": cells.obs["niche"].astype(str).to_numpy()}, geometry=shapely.buffer(cell_polygons, 2))
    .dissolve("niche")
    .geometry.buffer(-2)
)
centroids = shapely.points(cells.obsm["spatial"])
own = np.zeros(cells.n_obs, bool)
for n, polygon in union.items():
    shapely.prepare(polygon)
    in_niche = (cells.obs["niche"] == n).to_numpy()
    own[in_niche] = shapely.contains(polygon, centroids[in_niche])
print(f"cells inside a polygon of their own niche: {own.mean():.4f}")
niches = gpd.GeoDataFrame({"niche": pd.Categorical(union.index, categories=names)}, geometry=union.to_numpy())
niches = niches.explode(index_parts=False).reset_index(drop=True)
sd.SpatialData(shapes={"niches": ShapesModel.parse(niches, transformations=to_global)}).write(
    OUT / "niches.zarr", overwrite=True
)
# their geometry: number of polygons, and their area and roundness (4 pi area / perimeter²), each
# averaged over the niche's area, so the large polygons most cells lie in count most
area, roundness = niches.area, 4 * np.pi * niches.area / niches.length**2
by_niche = niches.assign(area=area, area_x_round=area * roundness, area2=area**2).groupby("niche", observed=True)
geometry = pd.DataFrame(
    {
        "n_polygons": by_niche.size(),
        "area": by_niche["area2"].sum() / by_niche["area"].sum(),
        "roundness": by_niche["area_x_round"].sum() / by_niche["area"].sum(),
    }
)

# back onto all cells: the others keep their counts and expression, without cluster or niche
adata.obsm["X_umap"] = np.full((adata.n_obs, 2), np.nan)
adata.obsm["X_umap"][adata.obs["analysed"].to_numpy()] = cells.obsm["X_umap"]
for key in ("leiden", "cell_type", "niche"):
    adata.obs[key] = cells.obs[key].reindex(adata.obs_names)
    adata.uns[f"{key}_colors"] = cells.uns[f"{key}_colors"]
adata.uns["rank_genes_groups"] = cells.uns["rank_genes_groups"]
adata.uns["niche_names"] = NICHE_NAMES
adata.write_h5ad(OUT / "cells.h5ad")

# tissue depth: each cell's distance to the outline of its piece (µm), median per niche
outline = tissue.loc[tissue["piece"] == "1"].geometry.iloc[0].boundary
depth = shapely.distance(shapely.points(cells.obsm["spatial"] / um), outline) * um
geometry["depth"] = pd.Series(depth, index=cells.obs_names).groupby(cells.obs["niche"].to_numpy()).median()
print(geometry.round(3))
geometry.to_csv(OUT / "niche_geometry.csv")
print("wrote", OUT)
