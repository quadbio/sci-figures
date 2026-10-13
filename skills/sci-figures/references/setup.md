# Setup

The machine steps (Arial, TeX) are once per machine. If one needs rights or software you don't have, tell the user.

## scifig
In the figure repo's `pixi.toml` (its lock pins the commit):
```toml
[pypi-dependencies]
scifig = { git = "https://github.com/quadbio/sci-figures" }
```
With uv: `uv add "scifig @ git+https://github.com/quadbio/sci-figures"`. For live edits to scifig, depend on a
checkout instead: `scifig = { path = "../sci-figures", editable = true }`.

## Figure conventions
`resources/figure_conventions.yaml` (`style.md`, Color and marks; an example in `examples/resources/`) must be
git-tracked, since worktrees see only tracked files. If `resources/` is ignored, add to `.gitignore`:
```
resources/*
!resources/figure_conventions.yaml
```

## Arial
```bash
python -m scifig.fonts   # into ~/.local/share/fonts, no root needed
```
Alternatively `pixi add mscorefonts`, or a folder with `arial*.ttf` in `SCIFIG_FONT_DIR`. Arial is Microsoft's, under
its own license; `scifig.fonts` fetches conda-forge's `mscorefonts` package.

## TeX (for equations)
Equations are typeset by LaTeX (`usetex=True`), which needs `latex` and `dvipng` on `PATH`. A full TeX Live or MacTeX
has everything; on a cluster, look for a module (`module spider texlive`). Otherwise TinyTeX, no root needed:
```bash
curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh   # into ~/.TinyTeX; elsewhere: ... | TINYTEX_DIR=<dir> sh
tlmgr install newtx newtxsf helvetic psnfss cm-super type1cm underscore geometry dvipng
```
After switching TeX installations, clear matplotlib's cache (`rm -r ~/.cache/matplotlib/tex.cache`). Equations embed
as Type 1 fonts (Helvetica and sans-serif math), editable in Illustrator only where those fonts are installed.
