# sci-figures

A Claude Code plugin for Nature-style research figures (main, Extended Data, supplementary) and their legends. The
agent writes the plotting code (matplotlib, seaborn, scanpy, spatialdata-plot); the skill says what the result must
achieve, from the figure's message to its export as one PDF with editable Arial text, and has independent reviewers
check the layout and the legend against the code.

| Part | What it does |
| --- | --- |
| `skills/sci-figures/` | The workflow, visual and legend conventions, the two reviews, setup, and two complete example figures (outline, script, legend). Loaded on demand. |
| `src/scifig/` | `apply_style`, mm layout (`new_figure`, `add_axes_mm`, `panel_letter`), recurring elements (`badge`, `colorbar`, `embedding_axes`, `scale_bar`) and `save`, which checks fonts, sizes and raster resolution. |

## Use

Ask Claude for a figure, a panel or a legend in the repo that holds the figure scripts.

1. It agrees the format and an outline with you (message, story line, one entry per panel) and saves the outline
   next to the script.
2. It computes the plotted data, then writes one script per figure that only loads and plots it.
3. It checks the preview against the layout checklist, writes the legend from the code and the data, and runs the
   layout and legend reviews in parallel.
4. It shows you the PDF with its legend and lists the review findings it declined.

Colors and marks shared across a paper's figures live in the repo's `resources/figure_conventions.yaml`.

## Install

**The plugin**, once per machine, from the [quadbio marketplace](https://github.com/quadbio/claude-plugins).

**The package**, Arial and TeX (for equations): [`skills/sci-figures/references/setup.md`](skills/sci-figures/references/setup.md).

## Develop

```bash
uv sync --group dev
uv run python -m scifig.fonts   # Arial, once per machine
uv run pytest                   # the equation test is skipped without TeX
uv run pre-commit run --all-files
claude plugin validate .
claude --plugin-dir .           # try the skill from this checkout
```

The example figures: `uv run --extra examples python skills/sci-figures/examples/fig1_moscot.py` writes
`figures/fig1_moscot.pdf`, its legend and preview (needs TeX). The spatial one needs the `spatial-examples` extra and the
Xenium dataset (`fig2_spatial_outline.md`, Source): run `fig2_spatial_data.py` (about 7 min on 8 cores), then
`fig2_spatial.py`.

For live package edits in a figure repo, depend on the checkout instead:
`scifig = { path = "../sci-figures", editable = true }`.

## Release

Bump `version` in both `pyproject.toml` and `.claude-plugin/plugin.json` and the pin in
`skills/sci-figures/references/setup.md` (tests check they agree), tag `vX.Y.Z`, then bump the `ref` in
[quadbio/claude-plugins](https://github.com/quadbio/claude-plugins).

## License

MIT
