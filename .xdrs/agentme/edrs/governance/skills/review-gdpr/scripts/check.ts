import * as fs from 'node:fs';
import path from 'node:path';

import { reviewDateStatus } from './dates';
import { APPLICABILITY_ID, type Block, type HubItem, ITEMS, fieldValue, parseBlocks } from './hub';

export const HUB_FILE_NAME = '010-gdpr-applicability.md';
const SKIPPED_DIRS = new Set(['node_modules', '.git', '.tmp']);
const POLICY_DIRS = ['adrs', 'bdrs', 'edrs'];
const ROLES = new Set(['controller', 'processor', 'joint']);
const ITEM_STATUSES = new Set(['pointer', 'not-applicable']);
const MARKDOWN_LINK = /\[[^\]]*\]\(\s*<?([^\s)>]+)>?(?:\s+"[^"]*")?\s*\)/u;
const URL_POINTER = /^https?:\/\//iu;

export type Severity = 'ERROR' | 'WARNING';
export type Finding = {
  readonly severity: Severity;
  readonly file: string;
  readonly line: number | null;
  readonly message: string;
};
export type ItemResult = {
  readonly id: string;
  readonly status: string | null;
  readonly resolved: boolean;
};
export type CheckMode = 'missing' | 'multiple' | 'opted-out' | 'applicable' | 'invalid';
export type CheckResult = {
  readonly ok: boolean;
  readonly mode: CheckMode;
  readonly findings: Finding[];
  readonly items: ItemResult[];
  readonly validUntil: string | null;
  readonly externalPointers: number;
  readonly expired: number;
};
export type CheckOptions = { readonly dir: string; readonly today: string };

const toPosix = (value: string): string => value.split(path.sep).join('/');

