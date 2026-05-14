# benkyo

**Problem-driven learning support, grounded in the educational psychology literature.**

A small Python CLI plus a bundle of Claude Code skills that together turn Claude into a research-grounded tutor — one that defers to the learner, calibrates against bias, and tracks a per-project map of "what to really understand" vs "what to just use as a tool."

**Status**: β. The CLI is English; the skills are currently Japanese-first.

## What it is

Two pieces that depend on each other:

1. **`benkyo` CLI** — A Python tool (Click + SQLite + platformdirs) that owns a global concept-dependency graph and stores, per project, whether each concept is being treated *procedurally* (use as a formula) or *conceptually* (understand the why). It also stores problems, prereq/related edges, project goals, and free-text session metadata.
2. **5 Claude Code skills** — Operational playbooks (under `.claude/skills/`) that tell Claude when and how to drive the CLI on the learner's behalf. The learner converses naturally; Claude translates intents into CLI ops and applies decision rules drawn from published meta-analyses.

The learner never types `benkyo` themselves. They talk to Claude.

## Why

Naive LLM tutors fail in characteristic ways that the educational psychology literature has named and measured:

- They trust the learner's "got it" too quickly (foresight bias / hindsight bias; Bjork, Dunlosky & Kornell, 2013).
- They jump to explanation instead of letting the learner attempt first (loses generation effect d ≈ 0.40; Bertsch et al., 2007), and they jump to instruction before problem-solving (loses Productive Failure g = 0.36–0.87 for conceptual; Sinha & Kapur, 2021).
- They keep scaffolding when the learner has become fluent (expertise reversal; Kalyuga, 2007).
- They lose track of which concepts the learner actually said they remembered between sessions (no delayed JOL; Rhodes & Tauber, 2011 report γ ≈ 0.93 for delayed vs much lower for immediate).
- They frame practice as a test, halving its effect (Bertsch et al., 2007: incidental d = 0.65 vs intentional d = 0.32).
- They miss the strongest teaching moments: high-confidence wrong answers (hypercorrection; Butterfield & Metcalfe, 2001).

benkyo addresses these by making the *structural* parts persistent (the CLI) and the *behavioral* parts explicit (the skills, with literature pointers next to each rule). The tutor's job is then to follow the skills, not improvise.

## Install

### 1. Install the CLI

```bash
uv tool install benkyo
```

(or `pipx install benkyo`)

Verify:

```bash
benkyo --version
benkyo info
```

The DB lives at the OS-default app data location (override with `BENKYO_DB` or `--db`).

### 2. Install the Claude Code plugin

```bash
/plugin marketplace add YoseiUshida/benkyo
/plugin install benkyo
```

This installs all 5 skills. Restart Claude Code; the skills should appear in `/help` and in the `Skill` tool's options.

## Quick start

Open Claude Code in a fresh directory and just talk:

```
You: ラプラス変換を勉強したい、何から始めれば？
```

Claude (via `benkyo-project-init`) will: ask 3–4 concrete goals to choose from, run a brief diagnostic, draft an initial concept graph, persist it via `benkyo project add` / `benkyo concept add` / etc., and hand off to `benkyo-tutoring` for the actual session.

From there, the learner just keeps talking. The 5 skills auto-trigger by trigger phrase / situation; the right one fires for the situation (see *Skill bundle* below).

## Skill bundle

| Skill | Triggers on | What it does |
|---|---|---|
| `benkyo-project-init` | "○○を勉強したい", new subject, materials shared, post-long-gap resume | Extracts goal, drafts initial graph, sets the initial procedural/conceptual cut |
| `benkyo-tutoring` | Mid-session activity ("分からない", "教えて", "次", "分かった") | The default in-session behavior: PS-I vs I-PS mode choice, breakdown protocol, self-eval handling |
| `benkyo-treatment-shift` | "ちゃんと理解したい" (commit), "公式で OK" (release), or detected fatigue/transfer-failure signals | Changes a concept's depth-of-engagement; ensures prereqs exist before committing |
| `benkyo-graph-edit` | "これも追加" / "これ別物" / mentioned concept not in graph yet | Adds nodes/edges with identity check; granularity decisions |
| `benkyo-session-wrap` | "終わり", "また明日", abrupt interruption | Recap, delayed JOL seed, persist state to `project.metadata` |

Each `SKILL.md` references a shared library at `.claude/skills/_benkyo-shared/references/` for decision tables, the natural-language ↔ internal-vocab map, and literature pointers. (Files prefixed with `_` are not loaded as skills by Claude Code, so the bundle stays clean.)

## Architecture

```
Learner (natural language)
        ↓ ↑
Claude Code  ← skill auto-trigger by description
        ↓ ↑
    SKILL.md  → references/ (decision tables, nl-to-cli map, lit pointers)
        ↓
   benkyo CLI (read/write)
        ↓
   SQLite DB
```

Domain model in the DB (simplified):

- `concept_nodes` (`c1`, `c2`, …) — global, shared across projects
- `problem_nodes` (`p1`, `p2`, …) — also global
- `edges` — `prereq` or `related`, between nodes
- `projects` (`prj1`, …) — owns goal problems, treatments, free-text metadata
- `project_concepts` — per-project treatment (`procedural` / `conceptual` / unset → default conceptual)

The "window" of a project is computed by BFS from goal problems via prereq edges; concepts marked procedural terminate traversal (they bound the depth the tutor needs to teach).

