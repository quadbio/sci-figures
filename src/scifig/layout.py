"""Figure canvas and axes in millimetres, panel letters."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

from .style import SIZES

MM = 1 / 25.4  # inches per mm


def new_figure(width: float, height: float) -> Figure:
    """Figure of exact size in mm."""
    return plt.figure(figsize=(width * MM, height * MM))


def _size_mm(fig: Figure) -> tuple[float, float]:
    w, h = fig.get_size_inches()
    return w / MM, h / MM


def add_axes_mm(fig: Figure, left: float, top: float, width: float, height: float, **kwargs) -> Axes:
    """Axes box (spines, not tick labels) at an exact position in mm from the figure's top-left corner."""
    fw, fh = _size_mm(fig)
    return fig.add_axes((left / fw, 1 - (top + height) / fh, width / fw, height / fh), **kwargs)


def panel_letter(
    fig: Figure,
    letter: str,
    left: float,
    top: float,
    title: str | None = None,
    over: Axes | Sequence[Axes] | None = None,
) -> Text:
    """Bold 8 pt panel letter with its top-left corner at ``left, top`` (mm).

    An optional panel title sits on its line, centered over the axes ``over`` (the plot or plots it titles).
    """
    fw, fh = _size_mm(fig)
    t = fig.text(left / fw, 1 - top / fh, letter, fontsize=SIZES["panel"], fontweight="bold", ha="left", va="top")
    if title:
        if over is None:
            raise ValueError("A panel title is centered over its plot: pass the axes it titles as `over`.")
        axes = [over] if isinstance(over, Axes) else list(over)

        def span(renderer):  # at draw time, since equal aspect resizes axes
            return Bbox.union([a.get_window_extent(renderer) for a in axes])

        fig.add_artist(
            Annotation(title, xy=(0.5, 0), xycoords=(span, t), ha="center", va="bottom", fontsize=SIZES["text"])
        )
    return t
