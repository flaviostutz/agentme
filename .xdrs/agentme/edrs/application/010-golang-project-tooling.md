---
name: agentme-edr-010-go-project-tooling-and-structure
description: Defines the standard Go project toolchain, layout, and Makefile workflow using Mise for agentme-based projects. Use when scaffolding or reviewing Go projects.
---

# agentme-edr-010: Go project tooling and structure

## Context and Problem Statement

Go (Golang) projects often diverge in their module layout, tooling conventions, and build processes, making cross-project onboarding slow and CI pipelines hard to standardize. Without clear decisions on linting, testing, binary distribution, and package structure, teams repeatedly reinvent the same scaffolding.

What tooling and project structure should Go projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Go toolchain with `go build`, `go test`, and `golangci-lint`, module-root folder responsibilities from [agentme-edr-016](../principles/016-cross-language-module-structure.md), feature packages in subdirectories, a `cli/` package for command wiring, and a Makefile as the single entry point for all development tasks.**

A predictable layout and minimal external tooling keep Go projects approachable, fast to build, and easy to distribute as cross-platform binaries.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Mandatory tool version management and command runner for Go, `golangci-lint`, and project CLIs |
| **go toolchain** | Compilation, testing, formatting (`go build`, `go test`, `go fmt`, `go vet`, `go mod`) |
| **golangci-lint** | Linting — aggregates many linters in one fast run; configured via `.golangci.yml` |
| **monotag** | Version tagging from git history for the `publish` target |

All commands are run exclusively through the Makefile, never ad-hoc. The project root **MUST** define a `.mise.toml` that pins `go`, `golangci-lint`, and any other Go-related CLIs used by the project. Contributors and CI **MUST** bootstrap with `make setup` or `mise install`, then invoke routine work with `make <target>`. Each Makefile recipe **MUST** execute the underlying tool through `mise exec -- <tool> ...`, following [agentme-edr-017](../devops/017-tool-execution-and-scripting.md).
Direct installation of project-required Go CLIs with `go install ...@latest` as a repair step is **NOT** allowed unless an XDR for that repository explicitly permits it.

#### Project structure

```
/                              # project root or Go module root inside a monorepo
├── .mise.toml                 # pinned Go, golangci-lint, and related CLIs
├── Makefile                   # build, lint, test, publish, and utility targets
├── README.md                  # module README with usage and development commands
├── .gitignore                 # MUST ignore dist/ and .cache/
├── .golangci.yml              # golangci-lint configuration
├── go.mod                     # module declaration (github.com/<owner>/<project>)
├── go.sum                     # locked dependency checksums
├── main.go                    # binary entry point — argument dispatch only, no logic
├── .cache/                    # GOCACHE, GOMODCACHE, golangci-lint cache, coverage
├── dist/                      # built binaries and packaged outputs
├── <feature-a>/               # domain package (e.g. ownership/, changes/, utils/)
│   ├── *.go                   # business logic
│   └── *_test.go              # unit tests co-located with source
├── <feature-b>/
│   └── ...
├── cli/                       # CLI wiring — ties flags to domain packages
│   ├── <feature-a>/
│   │   └── *.go
│   └── <feature-b>/
│       └── *.go
├── tests_integration/         # optional integration tests for this module
├── tests_benchmark/           # optional benchmark harnesses and datasets
└── examples/                  # optional sibling consumer examples for libraries
```

**Key layout rules:**

- One Go module per project (`go.mod` at the project root). In a monorepo, each Go project has its own `go.mod` in its subdirectory. No nested modules within a single project unless explicitly justified.
- In a multi-module repository, each Go module MUST live in its own folder root with its own `Makefile`, `README.md`, `dist/`, and `.cache/`.
- `main.go` is solely an argument dispatcher — it reads `os.Args[1]` and delegates to a `cli/<feature>/Run*()` function. No domain logic lives in `main.go`.
- Business logic lives in named feature packages at the root (e.g., `ownership/`, `changes/`, `utils/`). These packages are importable and testable without any CLI concerns.
- `cli/` packages own flag parsing, output formatting, and the wiring between flags and domain functions. No business logic lives in `cli/`.
- Packages are flat by default; sub-packages are only introduced when a feature package itself exceeds ~400 lines or has clearly separable sub-concerns.
- Consumer examples for reusable libraries belong in a sibling `examples/` folder and MUST import the public module path rather than reaching into internal source paths. Because Go libraries are not typically consumed from a local packaged artifact, local example validation may use a temporary module replacement for resolution, but the import path MUST remain the public module path.

