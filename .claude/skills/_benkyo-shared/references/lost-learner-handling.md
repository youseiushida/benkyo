# Handling a learner who doesn't know where to start

When the learner expresses "I don't know where to start" or seems disoriented, the tutor must take initiative. Asking "what do you want to do?" empty-handed is unhelpful and shifts the cognitive burden onto someone already stuck.

## 4 cases

| # | State | Learner phrasing | Approach |
|---|---|---|---|
| 1 | No project yet, has subject | 「電気回路の勉強したい」 | extract concrete goal problem → project create |
| 2 | Project exists, lost at session start | 「何やってたっけ」 | show current state + propose 1-3 next steps |
| 3 | Mid-session, lost | 「今何やってるんだっけ」 | recap breakdown stack + offer continue/back/switch |
| 4 | Completely goal-less | 「何か勉強したい、特に決めてない」 | extract interest via casual questions; or use exploration mode |

## Case 1: Subject named, no project yet

The learner has a domain (電気回路, 制御理論, ヘブライ語) but no concrete goal.

**Tutor's job**: extract a concrete goal problem ASAP, so the project has a target.

```
Learner: 電気回路の勉強したい、何から始めればいい？

Tutor: 電気回路で何ができるようになりたい？例えば:
  - 試験対策 (どの試験、範囲は？)
  - 特定の過去問が解けるようになりたい
  - 「○○を設計できる」のような実用目標
  - 教科書を最後まで読みたい

Learner: 大学の試験、RLC回路の過去問が解けるように。

Tutor: 過去問あれば渡して、無くても進められる。
  [project create]
  試しに RLC 系の過去問を 1 問解いてみる？現在地が分かる。
```

**Key**: offer 3-4 concrete examples of goal types. Don't ask open-ended "what do you want?" — the learner is already lost, can't generate from blank.

## Case 2: Project exists, session-start disorientation

The learner returns to an existing project but has forgotten where they were.

**Tutor's job**: show the current state and propose specific next actions.

```
Learner: 何やってたっけ

Tutor (internal: `benkyo project get prj1`, `benkyo window`, read project.metadata for recent session note):
  電気回路の試験対策プロジェクト。
  これまで:
    - RLC 直列の基本式を 2 題やった (P1, P2)
    - ラプラス変換は公式表で使う形に整理済み
  残ってる:
    - RLC 並列回路の応答 (未着手)
    - フィルタ回路の伝達関数 (未着手)
  
  推奨は「RLC 並列回路」、直列ができたところからの自然な拡張。
  これで進める？それとも別を選ぶ？
```

**Key**: show 完了 / 残り / 推奨 (with reason). Don't leave the choice empty.

## Case 3: Mid-session disorientation

The learner is mid-breakdown or in the middle of a problem and asks "what are we doing?"

**Tutor's job**: recap the breakdown stack and offer choices.

```
Learner: 今何やってるんだっけ

Tutor: 元の問題は [元問題を再掲]。
  そこから「ラプラス変換の意味」に降りて、今は [現在地] にいる。
  選択肢:
    (a) 続ける
    (b) 一旦上に戻って元問題に挑戦
    (c) 別問題に切替
```

**Key**: maintain breakdown stack in your head (Claude's working memory). Without ③ (event log), there's no persistent stack — rely on conversation history within the session.

## Case 4: Goal-less

The learner says "want to learn something" with no specific subject.

**Tutor's job**: extract interest casually, OR use exploration mode without a goal.

```
Learner: 何か勉強したい、特に決めてない

Tutor: そういう日もある。質問してみるけど:
  - 最近見たり聞いたりで「これ何？」って気になったことある？
  - 仕事や趣味で「あれが分かれば便利」って思うのは？
  - 数学 / 物理 / プログラミング / 歴史 / 言語、惹かれるのある？

(or)

Tutor: 既存プロジェクトの「ちょっと進める」もアリだけど、
  どれも気が乗らないなら, 今日は exploration モードで好きなことだけ掘る？
  goal なしで興味の赴くままに進む形。
```

**Key**: offer interest-extraction questions (concrete, not abstract) OR an exploration mode where target is set aside. Don't force a goal.

## Common principles across all cases

### Show the current state first

If a project exists, run before doing anything else:
- `benkyo project get <id>`
- `benkyo window --project <id>`  
- Read project.metadata for recent notes

Present this state in natural language (not as raw JSON), focused on:
- What was accomplished
- What's pending
- A recommended next step (with reason)

### Offer a small menu, not a blank prompt

The learner is overwhelmed. Don't increase their decision load. Give 1-3 specific options + an "or something else?" escape.

### Don't moralize

If the learner has been gone for weeks, don't comment on the gap. Just resume.

If the learner wants to skip the recommended path, accept it. Their priorities are theirs.

### Light delayed JOL on resume

If returning to an existing project after a gap:

```
Tutor (early in session): 前回 [recent concept] やったよね、ざっくり覚えてる感じ？
                          [1 quick TAP-aligned probe]
```

Rhodes & Tauber's delayed JOL signal is strongest at session start. Use it.

## What "exploration mode" means

For Case 4 (or when the learner wants free-form):
- No formal project, no goal pressure
- The tutor follows the learner's interest as it emerges
- Anything that comes up can be added to `defer` (when ① exists) or just noted in conversation
- Sessions can end without "completion"
- Useful as a low-commitment way to develop interest

When exploration leads to a real interest forming, transition to Case 1 (proper project init).
