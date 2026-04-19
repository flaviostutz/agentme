---
name: 003-create-golang-project
description: >
  Scaffolds the initial boilerplate structure for a Go (Golang) CLI or library project following
  the standard tooling and layout defined in agentme-edr-010. Activate this skill when the user
  asks to create, scaffold, or initialize a new Go project, CLI binary, or Go module.
metadata:
  author: flaviostutz
  version: "1.0"
compatibility: Go 1.21+
---

## Overview

Creates a complete Go CLI project from scratch, following the layout from [agentme-edr-010](../../010-golang-project-tooling.md). Business logic lives in named feature packages; CLI wiring lives in `cli/<feature>/`; `main.go` is a thin dispatcher. The module root owns its `Makefile`, `README.md`, `dist/`, and `.cache/` folders.

Related EDRs: [agentme-edr-010](../../010-golang-project-tooling.md), [agentme-edr-016](../../../principles/016-cross-language-module-structure.md)

## Instructions

### Phase 1: Gather information

Ask for (or infer from context):

- **Module name** — Go module path, e.g. `github.com/<owner>/<project>` (in a monorepo this is typically the workspace module path plus the project subdirectory)
- **Binary name** — name of the produced CLI binary (default: project name)
- **Short description** — one sentence
- **Author** name or GitHub username
- **Go version** — default `1.24`
- **First feature package name** — the first domain package to scaffold (e.g. `analyze`, `parse`, `report`)
- **First CLI subcommand name** — typically matches the feature package (e.g. `analyze`)
- **Confirm target directory** — default: current workspace root

---

### Phase 2: Create root files

**`./.mise.toml`** (replace `[go-version]` and `[golangci-lint-version]`):

```toml
[tools]
go = "[go-version]"
golangci-lint = "[golangci-lint-version]"
```

Pin any additional project CLIs used by the Makefile here as well. Use an explicit `golangci-lint` version rather than `latest`.

**`go.mod`** (replace `[module]`, `[go-version]`):

```
module [module]

go [go-version]

require (
	github.com/sirupsen/logrus v1.9.3
	github.com/stretchr/testify v1.9.0
)
```

**`main.go`** (replace `[module]`, `[subcommand]`, `[feature]`):

```go
package main

import (
	"fmt"
	"os"

	cli[Feature] "[module]/cli/[feature]"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: [binary] [[feature]]")
		os.Exit(1)
	}

	switch os.Args[1] {
	case "[subcommand]":
		cli[Feature].Run(os.Args)
	default:
		fmt.Printf("Unknown command: %s\n", os.Args[1])
		fmt.Println("Usage: [binary] [[feature]]")
		os.Exit(1)
	}
}
```

**`Makefile`** (replace `[binary]`):

```makefile
SHELL := /bin/bash
MISE := mise exec --

BINARY := [binary]
CACHE_DIR := .cache
export GOCACHE := $(abspath $(CACHE_DIR)/go-build)
export GOMODCACHE := $(abspath $(CACHE_DIR)/go-mod)
export GOLANGCI_LINT_CACHE := $(abspath $(CACHE_DIR)/golangci-lint)

all: build lint test

setup:
	mise install
	$(MAKE) install

build: install
	@mkdir -p dist
	@mkdir -p $(GOCACHE) $(GOMODCACHE)
	$(MISE) go build -o dist/$(BINARY) .

build-all: build-arch-os-darwin-amd64 build-arch-os-darwin-arm64 build-arch-os-linux-amd64 build-arch-os-linux-arm64 build-arch-os-windows-amd64
	@echo "All platform builds complete"

build-arch-os-darwin-amd64:
	$(MAKE) build-arch-os OS=darwin ARCH=amd64

build-arch-os-darwin-arm64:
	$(MAKE) build-arch-os OS=darwin ARCH=arm64

build-arch-os-linux-amd64:
	$(MAKE) build-arch-os OS=linux ARCH=amd64

build-arch-os-linux-arm64:
	$(MAKE) build-arch-os OS=linux ARCH=arm64

build-arch-os-windows-amd64:
	$(MAKE) build-arch-os OS=windows ARCH=amd64

build-arch-os:
	@if [ "${OS}" == "" ]; then echo "ENV OS is required"; exit 1; fi
	@if [ "${ARCH}" == "" ]; then echo "ENV ARCH is required"; exit 1; fi
	@echo "Compiling $(BINARY) for ${OS}-${ARCH}..."
	@mkdir -p dist/${OS}-${ARCH}
	@mkdir -p $(GOCACHE) $(GOMODCACHE)
	$(MISE) go mod download
	GOOS=${OS} GOARCH=${ARCH} CGO_ENABLED=0 $(MISE) go build -a -o dist/${OS}-${ARCH}/$(BINARY) .
	@echo "Done"

install:
	$(MISE) go mod download

lint:
	$(MISE) golangci-lint run ./...

lint-fix:
	$(MISE) golangci-lint run --fix ./...

test:
	$(MISE) go test -cover ./...

test-coverage:
	@mkdir -p $(CACHE_DIR)
	$(MISE) go test -coverprofile=$(CACHE_DIR)/coverage.out ./...
	$(MISE) go tool cover -func $(CACHE_DIR)/coverage.out

benchmark:
	$(MISE) go test -bench . -benchmem -count 5 ./...

clean:
	rm -rf dist
	rm -rf .cache

start:
	$(MISE) go run ./ [subcommand]
```

