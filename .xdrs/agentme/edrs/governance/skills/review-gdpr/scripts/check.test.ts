import * as fs from 'node:fs';
import path from 'node:path';

import { type CheckResult, check, formatCheck } from './check';
import { addMonths, isValidIsoDate, reviewDateStatus } from './dates';
import { ITEMS, parseBlocks } from './hub';
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

const run = (root: string, today = TODAY): CheckResult => check({ dir: root, today });
const messages = (result: CheckResult): string[] =>
  result.findings.map((finding) => finding.message);
const NA = (date: string): string[] => [
  'Status: not-applicable',
  'Reasoning: Art. 37(1) not met',
  'Owner: dpo-team',
  `Review-date: ${date}`,
];

describe('opt-out hub', () => {
  it('passes when complete', () => {
    const root = makeDir();
    writeHub(root, OPT_OUT);
    const result = run(root);
    expect(result).toMatchObject({ ok: true, mode: 'opted-out', validUntil: '2027-06-01' });
    expect(formatCheck(result)).toEqual(['check: opted-out, valid until 2027-06-01']);
  });

  it.each(['Reason', 'Inventory', 'Owner', 'Review-date'])('fails when %s is missing', (key) => {
    const root = makeDir();
    writeHub(
      root,
      OPT_OUT.split('\n')
        .filter((line) => !line.startsWith(`${key}:`))
        .join('\n'),
    );
    const result = run(root);
    expect(result.ok).toBe(false);
    expect(messages(result)).toContain(`hub opt-out requires ${key}`);
  });

  it('fails beside another gdpr policy of the same scope, ignoring skills folders', () => {
    const root = makeDir();
    writeHub(root, OPT_OUT);
    write(root, 'edrs/governance/skills/review-gdpr/SKILL.md');
    write(root, 'edrs/governance/skills/gdpr-notes/README.md');
    expect(run(root).ok).toBe(true);
    write(root, 'bdrs/ops/406-GDPR-workflow.md');
    const result = run(root);
    expect(result.ok).toBe(false);
    expect(result.findings[0]).toMatchObject({ file: 'bdrs/ops/406-GDPR-workflow.md' });
    expect(messages(result)[0]).toContain('must not coexist');
  });

  it('fails when it contains item blocks', () => {
    const root = makeDir();
    writeHub(root, `${OPT_OUT}\n#### 02-retention\n\nStatus: pointer\n`);
    const result = run(root);
    expect(messages(result)).toEqual([
      'hub opt-out must not contain item entries (found "retention")',
    ]);
    expect(result.findings[0]?.line).toBe(11);
  });

  it('fails when the review date is expired or too far ahead', () => {
    const root = makeDir();
    writeHub(root, OPT_OUT.replace('2027-06-01', '2026-11-22'));
    const expired = run(root);
    expect(messages(expired)[0]).toContain('is expired');
    expect(expired.expired).toBe(1);
    writeHub(root, OPT_OUT.replace('2027-06-01', '2028-01-01'));
    expect(messages(run(root))[0]).toContain('more than 12 months ahead');
    writeHub(root, OPT_OUT.replace('2027-06-01', '2027-02-30'));
    expect(messages(run(root))[0]).toContain('not a valid YYYY-MM-DD date');
  });
});

