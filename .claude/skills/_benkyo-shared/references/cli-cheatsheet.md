# benkyo CLI cheatsheet

Quick reference for the `benkyo` CLI commands. JSON output, exit codes: 0=ok, 1=invalid_arg, 2=not_found, 3=conflict.

## Global options

```
benkyo --db <path>           # override DB file path (precedence: flag > env BENKYO_DB > OS default)
benkyo --version             # show version
benkyo info                  # show DB path, source, and counts per table
```

## Concept nodes

```
benkyo concept add --content <text>                  # or --content-file <path>, or --content -  (stdin)
benkyo concept get <id>
benkyo concept update <id> --content <text>
benkyo concept delete <id>                           # cascades to project_concepts and edges
benkyo concept list [--query <text>]                 # substring filter on content
benkyo concept find --content <text>                 # exact-match (identity check; ALWAYS run before add)
```

## Problem nodes

```
benkyo problem add --statement <text> --answer <text>
benkyo problem get <id>
benkyo problem update <id> [--statement <text>] [--answer <text>]
benkyo problem delete <id>
benkyo problem list [--query <text>]
```

## Edges

Two types: `prereq` (directed, X depends on Y) and `related` (used for confusable / cooccurring pairs).

```
benkyo edge add --from <id> --to <id> --type <prereq|related>
benkyo edge delete --from <id> --to <id> --type <prereq|related>
benkyo edge list [--from <id>] [--to <id>] [--type <prereq|related>]
```

## Projects

```
benkyo project create --metadata <text> [--goals <id1,id2,...>]
benkyo project get <id>
benkyo project update <id> [--metadata <text>] [--goals <ids>]
benkyo project delete <id>                           # cascades to project_concepts and project_goals
benkyo project list
```

## Treatment (per (project, concept))

```
benkyo treatment set --project <id> --concept <id> --treatment <procedural|conceptual> [--reference <text>]
benkyo treatment get --project <id> --concept <id>   # returns {treatment, default: bool}; default=true means unset
benkyo treatment unset --project <id> --concept <id> # back to default (conceptual)
benkyo treatment list --project <id> [--treatment <procedural|conceptual>]
```

## Traversal

```
benkyo window --project <id>                                # all in-window nodes + edges; procedural concepts are terminals
benkyo breakdown --project <id> --node <id>                 # direct prereq dependencies of node, each annotated with treatment
benkyo frontier --project <id>                              # procedural concepts within window (promotion candidates)
benkyo ancestors --project <id> --node <id>                 # nodes that depend on this node, within window
```

## Render (visualization)

```
benkyo render --project <id> --format <mermaid|dot> [--output <path>]
```

- Default format: mermaid (embeddable in markdown).
- Without `--output`: raw text on stdout (pipe-friendly: `... --format dot | dot -Tpng > graph.png`).
- Shape conventions: problem = stadium, conceptual = rectangle, procedural = cylinder.

## Export / Import

```
benkyo export graph [--output <path>]
benkyo export project <id> [--output <path>]
benkyo import graph <path> [--on-conflict skip|overwrite|error]
benkyo import project <path> [--on-conflict skip|overwrite|error]
```

- Graph export contains all nodes + edges; project export references global ids and contains only project metadata + treatments.
- Format strings: `benkyo/graph/v1` or `benkyo/project/v1`.

## ID conventions

- Concepts: `c1`, `c2`, ...
- Problems: `p1`, `p2`, ...
- Projects: `prj1`, `prj2`, ...

## Common patterns

### Add a new concept (with identity check)

```
benkyo concept find --content "Laplace transform"    # check for duplicates first
# if no match:
benkyo concept add --content "Laplace transform: ..."
```

### Set procedural treatment with a reference table

```
benkyo treatment set \
  --project prj1 --concept c5 \
  --treatment procedural \
  --reference-file laplace-table.md
```

### Commit (procedural → conceptual)

```
benkyo treatment unset --project prj1 --concept c5
# then ensure prereqs of c5 exist; add them as procedural if missing
```

### Release (conceptual → procedural)

```
benkyo treatment set --project prj1 --concept c5 \
  --treatment procedural --reference "<reference text>"
```

### Inspect a project's state

```
benkyo project get prj1
benkyo window --project prj1
benkyo frontier --project prj1
```

### Re-show graph after edits

```
benkyo render --project prj1 --format mermaid
```
