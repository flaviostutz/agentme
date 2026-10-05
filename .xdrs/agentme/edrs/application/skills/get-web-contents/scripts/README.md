# get-web-contents scripts

Reads one web page over HTTP and prints readable text, links and a status as JSON. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - one entry point per command (parses `argv`, wires connectors, sets the exit code)
- `src/adapters/connectors/` - HTTP and DNS connectors (credential-less, no automatic redirects)
- `src/app/` - command flows and pure helpers. Receive every dependency as an injected port
- `src/shared/` - constants and the `ExitError` type
- `*_mock.ts` - reusable in-memory world used by the tests

## Usage

```bash
npx -y tsx@4.23.15 src/adapters/cli/page-get.ts --url <url> [--allow-private]
```

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the runtime sources.
