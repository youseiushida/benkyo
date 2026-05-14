# Concept node granularity guide

Determining the right level of granularity for concept nodes is one of the most consequential graph-curation decisions. Too coarse: treatment becomes blunt, breakdown is meaningless. Too fine: graph bloats, traversal becomes noise.

## The 5 criteria

A concept node should be a single node if its scope satisfies these criteria together. If any criterion is violated, consider splitting.

### Criterion 1: Single treatment unit

A node should be the smallest unit that can be assigned procedural or conceptual treatment as a whole.

**Why this matters**: treatment annotation lives at the node level. If you want to treat part of a "concept" procedurally and another part conceptually, the node is too coarse.

**Example**: "Laplace transform" — if you want the whole thing as a unit (table + properties + inverse + convolution) for "use as a tool", it's one node. If you want "convolution theorem" conceptual but the rest procedural, split off "convolution theorem".

### Criterion 2: Uniform prerequisites

A node's prerequisites should be roughly consistent across its sub-aspects.

**Why this matters**: when you breakdown a conceptual node, you traverse to its prereqs. If different sub-aspects need different prereqs, breakdown becomes inconsistent.

**Example**: "Differential equations" is too coarse — separable ODE needs only integration, linear ODE needs complex roots, Sturm-Liouville needs eigenvalues. These are wildly different prereqs. Split into solution-method-level nodes.

### Criterion 3: Aligned with textbook / course chunking

Default granularity is **textbook section level** — finer than chapters, coarser than individual theorems.

**Why this matters**: pedagogical chunking has been refined over decades and tends to satisfy criteria 1 & 2 naturally. Following it reduces ad-hoc judgment burden.

**Example** (complex analysis): split into "complex numbers and operations", "analytic functions and Cauchy-Riemann", "Cauchy's theorem", "Cauchy's integral formula", "Laurent series", "residue theorem", "conformal mapping". Each is a section in standard textbooks.

### Criterion 4: Reusability

A node deserves to exist (rather than being absorbed into a parent) if it appears as a prereq of multiple parent nodes or problems.

**Why this matters**: shared prereqs are the structural meat of the graph. Hyper-specific sub-concepts used only in one place can be folded into the parent's explanation rather than as a separate node.

**Example**: "Partial fraction decomposition" is a prereq for Laplace inverse, rational integration, linear ODE — independent node. "Bromwich integral contour selection" is used only in one specific Laplace inverse technique — could be absorbed into the parent.

### Criterion 5: Probing feasibility

You should be able to probe the learner's understanding of the node as a single unit.

**Why this matters**: treatment updates (commit/release) and self-evaluation handling depend on being able to ask "do you understand X?" and get a meaningful answer.

**Counter-example**: "Complex function theory" as a single node — too abstract to probe. "Do you understand complex function theory?" cannot be answered meaningfully. Split until probable.

## Rationale and literature support

- **Sinha & Kapur**: PF generates "multiple representations and solution methods (RSMs)". If a concept has multiple solution methods, those benefit from being separate nodes (so the learner can compare).
- **Brunmair & Richter**: confusable pairs (between-category similarity high) need to be discriminated. Each must be a separate node to be linked by a `related` edge.
- **Kalyuga rapid diagnostic**: "first-step" probes ask for the next move in a problem. The granularity must support a sensible first-step — too coarse and there's no answerable first-step.

## Lazy refinement

Default approach: **start coarse, split when needed**.

Reasons:
- Cross-project granularity tension: the same concept may want finer treatment in some projects than others. The global graph must accommodate the finest split anyone needs.
- Pre-empting splits "just in case" is over-engineering. The actual need surfaces during use.

Practical sequence:
1. When creating a project, use section-level granularity (criterion 3).
2. When a treatment decision can't apply uniformly within a node (criterion 1 violated), split.
3. When breakdown reveals inconsistent prereqs (criterion 2 violated), split.
4. When a sub-aspect of a node is reused independently elsewhere (criterion 4 newly satisfied), split.

## Merging signals

A node should be merged with another if:

- They're always referenced together (same prereqs, same problems use both).
- Their content overlaps substantially.
- Treatment in every project has been the same for both.
- The textbook treats them as one unit.

Run `concept find --content <...>` before adding any new concept to catch duplicates that should be merged with existing.

## Cross-project tension

The global graph is shared, but treatments are per-project. If Project A wants coarse granularity ("Laplace transform" as one node) and Project B wants finer ("Laplace definition", "transform table", "inverse transform"), the global graph must support B's finer split. Project A can compensate by marking all fine nodes as procedural — coarse handling emerges from treatment, not granularity.

**Rule**: split to the finest grain that any project needs. Coarser-use projects aggregate via treatment.

## Quick decision flowchart

```
New concept to add?
├─ Run `concept find --content` to check identity
├─ If similar exists: consider merging or referencing existing
└─ If genuinely new:
   ├─ Does the textbook/course treat it as a section? → use that
   ├─ Will treatment be uniform (criterion 1)? → keep as one node
   ├─ Will breakdown be consistent (criterion 2)? → keep as one node
   ├─ Will it be probed as a unit (criterion 5)? → keep as one node
   └─ Otherwise: split before adding
```

## What's NOT a granularity issue

- Single concept with multiple notations (e.g., "del" and "∇" — same concept, alt notation): one node, mention notations in content.
- Concept that has historical alternative names ("Heaviside function" = "unit step function"): one node, list aliases in content.
- Concept that's an instance of a more general one ("specific RLC circuit type" vs "RLC circuit"): only split if the specific instance has substantially different prereqs or treatment.

When in doubt, **lean coarse** and split lazily.
