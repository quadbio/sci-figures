"""Global matplotlib style for Nature-style research figures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib as mpl
from cycler import cycler
from matplotlib import font_manager

FONT = "Arial"

# Font sizes in pt (Nature): all text 7 pt, never below 5 pt; panel letters 8 pt bold.
SIZES = {"text": 7, "min": 5, "panel": 8}

# Line widths in pt: minor ticks and patch edges; axes, ticks, error bars and box plots; data lines.
LINEWIDTHS = {"thin": 0.25, "axis": 0.5, "data": 1.0}

# Rasterized parts: 1200 dpi stays sharp at 4x enlargement in Illustrator.
RASTER_DPI = 1200

# scanpy's default categorical palette (scanpy.plotting.palettes.default_20, BSD-3-Clause),
# used as the color cycle so plain matplotlib plots match scanpy's category colors.
DEFAULT_20 = [
    "#1f77b4",
    "#ff7f0e",
    "#279e68",
    "#d62728",
    "#aa40fc",
    "#8c564b",
    "#e377c2",
    "#b5bd61",
    "#17becf",
    "#aec7e8",
    "#ffbb78",
    "#98df8a",
    "#ff9896",
    "#c5b0d5",
    "#c49c94",
    "#f7b6d2",
    "#dbdb8d",
    "#9edae5",
    "#ad494a",
    "#8c6d31",
]


def _font_dirs() -> list[Path]:
    """Directories that may contain Arial, most specific first."""
    dirs = []
    for var in ("SCIFIG_FONT_DIR", "CONDA_PREFIX", "PIXI_ENVIRONMENT_PREFIX"):
        val = os.environ.get(var)
        if val:
            p = Path(val)
            dirs += [p, p / "fonts"]
    dirs += [Path(sys.prefix) / "fonts", Path.home() / ".local/share/fonts", Path.home() / ".fonts"]
    return [d for d in dirs if d.is_dir()]


def register_fonts() -> bool:
    """Register Arial from the active environment (e.g. conda-forge ``mscorefonts``).

    Returns True if Arial is available afterwards.
    """
    known = {Path(f.fname).resolve() for f in font_manager.fontManager.ttflist}
    for d in _font_dirs():
        for f in d.glob("[Aa]rial*.ttf"):
            if f.resolve() not in known:
                font_manager.fontManager.addfont(str(f))
    return any(f.name == FONT for f in font_manager.fontManager.ttflist)


def apply_style(strict: bool = True) -> None:
    """Apply the figure style. Call once after importing scanpy and before plotting.

    Parameters
    ----------
    strict
        Raise if Arial is not available. Never set to False for figures that leave your machine.
    """
    if not register_fonts():
        msg = (
            f"Font '{FONT}' not found. Run `python -m scifig.fonts` once (installs into "
            "~/.local/share/fonts), or `pixi add mscorefonts` in a pixi environment."
        )
        if strict:
            raise RuntimeError(msg)
        print(f"WARNING: {msg}", file=sys.stderr)

    n = SIZES["text"]
    lw = LINEWIDTHS
    mpl.rcParams.update(
        {
            # fonts and editable text
            "font.family": "sans-serif",
            "font.sans-serif": [FONT, "Helvetica", "DejaVu Sans"],
            "font.size": n,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "mathtext.fontset": "custom",
            "mathtext.rm": FONT,
            "mathtext.it": f"{FONT}:italic",
            "mathtext.bf": f"{FONT}:bold",
            "mathtext.sf": FONT,
            "mathtext.cal": FONT,  # default 'cursive' is missing on Linux servers
            "mathtext.default": "regular",
            # equations (usetex=True on their text only): Helvetica (matches Arial), sans-serif math
            "text.latex.preamble": r"\usepackage{amsmath}\usepackage[T1]{fontenc}\usepackage{newtxsf}"
            r"\DeclareSymbolFont{operators}{T1}{phv}{m}{n}\DeclareMathAlphabet{\mathrm}{T1}{phv}{m}{n}"
            # math comma and period from Helvetica: recent newtx virtual fonts break matplotlib's dvi reader
            r"\DeclareMathSymbol{,}{\mathpunct}{operators}{`,}\DeclareMathSymbol{.}{\mathord}{operators}{`.}",
            # sizes
            "axes.titlesize": n,
            "axes.titleweight": "normal",
            "axes.titlepad": 3,
            "axes.labelsize": n,
            "axes.labelpad": 2,
            "xtick.labelsize": n,
            "ytick.labelsize": n,
            "legend.fontsize": n,
            "legend.title_fontsize": n,
            "figure.titlesize": n,
            # axes
            "axes.linewidth": lw["axis"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "axes.facecolor": "none",
            "axes.edgecolor": "black",
            "axes.labelcolor": "black",
            "axes.prop_cycle": cycler(color=DEFAULT_20),
            "axes.unicode_minus": True,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": lw["axis"],
            "ytick.major.width": lw["axis"],
            "xtick.minor.width": lw["thin"],
            "ytick.minor.width": lw["thin"],
            "xtick.major.size": 2,
            "ytick.major.size": 2,
            "xtick.minor.size": 1,
            "ytick.minor.size": 1,
            "xtick.major.pad": 1.5,
            "ytick.major.pad": 1.5,
            # marks
            "lines.linewidth": lw["data"],
            "lines.markersize": 3,
            "patch.linewidth": lw["thin"],
            "errorbar.capsize": 0,
            "boxplot.flierprops.markersize": 1.5,
            "boxplot.boxprops.linewidth": lw["axis"],
            "boxplot.whiskerprops.linewidth": lw["axis"],
            "boxplot.capprops.linewidth": lw["axis"],
            "boxplot.medianprops.linewidth": lw["axis"],
            "boxplot.medianprops.color": "black",
            "image.cmap": "viridis",
            "scatter.edgecolors": "none",
            # legends
            "legend.frameon": False,
            "legend.borderaxespad": 0.2,
            "legend.borderpad": 0.2,
            "legend.handlelength": 1.0,
            "legend.handleheight": 0.7,
            "legend.handletextpad": 0.4,
            "legend.labelspacing": 0.25,
            "legend.columnspacing": 0.8,
            "legend.markerscale": 1.0,
            # output: exact figure size, raster parts at RASTER_DPI
            "figure.dpi": 150,
            "figure.facecolor": "white",
            "savefig.dpi": RASTER_DPI,
            "savefig.bbox": None,
            "savefig.pad_inches": 0,
            "savefig.facecolor": "white",
        }
    )