#### go.mod

- Module path: `github.com/<owner>/<project>` (or the relevant VCS path for the project)
- Use the latest stable Go version (e.g. `go 1.24`).
- Separate `require` blocks: direct dependencies first, then `// indirect` dependencies.
- The Go version declared in `go.mod` and the Go version pinned in `.mise.toml` **MUST** stay aligned.

#### Makefile targets

| Target | Description |
|--------|-------------|
| `all` | Default; runs `build lint test` in sequence |
| `build` | `mise exec -- go mod download && mise exec -- go build -o dist/<binary>` with Go caches redirected into `.cache/` |
| `build-all` | Cross-compile for all target platforms (darwin/linux/windows × amd64/arm64) |
| `build-arch-os` | Compile for a specific `OS` and `ARCH` environment variable pair; output to `dist/${OS}-${ARCH}/<binary>` |
| `install` | `mise exec -- go mod download` |
| `lint` | `mise exec -- golangci-lint run ./...` with its cache redirected into `.cache/` |
| `lint-fix` | `mise exec -- golangci-lint run --fix ./...` with its cache redirected into `.cache/` |
| `test` | `mise exec -- go test -cover ./...` — runs all tests with coverage and stores disposable outputs under `.cache/` |
| `test-unit` | `mise exec -- go test -cover ./...` — alias for unit tests only (same here; integration tests get a separate tag) |
| `coverage` | `mise exec -- go tool cover -func .cache/coverage.out` — displays coverage summary |
| `clean` | Remove `dist/` and `.cache/` |
| `start` | `mise exec -- go run ./ <default-args>` — launch the binary locally for dev use |
| `publish` | Tag with `mise exec -- npx -y monotag ...`, then push tag + binaries to GitHub Releases |

The required invocation pattern is:

```sh
make setup
make build
make test
make lint
```

The Makefile recipes themselves must use `mise exec --` for the underlying tool commands.

#### Cross-platform binary distribution

When the project produces a CLI binary for end-users:

- Build separate binaries for: `darwin/amd64`, `darwin/arm64`, `linux/amd64`, `linux/arm64`, `windows/amd64`.
- Use `GOOS`, `GOARCH`, and `CGO_ENABLED=0` to produce fully static binaries.
- Store outputs under `dist/${OS}-${ARCH}/<binary-name>`.
- Optionally wrap binaries in npm packages (one package per platform) for distribution via `npx`. Each npm package contains only the binary for its platform; a meta-package with a `bin/` entry that delegates to the correct platform package is added at the root of the npm folder.

#### Testing

- Tests are co-located with source: `<feature>/<file>_test.go`.
- Use `github.com/stretchr/testify` (`assert`, `require`) for test assertions.
- Run all tests: `go test -cover ./...`
- Benchmarks: keep simple `Benchmark*` functions co-located in `*_test.go`; use `tests_benchmark/` when the benchmark needs dedicated harnesses or datasets.
- Integration or slow tests: guard with `//go:build integration` and keep them in `tests_integration/` when they are not naturally co-located with one package.

Redirect Go tool caches into `.cache/` using `GOCACHE`, `GOMODCACHE`, and `GOLANGCI_LINT_CACHE` from the module `Makefile` so the repository does not accumulate scattered cache directories.

#### Linting

Configure `.golangci.yml` with at minimum:

```yaml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - typecheck
run:
  timeout: 5m
```

#### Logging

Use `github.com/sirupsen/logrus` for structured logging. Set the log level from a `--verbose` CLI flag, defaulting to `false` / `WarnLevel`. Do not use `fmt.Println` for diagnostic output.

#### CLI flag parsing

Use the standard library `flag` package for CLI flags. Each `cli/<feature>` package defines its own `FlagSet`, parses it from `os.Args[2:]`, and calls the corresponding domain function.

## References

- [003-create-golang-project](skills/003-create-golang-project/SKILL.md) — scaffolds a new Go project following this structure
