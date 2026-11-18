---
name: test-question-bank
description: >
  Tests the exercise question bank with simulated respondents: each profile alone, all profiles together, Cronbach alpha per characteristic and a 500-person mixed stress test.
  Activate after any change to questions, characteristics, profiles, config.json or the engine formulas, or when asked to run the dry-run, simulation, stress test or alpha check.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-11-17
---

## Overview

Runs four simulated-respondent tests over the exercise registries and reports FAIL and WARN findings per profile, per profile pair and per characteristic. The focus is the questions and characteristics, not the software.

### Inputs

#### Required

- None.

#### Optional

- Registry folder (default `.xdrs/exercise/adrs/data/.assets`).
- Subset of tests: `per-profile`, `all-profiles`, `alpha`, `stress`.
- Population sizes and random seed.
- Run name.

### Outputs

#### Contents

- Chat summary of outcome, FAIL and WARN findings and likely causes (<250 words).
- `report.md` with tables per profile, per characteristic and per respondent type (uncapped: generated tables).
- `results.json` with all checks and numbers (uncapped: generated data).

#### Changes

- Creates the run folder `.tmp/test-question-bank/[run-name]/`.

### Halt Conditions

- The registry folder or one of its JSON files is missing.
- Registry lint fails.
- The script exits with an error other than a test FAIL.

### Runtime Requirements

- Node.js 18 or later.
- No packages to install.

## Instructions

Keep the chat summary <250 words and every intermediate message <100 words.

### Phase 1: Prepare

1. Run `node .xdrs/exercise/edrs/application/.assets/lint-registries.js`; halt if it reports errors.
2. Read `exercise-edr-policy-103-question-bank-testing` for the thresholds.
3. Choose a lowercase run name, or let the script use the `YYYYMMDDHHMMSS` timestamp. A taken name gets `-2`, `-3` appended.

### Phase 2: Run the tests

1. Run from the repository root:
   `node .xdrs/exercise/edrs/application/skills/test-question-bank/scripts/run.js --name [run-name]`
2. Use `--only per-profile,alpha` and smaller `--n-*` values only for quick checks while iterating. The accepting run MUST use the defaults.
3. The default run takes about 2.5 minutes. Run it with a wait of at least 300 seconds.
4. Use the same `--seed` to compare a run before and after a change.

| Test | Default people | What it finds |
|---|---|---|
| `per-profile` | 200 per profile | Levels not recovered, profile never reaching good enough, biased characteristics |
| `all-profiles` | 500 | Clashes from shared characteristics, false highs, profile pairs pulling each other |
| `alpha` | 1000 per profile | Characteristics answered inconsistently (LOW) or redundantly (HIGH), too few items |
| `stress` | 500 | Broken scores, wrong ordering of low, medium, high, weak identification, invalid respondents not flagged |

### Phase 3: Read and report

1. Read `Result` in `report.md`, then the table of each test that has findings.
2. For each FAIL, name the profile, characteristic or question to inspect and the probable cause (keying, weights, routes, item count, profile size).
3. Group WARN findings by test and cause; do not list identical items one by one.
4. State that respondents are simulated, so wording and real-world validity are not tested.
5. Send the summary and end the final chat message with `results-path: .tmp/test-question-bank/[run-name]/`.

### Phase 4: Act on findings

1. A FAIL MUST be fixed, then the full run repeated with the same seed.
2. A WARN MUST be fixed or justified to the user.
3. Do not edit thresholds, the policy or registries to make a finding disappear.

Work files go only in `.tmp/test-question-bank/[run-name]/`, never directly in `.tmp/test-question-bank/`. Use `.tmp/test-question-bank/.work/` for caches and the OS temp dir for throwaway scripts.

## Examples

- After adding questions to `sensory_differences`: run with defaults, find `alpha 0.91 > 0.9` for it, and report which profiles test it.
- After changing `profile_margin_stop`: run `--only per-profile`, then the full run before accepting.
- Reproduce a finding: run again with the same `--seed` and `--name`; the script appends `-2` to the folder.

## Edge Cases

- A profile with few characteristics (for example `ocd`) can WARN on good enough because its margin is near `profile_margin_stop`.
- A characteristic listed by several profiles is tested once per profile, so it can appear several times.
- A characteristic in no profile is not tested and raises a WARN.
- A new profile is picked up from the registry; no script change is needed.
- Fewer than 3 main items or 30 complete respondents gives "not measured", never a pass.

## Anti-Patterns

- **Mistake:** Treating a PASS as proof that the questions are valid.
  **Why it happens:** The report looks like a measurement of real people.
  **Instead:** State that respondents are simulated and only keying, weights, routes and arithmetic are tested.

- **Mistake:** Accepting a change after a quick `--only` or small-population run.
  **Why it happens:** The full run takes minutes.
  **Instead:** Use quick runs while iterating and the default full run before accepting.

- **Mistake:** Raising the noise or loosening a threshold until alpha or a check passes.
  **Why it happens:** It is faster than fixing the items.
  **Instead:** Fix keying, weights or items; thresholds change only through `exercise-edr-policy-103-question-bank-testing`.

- **Mistake:** Writing outputs directly in `.tmp/test-question-bank/`.
  **Why it happens:** The default folder looks like the output location.
  **Instead:** Use a run folder `.tmp/test-question-bank/[run-name]/`.

## References

- [003-skill-standards](../../../../../_core/adrs/principles/003-skill-standards.md)
- [023-skill-runtime-standards](../../../../../_core/adrs/principles/023-skill-runtime-standards.md)
- [exercise-edr-policy-103 - Question bank testing](../../103-question-bank-testing.md)
- [exercise-edr-policy-102 - Registry lint](../../102-registry-lint.md)
- [exercise-bdr-policy-604 - Question authoring](../../../../bdrs/product/604-question-authoring.md)
