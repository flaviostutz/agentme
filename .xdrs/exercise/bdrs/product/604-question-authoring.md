---
name: exercise-bdr-policy-604-question-authoring
description: Defines how questions are written, typed, weighted, routed and checked before they enter the question registry. Use when creating, changing or reviewing a question in the exercise registries.
apply-to: All Questions in the exercise question registry
valid-from: 2026-11-17
---

# exercise-bdr-policy-604: Question authoring

## Context and Problem Statement

The quality of the results depends on the quality of each question. Vague, leading, compound or contradicting questions produce meaningless scores.

Question: What must a question satisfy before it is accepted into the registry?

## Decision Outcome

**Short, concrete, neutral, single-idea questions with explicit characteristic weights, a stage-appropriate type, routes that deepen the investigation and a dry-run before acceptance.**

### Details

#### 01-field-limits

`id` MUST be snake_case with at most 7 words. `title` is required with at most 19 words. `details` is optional with at most 59 words. These limits are checked by `exercise-edr-policy-102`.

#### 02-concrete-and-neutral-wording

A title MUST describe a concrete experience or behaviour the user can recall, not an abstract trait or a judgement about themselves. Vague words and dubious wording MUST be avoided.

A title and its `details` MUST use neutral wording. They MUST NOT use leading, emotionally charged or biased language, or phrasing that makes one answer look more socially desirable, healthier, smarter or more acceptable than another, because that pushes the user toward the answer they think is expected instead of the one that is true. A statement and its reverse-keyed counterpart (`11-reverse-keyed-pairs`) SHOULD sound equally acceptable. Examples: prefer "I forget tasks unless I write them down" to "I am hopelessly forgetful", and "I need time alone to think about a problem" to "I withdraw from people to avoid them".

#### 03-one-idea-per-question

A title MUST express a single idea, so that one answer can only mean one thing. A double-barrelled question, which joins two experiences, behaviours or conditions in one statement (for example "I am calm and organised" or "How often do you forget appointments or lose things?"), MUST NOT be accepted: when the user agrees with one part and not the other, the answer cannot be interpreted. It MUST be split into simple, direct questions, each informing its own Characteristic or angle. A short example list after "such as" MAY illustrate one behaviour, but the behaviour itself MUST stay a single one. A title MUST NOT combine a behaviour with its reason, cause or consequence unless that link is what the Question measures (for example a differentiation Question about why).

#### 04-answer-type

`answer` MUST be `agreement` for statements and `frequency` for how often something happens. The wording MUST fit the scale (`exercise-bdr-policy-602`).

#### 05-weights

Each listed Characteristic MUST have a weight in -1..1, not 0. With a positive weight, answers above the neutral middle (agreeing, frequent) add points to the Characteristic and answers below it (disagreeing, rare) subtract points; a negative weight reverses this (`exercise-edr-policy-101.01-evidence`). The absolute weight is also the strength of the evidence: the score is a weighted mean (`exercise-edr-policy-101.02-characteristic-score`), so a low weight, for example 0.5 on a secondary Characteristic, makes the answer count half as much for that Characteristic and does not pull its score toward 0. A Question SHOULD list few Characteristics, only those it really informs.

#### 06-source

`source` MUST state where the question came from as plain text: the instrument, reference or draft inventory and, when one exists, the specific item or argument. A Question MUST NOT contradict its cited source; it MAY omit, change or reword it.

#### 07-stage-types

`type` MUST follow these meanings:
- `discovery`: generic, identifies what to investigate; SHOULD route to exploration or differentiation Questions but MAY have no routes. Every Characteristic listed in a Profile SHOULD be the main Characteristic of at least one `discovery` Question, so the engine reaches it early without depending on routes.
- `exploration`: specific cases of a Characteristic from several angles; SHOULD route to differentiation Questions.
- `differentiation`: identifies a specialization, such as how, when, in which context or for which reason.
- `balancing`: seeks counter-evidence; normally has a negative weight and is answered with agreement, because a counter-statement ("I can stop easily") reads naturally as a statement. Frequency MAY be used when the counter-experience is about how often something happens; "never" then counts as full counter-evidence.

For one Characteristic the desired flow is exploration, then differentiation, then balancing. The flow is desired, not mandatory: the engine does not enforce it (`exercise-adr-policy-101.03-next-question-priority`) and a Question MAY be asked or routed out of this order.

