---
name: benkyo-graph-edit
description: Edit the structure of a benkyo concept/problem graph — add or remove nodes and edges, adjust granularity, fix duplicates. Use this skill when the learner says 「これも追加して」「これとあれは関連してる」「これは別物」「これも勉強したい(新概念)」「これとこれ同じ」「これは分けるべき」, or when you (the tutor) notice during a session that a concept the learner just mentioned isn't in the graph yet, or that a relationship between existing nodes is missing/wrong. Also trigger when reviewing or refining the graph structurally — e.g., during project init when assessing the initial set of nodes.
---

# benkyo-graph-edit: structuring and editing the graph

This skill governs all structural changes to the global benkyo graph: adding concept and problem nodes, adding/removing edges, deciding granularity, handling duplicates. The rules apply during project init AND mid-session (when graph gaps surface).

## Cardinal vocabulary rule

Even when discussing graph edits with the learner, never use internal terms (node, edge, prereq, related, graph, granularity, merge, fork) in learner-facing utterances. Translate:

- node → 「項目」「概念」「問題」
- edge → 「つながり」「関係」「線」
- prereq edge → 「前提」「土台になる関係」
- related edge → 「関連」「セットで覚える関係」
- merge → 「同じだから 1 つにまとめる」
- fork / split → 「細かく分ける」
- graph → 「全体像」「学習の地図」

Internal operation: `benkyo edge add --from c1 --to c2 --type related`
Spoken to learner: 「ラプラス変換とフーリエ変換, 混同しやすいから 『セットで覚えておく』マークしとくね」

**Internal IDs are also forbidden**: never write `c1`, `c2`, `p1`, `prj1` etc. in learner-facing text. Especially in graph-edit, the temptation to say "c7 を追加して c1 に related で繋いだ" is high — translate to "『フーリエ変換』を追加して『ラプラス変換』とセットで覚える関係にしといた" instead.

See `../_benkyo-shared/references/nl-to-cli.md`. Re-read before composing any learner-facing message that touches structural details.

## When this skill triggers

- Learner explicitly asks for a structural change ("これも追加して", "これとあれは関連してる", "これは別物")
- During a tutoring session, you (the tutor) notice a needed graph change (the learner mentions a concept that's not yet in the graph; or two concepts that should be linked but aren't)
- During project init, while drafting the initial graph

## Cardinal rule: always check identity before adding

The global graph is shared across projects. Adding a duplicate of an existing concept fragments the graph and undermines the cross-project reuse benefit.

Before any `benkyo concept add`:

```
benkyo concept find --content "<exact or near-exact name>"
```

If matches exist, evaluate:
- Same concept? → reuse the existing id; don't add
- Different but related? → add the new one, then add a `related` edge if the relationship is real
- Genuinely the same content but worded differently? → consider `concept merge` (when implemented) or just reuse

## Granularity: the core decision

Granularity is the most consequential editing decision. The full rules are in `../_benkyo-shared/references/granularity-guide.md`. Summary:

A concept node should satisfy these 5 criteria:

1. **Single treatment unit**: it can be assigned procedural or conceptual as a whole.
2. **Uniform prereqs**: its sub-aspects need similar prereqs.
3. **Aligned with textbook/course chunking**: roughly section-level granularity.
4. **Reusable**: it appears as a prereq of multiple parents (otherwise absorb into parent).
5. **Probable**: you can ask "do you understand X?" and get a meaningful answer.

Violations:

- If treatment can't be uniform → split
- If prereqs differ widely across sub-aspects → split
- If you can't probe it as a unit → split (too abstract)
- If it's used only once → maybe absorb into the parent
- If it always appears with another node, same prereqs, same problems → merge

**Lazy refinement principle**: start with section-level granularity. Split only when an actual use case demands finer treatment. Don't pre-split "just in case".

**Cross-project rule**: the global graph supports the FINEST granularity that any project needs. Coarser-use projects aggregate by marking groups of fine nodes as procedural.

## Edges: prereq vs related

### prereq

`X → Y` (in CLI: `--from X --to Y --type prereq`) means **X depends on Y, Y is directly used to understand or solve X**.

Add a prereq when:
- The learner would necessarily get stuck on Y if attempting X
- Y's fact, procedure, or concept is *directly used* in X

Don't add prereq when:
- Y is just mentioned in X's section
- Y is a philosophical/historical precursor but not used
- Y is the same notation but a different concept

**Direction**: `from` is dependent, `to` is depended-upon. To say "Laplace transform depends on definite integral":
```
benkyo edge add --from c_laplace --to c_definite_integral --type prereq
```

### related

`X ↔ Y` (`--type related`) is used in two senses (both stored as the same edge type for now):

- **related-confusable**: X and Y are easily confused with each other. The learner needs to discriminate. (Brunmair & Richter: between-category similarity drives interleaving benefit. These are the confusable pairs.)
- **related-cooccurring**: X and Y appear together in curriculum or topically near, but no dependency.

Sub-type isn't stored formally yet (lazy schema refinement). The interpretation is inferred from the contents and context.

Add a `related` edge when:
- Two concepts are mistakable for each other (confusable)
- Two concepts often appear together as alternatives or extensions
- A learner has visibly confused them

Don't add `related` when:
- The relationship is purely "same chapter"
- There's a clear dependency (use `prereq` instead)
- The relationship is incidental and doesn't help learning

### Transitivity

DON'T draw transitive edges. If A → B and B → C, don't also add A → C (unless A also *directly* uses C).

### Test when in doubt

Three questions to decide prereq vs related:

