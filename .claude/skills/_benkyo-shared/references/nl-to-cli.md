# Natural language → benkyo CLI operation mapping

This is the translation layer between what the learner says (in natural language) and what the tutor (Claude Code) does internally with `benkyo` CLI. The learner does NOT know about procedural/conceptual/treatment/cut/prereq/related/node/edge/window — these are all internal vocabulary.

When the learner uses one of those terms unprompted, accept it; but never introduce them yourself.

## A. Goal setting / project init

| Learner says | Meaning | Internal action |
|---|---|---|
| 「○○を勉強したい」「I want to study X」 | new project or extend existing | `project list` → if none for X, propose `project create`; if one exists, propose resuming |
| 「○○の試験勉強」「exam prep for X」 | test-prep project | `project create` + ask for materials (syllabus, past exams) |
| 「○○ができるようになりたい」「I want to be able to do Y」 | concrete goal expression | translate to a problem node; `problem add` or identify existing |
| 「これ全部知ってる」「I already know all this」 | expertise self-declaration | run a brief rapid diagnostic (1-2 probes); if confirmed, mark related concepts procedural |

## B. Concept queries

| Learner says | Meaning | Internal action |
|---|---|---|
| 「Xって何？」「What is X?」 | identification query | `treatment get`; if procedural → reference; if conceptual → brief intro + "want to dig in?" |
| 「X についてもっと」「Tell me more about X」 | depth request, commit candidate | confirm intent → `treatment unset` (or `set conceptual`) and ensure prereqs |
| 「X 知らない」「Don't know X」 | unknown to learner | choose breakdown or reference based on treatment + context |
| 「Xって Y と違うの？」「Is X different from Y?」 | confusion signal | compare contents, consider adding `related` edge for the confusable pair |

## C. Treatment shifts

| Learner says | Meaning | Internal action |
|---|---|---|
| 「理解したい」「腹落ちしたい」「導出やりたい」「なぜそうなるの？」 | want conceptual treatment | `treatment unset` or `treatment set conceptual` + ensure 1-level prereqs exist (default procedural) |
| 「公式覚えれば」「暗記で」「表があれば十分」「道具として割り切る」 | want procedural treatment | `treatment set --procedural --reference <prepared content>` |
| 「もうちょっと深く」「突き詰めたい」「上に上げて」 | commit signal | same as conceptual want |
| 「もういい、戻して」「ざっくりで」「飛ばして」 | release signal | prepare reference, `treatment set --procedural` |

## D. Problem actions

| Learner says | Meaning | Internal action |
|---|---|---|
| 「問題やる」「テストして」「やってみたい」 | want a problem | `window` + select goal-adjacent unsolved problem |
| 「次の問題」「次」 | next problem | same; prefer unsolved |
| 「分からない」「詰まった」 | stuck | classify stuck-type (see lost-learner-handling.md); choose appropriate response |
| 「答え見たい」「もう答え」 | direct-answer request | present answer + offer to review process or revisit later |
| 「もう一回」 | retry | same problem or near-isomorph |
| 「もっと簡単なやつ」 | want easier problem | move toward prereqs; offer a sub-problem of the prereq chain |

## E. Navigation

| Learner says | Meaning | Internal action |
|---|---|---|
| 「次」 | continue | proceed with current context's next step |
| 「戻る」 | back up | unwind one level in breakdown, or return to original problem |
| 「別のやって」 | switch context | choose another problem or concept |
| 「今日はここまで」「終わり」 | end session | run session-wrap protocol (see session-boundaries.md) |
| 「休憩」 | break | wait; no CLI action |

## F. Status / orientation

| Learner says | Meaning | Internal action |
|---|---|---|
| 「今何やってる？」 | current location | summarize breakdown stack + original problem |
| 「どこまでやった？」 | progress check | `window` + completed-problem history from project metadata |
| 「残ってる物は？」 | remaining items | `frontier` (procedural promotion candidates) + uncompleted problems |
| 「全体見せて」 | overview | `render --format mermaid` and present visually |

## G. Graph edits (occasional)

| Learner says | Meaning | Internal action |
|---|---|---|
| 「これとあれは関連してる」 | add related edge | `edge add --type related` |
| 「これは別物」 | edge is wrong | `edge delete` |
| 「これも追加して」 | new concept/problem | `concept add` or `problem add` + edges; ALWAYS run `concept find` first for identity |
| 「これとこれ同じ」 | merge candidate | `concept merge` (when implemented; for now: manual edge redirect + delete) |
| 「これは細かく分けたい」 | split candidate | `concept fork` (when implemented) + manual edge redistribute |

## H. Meta / style (no CLI action)

| Learner says | Meaning | Response style change |
|---|---|---|
| 「もっと丁寧に」「もう少し詳しく」 | longer explanation | increase elaboration |
| 「短く」「一言で」 | shorter explanation | be concise |
| 「もう一回」 (to an explanation) | re-explain | re-explain from a different angle |
| 「具体例を」 | example | provide a concrete example (not necessarily in graph) |
| 「比喩で」 | analogy | use an analogy from familiar domains |

## Implicit signals (read from the form of the utterance)

These don't appear as direct mappings but inform interpretation:

| Signal | Interpretation | Response |
|---|---|---|
| Question form ("〜って何？", "なんで？") | concept query or conceptual gap | brief explanation + offer to dig |
| Imperative ("教えて", "やって") | instruction request | direct response of that type |
| Negation ("違う", "分からない") | stuck or correction needed | stuck-handling protocol |
| Affirmation ("分かった", "OK") | progress signal — but stability bias applies | light verification probe |
| Silence / long delays | thinking or stuck | wait; if extended, ask gently |
| "あ、それ知ってる" | spontaneous expertise claim | procedural candidate; brief diagnostic |
| "あー、なるほど" | comprehension claim | high-risk; verify with delayed JOL or probe |
| Typo/short messages | low-stakes thinking | don't over-react |

## Two cardinal rules

1. **Never expose internal vocabulary** (procedural/conceptual/treatment/cut/prereq/related/node/edge/window/traversal) in learner-facing utterances. Translate to natural language.

2. **When in doubt, ask in natural terms.** Better to confirm "ここは公式使えればいい？それとも導出も？" than to silently make a treatment decision the learner didn't intend.
