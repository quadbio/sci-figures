# Reviews

Two subagents that have not seen the conversation, run in parallel. Pass each only file paths, never summaries or explanations of the figure. They report; they do not edit.

## Layout review
- `PREVIEW`: `figures/.preview/<name>.png`
- `OUTLINE`: the approved outline
- `CONVENTIONS`: the absolute path of `references/style.md` in this skill

```
Review the figure PREVIEW against the visual conventions CONVENTIONS and the message in
OUTLINE. Read all of them. Inspect the whole figure and zoomed crops covering every region.
Assess:

1. Collisions: elements that overlap or touch; anything clipped or cut off.
2. Layout: deviations from the panel, alignment, connection and whitespace rules in CONVENTIONS,
   including anything in the bands of a panel letter, near-misses (elements that almost line
   up) and empty space beside squeezed elements.
3. Consistency: sizes of text, markers or lines that differ without a reason; text that
   looks smaller than 5 pt.
4. Message: whether it can be read from the figure alone; text that could go or be replaced
   by a visual element; panels that do not advance it.
5. Schematics and equations: whether the flow of what a schematic depicts can be followed;
   symbols undefined where they first appear or differing between drawing and equation;
   made-up data in a schematic that could be mistaken for real data.

Report a numbered list, most important first. For each finding: category, panel, problem,
location in the figure and suggested fix. Write "No issues" for a category without findings.
```

## Legend review
- `LEGEND`: `figures/<name>_legend.md`
- `SCRIPTS`: the figure script and every script or notebook that computed plotted data (follow imports and file reads back to the analysis step)
- `PREVIEW`: `figures/.preview/<name>.png`
- `CONVENTIONS`: the absolute path of `references/legends.md` in this skill
- `AUTHOR_CONVENTIONS`: a file quoting, verbatim, the rules the user stated for this paper's legends (omit if none)

```
Review the figure legend LEGEND against the code that produced the figure (SCRIPTS), the
rendered figure (PREVIEW) and the legend conventions (CONVENTIONS, overridden where they
conflict by AUTHOR_CONVENTIONS, if given). Read all of them. Assess:

1. Scientific correctness: every statement matches the code, including data sets and subsets,
   cell or sample numbers (recompute or trace them), axes and their scales, encodings,
   aggregation, what error bars, bands and boxes show, tests and their settings, n and what
   it counts, and scale-bar lengths (trace the conversion from data units). Flag statements
   the code does not support, and code behavior that changes interpretation but is not
   stated (e.g. values beyond axis limits or colorbar ends, capped sizes).
2. Conciseness: words or sentences that can go without losing information; facts stated twice.
3. Style: adherence to the conventions; sentences that parse more than one way.
4. Completeness: everything the conventions require is present for every panel, every
   visual element that would mislead without a note is explained, and every symbol in the
   figure's equations and labels is defined, in the figure or the legend.

Report a numbered list, most important first. For each finding: category, panel, problem,
evidence (file and line, or what the figure shows) and replacement text. Write "No issues"
for a category without findings.
```

## After the reviews
- Fix correctness findings. If the legend describes the intended analysis and the code is wrong, stop and tell the user.
- Apply other findings that agree with the conventions. The user's instructions beat reviewer findings: report each declined finding with the instruction, or other reason, that overrides it.
