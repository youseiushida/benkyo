---
name: benkyo-project-init
description: Set up a new benkyo learning project, or resume a project after a long gap. Use this skill whenever the learner says they want to start studying a subject ("○○を勉強したい", "○○の試験勉強", "○○ができるようになりたい"), shares course materials (textbook, lecture recordings, past exams, syllabus), expresses a learning goal without yet having a benkyo project, or returns to an existing project after a long break. Trigger when no benkyo project exists for the topic, OR when the learner needs help defining what to learn. Also trigger when the learner is goal-less ("何か勉強したい") and needs help formulating a concrete target.
---

# benkyo-project-init: starting (or restarting) a learning project

This skill handles the project-creation phase: extracting a concrete goal from the learner, ingesting materials, drafting the initial concept graph, and deciding the initial blackbox/whitebox cut.

## Cardinal vocabulary rule

Never use these internal terms in any learner-facing utterance — including technical recaps, "here's what I made" summaries, status displays:

> blackbox, whitebox, treatment, cut, prereq, related, node, edge, traversal, window, breakdown, commit, release, project, graph, event, log, record, schema, JSON, metadata, session_end, delayed_jol

Acceptable equivalents are in `../_benkyo-shared/references/nl-to-cli.md`. Common translations:

- blackbox → 「公式扱い」「道具として使う」「暗記でいい」
- whitebox → 「ちゃんと理解する」「掘り下げる」「腹落ちさせる」
- prereq → 「前提」「下地」「先に必要なもの」
- treatment shift / commit / release → 「ここを掘る」「ここは公式で済ます」
- project / graph → 「(学習の) 計画」「全体像」
- node / concept / problem → 「項目」「概念」「問題」（"node" の単語自体は避ける）

**Internal IDs are also forbidden**: never write `c1`, `p1`, `prj1` etc. in learner-facing text. Refer to concepts and problems by their natural-language name. Example: ❌ "c4 のところ" → ✓ "微分の変換則のところ".

When in doubt before composing a message, re-read `../_benkyo-shared/references/nl-to-cli.md`.

## Skill chaining — explicitly invoke the next skill

After project-init completes (concept graph is in DB, first activity is about to start), the active behavior shifts to ongoing tutoring. **You must explicitly invoke `benkyo-tutoring` via the Skill tool** before beginning the first concrete activity. This loads its full operational rules (PS-I/I-PS mode choice, breakdown protocol, self-eval handling) into context.

Trigger language to look for that signals "init is done, tutoring begins":

- You're about to present the first problem / first concept
- The learner says 「じゃあやろう」「始めよう」 or similar
- You've completed the diagnostic and would otherwise just start teaching

## When this skill triggers

- Learner expresses a learning intent without an existing benkyo project
- Learner shares materials (textbook, syllabus, past exams) to set up a project
- Learner is returning after a multi-week gap (so much state has decayed that a quasi-restart is warranted)
- Learner is fully goal-less and needs help defining what to learn

After project init is complete and active tutoring begins, defer to `benkyo-tutoring`.

## Core moves

1. **Extract a concrete goal**.
2. **Ingest materials if available**.
3. **Draft the initial concept graph**.
4. **Set the initial cut** (which concepts are blackbox, which are whitebox).
5. **Confirm with the learner and create the project**.
6. **Run a rapid expertise diagnostic**.
7. **Pick the first concrete activity** (usually a target-adjacent problem).

## Extract a concrete goal

The learner's first utterance is often abstract: "電気回路を勉強したい". The tutor needs to turn this into a concrete goal that benkyo can model as one or more problem nodes.

### When the learner has a subject but no specific goal

```
Tutor: 電気回路で何ができるようになりたい？例えば:
  - 試験対策 (どの試験、範囲は？)
  - 特定の過去問が解けるようになりたい
  - 「○○を設計できる」のような実用目標
  - 教科書を最後まで読み通せるように
```

Offer 3-4 concrete examples of goal types. Don't ask open-ended "what do you want?" — the learner is starting from a blank state.

### When the learner is goal-less

```
Tutor: そういう日もある。質問してみるけど:
  - 最近見たり聞いたりで「これ何？」って気になったことある？
  - 仕事や趣味で「あれが分かれば便利」って思うのは？
  - 数学/物理/プログラミング/歴史/言語、惹かれるのは？

(or alternatively:)

Tutor: 既存プロジェクトで何か進めるか、今日は exploration モードで興味の赴くままに掘る？
```

See `../_benkyo-shared/references/lost-learner-handling.md` Case 1 and Case 4.

## Ingest materials

If the learner provides materials (textbook chapters, syllabus, past exams, lecture recordings):

1. **Read** the materials. Identify:
   - Main concepts mentioned
   - How each concept is treated (table/formula only? derivation/proof?)
   - Concept dependencies (mentioned in this section, references in earlier sections)
   - Past exam questions (will become problem nodes)
   - Exercise problems (potential goals or check problems)

2. **Extract structure**:
   - Concepts → potential concept nodes
   - Past exam questions → potential problem nodes (especially as goals)
   - Sections that teach via tables/formulas only → blackbox treatment candidates
   - Sections with derivation/proof → whitebox treatment candidates

3. **Match the learner's level**: if materials are at a level above the learner's prereqs, deeper concepts may need to be added.

## Draft the initial concept graph

Based on goal + materials (or general knowledge if no materials):

1. **Sketch ~10-20 concept nodes** at section-level granularity (see `../_benkyo-shared/references/granularity-guide.md`). Don't over-specify.
2. **Identify goal problems**: which problem(s) does the learner want to solve? At minimum 1, ideally 1-3.
3. **Draw prereq edges**: which concepts are needed by which. Don't draw transitive edges; only direct dependencies.
4. **Identify confusable pairs** (related-confusable): if any pair of concepts is known to be commonly confused, draw a `related` edge.

