# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-05-14

### Fixed

- **`--scope project` now shows all reachable concepts** — previous implementation
  queried `project_concepts` as a membership filter, so default-whitebox concepts
  (no explicit `treatment set` call) were invisible. Replaced with the same BFS
  as `window` but without the blackbox-terminal rule.
- **Graph styling: cylinder removed** — blackbox concepts now render as rectangles
  with amber fill (`#fde68a`) instead of 3D cylinders. Whitebox concepts get light
  blue fill (`#dbeafe`); problems get light grey (`#f0f4ff`). All three node types
  use `classDef` in mermaid and `fillcolor` in DOT.

## [0.4.0] - 2026-05-14

### Added

- **`name` field on `concept_nodes`** — short display label, independent of
  `content`. Auto-extracted from the first `Name: ...` token in content; set
  explicitly with `--name`. Concept graph labels, breakdown output, and
  `concept list` all use `name` instead of the full definition text.
  - `benkyo concept add --name "凸関数" --content "凸関数: f: C→ℝ は..."` (explicit)
  - `benkyo concept update <id> --name "LP標準形"` (label-only update)
  - Auto-migration: `_migrate_v03_to_v04()` adds the column and backfills all
    existing concepts from their content. Idempotent; runs on every `connect()`.
- **`benkyo render --scope <window|project|graph>`** — three render scopes:
  - `window` (default): existing BFS-from-goals behavior.
  - `project`: all nodes explicitly registered in the project
    (`project_concepts` + goal problems). Reveals practice problems, formula
    concepts, and related items that fall outside the window.
  - `graph`: entire global concept/problem graph.
- **Mermaid treatment styling**: `classDef blackbox fill:#e8d5b7,...` emitted
  when there are nodes; `class <ids> blackbox` marks blackbox nodes. Blackbox
  status is now distinguishable at a glance without relying on cylinder shape
  alone.
- **3 migration regression tests** (`tests/test_migration.py`): v0.3 DB gets
  name column; v0.2 DB gets name column via chained migration; v0.4 DB idempotent.

### Fixed

- **Related edges in mermaid are now undirected** (`-.-` instead of `-.->`)
  — symmetric "easy to confuse" relationships no longer imply a direction.
- **Problem labels truncated to 40 chars** in both mermaid and DOT. Previously
  full statement text (100-500 chars) was used as the node label, making
  rendered graphs unreadable.

## [0.3.0] - 2026-05-14

**Breaking**: treatment values renamed `procedural` → `blackbox`,
`conceptual` → `whitebox`. Auto-migrating on first `connect()` so existing
v0.2 DBs upgrade transparently; no user action needed.

### Why

The terms `procedural` / `conceptual` were borrowed from the math-education
literature (Sinha & Kapur 2021, Hiebert & Lefevre 1986) where they mean what
benkyo intended. But the same word *procedural* also denotes the opposite
concept in cognitive psychology (ACT-R: automated expert knowledge) — the
end-state of expertise, not a shortcut around it. That overlap was a
persistent source of LLM-prior interference for the skill layer and of
read-time friction for engineers. `blackbox` / `whitebox` is a cleaner
metaphor for "use as a tool" vs "understand the internals", lines up with
software-engineering intuition, and has no prior-knowledge collision.

The mapping to cited papers is preserved in `literature-pointers.md` and
README's terminology note: paper's "conceptual knowledge" ≈ benkyo's
"whitebox treatment"; paper's "procedural knowledge" ≈ benkyo's "blackbox
treatment".

### Changed (breaking)

- **DB schema**: `project_concepts.treatment` CHECK constraint values changed
  from `('procedural', 'conceptual')` to `('blackbox', 'whitebox')`.
- **CLI**: `benkyo treatment set --treatment <blackbox|whitebox>` (was
  `<procedural|conceptual>`); `treatment list --treatment` filter same; help
  text updated.
- **Skill files**: all 5 `SKILL.md` and 7 of the 8 shared references in
  `_benkyo-shared/references/` updated to the new vocabulary. `literature-
  pointers.md` keeps "conceptual knowledge" / "procedural knowledge" only
  where citing Sinha & Kapur directly, with an explicit terminology-bridge
  note at the top of the file.
