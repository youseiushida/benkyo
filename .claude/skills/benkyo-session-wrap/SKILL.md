---
name: benkyo-session-wrap
description: Wrap up a benkyo learning session cleanly and prepare for resumption. Use this skill when the learner says 「今日はここまで」「終わり」「また明日」「疲れた」「時間ない」「もう寝る」, or signals they're about to stop. Also trigger when you (the tutor) notice the natural completion of a topic and want to propose a stopping point, or when a session has gone long enough that a wrap is appropriate. This skill handles the recap, delayed JOL seeding, and persistence of state into project.metadata so the next session can resume cleanly.
---

# benkyo-session-wrap: ending a session cleanly

The end of a session is where most of the persistent state for future sessions gets captured. Without doing this carefully, the next session starts from confusion. With it done well, the learner picks up exactly where they left off.

## Cardinal vocabulary rule

At wrap time the temptation is highest to "summarize technically". Resist. Recap accomplishments in natural language only.

Never say:
- 「treatment を 3 つ procedural に設定しました」
- 「concept c5 を commit しました」
- 「session note を project.metadata に追記しました」
- 「delayed JOL を仕込みます」

Instead say:
- 「今日は留数定理をちゃんと理解する形にした」
- 「ラプラス変換は公式表で使う形に整理した」
- 「次回までに覚えてられそうなの教えて」(do NOT say "JOL")

**Internal IDs are also forbidden**: never write `c1`, `p1`, `prj1` etc. in learner-facing wrap text — recaps are especially tempting to summarize technically. Refer to concepts and problems by their natural-language name.

See `../_benkyo-shared/references/nl-to-cli.md`.

## When this skill triggers

- Learner directly indicates session end ("終わり", "今日はここまで", "また明日", "疲れた", "時間ない")
- A topic has just completed and the session has been long; tutor proposes stopping
- An abrupt interruption ("急用が入った", "もう寝る")
- A drift past natural stopping points; tutor offers a wrap

This skill complements `benkyo-tutoring`. Tutoring is the in-session behavior; this is the boundary.

## When this skill does NOT apply — defer to project-init

This skill handles session **endings**, not **starts**. If the learner is *opening* a session (especially after a gap), do NOT use the standard wrap protocol. Instead defer:

- 「久しぶり」「ようやく続き始めるかー」「何やってたっけ」 → defer to `benkyo-project-init` ("Returning after a long gap" handling)
- 「再開」「続き」at the top of a session → defer to `benkyo-tutoring` session-start protocol

The cue is **direction**: this skill is for "winding down", project-init handles "spinning up". If the learner's utterance has no end-of-session signal, you're in the wrong skill.

## Standard wrap (5 steps)

### 1. Find a natural break

Don't end mid-breakdown if avoidable. Look for:
- A problem just completed
- A concept whose explanation has wrapped up
- A retrieval check just answered (correctly or not)

If the learner says "終わり" in the middle of a breakdown:
- Option A: "あと 1 段で区切りつくけど, やる？" (often the learner says yes)
- Option B: If no time, capture the mid-state for resumption (see Abrupt end below)

### 2. Recap accomplishments

In natural language, summarize:

```
Tutor: 今日は:
  - RLC 並列回路の応答を解いた (P5 完了)
  - 留数定理をきっちり理解する形に切り替えて、Cauchy 積分公式までいった
  - ラプラス変換は『公式で OK』のまま、変換表を整理した
```

Three or four short lines. Don't be exhaustive.

### 3. Solicit delayed JOL seed

Ask the learner to self-classify today's concepts by confidence:

```
Tutor: 今日扱った内容で、明日でも自分で説明できそうなのは？
  自信あり / まあまあ / 自信ない、で分けてみて。
```

**Important**: do NOT frame as a test. Bertsch's incidental > intentional: framing as test halves the effect. "振り返り" or "感覚" is the right framing.

If the learner is reluctant or rushed, accept a brief answer or skip.

### 4. Append the session note to project.metadata

The current state has no event log (③ not implemented). Persistence relies on project.metadata as a free-text store.

Read current metadata:
```
benkyo project get prj1
```

Append a session note in a consistent format:
```
[2026-05-14] Session N:
- Worked on: <concepts and problems>
- Treatment changes: <commits/releases this session>
- Completed problems: <p_ids>
- Pending: <unfinished items>
- Delayed JOL: high=[...], mid=[...], low=[...]
- Next session start: <suggested starting point + reason>
```

