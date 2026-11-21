---
name: exercise-bdr-policy-606-web-ui-flow-and-experience
description: Defines the screens, flow and experience rules of the exercise questionnaire in a web browser. Use when designing, building or reviewing the web user interface.
apply-to: The screens, interaction and accessibility of the web client of the exercise questionnaire system
valid-from: 2026-11-18
---

# exercise-bdr-policy-606: Web UI flow and experience

## Context and Problem Statement

The audience answers personal questions and includes people with attention, sensory or reading differences. A careless interface can bias answers, overwhelm users or turn results into a verdict.

Question: How does the web interface present the flow, the answers and the results?

## Decision Outcome

**A calm one-question wizard that shows how clear the picture has become instead of a fixed total, and shows results with their uncertainty at any time.**

### Details

#### 01-intro-screen

Before the first Question the interface MUST show: that the questionnaire is a draft self-reflection aid and not a diagnosis (`exercise-bdr-policy-601.05-report-uncertainty-and-limits`); that every Question can be skipped and the user can stop at any time (`exercise-bdr-policy-601.07-user-control`); that choosing an answer moves to the next Question; that answers stay in the browser (`exercise-adr-policy-102.03-answers-stay-on-device`); and the Profile selection with every Profile selected (`exercise-bdr-policy-603.08-choose-analysed-profiles`). The screen MUST have one primary action to start. This notice MUST appear only on this screen and on the results screen (`06-results-screen`); Question screens MUST NOT repeat it.

#### 02-one-question-per-screen

The interface MUST show one Question at a time. It MUST NOT show or prefetch several Questions, because the next Question depends on the last Answer (`exercise-adr-policy-101.03-next-question-priority`).

#### 03-answer-input

The interface MUST show all 5 choices of the Question's scale, each with a text label (`exercise-bdr-policy-602`), as touch-friendly buttons in one radio group, with "least like me" and "most like me" captions at the two ends. The layout MUST depend on the viewport width:
- from 640 px: a horizontal row, from the lowest choice on the left to the highest on the right;
- below 640 px: a vertical column, with the highest choice on top and the lowest at the bottom.

Choosing an answer (tap, click, Enter or Space on the focused choice, or the keys 1 to 5 from lowest to highest) MUST show the choice as selected for about half a second and then move to the next Question, with no "Next" button and without motion when `prefers-reduced-motion` is set; "Back" reverses it (`10-calm-and-low-stimulation`). Each choice SHOULD show its key as a small, subtle hint (the number on the choice, and "S" on skip), hidden on touch-only devices. The arrow keys MUST only move the focus in the direction shown (up or right is a higher choice) and MUST NOT select. The skip choice MUST be a separate control, visually apart from the scale (`exercise-bdr-policy-602.04-skip-is-always-available`), and MUST move on the same way; the key S SHOULD select it.

#### 04-navigation-controls

Every Question screen MUST show "Back", "See partial results" and access to the Profile selection. "Back" MUST remove the most recent Answer and replay the rest through the engine (`exercise-adr-policy-101.09-state-is-derived`); it MUST NOT edit an earlier Answer in place. "See partial results" MUST be a secondary text link (not a button), visually aligned with "Change profiles", and bold enough to be easy to spot without looking like the primary way to continue answering. While at least one analysed Profile is still "not enough answers" or "still exploring", the link label MUST be "See partial results"; once every analysed Profile is "finished" and no response-quality notice is active, the label MUST change to "See results". The Profile selection MUST follow `exercise-adr-policy-101.10-analysed-profiles` and say that answers already given are reused. The Profile selection screen MUST also show a "Your data" area with "Export to a file", "Import a session file" and "Erase all data" (`exercise-adr-policy-102.04-export-import-and-erase`); "Erase all data" MUST be styled as a destructive action (red). It MUST first show an inline confirmation ("Yes, erase everything" and "Cancel") and only then erase and return to the intro screen. The same control MUST be used wherever erase is offered.

#### 05-progress-without-fixed-total

