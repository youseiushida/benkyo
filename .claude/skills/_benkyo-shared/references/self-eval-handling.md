# Handling learner self-evaluation

Learners are systematically unreliable about their own learning state — at least in the short term. The tutor must account for three biases and use the structure of session timing to extract reliable signal.

## Central principle

| Self-evaluation timing | Trust level | Why |
|---|---|---|
| Immediately after explanation/solving | LOW | fluency illusion, foresight bias |
| At start of a later session (delayed) | HIGH | Rhodes & Tauber 2011 — delayed-over-immediate JOL accuracy Hedges's *g* = 0.93 |
| Hindsight ("I knew it all along") | LOW | hindsight bias (Bjork 2013) |

## Three biases to correct for

### Stability bias

The learner assumes their memory state doesn't change over time. "I know this now" → "I'll know this tomorrow."

**Correction**: don't equate "knows now" with "will know later". Set up delayed JOL via session-end seed + session-start probe.

### Foresight bias

Reading a problem makes the learner think they can solve it. "This looks easy."

**Correction**: have the learner attempt before discussion. "じゃあやってみて" — even brief attempts catch foresight bias.

### Hindsight bias

Seeing the answer makes the learner think they would have known it. "Ah, I already knew that."

**Correction**: ask for explain-back. "なぜそうなるか説明してみて" — bypasses the recognition shortcut.

## Confidence × correctness matrix

When the learner attempts a problem, classify by their confidence + the outcome:

|  | Correct | Wrong |
|---|---|---|
| **High confidence** | Verify process briefly. Consider release if blackbox-eligible. | **HYPERCORRECTION moment** — Butterfield & Metcalfe: highest learning value. Explicit contrasting correction + re-probe later. |
| **Low confidence** | Verify process. If genuine: reinforce. If accidental: more practice. | Standard PS-I correction. |

### Each cell elaborated

**High confidence + correct**:
```
Tutor: 正解。ちなみに [process check question] のところはどう判断した？

(if process is sound:)
Tutor: 完璧。このまま release(暗記扱いに切替) する選択肢もある。どうする？
```

**High confidence + wrong** (CRITICAL — golden moment):
```
Tutor: ちょっと待って、ここ自信あったよね？
  実はこうで、理由はこう (explicit contrast with their reasoning).
  [later in session]: さっきの場面もう一回試してみよう。[same problem variation]
```

Re-probe later in the same session, AND seed for delayed re-probe in next session.

**Low confidence + correct**:
```
Tutor: 合ってる。自信なかった？どこが引っかかった？
```

If genuine reasoning (just hesitation): note as solidifying. If accidental (couldn't explain): treat as low-grasp; more practice.

**Low confidence + wrong**:
```
Tutor: ここ詰まったね。一緒に見てこう [PS-I sequence, instruction building on attempt]
```

Standard handling.

## Delayed JOL: protocol

### Session-end seed

Toward the end of a session, ask the learner to classify the day's concepts by confidence:

```
Tutor: 今日扱った内容で、明日も自分で説明できそうなのはどれ？
  自信あり / まあまあ / 自信ない、で分けてみて。
```

Important: **do NOT frame as "test"**. Bertsch's generation effect data shows incidental > intentional (d=0.65 vs d=0.32).

Record via `benkyo session end` — never call `events add` for these directly. The summary JSON's `delayed_jols` list becomes one `delayed_jol_recorded` event per entry, atomically alongside the `session_end` event:

```json
{
  "delayed_jols": [
    {"concept_id": "c1", "claim": "high"},
    {"concept_id": "c4", "claim": "mid"},
    {"concept_id": "c5", "claim": "low", "note": "Bromwich はそもそも苦手意識"}
  ],
  ...
}
```

Each entry's optional `note` is captured on that specific event's `notes` column — use it for the qualitative context behind the claim (the learner's wording, the observation that triggered the note).

### Session-start verification

Next session, recover the claims and verify the high-confidence ones:

```
benkyo events list --project <id> --kind delayed_jol_recorded --limit 10
```

Then probe (incidental framing):

```
Tutor: 前回ラプラス変換は自信ありって言ってたよね。軽くおさらいから。
  [TAP-aligned probe, 1 problem]
```

- If solved: delayed JOL was accurate. Trust other claims similarly. Release blackbox-eligible if appropriate.
- If failed: stability bias caught — write a `hypercorrection_detected` event for the cross-session re-probe pipeline:
  ```
  benkyo events add --kind hypercorrection_detected \
    --project <id> \
    --payload '{"concept_id": "c1", "prior_claim": "high", "current_state": "retrieval_failed"}' \
    --notes "<the learner's reaction, the canonical answer, the divergence>"
  ```

This catch is high-value evidence about the learner's self-evaluation accuracy and a target for next-session re-probing.

## "分かった" by situation

| Where it occurs | Trust | Verification |
|---|---|---|
| Immediately after explanation | LOW | TAP-aligned probe before moving on |
| Just after solving a problem | MED | one isomorphic variation problem |
| Next session start (delayed) | HIGH | one quick probe; mostly trust |
| "Ah, I knew that" (hindsight) | LOW | "なぜ" — explain back |

## "分からない" by situation

| Where it occurs | Likely cause | Response |
|---|---|---|
| At problem reading | foresight or true novice | rapid probe (Kalyuga first-step) to see |
| Mid-solving | classified stuck (see decision-tables) | matched response |
| During explanation | style mismatch or missing prereq | change angle or drop down |
| "Everything is unclear" | overload or motivation drop | break, narrow scope, propose release |

## Process > outcome verification

Even when the outcome is correct, verify the process. Outcome-only verification misses:
- Lucky guesses
- Memorized algorithms applied without understanding
- Surface-level pattern matching

Practical: after a correct answer, ask one process question. "Why did you use formula X here and not Y?" The answer reveals depth.

If the learner solved it correctly but can't articulate why → the concept isn't really integrated. Reinforce or transition handling carefully.

## Specific probes that work

### TAP-aligned ("transfer-appropriate processing")

Match the probe form to the eventual-use form. If they'll need to calculate things, probe with a calculation. If they'll need to explain things, probe with an explanation request.

Adesope: identical TAP yields g=0.63 vs dissimilar g=0.53.

### Variation probes (transfer test)

Take the just-solved problem and change one parameter. If they can solve the variation, the skill is transferable. If not, the original was surface-level.

### Explain-back

"Tell me in your own words why this works." Bypasses recognition-only knowledge.

## Anti-patterns

- **Trusting "I get it"**: virtually always premature.
- **Asking "are you sure?"**: invites defensive answers. Use probes instead.
- **Skipping verification for time**: the time savings are illusory — unverified knowledge erodes.
- **Punishing wrong answers**: high-confidence wrong is the GOLDEN moment, not the failure moment. Treat it as a gift.
- **Treating delayed JOL as a test**: incidental framing matters; "テストするよ" halves the effect.