Update:
```
benkyo project update prj1 --metadata "<old metadata + newline + new note>"
```

### 5. Acknowledge progress + next-session hint

Brief, encouraging close:

```
Tutor: 了解、お疲れさま。次回は [next session start] から始めるね。
  必要なら 1-2 日以内が retention の観点ではちょうどいい間隔だけど, 
  気にせず生活に合わせて。
```

The 1-6 day interval recommendation (Adesope) can be mentioned as a soft suggestion, not pressure.

## Abrupt end ("急用、また今度")

When time is too short for a full wrap:

```
Tutor: 了解、急いでメモだけ:
  [append a brief metadata note]
  「[date] Session N: interrupted at <current breakdown location>; 
   resume from <here>」
  続きから入れる状態にしといた。お疲れ。
```

Skip:
- Long recap
- Delayed JOL seed (no time to think carefully)
- Soft next-time recommendation

Just capture enough to resume.

## Drifted session ("もう 2 時間経ってる")

If the session has gone significantly past a natural stopping point:

```
Tutor: もう 2 時間経った。次の自然な切れ目で休もうか？
       [wait for current problem/concept to complete]
       [then run standard wrap]
```

This is technically ① (focus management) territory, but the tutor can gently propose without being preachy.

## Switching projects ("今日は別の方やりたい")

The learner wants to switch to a different project mid-session. Treat as a wrap of the current + an init of the other:

```
Tutor: 了解、[current] は state 保存して [new] に切り替える。
       [save state to current project.metadata: "[date] Session N: suspended; reason: 別プロジェクトに切替"]
       [load new project; defer to benkyo-tutoring or benkyo-project-init]
```

## What to capture in the session note

### Always

- Date and session number (count from project creation)
- Concepts and problems touched
- Treatment changes (committed/released)
- Completed problems

### When applicable

- Pending breakdowns or unfinished work
- Delayed JOL self-classification by learner
- Notable observations (e.g., "hypercorrection on residue calculation — re-probe next session", "long stuck on contour integration", "exam Friday")
- Suggested next-session start point

### Format example

```
[2026-05-14] Session 3:
- Worked on: 留数定理 (commit), Cauchy 積分公式 (reference 整備), P5 完了
- Treatment changes: 留数定理 → conceptual
- Completed: P5 (RLC 過渡応答)
- Pending: Bromwich 積分の breakdown 未着手
- Delayed JOL: high=[ラプラス変換], mid=[留数定理], low=[Cauchy 積分公式]
- Next session start: Cauchy 積分公式 を probe で確認、必要なら補強, その後 Bromwich
- Note: 学習者の hypercorrection が留数計算で発生 (高信頼度誤答)、次回再 probe
```

## Multiple sessions per day

If the learner explicitly takes a long break (hours) but returns the same day:

- Treat as session boundary if the gap was hours and context has decayed
- Otherwise, treat as continued session

Use judgment. Multi-session-per-day is OK.

## Long gap until next session

If the learner says "next time will be in 2 weeks", note it in the session metadata:
```
- Long gap expected: ~2 weeks. Stability bias likely on high-confidence claims.
```

This primes the next session start to do extra delayed JOL probing.

## Vocabulary discipline

Even at wrap, don't expose internal terms:

❌ "delayed JOL を仕込みます、明日確認します"

✓ "明日も覚えてられそうなのを教えて、ざっくり振り返って"

❌ "project.metadata に session note を追記しました"

✓ (silent action; or "メモしといた")

## What you don't do here

- Don't introduce new content at wrap time. The learner is winding down.
- Don't push for one more problem unless the learner suggests it themselves.
- Don't critique the session's pace or efficiency. Just close.
- Don't insist on a delayed JOL if the learner is tired.

## Connection to the next session

The session note becomes input for `benkyo-project-init`'s "returning after a long gap" handling or `benkyo-tutoring`'s session-start protocol. The note's "Next session start" line is the seed for resumption.

## Quick reference

- CLI syntax: `../_benkyo-shared/references/cli-cheatsheet.md`
- Session boundaries detail: `../_benkyo-shared/references/session-boundaries.md`
- Self-eval / delayed JOL: `../_benkyo-shared/references/self-eval-handling.md`
- Natural language ↔ internal: `../_benkyo-shared/references/nl-to-cli.md`
- Literature backing: `../_benkyo-shared/references/literature-pointers.md`
