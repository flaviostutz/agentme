import { execFileSync } from 'node:child_process';
import * as fs from 'node:fs';
import path from 'node:path';

import {
  type DiscoverItem,
  type DiscoverResult,
  MAX_FILE_BYTES,
  REDACTED,
  discover,
  writeDiscover,
} from './discover';
import { DEFAULT_KEYWORDS, createMatcher, loadKeywords, splitWords } from './keywords';
import { makeDir, removeDirs, write } from './testkit_mock';

afterEach(removeDirs);

const EMAIL = 'jane.doe@example.com';
const SSN = '123-45-6789';

const scan = (root: string): DiscoverResult => discover({ dir: root, keywords: DEFAULT_KEYWORDS });
const find = (result: DiscoverResult, kind: string, name?: string): DiscoverItem[] =>
  result.items.filter(
    (entry) => entry.kind === kind && (name === undefined || entry.name === name),
  );
const walkAll = (root: string): string[] =>
  fs
    .readdirSync(root, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => path.relative(root, path.join(entry.parentPath, entry.name)))
    .sort();

describe('candidate detection', () => {
  it('finds personal and special category fields in several languages', () => {
    const root = makeDir();
    write(
      root,
      'src/model.ts',
      'const row = { geburtsdatum: 1, nome: 2, Prénom: 3, birthDate: 4, emails: 5, healthCheck: 6 };\nconst diagnosis = 1;\nconst sexual_orientation = 2;\n',
    );
    const result = scan(root);
    expect(find(result, 'pii-field').map((entry) => entry.name)).toEqual([
      'birth_date',
      'email',
      'geburtsdatum',
      'nome',
      'prenom',
    ]);
    expect(find(result, 'special-category-field').map((entry) => [entry.name, entry.line])).toEqual(
      [
        ['diagnosis', 2],
        ['sexual_orientation', 3],
      ],
    );
    expect(result.items.every((entry) => entry.value === REDACTED)).toBe(true);
  });

  it('detects trackers, LLM SDKs, regions and log statements', () => {
    const root = makeDir();
    write(
      root,
      'web/index.html',
      '<script src="https://www.googletagmanager.com/gtag/js"></script>\n<script>fbq(\'init\')</script>\n',
    );
    write(
      root,
      'app.ts',
      "import OpenAI from 'openai';\nimport { replayIntegration } from '@sentry/browser';\nconsole.log(`user ${user.email}`);\nlogger.info('started');\nconst r = 'eu-west-1';\n",
    );
    write(root, 'infra/main.tf', 'provider "aws" {\n  region = "us-east-1"\n}\n');
    write(root, 'src/types.ts', 'type Opts = { region: string };\n');
    const result = scan(root);
    expect(find(result, 'tracker-sdk').map((entry) => entry.name)).toEqual(
      expect.arrayContaining(['google-analytics', 'facebook-pixel', 'sentry-session-replay']),
    );
    expect(find(result, 'llm-sdk', 'openai')).toHaveLength(1);
    expect(find(result, 'cloud-region').map((entry) => `${entry.file}:${entry.name}`)).toEqual([
      'app.ts:eu-west-1',
      'infra/main.tf:region',
      'infra/main.tf:us-east-1',
    ]);
    expect(find(result, 'log-statement')).toEqual([
      expect.objectContaining({ file: 'app.ts', line: 3, name: 'email' }),
    ]);
  });

  it('classifies paths: hub, runbooks, docs and data files', () => {
    const root = makeDir();
    write(root, 'adrs/principles/010-gdpr-applicability.md');
    write(root, 'docs/runbooks/breach-response.md');
    write(root, 'docs/Data-Subject-Requests.md');
    write(root, 'README.md');
    write(root, 'legal/privacy-policy.pdf', 'binary-ish');
    write(root, 'src/consent.ts');
    const result = scan(root);
    expect(find(result, 'hub').map((entry) => entry.file)).toEqual([
      'adrs/principles/010-gdpr-applicability.md',
    ]);
    expect(find(result, 'runbook-candidate').map((entry) => `${entry.file}:${entry.name}`)).toEqual(
      ['docs/Data-Subject-Requests.md:data-subject', 'docs/runbooks/breach-response.md:runbooks'],
    );
    expect(find(result, 'doc-candidate').map((entry) => entry.file)).toEqual([
      'README.md',
      'legal/privacy-policy.pdf',
    ]);
  });

  it('extends keywords from a file and rejects invalid ones', () => {
    const root = makeDir();
    write(root, 'a.ts', 'const loyaltyCard = 1;\nconst blutgruppe = 2;\n');
    const file = write(
      makeDir(),
      'kw.json',
      JSON.stringify({ pii: ['loyalty_card'], special: ['blutgruppe'] }),
    );
    const result = discover({ dir: root, keywords: loadKeywords(file) });
    expect(find(result, 'pii-field', 'loyalty_card')).toHaveLength(1);
    expect(find(result, 'special-category-field', 'blutgruppe')).toHaveLength(1);
    expect(loadKeywords(undefined)).toBe(DEFAULT_KEYWORDS);
    expect(loadKeywords(write(root, 'empty.json', '{}')).pii).toEqual(DEFAULT_KEYWORDS.pii);
    expect(() => loadKeywords(write(root, 'bad1.json', '[]'))).toThrow('JSON object');
    expect(() => loadKeywords(write(root, 'bad2.json', '{"pii":[1]}'))).toThrow('array of strings');
    expect(() => loadKeywords(path.join(root, 'nope.json'))).toThrow('cannot be read');
  });

  it('splits identifiers into words', () => {
    expect(splitWords('IPAddress')).toEqual(['ip', 'address']);
    expect(splitWords('user_birthDate-1')).toEqual(['user', 'birth', 'date', '1']);
    expect(createMatcher(DEFAULT_KEYWORDS).pii('x = date_of_birth')).toEqual(['date_of_birth']);
    expect(createMatcher(DEFAULT_KEYWORDS).special('GET /health')).toEqual(['health']);
    expect(createMatcher(DEFAULT_KEYWORDS).special('GET /health_check')).toEqual([]);
  });
});

