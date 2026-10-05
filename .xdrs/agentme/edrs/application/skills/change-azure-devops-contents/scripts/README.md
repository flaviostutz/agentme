# change-azure-devops-contents scripts

TypeScript scripts behind the `change-azure-devops-contents` skill. They wrap `az rest` to write pull request threads and to comment on, update and create work items, each idempotent and verified by read-back. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - one entry point per command (reads the items file, sets the exit code)
- `src/adapters/connectors/` - `az` CLI, items-file, temp body file and `pandoc` connectors
- `src/app/` - handlers and pure helpers. Receive every dependency as an injected port
- `src/shared/` - the `ExitError` type
- `*_mock.ts` - reusable in-memory fake `az` used by the tests

## Usage

Every command reads a JSON array of items from `--input <file>` or stdin and prints one result per item.

```bash
npx -y tsx@4.23.15 src/adapters/cli/pr-comment-create.ts --input items.json   # [{prUrl, body}]
npx -y tsx@4.23.15 src/adapters/cli/pr-comment-reply.ts --input items.json   # [{prUrl, commentId, body}]
npx -y tsx@4.23.15 src/adapters/cli/pr-thread-status-set.ts --input items.json   # [{prUrl, commentId, status}]
npx -y tsx@4.23.15 src/adapters/cli/work-item-comment-create.ts --input items.json   # [{workItemUrl, body}]
npx -y tsx@4.23.15 src/adapters/cli/work-item-update.ts --input items.json   # [{workItemUrl, expectedRev, title?, body?, bodyField?}]
npx -y tsx@4.23.15 src/adapters/cli/work-item-create.ts --input items.json   # [{workItemUrl, type, title, body, areaPath?, iterationPath?}]
```

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill together with `get-azure-devops-contents`.
