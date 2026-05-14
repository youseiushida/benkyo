---
name: benkyo-treatment-shift
description: Change the depth-of-engagement (procedural vs conceptual treatment) for a concept in a benkyo project. Use this skill when the learner expresses 「ちゃんと理解したい」「腹落ちしたい」「導出やりたい」「なぜそうなる？」「もっと深く」 (commit signals — wants deeper understanding), or 「公式覚えれば」「暗記でいい」「ざっくり」「飛ばして」「もういい」 (release signals — wants to shortcut to memorization). Also trigger when you (the tutor) detect indirect signals: repeated "なんで" on a concept, mis-applying a procedural reference, failed transfer to varied problems (commit candidates), or stuck-multiple-breakdowns / fatigue / time-pressure (release candidates).
---

# benkyo-treatment-shift: changing depth of engagement

This skill handles the operation of changing a concept's treatment within a project — moving it from "use as a tool" (procedural) to "really understand" (conceptual), or vice versa. Both directions have specific protocols.

The decision when to shift is part of this skill. The actual ongoing teaching is in `benkyo-tutoring`.

## Cardinal vocabulary rule

Internal terms (procedural, conceptual, treatment, cut, commit, release, prereq, node, edge, graph) are NEVER spoken to the learner. Translate:

- commit / 「上に上げる」 → 「ここを掘り下げる」「ちゃんと理解する」
- release / 「下に降ろす」 → 「公式で済ます」「ツールとして使う」「飛ばす」
- procedural → 「公式扱い」「使えれば OK」
- conceptual → 「理解する対象」

When you internally execute `benkyo treatment set ...`, what you say out loud is "じゃあここは公式覚えて使う形に切り替えるね" (or similar), NEVER "treatment を procedural にしました".

**Internal IDs are also forbidden**: never write `c1`, `p1`, `prj1` etc. in learner-facing text. Refer to concepts by their natural-language name or content.

See `../_benkyo-shared/references/nl-to-cli.md` for the full translation table.

## Trigger types

### Direct signals (from learner)

| Learner says | Direction |
|---|---|
| 「理解したい」「腹落ちしたい」「導出やりたい」「なぜそうなる？」「もっと深く」 | commit (procedural → conceptual) |
| 「公式覚えれば」「暗記でいい」「ざっくり」「飛ばして」「もういい」 | release (conceptual → procedural) |

When a direct signal is clear, confirm intent briefly then execute.

### Indirect signals (inferred by tutor)

For **commit**:
- Repeated "なんで？" or meaning-questions about the same concept (≥ 2 times in a session)
- Misapplying the procedural reference (e.g., wrong formula choice, wrong substitution pattern)
- Failed transfer: solves the original problem but fails when conditions change slightly
- "Which formula here?" repeated — suggests not understanding applicability conditions

For **release**:
- Stuck on this node despite 2-3 breakdown attempts
- Fatigue, frustration ("もういい", reaction time slowing)
- Time pressure expressed ("明日試験")
- Diminishing returns: more breakdown isn't moving the learner closer to goal
- Same concept causing trouble across multiple sessions

