import * as fs from 'node:fs';
import path from 'node:path';

import { HUB_FILE_NAME } from './check';
import { listFiles } from './files';
import {
  LLM_RULES,
  LOG_CALL,
  REGION_KEY,
  TRACKER_RULES,
  type KeywordMatcher,
  type Keywords,
  type PatternRule,
  createMatcher,
  findRegionStrings,
  splitWords,
} from './keywords';

export const REDACTED = '<redacted>';
export const MAX_FILE_BYTES = 1024 * 1024;
const MAX_LINE_LENGTH = 2000;
const BINARY_SNIFF_BYTES = 8000;

export type ItemKind =
  | 'pii-field'
  | 'special-category-field'
  | 'tracker-sdk'
  | 'llm-sdk'
  | 'cloud-region'
  | 'log-statement'
  | 'data-file'
  | 'runbook-candidate'
  | 'doc-candidate'
  | 'hub'
  | 'skipped';

export type DiscoverItem = {
  readonly kind: ItemKind;
  readonly name: string;
  readonly file: string;
  readonly line: number;
  readonly value: typeof REDACTED;
  readonly reason?: string;
};

export type DiscoverResult = {
  readonly items: DiscoverItem[];
  readonly counts: Record<string, number>;
  readonly filesListed: number;
};

const DATA_EXTENSIONS = new Set([
  'csv',
  'tsv',
  'ndjson',
  'jsonl',
  'dump',
  'bak',
  'log',
  'sqlite',
  'sqlite3',
  'db',
]);
const DATA_DIRS = new Set(['fixtures', 'data', 'samples', 'seeds', 'testdata']);
const STRUCTURED_DATA_EXTENSIONS = new Set(['json', 'yaml', 'yml']);
const BINARY_EXTENSIONS = new Set([
  'png',
  'jpg',
  'jpeg',
  'gif',
  'webp',
  'ico',
  'bmp',
  'tiff',
  'pdf',
  'zip',
  'gz',
  'tgz',
  'tar',
  'bz2',
  'xz',
  '7z',
  'rar',
  'jar',
  'war',
  'class',
  'exe',
  'dll',
  'so',
  'dylib',
  'o',
  'a',
  'wasm',
  'woff',
  'woff2',
  'ttf',
  'otf',
  'eot',
  'mp3',
  'mp4',
  'mov',
  'avi',
  'webm',
  'wav',
  'ogg',
  'doc',
  'docx',
  'xls',
  'xlsx',
  'ppt',
  'pptx',
  'odt',
  'psd',
  'pyc',
]);
const PROSE_EXTENSIONS = new Set(['md', 'mdx', 'txt', 'rst', 'adoc']);
const DOC_EXTENSIONS = new Set([
  '',
  ...PROSE_EXTENSIONS,
  'html',
  'htm',
  'pdf',
  'doc',
  'docx',
  'odt',
]);
const CONFIG_EXTENSIONS = new Set([
  'yml',
  'yaml',
  'json',
  'tf',
  'tfvars',
  'hcl',
  'toml',
  'ini',
  'cfg',
  'conf',
  'properties',
  'env',
]);
const RUNBOOK_WORDS = new Set([
  'runbook',
  'runbooks',
  'playbook',
  'playbooks',
  'incident',
  'incidents',
  'breach',
  'breaches',
  'dsr',
  'dsar',
  'erasure',
]);
const DOC_WORDS = new Set([
  'readme',
  'privacy',
  'consent',
  'cookie',
  'cookies',
  'gdpr',
  'dpa',
  'ropa',
  'dpia',
]);

const extensionOf = (relative: string): string =>
  path.posix.extname(relative).slice(1).toLowerCase();

const isLockFile = (basename: string): boolean => /(?:\.lock|-lock\.\w+|^go\.sum)$/u.test(basename);

// Data files are identified by name only and are never opened.
const dataFileType = (relative: string): string | undefined => {
  const basename = path.posix.basename(relative);
  const extension = extensionOf(relative);
  if (basename.startsWith('.env')) return 'env';
  if (DATA_EXTENSIONS.has(extension)) return extension;
  const directories = relative.split('/').slice(0, -1);
  return STRUCTURED_DATA_EXTENSIONS.has(extension) &&
    directories.some((segment) => DATA_DIRS.has(segment))
    ? extension
    : undefined;
};

const wordsOf = (segment: string): string[] => splitWords(segment.replace(/\.[^.]*$/u, ''));

const runbookWord = (relative: string): string | undefined => {
  for (const segment of relative.split('/')) {
    const words = wordsOf(segment);
    const hit = words.find((word) => RUNBOOK_WORDS.has(word));
    if (hit !== undefined) return hit;
    if (words.some((word, index) => word === 'data' && words[index + 1]?.startsWith('subject')))
      return 'data-subject';
  }
  return undefined;
};

const docWord = (relative: string): string | undefined =>
  DOC_EXTENSIONS.has(extensionOf(relative))
    ? wordsOf(path.posix.basename(relative)).find((word) => DOC_WORDS.has(word))
    : undefined;