**`.golangci.yml`**:

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

**`.gitignore`**:

```
dist/
.cache/
coverage.out
*.pprof
.DS_Store
```

**`README.md`** (replace `[binary]`, `[description]`, `[owner]`, `[repo]`):

```markdown
# [binary]

[description]

## Usage

    [binary] [subcommand] --help

## Development

	make setup
	make build    # compile binary to dist/
	make lint     # run golangci-lint with cache in .cache/
	make test     # run tests with coverage artifacts in .cache/
	make start    # run locally with default args
```

---

### Phase 3: Create the feature package

**`[feature]/[feature].go`** (replace `[feature]`, `[Feature]`):

```go
package [feature]

import "github.com/sirupsen/logrus"

// Options holds the parameters for [Feature] analysis.
type Options struct {
	Verbose bool
}

// Result holds the output of a [Feature] run.
type Result struct {
	Summary string
}

// Run executes the [Feature] logic with the given options.
func Run(opts Options) (Result, error) {
	if opts.Verbose {
		logrus.SetLevel(logrus.DebugLevel)
	}
	logrus.Debug("[Feature] started")

	// TODO: implement business logic here

	return Result{Summary: "ok"}, nil
}
```

**`[feature]/[feature]_test.go`** (replace `[feature]`, `[Feature]`):

```go
package [feature]

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test[Feature]Run(t *testing.T) {
	result, err := Run(Options{Verbose: false})
	require.NoError(t, err)
	assert.Equal(t, "ok", result.Summary)
}
```

---

### Phase 4: Create the CLI package

**`cli/[feature]/[feature].go`** (replace `[module]`, `[feature]`, `[Feature]`, `[subcommand]`):

```go
package cli[Feature]

import (
	"flag"
	"fmt"
	"os"

	"github.com/sirupsen/logrus"
	"[module]/[feature]"
)

// Run parses CLI flags for the [subcommand] command and calls the domain package.
func Run(args []string) {
	fs := flag.NewFlagSet("[subcommand]", flag.ExitOnError)
	verbose := fs.Bool("verbose", false, "Show verbose logs during processing")

	if err := fs.Parse(args[2:]); err != nil {
		fmt.Fprintf(os.Stderr, "error parsing flags: %v\n", err)
		os.Exit(1)
	}

	if *verbose {
		logrus.SetLevel(logrus.DebugLevel)
	}

	result, err := [feature].Run([feature].Options{
		Verbose: *verbose,
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(result.Summary)
}
```

---

### Phase 5: Verify and run

After creating all files, run the following in the project root:

```bash
make setup
make all
```

Fix any compile or lint errors before finishing.

---

## Conventions and reminders

- `main.go` dispatches only — no logic.
- Business logic only in `[feature]/` packages — no flag parsing, no `fmt.Println` for diagnostics.
- `cli/[feature]/` owns flags, output, and calls domain. No logic here beyond reading flags and printing results.
- All tests co-located (`*_test.go` next to the file under test).
- Use `tests_integration/` for integration flows and `tests_benchmark/` when benchmarks need dedicated harnesses or datasets.
- Log with `logrus`; never use `fmt.Println` for diagnostic/debug output.
- All development tasks go through `make` targets. The Makefile recipes call `mise exec -- go ...` and related tools directly.
- Do not create an `internal/` package unless explicitly justified (importability is preferred).
- If the project is a reusable library, place consumer examples in a sibling `examples/` folder outside the module root and keep them on the public module import path.
