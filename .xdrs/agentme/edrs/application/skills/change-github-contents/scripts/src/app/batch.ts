import { usageError } from '../shared/errors';

import { parseArgs } from './args';
import type { Deps } from './ports';

export type Item = Record<string, unknown>;
export type ItemStatus = 'verified' | 'already-present' | 'error';
export type ItemResult = { status: ItemStatus; [key: string]: unknown };
export type Handler = (item: Item, deps: Deps) => ItemResult;

const errorMessage = (error: unknown): string => {
  const { stderr } = error as { stderr?: string };
  return String(stderr ?? (error as Error).message).trim();
};

// Reads the JSON items array from `--input <file>` or stdin.
export const readItems = (argv: readonly string[], deps: Deps): Item[] => {
  const { input } = parseArgs(argv);
  const text = deps.input.read(typeof input === 'string' ? input : undefined);
  let items: unknown;
  try {
    items = JSON.parse(text);
  } catch (error) {
    throw usageError(`input is not valid JSON: ${(error as Error).message}`);
  }
  if (!Array.isArray(items)) throw usageError('input must be a JSON array of items');
  return items as Item[];
};

// Returns the named fields of an item as strings; fails when any is missing or empty.
export const requireFields = (item: Item, fields: readonly string[]): Record<string, string> => {
  const missing = fields.filter((field) => typeof item?.[field] !== 'string' || item[field] === '');
  if (missing.length > 0) throw new Error(`item is missing string field(s): ${missing.join(', ')}`);
  return Object.fromEntries(fields.map((field) => [field, item[field] as string]));
};

// Runs the handler for every item; one failing item never stops the batch.
export const runBatch = (items: readonly Item[], handler: Handler, deps: Deps): ItemResult[] =>
  items.map((item, index) => {
    try {
      return { index, ...handler(item, deps) };
    } catch (error) {
      const commentId = item?.['commentId'];
      return {
        index,
        ...(commentId === undefined ? {} : { commentId }),
        status: 'error',
        error: errorMessage(error),
      };
    }
  });

// Shared command wrapper: exit 2 on bad input, 1 when any item failed, else 0.
export const runBatchCommand = (argv: readonly string[], handler: Handler, deps: Deps): number => {
  const results = runBatch(readItems(argv, deps), handler, deps);
  deps.output.out(`${JSON.stringify(results, undefined, 2)}\n`);
  return results.some((result) => result.status === 'error') ? 1 : 0;
};
