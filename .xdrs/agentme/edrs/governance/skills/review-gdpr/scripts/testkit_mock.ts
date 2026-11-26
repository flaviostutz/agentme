import * as fs from 'node:fs';
import * as os from 'node:os';
import path from 'node:path';

const created: string[] = [];

export const makeDir = (): string => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'review-gdpr-'));
  created.push(dir);
  return dir;
};

export const removeDirs = (): void => {
  for (const dir of created.splice(0)) fs.rmSync(dir, { recursive: true, force: true });
};

export const write = (
  root: string,
  relative: string,
  content: string | Uint8Array = 'content\n',
): string => {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content);
  return target;
};

export const HUB_PATH = 'adrs/principles/010-gdpr-applicability.md';
export const TODAY = '2026-11-23';

export const OPT_OUT = `# 010 GDPR applicability

#### 01-applicability

Status: opted-out
Reason: The tool processes no personal data.
Inventory: Reviewed the config store, logs and integrations; none hold personal data.
Owner: platform-team
Review-date: 2027-06-01
`;

type ItemSpec = { readonly id: string; readonly lines?: readonly string[] };

const DEFAULT_ITEMS = [
  'roles',
  'dpo',
  'ropa',
  'dpia',
  'processors-and-transfers',
  'retention',
  'lawful-bases-and-consents',
  'dsr-and-breach-runbooks',
];

export const itemBlock = (index: number, spec: ItemSpec): string => {
  const lines = spec.lines ?? ['Status: pointer', 'Pointer: [doc](./pointer.md)'];
  const role =
    spec.id === 'roles' && !lines.some((line) => line.startsWith('Role:'))
      ? ['Role: controller']
      : [];
  return [
    `#### ${String(index).padStart(2, '0')}-${spec.id}`,
    '',
    `Explanation: ${spec.id} explained`,
    ...role,
    ...lines,
    '',
  ].join('\n');
};

export const applicableHub = (
  overrides: Readonly<Record<string, readonly string[]>> = {},
  omit: readonly string[] = [],
  extra: readonly ItemSpec[] = [],
): string => {
  const head = [
    '# 010 GDPR applicability',
    '',
    '#### 01-applicability',
    '',
    'Status: applicable',
    'Data-categories: personal, special category',
    'Explanation: Customer accounts hold personal data.',
    '',
  ].join('\n');
  const specs: ItemSpec[] = [
    ...DEFAULT_ITEMS.filter((id) => !omit.includes(id)).map((id) => ({ id, lines: overrides[id] })),
    ...extra,
  ];
  return `${head}\n${specs.map((spec, index) => itemBlock(index + 2, spec)).join('\n')}`;
};

// Writes a hub plus a non-empty pointer target next to it.
export const writeHub = (root: string, text: string, relative = HUB_PATH): string => {
  const hub = write(root, relative, text);
  write(path.dirname(hub), 'pointer.md', '# Pointer target\n\nReal content.\n');
  return hub;
};
