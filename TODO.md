# TODO

<!-- Format: see agentme-edr-001 -->

## [BACKLOG] 14- Enforce environment short names in project templates and CI (2026-10-16)

- status: open
- prompt: Add a check that rejects `STAGE` values and `.env.<stage>` file names whose prefix is not one of `sbx`, `dev`, `tst`, `acc`, `prd`, per agentme-edr-307 rules `02-stage-value-must-be-validated` and `03-env-files-must-use-the-prefix-name`. Start with the `create-*-project` skills' Makefile templates (under `.xdrs/agentme/edrs/application/skills/`) and the CI examples in agentme-edr-302. Acceptance: a Makefile target run with `STAGE=staging` fails with a message naming the value.
- deferred reason: New tooling beyond the policy text; left out of the environments policy change.
- why this is important: Without a check, names drift back to production, staging and test.

## [BACKLOG] 13- Policy for production console change control (2026-10-16)

- status: open
- prompt: Write a policy on how developers and engineers may change production through consoles, which agentme-adr-301 rule `06-prd-serves-final-users` only says they can access together with monitoring. Cover read-only defaults, approval for writes, audit trail and break-glass access. Likely ADR governance plus EDR governance; check agentme-core-adr-policy-001 rule 03 for scope fit.
- deferred reason: Excluded from the environments policy to keep it to model, connectivity and access.
- why this is important: Console access to prd without change rules is the most direct way to break production.

## [BACKLOG] 12- Policy for data handling across environments (2026-10-16)

- status: open
- prompt: Write a policy on which data may exist in each environment (agentme-adr-301): whether production data may be copied to `dev`, `tst` or `acc`, masking and synthetic data rules, and retention in `sbx`. Check `_core-adr-policy-016` for the data subject and agentme-edr-306 rule `06-datasets-and-data-safety` for existing synthetic data rules.
- deferred reason: Excluded from the environments policy to keep it to model, connectivity and access.
- why this is important: Production data in lower environments is a common source of leaks.

## [BACKLOG] 11- Official benchmark price source for manage-investment-portfolio (2026-10-08)

- status: open
- prompt: `pm benchmark` reads monthly closes from the unofficial Yahoo Finance chart endpoint (`adapters/connectors/yahoo/` in `scripts/src/portfolio_manager/`). Replace or complement it with a documented source (for example a licensed or key-based price API, or user-supplied CSV of index levels) and keep the cache fallback, the ticker-only disclosure and the EUR conversion. Acceptance: benchmark figures no longer depend on an unofficial endpoint and the report drops the "approximate" mark when prices are month-end closes.
- deferred reason: No agreed data source; the unofficial endpoint was accepted for the first version because it needs no key.
- why this is important: An undocumented endpoint can change or stop without notice, and the benchmark comparison would silently fall back to the cache.

## [BACKLOG] 10- Link an external bank account to each investment account in manage-investment-portfolio (2026-10-08)

- status: open
- prompt: In `manage-investment-portfolio`, let the user link a bank account to an investment account so that deposits and withdrawals become transfers between the two and buys and sells move money in the investment account only. Needs bank statement layouts (adapters under `adapters/connectors/institutions/`), a transfer matching rule, reconciliation checks and the effect on wealth and net flows. Acceptance: wealth over investment accounts plus linked bank accounts reconciles with the statements, and external flows are only those that cross the combined boundary.
- deferred reason: Needs bank statement layouts and sample statements from the user; roughly doubles the scope of the 3.0.0 report upgrade.
- why this is important: Deposits shown as external flows overstate money added when the money came from the user's own bank account that is tracked elsewhere.

## [BACKLOG] 9- Live-verify GitHub contents skills and Azure DevOps work item comments API (2026-10-05)

- status: open
- prompt: The GitHub `issue-get`, `issue-update`, `issue-create`, `issue-comment-create` resources (`get-github-contents`, `change-github-contents`) were verified only with fake `gh` because the local token was invalid, and the Azure DevOps work item comments API (`7.1-preview.4`, used by `work-item-get` and `work-item-comment-create`) and `work-item-update` / `work-item-create` writes were verified only with a fake `az`. With valid credentials, run each against a throwaway issue and work item, fix any response-shape mismatch, and record the result in the skills' Known Issues.
- deferred reason: No valid GitHub token in the session; write calls against a real Azure DevOps project were not approved.
- why this is important: Refining a story from a URL relies on these shapes; a mismatch would surface only when writing back to a real source.

## [BACKLOG] 8- Add SKILL.test.md with script-use assertions to the finance skills (2026-10-05)

- status: developing
- prompt: `manage-investment-portfolio` and `analyse-account-transactions` (under `.xdrs/_local/bdrs/finance/skills/`) have scripts that do all arithmetic but no `SKILL.test.md`. Add one per skill with scenarios whose assertions require running the packaged command for every calculation and bulk-data step and not computing in chat, per agentme-edr-017 rule 02 and agentme-edr-005 rule 14, using fictitious data. Acceptance: `run-skill-tests` passes for both skills.
- deferred reason: Found while auditing skills for agentme-edr-005 rules 10-14; out of scope for the analyse-cvs change.
- why this is important: Without scenarios nothing detects a regression where the LLM starts computing balances or returns in chat.

## [BACKLOG] 7- Move template-based project scaffolding in create-* and monorepo-setup skills to scripts (2026-10-05)

- status: open
- prompt: `create-python-project`, `create-javascript-project`, `create-golang-project` and `monorepo-setup` (under `.xdrs/agentme/edrs/`) embed Makefile, mise, gitignore, README, package and pyproject templates in their phases and have the LLM write each file. Package a script per skill (`scripts/` with tests, per agentme-edr-005 rules 06-07) that takes the project name, module names and options and writes the files deterministically, and reduce the SKILL.md phases to collecting inputs, running the script and reviewing the result. Acceptance: skills run the script, scenarios assert it per agentme-edr-005 rule 14, and the generated files equal today's templates.
- deferred reason: Larger refactor of four skills, out of scope for the analyse-cvs change.
- why this is important: Scaffolding is bulk file generation (agentme-edr-005 rule 11); a script makes it faster, cheaper and identical every time.


## [BACKLOG] 6- Ask xdrs-core for a header-lint exemption for manifests and lockfiles in skill scripts (2026-10-05)

- status: open
- prompt: Structured skill scripts (agentme-edr-005) keep `package.json`, `pnpm-lock.yaml`, `tsconfig.json`, `pyproject.toml` and `uv.lock` in `scripts/`, and `xdrs-core lint` reports header errors on them. Ask xdrs-core (open an issue or change) to exempt manifests and lockfiles under `skills/*/scripts/`, then remove any workaround here. Acceptance: root `make lint` has no header errors for those files.
- deferred reason: Needs a change in the upstream xdrs-core package.
- why this is important: Keeps the lint output clean so real findings are not hidden.

## [BACKLOG] 1- ETF look-through exposure for the manage-investment-portfolio skill (2026-09-30)

- status: open
- prompt: Investigate and implement ETF look-through exposure (region, sector, top holdings) in the manage-investment-portfolio skill (`app/classify.py`, `app/reports/markets.py` in `scripts/src/portfolio_manager/`, `markets.md`). Classifications today come only from identifiers with a source URL and an as-of date; extend `classify` to accept constituent weights per ETF and report aggregated exposure.
- deferred reason: Needs a data source for ETF constituents; out of scope for the first version.
- why this is important: Allocation by ETF name hides the real regional and sector exposure.
