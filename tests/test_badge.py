"""Badges: the shape is the caller's, the size is shared, so a diamond holds the circle's ID."""

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest
from matplotlib.text import Text

import scifig as sf


def _extent(marker):
    """Width of the drawn marker, in points."""
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 40, 40)
    line, _ = sf.badge(ax, 0.5, 0.5, "#1f77b4", id="7", marker=marker)
    fig.canvas.draw()
    path = line._marker.get_path().transformed(line._marker.get_transform())
    return line.get_marker(), path.get_extents().width * line.get_markersize()


def test_shape_is_applied():
    assert _extent("D")[0] == "D"
    assert _extent("o")[0] == "o"


def test_line_marker_refused():
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 40, 40)
    with pytest.raises(ValueError, match="filled"):
        sf.badge(ax, 0.5, 0.5, "#1f77b4", marker="x")


def test_diamond_inscribes_the_circles_square():
    # A circle of diameter d inscribes a square of side d/sqrt(2); a diamond inscribes the same
    # square when its tips span d*sqrt(2) -- which is what one shared markersize gives.
    _, circle = _extent("o")
    _, diamond = _extent("D")
    assert np.isclose(diamond, circle * np.sqrt(2))


def test_ink_on():
    assert sf.ink_on("white") == "black"
    assert sf.ink_on("#ffdd57") == "black"
    assert sf.ink_on("#1f77b4") == "white"


def test_blended_transform_places_badge_beside_tick():
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 20, 5, 40, 40)
    ax.barh(range(3), [1, 2, 3])
    trans = ax.get_yaxis_transform()
    line, text = sf.badge(ax, -0.1, 2, "#1f77b4", id="3", transform=trans)
    fig.canvas.draw()
    expected = trans.transform((-0.1, 2))
    assert np.allclose(line.get_transform().transform(line.get_xydata())[0], expected)
    assert np.allclose(text.get_transform().transform(text.get_position()), expected)
    assert ax.get_xlim()[0] == 0  # the badge does not stretch the view


def _legend(*handles, **kwargs):
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 40, 40)
    legend = ax.legend(handles=list(handles), **kwargs)
    fig.canvas.draw()
    ids = [t for t in legend.findobj(Text) if t not in legend.get_texts() and t is not legend.get_title()]
    return legend, legend.legend_handles, ids


def test_handle_needs_no_handler_map():
    legend, (mark,), (idtext,) = _legend(sf.badge_handle("#1f77b4", id=5, label="Forebrain"))
    assert [t.get_text() for t in legend.get_texts()] == ["Forebrain"]
    assert mark.get_marker() == "o"
    assert idtext.get_text() == "5"
    assert idtext.get_color() == "white"


def test_handle_fills_box_whatever_the_shape():
    fontsize, box = 10, 1.7
    _, marks, _ = _legend(
        sf.badge_handle("C0", marker="o"),
        sf.badge_handle("C1", marker="D"),
        fontsize=fontsize,
        handleheight=box,
        handlelength=box,
    )
    height = fontsize * box - 0.35 * fontsize * (box - 0.7)  # matplotlib's handle box, less its descent
    circle, diamond = marks
    assert np.isclose(circle.get_markersize(), height)
    assert np.isclose(diamond.get_markersize() * np.sqrt(2), height)  # tips touch the box


def test_handle_id_takes_legend_size_unless_two_digits_overflow():
    _, _, (roomy,) = _legend(sf.badge_handle("C0", id=12), fontsize=10, handleheight=2, handlelength=2)
    _, _, (tight,) = _legend(sf.badge_handle("C0", id=12), fontsize=10)  # default box: 0.7 x 2 em
    assert roomy.get_fontsize() == 10
    assert tight.get_fontsize() < 10


def test_handle_outline_stays_inside_box():
    _, (plain,), _ = _legend(sf.badge_handle("C0"), fontsize=10, handleheight=1.7, handlelength=1.7)
    _, (outlined,), _ = _legend(
        sf.badge_handle("C0", edgecolor="black"), fontsize=10, handleheight=1.7, handlelength=1.7
    )
    assert outlined.get_markeredgecolor() == "black"
    assert np.isclose(outlined.get_markersize() + outlined.get_markeredgewidth(), plain.get_markersize())


def test_handle_refuses_line_marker():
    with pytest.raises(ValueError, match="filled"):
        sf.badge_handle("C0", marker="x")
