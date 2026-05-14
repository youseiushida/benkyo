# Literature pointers

Which operational decision is based on which paper. Use when debugging "why are we doing this?" or when proposing a change to the rules.

## Sinha & Kapur (2021), *Review of Educational Research* — Productive Failure meta-analysis

**Key effect**: PS-I (problem solving then instruction) outperforms I-PS for conceptual knowledge and transfer. Hedge's g = 0.36 [95% CI 0.20, 0.51], adjusted for publication bias = 0.87.

**Used for**:
- Default PS-I mode for conceptual treatment
- The "instruction building on student solutions" requirement (β = 0.27-0.28, the strongest predictor)
- Multiple-RSM generation step (have learner consider alternatives)
- Recognizing that low-graders and domain-general skills show reversed effect (use I-PS for true novices and domain-general)
- Procedural knowledge has g ≈ -0.03 (no PS-I advantage), justifying I-PS for procedural treatment

**Boundary**: PF requires *relevant* prior knowledge to activate. Cut and treatment must be set such that the conceptual node's prereqs are at sufficient level.

## Kalyuga (2007), *Educational Psychology Review* — Expertise reversal effect

**Key effect**: instructional methods effective for novices become harmful for experts. As expertise grows, scaffolding should decrease.

**Used for**:
- The treatment lifecycle (procedural for proficient items, conceptual for items to be understood)
- Rapid diagnostic methods (first-step approach: show problem, ask the next move; r = 0.92 with traditional knowledge tests, 4.9x time reduction)
- Tutorial adaptation: ES = 0.46 for adapted vs non-adapted (Kalyuga & Sweller 2004)
- Avoiding over-scaffolding when learner is fluent — reduces breakdown depth, releases treatment

**Used to justify**:
- Reducing breakdown depth as expertise grows
- Releasing concepts to procedural when learner is consistently solving
- Initial cut decision based on learner's existing skill

## Rhodes & Tauber (2011), *Psychological Bulletin* — Delayed JOL meta-analysis

**Key effect**: delayed judgments of learning (JOLs) are far more accurate than immediate ones. Gamma correlation g = 0.93 (delayed) vs much lower for immediate.

**Used for**:
- Session-end JOL seed + session-start verification protocol
- Trust calibration: trust learner's "I know X" only after delay
- Identifying stability-bias cases (high confidence at session end, failure at session start)

## Bjork, Dunlosky & Kornell (2013), *Annual Review of Psychology* — Self-Regulated Learning

**Key effects**:
- Stability bias: learners assume their memory state doesn't change.
- Foresight bias: reading a problem makes it seem solvable.
- Hindsight bias: seeing the answer makes it seem known.
- Fluency illusions during encoding.

**Used for**:
- The verification probe principle (don't trust immediate "分かった")
- Anticipation step (Kornell et al. 2009: 8s wrong guess + 5s study > 13s study)
- Treating learner self-evaluation as low-trust evidence
- Justification for objective state tracking (don't trust subjective reports)

## Bertsch et al. (2007), *Memory & Cognition* — Generation effect meta-analysis

**Key effect**: d = 0.40 overall benefit of generating vs reading. Modifiers:
- Calculation tasks: d = 0.92 (largest)
- Anagrams: d = -0.05 (only negative one — when too disconnected from cues)
- Incidental learning: d = 0.65 vs intentional d = 0.32 (don't frame as "test")
- 1+ day delay: d = 0.64 (effect grows with delay)
- Lists > 50: effect disappears (don't overload)

**Used for**:
- Have learner attempt before being told (incidental framing)
- "Don't say テスト" rule for probes
- Limit number of concepts in one session (cognitive load)
- Calculation tasks are especially valuable for generative practice

## Adesope, Trevisan & Sundararajan (2017), *Review of Educational Research* — Practice testing meta-analysis

**Key effect**: g = 0.61 overall benefit of retrieval practice vs other study methods.

**Modifiers**:
- vs restudy: g = 0.51
- vs filler: g = 0.93
- 1-6 day retention interval: g = 0.82 (peak)
- TAP (identical formats): g = 0.63 vs dissimilar g = 0.53
- Robust across classroom and lab settings

**Used for**:
- The probe-based verification approach
- Session interval recommendation (1-6 days for retention)
- TAP-aligned probe design (probe matches eventual-use form)
- Justification for retrieval-based tutoring (vs re-explaining)

## Brunmair & Richter (2019), *Psychological Bulletin* — Interleaving meta-analysis

**Key effect**: g = 0.42 overall. Heavy material-type moderation:
- Paintings: g = 0.67
- Math tasks: g = 0.34
- Expository texts: n.s.
- Word lists: g = -0.39 (blocking is better)
- 10-30s spacing between items kills the effect (g drops to 0.22)
- Higher between-category similarity → stronger interleaving benefit
- Higher within-category similarity → weaker interleaving benefit

**Used for**:
- The `related` edge type semantics (confusable vs cooccurring distinction)
- Limitation acknowledgment: interleaving is mostly session-internal, not cross-session (SRS scheduling kills it)
- Recognition that math/concept content gives modest interleaving benefit, not paintings-like

## Bjork & Bjork (1992) — Storage strength / retrieval strength

**Theoretical foundation**: storage strength (how well-learned) and retrieval strength (current accessibility) are dissociable. Retrieval reinforces, disuse degrades retrieval but not storage.

**Used for**:
- General mental model of learning (referenced but not directly operationalized in this skill, since ③ doesn't exist)
- Retrieval competition: related concepts compete; reviewing one can transiently weaken another. Influences related-edge handling.

**Caveat**: FSRS is built on this framework but is calibrated for flashcard retention, not academic concept understanding. Don't over-apply.

## Murre & Dros (2015), *PLOS One* — Ebbinghaus replication

**Key finding**: replicates forgetting curve. 24-hour bump exists but varies by subject.

**Used for**:
- General awareness of forgetting (no direct operational rule here)

## Butterfield & Metcalfe — Hypercorrection effect

**Key effect**: errors made with high confidence are corrected most strongly when given feedback. Replicated multiple times since 2001.

**Used for**:
- The confidence × correctness matrix (high-confidence wrong = golden teaching moment)
- Explicit correction protocol with later re-probe in same session

## Quick "why are we doing X?" lookup

| Decision | Primary paper |
|---|---|
| Default PS-I for conceptual | Sinha & Kapur |
| Default I-PS for procedural | Sinha & Kapur (g≈0 for procedural) |
| Anticipation step | Bjork 2013 / Kornell |
| Incidental framing of probes | Bertsch |
| Trust delayed JOL, not immediate | Rhodes & Tauber |
| 3 biases (stability/foresight/hindsight) | Bjork 2013 |
| Hypercorrection (high-conf wrong) | Butterfield & Metcalfe |
| Rapid diagnostic for expertise | Kalyuga |
| Reduce scaffold as expertise grows | Kalyuga (expertise reversal) |
| 1-6 day spacing for review | Adesope |
| TAP-aligned probes | Adesope |
| Interleaving (session-internal) | Brunmair & Richter |
| Related-edge confusable semantics | Brunmair & Richter |
| FSRS as inspiration (not direct) | Bjork & Bjork 1992 |
