# TODO

<!-- Format: see agentme-edr-001 -->

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

## [BACKLOG] 2- Generate Portfolio Performance import files from the portfolio ledger (2026-09-30)

- status: open
- prompt: Implement an export command in `.xdrs/_local/bdrs/finance/skills/manage-investment-portfolio/scripts/` (for example `pm export`) that writes Portfolio Performance importable CSV files (accounts, securities, transactions) from `data/events.json` and `data/accounts.json`. Acceptance: importing the files into Portfolio Performance reproduces the ledger's cash and positions; the export is deterministic and has offline tests with fictitious data.
- deferred reason: Out of scope for the first version of the skill.
- why this is important: Lets the user cross-check the results in an established tool.

## [BACKLOG] 1- ETF look-through exposure for the manage-investment-portfolio skill (2026-09-30)

- status: open
- prompt: Investigate and implement ETF look-through exposure (region, sector, top holdings) in the manage-investment-portfolio skill (`app/classify.py`, `app/report.py` in `scripts/src/portfolio_manager/`, `markets.md`). Classifications today come only from identifiers with a source URL and an as-of date; extend `classify` to accept constituent weights per ETF and report aggregated exposure.
- deferred reason: Needs a data source for ETF constituents; out of scope for the first version.
- why this is important: Allocation by ETF name hides the real regional and sector exposure.
