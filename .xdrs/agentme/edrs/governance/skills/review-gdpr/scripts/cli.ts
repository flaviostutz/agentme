import * as fs from 'node:fs';
import path from 'node:path';

import { check, formatCheck } from './check';
import { isValidIsoDate, localToday } from './dates';
import { discover, writeDiscover } from './discover';
import { type Keywords, loadKeywords } from './keywords';

export type Io = { readonly out: (text: string) => void; readonly err: (text: string) => void };

const USAGE = `Usage: review-gdpr.ts <discover|check> [options]

Commands:
  check     Validate the GDPR applicability hub offline (exit 1 on any ERROR)
              --dir <path>        directory to search for the hub (default: current directory)
              --json              print { ok, findings, items, ... } as JSON
              --today YYYY-MM-DD  override today's date (testing)
  discover  List candidate personal data locations for review (never prints values)
              --dir <path>        directory to scan (default: current directory)
              --json              print the items and counts as JSON
              --keywords <file>   JSON { "pii": [], "special": [] } extending the default keywords
              --out-id <id>       run folder id under .tmp/review-gdpr/ (default: local timestamp)

Exit codes: 0 ok, 1 findings or runtime failure, 2 usage error`;

type Flags = ReadonlyMap<string, string | true>;
type FlagSpec = Readonly<Record<string, 'boolean' | 'value'>>;

const FLAGS: Readonly<Record<string, FlagSpec>> = {
  check: { dir: 'value', json: 'boolean', today: 'value' },
  discover: { dir: 'value', json: 'boolean', keywords: 'value', 'out-id': 'value' },
};

class UsageError extends Error {
  name = 'UsageError';
}

const parseFlags = (command: string, args: readonly string[]): Flags => {
  const spec = FLAGS[command] ?? {};
  const parsed = new Map<string, string | true>();
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index] ?? '';
    const [name = '', inline] = arg.startsWith('--') ? arg.slice(2).split(/=(.*)/su) : [arg];
    const kind = arg.startsWith('--') ? spec[name] : undefined;
    if (kind === undefined) throw new UsageError(`unknown option for ${command}: ${arg}`);
    if (kind === 'boolean') {
      parsed.set(name, true);
    } else {
      const value = inline ?? args[index + 1];
      if (value === undefined || (inline === undefined && value.startsWith('--'))) {
        throw new UsageError(`option --${name} needs a value`);
      }
      parsed.set(name, value);
      if (inline === undefined) index += 1;
    }
  }
  return parsed;
};

const stringFlag = (flags: Flags, name: string): string | undefined => {
  const value = flags.get(name);
  return typeof value === 'string' ? value : undefined;
};

const resolveDir = (flags: Flags, cwd: string): string => {
  const dir = path.resolve(cwd, stringFlag(flags, 'dir') ?? '.');
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory())
    throw new UsageError(`--dir is not a directory: ${dir}`);
  return dir;
};

const timestampId = (now: Date): string => {
  const pad = (value: number): string => String(value).padStart(2, '0');
  const date = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`;
  return `${date}${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
};

const readKeywords = (flags: Flags, cwd: string): Keywords => {
  const file = stringFlag(flags, 'keywords');
  try {
    return loadKeywords(file === undefined ? undefined : path.resolve(cwd, file));
  } catch (error) {
    throw new UsageError((error as Error).message);
  }
};

const runCheck = (flags: Flags, io: Io, cwd: string, now: Date): number => {
  const dir = resolveDir(flags, cwd);
  const today = stringFlag(flags, 'today') ?? localToday(now);
  if (!isValidIsoDate(today))
    throw new UsageError(`--today must be a valid YYYY-MM-DD date: ${today}`);
  const result = check({ dir, today });
  io.out(
    flags.has('json')
      ? `${JSON.stringify(result, null, 2)}\n`
      : `${formatCheck(result).join('\n')}\n`,
  );
  return result.ok ? 0 : 1;
};

const runDiscover = (flags: Flags, io: Io, cwd: string, now: Date): number => {
  const dir = resolveDir(flags, cwd);
  const id = stringFlag(flags, 'out-id') ?? timestampId(now);
  if (!/^[\w.-]+$/u.test(id) || id === '.' || id === '..') {
    throw new UsageError(`--out-id must match [A-Za-z0-9._-]+: ${id}`);
  }
  const result = discover({ dir, keywords: readKeywords(flags, cwd) });
  const resultsPath = writeDiscover(dir, id, result);
  if (flags.has('json')) {
    io.out(`${JSON.stringify(result, null, 2)}\n`);
    return 0;
  }
  const counts = Object.entries(result.counts).map(([kind, count]) => `  ${kind}: ${count}`);
  const header = `discover: ${result.items.length} candidates in ${result.filesListed} files`;
  io.out(`${[header, ...counts, `results-path: ${resultsPath}`].join('\n')}\n`);
  return 0;
};

export const run = (
  argv: readonly string[],
  io: Io,
  cwd: string,
  now: Date = new Date(),
): number => {
  const [command, ...rest] = argv;
  if (argv.includes('--help') || argv.includes('-h')) {
    io.out(`${USAGE}\n`);
    return 0;
  }
  try {
    if (command === 'check') return runCheck(parseFlags(command, rest), io, cwd, now);
    if (command === 'discover') return runDiscover(parseFlags(command, rest), io, cwd, now);
    throw new UsageError(
      command === undefined ? 'a command is required' : `unknown command: ${command}`,
    );
  } catch (error) {
    if (error instanceof UsageError) {
      io.err(`Error: ${error.message}\n${USAGE}\n`);
      return 2;
    }
    io.err(`Error: ${(error as Error).message}\n`);
    return 1;
  }
};
