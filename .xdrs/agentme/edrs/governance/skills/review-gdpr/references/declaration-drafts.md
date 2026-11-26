# Declaration drafts

Starting points the skill shows in a report when the hub or an item is missing. They are proposals: the skill never creates them. Each draft is under 200 words. Replace every `<...>`; never invent facts about the application. Nothing here is legal advice.

## Opt-out hub (`adrs/principles/010-gdpr-applicability.md`)

Use only when the audit found no personal data.

```markdown
---
name: <scope>-adr-policy-010-gdpr-applicability
description: GDPR applicability of <application>: opted out, no personal data processed.
apply-to: <application>
valid-from: <YYYY-MM-DD>
---

# <scope>-adr-policy-010: GDPR applicability

## Context and Problem Statement
<Whether GDPR applies to this application. <40 words>

## Decision Outcome
**GDPR does not apply to <application>.**

### Details

#### 01-applicability
Status: opted-out
Reason: <why no personal data is processed>
Inventory: <data stores, logs and integrations reviewed, showing no personal data>
Owner: <team or person>
Review-date: <YYYY-MM-DD, at most 12 months ahead>
```

## Applicable hub

```markdown
#### 01-applicability
Status: applicable
Data-categories: <categories and tiers>
Explanation: <how GDPR applies to this application>

#### 02-roles
Status: pointer
Role: <controller|processor|joint>
Pointer: <relative path or URL>
Explanation: <what this means for the application>

#### 03-dpo
Status: not-applicable
Reasoning: <why Art. 37(1) is not met>
Owner: <team or person>
Review-date: <YYYY-MM-DD>
Explanation: <what this means for the application>
```

Continue with one entry for each remaining item: `ropa`, `dpia`, `processors-and-transfers`, `retention`, `lawful-bases-and-consents`, `dsr-and-breach-runbooks`. Items that cannot be not-applicable always use `Status: pointer`.

## Runbook skeleton

Propose headings taken from the checklists of agentme-edr-policy-408 rules 02 and 03, one heading per bullet, each to be filled by the owner. Mark the runbook owner, review date, last drill and case register at the top.
