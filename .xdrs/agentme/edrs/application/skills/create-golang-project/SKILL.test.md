---
skill: create-golang-project
skill-version: "1.1.0"
---

## Test Scenarios

### Scenario 1: Create a new Go CLI project, happy path

**Trigger / Input**

"Create a Go CLI project. Module `github.com/acme/logscan`, binary name `logscan`, first feature
`scan`, first subcommand `scan`."

**Expected Behaviour**

1. Phase 1 gathers or infers the module path, binary name, Go version (default `1.24`), first
   feature package name, and first CLI subcommand name.
2. Phase 2 creates `.mise.toml`, `go.mod`, a `main.go` that only dispatches to `adapters/cli`, the
   root `Makefile` (exporting `GOCACHE`/`GOMODCACHE`/`GOLANGCI_LINT_CACHE`, with `build`,
   `build-all`, `lint`, `test`, `test-coverage`, `benchmark`, and `clean` targets), `.golangci.yml`,
   `.gitignore`, and `README.md`.
3. Phase 3 creates `app/scan/scan.go` and `app/scan/scan_test.go` with the `Options`/`Result`/`Run`
   shape.
4. Phase 4 creates `adapters/cli/scan.go` that parses flags and calls into `app/scan`.
5. Phase 5 runs `make setup` and `make all`, fixing any compile or lint errors before finishing.

**Assertions**

- [ ] Output creates `main.go` containing only argument dispatch, with no business logic.
- [ ] Output places the `scan` domain logic in `app/scan/scan.go` and the flag parsing in
      `adapters/cli/scan.go`, not the reverse.
- [ ] Output's root `Makefile` exports `GOCACHE`, `GOMODCACHE`, and `GOLANGCI_LINT_CACHE` under
      `.cache/` and defines `build`, `lint`, and `test` targets.
- [ ] Output reports running `make setup` and `make all` and fixes any compile or lint errors
      before declaring completion.

### Scenario 2: Business logic requested inside main.go is redirected to app/

**Trigger / Input**

"Put the scan logic directly inside `main.go` instead of a separate package, and use
`fmt.Println` to print debug output during scanning."

**Expected Behaviour**

Per the Conventions and reminders section, the skill keeps `main.go` as a thin dispatcher with no
business logic, places the scan logic in `app/scan/`, and uses `logrus` instead of `fmt.Println`
for diagnostic/debug output.

**Assertions**

- [ ] Output does not place business logic inside `main.go`.
- [ ] Output uses `logrus` rather than `fmt.Println` for diagnostic/debug output.

### Scenario 3: internal/ package is not created without explicit justification

**Trigger / Input**

"Create an `internal/` package for the scan helpers so other repositories can't import them."

**Expected Behaviour**

Per the Conventions and reminders section, the skill does not create an `internal/` package by
default — it keeps the helpers importable (e.g., under `app/scan/` or `shared/`) unless the user
gives an explicit justification for restricting importability.

**Assertions**

- [ ] Output does not create an `internal/` package without the user first providing an explicit
      justification.
- [ ] Output keeps the scan helpers in an importable location such as `app/scan/` or `shared/`.
