# research.md and proposal draft templates

Templates used by the `research-topic` skill. Placeholders show the word cap of each generated text. Replace every placeholder, edit the file in place, and never leave superseded text beside its replacement. Tables and source lines are structured data and carry no cap.

## research.md

Location: `.tmp/research-topic/<topic-slug>/research.md`. Sections appear in this order, and a section stays empty ("none yet") until its phase runs.

```text
# Research: <topic title <12 words>

status: in-progress | verified | unverified
phase: <last completed phase number, 0 to 8>
intent: fix | enhance | follow-up need | decide | understand-only
generation: <current Gen-N number>

## Framing
- Problem: <the real problem <60 words>
- Intention: <what the person wants to achieve <40 words>
- Success criteria: <up to 3 checkable criteria, each <20 words>
- Constraints: <up to 4 constraints, each <20 words>
- Why unsolved (human side): <context, ownership, priorities <60 words>

## Landscape
- <finding <40 words> [S#]
- Key terms: <term: technical definition <25 words> [S#]>
- Why unsolved (evidence): <previous attempts, blockers <60 words> [S#]

## Pillars
| ID | Pillar | Question it answers |
|---|---|---|
| P1 | <name <6 words> | <question <20 words> |

## Hypotheses
| ID | Gen | Statement | Falsifier | Status |
|---|---|---|---|---|
| H1 | 1 | <candidate answer <30 words> | <what would prove it false <25 words> | open |

Status values: open, supported, contradicted, mixed, evolved, dropped. A mixed or contradicted hypothesis becomes evolved and points to its Gen-N+1 successor.

## Evidence
### H1
- Supporting: <finding <40 words> [S#]
- Contradicting: <finding <40 words> [S#]
- Existing solutions: <solution <30 words> [S#]
- Verdict: <why this status <40 words>

## Solutions
| ID | Option | Addresses | Evidence | Meets criteria | Cost / risk | Status |
|---|---|---|---|---|---|---|
| S1 | <option <25 words> | H1 | [S#] | yes / partly / no | <cost and risk <25 words> | candidate |

Status values: candidate, grounded, shortlisted, chosen, rejected. A rejected option keeps its reason.

## Deferred Risks
- <skipped or unresolved item <30 words> (phase N)

## Query log
1. <phase, hypothesis or gate> | <query text> | <results used or none> | <date>

## Sources
| ID | Location | Accessed | Type | Audit note |
|---|---|---|---|---|
| S1 | <https URL, workspace path or user> | 2026-10-17 | primary / secondary / opinion | <author, date, independence, bias <30 words> |
```

Rules:
- Every Landscape, Evidence and Solutions line carries a source tag `[S#]`, or `[llm-unverified]` when it comes only from model knowledge.
- `[llm-unverified]` never counts as supporting evidence and never makes a solution chosen.
- Queries in the query log carry no PII and no security details.
- Questions, answers and dry-run results never enter the file.
- `status` is `unverified` when no supporting evidence has a real source.

## Hypothesis and solution examples

Hypothesis row, typical:

| ID | Gen | Statement | Falsifier | Status |
|---|---|---|---|---|
| H2 | 1 | Onboarding fails because setup docs drift from the repo, not because tools are missing | Most failures trace to missing tools | supported [S3, S5] |

Evidence entry, edge case (LLM-only claim):

```text
- Supporting: Pairing sessions halve ramp-up time [llm-unverified]. Not counted as support; searched next round.
```

Solution comparison:

| Option | Addresses | Evidence | Meets criteria | Cost / risk |
|---|---|---|---|---|
| S1 Setup script checked in CI | H2 | [S4], [S6] | yes | Low effort; needs a CI owner |
| S2 Weekly doc review | H2 | [llm-unverified] | not yet grounded | Ongoing human effort |

## Proposal draft

The final output of Phase 8, shown in chat (<800 words). It stands alone: a reader who never saw the chat understands it, and another skill can take it as input. Omit the Solutions section when Phase 7 did not run. Write it in the language of the person's request.

```text
Proposal draft: <topic title>   (status: verified | unverified)

Problem and intention: <2-3 lines>
Landscape: <short overview with key terms defined [S#]>
Key findings:
- <finding, each with [S#]; existing solutions found appear here when Phase 7 did not run>
Solutions:
- <shortlisted or chosen options, evidence and trade-offs [S#]>
Open questions and Deferred Risks:
- <item>
Sources:
[S1] <https URL> (accessed 2026-10-17)
```

An "unverified" draft opens with the line "Status: unverified. No finding below is backed by a checked source." and lists the facts as claims to check.