1. **Is there a temporal "first"?** Yes → prereq. No → related.
2. **Solving X, do you use Y as a tool or contrast it?** Tool → prereq. Contrast → related.
3. **Abstraction levels different?** Different (one is a special case) → typically prereq. Same level (sibling) → typically related.

## Content quality standards

When adding a node, the content (concept) or statement+answer (problem) follows these rules. See full discussion in `../_benkyo-shared/references/granularity-guide.md`.

### Concept content (50-200 chars)

Purpose: identify and distinguish, not full explanation.

Format:
- Open with the name/title phrase ("ラプラス変換: ...")
- 1-3 sentences of definition
- Optionally: 1 sentence on use or distinguishing feature

NOT:
- Long exposition (don't write a Wikipedia paragraph)
- Just the name (no definition)
- Just a formula (no context)

Example:
```
ラプラス変換: 時間関数 f(t) (t≥0) を複素変数 s の関数 F(s) に写す積分変換。
F(s) = ∫₀^∞ f(t)e^(-st)dt と定義され、線型微分方程式を代数方程式に変換する用途で使われる。
Fourier 変換と類似だが、減衰因子 e^(-σt) により発散関数も扱える点が異なる。
```

### Problem statement (100-500 chars)

Purpose: a self-contained problem the learner can attempt.

Include:
- All conditions, values, units
- What's being asked
- Any necessary context

Don't include:
- Hints (foresight bias, generation effect)
- Solution method indicators
- "as discussed earlier" references

Example:
```
L = 0.1 H, C = 100 μF, R = 10 Ω の直列 RLC 回路に, t = 0 から振幅 1 V の
単位ステップ電圧を印加した時の電流 i(t) を求めよ。初期条件は i(0) = 0, di/dt(0) = 0。
```

### Problem answer (50-500 chars)

Format: key intermediate results + final answer. Not a full step-by-step (that's for teaching loop).

Example:
```
特性方程式: s² + 100s + 10⁵ = 0
ζ = 0.5 (under-damped)
ω₀ ≈ 316.2 rad/s, ω_d ≈ 273.9 rad/s
i(t) = (1/Lω_d) e^(-ζω₀t) sin(ω_d t) ≈ 0.0365 e^(-50t) sin(273.9 t) [A]
```

### Reference content for procedural concepts (200-1000 chars)

See `benkyo-treatment-shift` skill for the standards. Tables, formulas, recipes — not exposition.

## Common operations

### Adding a new concept (with safety)

```
# Step 1: identity check
benkyo concept find --content "<intended name>"

# Step 2 (if no match):
benkyo concept add --content "<name>: <1-3 sentence definition>"

# Step 3: add prereq edges if any
benkyo edge add --from <new_id> --to <prereq_id> --type prereq

# Step 4: if treatment in current project is non-default (procedural), set it
benkyo treatment set --project <prj_id> --concept <new_id> \
  --treatment procedural --reference "<content>"
```

### Adding a new problem

```
# Identity check via content match
benkyo problem list --query "<key phrase from problem>"

# If new:
benkyo problem add --statement "<full statement>" --answer "<key results + final>"

# Connect to concepts via prereq:
benkyo edge add --from <problem_id> --to <concept_id> --type prereq
# (For each concept directly used to solve this problem)

# If this is a project goal:
benkyo project update <prj_id> --goals <p1,p2,...,new_problem_id>
```

### Removing a wrong edge

```
benkyo edge delete --from <id1> --to <id2> --type <prereq|related>
```

### Identifying duplicates to merge

```
benkyo concept list --query "<part of name>"
# inspect results, decide if any pair is truly the same
# (merge command pending implementation; meanwhile, manually redirect edges then delete)
```

### Splitting a node (manually, before fork command)

Currently no atomic split. Procedure:

1. Create the new "split-off" concept(s) with `concept add`.
2. Identify which edges of the original should move to which split.
3. For each edge to move: `edge delete` old + `edge add` new direction.
4. Similarly for project_concepts (treatments): unset on original, set on splits.
5. When done, decide whether to keep, edit, or delete the original.

This is tedious; merge/fork commands are planned. For now, this is the manual flow.

## Vocabulary discipline

Even when discussing graph edits with the learner, don't use internal terms:

| Internal | Learner-facing |
|---|---|
| concept node | "概念" / "項目" |
| problem node | "問題" |
| prereq edge | "前提" / "土台" |
| related edge | "関連" / "セット" |
| graph | "学習の地図" / "全体像" |
| project | "今やってる学習" |

Example:

❌ "ラプラス変換と Fourier 変換の間に related edge を貼ろう"

✓ "ラプラス変換と Fourier 変換、混同しやすいから 『セットで覚えておく』マークしとくね"

## When the learner volunteers structure feedback

The learner might say:

- 「これとあれは関連してる」 → consider adding `related` edge after checking
- 「これは別物」 → check the offending edge; delete if wrong
- 「これは細かく分けたい」 → consider split (use manual procedure for now)
- 「これとこれ同じ」 → consider merge (manual redirect for now)

Always confirm intent before executing. Sometimes the learner's structural intuition is correct; sometimes it's based on a misunderstanding.

## Quick reference

- CLI syntax: `../_benkyo-shared/references/cli-cheatsheet.md`
- Granularity rules: `../_benkyo-shared/references/granularity-guide.md`
- Decision tables (edges, treatment): `../_benkyo-shared/references/decision-tables.md`
- Natural language ↔ internal: `../_benkyo-shared/references/nl-to-cli.md`
- Literature backing: `../_benkyo-shared/references/literature-pointers.md`
