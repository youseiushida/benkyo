# Literature pointers

Which operational decision is based on which paper. Use when debugging "why are we doing this?" or when proposing a change to the rules.

> **Terminology bridge**. The math-education literature we cite (Sinha & Kapur, Hiebert & Lefevre) uses the terms **"conceptual knowledge"** (understand the why) and **"procedural knowledge"** (apply the formula). benkyo implements these as the per-project **whitebox** (deep) and **blackbox** (tool-use) treatments. The bridge: paper's "conceptual" ≈ benkyo's "whitebox"; paper's "procedural" ≈ benkyo's "blackbox". We renamed in v0.3.0 to avoid the ACT-R sense of "procedural" (= automated expert knowledge), which is the opposite axis from what the math-ed papers mean.

## Sinha & Kapur (2021), *Review of Educational Research* — Productive Failure meta-analysis

**Key effect**: PS-I (problem solving then instruction) outperforms I-PS for conceptual knowledge and transfer. Hedge's *g* = 0.36, 95% CI [0.20, 0.51]. Egger's test and trim-and-fill detected no funnel-plot asymmetry, but a p-curve-based alternative estimate (van Aert et al. 2016 method) put the true effect at *g* = 0.87 — i.e., the 0.36 main estimate may be a lower bound under that method, not a center of an interval. **Don't quote it as "0.36–0.87" — it's two different estimators**.

**Used for**:
- Default PS-I mode for whitebox treatment
- Identifying **"instruction building on student solutions"** as a key fidelity factor. The cleanest evidence is the subgroup contrast (Table 3): PS-I *with* instruction-building yields *g* = 0.56; PS-I *without* it yields *g* = 0.20 (subgroup *p* = .02). Note: by Pearson importance this predictor ranks at the top (~.28), but its multiple-regression β collapses to ≈ 0.01 once correlated predictors are included — so report the subgroup *g*, not a β coefficient.
- Multiple-RSM generation step (have learner consider alternatives) — this is one of the predictors that **does** have a nonzero β in the regression (β ≈ 0.27).
- Recognizing that low-graders and domain-general skills show reversed effect (use I-PS for true novices and domain-general; domain-general subgroup *g* = -0.17).
- Procedural knowledge has *g* ≈ -0.03 (no PS-I advantage), justifying I-PS for blackbox treatment.

**Boundary**: PF requires *relevant* prior knowledge to activate. Cut and treatment must be set such that the whitebox node's prereqs are at sufficient level.

## Kalyuga (2007), *Educational Psychology Review* — Expertise reversal effect

**Key effect**: instructional methods effective for novices become harmful for experts. As expertise grows, scaffolding should decrease.

**Used for**:
- The treatment lifecycle (blackbox for proficient items, whitebox for items to be understood)
- Rapid diagnostic methods (first-step approach: show problem, ask the next move; **correlations up to** *r* = 0.92 with traditional knowledge tests across a series of studies, **with time reductions up to** 4.9x; Kalyuga 2006d / Kalyuga & Sweller 2004, as reviewed in Kalyuga 2007)
- Tutorial adaptation: ES = 0.46 for adapted vs non-adapted (Kalyuga & Sweller 2004)
- Avoiding over-scaffolding when learner is fluent — reduces breakdown depth, releases treatment

**Used to justify**:
- Reducing breakdown depth as expertise grows
- Releasing concepts to blackbox when learner is consistently solving
- Initial cut decision based on learner's existing skill

## Rhodes & Tauber (2011), *Psychological Bulletin* — Delayed JOL meta-analysis

**Key effect**: delayed judgments of learning (JOLs) are far more accurate than immediate ones. Across 4,554 participants and 112 effect sizes, the delayed-over-immediate advantage in JOL accuracy (operationalized as gamma correlations between JOLs and later recall) corresponds to a meta-analytic Hedges's *g* = 0.93. **Important**: the 0.93 is the *effect size of the delayed-vs-immediate comparison*, not a gamma value itself. The gamma correlations are the inputs being compared; their absolute values vary by study.

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
- 1+ day delay: d = 0.64 (effect grows with delay; though not strictly monotonic)
- Lists > 50 items: effect shrinks to d = 0.09, 95% CI [0.07, 0.11] — still positive but small; don't overload

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
| Default PS-I for whitebox | Sinha & Kapur (g = 0.36 [0.20, 0.51]) |
| Default I-PS for blackbox | Sinha & Kapur (g ≈ -0.03 for blackbox) |
| Instruction-building emphasis | Sinha & Kapur (subgroup g = 0.56 with vs 0.20 without; p = .02) |
| Anticipation step | Bjork 2013 / Kornell |
| Incidental framing of probes | Bertsch (d = 0.65 incidental vs 0.32 intentional) |
| Trust delayed JOL, not immediate | Rhodes & Tauber (Hedges's g = 0.93 for delayed-vs-immediate gamma comparison) |
| 3 biases (stability/foresight/hindsight) | Bjork 2013 |
| Hypercorrection (high-conf wrong) | Butterfield & Metcalfe |
| Rapid diagnostic for expertise | Kalyuga |
| Reduce scaffold as expertise grows | Kalyuga (expertise reversal) |
| 1-6 day spacing for review | Adesope |
| TAP-aligned probes | Adesope |
| Interleaving (session-internal) | Brunmair & Richter |
| Related-edge confusable semantics | Brunmair & Richter |
| FSRS as inspiration (not direct) | Bjork & Bjork 1992 |