The interface MUST NOT show a total number of Questions or a percentage complete, because the number of Questions is adaptive. It MUST show the number of Questions answered. The Question screen MUST show progress only in one status area, with the cues of rules 16, 19 and 21 in neutral words, and MUST NOT add other progress or status areas. The status area MUST sit below the answer controls and directly above the navigation buttons, so showing or dismissing a note does not move the Question or its choices.

#### 06-results-screen

The results screen MUST be reachable from every Question screen and after the session ends, and MUST let the user go back to answering (`exercise-bdr-policy-603.01-available-any-time`), with a "Back to answering" text link at the top left of the screen. The footer MUST also have a "Change profiles" text link and MUST NOT offer "Erase all data". It MUST follow `exercise-bdr-policy-603` and show:
- Per Profile, `score` as the same bar on the -1 to 1 scale used for Characteristics (with its margin drawn as a range) followed by its number and margin, `weighted_score` only as a number, the "finished" state or "not enough answers", the level icon of `23-profile-level-icon`, and the explanation of `weighted_score`. Coverage (`exercise-bdr-policy-603.03-profile-results`) MUST be visible in the expanded Profile details of `24-profile-details`. Every Profile row MUST expand to its Characteristics (`24-profile-details`).
- In a section collapsed by default, the Characteristic scores grouped by Domain (`exercise-bdr-policy-603.12-domain-results`), each Domain titled with its score and margin, each Characteristic as a bar on the -1 to 1 scale with its margin drawn as a range.
- The response-quality notice when the flag is raised (`exercise-bdr-policy-603.07-response-quality-notice`).
- In a section collapsed by default, the progress view of rules 13, 17 and 21: clarity per Profile, effect of recent answers and the accomplishments list.
- An information icon on the left of every Characteristic label (`22-know-more`).
- The draft and non-diagnostic notice (`exercise-bdr-policy-601.05-report-uncertainty-and-limits`), and the Profiles currently analysed.

Each collapsed section MUST be a button with `aria-expanded` and a one-line summary: the number of Characteristics with a score for the Domain section, and the list of its contents for the progress section.

In the results footer actions, "Keep answering" MUST be a button and the first action, and MUST be the primary one while at least one analysed Profile is still "not enough answers" or "still exploring". Once every analysed Profile is "finished" and no response-quality notice is active, "Print / save as PDF" MUST become the primary action and "Keep answering" MUST become secondary. "Export session" MUST be a secondary button.

#### 07-no-verdict-visuals

Results MUST NOT use percentages, gauges, rankings, badges that imply a match, or colours that imply good or bad, because they conflict with `exercise-bdr-policy-601.03-no-probabilities` and `exercise-bdr-policy-603.10-score-precision-and-weighted-view`. Colour MUST NOT be the only carrier of meaning.

#### 08-printable-results

Results SHOULD be printable or exportable to PDF so the user can share them with a professional (`exercise-bdr-policy-603.06-follow-up-suggestions`). The printed version MUST keep the margins, the draft notice and the neutral wording.

#### 10-calm-and-low-stimulation

The interface MUST NOT use timers, countdowns, points, streaks, badges, urgency prompts or celebratory animation. It MUST respect the `prefers-reduced-motion` setting and MUST NOT auto-advance without the user's choice being visible and reversible by "Back".

#### 11-readable-text

Text MUST be left-aligned in a sans-serif font of at least 16 px, with a line height of at least 1.5 and short sentences. The interface MUST NOT add font or text-size toggles.

#### 12-accessible-and-mobile-first

The interface MUST meet WCAG 2.2 level AA, including full keyboard operation, a visible focus indicator, screen-reader labels on every choice and on the bars of the results, and touch targets of at least 44 px. The layout MUST work from a 320 px wide viewport without horizontal scrolling.

#### 13-clarity-per-profile

