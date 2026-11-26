import * as fs from 'node:fs';
import path from 'node:path';

import { type Io, run } from './cli';
import {
  OPT_OUT,
  TODAY,
  applicableHub,
  makeDir,
  removeDirs,
  write,
  writeHub,
} from './testkit_mock';

afterEach(removeDirs);

const invoke = (
  args: readonly string[],
  cwd: string,
): { code: number; out: string; err: string } => {
  const captured = { out: '', err: '' };
  const io: Io = { out: (text) => (captured.out += text), err: (text) => (captured.err += text) };
  const code = run(args, io, cwd, new Date(2026, 10, 23, 9, 8, 7));
  return { code, ...captured };
};

describe('usage', () => {
  it.each([
    [[], 'a command is required'],
    [['explode'], 'unknown command: explode'],
    [['check', '--bogus'], 'unknown option for check: --bogus'],
    [['check', 'stray'], 'unknown option for check: stray'],
    [['check', '--dir'], 'option --dir needs a value'],
    [['check', '--dir', '--json'], 'option --dir needs a value'],
    [['check', '--today', '2026-02-30'], '--today must be a valid'],
    [['check', '--dir', 'does-not-exist'], '--dir is not a directory'],
    [['discover', '--today', TODAY], 'unknown option for discover: --today'],
    [['discover', '--out-id', '../escape'], '--out-id must match'],
    [['discover', '--out-id', '..'], '--out-id must match'],
    [['discover', '--keywords', 'missing.json'], 'keywords file cannot be read'],
  ])('exits 2 for %j', (args, message) => {
    const result = invoke(args, makeDir());
    expect(result.code).toBe(2);
    expect(result.err).toContain(message);
    expect(result.err).toContain('Usage:');
  });

  it('prints help with exit 0', () => {
    const result = invoke(['--help'], makeDir());
    expect(result).toMatchObject({ code: 0, err: '' });
    expect(result.out).toContain('check');
    expect(result.out).toContain('discover');
  });
});

describe('check command', () => {
  it('exits 0 and prints the opt-out summary', () => {
    const root = makeDir();
    writeHub(root, OPT_OUT);
    expect(invoke(['check', '--today', TODAY], root)).toEqual({
      code: 0,
      out: 'check: opted-out, valid until 2027-06-01\n',
      err: '',
    });
  });

  it('uses the current date, a relative --dir and the inline option form', () => {
    const root = makeDir();
    writeHub(
      root,
      OPT_OUT.replace('2027-06-01', '2026-11-22'),
      'app/adrs/principles/010-gdpr-applicability.md',
    );
    const result = invoke(['check', '--dir=app'], root);
    expect(result.code).toBe(1);
    expect(result.out).toContain('ERROR adrs/principles/010-gdpr-applicability.md:');
  });

  it('exits 1 and prints one line per failure', () => {
    const root = makeDir();
    writeHub(root, applicableHub({}, ['retention']));
    const result = invoke(['check', '--today', TODAY], root);
    expect(result.code).toBe(1);
    expect(result.out).toBe(
      'ERROR adrs/principles/010-gdpr-applicability.md: hub item "retention" has no pointer or reason\ncheck: hub item "retention" has no pointer or reason\n',
    );
  });

  it('prints the JSON shape', () => {
    const root = makeDir();
    writeHub(root, applicableHub());
    const ok = invoke(['check', '--json', '--today', TODAY], root);
    expect(ok.code).toBe(0);
    expect(JSON.parse(ok.out)).toMatchObject({
      ok: true,
      findings: [],
      items: expect.arrayContaining([{ id: 'dpo', status: 'pointer', resolved: true }]),
    });
    const failing = invoke(['check', '--json'], makeDir());
    expect(failing.code).toBe(1);
    expect(JSON.parse(failing.out)).toEqual(
      expect.objectContaining({
        ok: false,
        findings: [
          {
            severity: 'ERROR',
            file: '.',
            line: null,
            message: expect.stringContaining('hub missing'),
          },
        ],
        items: [],
      }),
    );
  });
});

describe('discover command', () => {
  it('prints counts and ends with results-path', () => {
    const root = makeDir();
    write(root, 'src/a.ts', 'const email = 1;\n');
    const result = invoke(['discover', '--out-id', 'run42'], root);
    expect(result.code).toBe(0);
    const lines = result.out.trimEnd().split('\n');
    expect(lines[0]).toBe('discover: 1 candidates in 1 files');
    expect(lines[1]).toBe('  pii-field: 1');
    const resultsPath = path.join(root, '.tmp/review-gdpr/run42/discover.json');
    expect(lines.at(-1)).toBe(`results-path: ${resultsPath}`);
    expect(fs.existsSync(resultsPath)).toBe(true);
  });

  it('prints JSON, still writes the file and defaults the id to a timestamp', () => {
    const root = makeDir();
    write(root, 'src/a.ts', 'const email = 1;\n');
    const result = invoke(['discover', '--json'], root);
    expect(JSON.parse(result.out)).toEqual({
      items: [{ kind: 'pii-field', name: 'email', file: 'src/a.ts', line: 1, value: '<redacted>' }],
      counts: { 'pii-field': 1 },
      filesListed: 1,
    });
    expect(fs.existsSync(path.join(root, '.tmp/review-gdpr/20261123090807/discover.json'))).toBe(
      true,
    );
  });

  it('extends keywords from --keywords', () => {
    const root = makeDir();
    write(root, 'src/a.ts', 'const loyaltyCard = 1;\n');
    const keywords = write(makeDir(), 'kw.json', '{"pii":["loyalty_card"]}');
    const result = invoke(['discover', '--json', '--keywords', keywords, '--out-id', 'k'], root);
    expect(JSON.parse(result.out).counts).toEqual({ 'pii-field': 1 });
  });

  it('exits 1 on runtime failures', () => {
    const root = makeDir();
    write(root, '.tmp', 'a file where the run folder should go');
    const result = invoke(['discover', '--out-id', 'x'], root);
    expect(result.code).toBe(1);
    expect(result.err).toMatch(/^Error: /u);
  });
});
