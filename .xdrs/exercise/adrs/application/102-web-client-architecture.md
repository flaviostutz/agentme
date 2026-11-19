---
name: exercise-adr-policy-102-web-client-architecture
description: Defines how the exercise questionnaire runs in a web browser and where answers are kept. Use when building, hosting or reviewing the web client of the questionnaire.
apply-to: The web client that presents the exercise questionnaire to users in a browser
valid-from: 2026-11-18
---

# exercise-adr-policy-102: Web client architecture

## Context and Problem Statement

The questionnaire collects sensitive personal answers. The engine is a pure function of the registries and the ordered answers, so it can run anywhere.

Question: Where does the engine run and where do answers live?

## Decision Outcome

**A static web app that runs the shared engine in the browser and keeps every answer on the user's device.**

### Details

#### 01-static-client-side-app

The web client MUST be a static application executed entirely in the browser. No server component MAY receive, process or store answers, scores or results.

#### 02-shared-engine-module

The browser MUST run the same engine module and registries that the test skill runs (`exercise-edr-policy-103-question-bank-testing`). The engine MUST NOT be reimplemented in the user interface. The user interface MUST only render the engine state and feed it Answers, so the rules of `exercise-adr-policy-101` and `exercise-edr-policy-101` hold unchanged.

#### 03-answers-stay-on-device

The session MUST be stored only in the browser's local storage, in the replayable form of `exercise-adr-policy-101.09-state-is-derived`: the ordered Answers, with skips stored as null, and the ordered changes to the analysed Profiles with the number of Answers given when each happened. Answers, scores and results MUST NOT be sent over the network. The client MUST NOT load third-party scripts, fonts or analytics that can observe the page content.

#### 04-export-import-and-erase

The user MUST be able to export the stored session to a JSON file, import it again and erase all stored data in one action. Importing MUST replay the Answers through the engine instead of trusting stored scores.

#### 05-registries-bundled-and-checked

The registries MUST be bundled as static files with the application. A build MUST fail when registry lint fails (`exercise-edr-policy-102-registry-lint`).

## References

- [exercise-adr-policy-101 - Question flow engine](101-question-flow-engine.md)
- [exercise-adr-policy-202 - Registries](../data/202-registries.md)
- [exercise-edr-policy-102 - Registry lint](../../edrs/application/102-registry-lint.md)
- [exercise-edr-policy-103 - Question bank testing](../../edrs/application/103-question-bank-testing.md)
- [exercise-bdr-policy-606 - Web UI flow and experience](../../bdrs/product/606-web-ui-flow-and-experience.md)
