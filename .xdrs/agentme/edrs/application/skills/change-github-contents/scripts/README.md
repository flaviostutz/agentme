# change-github-contents scripts

TypeScript scripts behind the `change-github-contents` skill. They wrap the `gh` CLI to write pull request comments, resolve review threads and create or update issues, each idempotent and verified by read-back. See [../SKILL.md](../SKILL.md) for usage by agents.

## Layout

Follows [agentme-edr-126](../../../126-pragmatic-hexagonal-architecture.md) layering:

- `src/adapters/cli/` - one entry point per command (reads the items file, sets the exit code)
- `src/adapters/connectors/` - `gh` CLI and items-file connectors
- `src/app/` - handlers and pure helpers. Receive every dependency as an injected port
- `src/shared/` - the `ExitError` type
- `*_mock.ts` - reusable in-memory fake `gh` used by the tests

## Usage

Every command reads a JSON array of items from `--input <file>` or stdin and prints one result per item.

```bash
npx -y tsx@4.23.15 src/adapters/cli/pr-comment-create.ts --input items.json   # [{prUrl, body}]
npx -y tsx@4.23.15 src/adapters/cli/pr-comment-reply.ts --input items.json    # [{prUrl, commentId, body}]
npx -y tsx@4.23.15 src/adapters/cli/pr-thread-resolve.ts --input items.json   # [{prUrl, commentId}]
npx -y tsx@4.23.15 src/adapters/cli/issue-comment-create.ts --input items.json # [{issueUrl, body}]
npx -y tsx@4.23.15 src/adapters/cli/issue-update.ts --input items.json         # [{issueUrl, expectedUpdatedAt, title?, body?}]
npx -y tsx@4.23.15 src/adapters/cli/issue-create.ts --input items.json         # [{repoUrl, title, body}]
```

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest with an 80% coverage floor
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill together with `get-github-contents`.
