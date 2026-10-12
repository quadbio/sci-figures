"""Example figure on synthetic data: mm layout, keys, badges, scanpy embeddings, an algorithm
schematic with equations, export.

Run with Arial and TeX installed (../references/setup.md):
    python skills/sci-figures/examples/fig1_moscot.py
Writes figures/fig1_moscot.pdf, figures/fig1_moscot_legend.md and figures/.preview/fig1_moscot.png.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import yaml
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, PathPatch
from matplotlib.path import Path as Curve

import scifig as sf

sf.apply_style()  # after importing scanpy; never call sc.set_figure_params
rng = np.random.default_rng(0)

# --- data (synthetic): progenitors and three terminal cell types ---
n = 3000
cell_type = rng.choice(["Progenitor", "Alpha", "Beta", "Delta"], n, p=[0.4, 0.2, 0.25, 0.15])
centers = {"Progenitor": (0, 0), "Alpha": (4, 3), "Beta": (5, -2), "Delta": (-1, 4)}
xy = np.array([centers[c] for c in cell_type]) + rng.normal(0, 0.9, (n, 2))
adata = ad.AnnData(
    np.zeros((n, 1)), obs=pd.DataFrame({"cell_type": pd.Categorical(cell_type)}, index=map(str, range(n)))
)
adata.obsm["X_sim"] = xy  # simulated 2D coordinates, not a computed UMAP
# Beta fate: high in Beta cells, low in Alpha and Delta, graded in progenitors towards Beta
adata.obs["beta_fate"] = np.select(
    [cell_type == "Beta", cell_type == "Progenitor"],
    [rng.beta(20, 1, n), 1 / (1 + np.exp(-1.5 * (xy[:, 0] - xy[:, 1])))],
    rng.beta(1, 20, n),
)

# a toy transport problem between four earlier cells x_i and three later cells y_j, each with a
# generic cell type (A-D, not those of the data) and a mass (a, b); cost, squared distance; solved
# by Sinkhorn's algorithm, P = diag(u) K diag(v) with marginals a and b
ot_x = np.array([(-0.3, 0.7), (0.9, -0.5), (3.0, 2.0), (-0.5, 2.9)])
ot_xt = ["A", "A", "B", "D"]
ot_y = np.array([(4.3, 3.3), (5.0, -1.7), (-1.2, 4.3)])
ot_yt = ["B", "C", "D"]
ot_a = np.array([0.35, 0.3, 0.2, 0.15])
ot_b = np.array([0.3, 0.45, 0.25])
ot_C = ((ot_x[:, None] - ot_y[None]) ** 2).sum(-1)
eps = 2.0
K = np.exp(-ot_C / eps)
u, v = np.ones(len(ot_a)), np.ones(len(ot_b))
for _ in range(5000):
    u = ot_a / (K @ v)
    v = ot_b / (K.T @ u)
P = u[:, None] * K * v[None, :]
assert np.allclose(P.sum(1), ot_a) and np.allclose(P.sum(0), ot_b)

stages = ["Pre-gastrulation", "Gastrulation", "Organogenesis"]
methods = ["moscot", "WOT", "TOME"]
n_rep = 10  # simulated replicates per method and stage
acc_mean = {"moscot": [0.85, 0.88, 0.8], "WOT": [0.7, 0.62, 0.66], "TOME": [0.75, 0.72, 0.7]}
acc_reps = {m: rng.normal(acc_mean[m], 0.03, (n_rep, len(stages))) for m in methods}
tissues = ["Heart field", "Endoderm"]
corr = {(t, m): rng.normal(mu, 0.1, 30) for t in tissues for m, mu in zip(methods, (0.5, 0.35, 0.3), strict=True)}
n_cells = np.array([1e3, 1e4, 1e5, 1e6])
runtime = {m: 0.01 * n_cells**e for m, e in zip(methods, (0.8, 1.0, 0.9), strict=True)}  # minutes

# --- colors: adata.uns for categorical obs, the repo conventions file for everything else ---
conventions = yaml.safe_load((Path(__file__).parent / "resources/figure_conventions.yaml").read_text())["colors"]
m_colors, t_colors = conventions["methods"], conventions["toy_cell_types"]


def key(ax, colors, title=None, loc="upper left", anchor=(1.03, 1), markers=None, **kw):
    """Categorical key with its ``loc`` corner at ``anchor`` (axes fraction), by default right of
    ``ax`` and top-aligned with it. All keys share one marker size; the handle is as wide as the
    marker, so markers sit flush with the key's edge. ``markers`` maps entries to shapes (circles by
    default; a square as large in area as the circle). Added as an artist, so an axes holds several."""
    size, markers = 3.5, markers or {}  # pt
    scale = {k: np.sqrt(np.pi) / 2 if markers.get(k) == "s" else 1 for k in colors}
    handles = [
        Line2D([], [], marker=markers.get(k, "o"), ls="", color=c, markeredgecolor="none", markersize=size * scale[k])
        for k, c in colors.items()
    ]
    leg = Legend(
        ax,
        handles,
        list(colors),
        title=title,
        loc=loc,
        bbox_to_anchor=anchor,
        borderaxespad=0,
        borderpad=0,
        alignment="left",
        handlelength=size / sf.SIZES["text"],
        **kw,
    )
    ax.add_artist(leg)
    return leg


def ylabel(ax, text, left):
    """Y label whose left edge sits at ``left`` mm, flush with the panel letter."""
    p, fw = ax.get_position(), fig.get_figwidth() / sf.MM
    ax.set_ylabel(text, va="top")  # rotated: "top" is the label's left edge
    ax.yaxis.set_label_coords((left / fw - p.x0) / p.width, 0.5)


# --- layout (mm): a and b in the first row; c, d and e in the second ---
R2 = 52  # top of row 2
fig = sf.new_figure(183, R2 + 41)
ax_a = sf.add_axes_mm(fig, 1, 5, 112, 44)
ax_b = sf.add_axes_mm(fig, 118, 6, 28, 28)
ax_b2 = sf.add_axes_mm(fig, 151.5, 6, 28, 28)
ax_c = sf.add_axes_mm(fig, 11, R2 + 7.5, 43, 25)
ax_d = sf.add_axes_mm(fig, 67.5, R2 + 7.5, 47.5, 25)
ax_e = sf.add_axes_mm(fig, 133.5, R2 + 7.5, 37, 25)
col_d = 58.5  # letter column of d

# b: one embedding colored by cell type and by Beta fate probability, so one axis indicator; keys
# below their plots, their titles on one line. scanpy stores the category colors in adata.uns
sc.pl.embedding(adata, "sim", color="cell_type", ax=ax_b, show=False, legend_loc=None, title="", size=7)
ct_colors = dict(zip(adata.obs["cell_type"].cat.categories, adata.uns["cell_type_colors"], strict=True))
sf.embedding_axes(ax_b, basis="Dim")
leg = key(ax_b, ct_colors, title="Cell type", anchor=(0, -5.5 / 28), ncols=2, columnspacing=1.0)
sc.pl.embedding(
    adata, "sim", color="beta_fate", ax=ax_b2, show=False, colorbar_loc=None, title="", size=7, vmin=0, vmax=1
)  # fixed scale: the colorbar ends are exactly 0 and 1
ax_b2.margins(0.02)  # the view of the first plot
ax_b2.axis("off")
for ax in (ax_b, ax_b2):
    ax.collections[0].set_rasterized(True)
cax = sf.add_axes_mm(fig, 151.5, 44, 24, 1.5)
sf.colorbar(ax_b2.collections[0], cax, label="Beta fate probability", ends=("0", "1"), orientation="horizontal")
fig.canvas.draw()
dy = leg.get_title().get_window_extent().y0 - cax.title.get_window_extent().y0  # titles on one line
cax.set_position(cax.get_position().translated(0, dy / fig.bbox.height))

# a: optimal transport. The cells with their masses (the marginals, labelled in the drawing) and
# the cost matrix computed from their positions define the problem, set under both with a brace;
# its solution, the coupling, follows the cost matrix on the same line. Each cell keeps one mark
# throughout: earlier cells circles, later cells squares, in their type's color, area
# proportional to mass; the keys to shape and color sit under the coupling. A cartoon, so its cell
# types are generic and colored apart from those of the data. mm, y upwards.
H, W = 44, 112
ax_a.set_xlim(0, W)
ax_a.set_ylim(0, H)
ax_a.set_aspect("equal")
ax_a.axis("off")
YH, YT = 42.5, 27.5  # headers; centre of the matrices
LIMS = (-2.2, 6.2), (-2.8, 5.6)  # the cells' view of the embedding
SIDE, cell = 22, 4.5  # mm: the cells' drawing, a matrix cell


def diameter(m):
    """Mark diameter (mm) of a mass ``m``: area proportional to mass."""
    return 4.4 * np.sqrt(m / 0.45)


def mark(ax, x, y, side, k):
    """Mark of earlier cell ``k`` (side "x") or later cell ``k`` (side "y") at ``x, y`` in ``ax``."""
    color, m, shape = (t_colors[ot_xt[k]], ot_a[k], "o") if side == "x" else (t_colors[ot_yt[k]], ot_b[k], "s")
    side_mm = diameter(m) * (np.sqrt(np.pi) / 2 if shape == "s" else 1)  # a square as large as the circle
    sf.badge(ax, x, y, color, diameter=side_mm, marker=shape)


def arrow(x0, x1):
    """Process arrow from ``x0`` to ``x1`` on the drawings' centre line."""
    ax_a.add_patch(
        FancyArrowPatch(
            (x0, YT),
            (x1, YT),
            arrowstyle="-|>,head_length=3,head_width=1.5",
            mutation_scale=1,
            color="black",
            lw=sf.LINEWIDTHS["axis"],
            shrinkA=0,
            shrinkB=0,
        )
    )


