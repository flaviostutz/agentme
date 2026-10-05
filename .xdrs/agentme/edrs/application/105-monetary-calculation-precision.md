---
name: agentme-edr-policy-105-monetary-calculation-precision
description: Defines when monetary values require exact decimal arithmetic and when floating point is acceptable, how exactness is kept across parsing, calculation and output, and how accepted float use is recorded. Use when writing or reviewing code or skill scripts that handle money, prices, balances, fees, taxes or FX.
apply-to: All code and skill scripts that store, calculate, convert or report monetary amounts
valid-from: 2026-10-05
---

# agentme-edr-policy-105: Monetary calculation precision

## Context and Problem Statement

Binary floating point cannot represent most decimal fractions (`0.1 + 0.2 != 0.3`), so money calculated with `float` silently drifts, breaks reconciliation and creates audit findings. Which numeric types must monetary code use, and when is float acceptable?

## Decision Outcome

**Use exact decimal arithmetic for every monetary value that is paid, booked or reported as a figure of record; allow float only for analysis, with a recorded justification**

The choice between exact and float MUST be explicit per calculation, kept exact end to end, and tested with values that expose float errors.

### Details

#### 01-decide-exact-or-float-explicitly

Every calculation involving money MUST be assigned to a precision tier (rule 02) by the author. Float MUST NOT be used merely because it is the language default or because an untyped parse produced it.

#### 02-precision-tiers

- Exact arithmetic is a MUST for amounts that are paid, charged, booked, reconciled or reported as figures of record: balances, prices, quantity times price, fees, taxes, and FX conversion of such amounts.
- Exact arithmetic is a SHOULD for any other monetary value, such as estimates, budgets and dashboard totals.
- Float MAY be used for analysis: predictions, statistics, visualisation, and derived ratios (returns, percentages, growth rates) when all of the following hold:
  - the maximum rounding error is acceptable for the purpose
  - exact arithmetic is impractical, for example the engine only accepts float
  - the business owner accepted the trade-off

#### 03-exact-chain

Exactness MUST hold from input to output, because one float step anywhere ruins the result:

- Amounts MUST be parsed from text without passing through float (JSON numbers parsed directly into the exact type or read as strings; CSV cells as strings).
- Amounts MUST be serialised as strings or exact database types (`NUMERIC`/`DECIMAL`), never as JSON floating-point numbers.
- Every rounding MUST name its rounding mode and scale (for example half-up to 2 decimals) and SHOULD happen once, at the final booking or display step.
- A currency code MUST travel with the amount whenever more than one currency exists.

#### 04-exact-types

Authors MUST pick the first option that works for the tier-MUST calculation, preferring what the runtime already provides over added dependencies:

1. A native exact decimal type (`decimal.Decimal`, `BigDecimal`).
2. Integer minor units (cents) in `int64`/`BigInt`, when only addition, subtraction and comparison at a fixed scale are needed. Multiplication or division by rates MUST round explicitly with a named mode.
3. A third-party exact decimal library (for example `big.js`) when the runtime has no native type (JavaScript), pinned as a dependency.

Native `float`/`number` arithmetic MUST NOT appear in a MUST-tier chain, including implicit conversions such as `Decimal(0.1)`, `parseFloat`, `Number(x)` or `Math.round`.

#### 05-library-chain-test

A library MUST NOT be assumed exact. Before adopting one, the author MUST confirm from its documentation that arithmetic is exact and add a unit test running the whole chain (parse, calculate, round, serialise) with float-trap values (rule 09). A library that cannot pass that test MUST NOT be used for tier-MUST calculations.

#### 06-purpose-split-for-ratios

Amounts and FX-converted amounts follow the money tiers. Ratios and statistics derived from them (returns, TWR/XIRR, volatility) follow the float-allowed analysis tier of rule 02 and MUST still be documented under rule 07.

#### 07-document-float-use

Each function or module that uses float on financial data MUST carry a short comment stating the maximum error, who accepted the trade-off, and when. The README of the module MUST list the float-based parts under a warning section so reviewers and users know which results are approximate.

#### 08-no-float-into-exact

A float-derived value MUST NOT feed a tier-MUST calculation. Re-entering the exact chain MUST go through an explicit conversion from a rounded string (`Decimal("12.35")`), with the rounding mode named, and the conversion SHOULD be commented as an approximation boundary.

#### 09-test-with-float-traps

Tier-MUST code MUST have unit tests following [agentme-edr-122](122-unit-test-requirements.md) that:

- sum values that fail in float (`0.1` ten times equals `1.0`; `0.1 + 0.2 == 0.3`)
- cover rounding half cases at the chosen scale (for example `7.625` to one decimal)
- assert the result type is the exact type, not only its value

A static check that forbids `float(` or `parseFloat` in the module SHOULD be added where practical.

## References

- [agentme-edr-121](121-coding-best-practices.md) - coding practices
- [agentme-edr-122](122-unit-test-requirements.md) - unit tests
