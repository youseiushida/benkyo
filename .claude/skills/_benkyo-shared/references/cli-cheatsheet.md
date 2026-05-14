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
benkyo concept add --content <text> [--name <short_label>]   # --name auto-extracted from content if omitted; or --content-file / --content -  (stdin)
benkyo concept get <id>
benkyo concept update <id> [--content <text>] [--name <short_label>]   # at least one required
benkyo concept delete <id>                                    # cascades to project_concepts and edges
benkyo concept list [--query <text>]                         # substring filter on content
benkyo concept find --content <text>                         # exact-match (identity check; ALWAYS run before add)
benkyo concept merge <source_id> --into <canonical_id> [--on-conflict <error|keep_canonical|keep_source>]
                                                             # collapse duplicate; redirects edges + project_concepts; --on-conflict resolves treatment clashes
benkyo concept fork <source_id> --content <text>             # or --content-file; create a new concept that copies source's edges (treatments NOT copied)
```

**`name` field**: short label used in graph diagrams and breakdown output. Auto-extracted from the first `Name: ...` token in content. Override explicitly when the auto-extracted form is wrong or you want a custom abbreviation.
```
benkyo concept add --name "凸関数" --content "凸関数: f: C→ℝ は全ての x,y と t∈[0,1] で..."
benkyo concept update c7 --name "LP標準形"    # update label only, keep content
```

## Problem nodes

```
benkyo problem add --statement <text> --answer <text>
benkyo problem get <id>
benkyo problem update <id> [--statement <text>] [--answer <text>]
benkyo problem delete <id>
benkyo problem list [--query <text>]
benkyo problem merge <source_id> --into <canonical_id>
                                                     # collapse duplicate; redirects edges + project_goals
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
benkyo treatment set --project <id> --concept <id> --treatment <blackbox|whitebox> [--reference <text>]
benkyo treatment get --project <id> --concept <id>   # returns {treatment, default: bool}; default=true means unset
benkyo treatment unset --project <id> --concept <id> # back to default (whitebox)
benkyo treatment list --project <id> [--treatment <blackbox|whitebox>]
```

## Traversal

```
benkyo window --project <id>                                # all in-window nodes + edges; blackbox concepts are terminals
benkyo breakdown --project <id> --node <id>                 # direct prereq dependencies of node, each annotated with treatment
benkyo frontier --project <id>                              # blackbox concepts within window (promotion candidates)
benkyo ancestors --project <id> --node <id>                 # nodes that depend on this node, within window
```

## Render (visualization)

```
benkyo render --project <id> [--scope <window|project|graph>] [--format <mermaid|dot>] [--output <path>]
```

- Default scope: `window` (BFS from goal problems via prereq edges).
- `--scope project`: all nodes explicitly registered in the project (project_concepts + goals). Use when you want the full picture — practice problems, formula concepts, and related items outside the window.
- `--scope graph`: entire global concept/problem graph.
- Default format: mermaid (embeddable in markdown).
- Without `--output`: raw text on stdout (pipe-friendly: `... --format dot | dot -Tpng > graph.png`).
- Node labels: concept `name` field (short); problem statement truncated to 40 chars.
- Shape conventions: problem = stadium, whitebox = rectangle, blackbox = cylinder.
- Related edges are undirected dashed (`-.-` in mermaid) — symmetric "easy to confuse" relationship.
- Blackbox nodes get `classDef blackbox` fill color in mermaid output.

## Events (append-only log of state changes)

The events table is the queryable history. Skills write to it on state changes,
and read from it for cross-session reasoning (delayed JOL verification,
hypercorrection re-probing, mastery tracking).

```
benkyo events add --kind <kind> [--project <id>] [--payload <json>] [--payload-file <path>] [--notes <text>]
benkyo events get <event_id>
benkyo events list [--project <id>] [--kind <kind>] [--since <iso>] [--until <iso>] [--limit <n>]
benkyo events delete <event_id>               # correction-only; the log is append-only by convention
```

Known kinds (the column is not CHECK-constrained, but stick to these unless
you have a specific reason to invent a new one):

| kind | typical payload |
|---|---|
| `session_start` | `{}` (use `--notes` for context like "1 week gap") |
| `session_end` | `{completed_problems, treatment_changes, pending}` |
| `delayed_jol_recorded` | `{concept_id, claim: "high"|"mid"|"low"}` |
| `hypercorrection_detected` | `{concept_id, problem_id, learner_confidence}` |
| `treatment_changed` | `{concept_id, from, to}` |
| `concept_probed` | `{concept_id, problem_id, correct: bool}` |

The `notes` column is free text — use it to capture LLM-flexibility context
that doesn't fit the payload schema ("学習者は明日試験", "風邪気味と発話", etc.).

## Sessions (high-level atomic operations)

Use these instead of composing `events add` sequences yourself. They wrap
multiple primitive writes in a single transaction.

```
benkyo session end --project <id> --summary-file <path>      # or --summary <json>
```

Summary JSON shape (all keys optional):

```json
{
  "completed_problems": ["p1", "p3"],
  "treatment_changes": [{"concept_id": "c5", "from": "blackbox", "to": "whitebox"}],
  "pending": ["c4 mid-derivation"],
  "delayed_jols": [
    {"concept_id": "c1", "claim": "high"},
    {"concept_id": "c2", "claim": "mid", "note": "怪しい"}
  ],
  "notes": "学習者は明日試験"
}
```

Writes one `session_end` event plus one `delayed_jol_recorded` event per entry
in `delayed_jols`. Each JOL entry's optional `note` becomes the event's
`notes` column. All-or-nothing transactionally.

## Schema (runtime introspection)

```
benkyo schema                # JSON tree of every command, subcommand, option, argument
```

Use this to verify the installed CLI matches what your cheatsheet expects, or
to discover available commands without parsing `--help` text.

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

### Set blackbox treatment with a reference table

```
benkyo treatment set \
  --project prj1 --concept c5 \
  --treatment blackbox \
  --reference-file laplace-table.md
```

### Commit (blackbox → whitebox)

```
benkyo treatment unset --project prj1 --concept c5
# then ensure prereqs of c5 exist; add them as blackbox if missing
```

### Release (whitebox → blackbox)

```
benkyo treatment set --project prj1 --concept c5 \
  --treatment blackbox --reference "<reference text>"
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
