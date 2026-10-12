"""Badges: the shape is the caller's, the size is shared, so a diamond holds the circle's ID."""

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest

import scifig as sf


def _extent(marker):
    """Width of the drawn marker, in points."""
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 40, 40)
    line, _ = sf.badge(ax, 0.5, 0.5, "#1f77b4", label="7", marker=marker)
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