The full CLI surface is documented at `.claude/skills/_benkyo-shared/references/cli-cheatsheet.md` — or just run `benkyo --help`.

## Research foundation

Each operational rule in the skills is backed by a published effect. The table below summarises; the literature pointer file (`.claude/skills/_benkyo-shared/references/literature-pointers.md`) gives the per-decision mapping.

| Operational rule | Primary source |
|---|---|
| Default PS-I for conceptual concepts; default I-PS for procedural | Sinha & Kapur (2021) |
| Build instruction on the learner's own attempt, not on the canonical solution | Sinha & Kapur (2021), β = 0.27–0.28 |
| Reduce scaffolding as the learner becomes fluent | Kalyuga (2007), expertise reversal |
| Rapid first-step diagnostic instead of long pre-tests | Kalyuga (2007), r = 0.92 with full tests |
| Solicit a delayed JOL at session end; verify at next session start | Rhodes & Tauber (2011), γ = 0.93 delayed |
| Brief anticipation before showing a worked example | Bjork et al. (2013); Kornell et al. (2009) |
| Frame probes incidentally — never say "test" | Bertsch et al. (2007), d = 0.65 vs 0.32 |
| Interleave related concepts within a session, not across days | Brunmair & Richter (2019) |
| Explicit contrasting correction for high-confidence wrong answers | Butterfield & Metcalfe (2001), hypercorrection |
| 1–6 day retention interval for probe scheduling | Adesope et al. (2017), g = 0.82 peak |
| Match probe format to intended use (TAP) | Adesope et al. (2017), g = 0.63 vs 0.53 |
| Treat learner self-evaluation as low-trust evidence | Bjork et al. (2013), 3 biases |

## References

Adesope, O. O., Trevisan, D. A., & Sundararajan, N. (2017). Rethinking the use of tests: A meta-analysis of practice testing. *Review of Educational Research*, *87*(3), 659–701. <https://doi.org/10.3102/0034654316689306>

Bertsch, S., Pesta, B. J., Wiscott, R., & McDaniel, M. A. (2007). The generation effect: A meta-analytic review. *Memory & Cognition*, *35*(2), 201–210. <https://doi.org/10.3758/BF03193441>

Bjork, R. A., & Bjork, E. L. (1992). A new theory of disuse and an old theory of stimulus fluctuation. In A. F. Healy, S. M. Kosslyn, & R. M. Shiffrin (Eds.), *From learning processes to cognitive processes: Essays in honor of William K. Estes* (Vol. 2, pp. 35–67). Erlbaum.

Bjork, R. A., Dunlosky, J., & Kornell, N. (2013). Self-regulated learning: Beliefs, techniques, and illusions. *Annual Review of Psychology*, *64*, 417–444. <https://doi.org/10.1146/annurev-psych-113011-143823>

Brunmair, M., & Richter, T. (2019). Similarity matters: A meta-analysis of interleaved learning and its moderators. *Psychological Bulletin*, *145*(11), 1029–1052. <https://doi.org/10.1037/bul0000209>

Butterfield, B., & Metcalfe, J. (2001). Errors committed with high confidence are hypercorrected. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, *27*(6), 1491–1494. <https://doi.org/10.1037/0278-7393.27.6.1491>

Kalyuga, S. (2007). Expertise reversal effect and its implications for learner-tailored instruction. *Educational Psychology Review*, *19*(4), 509–539. <https://doi.org/10.1007/s10648-007-9054-3>

Murre, J. M. J., & Dros, J. (2015). Replication and analysis of Ebbinghaus' forgetting curve. *PLOS ONE*, *10*(7), e0120644. <https://doi.org/10.1371/journal.pone.0120644>

Rhodes, M. G., & Tauber, S. K. (2011). The influence of delaying judgments of learning on metacognitive accuracy: A meta-analytic review. *Psychological Bulletin*, *137*(1), 131–148. <https://doi.org/10.1037/a0021705>

Sinha, T., & Kapur, M. (2021). When problem solving followed by instruction works: Evidence for productive failure. *Review of Educational Research*, *91*(5), 761–798. <https://doi.org/10.3102/00346543211019105>

## Limitations

- **Self-managed scheduling**: benkyo doesn't yet implement a spaced-retrieval scheduler (FSRS-style). Spacing recommendations come from session-wrap and project-init heuristics, not from a per-card forgetting model.
- **No event log**: per-event history isn't persisted; state lives in `project.metadata` as free text. The session-wrap skill writes structured notes there, but they're not queryable as events.
- **Japanese-first skills**: the SKILL.md files and decision tables are currently written in Japanese (the primary user language). The CLI itself is English.
- **Two-layer brittleness**: if the CLI changes its surface and the skill's cheat-sheet isn't updated, the skill's `benkyo` invocations will fail. Run the test suite + the skill evals together on changes.

## Development

```bash
uv sync --dev
uv run pytest                       # 134 tests
benkyo --help
```

Skill files live at `.claude/skills/benkyo-*/SKILL.md`. Each skill has `evals/evals.json` (3 single-turn scenarios) and `evals/trigger-eval.json` (16 trigger discrimination cases) — see `_benkyo-shared/evals/TRIGGER-OPTIMIZATION.md` if you want to run `example-skills:skill-creator`'s `run_loop.py` against them.

## License

MIT. See `LICENSE`.

The works cited in *References* belong to their respective authors and publishers. Cite the originals when reusing any quantitative claim.
