# benkyo

[![PyPI](https://img.shields.io/pypi/v/benkyo.svg)](https://pypi.org/project/benkyo/)
[![Python](https://img.shields.io/pypi/pyversions/benkyo.svg)](https://pypi.org/project/benkyo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A research-grounded tutor that defers to you, not to its training data.**

A Python CLI plus a SKILL.md bundle that turn an AI coding agent — Claude Code today, OpenAI Codex CLI with one symlink, anything else that consumes the open [Agent Skills](https://agentskills.io/) format — into a tutor with persistent memory. The agent tracks, per project, which concepts you want to truly understand and which you've decided to just use as a tool. Each operational rule cites the cognitive science it's built on.

**Status**: β. CLI in English. SKILL.md files are in English with Japanese-first natural-language examples (the agent adapts to the learner's language at runtime; English / other-language end-to-end use works in principle but is not yet evaluated). First-class plugin support is for Claude Code; Codex CLI works via manual install (see below).

> **Terminology.** A *project* in benkyo is a **learning unit** — one subject (e.g., Laplace transforms) bundled with the goal problems that anchor it and the per-concept treatment decisions for that subject. Each concept has a per-project **treatment**: *whitebox* (understand the why, including derivations) or *blackbox* (use as a tool, formula in / answer out). The cardinal-vocabulary rule in the skills (see `.claude/skills/`) translates these into the learner's natural language — the internal terms never appear in tutor speech. The current example translations are Japanese-first.
>
> **Note on the math-education literature**: papers we cite (Sinha & Kapur 2021; Hiebert & Lefevre 1986) call these *conceptual* and *procedural* knowledge respectively. benkyo renamed in v0.3.0 to avoid the unrelated ACT-R use of "procedural" (= automated expert knowledge), which is the opposite axis from what those papers mean. The mapping is one-to-one: paper's "conceptual" = benkyo's "whitebox"; paper's "procedural" = benkyo's "blackbox".

## Get started

### 1. Install the CLI and the skills

The Python CLI is the same for every agent:

```bash
uv tool install benkyo            # or: pipx install benkyo
benkyo --version                  # confirm it's on PATH
```

Then install the skills for your agent of choice:

**Claude Code** (first-class plugin support):

```bash
/plugin marketplace add youseiushida/benkyo
/plugin install benkyo
```

Restart Claude Code; the 5 skills appear in `/help`.

**OpenAI Codex CLI** (first-class plugin marketplace; the repo ships `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`):

```bash
codex plugin marketplace add youseiushida/benkyo
# Then in the Codex TUI: open the plugin directory, find "benkyo", install.
```

The same `SKILL.md` files are picked up by both agents (the repo carries `.claude-plugin/marketplace.json` for Claude Code and `.codex-plugin/plugin.json` for Codex, both pointing at the shared `.claude/skills/` tree — they coexist without conflict). Codex's central Plugin Directory listing is coming soon; until then, `codex plugin marketplace add` from this repo is the supported flow.

**Other SKILL.md-compatible agents** (Cursor, VS Code Copilot, Gemini CLI, ...): the frontmatter and body are agent-neutral. Point your agent's skill loader at `.claude/skills/benkyo-*` (or copy/symlink them into its skills directory). The bundle uses the open Agent Skills format.

### 2. Hand your materials to Claude Code (or Codex CLI, or any agentic CLI)

Drop your study materials — past exams, the textbook PDF, the syllabus, lecture notes — into the directory you launch Claude Code from. Then just describe what you want:

```
You: I have the past 5 years of finals for ECE 220 (signals & systems), the
     textbook PDF, and the syllabus. The exam is in 12 days. Help me prep.
```

`benkyo-project-init` reads the materials, extracts the concept set and dependencies from how the textbook structures them, turns past-exam problems into the project's goal problems, proposes which concepts to treat as "use the formula" vs "really understand," asks you to confirm, and hands off to `benkyo-tutoring` for the first activity.

This works for any STEM domain where the curriculum is structured and past problems exist: classical mechanics, organic chemistry, algorithms, statistics, fluid dynamics, ML theory, and so on.

#### See the map (at any point)

Before you commit time, or whenever you want to step back during a session, ask Claude:

```
You: Show me the map.        /  全体見せて
You: What does the plan look like?
You: Where am I in this?
```

Claude will render the current concept graph via `benkyo render --format mermaid` — problems as stadium shapes, "really understand" concepts as rectangles, "use as a tool" concepts as cylinders. Mermaid renders inline on GitHub, in Claude Code's chat, and in any markdown-aware viewer.

You can also drive it yourself:

```bash
benkyo render --project prj1 --format mermaid > graph.md
benkyo render --project prj1 --format dot | dot -Tpng > graph.png
```

This is how you verify Claude actually understood your materials — and how you keep the bird's-eye view of what you've decided to learn vs what you've decided to just use.

### 3. Just keep talking

The 5 skills auto-trigger from what you say or what you do. You never type `benkyo` yourself; Claude does it on your behalf.

- "I don't get this" → `benkyo-tutoring` drops into a one-level breakdown of the concept, then climbs back up
- "I want to really understand X" → `benkyo-treatment-shift` commits the concept, makes sure the prerequisites exist as nodes, and switches to Problem-Solving-then-Instruction mode
- "Just give me the formula" → `benkyo-treatment-shift` releases it back to blackbox with a reference table
- "Add convolution to the graph" → `benkyo-graph-edit` runs an identity check, then adds the node and edges
- "I'm done for today" → `benkyo-session-wrap` recaps, captures a delayed JOL, and atomically persists the session so next time picks up cleanly

## Concept

Two pieces that depend on each other:

1. **`benkyo` CLI** — a small Python tool (Click + SQLite + platformdirs) that owns a global concept-dependency graph plus, per project, the blackbox/whitebox treatment of each concept, the goal problems, an append-only events log (delayed JOL, hypercorrection, treatment changes, session boundaries), and free-text project metadata.
2. **5 Agent Skills** — operational playbooks (`SKILL.md` files under `.claude/skills/`) that tell the agent when and how to drive the CLI on the learner's behalf. The learner converses naturally; the agent translates intents into CLI ops and applies decision rules drawn from published meta-analyses. The files use the open Agent Skills format, so they work in any compatible agent (Claude Code natively, Codex CLI / Cursor / Gemini CLI / VS Code Copilot via the manual install above).

The learner never types `benkyo` themselves.

## Why

Naive LLM tutors fail in characteristic ways that the educational psychology literature has named and measured:

- They trust the learner's "got it" too quickly (foresight bias / hindsight bias; Bjork, Dunlosky & Kornell, 2013).
- They jump to explanation instead of letting the learner attempt first (loses generation effect d ≈ 0.40; Bertsch et al., 2007), and they jump to instruction before problem-solving (loses Productive Failure for conceptual knowledge: g = 0.36, 95% CI [0.20, 0.51]; Sinha & Kapur, 2021).
- They keep scaffolding when the learner has become fluent (expertise reversal; Kalyuga, 2007).
- They lose track of which concepts the learner actually said they remembered between sessions (no delayed JOL; Rhodes & Tauber, 2011, report a large meta-analytic advantage of delayed over immediate JOL gamma-correlation accuracy, Hedges's g = 0.93 across 112 effect sizes).
- They frame practice as a test, halving its effect (Bertsch et al., 2007: incidental d = 0.65 vs intentional d = 0.32).
- They miss the strongest teaching moments: high-confidence wrong answers (hypercorrection; Butterfield & Metcalfe, 2001).

benkyo addresses these by making the *structural* parts persistent (the CLI) and the *behavioral* parts explicit (the skills, with literature pointers next to each rule). The tutor's job is then to follow the skills, not improvise.

## Skill bundle

| Skill | Triggers on | What it does |
|---|---|---|
| `benkyo-project-init` | "○○を勉強したい" / "I want to study X", new subject, materials shared, post-long-gap resume | Extracts goal, drafts initial graph, sets the initial blackbox/whitebox cut |
| `benkyo-tutoring` | Mid-session activity ("分からない" / "I don't get it", "教えて" / "explain", "次" / "next", "分かった" / "got it") | The default in-session behavior: PS-I vs I-PS mode choice, breakdown protocol, self-eval handling |
| `benkyo-treatment-shift` | "ちゃんと理解したい" / "I want to really understand" (commit), "公式で OK" / "just memorize the formula" (release), or detected fatigue / transfer-failure signals | Changes a concept's depth-of-engagement; ensures prereqs exist before committing |
| `benkyo-graph-edit` | "これも追加" / "add this too", "これ別物" / "this is different", or a concept the learner mentions that isn't in the graph yet | Adds nodes/edges with an identity check; granularity decisions |
| `benkyo-session-wrap` | "終わり" / "I'm done", "また明日" / "let's continue tomorrow", abrupt interruption | Recap, delayed JOL seed, atomic persistence via `benkyo session end` |

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
- `project_concepts` — per-project treatment (`blackbox` / `whitebox` / unset → default whitebox)
- `events` (`e1`, …) — append-only log of state changes (`session_start`, `session_end`, `delayed_jol_recorded`, `hypercorrection_detected`, `treatment_changed`, `concept_probed`) with a free-text `notes` column for context that doesn't fit a payload schema

The "window" of a project is computed by BFS from goal problems via prereq edges; concepts marked blackbox terminate traversal (they bound the depth the tutor needs to teach).

The full CLI surface is documented at `.claude/skills/_benkyo-shared/references/cli-cheatsheet.md` — or just run `benkyo --help` / `benkyo schema`.

## Research foundation

Each operational rule in the skills is backed by a published effect. The table below summarises; the literature pointer file (`.claude/skills/_benkyo-shared/references/literature-pointers.md`) gives the per-decision mapping.

| Operational rule | Primary source |
|---|---|
| Default PS-I for whitebox concepts; default I-PS for blackbox | Sinha & Kapur (2021) |
| Build instruction on the learner's own attempt, not on the canonical solution | Sinha & Kapur (2021): PS-I with instruction-building g = 0.56 vs without g = 0.20 (subgroup p = .02) |
| Reduce scaffolding as the learner becomes fluent | Kalyuga (2007), expertise reversal |
| Rapid first-step diagnostic instead of long pre-tests | Kalyuga (2007), correlations up to r = 0.92 with full tests |
| Solicit a delayed JOL at session end; verify at next session start | Rhodes & Tauber (2011), Hedges's g = 0.93 for delayed-over-immediate gamma correlations |
| Brief anticipation before showing a worked example | Bjork et al. (2013); Kornell et al. (2009) |
| Frame probes incidentally — never say "test" | Bertsch et al. (2007), d = 0.65 vs 0.32 |
| Interleave related concepts within a session, not across days | Brunmair & Richter (2019) |
| Explicit contrasting correction for high-confidence wrong answers | Butterfield & Metcalfe (2001), hypercorrection |
| 1–6 day retention interval for probe scheduling | Adesope et al. (2017), g = 0.82 peak |
| Match probe format to intended use (TAP) | Adesope et al. (2017), g = 0.63 vs 0.53 |
| Treat learner self-evaluation as low-trust evidence | Bjork et al. (2013), 3 biases |

## Limitations

- **No probabilistic learner model**: benkyo deliberately stops at "events are queryable." It does **not** compute `P(mastered)` (BKT) or schedule reviews by a forgetting model (FSRS). Skills query the events log with simple heuristics. If you want a model, build it as a separate layer on top of the events log — that's the right boundary.
- **Self-managed scheduling**: spacing recommendations come from session-wrap and project-init heuristics, not from a per-card forgetting model. The 1–6 day Adesope window is a hint to the learner, not a queue.
- **Japanese-first natural-language layer (skills are language-neutral in principle)**: the `SKILL.md` files themselves are written in English (so any agent can read the instructions), but the cardinal-vocabulary translation examples, the eval prompts, and the trigger phrases listed in the skill descriptions are Japanese-first. Claude / Codex adapt to the learner's language at runtime, so English-speaking learners can use benkyo today — the agent will translate internal terms into natural English on the fly — but only Japanese end-to-end behavior has been evaluated. Localized example sets are a welcome contribution.
- **Two-layer brittleness**: if the CLI changes its surface and the skill's cheat-sheet isn't updated, the skill's `benkyo` invocations will fail. Run the test suite + the skill evals together on changes. `benkyo schema` lets skills introspect the live CLI shape.
- **Cross-agent behavior unverified end-to-end**: the 18 single-turn evals were re-run only in Claude Code. The Codex CLI install path (`codex plugin marketplace add` against this repo) is wired up via `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` but has not been load-tested in a real Codex session. Cursor / Gemini / VS Code Copilot work in principle (the SKILL.md format is portable) but are also unverified. PRs confirming or fixing cross-agent behavior welcome.

## Development

```bash
uv sync --dev
uv run pytest                       # 182 tests
benkyo --help
benkyo schema                       # JSON tree of the full CLI surface
```

Skill files live at `.claude/skills/benkyo-*/SKILL.md`. Each skill has `evals/evals.json` (3 single-turn scenarios) and `evals/trigger-eval.json` (16 trigger discrimination cases) — see `_benkyo-shared/evals/TRIGGER-OPTIMIZATION.md` if you want to run `example-skills:skill-creator`'s `run_loop.py` against them.

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

## License

MIT. See `LICENSE`.

The works cited in *References* belong to their respective authors and publishers. Cite the originals when reusing any quantitative claim.
