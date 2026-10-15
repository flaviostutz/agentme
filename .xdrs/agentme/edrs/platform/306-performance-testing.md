---
name: agentme-edr-policy-306-performance-testing
description: Defines performance testing for any software system - six kinds (baseline, load, stress, spike, soak, resilience), the performance-<slug> module, test-performance Makefile targets, allowed environments and prod guardrails, declared thresholds and exit codes, datasets, data safety and report files. Use when measuring how a system behaves under expected, peak, stressful or failing conditions.
apply-to: Software systems (API, UI, service, batch, AI or not) whose behavior under load, stress, long runs or failing dependencies must be measured against a deployed environment
valid-from: 2026-10-15
---

# agentme-edr-policy-306: Performance testing

## Context and Problem Statement

Functional tests show that a system is correct, not how it behaves with many users, for a long time, or when a database, disk, provider or network fails. Without a shared structure, performance checks are ad hoc, run against the wrong environment, leak data, or have no pass/fail criteria.

Question: How must a team structure, run and report performance tests?

## Decision Outcome

**Performance testing is a test type of its own: a `performance-<slug>/` module that runs black-box scenarios of six kinds against a deployed environment, with declared thresholds, standard Makefile targets and fixed report files.**

It is advised, not mandatory, and runs on demand. The best moments are a first release, a major architectural change, and before an expected surge of users (elections, Black Friday). For AI components, [agentme-edr-158](../application/158-ai-performance-testing.md) extends this Policy.

### Details

#### 01-six-kinds-of-performance-test

A scenario MUST declare exactly one kind:

| Kind | Question it answers | Load shape | Gated by thresholds |
|---|---|---|---|
| `baseline` | Does the system meet its targets under expected normal conditions? | Normal expected load | Yes |
| `load` | Does it meet its targets at expected peak? | Expected peak load | Yes |
| `stress` | How does it behave with more users than expected, and does it degrade gracefully? | Load increased until it breaks | Yes |
| `spike` | Does it survive a fast burst and recover afterwards? | Sudden jump, then drop | Yes |
| `soak` | Does it stay healthy over a long time (leaks, drift, growing latency)? | Expected load for hours | Yes |
| `resilience` | When a dependency or resource fails, is it graceful and is data intact? | Expected load plus injected faults | Integrity only (rule `05`) |

Resilience faults include database down, disk full, provider failure, network degradation (latency, loss) and restarted instances. Faults MUST be injected from outside the system under test, through a proxy, adapter or fault-injection tool placed in front of the dependency; the system code MUST NOT contain test-only fault switches.

#### 02-module-layout

Each performance suite MUST live in its own `performance-<slug>/` module, where `<slug>` names the system or flow under test, following [agentme-edr-016](../principles/016-cross-language-module-structure.md) rule `01-module-must-own-folder-root` and the naming of [agentme-edr-301](301-monorepo-structure.md). When it targets only part of a repository it MUST sit inside that application folder next to its modules; otherwise it MUST sit next to the root modules.

```text
performance-checkout/
├── Makefile
├── README.md          # target system, environments, acc differences, how to run
├── thresholds.yaml    # limits per kind and scenario
├── scenarios/         # one file per scenario, each declares its kind
├── dataset/           # optional, rule 06
├── dist/              # reports and samples, gitignored
└── .cache/
```

A performance module differs from `tests_benchmark/` of [agentme-edr-016](../principles/016-cross-language-module-structure.md) rule `07-tests-use-predictable-locations`: benchmarks time code in-process, while performance modules drive a deployed system from outside. Tool choice is free; simple scripts without a dataset are valid.

#### 03-makefile-targets

The module `Makefile` MUST follow [agentme-edr-303](303-common-targets.md) and expose:

- `test-performance`: runs `baseline`, `load` and `spike`;
- `test-performance-<kind>`: runs one kind, MUST exist for `stress`, `soak` and `resilience` and MAY exist for the others.

These targets need a live environment, so they MUST NOT be invoked from `test` or `all`, per [agentme-edr-303](303-common-targets.md) rule `08-default-targets-must-only-include-offline-subtargets`. The module's `test`, `lint` and `all` MUST stay offline and cover its own helper code (threshold evaluation, redaction, report writing) with unit tests per [agentme-edr-122](../application/122-unit-test-requirements.md).

#### 04-environments-and-prod-guardrails

