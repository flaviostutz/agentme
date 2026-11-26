---
name: agentme-edr-policy-161-consent-and-privacy-ux
description: Defines consent, cookie and tracker consent, privacy notice and children's data UX requirements for user interfaces of applications that process personal data under the GDPR and ePrivacy rules. Use when building or reviewing consent banners, sign-up flows, preference centres and SDK integrations.
apply-to: Web, mobile and desktop user interfaces and SDK integrations of applications whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-edr-policy-161: Consent and privacy UX

## Context and Problem Statement

Consent is valid only if freely given, specific, informed and unambiguous (Art. 4(11), 7). Interfaces that pre-tick boxes, hide the refusal option or load trackers before the choice produce invalid consent and legal exposure.

Question: What must user interfaces do to collect, record and withdraw consent and to inform people about processing?

## Decision Outcome

**Interfaces MUST collect consent by explicit opt-in per purpose, load nothing consent-dependent before it is given, and make withdrawal as easy as giving it**

Consent is required only where consent is the lawful basis declared in the `lawful-bases-and-consents` hub item of [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md). Code-level handling is in [agentme-edr-policy-162](162-personal-data-handling-in-code.md). Nothing here is legal advice.

### Details

#### 01-explicit-opt-in-per-purpose

Consent MUST be given by a clear affirmative action, with one choice per purpose (analytics, marketing, personalisation are separate). Pre-ticked boxes, silence, scrolling or continued use MUST NOT count as consent. Consent MUST NOT be bundled with terms of service or made a condition of a service that does not need the data (Art. 7(4)).

#### 02-equal-choice-no-dark-patterns

Accept and refuse MUST be equally prominent, in the same layer, with the same effort, visual weight and wording clarity. The interface MUST NOT use confusing wording, nagging, countdowns, or hidden refuse controls to steer users.

#### 03-cookies-trackers-and-sdks

Storing or reading information on the user's device, including cookies, local storage, device IDs and fingerprinting, needs prior consent unless strictly necessary for a service the user explicitly requested (ePrivacy Directive 2002/58/EC, Art. 5(3)). Therefore:

- Analytics, advertising, session-replay and social SDKs MUST NOT load or initialise before consent.
- A tag or SDK MUST be listed with its purpose and provider in the consent interface, and a new one MUST NOT ship without updating it.
- Strictly necessary items (session, security, load balancing, stored consent choice) MAY be set without consent but MUST be documented.

#### 04-informed-at-collection

Before or at collection, the interface MUST show the identity of the controller, the purposes, the lawful basis, recipients, retention, the person's rights and where to complain (Art. 13), with layered text in plain language. The privacy notice MUST be reachable from every collection point.

#### 05-withdrawal-as-easy-as-giving

Withdrawing consent MUST take no more steps than giving it and MUST be reachable from a persistent control (for example a footer link or settings entry). A withdrawal MUST take effect immediately and stop the related processing and SDKs.

#### 06-consent-record

Each consent event MUST be stored with: pseudonymous subject ID, timestamp, purposes and choice, version of the notice shown, and channel. Withdrawals MUST be stored the same way. Consent MUST be re-requested when purposes or providers change and SHOULD be refreshed at a documented interval.

#### 07-children

When the service is offered to children, the interface MUST obtain parental consent below the applicable age (16, or lower where the Member State sets it, never below 13; Art. 8), use age-appropriate language, and make reasonable efforts to verify it. It MUST NOT profile children for marketing.

#### 08-accessibility

Consent and privacy controls MUST be keyboard and screen-reader accessible and work on mobile viewports.

#### 09-testing

Tests MUST cover: no consent-dependent request before consent (assert on network calls or SDK init), withdrawal stops them, the record is written with the fields in rule 06, and refusal leaves the service working where the law requires it.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 4(11), 6, 7, 8, 13.
- [ePrivacy Directive 2002/58/EC](https://eur-lex.europa.eu/eli/dir/2002/58/oj), Art. 5(3); cited without access to the official text during authoring, to be confirmed in legal review.
