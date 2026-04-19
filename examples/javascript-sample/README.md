# javascript-sample

A hello world library sample organized as a module root in `lib/` with consumer examples in `examples/`.

## Getting Started

```bash
mise install
make test
```

## Overview

This sample keeps the published package in `lib/` and validates consumer behavior through the packaged artifact in `examples/usage-basic/`.

## Repository Map

| Folder | Description |
|--------|-------------|
| `lib/` | Published npm package with its own README, Makefile, dist, and cache strategy |
| `examples/` | Runnable consumer examples that install the built package |

## Development

```bash
make build
make lint
make test
```
