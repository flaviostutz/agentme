import path from 'node:path';

import { AUTO_PORT_MAX, AUTO_PORT_MIN, PROFILE_EXCLUDES } from '../shared/constants';
import type { EdgeLocation, ScratchPaths } from '../shared/types';

export type EdgeLookup = {
  platform: string;
  env: Record<string, string | undefined>;
  homedir: string;
  exists: (file: string) => boolean;
};

export const autoPortRange = (): number[] =>
  Array.from({ length: AUTO_PORT_MAX - AUTO_PORT_MIN + 1 }, (_, index) => AUTO_PORT_MIN + index);

const windowsBinaries = (env: EdgeLookup['env']): string[] =>
  [env['ProgramFiles(x86)'], env.ProgramFiles, env.LOCALAPPDATA]
    .filter((root): root is string => Boolean(root))
    .map((root) => path.win32.join(root, 'Microsoft', 'Edge', 'Application', 'msedge.exe'));

const linuxBinaries = (env: EdgeLookup['env']): string[] => {
  const dirs = (env.PATH ?? '').split(':').filter(Boolean);
  return ['microsoft-edge-stable', 'microsoft-edge'].flatMap((name) =>
    dirs.map((dir) => path.posix.join(dir, name)),
  );
};

// exists is injected so each platform can be tested from any OS.
export const edgePaths = ({ platform, env, homedir, exists }: EdgeLookup): EdgeLocation => {
  let binaries: string[];
  let profileDir: string | undefined;
  if (platform === 'darwin') {
    binaries = ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'];
    profileDir = path.posix.join(homedir, 'Library/Application Support/Microsoft Edge');
  } else if (platform === 'win32') {
    binaries = windowsBinaries(env);
    profileDir =
      env.LOCALAPPDATA && path.win32.join(env.LOCALAPPDATA, 'Microsoft', 'Edge', 'User Data');
  } else {
    binaries = linuxBinaries(env);
    profileDir = path.posix.join(homedir, '.config/microsoft-edge');
  }
  const found = binaries.find((candidate) => exists(candidate));
  return {
    binary: env.EDGE_PATH || found,
    profileDir: env.EDGE_PROFILE_DIR || profileDir,
  };
};

export const isExcludedFromCopy = (name: string): boolean => PROFILE_EXCLUDES.has(name);

export const scratchPaths = (tmpdir: string, session: string): ScratchPaths => ({
  profileDir: path.join(tmpdir, `playwright-browser-${session}-profile`),
  stateFile: path.join(tmpdir, `playwright-browser-${session}.state`),
});
