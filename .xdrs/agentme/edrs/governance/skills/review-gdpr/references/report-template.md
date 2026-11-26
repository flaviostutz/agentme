# Report template

Show this in chat and save it as `.tmp/review-gdpr/<id>/report.md`. Findings are uncapped in number; each field has a hard cap. Keep `## Summary` under 50 words. Never include personal data values.

```text
### GDPR Review
Scope: [application path or XDRS scope]
Run: [id]
Disclaimer: Not legal advice; not a compliance certificate.

## Findings
### 1. [ERROR|WARNING] - [file:line](file:line)
- Title of the finding (<15 words)
- Policy reference: [policy-name.NN-rule-title](policy-file:line)
- Why: Brief description of the issue (<20 words)
- Fix: Specific action, including the protection to apply (<20 words)
- Relevance: Why this matters (<15 words)

### 2. [second finding etc]

## Proposed drafts
### [Hub or item name]
[Draft from declaration-drafts.md, <200 words, marked "proposal, not created"]

## Summary
- Errors: [count]
- Warnings: [count]
- Outcome: [PASS|FAIL]
```

Outcome is FAIL when any ERROR exists. `check` findings use the same shape with the hub file as location.

When the audit stops early because of a valid opt-out, write one line under Findings: `No findings: opt-out valid until [date]`.

## Example finding

```text
### 1. [ERROR] - [src/db/schema.sql:42](src/db/schema.sql:42)
- Column holding a birth date has no retention entry
- Policy reference: [agentme-adr-policy-201-personal-data-retention-and-erasure.01-retention-per-category](.xdrs/agentme/adrs/data/201-personal-data-retention-and-erasure.md:30)
- Why: Personal data without a declared retention period or purge.
- Fix: Add the category to the retention item with a period and a purge job.
- Relevance: Storage limitation is audited first.
```
