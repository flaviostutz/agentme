import fs from 'node:fs';
import path from 'node:path';

import { isExcludedFromCopy } from '../../../app/edge-paths';
import type { FilesPort } from '../../../app/ports';
import { parseState, serializeState } from '../../../app/state';
import { SESSION_RESTORE_FILES, SINGLETON_FILES } from '../../../shared/constants';
import type { SessionState } from '../../../shared/types';

const LOCKED_CODES = new Set(['EBUSY', 'EPERM', 'EACCES']);

const errorCode = (error: unknown): string | undefined => (error as NodeJS.ErrnoException).code;

const copyEntry = (entry: fs.Dirent, from: string, to: string, skipped: string[]): void => {
  try {
    if (entry.isDirectory()) copyTree(from, to, skipped);
    else if (entry.isFile()) fs.copyFileSync(from, to);
  } catch (error) {
    // Windows locks some files (e.g. cookies) while the user's Edge runs.
    if (!LOCKED_CODES.has(errorCode(error) ?? '')) throw error;
    skipped.push(entry.name);
  }
};

const copyTree = (src: string, dst: string, skipped: string[]): void => {
  fs.mkdirSync(dst, { recursive: true, mode: 0o700 });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (!isExcludedFromCopy(entry.name)) {
      copyEntry(entry, path.join(src, entry.name), path.join(dst, entry.name), skipped);
    }
  }
};

// Copies Default/ and Local State into the scratch profile and returns the names of locked files it skipped.
const cloneProfile = (realProfile: string, profileCopy: string): string[] => {
  fs.rmSync(profileCopy, { recursive: true, force: true });
  const skipped: string[] = [];
  copyTree(path.join(realProfile, 'Default'), path.join(profileCopy, 'Default'), skipped);
  try {
    fs.copyFileSync(path.join(realProfile, 'Local State'), path.join(profileCopy, 'Local State'));
  } catch (error) {
    if (errorCode(error) !== 'ENOENT') skipped.push('Local State');
  }
  return skipped;
};

const removeRestoreFiles = (profileCopy: string): void => {
  for (const name of SINGLETON_FILES) fs.rmSync(path.join(profileCopy, name), { force: true });
  for (const name of SESSION_RESTORE_FILES) {
    fs.rmSync(path.join(profileCopy, 'Default', name), { recursive: true, force: true });
  }
};

const readState = (file: string): SessionState | undefined => {
  try {
    return parseState(fs.readFileSync(file, 'utf8'));
  } catch {
    return undefined;
  }
};

const writeState = (file: string, state: SessionState): void => {
  fs.writeFileSync(file, serializeState(state), { mode: 0o600 });
};

export const filesConnector: FilesPort = {
  exists: (file) => fs.existsSync(file),
  readState,
  writeState,
  cloneProfile,
  removeRestoreFiles,
};
