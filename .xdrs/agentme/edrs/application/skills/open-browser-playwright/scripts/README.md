# open-browser scripts

TypeScript scripts behind the `open-browser-playwright` skill. They open a visible Edge window on a copy of the user's signed-in profile, check the SSO user, and print a localhost CDP endpoint. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - the `open-browser.ts` entry point (parses `argv`, wires connectors, sets the exit code)
- `src/adapters/connectors/cdp/` - Edge process launch, CDP HTTP and WebSocket client
- `src/adapters/connectors/local-fs/` - profile copy and session state files
- `src/app/` - open, wait and tidy flows, pure argument parsing, SSO checks. Receive every dependency as an injected port
- `src/shared/` - constants and the `ExitError` type
- `*_mock.ts` - reusable in-memory world and fake WebSocket used by the tests

## Usage

```bash
npx -y tsx@4.23.15 src/adapters/cli/open-browser.ts <session> <url> [WIDTHxHEIGHT] [--cdp-port=N]
npx -y tsx@4.23.15 src/adapters/cli/open-browser.ts wait <session> <url> [seconds]
npx -y tsx@4.23.15 src/adapters/cli/open-browser.ts tidy <session>
```

Requires Node.js 22+ (global `WebSocket`) and Microsoft Edge.

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the runtime sources.