const item = (
  kind: ItemKind,
  name: string,
  file: string,
  line = 0,
  reason?: string,
): DiscoverItem => ({
  kind,
  name,
  file,
  line,
  value: REDACTED,
  ...(reason === undefined ? {} : { reason }),
});

const pathItems = (relative: string): DiscoverItem[] => {
  const type = dataFileType(relative);
  if (type !== undefined) return [item('data-file', type, relative)];
  const found: DiscoverItem[] = [];
  if (path.posix.basename(relative) === HUB_FILE_NAME)
    found.push(item('hub', '010-gdpr-applicability', relative));
  const runbook = runbookWord(relative);
  if (runbook !== undefined) found.push(item('runbook-candidate', runbook, relative));
  const doc = docWord(relative);
  if (doc !== undefined && !found.some((entry) => entry.kind === 'hub'))
    found.push(item('doc-candidate', doc, relative));
  return found;
};

const matchRules = (rules: readonly PatternRule[], line: string): string[] =>
  rules.filter((rule) => rule.pattern.test(line)).map((rule) => rule.name);

const lineItems = (
  matcher: KeywordMatcher,
  line: string,
  relative: string,
  lineNumber: number,
  isConfig: boolean,
): DiscoverItem[] => {
  const pii = matcher.pii(line);
  const special = matcher.special(line);
  const regions = findRegionStrings(line);
  if (isConfig && REGION_KEY.test(line)) regions.push('region');
  return [
    ...pii.map((name) => item('pii-field', name, relative, lineNumber)),
    ...special.map((name) => item('special-category-field', name, relative, lineNumber)),
    ...matchRules(TRACKER_RULES, line).map((name) =>
      item('tracker-sdk', name, relative, lineNumber),
    ),
    ...matchRules(LLM_RULES, line).map((name) => item('llm-sdk', name, relative, lineNumber)),
    ...regions.map((name) => item('cloud-region', name, relative, lineNumber)),
    ...(LOG_CALL.test(line)
      ? [...pii, ...special].map((name) => item('log-statement', name, relative, lineNumber))
      : []),
  ];
};

type ReadOutcome =
  { readonly text: string } | { readonly skip: string } | { readonly binary: true };

const readText = (absolute: string): ReadOutcome => {
  try {
    if (fs.statSync(absolute).size > MAX_FILE_BYTES) return { skip: 'file larger than 1 MB' };
    const buffer = fs.readFileSync(absolute);
    if (buffer.subarray(0, BINARY_SNIFF_BYTES).includes(0)) return { binary: true };
    return { text: new TextDecoder('utf-8', { fatal: true }).decode(buffer) };
  } catch (error) {
    return {
      skip:
        (error as { code?: string }).code === 'ERR_ENCODING_INVALID_ENCODED_DATA'
          ? 'invalid UTF-8'
          : 'unreadable',
    };
  }
};

const contentItems = (matcher: KeywordMatcher, dir: string, relative: string): DiscoverItem[] => {
  const extension = extensionOf(relative);
  if (
    BINARY_EXTENSIONS.has(extension) ||
    PROSE_EXTENSIONS.has(extension) ||
    isLockFile(path.posix.basename(relative))
  )
    return [];
  const outcome = readText(path.join(dir, relative));
  if ('skip' in outcome) return [item('skipped', outcome.skip, relative, 0, outcome.skip)];
  if ('binary' in outcome) return [];
  const isConfig =
    CONFIG_EXTENSIONS.has(extension) || path.posix.basename(relative).startsWith('Dockerfile');
  return outcome.text
    .split(/\r?\n/u)
    .flatMap((line, index) =>
      line.length > MAX_LINE_LENGTH ? [] : lineItems(matcher, line, relative, index + 1, isConfig),
    );
};

const compareItems = (left: DiscoverItem, right: DiscoverItem): number => {
  const keys = ['file', 'line', 'kind', 'name'] as const;
  for (const key of keys) {
    if (left[key] < right[key]) return -1;
    if (left[key] > right[key]) return 1;
  }
  return 0;
};

export const discover = (options: {
  readonly dir: string;
  readonly keywords: Keywords;
}): DiscoverResult => {
  const matcher = createMatcher(options.keywords);
  const files = listFiles(options.dir);
  const found = files.flatMap((relative) => [
    ...pathItems(relative),
    ...(dataFileType(relative) === undefined ? contentItems(matcher, options.dir, relative) : []),
  ]);
  const unique = new Map(
    found.map((entry) => [`${entry.file}\0${entry.line}\0${entry.kind}\0${entry.name}`, entry]),
  );
  const items = [...unique.values()].sort(compareItems);
  const counts: Record<string, number> = {};
  for (const entry of items) counts[entry.kind] = (counts[entry.kind] ?? 0) + 1;
  return { items, counts, filesListed: files.length };
};

// The only place the script writes: <dir>/.tmp/review-gdpr/<id>/discover.json
export const writeDiscover = (dir: string, id: string, result: DiscoverResult): string => {
  const runDir = path.join(dir, '.tmp', 'review-gdpr', id);
  fs.mkdirSync(runDir, { recursive: true });
  const target = path.join(runDir, 'discover.json');
  fs.writeFileSync(target, `${JSON.stringify(result, null, 2)}\n`);
  return target;
};
