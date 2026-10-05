import path from 'node:path';

import { SKILL_PORT_MAX } from '../shared/constants';

import { autoPortRange, edgePaths, isExcludedFromCopy, scratchPaths } from './edge-paths';

describe('autoPortRange', () => {
  it('covers 9390-9399 and never overlaps skill ports', () => {
    const ports = autoPortRange();
    expect(ports).toHaveLength(10);
    expect(ports[0]).toBe(9390);
    expect(ports[9]).toBe(9399);
    expect(ports.every((port) => port > SKILL_PORT_MAX)).toBe(true);
  });
});

describe('edgePaths', () => {
  it('resolves macOS locations', () => {
    const edge = edgePaths({
      platform: 'darwin',
      env: {},
      homedir: '/Users/me',
      exists: () => true,
    });
    expect(edge.binary).toBe('/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge');
    expect(edge.profileDir).toBe('/Users/me/Library/Application Support/Microsoft Edge');
  });

  it('picks the first existing Windows install', () => {
    const env = {
      'ProgramFiles(x86)': 'C:\\PF86',
      ProgramFiles: 'C:\\PF',
      LOCALAPPDATA: 'C:\\Users\\me\\AppData\\Local',
    };
    const edge = edgePaths({
      platform: 'win32',
      env,
      homedir: 'C:\\Users\\me',
      exists: (file) => file.startsWith('C:\\PF\\'),
    });
    expect(edge.binary).toBe('C:\\PF\\Microsoft\\Edge\\Application\\msedge.exe');
    expect(edge.profileDir).toBe('C:\\Users\\me\\AppData\\Local\\Microsoft\\Edge\\User Data');
    const none = edgePaths({ platform: 'win32', env: {}, homedir: 'C:\\', exists: () => false });
    expect(none).toEqual({});
  });

  it('searches PATH on Linux and honours overrides', () => {
    const edge = edgePaths({
      platform: 'linux',
      env: { PATH: '/usr/local/bin:/usr/bin' },
      homedir: '/home/me',
      exists: (file) => file === '/usr/bin/microsoft-edge',
    });
    expect(edge.binary).toBe('/usr/bin/microsoft-edge');
    expect(edge.profileDir).toBe('/home/me/.config/microsoft-edge');
    const custom = edgePaths({
      platform: 'linux',
      env: { EDGE_PATH: '/opt/edge', EDGE_PROFILE_DIR: '/data/edge' },
      homedir: '/home/me',
      exists: () => false,
    });
    expect(custom).toEqual({ binary: '/opt/edge', profileDir: '/data/edge' });
  });
});

describe('isExcludedFromCopy', () => {
  it('skips caches, locks and session-restore files only', () => {
    for (const name of ['Cache', 'Service Worker', 'SingletonLock', 'Sessions', 'Current Tabs']) {
      expect(isExcludedFromCopy(name)).toBe(true);
    }
    for (const name of ['Cookies', 'Preferences', 'Local Storage']) {
      expect(isExcludedFromCopy(name)).toBe(false);
    }
  });
});

describe('scratchPaths', () => {
  it('is per session', () => {
    expect(scratchPaths('/tmp', 's1')).toEqual({
      profileDir: path.join('/tmp', 'playwright-browser-s1-profile'),
      stateFile: path.join('/tmp', 'playwright-browser-s1.state'),
    });
  });
});
