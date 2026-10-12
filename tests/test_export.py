"""save: exact size, preview, editable Arial only, raster dpi lowered to fit the size budget."""

import shutil

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest

import scifig as sf


def test_pdf_and_preview(tmp_path, capsys):
    fig = sf.new_figure(89, 50)
    ax = sf.add_axes_mm(fig, 10, 5, 70, 35)
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("Time (h)")
    sf.panel_letter(fig, "a", 1, 1, title="Panel title", over=ax)
    (tmp_path / "src.md").write_text("**Fig. 1 | Title.**")
    out = sf.save(fig, tmp_path / "out" / "fig1", legend=tmp_path / "src.md")
    assert out.exists() and (out.parent / ".preview" / "fig1.png").exists()
    assert (out.parent / "fig1_legend.md").read_text() == "**Fig. 1 | Title.**"
    assert "89 x 50 mm" in capsys.readouterr().out


def test_other_font_refused(tmp_path):
    fig = sf.new_figure(89, 50)
    fig.text(0.5, 0.5, "DejaVu", family="DejaVu Sans")
    with pytest.raises(ValueError, match="fonts"):
        sf.save(fig, tmp_path / "f")


def test_core_fonts_cannot_bypass_the_font_check(tmp_path, monkeypatch):
    monkeypatch.setitem(matplotlib.rcParams, "pdf.use14corefonts", True)  # would write text as Type 1 core fonts
    fig = sf.new_figure(89, 50)
    fig.text(0.5, 0.5, "Arial")
    raw = sf.save(fig, tmp_path / "f").read_bytes()
    assert b"ArialMT" in raw and b"/Subtype /Type1" not in raw


@pytest.mark.skipif(not shutil.which("latex"), reason="needs TeX Live")
def test_latex_equation_accepted(tmp_path):
    fig = sf.new_figure(89, 50)
    fig.text(0.1, 0.5, r"$\underbrace{\lambda^2 \nabla^2 c}_{\text{diffusion}} = \mathrm{FGW}, 0.5$", usetex=True)
    sf.save(fig, tmp_path / "f")


def test_dpi_lowered_to_fit(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sf.export, "MAX_PDF_MB", 0.05)
    fig = sf.new_figure(89, 50)
    ax = sf.add_axes_mm(fig, 5, 5, 40, 40)
    ax.imshow(np.random.default_rng(0).random((100, 100)))
    sf.save(fig, tmp_path / "f")
    assert "rasters at 1200 dpi" not in capsys.readouterr().out


def test_title_on_the_letter_line_centered_over_its_plot():
    fig = sf.new_figure(89, 50)
    ax = sf.add_axes_mm(fig, 20, 8, 60, 35)
    letter = sf.panel_letter(fig, "a", 1, 1, title="Title", over=ax)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    lb, tb, ab = letter.get_window_extent(r), fig.artists[-1].get_window_extent(r), ax.get_window_extent(r)
    tol = 0.1 / 25.4 * fig.dpi  # 0.1 mm
    assert abs(lb.y0 - tb.y0) < tol
    assert abs((tb.x0 + tb.x1) / 2 - (ab.x0 + ab.x1) / 2) < tol
    with pytest.raises(ValueError, match="over"):
        sf.panel_letter(fig, "b", 1, 1, title="Title")
