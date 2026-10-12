"""Scale bars: length from data units, page length reported, unequal aspect refused."""

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest

import scifig as sf


def _image_fig(aspect):
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 60, 30)  # not proportional to the 150 x 100 µm image
    ax.imshow(np.zeros((200, 300)), extent=(0, 150, 0, 100), aspect=aspect)  # 0.5 µm per pixel
    return fig, ax


def test_page_length_reported(tmp_path, capsys):
    fig, ax = _image_fig("equal")
    sf.scale_bar(ax, 50, "µm")
    sf.save(fig, tmp_path / "f")
    mm_per_um = ax.get_window_extent().width / fig.dpi * 25.4 / 150
    assert f"{50 * mm_per_um:.2f} mm" in capsys.readouterr().out


def test_data_unit_size():
    fig = sf.new_figure(89, 60)
    ax = sf.add_axes_mm(fig, 5, 5, 60, 40)
    ax.imshow(np.zeros((200, 300)))  # pixel coordinates
    assert sf.scale_bar(ax, 20, "µm", data_unit_size=0.5)._scifig["data_length"] == 40


def test_unequal_aspect_refused(tmp_path):
    fig, ax = _image_fig("auto")
    sf.scale_bar(ax, 50, "µm")
    with pytest.raises(ValueError, match="differ"):
        sf.save(fig, tmp_path / "f")
