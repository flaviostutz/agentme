---
name: agentme-edr-policy-302-github-ci-cd-pipelines
description: Defines the standard GitHub Actions workflow split for CI, release tagging, publishing, and stage deployment. Use when configuring project automation.
apply-to: Projects using GitHub Actions
valid-from: 2026-05-25
---

# agentme-edr-policy-302: GitHub CI/CD pipelines

## Context and Problem Statement

Without a defined GitHub Actions pipeline structure, projects end up with inconsistent workflows — some combine CI and publishing in a single file, others trigger builds on wrong events, and release tagging is done ad-hoc. This leads to accidental publishes, broken release histories, and non-reproducible builds.

What GitHub Actions workflows should every project follow to ensure a safe, predictable, and automated CI/CD lifecycle?

## Decision Outcome

**Use separate, purpose-scoped GitHub Actions workflows: `ci.yml` for build verification on PRs and main, `release.yml` for calculating and creating a version tag with monotag, `publish.yml` for publishing artifacts when a version tag is pushed, and `deploy.yml` for deploying environments as defined in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `11-stage-deployment-lifecycle`.**

Separating these concerns eliminates accidental publishes from CI runs, ensures monotag has access to the full git history, and makes each workflow independently auditable and re-runnable.

### Details

#### Workflow overview

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | `pull_request` → `main`, `push` → `main` | Build, lint, and test the codebase |
| `release.yml` | `workflow_dispatch` | Tag the next version using monotag |
| `publish.yml` | `push` of any version tag | Publish artifacts for the tagged version |
| `deploy.yml` | `push` → `main`, `push` of any version tag | Deploy `tst`, `acc` or `prd` |

Version tags have no `v` prefix: `<semver>` in a single-module repository and `<module-name>/<semver>` in a monorepo, as defined in [agentme-edr-301](301-monorepo-structure.md). Tag triggers MUST use the pattern `'**'` so tags containing `/` match.

All workflows run on `ubuntu-latest`. Tool versions MUST be managed by Mise via `jdx/mise-action`. Projects SHOULD have a `.mise.toml` file to configure it

---

#### 01-ci-workflow

File: `.github/workflows/ci.yml`

Projects MUST configure this workflow, triggered on every PR targeting `main` and every push to `main`. It runs the standard `build`, `lint`, and `test` targets from the root Makefile and fails the workflow if any step exits non-zero.

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - run: make build
      - run: make lint
      - run: make test
```

*Why separate steps:* Separate steps surface exactly which phase failed (build, lint, or test) without requiring log inspection.

---

#### 02-release-workflow

File: `.github/workflows/release.yml`

Projects MUST use this manually dispatched (`workflow_dispatch`) workflow. It calculates the next semantic version tag using **monotag** and pushes that tag to the repository. Pushing the tag then automatically triggers the publish workflow.

The checkout step MUST use `fetch-depth: 0` so monotag can traverse the full commit history to determine the correct next version.

```yaml
name: release

on:
  workflow_dispatch:
    inputs:
      prerelease:
        description: 'Pre-release'
        type: boolean
        default: true

jobs:
  create-tag:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          # this is needed if you want the tag push to trigger another workflow
          # create a personal token and set a secret with name GH_PERSONAL_TOKEN
          # https://github.com/orgs/community/discussions/27028
          token: ${{ secrets.GH_PERSONAL_TOKEN }}
      - name: Create tag and push to repo
        run: |
          git config --global user.email "noreply@github.com"
          git config --global user.name "Github Wokflow"
          npx -y monotag@latest tag-push ${{ inputs.prerelease == true && '--prerelease' || '' }}
```

*Why `workflow_dispatch`:* Manual triggering gives developers explicit control over when a new release tag is created, preventing unintended releases from routine merges.

*Why `contents: write`:* Required to allow the workflow to push the new tag back to the repository.

---

#### 03-publish-workflow

File: `.github/workflows/publish.yml`

Projects that publish artifacts MUST configure this workflow, triggered exclusively when a version tag is pushed to the repository. This ensures only explicitly tagged commits produce published artifacts. It resolves the module from the tag (`dirname` of the tag name is `.` at the root and the module path in a monorepo) and runs `make -C <module> publish` against the tagged commit. A module that is deployed instead of published has no `publish` target and is not published.

```yaml
name: publish

on:
  push:
    tags:
      - '**'

permissions:
  contents: read
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - run: echo "MODULE=$(dirname "$GITHUB_REF_NAME")" >> "$GITHUB_ENV"
      - run: make -C "$MODULE" build
      - run: make -C "$MODULE" lint
      - run: make -C "$MODULE" test
      - run: git reset --hard HEAD
      - run: make -C "$MODULE" publish