The results screen (`06-results-screen`) MUST show for each analysed Profile how clear its picture is: "not enough answers" when it has no evaluated Characteristic, "finished" when `exercise-edr-policy-101.08-good-enough` holds for it, "imprecise" when it does not and no Question can still refine it (`exercise-bdr-policy-603.03-profile-results`), and "still exploring" otherwise, next to a precision bar that MUST fill as the Profile margin narrows. "Finished" means only a narrow margin; it MUST NOT be worded as a result, a diagnosis or a final assessment (`exercise-bdr-policy-603.11-profile-level`). The Question screen MUST NOT show Profile names, states or bars, because a constant view of the Profiles can bias later Answers; the only Profile names allowed there are those in the transient note of `21-latest-accomplishments`. The clarity view MUST NOT show the level of `23-profile-level-icon`, the direction of any Profile or an order of Profiles (`exercise-bdr-policy-601.02-no-diagnosis`).

#### 14-areas-closed-counter

The interface MUST show how many of the in-scope Characteristics are closed (`settled` or `given_up`, `exercise-edr-policy-101.06-characteristic-state`) out of all in-scope Characteristics (`exercise-adr-policy-101.10-analysed-profiles`), as "areas", not as Questions, in the header next to the number of Questions answered, on the Question and results screens, not in a separate box. The counter MUST be recomputed when the analysed Profiles change.

#### 15-domain-chapters

The interface MUST show the Domain of the current Question as the current chapter. A Domain is "well covered" when every in-scope Characteristic of it is closed. This MUST be reported only as an accomplishment (`21-latest-accomplishments`), not as a permanent label of the chapter.

#### 16-good-enough-milestone

When the good-enough indicator turns true, the interface MUST show once a calm, dismissible message offering to see the results or to keep refining. The message MUST NOT end the session (`exercise-adr-policy-101.08-session-end`) and MUST NOT block the next Question.

#### 17-effect-of-recent-answers

After every 10 Questions answered, the results screen SHOULD tell, per analysed Profile, how the margin changed over those answers, for example "the margin narrowed from 0.31 to 0.22". A margin that did not narrow or that widened MUST be reported neutrally and without implying a mistake by the user.

#### 18-save-and-resume

The interface MUST tell the user, quietly, that the progress is saved on this device. When the user returns with a stored session, it MUST offer to continue, export or erase it (`exercise-adr-policy-102.04-export-import-and-erase`).

#### 19-soft-pause

After every 50 Questions answered or skipped, the interface SHOULD offer a pause that points to the results. The offer MUST be dismissible and MUST NOT block the next Question.

#### 20-no-scores-while-answering

While answering, the interface MUST NOT show scores of open Characteristics, `weighted_score` or the order of Profiles, because they can bias later Answers. Results MUST be reached only through the results screen (`06-results-screen`), not through a partial panel on the Question screen.

#### 21-latest-accomplishments

An accomplishment is a change caused by an Answer, derived from the replayed Answers (`exercise-adr-policy-101.09-state-is-derived`). The accomplishments are:
- a Characteristic becoming `settled`;
- a Domain becoming "well covered" (`15-domain-chapters`);
- a Profile reaching 1/4, 1/2, 3/4 and all of its Characteristics evaluated, shown as counts;
- a Profile margin first falling at or below 3, 2 and 1 times its margin limit (`profile_margin_stop`, or its own `margin_stop`, `exercise-edr-policy-101.08-good-enough`);
- a Profile becoming "finished".

After an Answer that causes accomplishments, the status area of the Question screen (`05-progress-without-fixed-total`) MUST show a one-line, dismissible note with the latest one, replaced by newer ones. The same note area SHOULD also carry one-time flow hints, such as "Answer recorded. Moving to the next Question. Use Back to revise.", in the same style, not a new box. The results screen MUST list all accomplishments in order. Accomplishment notes MUST describe precision and coverage only, never direction or score, and all notes here MUST use calm wording (`10-calm-and-low-stimulation`).

#### 22-know-more

