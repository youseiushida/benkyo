# Natural language → benkyo CLI operation mapping

This is the translation layer between what the learner says (in natural language) and what the tutor (Claude Code) does internally with `benkyo` CLI. The learner does NOT know about blackbox/whitebox/treatment/cut/prereq/related/node/edge/window/event/log/record/schema/JSON — these are all internal vocabulary.

When the learner uses one of those terms unprompted, accept it; but never introduce them yourself.

## A. Goal setting / project init

| Learner says | Meaning | Internal action |
|---|---|---|
| 「○○を勉強したい」「I want to study X」 | new project or extend existing | `project list` → if none for X, propose `project create`; if one exists, propose resuming |
| 「○○の試験勉強」「exam prep for X」 | test-prep project | `project create` + ask for materials (syllabus, past exams) |
| 「○○ができるようになりたい」「I want to be able to do Y」 | concrete goal expression | translate to a problem node; `problem add` or identify existing |
| 「これ全部知ってる」「I already know all this」 | expertise self-declaration | run a brief rapid diagnostic (1-2 probes); if confirmed, mark related concepts blackbox |

## B. Concept queries

| Learner says | Meaning | Internal action |
|---|---|---|
| 「Xって何？」「What is X?」 | identification query | `treatment get`; if blackbox → reference; if whitebox → brief intro + "want to dig in?" |
| 「X についてもっと」「Tell me more about X」 | depth request, commit candidate | confirm intent → `treatment unset` (or `set whitebox`) and ensure prereqs |
| 「X 知らない」「Don't know X」 | unknown to learner | choose breakdown or reference based on treatment + context |
| 「Xって Y と違うの？」「Is X different from Y?」 | confusion signal | compare contents, consider adding `related` edge for the confusable pair |

## C. Treatment shifts

| Learner says | Meaning | Internal action |
|---|---|---|
| 「理解したい」「腹落ちしたい」「導出やりたい」「なぜそうなるの？」 | want whitebox treatment | `treatment unset` or `treatment set whitebox` + ensure 1-level prereqs exist (default blackbox) |
| 「公式覚えれば」「暗記で」「表があれば十分」「道具として割り切る」 | want blackbox treatment | `treatment set --blackbox --reference <prepared content>` |
| 「もうちょっと深く」「突き詰めたい」「上に上げて」 | commit signal | same as whitebox want |
| 「もういい、戻して」「ざっくりで」「飛ばして」 | release signal | prepare reference, `treatment set --blackbox` |

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
| 「残ってる物は？」 | remaining items | `frontier` (blackbox promotion candidates) + uncompleted problems |
| 「全体見せて」 | overview | `render --format mermaid` and present visually |

## G. Graph edits (occasional)

| Learner says | Meaning | Internal action |
|---|---|---|
| 「これとあれは関連してる」 | add related edge | `edge add --type related` |
| 「これは別物」 | edge is wrong | `edge delete` |
| 「これも追加して」 | new concept/problem | `concept add` or `problem add` + edges; ALWAYS run `concept find` first for identity |
| 「これとこれ同じ」 / 「これとこれまとめて」 | merge candidate | `concept find` で identity 検証 → `concept merge <source> --into <canonical>` で edges + project_concepts を redirect。treatment 衝突時は `--on-conflict <error\|keep_canonical\|keep_source>` で解決。problem は `problem merge` で同様 |
| 「これは細かく分けたい」 / 「これは別物にしたい」 | split candidate | granularity 5 criteria で確認 → `concept fork <source> --content <new content>` で新概念を作成 (edges は copy, treatments は **copy されない** = project ごとに再設定が必要) → 元概念から不要 edge を `edge delete` |

## H. Session boundaries and history (events log)

The events log is the persistence layer for cross-session reasoning. Skills
write to it on state changes and read from it at session boundaries. The
learner never hears the word "event" or "log".

| Learner says | Meaning | Internal action |
|---|---|---|
| 「今日はここまで」 + recap context | session-wrap (clean) | `session end --project <id> --summary-file <json>` (atomically writes session_end + delayed_jol_recorded events) |
| 「急用、また」 | abrupt end | `session end` with minimal summary (`{"pending": [...current location...], "notes": "interrupted"}`) — skip delayed_jols solicitation |
| 「久しぶり」「何やってたっけ」 | resume after gap | `events list --project <id> --kind delayed_jol_recorded --limit 10` to recover what learner claimed to remember; probe those (incidental framing) |
| 「あれ、覚えてない」 | retrieval failure post-claim | `events add --kind hypercorrection_detected --payload {concept_id, prior_claim, current_state}` for re-probing later |

| Internal action | Surface in natural language as |
|---|---|
| `events add --kind delayed_jol_recorded` | "覚えてられそうなの、自信あり/まあまあ/自信ないで教えて" (never "JOL", never "event", never "record") |
| `events list --kind session_end` for project history | "前回 [概念名] までいったね", "[項目名] は [日付] にやった" (paraphrase as natural recall) |
| `session end` invocation | (silent action; or "メモしといた") — never "session_end event を書いた" |
| `events add --kind hypercorrection_detected` | (silent action; or "ここ後で確認しよう") |

## I. Meta / style (no CLI action)

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
| Question form ("〜って何？", "なんで？") | concept query or whitebox gap | brief explanation + offer to dig |
| Imperative ("教えて", "やって") | instruction request | direct response of that type |
| Negation ("違う", "分からない") | stuck or correction needed | stuck-handling protocol |
| Affirmation ("分かった", "OK") | progress signal — but stability bias applies | light verification probe |
| Silence / long delays | thinking or stuck | wait; if extended, ask gently |
| "あ、それ知ってる" | spontaneous expertise claim | blackbox candidate; brief diagnostic |
| "あー、なるほど" | comprehension claim | high-risk; verify with delayed JOL or probe |
| Typo/short messages | low-stakes thinking | don't over-react |

## Three cardinal rules

1. **Never expose internal vocabulary** (blackbox/whitebox/treatment/cut/prereq/related/node/edge/window/traversal/event/log/record/schema/JSON/metadata, plus internal IDs `c<n>` / `p<n>` / `prj<n>` / `e<n>`) in learner-facing utterances. Translate to natural language.

2. **When in doubt, ask in natural terms.** Better to confirm "ここは公式使えればいい？それとも導出も？" than to silently make a treatment decision the learner didn't intend.

3. **Events inform expectations, never replace evidence.** The events log is a *prior* for what to probe and how aggressively — it is never a *conclusion* about what the learner currently knows. Past `delayed_jol_recorded` with `claim: high` means "probe this lightly first" — not "skip this concept." Foresight bias (Bjork 2013) applies symmetrically to skills reading their own logs.
