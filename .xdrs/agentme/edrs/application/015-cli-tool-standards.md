---
name: agentme-edr-015-cli-tool-standards
description: Defines how distributable CLI tools should separate command handling from library logic and expose consistent command behavior. Use when designing or reviewing CLI interfaces.
applied-to: Distributable CLI tools and their standalone libraries
---

# agentme-edr-015: CLI tool standards

## Context and Problem Statement

CLI projects often mix command parsing, business logic, config loading, and output formatting in one entry point, making them hard to reuse as libraries and inconsistent to operate.

What structure and interface rules should distributable CLI tools follow so they remain discoverable, scriptable, and reusable outside the command line?

## Decision Outcome

**Use a command-oriented CLI as a thin adapter over a standalone library, with CLI-owned config discovery, mandatory help/version/verbose flags, and consistent progress and exit behavior.**

This keeps the user-facing command predictable while preserving a clean library API for embedding, testing, and automation.

### Implementation Details

#### CLI command surface

- CLI tools should default to the format `[tool] [command] [options] [arguments]`.
- Example: `filedist extract --packages=test mydir`
- A single-action tool may omit `[command]` only when adding a subcommand would be artificial and there is no meaningful action split.
- Every CLI tool must expose:
  - `--help` on the root command
  - `--version` on the root command
  - `--verbose` on the root command and on subcommands when flags are parsed per command
- Root `--help` output must list all available commands, key options, and usage examples. Command-specific help must describe that command's arguments and options.

#### CLI to library separation

- Structure the software as `cli -> lib`.
- The CLI layer must only parse arguments, load config, call the library, and format output.
- Domain logic must live in the library and be usable without CLI globals such as `argv`, `stdout`, or process exit handlers.
- Every feature available through the CLI must also be available through the library API.
- Organize the library by action so the mapping stays direct and obvious.
  - `extract` command -> `extract(...)`
  - `validate` command -> `validate(...)`
- Avoid one generic library `run()` entry point that hides action-specific contracts behind switches or string commands.

#### Library API shape

- Each CLI action should map to a dedicated exported API with typed inputs and outputs appropriate for the language.
- Library APIs should accept in-memory options objects or typed parameters, not require config files or environment variables unless library-level config-file support is an explicit requirement.
- The CLI layer is responsible for translating flags, positional arguments, and config-file contents into library inputs.
- The library should return explicit results and errors so the CLI can decide what to print and which exit code to use.

#### Configuration

- Prefer flags and positional arguments for simple inputs.
- When configuration becomes long, nested, or repetitive, support a config file instead of pushing all values into flags.
- By default, config-file discovery and loading must happen in the CLI layer, not in the library layer.
- When a config file is supported, the CLI should try to load a JSON config file from `[cwd]/.[cli-name]rc` by default.
- The CLI should also support an explicit config path flag such as `--config`.
- For JavaScript tools, `cosmiconfig` is an acceptable implementation. Equivalent discovery libraries are acceptable in other ecosystems.
- The library must not depend on the presence of the config file; it should receive parsed configuration values from the CLI layer.
- The library may load or parse config files only when that behavior is an explicit requirement of the library contract for non-CLI consumers as well.

#### Output and progress

- Standard output must show a start message when work begins and a result message when work completes successfully.
- When processing is long-running or multi-stage, print concise intermediate progress messages.
- `--verbose` must reveal more internal detail about what the tool is doing without changing the meaning of the command result.
- Default output should stay concise and readable for humans.
- Errors should be written to standard error with an actionable message. Stack traces or raw internal errors should stay hidden by default and may be shown in verbose mode.

#### Exit behavior

- Exit with `0` only when the requested action completed successfully.
- Exit with `1` when the requested action could not be completed.
- The library should surface failure as return values, result objects, or language-idiomatic errors; the CLI is responsible for converting that outcome into user-facing messages and process exit codes.

#### Documentation

- `README.md` must include at least 4 CLI usage examples.
- `README.md` must include at least 2 library API examples for the same operation also available through the CLI.
- If the tool supports config files, at least 1 README example should show config-file usage.
- Examples must use the public command and public library API, not internal modules or private files.

#### Distribution and versioning

- The implementation language is project-dependent, but the packaging and entry-point strategy must match how users are expected to run the tool.
- Choose language tooling that stays compatible with ecosystem launchers such as `npx`, `pnpm dlx`, `uvx`, or equivalent distribution commands for that ecosystem.
- `--version` must print the same version declared in the published package or release artifact metadata.
- Do not hard-code a second version string that can drift from the published package version.
- Language-specific project structure and packaging rules still apply and should be combined with this XDR, especially [agentme-edr-003](003-javascript-project-tooling.md), [agentme-edr-010](010-golang-project-tooling.md), and [agentme-edr-014](014-python-project-tooling.md).

## Considered Options

* (REJECTED) **Ad hoc CLIs with embedded business logic** - Keep parsing, processing, config loading, and output formatting inside a single entry point.
  * Reason: Makes the tool hard to test, hard to reuse as a library, and inconsistent across commands.
* (CHOSEN) **Thin CLI adapter over action-oriented library APIs** - Keep the CLI responsible for user interaction and the library responsible for the actual behavior.
  * Reason: Preserves a clean programmatic API, keeps command behavior discoverable, and makes the CLI-to-library mapping easy to maintain.

## References

- [agentme-edr-003](003-javascript-project-tooling.md) - JavaScript project packaging and structure
- [agentme-edr-007](../principles/007-project-quality-standards.md) - README and examples baseline
- [agentme-edr-008](../devops/008-common-targets.md) - Standard command names for project entry points
- [agentme-edr-009](../principles/009-error-handling.md) - Process error signaling and error handling expectations
- [agentme-edr-010](010-golang-project-tooling.md) - Go CLI structure and verbose logging baseline
- [agentme-edr-014](014-python-project-tooling.md) - Python packaging and CLI entry-point guidance
- [cosmiconfig](https://github.com/cosmiconfig/cosmiconfig) - Example JSON configuration discovery library for JavaScript CLIs