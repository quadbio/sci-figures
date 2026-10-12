"""Recurring visual elements: embedding axis arrows, end-labelled colorbars, scale bars, badges."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import to_rgb
from matplotlib.markers import MarkerStyle

from .layout import MM, _size_mm
from .style import LINEWIDTHS, SIZES


def embedding_axes(ax: Axes, basis: str = "UMAP", arrow_mm: float = 5.0) -> None:
    """Replace frame and ticks with an L-shaped indicator labelled ``basis``1/2 at the bottom-left.

    Fits the view to the data so the indicator sits at the scatter's corner. Call after plotting.
    """
    ax.margins(0.02)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for s in ax.spines.values():
        s.set_visible(False)
    fw, fh = _size_mm(ax.figure)
    w_mm, h_mm = ax.get_position().width * fw, ax.get_position().height * fh
    arrow = {
        "arrowstyle": "-|>,head_length=0.25,head_width=0.12",
        "lw": LINEWIDTHS["axis"],
        "color": "black",
        "shrinkA": 0,
        "shrinkB": 0,
    }
    kw = {"xycoords": "axes fraction", "textcoords": "axes fraction", "arrowprops": arrow, "annotation_clip": False}
    ax.annotate("", xy=(arrow_mm / w_mm, 0), xytext=(0, 0), **kw)
    ax.annotate("", xy=(0, arrow_mm / h_mm), xytext=(0, 0), **kw)
    t = {"fontsize": SIZES["text"], "transform": ax.transAxes, "clip_on": False}
    ax.text(0, -0.8 / h_mm, f"{basis}1", ha="left", va="top", **t)
    ax.text(-0.8 / w_mm, 0, f"{basis}2", ha="right", va="bottom", rotation=90, **t)


def colorbar(
    mappable,
    cax: Axes,
    label: str | None = None,
    ends: tuple[str, str] | None = ("Low", "High"),
    orientation: str = "vertical",
) -> Colorbar:
    """Thin colorbar in ``cax`` (e.g. 1.5 x 12 mm), ticked at its ends only.

    ``ends`` replaces the end labels; ``None`` keeps the numbers (set vmin/vmax so they are
    exact). ``label`` sits above the bar, flush with its left edge. Horizontal end labels align
    inwards, so nothing overhangs the bar.
    """
    cb = cax.figure.colorbar(mappable, cax=cax, orientation=orientation)
    cb.outline.set_visible(False)
    cb.set_ticks([mappable.norm.vmin, mappable.norm.vmax])
    if ends is not None:
        cb.set_ticklabels(list(ends))
    cb.ax.tick_params(length=0, pad=1, labelsize=SIZES["text"])
    if orientation == "horizontal":
        lo, hi = cb.ax.get_xticklabels()
        lo.set_horizontalalignment("left")
        hi.set_horizontalalignment("right")
    if label:
        cax.set_title(label, loc="left", fontsize=SIZES["text"], pad=SIZES["text"] * 0.6 + 2)
    return cb


def scale_bar(
    ax: Axes, length: float, unit: str = "µm", data_unit_size: float = 1.0, loc: str = "lower right", **kwargs
):
    """Scale bar of ``length`` ``unit``, drawn in ``ax``'s data coordinates so it survives layout changes.

    ``data_unit_size`` is the size of one data unit in ``unit`` (e.g. µm per pixel). Other
    keyword arguments go to ``AnchoredSizeBar`` (e.g. ``bbox_to_anchor`` to place it outside
    the image). ``save`` reports its length on the page.
    """
    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

    kw = {"pad": 0.5, "sep": 2.0, "frameon": False, "size_vertical": 0, "fontproperties": {"size": SIZES["text"]}}
    kw |= kwargs
    bar = AnchoredSizeBar(ax.transData, length / data_unit_size, f"{length:g} {unit}", loc, **kw)
    bar.size_bar.get_children()[0].set_linewidth(LINEWIDTHS["data"])
    bar._scifig = {"length": length, "unit": unit, "data_length": length / data_unit_size}
    ax.add_artist(bar)
    return bar


def badge(
    ax: Axes,
    x: float,
    y: float,
    color,
    label: str | int | None = None,
    diameter: float = 3.0,
    transform=None,
    marker: str = "o",
):
    """An entity's mark: a filled shape (``diameter`` mm) with an optional centred ID.

    The ID is black or white by contrast. ``transform`` defaults to data coordinates. Returns ``(marker, text)``.

    ``marker`` is a filled matplotlib marker, so different kinds of entity can carry different
    shapes. At one ``diameter``, a diamond (``"D"``) leaves the ID as much room as a circle
    (equal inscribed square) but its tips reach 1.41x further; space neighbouring badges for that.
    """
    if not MarkerStyle(marker).is_filled():
        raise ValueError(f"A badge is a filled shape; {marker!r} is a line marker.")
    transform = transform or ax.transData
    (marker,) = ax.plot(
        [x],
        [y],
        marker=marker,
        ls="",
        markersize=diameter * MM * 72,
        markerfacecolor=color,
        markeredgecolor="none",
        transform=transform,
        clip_on=False,
        scalex=False,
        scaley=False,
    )
    text = None
    if label is not None:
        r, g, b = (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in to_rgb(color))
        ink = "black" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.179 else "white"  # WCAG luminance
        text = ax.text(
            x,
            y,
            str(label),
            transform=transform,
            ha="center",
            va="center_baseline",
            fontsize=SIZES["min"],
            color=ink,
            clip_on=False,
        )
    return marker, text