When you detect an indirect signal, **propose** (don't execute silently):

```
Tutor: ここ、3 回ほど見直してるけど、まだ詰まり気味だね。
  一旦この公式を使う形に切り替えて、先に進む？後で気持ちに余裕できたら戻ってきても良い。
```

## Commit protocol (procedural → conceptual)

Goal: open up the concept for full understanding (breakdown becomes traversable into prereqs).

### Steps

1. **Confirm with learner** in natural language: "ここから掘り下げる？時間と集中力ある？"
2. **Check prereqs exist**: run `benkyo breakdown --project --node <concept_id>` to see direct prereqs. If too few or none, the global graph lacks structure here.
3. **Add missing prereqs (one level only)**:
   - Identify what's needed for this concept to be understood
   - For each: `benkyo concept find --content <name>` (identity check)
   - If exists: link with `benkyo edge add --from <concept_id> --to <prereq_id> --type prereq`
   - If missing: `benkyo concept add --content <...>` then add edge
4. **Set new prereqs to procedural by default** (with reference content):
   - Commits intentionally cascade ONE level only; don't recursively conceptualize the entire prereq chain
   - The learner committed THIS concept, not its prereqs
5. **Verify each prereq's treatment**: ensure each is procedural with reference, OR explicitly known to be already mastered. If a prereq isn't ready, the commit may produce frustrating breakdown failures.
6. **Update the target concept's treatment** to conceptual:
   ```
   benkyo treatment unset --project prj1 --concept c5
   # or equivalently:
   # benkyo treatment set --project prj1 --concept c5 --treatment conceptual
   ```
7. **Notify the learner briefly** if new prereqs were added: "進めながら『定積分』と『複素指数関数』に触れる場面が出てくるけど、それぞれは公式が使えれば一旦 OK にして、必要ならそこも掘る感じで進めるね。"
8. **Begin teaching loop** (defer to `benkyo-tutoring`).

### Don't

- Don't commit without first checking prereqs. PF (PS-I) requires *relevant prior knowledge* (Sinha & Kapur). Committing into a void produces overload.
- Don't auto-recurse and commit prereqs of prereqs. Each commit is a discrete decision.
- Don't commit and then immediately try a hard problem. Build up first.

## Release protocol (conceptual → procedural)

Goal: close off the concept; just use the reference.

### Steps

1. **Confirm with learner** in natural language: "ここは公式で済ませて先に進もうか？"
2. **Prepare reference content** that's sufficient for use. The reference should:
   - Be enough to USE the concept (table, formulas, recipe)
   - Be project-context-specific (telecom vs PDE etc.)
   - Not include derivations or "why" content (that's what we just decided to drop)
   - See content standards in `../_benkyo-shared/references/granularity-guide.md` and decision-tables.md
3. **Set the treatment**:
   ```
   benkyo treatment set --project prj1 --concept c5 \
     --treatment procedural --reference-file <path>
   # or with inline reference:
   # benkyo treatment set --project prj1 --concept c5 \
   #   --treatment procedural --reference "<content>"
   ```
4. **Acknowledge the trade-off**: "じゃあこの公式を使う形で進めるね。気が向いたら戻ってきてもいい。"
5. **Continue toward the original goal** (defer to `benkyo-tutoring`).

### Don't

- Don't release a concept that's the project's core goal — releasing the target defeats the project.
- Don't release without preparing reference content. The reference is the substitute for understanding; if it's vague, the learner can't actually use the concept.
- Don't release a concept that was just committed in the same session (hysteresis: give a session for it to work).

## Cascade behavior

| Operation | Cascade |
|---|---|
| **commit** | Adds prereqs ONE level if missing; doesn't recurse. Future commits on those prereqs are separate decisions. |
| **release** | Single node only. Prereqs of the released node are unchanged (their treatments stay as set). The released node simply becomes a terminal in traversal. |

This is asymmetric on purpose:
- Commit *expands* the conceptual scope downward — one step at a time.
- Release *contracts* the conceptual scope at a node — no downstream effect needed because procedural is a terminal in window traversal.

## When the learner toggles rapidly

If the same concept oscillates commit ↔ release within a session, that's a signal something's wrong. Common causes:

- Cognitive load too high — try a smaller scope or break
- Genuine ambivalence about the depth needed — explicitly discuss what they want to achieve
- The concept is at the wrong granularity (should be split — see granularity-guide.md)

Pause the toggling. Talk it through.

## Vocabulary to the learner

| Internal | Learner-facing phrasing |
|---|---|
| commit | "掘り下げる" / "ちゃんと理解する" / "深く見る" |
| release | "公式で済ます" / "暗記で済ます" / "道具として使う" / "飛ばす" |
| procedural | "公式" / "ツール" / "道具" / "暗記項目" |
| conceptual | "理解" / "腹落ち" / "本質" |
| reference content | "公式表" / "早見表" / "メモ" |
| prereq | "下地" / "前提" / "必要な前の物" |

Never use the English internal terms in learner-facing utterances.

## Reference content quality

When preparing reference content for release, follow these standards (see `../_benkyo-shared/references/granularity-guide.md`):

- 200-1000 chars typical length
- Tables, formulas, recipes — not exposition
- Project-context appropriate (e.g., Laplace transform reference for telecom vs PDE differs)
- Self-contained (usable without other context)
- No "why" or derivation

Example for Laplace transform in a telecom project:

```
**変換表 (主要):**
δ(t)         → 1
u(t)         → 1/s
e^(-at)      → 1/(s+a)
sin(ωt)      → ω/(s²+ω²)
cos(ωt)      → s/(s²+ω²)

**演算則:**
線型性: L{αf + βg} = αF + βG
微分: L{f'(t)} = sF(s) - f(0)
積分: L{∫f dτ} = F(s)/s
たたみ込み: L{f*g} = F·G
```

## Quick reference

- CLI syntax: `../_benkyo-shared/references/cli-cheatsheet.md`
- Decision tables: `../_benkyo-shared/references/decision-tables.md`
- Granularity / content standards: `../_benkyo-shared/references/granularity-guide.md`
- Natural language ↔ internal: `../_benkyo-shared/references/nl-to-cli.md`
- Literature backing: `../_benkyo-shared/references/literature-pointers.md`
