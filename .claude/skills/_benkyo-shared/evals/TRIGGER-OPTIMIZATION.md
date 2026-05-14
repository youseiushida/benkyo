# Description trigger optimization

Each skill has a `evals/trigger-eval.json` with should-trigger and should-not-trigger query sets. These can be fed into `example-skills:skill-creator`'s `run_loop.py` for automated description optimization.

## Files

| Skill | Path |
|---|---|
| benkyo-tutoring | `.claude/skills/benkyo-tutoring/evals/trigger-eval.json` |
| benkyo-project-init | `.claude/skills/benkyo-project-init/evals/trigger-eval.json` |
| benkyo-treatment-shift | `.claude/skills/benkyo-treatment-shift/evals/trigger-eval.json` |
| benkyo-graph-edit | `.claude/skills/benkyo-graph-edit/evals/trigger-eval.json` |
| benkyo-session-wrap | `.claude/skills/benkyo-session-wrap/evals/trigger-eval.json` |

Each file has ~8 should-trigger + ~8 should-not-trigger queries, mixing:

- Direct trigger phrases from the description
- Indirect phrasings of the same intent
- Adjacent-but-different scenarios (other benkyo skills' territory)
- Completely unrelated tasks (coding, scheduling, etc.) — as negative cases

## Running the optimization

From the project root:

```bash
# Example for benkyo-tutoring:
python -m scripts.run_loop \
  --eval-set .claude/skills/benkyo-tutoring/evals/trigger-eval.json \
  --skill-path .claude/skills/benkyo-tutoring \
  --model claude-opus-4-7 \
  --max-iterations 5 \
  --verbose
```

(Path to `run_loop` and exact arguments are documented in `example-skills:skill-creator`.)

The script:

1. Splits eval set 60/40 train/test
2. Evaluates current description (3 runs each query for stability)
3. Generates description variants
4. Selects best by held-out test set score (avoids overfitting)
5. Writes results + best description to HTML report

## Manual review notes

The current descriptions were written "pushy" (per skill-creator guidance) to combat under-triggering. Initial check passed for the obvious cases — concrete proposals for the descriptions to be tested:

- All descriptions include explicit Japanese trigger phrases since the primary user language is Japanese
- The descriptions overlap somewhat (e.g., benkyo-tutoring and benkyo-treatment-shift both mention 「理解したい」). This is OK — both can trigger simultaneously and complement each other
- Potential improvements to test:
  - Add English phrasings for international users
  - Tighten the negative space (when NOT to trigger) more explicitly
  - Reduce overlap if simultaneous-trigger creates noise in actual sessions
