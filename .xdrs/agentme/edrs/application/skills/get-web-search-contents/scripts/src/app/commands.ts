import { CDP_PORT, DEFAULT_SESSION, MAX_PROMPT_CHARS, MAX_QUERY_CHARS } from '../shared/constants';
import { usageError } from '../shared/errors';

import { flag, optionalString, parseArgs, requireString } from './args';
import { runChat } from './chat';
import {
  validateId,
  validateLang,
  validateMaxSearches,
  validateRegion,
  validateText,
} from './guards';
import type { Deps, Wiring } from './ports';
import { runSearch } from './search';
import type { Engine } from './types';

const SEARCH_USAGE =
  'search --query <text> [--engine duckduckgo|google] [--google-confirmed] [--run-id <id>] [--max-searches <1-30>] [--lang <xx>] [--region <XX>] [--session <name>] [--cdp-port <port>]';
const CHAT_USAGE =
  'chat --prompt <text> --google-confirmed [--new-thread] [--close] [--run-id <id>] [--max-searches <1-30>] [--lang <xx>] [--region <XX>] [--session <name>] [--cdp-port <port>]';

const parseEngine = (raw: string | undefined): Engine => {
  if (raw === undefined || raw === 'duckduckgo') return 'duckduckgo';
  if (raw === 'google') return 'google';
  throw usageError('--engine must be duckduckgo or google');
};

const parsePort = (raw: string | undefined): number => {
  if (raw === undefined) return CDP_PORT;
  const port = Number(raw);
  if (!Number.isInteger(port) || port < 1024 || port > 65_535)
    throw usageError('--cdp-port must be 1024-65535');
  return port;
};

const connect = (wiring: Wiring, parsed: ReturnType<typeof parseArgs>): Deps => ({
  browser: wiring.connect(
    validateId(optionalString(parsed, 'session') ?? DEFAULT_SESSION, '--session'),
    parsePort(optionalString(parsed, 'cdp-port')),
  ),
  state: wiring.state,
  clock: wiring.clock,
  output: wiring.output,
});

const common = (
  parsed: ReturnType<typeof parseArgs>,
): {
  runId: string;
  maxSearches: number;
  googleConfirmed: boolean;
  lang?: string;
  region?: string;
} => ({
  runId: validateId(optionalString(parsed, 'run-id') ?? 'default', '--run-id'),
  maxSearches: validateMaxSearches(optionalString(parsed, 'max-searches')),
  googleConfirmed: flag(parsed, 'google-confirmed'),
  lang: validateLang(optionalString(parsed, 'lang')),
  region: validateRegion(optionalString(parsed, 'region')),
});

export const searchCommand = async (argv: readonly string[], wiring: Wiring): Promise<number> => {
  const parsed = parseArgs(argv);
  const query = validateText(
    requireString(parsed, 'query', SEARCH_USAGE),
    '--query',
    MAX_QUERY_CHARS,
  );
  const engine = parseEngine(optionalString(parsed, 'engine'));
  const options = { query, engine, ...common(parsed) };
  const result = await runSearch(connect(wiring, parsed), options);
  wiring.output.out(`${JSON.stringify(result, undefined, 2)}\n`);
  return 0;
};

export const chatCommand = async (argv: readonly string[], wiring: Wiring): Promise<number> => {
  const parsed = parseArgs(argv);
  const prompt = validateText(
    requireString(parsed, 'prompt', CHAT_USAGE),
    '--prompt',
    MAX_PROMPT_CHARS,
  );
  const options = {
    prompt,
    freshThread: flag(parsed, 'new-thread'),
    close: flag(parsed, 'close'),
    ...common(parsed),
  };
  const result = await runChat(connect(wiring, parsed), options);
  wiring.output.out(`${JSON.stringify(result, undefined, 2)}\n`);
  return 0;
};
