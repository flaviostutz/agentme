---
name: agentme-edr-010-go-project-tooling-and-structure
description: Defines the standard Go project toolchain, layout, and Makefile workflow for agentme-based projects. Use when scaffolding or reviewing Go projects.
---

# agentme-edr-010: Go project tooling and structure

## Context and Problem Statement

Go (Golang) projects often diverge in their module layout, tooling conventions, and build processes, making cross-project onboarding slow and CI pipelines hard to standardize. Without clear decisions on linting, testing, binary distribution, and package structure, teams repeatedly reinvent the same scaffolding.

What tooling and project structure should Go projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use the standard Go toolchain (`go build`, `go test`) with `golangci-lint` for linting, feature packages in subdirectories (no `internal/` by default), a `cli/` package for command wiring, and a Makefile as the single entry point for all development tasks, with the Go toolchain and related CLIs sourced from the repository's Mise-managed environment when the repository defines `.mise.toml`.**

A predictable layout and minimal external tooling keep Go projects approachable, fast to build, and easy to distribute as cross-platform binaries.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **go toolchain** | Compilation, testing, formatting (`go build`, `go test`, `go fmt`, `go vet`, `go mod`) |
| **golangci-lint** | Linting — aggregates many linters in one fast run; configured via `.golangci.yml` |
| **monotag** | Version tagging from git history for the `publish` target |

All commands are run exclusively through the Makefile, never ad-hoc.
When the repository has a root `.mise.toml`, `go`, `golangci-lint`, and any other Go-related CLIs used by the project **MUST** be pinned there and resolved from the Mise-managed environment rather than the host machine.
Direct installation of project-required Go CLIs with `go install ...@latest` as a repair step is **NOT** allowed unless an XDR for that repository explicitly permits it.

#### Project structure

```
/                              # project root (single Go module)
├── Makefile                   # build, lint, test, publish, and utility targets
├── go.mod                     # module declaration (github.com/<owner>/<project>)
├── go.sum                     # locked dependency checksums
├── main.go                    # binary entry point — argument dispatch only, no logic
├── .golangci.yml              # golangci-lint configuration
├── .gitignore
├── README.md
├── <feature-a>/               # domain package (e.g. ownership/, changes/, utils/)
│   ├── *.go                   # business logic
│   └── *_test.go              # unit tests co-located with source
├── <feature-b>/
│   └── ...
└── cli/                       # CLI wiring — ties flags to domain packages
    ├── <feature-a>/
    │   └── *.go
    └── <feature-b>/
        └── *.go
```

**Key layout rules:**

- One Go module per project (`go.mod` at the project root). In a monorepo, each Go project has its own `go.mod` in its subdirectory. No nested modules within a single project unless explicitly justified.
- `main.go` is solely an argument dispatcher — it reads `os.Args[1]` and delegates to a `cli/<feature>/Run*()` function. No domain logic lives in `main.go`.
- Business logic lives in named feature packages at the root (e.g., `ownership/`, `changes/`, `utils/`). These packages are importable and testable without any CLI concerns.
- `cli/` packages own flag parsing, output formatting, and the wiring between flags and domain functions. No business logic lives in `cli/`.
- Packages are flat by default; sub-packages are only introduced when a feature package itself exceeds ~400 lines or has clearly separable sub-concerns.

#### go.mod

- Module path: `github.com/<owner>/<project>` (or the relevant VCS path for the project)
- Use the latest stable Go version (e.g. `go 1.24`).
- Separate `require` blocks: direct dependencies first, then `// indirect` dependencies.
- If the repository uses Mise, the Go version declared in `go.mod` and the Go version pinned in `.mise.toml` **MUST** stay aligned.

#### Makefile targets

| Target | Description |
|--------|-------------|
| `all` | Default; runs `build lint test` in sequence |
| `build` | `go mod download && go build -o dist/<binary>` |
| `build-all` | Cross-compile for all target platforms (darwin/linux/windows × amd64/arm64) |
| `build-arch-os` | Compile for a specific `OS` and `ARCH` environment variable pair; output to `dist/${OS}-${ARCH}/<binary>` |
| `install` | `go mod download` |
| `lint` | `golangci-lint run ./...` |
| `lint-fix` | `golangci-lint run --fix ./...` |
| `test` | `go test -cover ./...` — runs all tests with coverage |
| `test-unit` | `go test -cover ./...` — alias for unit tests only (same here; integration tests get a separate tag) |
| `coverage` | `go tool cover -func ./coverage.out` — displays coverage summary |
| `clean` | Remove `dist/` and any coverage files |
| `start` | `go run ./ <default-args>` — launch the binary locally for dev use |
| `publish` | Tag with `monotag`, then push tag + binaries to GitHub Releases |

When the repository uses Mise, the intended invocation pattern is:

```sh
mise install
mise exec -- make build
mise exec -- make test
mise exec -- make lint
```

Using `make build`, `make test`, or `make lint` from an already activated Mise shell is equivalent.

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
- Benchmarks: `go test -bench . -benchmem -count 20`
- Integration or slow tests: guard with `//go:build integration` and skip in unit runs via `-tags=unit`.

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

### Related Skills

- [003-create-golang-project](skills/003-create-golang-project/SKILL.md) — scaffolds a new Go project following this structure