describe('redaction and data files', () => {
  it('never prints or stores matched values', () => {
    const root = makeDir();
    write(
      root,
      'src/user.ts',
      `const user = { email: '${EMAIL}', ssn: '${SSN}' };\nconsole.log('${EMAIL}', user.ssn);\n`,
    );
    write(root, 'data/people.json', `{"email":"${EMAIL}"}`);
    const result = scan(root);
    const resultsPath = writeDiscover(root, 'run1', result);
    const stored = fs.readFileSync(resultsPath, 'utf8');
    for (const output of [JSON.stringify(result), stored]) {
      expect(output).not.toContain(EMAIL);
      expect(output).not.toContain('jane.doe');
      expect(output).not.toContain(SSN);
    }
    expect(find(result, 'pii-field', 'ssn')).toHaveLength(2);
  });

  it('lists data files by path and type without reading them', () => {
    const root = makeDir();
    write(root, 'customers.csv', `email,ssn\n${EMAIL},${SSN}\n`);
    write(root, '.env.production', 'API_EMAIL=x\n');
    write(root, 'tests/fixtures/users.yaml', 'email: a\n');
    write(root, 'config/settings.json', '{"email": 1}');
    write(root, 'big.sqlite', Buffer.alloc(MAX_FILE_BYTES + 10));
    const result = scan(root);
    expect(find(result, 'data-file').map((entry) => [entry.file, entry.name, entry.line])).toEqual([
      ['.env.production', 'env', 0],
      ['big.sqlite', 'sqlite', 0],
      ['customers.csv', 'csv', 0],
      ['tests/fixtures/users.yaml', 'yaml', 0],
    ]);
    expect(
      result.items.filter((entry) => entry.kind !== 'data-file').map((entry) => entry.file),
    ).toEqual(['config/settings.json']);
  });
});

