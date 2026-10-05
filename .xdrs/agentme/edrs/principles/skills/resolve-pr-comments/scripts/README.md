# resolve-pr-comments scripts

Node.js script (no dependencies) behind the `resolve-pr-comments` skill. `update-section.js` reads and updates the tracking file (`.tmp/review-pr-<N>.md`) by stable section id; see the header comment of the script for the commands. See [../SKILL.md](../SKILL.md) for usage by agents.

## Development

- `make lint` runs ESLint through `npx` with a pinned version
- `make test` runs the unit tests with an 80% coverage floor
- `make clean` removes caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill together with the contents skills it activates.