def brace(x0, x1, y, h=2):
    """Curly brace from ``x0`` to ``x1`` hanging from ``y``, its tip ``h`` below."""
    xm, r, ym = (x0 + x1) / 2, min(1.5, (x1 - x0) / 4), y - h / 2
    codes = [Curve.MOVETO] + [Curve.CURVE4] * 3 + [Curve.LINETO] + [Curve.CURVE4] * 3
    for a, s in ((x0, 1), (x1, -1)):  # each half, from its end to the tip
        verts = [(a, y), (a, ym), (a, ym), (a + s * r, ym), (xm - s * r, ym), (xm, ym), (xm, ym), (xm, y - h)]
        ax_a.add_patch(PathPatch(Curve(verts, codes), fill=False, lw=sf.LINEWIDTHS["axis"]))


def text(ax, x, y, s, **kw):
    """Text typeset by LaTeX like the equations."""
    return ax.text(x, y, s, ha=kw.pop("ha", "center"), va=kw.pop("va", "center"), usetex=True, **kw)


def matrix(x0, values, header, **kw):
    """Heatmap of ``values`` (earlier cells in rows, later in columns) whose grid starts at ``x0``,
    headed by the cells' marks, with its colorbar right of it (``kw`` to ``sf.colorbar``)."""
    gx = x0 + cell * np.arange(len(ot_b) + 1)
    gy = YT + 2 * cell - cell * np.arange(len(ot_a) + 1)
    for i in range(len(ot_a)):
        mark(ax_a, x0 - 3.2, gy[i] - cell / 2, "x", i)
    for j in range(len(ot_b)):
        mark(ax_a, (gx[j] + gx[j + 1]) / 2, gy[0] + 2.4, "y", j)
    mesh = ax_a.pcolormesh(gx, gy, values, cmap=kw.pop("cmap"), vmin=kw.pop("vmin", None), vmax=kw.pop("vmax", None))
    sf.colorbar(mesh, sf.add_axes_mm(fig, 1 + gx[-1] + 1.5, 5 + H - gy[0], 1.2, gy[0] - gy[-1]), **kw)
    text(ax_a, gx.mean(), YH, header)
    return gx, gy


