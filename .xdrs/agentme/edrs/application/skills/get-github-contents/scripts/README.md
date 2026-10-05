# get-github-contents scripts

TypeScript scripts behind the `get-github-contents` skill. They wrap the `gh` CLI to read GitHub issues, pull request metadata and pull request comments. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - one entry point per command (parses `argv`, wires connectors, sets the exit code)
- `src/adapters/connectors/` - `gh/` runs the gh CLI, `http/` downloads attachments without following redirects off GitHub hosts, `local-fs/` writes files
- `src/app/` - command flows and pure helpers. Receive every dependency as an injected port
- `src/shared/` - constants and the `ExitError` type
- `*_mock.ts` - reusable in-memory world used by the tests

## Usage

```bash
npx -y tsx@4.23.15 src/adapters/cli/issue-get.ts --issue-url <url> [--download-dir <dir>] [--no-download]
npx -y tsx@4.23.15 src/adapters/cli/pr-metadata-get.ts --pr-url <url>
npx -y tsx@4.23.15 src/adapters/cli/pr-comments-list.ts --pr-url <url>
```

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the runtime sources.
