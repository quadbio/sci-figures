**Message:** Moscot fate probabilities track driver-gene expression, and moscot scales to one million cells.
**Story line:** method (a), its output on cells (b), accuracy against alternatives (c, d), then scaling (e).

**a** Optimal transport
- Role: intuition for the problem moscot solves between time points, in the order it is computed
- Shows: a toy problem, four earlier and three later cells with generic cell types (A-D) and masses; the coupling is its Sinkhorn solution
- Plot: the cells in the embedding (earlier circles, later squares, area proportional to mass; marginals labelled there), the cost matrix and the coupling as heatmaps headed by the cells' marks, on one line with arrows; the problem and its feasible set under the cells and costs, which define it (brace); keys to time point and cell type in a column right of the coupling
- Shared: none (a cartoon; its cell types are generic)

**b** Cells and Beta fate
- Role: the cells and fates of the system, and moscot's output, a fate probability per cell
- Shows: 3,000 simulated cells
- Plot: one embedding twice, colored by cell type and by Beta fate probability (0 to 1); one axis indicator; keys below their plots

**c** Transition accuracy
- Role: moscot predicts transitions more accurately
- Shows: 10 replicates per method and stage
- Plot: points per replicate with median and IQR; method key, shared with d

**d** Driver-gene correlation
- Role: fate probabilities agree with driver-gene expression
- Shows: 30 driver genes per tissue and method
- Plot: box plots with points, one shared y axis

**e** Runtime
- Role: moscot scales to a million cells
- Plot: runtime against cells, log-log, one line per method, labelled directly