describe('file selection', () => {
  const populate = (root: string): void => {
    write(root, 'node_modules/lib/index.ts', 'const email = 1;\n');
    write(root, 'dist/out.ts', 'const email = 1;\n');
    write(root, 'build/out.ts', 'const email = 1;\n');
    write(root, 'coverage/out.ts', 'const email = 1;\n');
    write(root, '.tmp/old/discover.ts', 'const email = 1;\n');
    write(root, 'ignored/secret.ts', 'const email = 1;\n');
    write(root, 'plain.secret.ts', 'const email = 1;\n');
    write(root, 'logs/app.ts', 'const email = 1;\n');
    write(root, 'kept.ts', 'const email = 1;\n');
    write(root, 'nested/gen/auto.ts', 'const email = 1;\n');
    write(root, 'nested/keep.ts', 'const email = 1;\n');
    write(root, 'image.png', Buffer.from([0, 1, 2]));
    write(
      root,
      'blob.bin',
      Buffer.concat([Buffer.from('email'), Buffer.from([0]), Buffer.from('email')]),
    );
    write(root, 'package-lock.json', '{"openai": 1}');
    write(root, 'notes.md', 'email phone address\n');
    write(root, 'huge.ts', `${'const email = 1;\n'.repeat(Math.ceil(MAX_FILE_BYTES / 16) + 10)}`);
    write(root, 'minified.js', `var a="${'x'.repeat(2500)}";var email=1;\n`);
    write(root, '.gitignore', '# comment\nignored/\n*.secret.ts\n!kept.ts\n/logs\n**/gen/*.ts\n');
  };
  const files = (result: DiscoverResult): string[] => [
    ...new Set(result.items.map((entry) => entry.file)),
  ];

  it('skips build dirs, binaries, oversized files and honours .gitignore without git', () => {
    const root = makeDir();
    populate(root);
    const result = scan(root);
    expect(files(result)).toEqual(['huge.ts', 'kept.ts', 'nested/keep.ts']);
    expect(find(result, 'skipped')).toEqual([
      expect.objectContaining({
        file: 'huge.ts',
        reason: 'file larger than 1 MB',
        value: REDACTED,
      }),
    ]);
  });

  it('honours .gitignore through git, including untracked files', () => {
    const root = makeDir();
    populate(root);
    execFileSync('git', ['init', '-q'], { cwd: root });
    execFileSync('git', ['add', '.gitignore', 'kept.ts'], { cwd: root });
    const result = scan(root);
    expect(files(result)).toEqual(['huge.ts', 'kept.ts', 'nested/keep.ts']);
  });

  it('records invalid UTF-8 and unreadable files as skipped and continues', () => {
    const root = makeDir();
    write(root, 'a-bad.ts', Buffer.from([99, 255, 254, 65]));
    fs.symlinkSync(path.join(root, 'missing-target'), path.join(root, 'b-broken.ts'));
    write(root, 'c-good.ts', 'const email = 1;\n');
    const result = scan(root);
    expect(find(result, 'skipped').map((entry) => [entry.file, entry.reason])).toEqual([
      ['a-bad.ts', 'invalid UTF-8'],
      ['b-broken.ts', 'unreadable'],
    ]);
    expect(find(result, 'pii-field', 'email')).toHaveLength(1);
  });

  it('is deterministic and writes only under .tmp/review-gdpr/<id>/', () => {
    const root = makeDir();
    populate(root);
    const before = walkAll(root);
    const first = scan(root);
    const resultsPath = writeDiscover(root, '20261123120000', first);
    const after = walkAll(root);
    expect(after.filter((file) => !before.includes(file))).toEqual([
      '.tmp/review-gdpr/20261123120000/discover.json',
    ]);
    expect(resultsPath).toBe(path.join(root, '.tmp/review-gdpr/20261123120000/discover.json'));
    expect(before.every((file) => after.includes(file))).toBe(true);
    expect(scan(root)).toEqual(first);
    expect(JSON.parse(fs.readFileSync(resultsPath, 'utf8'))).toEqual(first);
    const fileOrder = first.items.map((entry) => entry.file);
    expect(fileOrder).toEqual([...fileOrder].sort());
  });
});
