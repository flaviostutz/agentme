import { execFileSync } from 'node:child_process';

import type { AzPort } from '../../../app/ports';

const splitBin = (value: string | undefined): { bin: string; prefix: string[] } => {
  const parts = (value ?? 'az').split(' ').filter(Boolean);
  return { bin: parts[0] ?? 'az', prefix: parts.slice(1) };
};

// AZ_BIN lets tests substitute a fake az.
export const createAz = (env: Record<string, string | undefined>): AzPort => ({
  run: (args): string => {
    const { bin, prefix } = splitBin(env['AZ_BIN']);
    return execFileSync(bin, [...prefix, ...args], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      env,
      maxBuffer: 64 * 1024 * 1024,
    });
  },
});
