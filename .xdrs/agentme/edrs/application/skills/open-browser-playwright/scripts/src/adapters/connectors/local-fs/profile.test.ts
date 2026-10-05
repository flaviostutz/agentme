import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { filesConnector } from './profile';

describe('filesConnector', () => {
  let dir: string;

  beforeEach(() => {
    dir = fs.mkdtempSync(path.join(os.tmpdir(), 'open-browser-profile-'));
  });

  afterEach(() => {
    jest.restoreAllMocks();
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const makeRealProfile = (): string => {
    const real = path.join(dir, 'real');
    fs.mkdirSync(path.join(real, 'Default', 'Local Storage'), { recursive: true });
    fs.mkdirSync(path.join(real, 'Default', 'Cache'), { recursive: true });
    fs.writeFileSync(path.join(real, 'Default', 'Cookies'), 'cookies');
    fs.writeFileSync(path.join(real, 'Default', 'Cache', 'blob'), 'cache');
    fs.writeFileSync(path.join(real, 'Default', 'Local Storage', 'leveldb'), 'ls');
    fs.writeFileSync(path.join(real, 'Local State'), '{}');
    return real;
  };

  it('clones the profile without caches and lock files', () => {
    const real = makeRealProfile();
    const copy = path.join(dir, 'copy');
    fs.mkdirSync(copy);
    fs.writeFileSync(path.join(copy, 'stale'), 'old');

    const skipped = filesConnector.cloneProfile(real, copy);

    expect(skipped).toEqual([]);
    expect(fs.existsSync(path.join(copy, 'stale'))).toBe(false);
    expect(fs.readFileSync(path.join(copy, 'Default', 'Cookies'), 'utf8')).toBe('cookies');
    expect(fs.existsSync(path.join(copy, 'Default', 'Local Storage', 'leveldb'))).toBe(true);
    expect(fs.existsSync(path.join(copy, 'Default', 'Cache'))).toBe(false);
    expect(fs.existsSync(path.join(copy, 'Local State'))).toBe(true);
  });

  it('skips locked files and reports them', () => {
    const real = makeRealProfile();
    const original = fs.copyFileSync.bind(fs);
    jest.spyOn(fs, 'copyFileSync').mockImplementation((from, to, mode) => {
      if (String(from).endsWith('Cookies'))
        throw Object.assign(new Error('busy'), { code: 'EBUSY' });
      original(from, to, mode);
    });

    const skipped = filesConnector.cloneProfile(real, path.join(dir, 'copy'));

    expect(skipped).toEqual(['Cookies']);
  });

  it('rethrows unexpected copy errors', () => {
    const real = makeRealProfile();
    jest.spyOn(fs, 'copyFileSync').mockImplementation(() => {
      throw Object.assign(new Error('disk'), { code: 'ENOSPC' });
    });
    expect(() => filesConnector.cloneProfile(real, path.join(dir, 'copy'))).toThrow('disk');
  });

  it('tolerates a profile without Local State', () => {
    const real = makeRealProfile();
    fs.rmSync(path.join(real, 'Local State'));
    expect(filesConnector.cloneProfile(real, path.join(dir, 'copy'))).toEqual([]);
  });

  it('removes lock and session-restore files from the copy', () => {
    const copy = path.join(dir, 'copy');
    fs.mkdirSync(path.join(copy, 'Default', 'Sessions'), { recursive: true });
    fs.writeFileSync(path.join(copy, 'SingletonLock'), '');
    fs.writeFileSync(path.join(copy, 'Default', 'Current Tabs'), '');
    fs.writeFileSync(path.join(copy, 'Default', 'Cookies'), 'c');

    filesConnector.removeRestoreFiles(copy);

    expect(fs.existsSync(path.join(copy, 'SingletonLock'))).toBe(false);
    expect(fs.existsSync(path.join(copy, 'Default', 'Sessions'))).toBe(false);
    expect(fs.existsSync(path.join(copy, 'Default', 'Current Tabs'))).toBe(false);
    expect(fs.existsSync(path.join(copy, 'Default', 'Cookies'))).toBe(true);
  });

  it('writes and reads the session state with owner-only permissions', () => {
    const file = path.join(dir, 's.state');
    const state = { port: 9390, browserId: 'b', user: 'me', tabId: 'T', baseline: ['B'] };
    expect(filesConnector.exists(file)).toBe(false);
    expect(filesConnector.readState(file)).toBeUndefined();
    filesConnector.writeState(file, state);
    expect(filesConnector.exists(file)).toBe(true);
    expect(filesConnector.readState(file)).toEqual(state);
    if (process.platform !== 'win32') expect(fs.statSync(file).mode % 0o1000).toBe(0o600);
  });
});
