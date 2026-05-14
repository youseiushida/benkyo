# Eval test cases

Each benkyo skill has an `evals/evals.json` with realistic test prompts. These are starting points for the skill-creator eval framework.

## Structure

Each test case has:

- `id`: numeric
- `name`: short descriptive identifier
- `prompt`: a realistic learner utterance
- `expected_output`: a description (not assertions) of what the tutor should do, including which skills should trigger, what CLI calls are expected, and what vocabulary discipline should hold
- `files`: input files if any (currently none)

## Running formal evaluations

The skill-creator framework (`example-skills:skill-creator`) can run these in a comparison loop. The high-level workflow:

1. From each skill's directory, the eval framework spawns subagents for each prompt
   - **With-skill run**: subagent has access to the skill files
   - **Baseline run**: subagent has no skill access (or has the older skill version)
2. Output diffs are saved
3. An eval-viewer presents them side-by-side for human review
4. Quantitative assertions (boolean pass/fail) can be added per case after initial review

Detailed instructions are in `example-skills:skill-creator`'s SKILL.md.

## Adding test cases

When adding cases, prefer:

- **Realistic learner utterances** — what someone would actually say in conversation, not abstract requests
- **Coverage of edge cases** — error paths, vocabulary discipline failures, skill chaining
- **Concrete enough to verify** — vague prompts produce vague evaluations

Avoid:

- Overly clean "test data" that wouldn't appear in real sessions
- Prompts that test multiple skills at once (split into separate cases)
- Cases that depend on prior conversation state without explicit setup

## Status

Each skill has 3 starter cases. Run them through skill-creator to identify which scenarios produce different behaviors with vs without the skill, and iterate.
