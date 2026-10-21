# get-web-search-contents scripts

Searches DuckDuckGo or Google through the browser opened by `open-browser-playwright` and prints ranked results plus the engine's AI summary as JSON. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - the `search` and `chat` entry points and their wiring (`deps.ts`)
- `src/adapters/connectors/playwright-cli/` - browser port over a pinned `@playwright/cli`, attached to the CDP port
- `src/adapters/connectors/fs/` - per-run search counter under `.tmp/get-web-search-contents/<run-id>/`
- `src/app/` - command flows, guards and pure helpers. Receive every dependency as an injected port. `scripts.ts` holds the functions that run inside the page, the part most likely to break when an engine changes its markup
- `src/shared/` - constants and the `ExitError` type
- `*_mock.ts` - reusable in-memory world used by the tests

## Usage

```bash
npx -y tsx@4.23.15 src/adapters/cli/search.ts --query <text> [--engine duckduckgo|google] [--google-confirmed] [--run-id <id>] [--max-searches <1-30>] [--lang <xx>] [--region <XX>] [--session <name>] [--cdp-port <port>]
npx -y tsx@4.23.15 src/adapters/cli/chat.ts --prompt <text> --google-confirmed [--new-thread] [--close] [same shared flags]
```

Exit codes: 0 success (check `status`), 1 runtime failure, 2 usage error or refused query.

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor; tests use jsdom with synthetic fixtures only, never captured pages
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the runtime sources.