describe('applicable hub', () => {
  it('passes when every item resolves', () => {
    const root = makeDir();
    writeHub(root, applicableHub());
    const result = run(root);
    expect(result).toMatchObject({ ok: true, mode: 'applicable' });
    expect(result.items).toHaveLength(8);
    expect(formatCheck(result)).toEqual(['check: hub found, 8 items resolved, 0 expired']);
  });

  it('passes a processor role and a reasoned dpo not-applicable', () => {
    const root = makeDir();
    writeHub(
      root,
      applicableHub({
        roles: ['Role: processor', 'Status: pointer', 'Pointer: ./pointer.md'],
        dpo: NA('2027-01-10'),
      }),
    );
    const result = run(root);
    expect(result.ok).toBe(true);
    expect(result.items.find((item) => item.id === 'dpo')).toMatchObject({
      status: 'not-applicable',
      resolved: true,
    });
  });

  it('fails not-applicable on retention', () => {
    const root = makeDir();
    writeHub(root, applicableHub({ retention: NA('2027-01-10') }));
    expect(messages(run(root))).toEqual(['hub item "retention" cannot be not-applicable']);
  });

  it('fails not-applicable without reasoning, owner or date', () => {
    const root = makeDir();
    writeHub(root, applicableHub({ dpo: ['Status: not-applicable'] }));
    expect(messages(run(root))).toEqual([
      'hub item "dpo" requires Reasoning',
      'hub item "dpo" requires Owner',
      'hub item "dpo" requires Review-date',
    ]);
  });

  it.each([
    ['exactly today', TODAY, true],
    ['exactly today + 12 months', '2027-11-23', true],
    ['today + 12 months + 1 day', '2027-11-24', false],
    ['yesterday', '2026-11-22', false],
  ])('review date %s', (_name, date, ok) => {
    const root = makeDir();
    writeHub(root, applicableHub({ ropa: NA(date) }));
    expect(run(root).ok).toBe(ok);
  });

  it('counts expired not-applicable entries', () => {
    const root = makeDir();
    writeHub(root, applicableHub({ dpia: NA('2025-01-01') }));
    const result = run(root);
    expect(result.expired).toBe(1);
    expect(formatCheck(result)).toEqual([
      expect.stringMatching(
        /^ERROR adrs\/principles\/010-gdpr-applicability\.md:\d+: hub item "dpia" Review-date 2025-01-01 is expired/u,
      ),
      expect.stringMatching(/^check: hub item "dpia" Review-date/u),
    ]);
  });

  it('fails a pointer to a missing file or an empty file', () => {
    const root = makeDir();
    const hub = writeHub(
      root,
      applicableHub({
        retention: ['Status: pointer', 'Pointer: ./missing.md'],
        ropa: ['Status: pointer', 'Pointer: ./empty.md'],
      }),
    );
    write(path.dirname(hub), 'empty.md', '  \n');
    expect(messages(run(root))).toEqual([
      'hub item "ropa" pointer target "./empty.md" is empty',
      'hub item "retention" pointer target "./missing.md" does not exist',
    ]);
  });

  it('resolves markdown links, anchors and directories and rejects empty directories', () => {
    const root = makeDir();
    const hub = writeHub(
      root,
      applicableHub({
        retention: ['Status: pointer', 'Pointer: [Retention](./pointer.md#section "title")'],
        ropa: ['Status: pointer', 'Pointer: ./registers/'],
        dpia: ['Status: pointer', 'Pointer: ./void/'],
        dpo: ['Status: pointer', 'Pointer: #only-anchor'],
        'processors-and-transfers': ['Status: pointer', 'Pointer: /etc/hosts'],
      }),
    );
    write(path.dirname(hub), 'registers/ropa.md', 'record');
    fs.mkdirSync(path.join(path.dirname(hub), 'void'));
    expect(messages(run(root))).toEqual([
      'hub item "dpo" pointer has no file path',
      'hub item "dpia" pointer target "./void/" is empty',
      'hub item "processors-and-transfers" pointer "/etc/hosts" must be a relative path or an http(s) URL',
    ]);
  });

  it('accepts URL pointers without fetching and counts them', () => {
    const root = makeDir();
    writeHub(
      root,
      applicableHub({
        dpo: ['Status: pointer', 'Pointer: https://example.org/dpo'],
        ropa: ['Status: pointer', 'Pointer: [r](http://example.org/r)'],
      }),
    );
    const result = run(root);
    expect(result).toMatchObject({ ok: true, externalPointers: 2 });
    expect(formatCheck(result)).toEqual([
      'info: 2 unverified external pointer(s)',
      'check: hub found, 8 items resolved, 0 expired',
    ]);
  });

  it('fails a missing item, a missing pointer and a missing status', () => {
    const root = makeDir();
    writeHub(
      root,
      applicableHub(
        {
          dpo: ['Status: pointer'],
          ropa: ['Pointer: ./pointer.md'],
          dpia: ['Status: maybe'],
          'processors-and-transfers': [],
        },
        ['retention'],
      ),
    );
    expect(messages(run(root))).toEqual([
      'hub item "dpo" requires Pointer',
      'hub item "ropa" has no Status',
      'hub item "dpia" has invalid Status "maybe" (expected pointer or not-applicable)',
      'hub item "processors-and-transfers" has no pointer or reason',
      'hub item "retention" has no pointer or reason',
    ]);
  });

  it('fails unknown and duplicated item ids and a repeated applicability entry', () => {
    const root = makeDir();
    writeHub(
      root,
      applicableHub({}, [], [{ id: 'unicorns' }, { id: 'retention' }, { id: 'applicability' }]),
    );
    expect(messages(run(root))).toEqual([
      'hub entry "unicorns" is not a known item id',
      'hub entry "retention" is declared more than once',
      'hub entry "applicability" is declared more than once',
    ]);
  });

  it('requires a valid Role on roles and the applicability fields', () => {
    const root = makeDir();
    writeHub(
      root,
      applicableHub({ roles: ['Role: owner', 'Status: pointer', 'Pointer: ./pointer.md'] }).replace(
        'Data-categories: personal, special category\n',
        '',
      ),
    );
    expect(messages(run(root))).toEqual([
      'hub applicability requires Data-categories',
      'hub item "roles" requires Role: controller, processor or joint',
    ]);
  });
});

