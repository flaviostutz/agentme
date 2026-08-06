# Shared Module: Conflict Detection Between Governance Layers

## Purpose

This module provides LLM-agent instructions for detecting semantic and structural conflicts between `#### NN-rulename` rule blocks across all governance policies loaded for a scope. It is invoked from within skills (001-review, 002-write-policy, etc.) after all governance layers have been loaded and before any authoring or review work begins.

Lint tools enforce *structural* conflicts only (duplicate rule numbers with different content). This module handles *semantic* conflicts: two rules with different numbers that are logically incompatible.

## Instructions

### Step 1: Build the Governance Policy Map

For each governance layer loaded in precedence order (scope-type chain → follows-meta → local-meta), extract every `#### NN-rulename` rule block into a flat map:

```
policy_rules[rule_id] = {
  rule_id:      "NN-rulename"     # e.g., "01-file-naming"
  body:         <text after #### heading until next heading>
  source_file:  <path to policy file>
  precedence:   <integer; higher = later in chain = overrides earlier>
  declared_conflict_targets: [<list of rule_ids from ## Conflicts section>]
}
```

If two entries share the same `rule_id`, the one with higher precedence wins for authoring and review purposes.

### Step 2: Detect Structural Conflicts (Same Rule Number)

For every rule_id that appears more than once across the loaded policies:

1. Compare the bodies of all occurrences.
2. If any two occurrences have substantially different content:
   a. Check whether the higher-precedence policy's `## Conflicts` section lists the lower-precedence `rule_id`.
   b. **Declared conflict**: if listed → the override is valid; note it as an informational finding only.
   c. **Undeclared conflict**: if NOT listed → report as ERROR: `CONFLICT — Rule \`NN-rulename\` is defined differently in \`[source A]\` and \`[source B]\`. The override in \`[higher-precedence file]\` must declare this in its \`## Conflicts\` section before this scope's documents can be validated.`

### Step 3: Detect Semantic Conflicts (Different Rule Numbers)

For every pair of rules across all loaded policies:

1. Read each rule's body carefully.
2. Flag a SEMANTIC CONFLICT if the rules are logically incompatible — meaning a document that satisfies rule A cannot also satisfy rule B as written. Examples:
   - Rule A: "MUST NOT include a References section" / Rule B: "MUST include a References section"
   - Rule A: "filenames MUST be uppercase" / Rule B: "filenames MUST be lowercase"
3. Check whether the higher-precedence policy's `## Conflicts` section declares the pair.
4. **Declared semantic conflict**: if declared → note as informational finding.
5. **Undeclared semantic conflict**: report as WARNING: `SEMANTIC CONFLICT — Rule \`NN-ruleA\` in \`[file A]\` may be incompatible with rule \`NN-ruleB\` in \`[file B]\`. Review whether both can be satisfied simultaneously. If one overrides the other, add a \`## Conflicts\` declaration to the overriding policy.`

### Step 4: Report Findings

Summarise all detected conflicts before proceeding with the skill's main task:

```
### Conflict Analysis

**Undeclared structural conflicts (ERRORS — must fix before proceeding):**
- Rule `NN-rulename`: defined in `[file A, line N]` and `[file B, line N]` with different content. Declare the override in [file B]'s ## Conflicts section.

**Undeclared semantic conflicts (WARNINGS — review recommended):**
- Rules `NN-ruleX` (file A) and `NN-ruleY` (file B) may be incompatible: [brief reason].

**Declared overrides (informational):**
- Rule `NN-rulename` overridden by `[file B]` as declared in its ## Conflicts section.
```

If there are undeclared **structural** conflicts (ERRORs), halt the skill and do NOT continue until the conflicts are declared. Semantic conflicts are warnings; the skill may continue but must flag them to the user.

### Step 5: Apply Override Resolution

When a declared structural conflict exists (rule_id appears in both A and B, override is declared):
- Use the body from the higher-precedence policy for all authoring and review decisions.
- Cite the lower-precedence policy as "overridden by [file B] — see its ## Conflicts section".

When a declared semantic conflict exists:
- Apply both rules as written; the later-in-chain rule takes precedence on any direct contradiction.
- Note both rules as constraints in the authoring or review context.