```

*Why rebuild on publish:* The checkout is done from the exact tag commit. Rebuilding ensures the published artifact matches exactly what is tagged, rather than relying on a prior CI artifact.

*Why `id-token: write`:* Required for npm provenance attestation via `npm publish --provenance`, as specified in [agentme-edr-101](../application/101-javascript-project-tooling.md).

---

#### 04-performance-step-is-optional

Performance tests need a deployed environment, so `ci.yml` MUST NOT run them. A project MAY add a separate manually dispatched or post-deploy job that runs `make test-performance` (or one `test-performance-<kind>` target) with `STAGE` set to `acc`, and MAY run the baseline kind against a prod canary. Kinds, environments, guardrails and thresholds follow [agentme-edr-306](306-performance-testing.md).

---

#### 05-deploy-workflow

File: `.github/workflows/deploy.yml`

Projects that deploy environments MUST use this workflow and MUST include only the stage jobs they use. Stage selection follows [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `11-stage-deployment-lifecycle`:

- `tst` runs on push to `main` and deploys all deployable modules (the root `make deploy` delegates to each module); an unchanged IaC deploy is a no-op.
- A `resolve` job runs on tag pushes. It takes the semver after the last `/` of the tag and sets stage `acc` when it contains `-`, otherwise `prd`, and outputs the module path. Stage jobs MUST select on these outputs, not on a pattern over the whole tag, because module names may contain `-`.
- Every stage job MUST rerun `make build`, `make lint` and `make test` for its commit, then `STAGE=<stage> make deploy`, so each environment is built with its own configuration.
- The `prd` job MUST use the GitHub Environment `prd` configured with required reviewers, so a manual approval happens before the job and its credentials are used. Tag rulesets restricting who can create tags MAY be added, but the approval is the main production protection.
- Credentials MUST reach the job as the standard AWS environment variables of [agentme-edr-308](308-iac-module-and-deployment.md). OIDC role assumption with `aws-actions/configure-aws-credentials`, which exports them, SHOULD be used; static keys held as secrets of a per-stage GitHub Environment MAY be used. For `tst` and `acc` only, stage-suffixed repository secrets (for example `AWS_ACCESS_KEY_ID_ACC`) MAY be mapped to the standard names in the job.
- `deploy.yml` MUST NOT run `undeploy` for `tst`, `acc` or `prd`.
- To roll back, re-run the workflow of the previous good tag; it passes the `prd` approval again.

```yaml
name: deploy

on:
  push:
    branches: [main]
    tags:
      - '**'

permissions:
  contents: read
  id-token: write

jobs:
  resolve:
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    outputs:
      module: ${{ steps.tag.outputs.module }}
      stage: ${{ steps.tag.outputs.stage }}
    steps:
      - id: tag
        run: |
          echo "module=$(dirname "$GITHUB_REF_NAME")" >> "$GITHUB_OUTPUT"
          case "${GITHUB_REF_NAME##*/}" in
            *-*) echo "stage=acc" >> "$GITHUB_OUTPUT" ;;
            *) echo "stage=prd" >> "$GITHUB_OUTPUT" ;;
          esac

  deploy-tst:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: tst
    env:
      STAGE: tst
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: make build
      - run: make lint
      - run: make test
      - run: make deploy

  deploy-acc:
    needs: resolve
    if: needs.resolve.outputs.stage == 'acc'
    runs-on: ubuntu-latest
    environment: acc
    env:
      STAGE: acc
      MODULE: ${{ needs.resolve.outputs.module }}
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: make -C "$MODULE" build
      - run: make -C "$MODULE" lint
      - run: make -C "$MODULE" test
      - run: make -C "$MODULE" deploy

  deploy-prd:
    needs: resolve
    if: needs.resolve.outputs.stage == 'prd'
    runs-on: ubuntu-latest
    environment: prd # required reviewers: manual approval before the job runs
    env:
      STAGE: prd
      MODULE: ${{ needs.resolve.outputs.module }}
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: make -C "$MODULE" build
      - run: make -C "$MODULE" lint
      - run: make -C "$MODULE" test
      - run: make -C "$MODULE" deploy
```

*Why Environments:* `vars.AWS_DEPLOY_ROLE_ARN` and `vars.AWS_REGION` are set per GitHub Environment, so each stage assumes its own role in its own account.

---

#### Required secrets and permissions

| Secret / Permission | Used in | Purpose |
|--------------------|---------|---------| 
| `GITHUB_TOKEN` (built-in) | `release.yml` | Push newly calculated tag back to the repository |
| `GH_PERSONAL_TOKEN` | `release.yml` | Token that lets the tag push trigger `publish.yml` and `deploy.yml` (tags pushed with `GITHUB_TOKEN` trigger no workflows) |
| `id-token: write` | `publish.yml`, `deploy.yml` | OIDC token for npm provenance and for AWS role assumption |
| `contents: write` | `release.yml` | Allow the workflow job to push tags |
| `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION` (Environment variables) | `deploy.yml` | Role and region of each stage; static-key alternative: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` as Environment secrets |

---

#### Relationship between workflows

```
PR opened / push to main
        │
        ▼
  ci.yml runs
  (build + lint + test)
        │
        ▼ (merge to main)
  developer dispatches
  release.yml manually
        │
        ▼
  monotag calculates
  next semver tag
        │
        ▼
  tag pushed → 1.2.3 (or orders/1.2.3 in a monorepo)
        │
        ▼
  publish.yml triggered
  (build + publish artifacts)

  Deployable modules:
  merge to main      → deploy.yml → tst
  tag 1.2.3-beta.1   → deploy.yml → acc
  tag 1.2.3          → deploy.yml → approval → prd
```