describe('hub discovery and structure', () => {
  it('fails when the hub is missing, ignoring look-alikes in other folders and node_modules', () => {
    const root = makeDir();
    write(root, 'docs/010-gdpr-applicability.md', OPT_OUT);
    write(root, 'node_modules/pkg/adrs/principles/010-gdpr-applicability.md', OPT_OUT);
    const result = run(root);
    expect(result).toMatchObject({ ok: false, mode: 'missing' });
    expect(formatCheck(result)[0]).toMatch(/^ERROR \.: hub missing/u);
  });

  it('fails when two hubs exist', () => {
    const root = makeDir();
    writeHub(root, OPT_OUT);
    writeHub(root, OPT_OUT, '_local/adrs/principles/010-gdpr-applicability.md');
    const result = run(root);
    expect(result.mode).toBe('multiple');
    expect(messages(result)[0]).toContain('_local/adrs/principles/010-gdpr-applicability.md');
  });

  it('fails when the first entry is not applicability or its Status is invalid', () => {
    const root = makeDir();
    writeHub(root, '# Hub\n\n#### 01-retention\n\nStatus: pointer\n');
    expect(messages(run(root))).toEqual(['the first hub entry must be "applicability"']);
    writeHub(root, '# Hub with nothing\n');
    expect(messages(run(root))).toEqual(['the first hub entry must be "applicability"']);
    writeHub(root, '#### 01-applicability\n\nStatus: maybe\n');
    expect(messages(run(root))).toEqual([
      'hub applicability Status must be applicable or opted-out',
    ]);
  });
});

describe('parseBlocks and dates', () => {
  it('reads key lines up to the next heading, with CRLF and first key wins', () => {
    const blocks = parseBlocks(
      '#### 01-applicability\r\nStatus: opted-out\r\nStatus: other\r\nnot a key\r\n## Section\r\nOwner: ignored\r\n#### 02-dpo\r\nPointer:\r\n',
    );
    expect(blocks.map((block) => block.id)).toEqual(['applicability', 'dpo']);
    expect(blocks[0]?.fields).toEqual({ Status: { value: 'opted-out', line: 2 } });
    expect(blocks[1]?.fields['Pointer']?.value).toBe('');
  });

  it('adds calendar months with day clamping', () => {
    expect(addMonths('2028-02-29', 12)).toBe('2029-02-28');
    expect(addMonths('2026-11-23', 12)).toBe('2027-11-23');
    expect(addMonths('2026-12-31', 2)).toBe('2027-02-28');
    expect(isValidIsoDate('2026-13-01')).toBe(false);
    expect(isValidIsoDate('26-1-1')).toBe(false);
    expect(reviewDateStatus('2026-11-23', '2026-11-23')).toBe('ok');
  });
});

describe('item list', () => {
  it('equals the item table of agentme-adr-policy-501 rule 06', () => {
    const policy = path.resolve(
      __dirname,
      '../../../../../adrs/governance/501-gdpr-applicability-and-declarations.md',
    );
    const text = fs.readFileSync(policy, 'utf8');
    const section = text.slice(text.indexOf('#### 06-applicable-form'), text.indexOf('#### 07-'));
    const rows = [...section.matchAll(/^\|\s*`([^`]+)`\s*\|[^|]*\|\s*(Yes|No)\b[^|]*\|\s*$/gmu)];
    const documented = rows.map((row) => ({ id: row[1], mayBeNotApplicable: row[2] === 'Yes' }));
    expect(documented.length).toBeGreaterThan(0);
    expect(ITEMS).toEqual(documented);
  });
});
