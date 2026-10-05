import {
  DEFAULT_SIZE,
  DEFAULT_SSO_WAIT_SECONDS,
  DEFAULT_WAIT_SECONDS,
  SKILL_PORT_MAX,
  SKILL_PORT_MIN,
  SUBCOMMANDS,
} from '../shared/constants';
import { usageError } from '../shared/errors';
import type { CommonOptions, Options, WindowSize } from '../shared/types';

export type Env = Record<string, string | undefined>;

export const validateSessionName = (name: string | undefined): string => {
  if (!/^[\w-]{1,32}$/.test(name ?? '')) {
    throw usageError('session name must match [A-Za-z0-9_-]{1,32}');
  }
  const value = name ?? '';
  if (SUBCOMMANDS.includes(value)) {
    throw usageError(`session name "${value}" is reserved`);
  }
  return value;
};

export const validateTargetUrl = (value: string | undefined): string => {
  let url: URL;
  try {
    url = new URL(value ?? '');
  } catch {
    throw usageError(`invalid url: ${value}`);
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw usageError('url must use http or https');
  }
  return url.href;
};

export const validateSsoCheckUrl = (value: string): string => {
  if (!/^https:\/\/[A-Za-z0-9.-]+(:\d{1,5})?(\/[^\s'"`\\<>]*)?$/.test(value)) {
    throw usageError('SSO_CHECK_URL must be an https URL with a plain host name');
  }
  return new URL(value).href;
};

export const parsePositiveInt = (value: string, name: string): number => {
  if (!/^\d{1,6}$/.test(value) || Number(value) < 1) {
    throw usageError(`${name} must be a positive whole number`);
  }
  return Number(value);
};

export const parseSize = (value: string): WindowSize => {
  const match = /^(\d{2,5})x(\d{2,5})$/.exec(value);
  if (!match) throw usageError('window size must look like 1200x900');
  return { width: Number(match[1]), height: Number(match[2]) };
};

export const parseCdpPort = (value: string): number => {
  if (!/^\d{4}$/.test(value) || Number(value) < SKILL_PORT_MIN || Number(value) > SKILL_PORT_MAX) {
    throw usageError(
      `--cdp-port must be between ${SKILL_PORT_MIN} and ${SKILL_PORT_MAX} (agentme-edr-128 rule 05)`,
    );
  }
  return Number(value);
};

const splitArgs = (argv: string[]): { cdpPort: number | undefined; positional: string[] } => {
  let cdpPort: number | undefined;
  const positional: string[] = [];
  for (const arg of argv) {
    if (arg.startsWith('--cdp-port=')) cdpPort = parseCdpPort(arg.slice('--cdp-port='.length));
    else if (arg.startsWith('--')) throw usageError(`unknown option ${arg}`);
    else positional.push(arg);
  }
  return { cdpPort, positional };
};

const parseWait = (positional: string[], common: CommonOptions): Options => {
  if (common.skipSso) throw usageError('SKIP_SSO=true cannot be combined with wait');
  if (common.cdpPort !== undefined) {
    throw usageError('wait keeps the port the session was opened with; drop --cdp-port');
  }
  if (positional.length < 3 || positional.length > 4) {
    throw usageError('wait needs <session> <url> [seconds]');
  }
  const seconds = positional[3];
  return {
    ...common,
    command: 'wait',
    session: validateSessionName(positional[1]),
    url: validateTargetUrl(positional[2]),
    waitSeconds: seconds ? parsePositiveInt(seconds, 'seconds') : DEFAULT_WAIT_SECONDS,
  };
};

export const parseArgs = (argv: string[], env: Env): Options => {
  const { cdpPort, positional } = splitArgs(argv);
  const checkUrl = env.SSO_CHECK_URL;
  const waitEnv = env.SSO_WAIT_SECONDS;
  const common: CommonOptions = {
    skipSso: env.SKIP_SSO === 'true',
    ssoCheckUrl: checkUrl ? validateSsoCheckUrl(checkUrl) : undefined,
    ssoWaitSeconds: waitEnv
      ? parsePositiveInt(waitEnv, 'SSO_WAIT_SECONDS')
      : DEFAULT_SSO_WAIT_SECONDS,
    cdpPort,
  };

  const [first] = positional;
  if (first === 'wait') return parseWait(positional, common);
  if (first === 'tidy') {
    if (positional.length !== 2) throw usageError('tidy needs <session>');
    return { ...common, command: 'tidy', session: validateSessionName(positional[1]) };
  }
  if (positional.length < 2 || positional.length > 3) {
    throw usageError('missing <session> or <url>');
  }
  return {
    ...common,
    command: 'open',
    session: validateSessionName(positional[0]),
    url: validateTargetUrl(positional[1]),
    size: parseSize(positional[2] ?? DEFAULT_SIZE),
  };
};