On the left of every Characteristic label on the results screen, the interface MUST show an information icon button, so the user can compare the Characteristic with their own education, experience and perspective. It MUST have an accessible name that includes the Characteristic name, a touch target of at least 44 px, and keyboard and screen-reader operation. It MUST toggle a drop-down box, collapsed by default, that shows:
- the Characteristic `userInfo`, or its `description` when `userInfo` is absent (`exercise-bdr-policy-605.09-characteristic-user-info`);
- a short reminder that the text is a draft description, not a validated definition (`exercise-adr-policy-202.06-catalogue-status-is-draft`);
- at the end, a "Know more" link to `userUrl`, only when the Characteristic has one.

The link MUST open in a new tab with `rel="noopener noreferrer"`, MUST NOT carry any session data, and MUST be announced as an external site. The box MUST NOT say what a score or its direction means for any Profile (`exercise-bdr-policy-601.02-no-diagnosis`), and opening it MUST NOT change any Answer or state. Question screens MUST NOT offer it, because it would name the Characteristic before the Answer.

#### 23-profile-level-icon

In the Profiles table of the results screen, the interface MUST show on the left of every Profile name an icon with its level label below the name (`exercise-bdr-policy-603.11-profile-level`): neutral, low, medium or high once the Profile is well explored or "imprecise" (then in grey, with its score bar), and a "pending" icon before. For an "imprecise" Profile, the Profiles table MUST be followed by a short note saying that its questions are finished but its answers may conflict, so answering again more carefully may help. The icons MUST be of one neutral colour, as a three-step level glyph (none filled for neutral) and a hollow dashed circle, and each MUST be paired with its text label, because colour cannot carry meaning (`07-no-verdict-visuals`). Its accessible name MUST read like "Characteristics of this Profile: high", never as a statement about the person. Profiles MUST stay in registry order. Question screens MUST NOT show it (`13-clarity-per-profile`).

#### 24-profile-details

Every Profile row of the results screen MUST be a button, collapsed by default, with `aria-expanded` and a touch target of at least 44 px, that expands to the flat list of the Characteristics the Profile lists. The list MUST NOT be grouped by Domain and MUST be sorted by score from highest to lowest, with "not evaluated yet" items at the end. It MUST show, per Characteristic, the information icon of `22-know-more`, its score bar with margin and state, or "not evaluated yet" when it has no score. Rows with high margins MUST be marked with neutral grey styling and, in place of the state, an uncertainty label that says why: "mixed answers" for a `settled` Characteristic whose margin is above `margin_stop` (its answers disagree with each other, so more Questions would not narrow it), "wide margin" for an `open` one, "few answers" when its margin is unknown; the Characteristic name MUST NOT carry the label, because colour cannot carry meaning alone (`07-no-verdict-visuals`). Before the list, the expanded view MUST show one precision bar for that Profile, in the visual language of `13-clarity-per-profile`, with the coverage as "N of M evaluated". It MUST NOT repeat the Profile name or state of the row header, and MUST be separated from the list by a divider. Opening it MUST NOT change any Answer or state. The view MUST end with a red "Delete answers" button when the Profile has related Answers (to Questions touching its Characteristics, shared ones included). It MUST first ask for inline confirmation that names the number of Answers and warns that other Profiles sharing the Characteristics may change; only then MUST it delete them, replay the rest and continue answering.

## References

- [exercise-bdr-policy-601 - Purpose and guardrails](601-purpose-and-guardrails.md)
- [exercise-bdr-policy-602 - Response scales](602-response-scales.md)
- [exercise-bdr-policy-603 - Results presentation](603-results-presentation.md)
- [exercise-adr-policy-101 - Question flow engine](../../adrs/application/101-question-flow-engine.md)
- [exercise-adr-policy-102 - Web client architecture](../../adrs/application/102-web-client-architecture.md)
- [Web UI functional sample](.assets/web-ui-functional-sample.html) - Self-contained, working HTML app (intro, questions, results, import/export) that runs the shared engine and registries inlined by the build script; illustrative, the rules above prevail over it
- [Web sample build script](.assets/build-web-sample.js) - Fails when registry lint fails, then inlines `engine.js` and the registries into the generated regions of the functional sample
