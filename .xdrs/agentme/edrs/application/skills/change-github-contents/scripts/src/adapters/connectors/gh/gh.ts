import { execFileSync } from 'node:child_process';

import type { GhPort } from '../../../app/ports';

const splitBin = (value: string | undefined): { bin: string; prefix: string[] } => {
  const parts = (value ?? 'gh').split(' ').filter(Boolean);
  return { bin: parts[0] ?? 'gh', prefix: parts.slice(1) };
};

// GH_BIN lets tests substitute a fake gh; GH_PAGER=cat keeps gh from opening a pager.
export const createGh = (env: Record<string, string | undefined>): GhPort => ({
  run: (args): string => {
    const { bin, prefix } = splitBin(env['GH_BIN']);
    return execFileSync(bin, [...prefix, ...args], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...env, GH_PAGER: 'cat' },
      maxBuffer: 64 * 1024 * 1024,
    });
  },
});