`STAGE` ([agentme-edr-303](303-common-targets.md) rule `04-standard-environment-variables`) and the target address MUST be provided explicitly with no default; a run without them, or against an unreachable target, MUST fail fast with a message naming the missing value. Non-secret settings follow [agentme-edr-305](305-environment-variable-configuration.md).

The main environment is `acc` ([agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `05-acc-must-mirror-prd-architecture`), which MUST mirror `prd` (topology, configuration, instance sizes, scaling rules, dependency versions, data volume class); every known difference MUST be listed in the README, and results are then indicative only.

| Kind | `acc` | `prd` |
|---|---|---|
| `baseline` | Allowed | Allowed, SHOULD run against the canary |
| `load`, `soak` | Allowed | Allowed with guardrails |
| `spike`, `stress`, `resilience` | Allowed | MUST NOT run |

Prod runs MUST have all of: approval of the service owner, an off-peak window, synthetic data tagged with a marker and removed after the run, a one-step abort switch, and a cap on requests or cost. The default `test-performance` MUST NOT be run against prod; use explicit kind targets.

#### 05-thresholds-and-exit-codes

Thresholds MUST be versioned in `thresholds.yaml` before the first run and MUST NOT be edited to turn a failing run green without a recorded reason. A scenario of a gated kind MUST exit non-zero when any threshold is breached (for example p95 latency, error rate, throughput floor).

`resilience` metrics (time to detect, time to recover, error rate during the fault) are reported only. Integrity violations MUST ALWAYS exit non-zero for every kind: a post-run consistency check MUST compare what the load tool sent with what the system persisted and report corrupted records, lost or duplicated transactions and transactions left incomplete.

#### 06-datasets-and-data-safety

A scenario that needs realistic inputs and expected results SHOULD keep them in `dataset/`, following [agentme-edr-201](../data/201-ml-dataset-structure.md) rule `04-complex-structured-datasets-must-use-per-entry-json-files`: `data/` with one JSON per entry, `dataset.schema.json`, `README.md`, validated by `make lint`. Entries SHOULD use the envelope of [agentme-edr-152](../application/152-ai-test-types-taxonomy.md) rule `02-golden-dataset-entry-envelope` without `test_types`: `input`, optional `expected_output`, `group` and `mock_fixtures` (fakes for parts of the system that are not under test). The module owns its dataset; entries MUST NOT be tagged as eval entries and `eval.py` never reads them.

Inputs MUST be synthetic. Recorded samples, logs and reports MUST NOT contain credentials, tokens, authorization headers or personal data, and MUST be redacted before being written. `dist/` MUST stay gitignored per [agentme-edr-016](../principles/016-cross-language-module-structure.md) rule `03-build-outputs-must-go-to-dist`.

#### 07-report-files

Each run MUST write, programmatically and without generative models, to `dist/`:

- `results-<kind>.json` with `kind`, `stage`, `date`, `scenario`, `thresholds`, `metrics` (`latency_p50_ms`, `latency_p95_ms`, `latency_p99_ms`, `throughput_rps`, `error_rate`), `integrity` and `status`;
- `report-<kind>.md` with the same data as readable tables, the pass/fail verdict and the list of breached thresholds.

```text
kind: load  stage: tst  status: PASS
p50 120 ms  p95 480 ms (limit 600)  p99 900 ms  error rate 0.4% (limit 1%)
integrity: 0 lost, 0 duplicated, 0 corrupted
```

#### 08-cadence

Teams SHOULD run the kinds that fit the risk when a trigger from the Decision Outcome appears, and SHOULD keep one recorded baseline run to compare later runs against. A pipeline step MAY run them as described in [agentme-edr-302](302-github-pipelines.md) rule `04-performance-step-is-optional`.

## References

- [agentme-edr-158](../application/158-ai-performance-testing.md) - AI performance testing, extends this Policy
- [agentme-edr-303](303-common-targets.md) - Makefile targets and `STAGE`
- [agentme-edr-302](302-github-pipelines.md) - Optional pipeline step
- [agentme-edr-301](301-monorepo-structure.md) - Module placement
- [agentme-edr-016](../principles/016-cross-language-module-structure.md) - Module structure and `tests_benchmark/`
- [agentme-edr-201](../data/201-ml-dataset-structure.md) - Dataset layout and lint
- [agentme-edr-152](../application/152-ai-test-types-taxonomy.md) - Dataset entry envelope
- [agentme-edr-122](../application/122-unit-test-requirements.md) - Unit tests for helper code
- [agentme-edr-305](305-environment-variable-configuration.md) - Environment configuration