- Cardinal-vocabulary rule extended to forbid `procedural`, `conceptual` in
  learner-facing text (they're still internal-only terms when used at all).

### Added

- `_migrate_v02_to_v03()` in `db.py` — auto-detects an old `project_concepts`
  CHECK constraint by inspecting `sqlite_master` and rebuilds the table with
  the new values + new CHECK in a transaction. Idempotent. Runs on every
  `connect()`; no-op for fresh and already-migrated DBs.
- 3 migration regression tests (`tests/test_migration.py`): v0.2 DB migrates;
  fresh DB no-op; re-open idempotent.

### Fixed

- **`benkyo-graph-edit` skill docs were out of sync with the CLI**. The body
  said `concept merge` / `concept fork` / `problem merge` were "pending
  implementation" and walked agents through a tedious manual edge-redirect
  procedure, but those commands have existed in the CLI since v0.1.1. The
  skill now invokes the real atomic commands, with explicit notes on
  `--on-conflict` treatment-clash resolution and the deliberate
  fork-copies-edges-but-not-treatments asymmetry. cli-cheatsheet.md and
  nl-to-cli.md updated to match.
- README positioning broadened from "Claude Code plugin" to "Agent Skills
  bundle". The `SKILL.md` files use the open Agent Skills format and are
  portable to any compatible agent.
- **First-class Codex CLI support** via the repo's own plugin marketplace.
  Added `.codex-plugin/plugin.json` (manifest pointing the `skills` field at
  the existing `.claude/skills/` tree, so one tree serves both agents) and
  `.agents/plugins/marketplace.json` (so `codex plugin marketplace add
  youseiushida/benkyo` registers this repo as an installable source). End
  users install with a single `codex plugin marketplace add` plus a TUI
  install — no symlink, no manual copy. Central Codex Plugin Directory
  listing is "coming soon" upstream; until then, the repo-as-marketplace
  flow is the supported path. Behavior in Cursor / VS Code Copilot / Gemini
  CLI still requires the agent-specific install (per their loaders);
  unverified end-to-end.

### Migration notes (for the lone v0.2.0 user)

If you installed v0.2.0 and have a DB at the OS-default location, just
upgrade: `uv tool install --force benkyo`. The next time anything opens the
DB, the migration runs automatically and any existing `procedural` /
`conceptual` rows become `blackbox` / `whitebox`. No manual SQL needed.

The cleanest verification is `benkyo treatment list --project <id>` after
upgrade: values should be `blackbox` / `whitebox` only.

## [0.2.0] - 2026-05-14

Adds a queryable events log so the skills' research-grounded claims —
delayed-JOL verification, hypercorrection re-probing, stability-bias
detection — become realizable across sessions, not just within one. The
session-wrap protocol moves from free-text metadata to structured event
records via a single atomic command.

### Added

- **`events` table** (append-only) with `id` (`e<n>`), `ts`, `project_id`,
  `kind`, `payload_json`, `notes`. The `kind` column is intentionally not
  CHECK-constrained; the MVP set (`session_start`, `session_end`,
  `delayed_jol_recorded`, `hypercorrection_detected`, `treatment_changed`,
  `concept_probed`) is convention, not enforcement. The `notes` column is the
  LLM-flexibility escape hatch for context that doesn't fit a payload schema.
- **`benkyo events`** subcommand (`add`, `get`, `list`, `delete`) with
  `--project`, `--kind`, `--since`, `--until`, `--limit` filters on `list`.
- **`benkyo session end`** — single atomic command that writes one
  `session_end` event plus one `delayed_jol_recorded` event per entry in the
  summary's `delayed_jols` list. All-or-nothing transactionally. Skills use
  this instead of composing `events add` sequences themselves.
- **`benkyo schema`** — JSON tree of every command, subcommand, option, and
  argument. Skills can introspect the live CLI surface at runtime instead of
  relying on hand-maintained cheat sheets staying in sync.
- `PRAGMA busy_timeout = 5000` on every connection.
- 6 new MVP event kinds documented in `repository.KNOWN_EVENT_KINDS`.
- 45 new tests (`tests/test_events.py`, `tests/test_session_end.py`,
  `tests/test_cli/test_events.py`, `tests/test_cli/test_session.py`).

### Changed

- **`benkyo-session-wrap` SKILL.md step 4** rewritten from "append a session
  note to `project.metadata` (free text)" to "persist via
  `benkyo session end --summary-file`". The protocol no longer touches
  `project.metadata` at session boundaries.
- **`benkyo-project-init` SKILL.md "Returning after a long gap"** rewritten to
  recover state from `benkyo events list --kind session_end` and
  `--kind delayed_jol_recorded`, with the explicit "events as prior, never
  as conclusion" rule (foresight bias applies symmetrically to skills reading
  their own past records).
