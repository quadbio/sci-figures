"""Export: one PDF per figure with editable Arial text, plus a PNG preview."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import matplotlib as mpl
from matplotlib.collections import Collection, QuadMesh
from matplotlib.figure import Figure

from .layout import MM, _size_mm
from .style import FONT, RASTER_DPI

MAX_PDF_MB = 5.0
DPI_STEPS = (RASTER_DPI, 900, 600, 450, 300)  # tried in order; 300 is Nature's minimum
RASTER_MIN_VERTICES = 10_000  # collections drawing more vertices are rasterized: about 400 points, or long outlines


def _vertices(c: Collection) -> int:
    """Vertices a collection draws: its marker's times its points for a scatter, else its paths'."""
    if isinstance(c, QuadMesh):
        h, w = c.get_coordinates().shape[:2]
        return (h - 1) * (w - 1) * 4
    paths, n_offsets = c.get_paths(), len(c.get_offsets())
    if len(paths) == 1 and n_offsets > 1:
        return len(paths[0].vertices) * n_offsets
    return sum(len(p.vertices) for p in paths)


def _rasterize_dense(fig: Figure) -> int:
    """Rasterize each collection drawing more than ``RASTER_MIN_VERTICES`` vertices; return their number."""
    n = 0
    for c in fig.findobj(Collection):
        if _vertices(c) > RASTER_MIN_VERTICES and not c.get_rasterized():
            c.set_rasterized(True)
            n += 1
    return n


def _scale_bars(fig: Figure) -> list[str]:
    """Page length of each ``scale_bar``; raises if its axes scale x and y differently."""
    fig.canvas.draw()  # equal aspect resizes axes at draw time
    out = []
    for ax in fig.axes:
        for bar in ax.artists:
            meta = getattr(bar, "_scifig", None)
            if meta is None:
                continue
            o, x1, y1 = ax.transData.transform([(0, 0), (1, 0), (0, 1)])
            mm_x, mm_y = abs(x1[0] - o[0]) / fig.dpi / MM, abs(y1[1] - o[1]) / fig.dpi / MM
            if abs(mm_x - mm_y) > 0.01 * max(mm_x, mm_y):
                raise ValueError(
                    f"Scale bar {meta['length']:g} {meta['unit']}: x and y scales differ; set ax.set_aspect('equal')."
                )
            out.append(
                f"Scale bar {meta['length']:g} {meta['unit']} = {meta['data_length'] * mm_x:.2f} mm on the page."
            )
    return out


def save(fig: Figure, path: str | Path, legend: str | Path | None = None, dpi: int | None = None) -> Path:
    """Write ``path`` as PDF and ``<dir>/.preview/<name>.png``; print size, raster dpi and scale bars.

    Collections drawing more than ``RASTER_MIN_VERTICES`` vertices (dense scatters, cell outlines)
    are rasterized. Rasters are written at the first of ``DPI_STEPS`` that keeps the PDF within
    ``MAX_PDF_MB`` (or at ``dpi``). Raises if the PDF holds fonts other than Arial or Type 3 fonts, which are
    not editable. ``legend``, the legend kept with the script, is copied next to the PDF as
    ``<name>_legend.md``.
    """
    path = Path(path).with_suffix(".pdf")
    path.parent.mkdir(parents=True, exist_ok=True)
    if legend is not None:
        dest = path.with_name(f"{path.stem}_legend.md")
        if Path(legend).resolve() != dest.resolve():
            shutil.copyfile(legend, dest)
    report = _scale_bars(fig)
    if n := _rasterize_dense(fig):
        report.append(f"Rasterized {n} collection(s) of more than {RASTER_MIN_VERTICES} vertices.")
    for d in [dpi] if dpi else DPI_STEPS:
        with mpl.rc_context({"pdf.use14corefonts": False}):  # so Type 1 fonts can only come from LaTeX
            fig.savefig(path, dpi=d)
        mb = path.stat().st_size / 1e6
        if mb <= MAX_PDF_MB:
            break
    raw = path.read_bytes()
    # Type 1 fonts come only from LaTeX equations (usetex=True); all other text must be Arial.
    fonts = re.findall(rb"/Subtype\s*/(?!Type1\b)\w+\s*/BaseFont\s*/([\w+\-,]+)", raw)
    fonts = {f.decode(errors="ignore") for f in fonts}
    if re.search(rb"/Subtype\s*/Type3", raw) or any(FONT not in f for f in fonts):
        raise ValueError(f"{path.name} embeds non-editable or non-{FONT} fonts: {sorted(fonts)}.")
    w, h = _size_mm(fig)
    print(f"{path.name}: {w:.0f} x {h:.0f} mm, {mb:.2f} MB, rasters at {d} dpi.", *report, sep="\n")
    if mb > MAX_PDF_MB:
        print(f"Above {MAX_PDF_MB:g} MB: rasterize dense scatters, subsample points or use smaller markers.")
    preview = path.parent / ".preview" / f"{path.stem}.png"
    preview.parent.mkdir(exist_ok=True)
    fig.savefig(preview, dpi=300)
    return path
