# Session boundaries: start and end protocols

How to begin and end a learning session, and how to persist state across sessions when there is no event log (③) yet.

## Session start

### 4 steps

1. **Confirm project**: `benkyo project list`; ask the learner which to resume (or use most recent active).
2. **Show current state**: `benkyo window --project <id>`, plus read project.metadata for the most recent session note.
3. **Delayed JOL probe**: if the previous session's metadata recorded a delayed JOL seed, probe the high-confidence claims now (1 problem, TAP-aligned, incidental framing).
4. **Focus negotiation**: propose 1-3 specific next steps with reasons; learner chooses.

### Example

```
Tutor: 電気回路の試験対策プロジェクトを再開？

Learner: うん

Tutor (internal: project get, window, read metadata):
  これまで: RLC 直列の基本式を 2 題完了、ラプラス変換は公式表扱い。
  前回末で「ラプラス変換は自信あり、留数定理はまあまあ」だったね。
  軽く確認させてもらっていい？ [Laplace simple problem]

Learner: [solves]

Tutor: バッチリ。じゃあ今日は次のステップに行こう。
  推奨は「RLC 並列回路の応答」、自然な続き。
  別がよければそれでもいいし、もう少しおさらいしてからでも。

Learner: それで行こう

Tutor: [presents the problem; PS-I begins]
```

## Session end

### 5 steps

1. **Stop at natural break**: avoid mid-breakdown endings; let a problem complete or a concept finish.
2. **Recap accomplishments**: "今日は [X] を理解、[Y] を release、[Z] の breakdown 1 段やった".
3. **Capture state changes**: any treatment updates, new nodes, completed problems — these are already in the DB via CLI, but make sure you didn't miss any.
4. **Solicit delayed JOL seed**: ask the learner to classify today's concepts by self-confidence. NOT framed as a test.
5. **Append session note to project.metadata**.

### Session note format

Append to project.metadata (free-text, since no ③ yet):

```
[YYYY-MM-DD] Session N:
- Worked on: <concepts and problems touched>
- Treatment changes: <commit/release events>
- Completed problems: <p_ids>
- Pending: <unfinished breakdowns, unattempted problems>
- Delayed JOL: high: <list>, mid: <list>, low: <list>
- Next session start: <suggested starting point>
```

Pseudocode:
```
project = benkyo project get prj1
new_metadata = project.metadata + "\n\n" + session_note
benkyo project update prj1 --metadata "<new_metadata>"
```

### Example

```
Tutor: お疲れさま。今日は留数定理の breakdown を一段やって、Cauchy 積分公式
       までは押さえた。明日もちゃんと説明できそうなのは？
       自信あり / まあまあ / 自信ない で分けてみて。

Learner: ラプラス変換は自信あり、留数はまあまあ、Cauchy 積分公式は自信ない

Tutor (internal: append to project.metadata):
  [2026-05-14] Session 3:
  - Worked on: 留数定理 (commit), Cauchy 積分公式 (reference 整備)
  - Treatment changes: 留数定理 → conceptual
  - Completed: P5
  - Pending: Bromwich 積分の breakdown が未着手
  - Delayed JOL: high=[ラプラス変換], mid=[留数定理], low=[Cauchy 積分公式]
  - Next: Cauchy 積分公式 を probe で確認、その後 Bromwich 積分

Tutor: 了解。次回は Cauchy 積分公式の確認から始めるね。お疲れ。
```

## Edge cases

### Abrupt end ("時間切れ、また今度")

Skip the long recap. Just capture enough to resume:

```
Tutor: 了解、急いでメモだけ:
  [append: "[date] Session N: interrupted at <current breakdown location>; resume from <here>"]
  続きから入れる状態にしといた。お疲れ。
```

No delayed JOL seed if there's no time.

### Long-duration session ("もう 2 時間経ってる")

This is technically ① (focus management) territory, but for now, the tutor can gently propose a stop:

```
Tutor: もう 2 時間か。次の自然な切れ目で休もうか？
  [completes current problem or concept, then runs normal session-end]
```

### Long gap between sessions (1 week+)

Probe more aggressively at session start:

```
Tutor: 久しぶり。前回から少し空いたから、おさらい多めで始めようか。
  前回末の自信申告:
  - 自信あり: [list] → 全部軽く probe (1 問ずつ)
  - まあまあ: [list] → 1-2 個 probe
  - 自信ない: [list] → 改めて学習し直す前提

  どれから行く？
```

Expect more stability bias caught — many "自信あり" claims may have decayed.

### Cross-project switch ("今日は別の方やりたい")

Save current project state, load new one:

```
Tutor: 了解、[current project] は suspend して [new project] に切り替える。
  [append note: "[date] Session N: suspended; reason: 学習者の希望で別プロジェクトに"]
  [load new project state]
  [run normal session-start protocol]
```

## Optimal between-session interval

From Adesope (1-6 days is the peak retention interval), suggest:

- 1-2 days: ideal for active drilling (testing effect peak)
- 3-6 days: good for retention consolidation
- 1+ week: getting risky for stability of "high confidence" items

But don't be prescriptive. The learner's life dictates timing. Mention it as a soft recommendation if asked.

## What to do without ③ (event log)

Currently, the only persistence is project.metadata (free text). Limitations:

- Can't query "how confident was learner on concept X over 5 sessions"
- Can't compute "average commit-to-release time"
- Self-evaluation accuracy can't be measured automatically

Workarounds:
- Append-only session notes in metadata
- Mention key facts at session start so they're in the conversation context
- Trust learner to read their own metadata if they're curious

When ③ arrives, this whole protocol becomes structured event records.