# the cells, with axis labels, their positions and masses labelled at one cell of each kind
ax_cells = sf.add_axes_mm(fig, 1 + 3.3, 5 + H - (YT - 2 * cell + SIDE), SIDE, SIDE)  # bottom on the matrices'
for side, pts in (("x", ot_x), ("y", ot_y)):
    for k, (x, y) in enumerate(pts):
        mark(ax_cells, x, y, side, k)
sf.embedding_axes(ax_cells, basis="Dim", arrow_mm=4)
ax_cells.set_xlim(*LIMS[0])
ax_cells.set_ylim(*LIMS[1])
text(ax_cells, ot_x[1, 0], ot_x[1, 1] - 1.35, r"$x_i, a_i$")
text(ax_cells, ot_y[0, 0], ot_y[0, 1] + 1.3, r"$y_j, b_j$")
text(ax_a, 3.3 + SIDE / 2, YH, "Cells")
arrow(27, 31)

# the cost matrix, then the coupling on the same line
gx, gy = matrix(37.5, ot_C, r"Cost $C_{ij} = \lVert x_i - y_j \rVert^2$", cmap="viridis")
arrow(61, 65)
gxp, _ = matrix(71.5, P, r"Coupling $P^{\ast}_{ij}$", cmap="Greys", vmin=0, vmax=0.3, ends=("0", "0.3"))