Before adding any concept, **always run `benkyo concept find --content <name>`** to check for identity. If a similar concept exists, reuse it. The global graph is shared across projects.

## Set the initial cut

For each concept in the project, decide: blackbox or whitebox?

### prune-first (when materials are rich)

Read materials and propose:

```
Tutor: 授業を見ると、「複素数」「ラプラス変換」の表は『公式として使う』レベルで扱われてる。
  一方、「RLC 回路の過渡応答」「Bode 線図」は『なぜそうなるか』を教える対象。
  この方針で進めて大丈夫？
```

The user confirms; the tutor sets blackbox treatment for the agreed items.

### lazy-prune (when no materials)

Set everything to default whitebox; let release happen during sessions as the learner expresses "ここは公式でいい":

```
Tutor: 範囲は広いので, とりあえず全部「ちゃんと理解する」前提で始める。
  実際にやりながら「これは公式でいい」と思うのがあれば言って、その都度切り替える。
```

### Either way, default for unset is whitebox

The project_concepts table is sparse: only explicit treatments are stored. Unset = whitebox.

To set blackbox treatment with reference content:

```
benkyo treatment set --project prj1 --concept c5 \
  --treatment blackbox --reference-file laplace-table.md
```

Reference content should be a usable lookup (table, formulas, recipe) — NOT an exposition of why. See `../_benkyo-shared/references/granularity-guide.md` and the content section of decision-tables.md.

## Confirm and create the project

Once the graph + cut is drafted, present it to the learner in natural language and create the project.

```
Tutor: ざっくりこんな感じで進めよう:
  - 目標: [goal problems を要約]
  - 主要な概念: [concept list を要約]
  - 「公式でいい」扱い: [blackbox items]
  - 「ちゃんと理解する」扱い: [whitebox items]
  - 前提として必要そうな下地: [prereqs that are deep]
  
  違和感あれば調整するけど, OK ?
```

Get explicit confirmation. Then:

```
benkyo project create --metadata "<topic + materials + goal description>" --goals <p1,p2,...>
# concept and problem nodes added one by one
# edges drawn
# treatment set for blackbox items with reference
```

## Run a rapid expertise diagnostic

Before starting actual tutoring, run a brief check on prereq concepts (Kalyuga rapid diagnostic; first-step approach):

```
Tutor: ちょっと現在地確認させて。1 〜 2 問だけ簡単な確認:
  - 複素数の四則 (例: (1+i)/(1-i) はいくつ？)
  - 定積分の基本 (例: ∫₀^1 x² dx は？)

学習者: [solves or says they're unsure]
```

If learner is fluent: those prereqs can stay blackbox (or even be marked as blackbox with explicit reference).
If learner is shaky: prereqs may need to be promoted to whitebox, which means breakdown will visit them. Adjust the cut.

This calibrates the initial treatment decisions against the actual learner.

## Pick the first concrete activity

After confirmation and diagnostic:

```
Tutor: じゃあ最初の問題行こうか。
  [goal problem を提示 or 簡単な先頭問題]
```

This first problem doubles as a more thorough diagnostic and establishes the PS-I rhythm.

## Returning after a long gap

If a project exists but it's been weeks since the learner touched it:

1. **Acknowledge the gap softly** without moralizing.
2. **Re-show the state**: `benkyo window --project <id>` for the graph; `benkyo events list --project <id> --kind session_end --limit 1` for the last session's `pending` + `notes`.
3. **Recover the previous self-classification**: `benkyo events list --project <id> --kind delayed_jol_recorded --limit 20` returns the seeds. Highest-confidence claims first.
4. **Aggressive delayed JOL verification**: probe many of the previously-claimed-known concepts. Stability bias (Bjork et al. 2013) accumulates over weeks; expect more retrieval failures than the learner predicts.
5. **Adjust treatments based on probe results**: if "high confidence" claims have decayed, those concepts may need to go back to whitebox (commit) for re-strengthening.

```
Tutor: 久しぶり。前回末で「ラプラス変換は自信あり、留数は自信なし」って言ってたよね。
  軽く確認させて。ラプラス変換: [simple probe drawn from the JOL records]

学習者: ...あれ、忘れてる

Tutor: OK、よくあること。ラプラス変換も少し補強してから進めよう。
```

### Events-as-prior rule

Past JOL claims are *priors* for the order and aggressiveness of probing. They are never *conclusions*: a "high" claim from 2 weeks ago does NOT mean the learner currently remembers — it means "probe this lightly first." Probe results always override claims. The Rhodes & Tauber (2011) meta-analytic *g* = 0.93 (delayed-over-immediate JOL accuracy) is pooled across primarily short delays (mostly ~24 hours in the source studies); week-plus delays are uncharted territory. Treat older claims with more skepticism.

## What this skill does NOT do

After the project is created and the first concrete activity begins, the active skill should be `benkyo-tutoring`, not this one. This skill is for the setup phase only.

When in doubt about whether project init is complete: if the learner is attempting a problem or asking about a specific concept, that's tutoring territory.

## Quick reference

- CLI syntax: `../_benkyo-shared/references/cli-cheatsheet.md`
- Granularity rules: `../_benkyo-shared/references/granularity-guide.md`
- Natural language ↔ internal: `../_benkyo-shared/references/nl-to-cli.md`
- Lost learner cases 1 & 4: `../_benkyo-shared/references/lost-learner-handling.md`
- Literature backing: `../_benkyo-shared/references/literature-pointers.md`