- **`benkyo-tutoring` SKILL.md session-start** now queries
  `delayed_jol_recorded` events for the verification protocol.
  Hypercorrection moments are recorded as `hypercorrection_detected` events
  for cross-session re-probing (in addition to in-session contrastive
  correction).
- **`benkyo-treatment-shift` SKILL.md** commit/release protocols both now
  log a `treatment_changed` event with `{concept_id, from, to}` payload.
- Cardinal vocabulary rule extended in all 5 SKILL.md files: `event`, `log`,
  `record`, `schema`, `JSON`, `metadata`, `session_end`, `delayed_jol`,
  `hypercorrection`, `payload`, `kind` added to the forbidden internal-terms
  list. Internal IDs (`c<n>` / `p<n>` / `prj<n>` / `e<n`) explicitly forbidden
  in learner-facing text.
- `_benkyo-shared/references/cli-cheatsheet.md` — new sections for Events,
  Sessions (high-level atomic), and Schema (runtime introspection).
- `_benkyo-shared/references/nl-to-cli.md` — new section H ("Session
  boundaries and history") mapping learner phrases to event reads/writes,
  with explicit translations of internal event operations. Added a third
  cardinal rule: **events inform expectations, never replace evidence**.
- `_benkyo-shared/references/session-boundaries.md` — rewritten end-to-end to
  use events as the persistence layer. The "What to do without ③ (event log)"
  workaround section removed.
- `_benkyo-shared/references/self-eval-handling.md` — delayed JOL recording
  switched from free-text metadata to the `benkyo session end` summary;
  hypercorrection moments produce `hypercorrection_detected` events.
- README reorganized: "Get started" 3-step flow moved to the top so first-time
  readers see install → drop materials → talk before the why/how detail. Added
  a "See the map" subsection so users can discover `benkyo render` for graph
  visualization. Tagline rewritten.
- All 18 single-turn skill evaluations re-run against the v0.2.0 skills —
  no regression observed, and new protocols (events writing, session end
  atomic, defer-to-project-init for resume) function as designed.

### Fixed

- **Citation precision pass**. All quantitative claims re-checked against
  primary sources. Corrections:
  - **Rhodes & Tauber (2011)**: 0.93 is the meta-analytic Hedges's *g* for
    delayed-vs-immediate JOL accuracy, not a gamma correlation value. Symbol
    "γ = 0.93" was incorrect across 8 places (README + 4 skill / reference
    files); all now read "Hedges's *g* = 0.93".
  - **Sinha & Kapur (2021) "β = 0.27–0.28 for instruction building"**: the
    β coefficients of 0.27 and 0.28 actually belong to *multiple-RSM
    generation* and *group work*; "instruction building on student solutions"
    has a near-zero regression β once correlated predictors are controlled.
    Replaced with the cleaner subgroup contrast: PS-I with instruction-building
    *g* = 0.56 vs without *g* = 0.20 (Table 3, subgroup *p* = .02).
  - **"g = 0.36–0.87" range form**: 0.36 is the main meta-analytic estimate
    [95% CI 0.20, 0.51], 0.87 is a p-curve-based alternative from a different
    estimator. They are not the bounds of an interval. Egger's test and
    trim-and-fill detected no funnel-plot asymmetry. The range form has been
    removed; the two estimates are now reported separately with their methods.
  - **Kalyuga (2007) "r = 0.92 with full tests, 4.9x time reduction"**: the
    primary source says "correlations *up to* .92" and "time reductions *up
    to* 4.9". The "up to" qualifier has been restored.
  - **Bertsch et al. (2007) "Lists > 50: effect disappears"**: the actual
    moderator estimate is *d* = 0.09, 95% CI [0.07, 0.11] — small but still
    significantly positive. Updated to "shrinks to *d* = 0.09".
  - **decision-tables.md** Bertsch / Sinha-&-Kapur entries refactored to use
    the corrected numbers and to make the I-PS/PS-I logic explicit.

### Scope decision

**Probabilistic learner modeling (BKT, DKT, etc.) is explicitly out of scope
for benkyo.** benkyo provides structured memory and a behavioral playbook; it
does not compute `P(mastered)`. Skills query the events log with simple
heuristics. If you want a probabilistic model or a forgetting-curve scheduler
(FSRS-style), build it as a separate layer on top of the events log — that
is the right boundary.

## [0.1.1] - 2026-05-14

First public release. CLI + 5 Claude Code skills, plugin marketplace manifest,
README with research-foundation citations, MIT license.

### Added

- 5 Claude Code skills under `.claude/skills/` (`benkyo-project-init`,
  `benkyo-tutoring`, `benkyo-treatment-shift`, `benkyo-graph-edit`,
  `benkyo-session-wrap`), each with `SKILL.md`, `evals/evals.json`, and
  `evals/trigger-eval.json`.
- Shared reference library at `.claude/skills/_benkyo-shared/references/`
  (CLI cheatsheet, natural-language ↔ internal vocab map, decision tables,
  granularity guide, lost-learner handling, self-eval handling, session
  boundaries, literature pointers).
- `.claude-plugin/marketplace.json` so the skills can be installed via
  `/plugin marketplace add youseiushida/benkyo`.
- README with installation, quick start, architecture overview, research
  foundation table, and APA-formatted references for the 9 cited papers.
- `concept merge`, `concept fork`, `problem merge` commands and underlying
  repository operations, with conflict resolution flags.
- Regression tests for Japanese content handling on Windows (`tests/test_encoding.py`).
- Cardinal vocabulary rule extension: internal IDs (`c1`, `p1`, `prj1`)
  explicitly forbidden in learner-facing text.
- Session-wrap skill: "defer to project-init" shortcut for resume scenarios
  ("久しぶり" / "ようやく続き始めるかー" / "何やってたっけ").
- pyproject.toml metadata: classifiers, keywords, project URLs.

### Changed

- CLI surface and treatment values fully converted to English
  (`procedural` / `conceptual` values; `prereq` / `related` edge types; all
  command help text). Internal terms remain English; the cardinal-vocabulary
  rule in the skills translates them to natural Japanese for the learner.
- Forced UTF-8 stdout/stderr in `cli.py` to handle Windows cp932 encoding
  failures when CLI output contains Japanese characters.

### Fixed

- `benkyo treatment-shift/evals/evals.json` eval-3 expected_output: "収束級数"
  (series convergence) corrected to "広義積分の収束判定" (improper-integral
  convergence test), which is what `c1`'s content actually requires.

## [0.1.0] - 2026-05-14

Initial private release of the CLI core.

### Added

- SQLite-backed schema: `concept_nodes`, `problem_nodes`, `edges`,
  `projects`, `project_goals`, `project_concepts`, `id_counters`.
- ID convention: `c<n>` for concepts, `p<n>` for problems, `prj<n>` for
  projects.
- Commands: `concept`, `problem`, `edge`, `project`, `treatment`, `breakdown`,
  `window`, `frontier`, `ancestors`, `render`, `import`, `export`, `info`.
- Per-`(project, concept)` procedural/conceptual treatment with default
  fallback to `conceptual` when unset.
- Window traversal: BFS from goal problems via prereq edges, with procedural
  concepts terminating descent.
- `--db` flag and `BENKYO_DB` environment variable for DB path override.
- platformdirs-based default DB location (OS-appropriate app data dir).

[Unreleased]: https://github.com/youseiushida/benkyo/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/youseiushida/benkyo/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/youseiushida/benkyo/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/youseiushida/benkyo/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/youseiushida/benkyo/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/youseiushida/benkyo/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/youseiushida/benkyo/releases/tag/v0.1.0
