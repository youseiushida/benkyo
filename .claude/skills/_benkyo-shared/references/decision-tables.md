# Quick decision tables

Look-up tables for common operational decisions. Each table maps a situation to an action.

## Treatment classification (procedural vs conceptual)

For each (project, concept) pair:

| Situation | Treatment | Reason |
|---|---|---|
| Material/textbook teaches via tables and formulas only | procedural | match the course's intent |
| Material/textbook teaches via derivation/proof | conceptual | match the course's intent |
| Learner explicitly says "use it as a tool" / "暗記でいい" | procedural | learner intent |
| Learner explicitly says "understand it" / "理解したい" | conceptual | learner intent |
| Concept is the project's stated goal | conceptual | goal-level usually requires understanding |
| Concept is far below the project's goal, used as background | procedural | conserve cognitive load |
| Time pressure (e.g., exam imminent) | procedural | efficient short-term gain |
| Rapid diagnostic shows learner already proficient | procedural | no value in conceptualizing what's mastered (Kalyuga) |
| Rapid diagnostic shows learner is true novice | conceptual default, but with heavy I-PS scaffolding |
| Unable to decide | conceptual (default) | safer, can release later if confirmed |

## Edge type selection (prereq vs related)

| Relationship | Edge type |
|---|---|
| X is necessary to understand/apply Y, AND directly used | prereq (X→Y, X is the prereq of Y; actually our convention is Y→X means Y depends on X) |
| Wait, careful: convention | We use direction "depends-on": `edge add --from Y --to X --type prereq` means Y depends on X |
| X and Y are often confused (mistakable for each other) | related (`confusable` style, no formal sub-type yet) |
| X and Y appear together in curriculum, but no dependency | related (`cooccurring` style) |
| X is a generalization of Y; Y is a special case | usually no edge; or related if learner conflates |
| X is mentioned in Y's reference (e.g., Y's chapter cites X) | NOT an edge unless X is actually used to understand Y |
| X and Y share notation | NOT an edge |
| X and Y are taught in same lecture/section but independently | NOT an edge |

**Edge direction for prereq**: `from` is the dependent, `to` is the depended-upon. To say "Laplace transform depends on definite integral":
```
benkyo edge add --from c_laplace --to c_definite_integral --type prereq
```

## Breakdown vs other responses

When learner says "分からない" / 「詰まった」:

| Learner's actual confusion | Response |
|---|---|
| Problem statement vocabulary | clarify terminology, no breakdown |
| Doesn't know which concept to apply | direct hint ("ここはラプラス変換を使う") — retrieval cue |
| Knows the concept name but doesn't understand it | breakdown begins |
| Knows the concept but can't apply | worked example or intermediate scaffold |
| Wants the answer immediately | provide answer + offer to revisit later |

## PS-I vs I-PS choice

For each session segment:

| Situation | Mode | Reason |
|---|---|---|
| Conceptual node, prereqs ready, novel target | **PS-I** | core PF setup; Sinha & Kapur g=0.36-0.87 |
| Procedural node | **I-PS** | provide reference, then practice (Adesope) |
| Learner is true novice (no relevant prereqs) | **I-PS** | Sinha & Kapur: low-graders showed reverse effect; scaffold needed |
| Time pressure | **I-PS** | PF needs delay for retention benefit |
| Learner explicitly requests direct teaching | **I-PS** | respect intent; offer PS-I later |
| Domain-general skill | **I-PS** | Sinha & Kapur g=-0.17 for domain-general |
| Calculation/manipulation skill | **I-PS + faded examples** | Bertsch d=0.92 for calculation in generation effect |

## Commit / release decision

### Commit (procedural → conceptual)

| Signal | Action |
|---|---|
| Learner explicit: "理解したい" | confirm + commit |
| Learner asks "なんで" twice on same concept | propose commit; confirm |
| Learner mis-applies procedural reference repeatedly | propose commit; confirm |
| Learner fails transfer to slightly varied problems | propose commit; confirm |
| Prereqs not in good shape | DON'T commit yet; fix prereqs first |
| Time pressure | DON'T commit; defer |

### Release (conceptual → procedural)

| Signal | Action |
|---|---|
| Learner explicit: "もういい、暗記で" | confirm + release |
| Stuck on this node despite 2-3 breakdown attempts | propose release; confirm |
| Time pressure expressed | propose release; confirm |
| Diminishing returns on deep approach | propose release; confirm |
| Node is the project's core goal | DON'T release; fundamental |
| Just committed; haven't given conceptual approach a chance | DON'T release; hysteresis (give 1 session) |

## Confidence × correctness (after a problem attempt)

| Confidence | Correct | Action |
|---|---|---|
| High | Correct | Verify process, consider release if procedural-eligible |
| High | Wrong | **HYPERCORRECTION moment** — explicit, contrasting correction; re-probe later in session |
| Low | Correct | Verify process; if genuine, plan reinforcement; if accidental, more practice |
| Low | Wrong | Standard correction via PS-I or worked example |

## Self-eval trust matrix

| When learner says "分かった" | Trust level | Action |
|---|---|---|
| Immediately after explanation | LOW | brief verification probe, TAP-aligned |
| Just after solving a problem | MEDIUM | one isomorphic variation problem |
| At start of next session, days later | HIGH (Rhodes & Tauber g=0.93) | one quick probe; mostly trust |
| "Ah, I knew that all along" (hindsight) | LOW | require explain-back |

## "I don't know where to start" handling

| Project state | Goal clarity | Approach |
|---|---|---|
| No project | Has subject ("X studied") | extract concrete goal problem; project create |
| No project | Goal-less ("just want to learn something") | exploration mode or interest extraction |
| Has project | Lost at session start | show current state (window, frontier, recent activity); propose 1-3 next steps |
| Has project | Lost mid-session | recap breakdown stack; offer continue/back/switch |