# the problem, defined by the cells and the costs: under both, joined to them by a brace; its
# minimizer P* is the coupling shown. After a comma, its feasible set on the same line, the two on
# one level. Terms labelled; \textstyle keeps labels at 7 pt, \vphantom aligns the braces,
# \makebox[0pt] keeps a label from widening its term
cost = r"\underbrace{\sum\nolimits_{i,j} C_{ij} P_{ij}}_{\textstyle\text{transport cost}}"
entropy = r"\underbrace{\varepsilon H(P)\vphantom{\sum\nolimits_{i,j}}}_{\textstyle\text{entropy}}"
feasible = r"\underbrace{U(a,b)\vphantom{\sum\nolimits_{i,j}}}_{\textstyle\makebox[0pt]{feasible set}}"
x0, x1 = 3.3, gx[-1] + 8
brace(x0, x1, gy[-1] - 4)
problem = text(
    ax_a,
    (x0 + x1) / 2,
    8.5,
    rf"$\displaystyle P^{{\ast}} = \operatorname*{{arg\,min}}_{{P \in U(a,b)}} {cost} - {entropy},$",
    va="baseline",
)
fig.canvas.draw()
right = ax_a.transData.inverted().transform(problem.get_window_extent().corners()[-1])[0]
marginals = r"P\textbf{1} = a,\ P^{\top}\textbf{1} = b\vphantom{\sum\nolimits_{i,j}}"
constraints = rf"\{{P \geq 0 : \underbrace{{{marginals}}}_{{\textstyle\makebox[0pt]{{marginal constraints}}}}\}}"
text(ax_a, right + 5.5, 8.5, rf"$\displaystyle {feasible} = {constraints}$", ha="left", va="baseline")

# keys to the marks in a column right of the coupling, aligned on their left edge and with the
# matrices' marks at the top
kx = gxp[-1] + 10
key(
    ax_a,
    {"Earlier": "black", "Later": "black"},
    title="Time point",
    markers={"Later": "s"},
    anchor=(kx / W, (gy[0] + 4.6) / H),
)
key(ax_a, t_colors, title="Cell type", ncols=2, columnspacing=0.8, anchor=(kx / W, (gy[0] - 7.5) / H))

