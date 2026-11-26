# review-gdpr scripts

TypeScript scripts behind the `review-gdpr` skill. They validate the GDPR applicability hub declared by [agentme-adr-policy-501](../../../../../adrs/governance/501-gdpr-applicability-and-declarations.md) and list candidate personal data locations for the LLM review described in [../SKILL.md](../SKILL.md). Zero runtime dependencies: Node.js built-ins only.

## Layout

Ad hoc flat layout per [agentme-edr-005](../../../../principles/005-skill-scripts-and-composition.md):

- `review-gdpr.ts` - process entry point (argv, stdout, stderr, exit code)
- `cli.ts` - option parsing, output formatting and exit codes
- `check.ts`, `hub.ts`, `dates.ts` - the `check` command, hub parsing with the single item list `ITEMS`, review date rules
- `discover.ts`, `files.ts`, `keywords.ts` - the `discover` command, file listing with `.gitignore` support, keyword and pattern tables
- `*.test.ts`, `testkit_mock.ts` - Jest tests and their synthetic fixture helpers

## Usage

```bash
npx -y tsx@4.23.15 scripts/review-gdpr.ts check
npx -y tsx@4.23.15 scripts/review-gdpr.ts check --dir ../my-app --json
npx -y tsx@4.23.15 scripts/review-gdpr.ts check --dir . --today 2026-11-23
npx -y tsx@4.23.15 scripts/review-gdpr.ts discover --dir ../my-app
npx -y tsx@4.23.15 scripts/review-gdpr.ts discover --dir ../my-app --json --out-id 20261123120000
npx -y tsx@4.23.15 scripts/review-gdpr.ts discover --dir ../my-app --keywords extra-keywords.json
```

### check

Offline and deterministic; suitable for CI. Finds `010-gdpr-applicability.md` under an `adrs/principles/` folder anywhere below `--dir` (skipping `node_modules`, `.git`, `.tmp`) and validates it against agentme-adr-policy-501: exactly one hub, opt-out or applicable form, every item with a resolving pointer or a reasoned `not-applicable` (only where allowed), review dates today to today + 12 months, and no other `gdpr` policy beside an opt-out. `http(s)` pointers are not fetched; they are counted as `info: <n> unverified external pointer(s)`.

| Option | Meaning |
|---|---|
| `--dir <path>` | Directory to search (default: current directory) |
| `--json` | Print `{ ok, mode, findings: [{ severity, file, line, message }], items, validUntil, externalPointers, expired }` |
| `--today YYYY-MM-DD` | Override today's date (testing) |

Human output is one `ERROR <file>[:line]: <message>` line per finding, then `check: <message>` per failure, or on success `check: hub found, <n> items resolved, <m> expired` (applicable) or `check: opted-out, valid until <date>`.

### discover

Read-only helper that feeds the LLM review. It lists candidates as `{ kind, name, file, line, value }` and writes them to `<dir>/.tmp/review-gdpr/<id>/discover.json`; nothing else is written. Without `--json` it prints a count summary and ends with `results-path: <path>`; with `--json` it prints the same JSON as the file.

| Kind | Source |
|---|---|
| `pii-field`, `special-category-field` | identifier names matching the keyword lists (English, Portuguese, Spanish, French, German) |
| `tracker-sdk`, `llm-sdk` | analytics, advertising, session replay and LLM SDK names or script hosts |
| `cloud-region` | region strings such as `eu-west-1`, and `region:` keys in config and IaC files |
| `log-statement` | log or print lines whose arguments reference a keyword |
| `data-file` | file name only: `.csv .tsv .ndjson .jsonl .dump .bak .log .sqlite .db`, `.env*`, json or yaml under `fixtures`, `data`, `samples`, `seeds`, `testdata` |
| `runbook-candidate`, `doc-candidate`, `hub` | file or path names (runbook, incident, breach, dsr, erasure, README, privacy, consent, cookie, gdpr, dpa, ropa, dpia) |
| `skipped` | unreadable or invalid UTF-8 files and files over 1 MB, with a `reason` |

Files come from `git ls-files --cached --others --exclude-standard` inside a git work tree, otherwise from a directory walk that honours the root `.gitignore` (comments, `dir/`, `/anchored`, `*`, `**`, `?`; negations are ignored). `node_modules`, `.git`, `.tmp`, `dist`, `build`, `coverage`, binary files and files over 1 MB are always skipped. Output is sorted and deterministic.

| Option | Meaning |
|---|---|
| `--dir <path>` | Directory to scan (default: current directory) |
| `--json` | Print the items and counts as JSON |
| `--keywords <file>` | JSON `{ "pii": [], "special": [] }` extending the default keywords |
| `--out-id <id>` | Run folder id, `[A-Za-z0-9._-]+` (default: local time `YYYYMMDDHHMMSS`) |

#### Redaction guarantee

Matched values are never printed or stored: `value` is always the literal `<redacted>`, and `name` is the matched keyword or SDK label, not the source text. Data files are listed by path and type only and are never opened. Markdown and text files and lock files are not scanned for content.

#### Extending keywords

Add words to a JSON file and pass it with `--keywords`. Multi-word keywords use `_`; matching ignores case, accents and separators, so `loyalty_card` also matches `loyaltyCard` and `Loyalty-Card`.

```json
{ "pii": ["loyalty_card", "matrikelnummer"], "special": ["blutgruppe"] }
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (`check` found no ERROR; `discover` completed) |
| 1 | `check` reported an ERROR, or a runtime failure such as an unwritable run folder |
| 2 | Usage error: unknown command or option, missing value, invalid `--today`, `--dir`, `--out-id` or keywords file |

## Application API

The CLI is a thin adapter over plain functions:

```ts
import { check } from './check';
import { discover, writeDiscover } from './discover';
import { DEFAULT_KEYWORDS } from './keywords';

const result = check({ dir: '../my-app', today: '2026-11-23' }); // { ok, findings, items, ... }
const found = discover({ dir: '../my-app', keywords: DEFAULT_KEYWORDS });
const resultsPath = writeDiscover('../my-app', 'run-1', found);
```

## Development

- `make lint` runs `tsc --noEmit` and ESLint with zero warnings
- `make test` runs Jest on synthetic fixtures with an 80% coverage floor. A test fails when `ITEMS` in `hub.ts` differs from the item table of agentme-adr-policy-501 rule 06
- `make clean` removes `node_modules` and caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the runtime sources into `dist/build/` and `dist/review-gdpr.zip`.
