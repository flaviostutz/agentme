---
name: exercise
description: Policies defining a self-reflection questionnaire system that asks questions, scores characteristics from the answers and groups the findings into profiles.
scope-type: standard
apply-to: Anyone designing, implementing or populating the exercise questionnaire system, its question bank and its registries.
valid-from: 2026-11-17
---

# exercise Scope Overview

## Overview

The `exercise` scope declares how a self-reflection questionnaire works: how the domain model is organised, how the next question is chosen, how answers become scores, what the user sees and how the question, characteristic and profile registries are authored. The scope replaces a free-form specification with Policies.

The system asks the user questions to identify characteristics, goes deeper into some of them and groups the findings into profiles so the user can follow up on self-recognition. It never diagnoses.

## Content

### What this scope covers

- **Domain model**: Domain, Characteristic, Profile, Question and Answer, and the JSON registries that hold them.
- **Flow engine**: a single question queue, follow-up routes and the next-question priority.
- **Measurement**: the formulas that turn answers into characteristic scores, confidence and profile results.
- **Product**: purpose and guardrails, the response scales, results presentation and the authoring standards for questions, characteristics and profiles.

### What this scope does not cover

Application code, user interface design, privacy, multilingual support, question versioning and instrument catalogues. Deferred items are tracked in the repository `TODO.md`.

## Type Indexes

- [ADRs Index](adrs/index.md) - Domain model, registries and the question flow engine
- [EDRs Index](edrs/index.md) - Measurement formulas and registry lint
- [BDRs Index](bdrs/index.md) - Purpose, response scales, results and authoring standards