#### 08-routes

A route MUST point to an existing Question and SHOULD point to a Question of the same or a later stage for the same or a related Characteristic. A route to an earlier stage is allowed but discouraged. A Question MUST NOT route to itself and routes MUST NOT form a cycle (`exercise-edr-policy-102`).

#### 09-dry-run-before-accept

Before accepting a Question, the author MUST dry-run answers of different kinds of people and contexts and check that the title, details, weights and routes fit the description of every listed Characteristic, and MUST check the internal consistency of the Characteristic's Questions (`12-internal-consistency`). The simulated part of the dry-run is automated by `exercise-edr-policy-103-question-bank-testing`.

#### 10-check-related-questions

The author MUST check whether other registry Questions should be routes from the new one, and whether the new one contradicts an existing one. Contradicting Questions are only allowed when they are balancing double-checks with a negative weight.

#### 11-reverse-keyed-pairs

A Characteristic carried as main by six or more Questions SHOULD have at least two reverse-keyed Questions (`answer: agreement`, negative weight, `type: balancing`), and the first one SHOULD have a route with `when: gte` and `threshold: 0.5` to the second. The route fires for honest agreement with the reversed statement and for yes-saying, which is what the response quality check (`exercise-edr-policy-101.11-response-quality`) compares. A Characteristic with a single reverse-keyed Question lets one noisy answer decide whether keying disagreement can be seen.

#### 12-internal-consistency

Before accepting a Characteristic's Questions, and again after any change to them, the author MUST measure their internal consistency with Cronbach's alpha, to check that the Questions that inform the same Characteristic are answered in a coherent way. The check is part of the dry-run (`09-dry-run-before-accept`) and MUST be done per Characteristic and MUST NOT be done over the whole bank. `exercise-edr-policy-103-question-bank-testing.05-internal-consistency` automates the simulated measurement.

- **Items:** the Questions that list the Characteristic as main (first) Characteristic. At least 3 items are needed; with fewer, or with fewer than 30 respondents who answered a pair of items, the Characteristic MUST be reported as not measured instead of passing.
- **Item scores:** each non-null answer is rescaled to -1..1 (agreement is used as is; frequency becomes `2 x value - 1`) and multiplied by the sign of the Question's weight, so reverse-keyed Questions (`11-reverse-keyed-pairs`) point the same way as the others.
- **Alpha:** `alpha = k / (k - 1) x (1 - sum(item variance) / variance(total score))` over the respondents who answered all `k` items. Because the adaptive engine does not ask every Question, the test run MAY present all items of the Characteristic to every test respondent, or MAY use the standardised form `alpha = k x r / (1 + (k - 1) x r)`, where `r` is the mean correlation between the item scores over the pairs of items answered by the same respondents.
- **Target:** alpha MUST be between 0.70 and 0.90.
  - Below 0.70, the Questions are not answered in the same way. The author MUST review wording, keying (weight sign), and whether each Question really matches the Characteristic description. Checking which item raises alpha most when removed helps to find the Question to fix, split or move.
  - Above 0.90, the Questions are probably redundant. The author SHOULD merge, remove or reword the near duplicates, because they lengthen sessions without adding evidence.

A result MUST state its respondent source. Simulated respondents are generated from the registry weights themselves, so they only check the keying and the arithmetic, not the wording; only answers from real people confirm internal consistency. The check is a test of the Questions: it MUST NOT change any score, margin or route at run time, and it MUST NOT be shown to the user.

#### 13-weights-and-main-question-count

An author SHOULD raise a secondary weight only when the Question tells as much about that Characteristic as about the main one, because a secondary Question counts for less in the weighted score. An author MUST NOT give a Question a negative or reversed secondary weight on a Characteristic that a respondent can hold at the same time, unless the Question really measures their opposition. Each Characteristic SHOULD have at least three main Questions, so that its evidence does not come mostly from other Characteristics' Questions.

## References

- [exercise-bdr-policy-602 - Response scales](602-response-scales.md)
- [exercise-bdr-policy-605 - Characteristic and profile authoring](605-characteristic-and-profile-authoring.md)
- [exercise-edr-policy-103 - Question bank testing](../../edrs/application/103-question-bank-testing.md)
- [exercise-edr-policy-102 - Registry lint](../../edrs/application/102-registry-lint.md)
- [Original spec with the draft question inventory](../../../../spec-original.md)
