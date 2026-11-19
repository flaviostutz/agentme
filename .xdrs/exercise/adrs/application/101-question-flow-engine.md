---
name: exercise-adr-policy-101-question-flow-engine
description: Defines how the exercise engine queues, selects, refills and ends questions. Use when implementing or reviewing the question flow or adding routes to questions.
apply-to: The engine of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-adr-policy-101: Question flow engine

## Context and Problem Statement

The user answers questions one at a time. The order must feel connected, so the user keeps context, and must go deeper only where it helps to identify a characteristic.

Question: How does the engine decide which question comes next, and when does the session end?

## Decision Outcome

**One queue of questions; routes and profile-gap top-ups only add questions to the queue; the next question comes from a fixed priority order.**

### Details

#### 01-initial-queue

At session start the queue MUST contain every Question of type `discovery` that carries at least one in-scope Characteristic (`10-analysed-profiles`), in registry order (domains in the order of `exercise-adr-policy-201.02-domain-is-a-fixed-list`).

#### 02-routes-add-only

After a Question is answered with a value (not skipped), each of its `routes` MUST be evaluated against the answer: `gte` matches when answer >= threshold, `lte` matches when answer <= threshold. For every matching route, the target Question MUST be added to the queue unless it was already asked, is already queued (`04-no-repeat`) or carries no in-scope Characteristic (`10-analysed-profiles`). A skipped Question MUST NOT trigger routes. Routes MUST NOT remove, reorder or skip any queued Question.

#### 03-next-question-priority

The next Question MUST be chosen from the queue by this order of criteria, each applied only to break ties left by the previous one:
1. Added by a route of the last answered Question (in route order).
2. Same Domain as the last asked Question (`exercise-adr-policy-201.07-question-domain-is-derived`).
3. Lowest number of non-null evidence entries among the open in-scope Characteristics of the Question (`10-analysed-profiles`, `exercise-edr-policy-101`). This spreads questions over the Characteristics that are least measured, so no Characteristic takes most of the questions of a Profile.
4. Lowest stage among `exploration`, `differentiation`, `balancing`, counting only Questions that have at least one open in-scope Characteristic (`exercise-edr-policy-101`). `discovery` ranks before all three.
5. Earliest insertion into the queue.

Questions added by `06-profile-gap-top-up` take part in this order like any other queued Question.

#### 04-no-repeat

A Question MUST be asked at most once per session, including when it was skipped. The engine MUST ignore any attempt to add to the queue a Question that was already asked or is already queued, for any reason (route, refill or any other source), without error and without duplicating or reordering the queue.

#### 05-refill-from-bank

When the queue is empty, the engine MUST add every unasked Question that carries an in-scope Characteristic (`10-analysed-profiles`) which is open and has at least one non-null evidence entry. If no such Question exists, the queue stays empty.

#### 06-profile-gap-top-up

After each asked Question (answered or skipped) and before choosing the next one, the engine MUST top up the queue for the gaps of the current Domain. A gap is an in-scope Characteristic (`10-analysed-profiles`) that is open and has fewer than `min_answered` non-null evidence entries (`exercise-edr-policy-101`). For every gap whose Domain is the Domain of the last asked Question and that is carried by no queued Question, the engine MUST add one unasked Question carrying it, choosing the lowest stage (`discovery`, `exploration`, `differentiation`, `balancing`) and then registry order; when none exists nothing is added. Gaps of other Domains wait until the engine enters those Domains (`03-next-question-priority`), so the user keeps context while every Profile Characteristic still gets measured.

#### 07-prune

Before choosing the next Question, the engine MUST remove from the queue every Question whose in-scope Characteristics (`10-analysed-profiles`) are all settled or given up (`exercise-edr-policy-101`), and every Question that carries no in-scope Characteristic.

#### 08-session-end

The session MUST end when the queue is empty after refill. The user MAY stop at any time and MUST be able to see results after any number of answers (`exercise-bdr-policy-603`).

#### 09-state-is-derived

The engine MUST be a pure function of the registries, the ordered Answers (`exercise-adr-policy-201.08-answer-is-value-or-null`) and the analysed Profiles and the ordered changes to them, each with the number of Answers given when it happened (`10-analysed-profiles`). The queue, asked set and last Question MUST be recomputable by replaying them. Replay MUST ask each stored Question in the stored order, even when the engine would have chosen another (as after the user deletes Answers), and MUST reject only unknown or repeated Questions.

#### 10-analysed-profiles

A session MUST start with a non-empty selection of analysed Profiles, which defaults to every Profile in the registry. The Characteristics listed in at least one analysed Profile are in scope; the engine MUST only queue, route to, top up for and stop on in-scope Characteristics, so questions concentrate on what the chosen Profiles need. Out-of-scope Characteristics MUST NOT stop being scored: every answered Question adds evidence to all of its Characteristics, in scope or not (`exercise-edr-policy-101.01-evidence`).

A Profile MAY be added to or removed from the analysed Profiles at any moment of the session, as long as at least one stays. A change MUST NOT discard, reorder or re-ask any Answer: evidence is kept for every Characteristic, in scope or not, so state (`exercise-edr-policy-101.06-characteristic-state`) and scores follow from the existing Answers at once, and a Profile removed and added again picks its evidence up where it was. A Characteristic stays in scope while any analysed Profile lists it.

After a change, before choosing the next Question, the engine MUST re-check the queue against the new scope:
1. Remove every queued Question that carries no open in-scope Characteristic (`07-prune` applies the same test). The removed Question was not asked, so it MAY be queued again by a later change.
2. Add every unasked `discovery` Question that carries an open in-scope Characteristic that was not in scope before the change. Nothing is added when a Profile is removed, because the scope only shrinks.
3. Keep every other queued Question, with its order. `06-profile-gap-top-up` and `05-refill-from-bank` then work on the new scope as usual, so more Questions are queued organically as the gaps show.

Profile results, good enough (`exercise-edr-policy-101.08-good-enough`) and the weights of `exercise-edr-policy-101.10-weighted-profile-score` MUST consider only the analysed Profiles and MUST be recomputed after every change. Results MUST NOT show a removed Profile as analysed.

#### 12-dry-run-flow-changes

A change to the priority, top-up, refill or analysed Profiles rules (`03-next-question-priority`, `05-refill-from-bank`, `06-profile-gap-top-up`, `10-analysed-profiles`) SHOULD be checked with a simulated test run (`exercise-edr-policy-103-question-bank-testing`), including a run scoped to one Profile and runs that add and remove Profiles during the session.

## References

- [exercise-adr-policy-201 - Domain model](../data/201-domain-model.md)
- [exercise-edr-policy-101 - Measurement formulas](../../edrs/application/101-measurement-formulas.md)
- [exercise-bdr-policy-603 - Results presentation](../../bdrs/product/603-results-presentation.md)
