# Session boundaries: start and end protocols

How to begin and end a learning session. As of v0.2.0, persistence uses the structured events log; `project.metadata` is just the project's free-text description and is not used as a session journal.

## Session start

### 5 steps

1. **Confirm project**: `benkyo project list`; identify which to resume.
2. **Show current state**: `benkyo window --project <id>` for the graph.
3. **Recover the previous session**: `benkyo events list --project <id> --kind session_end --limit 1`. The payload's `pending` and the `notes` column tell you where to resume.
4. **Recover the previous self-classification**: `benkyo events list --project <id> --kind delayed_jol_recorded --limit 20`. These are the seeds the last wrap captured. Probe the high-confidence ones first with one TAP-aligned problem each, **incidentally framed** (Bertsch d=0.65 incidental vs d=0.32 intentional — don't say "test").
5. **Record session start + focus negotiation**:
   ```
   benkyo events add --kind session_start --project <id> --notes "<gap-length, learner context>"
   ```
   Then propose 1–3 specific next steps with reasons; let the learner choose.

### Example

```
Tutor: 電気回路の試験対策プロジェクトを再開？

Learner: うん

Tutor (internal: project list, window, events list --kind session_end --limit 1,
                 events list --kind delayed_jol_recorded --limit 10):
  これまで: RLC 直列の基本式を 2 題完了、ラプラス変換は公式表扱い。
  前回末で「ラプラス変換は自信あり、留数定理はまあまあ」って言ってたよね。
  軽く確認させてもらっていい？ [Laplace simple problem]

Learner: [solves]

Tutor: バッチリ。じゃあ今日は次のステップに行こう。
  推奨は「RLC 並列回路の応答」、自然な続き。
  別がよければそれでもいいし、もう少しおさらいしてからでも。

Learner: それで行こう

Tutor: [presents the problem; PS-I begins]
       (internal: events add --kind session_start --notes "3 day gap, exam in 10 days")
```

### Events as prior, never as conclusion

The recovered JOL claims are *priors* — they tell you what to probe first and how aggressively, not what the learner currently knows. A `claim: "high"` from 2 weeks ago does NOT license skipping; it licenses light + early probing. Probe results always override. Foresight bias (Bjork et al. 2013) applies symmetrically when a skill reads its own past records.

## Session end

### 5 steps

1. **Stop at natural break**: avoid mid-breakdown endings; let a problem complete or a concept finish if practical.
2. **Recap accomplishments** in natural language: "今日は [X] を理解、[Y] を公式扱いに整理、[Z] の中身を一段見た".
3. **Capture state changes**: any treatment updates and new nodes are already in the DB via CLI (and treatment-shift writes `treatment_changed` events). Make sure nothing's been done silently.
4. **Solicit delayed JOL seed**: ask the learner to classify today's concepts by self-confidence. **NOT framed as a test** — say "感覚で", "振り返り" (Bertsch incidental framing).
5. **Persist via `benkyo session end`** with the summary JSON:
   ```
   benkyo session end --project <id> --summary-file <path>
   ```
   This atomically writes the `session_end` event plus one `delayed_jol_recorded` event per JOL entry. No need to call `events add` separately.

### Summary JSON shape

```json
{
  "completed_problems": ["p5"],
  "treatment_changes": [
    {"concept_id": "c4", "from": "blackbox", "to": "whitebox"}
  ],
  "pending": ["c5 (Bromwich 積分 breakdown 未着手)"],
  "delayed_jols": [
    {"concept_id": "c1", "claim": "high"},
    {"concept_id": "c4", "claim": "mid"},
    {"concept_id": "c5", "claim": "low", "note": "苦手意識"}
  ],
  "notes": "学習者は来週試験。c4 で hypercorrection あり (詳細は events log)"
}
```

The `notes` field is the LLM-flexibility escape hatch — anything qualitative that doesn't fit the structured shape goes here.

### Example

```
Tutor: お疲れさま。今日は留数定理の中身を一段見て、Cauchy 積分公式までは押さえた。
       明日もちゃんと説明できそうなのは？感覚でいいから、自信あり/まあまあ/自信ないで分けてみて。

Learner: ラプラス変換は自信あり、留数はまあまあ、Cauchy 積分公式は自信ない

Tutor (internal: prepare summary JSON, then session end):
  {
    "completed_problems": ["p5"],
    "treatment_changes": [{"concept_id": "c4", "from": "blackbox", "to": "whitebox"}],
    "pending": ["c5 (Bromwich 積分が未着手)"],
    "delayed_jols": [
      {"concept_id": "c1", "claim": "high"},
      {"concept_id": "c4", "claim": "mid"},
      {"concept_id": "c6", "claim": "low"}
    ],
    "notes": "次回は Cauchy 積分公式の確認から、その後 Bromwich"
  }

Tutor: 了解。次回は Cauchy 積分公式の確認から始めるね。お疲れ。
```

## Edge cases

### Abrupt end ("時間切れ、また今度")

Skip the long recap and JOL solicitation:

```
benkyo session end --project prj1 --summary '{"pending": ["c4 breakdown 中"], "notes": "interrupted by 急用"}'
```

```
Tutor: 了解、メモしといた。続きから入れる状態にしといたよ。お疲れ。
```

The minimal summary still produces a `session_end` event with `pending` + `notes` — enough for next-session resume.

### Long-duration session ("もう 2 時間経ってる")

This is technically ① (focus management) territory, but for now the tutor can gently propose a stop:

```
Tutor: もう 2 時間か。次の自然な切れ目で休もうか？
  [completes current problem or concept, then runs normal session end]
```

### Long gap between sessions (1 week+)

This is `benkyo-project-init`'s "Returning after a long gap" handling — the session-wrap skill should defer to project-init for the *next* session's start, but the *current* session's end is still standard `session end`. Just note the gap-likely duration in the `notes`:

```json
{
  ...,
  "notes": "学習者は来週試験まで毎日。1 週間ぶりは想定しない"
}
```

When the gap actually happens, project-init reads the events log and decides probing aggressiveness (see `benkyo-project-init`'s skill).

### Cross-project switch ("今日は別の方やりたい")

Save current project state via session end (with `notes: "suspended; reason: 別プロジェクトに切替"`), then load new project (defer to `benkyo-project-init` or `benkyo-tutoring`).

## Optimal between-session interval

From Adesope (1–6 days is the peak retention interval), suggest:

- 1-2 days: ideal for active drilling (testing effect peak)
- 3-6 days: good for retention consolidation
- 1+ week: getting risky for stability of "high confidence" items

But don't be prescriptive. The learner's life dictates timing. Mention it as a soft recommendation if asked.

## Why events, not metadata

`project.metadata` stays as a free-text project description (what the learner is studying, why). It is not the persistence layer for session history.

The events log is queryable:
- `events list --kind delayed_jol_recorded` → all JOL claims, all sessions
- `events list --kind treatment_changed --since 2026-04-01` → treatment timeline
- `events list --kind hypercorrection_detected --project <id>` → moments worth re-probing

This unlocks cross-session reasoning the free-text approach couldn't:
- Delayed JOL verification across multiple intervals (Rhodes & Tauber 2011)
- Hypercorrection re-probe scheduling (Butterfield & Metcalfe 2001)
- Stability bias detection by comparing claims to subsequent probe results (Bjork et al. 2013)
- Spacing interval measurement (Adesope et al. 2017)

Use `notes` columns generously for context that doesn't fit a payload schema; the LLM-flexibility doesn't have to die just because the structure exists.