const listEntries = (dir: string): fs.Dirent[] => {
  try {
    return fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
};

const walkFiles = (
  root: string,
  accept: (file: string, dirs: readonly string[]) => boolean,
): string[] => {
  const found: string[] = [];
  const visit = (dir: string, dirs: readonly string[]): void => {
    for (const entry of listEntries(dir)) {
      if (entry.isDirectory()) {
        if (!SKIPPED_DIRS.has(entry.name)) visit(path.join(dir, entry.name), [...dirs, entry.name]);
      } else if (accept(path.join(dir, entry.name), dirs)) {
        found.push(path.join(dir, entry.name));
      }
    }
  };
  visit(root, []);
  return found.sort();
};

const isHubPath = (file: string): boolean =>
  path.basename(file) === HUB_FILE_NAME &&
  path.basename(path.dirname(file)) === 'principles' &&
  path.basename(path.dirname(path.dirname(file))) === 'adrs';

export const findHubs = (dir: string): string[] => walkFiles(dir, isHubPath);

// Policy files named *gdpr* in the hub scope, excluding skills and the hub itself.
const findGdprPolicies = (hub: string): string[] => {
  const scopeRoot = path.dirname(path.dirname(path.dirname(hub)));
  return POLICY_DIRS.flatMap((policyDir) =>
    walkFiles(
      path.join(scopeRoot, policyDir),
      (file, dirs) =>
        path.basename(file).toLowerCase().includes('gdpr') && !dirs.includes('skills'),
    ),
  ).filter((file) => file !== hub);
};

type Context = {
  readonly file: string;
  readonly hubDir: string;
  readonly today: string;
  readonly findings: Finding[];
  readonly counters: { external: number; expired: number };
};

const addError = (
  context: Context,
  line: number | null,
  message: string,
  file = context.file,
): void => {
  context.findings.push({ severity: 'ERROR', file, line, message });
};

const requireFields = (
  context: Context,
  block: Block,
  label: string,
  keys: readonly string[],
): void => {
  for (const key of keys) {
    if (fieldValue(block, key) === undefined)
      addError(context, block.line, `${label} requires ${key}`);
  }
};

const checkReviewDate = (context: Context, block: Block, label: string): void => {
  const value = fieldValue(block, 'Review-date');
  if (value === undefined) return;
  const line = block.fields['Review-date']?.line ?? block.line;
  const status = reviewDateStatus(value, context.today);
  if (status === 'invalid')
    addError(context, line, `${label} Review-date "${value}" is not a valid YYYY-MM-DD date`);
  if (status === 'too-far')
    addError(context, line, `${label} Review-date ${value} is more than 12 months ahead`);
  if (status === 'expired') {
    context.counters.expired += 1;
    addError(context, line, `${label} Review-date ${value} is expired (today is ${context.today})`);
  }
};

const extractPointerTarget = (value: string): string => {
  const link = MARKDOWN_LINK.exec(value);
  return (link?.[1] ?? value).trim().replaceAll(/^[`"'<]+|[`"'>]+$/gu, '');
};

const safeDecode = (value: string): string => {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
};

// Returns an error message, or undefined when the pointer resolves to non-empty content.
const resolvePointer = (context: Context, value: string): string | undefined => {
  const target = extractPointerTarget(value);
  if (URL_POINTER.test(target)) {
    context.counters.external += 1;
    return undefined;
  }
  const relative = safeDecode(target.split('#')[0] ?? '');
  if (relative === '') return 'pointer has no file path';
  if (path.isAbsolute(relative))
    return `pointer "${relative}" must be a relative path or an http(s) URL`;
  const resolved = path.resolve(context.hubDir, relative);
  try {
    const stat = fs.statSync(resolved);
    const empty = stat.isDirectory()
      ? fs.readdirSync(resolved).length === 0
      : fs.readFileSync(resolved, 'utf8').trim() === '';
    return empty ? `pointer target "${relative}" is empty` : undefined;
  } catch {
    return `pointer target "${relative}" does not exist`;
  }
};

const missingContent = (block: Block): string =>
  fieldValue(block, 'Pointer') === undefined && fieldValue(block, 'Reasoning') === undefined
    ? 'has no pointer or reason'
    : 'has no Status';

const lineOf = (block: Block, key: string): number => block.fields[key]?.line ?? block.line;

const checkRole = (context: Context, block: Block, label: string): void => {
  const role = fieldValue(block, 'Role');
  if (role === undefined || !ROLES.has(role)) {
    addError(context, block.line, `${label} requires Role: controller, processor or joint`);
  }
};

const checkItemStatus = (
  context: Context,
  block: Block,
  spec: HubItem,
  label: string,
): string | undefined => {
  const status = fieldValue(block, 'Status');
  if (status === undefined) {
    addError(context, block.line, `${label} ${missingContent(block)}`);
  } else if (!ITEM_STATUSES.has(status)) {
    const expected = 'expected pointer or not-applicable';
    addError(
      context,
      lineOf(block, 'Status'),
      `${label} has invalid Status "${status}" (${expected})`,
    );
  } else if (status === 'pointer') {
    const pointer = fieldValue(block, 'Pointer');
    const problem = pointer === undefined ? 'requires Pointer' : resolvePointer(context, pointer);
    if (problem !== undefined) addError(context, lineOf(block, 'Pointer'), `${label} ${problem}`);
  } else if (spec.mayBeNotApplicable) {
    requireFields(context, block, label, ['Reasoning', 'Owner', 'Review-date']);
    checkReviewDate(context, block, label);
  } else {
    addError(context, lineOf(block, 'Status'), `${label} cannot be not-applicable`);
  }
  return status;
};

const validateItem = (context: Context, block: Block, spec: HubItem): ItemResult => {
  const label = `hub item "${spec.id}"`;
  const errorsBefore = context.findings.length;
  requireFields(context, block, label, ['Explanation']);
  if (spec.id === 'roles') checkRole(context, block, label);
  const status = checkItemStatus(context, block, spec, label);
  return {
    id: spec.id,
    status: status ?? null,
    resolved: context.findings.length === errorsBefore,
  };
};

const validateApplicable = (
  context: Context,
  blocks: readonly Block[],
  applicability: Block,
): ItemResult[] => {
  requireFields(context, applicability, 'hub applicability', ['Data-categories', 'Explanation']);
  const known = new Map(ITEMS.map((item) => [item.id, item]));
  const seen = new Set<string>();
  const results: ItemResult[] = [];
  for (const block of blocks.slice(1)) {
    const spec = known.get(block.id);
    if (block.id === APPLICABILITY_ID || seen.has(block.id)) {
      addError(context, block.line, `hub entry "${block.id}" is declared more than once`);
    } else if (spec === undefined) {
      addError(context, block.line, `hub entry "${block.id}" is not a known item id`);
    } else {
      seen.add(block.id);
      results.push(validateItem(context, block, spec));
    }
  }
  for (const spec of ITEMS.filter((item) => !seen.has(item.id))) {
    addError(context, null, `hub item "${spec.id}" has no pointer or reason`);
    results.push({ id: spec.id, status: null, resolved: false });
  }
  return results;
};

const validateOptOut = (
  context: Context,
  hub: string,
  blocks: readonly Block[],
  applicability: Block,
  dir: string,
): void => {
  requireFields(context, applicability, 'hub opt-out', [
    'Reason',
    'Inventory',
    'Owner',
    'Review-date',
  ]);
  checkReviewDate(context, applicability, 'hub opt-out');
  for (const block of blocks.slice(1)) {
    addError(
      context,
      block.line,
      `hub opt-out must not contain item entries (found "${block.id}")`,
    );
  }
  for (const policy of findGdprPolicies(hub)) {
    const name = path.basename(policy);
    addError(
      context,
      null,
      `hub opt-out must not coexist with the gdpr policy "${name}"`,
      toPosix(path.relative(dir, policy)),
    );
  }
};

const failure = (
  mode: CheckMode,
  message: string,
  extra: Partial<CheckResult> = {},
): CheckResult => ({
  ok: false,
  mode,
  findings: [{ severity: 'ERROR', file: '.', line: null, message }],
  items: [],
  validUntil: null,
  externalPointers: 0,
  expired: 0,
  ...extra,
});

const validateHub = (hub: string, options: CheckOptions): CheckResult => {
  const file = toPosix(path.relative(options.dir, hub));
  const context: Context = {
    file,
    hubDir: path.dirname(hub),
    today: options.today,
    findings: [],
    counters: { external: 0, expired: 0 },
  };
  const blocks = parseBlocks(fs.readFileSync(hub, 'utf8'));
  const applicability = blocks[0];
  const status = applicability === undefined ? undefined : fieldValue(applicability, 'Status');
  let mode: CheckMode = 'invalid';
  let items: ItemResult[] = [];
  if (applicability?.id !== APPLICABILITY_ID) {
    addError(
      context,
      applicability?.line ?? null,
      `the first hub entry must be "${APPLICABILITY_ID}"`,
    );
  } else if (status === 'opted-out') {
    mode = 'opted-out';
    validateOptOut(context, hub, blocks, applicability, options.dir);
  } else if (status === 'applicable') {
    mode = 'applicable';
    items = validateApplicable(context, blocks, applicability);
  } else {
    addError(
      context,
      applicability.fields['Status']?.line ?? applicability.line,
      'hub applicability Status must be applicable or opted-out',
    );
  }
  const ok = context.findings.length === 0;
  return {
    ok,
    mode,
    findings: context.findings,
    items,
    validUntil:
      ok && mode === 'opted-out' && applicability !== undefined
        ? (fieldValue(applicability, 'Review-date') ?? null)
        : null,
    externalPointers: context.counters.external,
    expired: context.counters.expired,
  };
};

export const check = (options: CheckOptions): CheckResult => {
  const hubs = findHubs(options.dir);
  const [hub] = hubs;
  if (hub === undefined)
    return failure('missing', `hub missing: no adrs/principles/${HUB_FILE_NAME} found`);
  if (hubs.length > 1) {
    const names = hubs.map((item) => toPosix(path.relative(options.dir, item))).join(', ');
    return failure('multiple', `more than one hub found (exactly one is allowed): ${names}`);
  }
  return validateHub(hub, options);
};

export const formatCheck = (result: CheckResult): string[] => {
  const errors = result.findings.filter((finding) => finding.severity === 'ERROR');
  const lines = errors.map(
    (finding) =>
      `ERROR ${finding.file}${finding.line === null ? '' : `:${finding.line}`}: ${finding.message}`,
  );
  if (!result.ok) return [...lines, ...errors.map((finding) => `check: ${finding.message}`)];
  if (result.externalPointers > 0)
    lines.push(`info: ${result.externalPointers} unverified external pointer(s)`);
  if (result.mode === 'opted-out')
    return [...lines, `check: opted-out, valid until ${result.validUntil}`];
  const resolved = result.items.filter((item) => item.resolved).length;
  return [...lines, `check: hub found, ${resolved} items resolved, ${result.expired} expired`];
};