# c: one point per replicate with median and interquartile range; the method key is drawn
# here, with the first panel that uses it, in one row above the axes to free the column to its right
for i, m in enumerate(methods):
    for j, reps in enumerate(acc_reps[m].T):
        xi = j * 4 + i  # stages a slot apart, as the tissues in d
        ax_c.scatter(xi + rng.uniform(-0.18, 0.18, n_rep), reps, s=4, color=m_colors[m], lw=0)
        q1, med, q3 = np.percentile(reps, [25, 50, 75])
        ax_c.plot([xi, xi], [q1, q3], color="black", lw=sf.LINEWIDTHS["axis"])
        ax_c.plot([xi - 0.3, xi + 0.3], [med, med], color="black", lw=sf.LINEWIDTHS["axis"])
ax_c.set_xticks([1, 5, 9], ["Pre-\ngastrulation", "Gastrulation", "Organo-\ngenesis"])
ylabel(ax_c, "Accuracy", 1)
ax_c.set_ylim(0.5, 1)
ax_c.set_yticks([0.5, 0.75, 1])
key(ax_c, {m: m_colors[m] for m in methods}, loc="lower left", anchor=(0, 1.04), ncols=3, columnspacing=1.0)

# d: box plots for both tissues on one shared y axis; methods colored as in c
xpos, data, cols = [], [], []
for j, t in enumerate(tissues):
    for i, m in enumerate(methods):
        xpos.append(j * 4 + i)
        data.append(corr[(t, m)])
        cols.append(m_colors[m])
bp = ax_d.boxplot(data, positions=xpos, widths=0.7, patch_artist=True, showfliers=False)
for patch, c in zip(bp["boxes"], cols, strict=True):
    patch.set_facecolor(c)
for p, d in zip(xpos, data, strict=True):
    ax_d.scatter(p + rng.uniform(-0.18, 0.18, len(d)), d, s=4, c="black", lw=0, zorder=3)  # above the boxes
ax_d.set_xticks([1, 5], tissues)
ylabel(ax_d, "Spearman correlation", col_d)
ax_d.set_ylim(-0.1, 0.8)
ax_d.set_yticks([0, 0.4, 0.8])

# e: runtime on log-log axes; lines labelled directly, colored as in c. Plain tick labels:
# mathtext would shrink the superscripts of 10³ below 5 pt
k_cells = n_cells / 1e3
for m in methods:
    ax_e.plot(k_cells, runtime[m], "-o", color=m_colors[m], markersize=2.5)
    ax_e.annotate(m, (k_cells[-1], runtime[m][-1]), xytext=(4, 0), textcoords="offset points", va="center")
ax_e.set_xscale("log")
ax_e.set_yscale("log")
ax_e.set_xticks([1, 10, 100, 1000])
ax_e.set_yticks([10, 100, 1000, 10000])
ax_e.minorticks_off()
for axis in (ax_e.xaxis, ax_e.yaxis):
    axis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax_e.set_xlabel("Cells (thousands)")
ylabel(ax_e, "Runtime (min)", 121)

fig.canvas.draw()
col_b = ax_b.get_tightbbox().x0 / fig.dpi * 25.4  # b's leftmost text (Dim2)

# letters; titles for all of a row or none, centered over their plots
for letter, left, top, title, over in [
    ("a", 1, 1, None, None),
    ("b", col_b, 1, None, None),
    ("c", 1, R2, "Cell-type transitions", ax_c),
    ("d", col_d, R2, "Fate probability and driver genes", ax_d),
    ("e", 121, R2, "Scaling", ax_e),
]:
    sf.panel_letter(fig, letter, left, top, title=title, over=over)
sf.save(fig, "figures/fig1_moscot", legend=Path(__file__).with_name("fig1_moscot_legend.md"))
plt.close(fig)
