import { usageError } from '../shared/errors';

export type ParsedArgs = Record<string, string | true>;

// Parses `--flag value` and bare `--flag` pairs; anything else is a usage error.
export const parseArgs = (argv: readonly string[]): ParsedArgs => {
  const parsed: ParsedArgs = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index] ?? '';
    if (!arg.startsWith('--')) throw usageError(`unexpected argument: ${arg}`);
    const next = argv[index + 1];
    if (next === undefined || next.startsWith('--')) {
      parsed[arg.slice(2)] = true;
    } else {
      parsed[arg.slice(2)] = next;
      index += 1;
    }
  }
  return parsed;
};

export const requireString = (parsed: ParsedArgs, name: string, usage: string): string => {
  const value = parsed[name];
  if (typeof value !== 'string') throw usageError(`Usage: ${usage}`);
  return value;
};

export const optionalString = (parsed: ParsedArgs, name: string): string | undefined => {
  const value = parsed[name];
  if (value === undefined) return undefined;
  if (typeof value !== 'string') throw usageError(`--${name} needs a value`);
  return value;
};

export const flag = (parsed: ParsedArgs, name: string): boolean => {
  const value = parsed[name];
  if (value === undefined) return false;
  if (value !== true) throw usageError(`--${name} takes no value`);
  return true;
};
