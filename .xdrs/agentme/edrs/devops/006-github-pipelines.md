---
name: agentme-edr-006-github-ci-cd-pipelines
description: Defines the standard GitHub Actions workflow split for CI, release tagging, and publishing. Use when configuring project automation.
---

# agentme-edr-006: GitHub CI/CD pipelines

## Context and Problem Statement

Without a defined GitHub Actions pipeline structure, projects end up with inconsistent workflows — some combine CI and publishing in a single file, others trigger builds on wrong events, and release tagging is done ad-hoc. This leads to accidental publishes, broken release histories, and non-reproducible builds.

What GitHub Actions workflows should every project follow to ensure a safe, predictable, and automated CI/CD lifecycle?

## Decision Outcome

**Use three separate, purpose-scoped GitHub Actions workflows: `ci.yml` for build verification on PRs and main, `release.yml` for calculating and creating a version tag with monotag, and `publish.yml` for publishing artifacts when a version tag is pushed.**

Separating these concerns eliminates accidental publishes from CI runs, ensures monotag has access to the full git history, and makes each workflow independently auditable and re-runnable.

### Implementation Details

#### Workflow overview

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | `pull_request` → `main`, `push` → `main` | Build, lint, and test the codebase |
| `release.yml` | `workflow_dispatch` | Tag the next version using monotag |
| `publish.yml` | `push` of tags matching `*` | Publish artifacts for the tagged version |

All workflows run on `ubuntu-latest`. Tool versions MUST be managed by Mise via `jdx/mise-action`. Projects should have a .mise.toml file to configure it

---

#### 01-ci-workflow

File: `.github/workflows/ci.yml`

Triggered on every PR targeting `main` and every push to `main`. Runs the standard `build`, `lint`, and `test` targets from the root Makefile and fails the workflow if any step exits non-zero.

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

Manually dispatched (`workflow_dispatch`). Calculates the next semantic version tag using **monotag** and pushes that tag to the repository. Pushing the tag then automatically triggers the publish workflow.

The checkout step **must** use `fetch-depth: 0` so monotag can traverse the full commit history to determine the correct next version.

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
      - uses: actions/checkout@v3
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
          npx -y monotag@latest tag-push ${{ inputs.prerelease == true && '--pre-release' || '' }}
```

*Why `workflow_dispatch`:* Manual triggering gives developers explicit control over when a new release tag is created, preventing unintended releases from routine merges.

*Why `contents: write`:* Required to allow the workflow to push the new tag back to the repository.

---

#### 03-publish-workflow

File: `.github/workflows/publish.yml`

Triggered exclusively when a tag matching `v*.*.*` is pushed to the repository. This ensures only explicitly tagged commits produce published artifacts. Runs `make publish` against the tagged commit.

```yaml
name: publish

on:
  push:
    tags:
      - '*'

permissions:
  contents: read
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
      - run: make build
      - run: make lint
      - run: make test
      - run: git reset --hard HEAD
      - run: make publish

```

*Why rebuild on publish:* The checkout is done from the exact tag commit. Rebuilding ensures the published artifact matches exactly what is tagged, rather than relying on a prior CI artifact.

*Why `id-token: write`:* Required for npm provenance attestation via `npm publish --provenance`, as specified in [agentme-edr-003](../application/003-javascript-project-tooling.md).

---

#### Required secrets and permissions

| Secret / Permission | Used in | Purpose |
|--------------------|---------|---------| 
| `GITHUB_TOKEN` (built-in) | `release.yml` | Push newly calculated tag back to the repository |
| `id-token: write` | `publish.yml` | Generate OIDC token for npm provenance |
| `contents: write` | `release.yml` | Allow the workflow job to push tags |

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
  tag pushed → v1.2.3
        │
        ▼
  publish.yml triggered
  (build + publish artifacts)
```

