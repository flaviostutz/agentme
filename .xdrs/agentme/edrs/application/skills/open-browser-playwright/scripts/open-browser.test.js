#!/usr/bin/env node
'use strict';

// Unit tests for open-browser-lib.js plus offline usage checks of the open-browser.js runner.

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const lib = require('./open-browser-lib');

const RUNNER = path.join(__dirname, 'open-browser.js');

function assertUsage(fn, pattern) {
  assert.throws(fn, (err) => {
    assert.ok(err instanceof lib.ExitError);
    assert.equal(err.code, 64);
    if (pattern) assert.match(err.message, pattern);
    return true;
  });
}

test('parseArgs: open with defaults', () => {
  const opts = lib.parseArgs(['my-task', 'https://example.com'], {});
  assert.deepEqual(opts, {
    command: 'open',
    session: 'my-task',
    url: 'https://example.com/',
    size: { width: 1300, height: 900 },
    skipSso: false,
    ssoCheckUrl: null,
    ssoWaitSeconds: 45,
    cdpPort: null,
  });
});

test('parseArgs: open with size, port and env', () => {
  const opts = lib.parseArgs(['s1', 'http://example.com/a', '800x600', '--cdp-port=9231'], {
    SKIP_SSO: 'true',
    SSO_CHECK_URL: 'https://portal.example.com/me',
    SSO_WAIT_SECONDS: '10',
  });
  assert.equal(opts.cdpPort, 9231);
  assert.deepEqual(opts.size, { width: 800, height: 600 });
  assert.equal(opts.skipSso, true);
  assert.equal(opts.ssoCheckUrl, 'https://portal.example.com/me');
  assert.equal(opts.ssoWaitSeconds, 10);
});

test('parseArgs: SKIP_SSO only accepts exactly "true"', () => {
  assert.equal(lib.parseArgs(['s1', 'https://example.com'], { SKIP_SSO: 'yes' }).skipSso, false);
  assert.equal(lib.parseArgs(['s1', 'https://example.com'], { SKIP_SSO: 'TRUE' }).skipSso, false);
});

test('parseArgs: wait and tidy', () => {
  const wait = lib.parseArgs(['wait', 's1', 'https://example.com'], {});
  assert.equal(wait.command, 'wait');
  assert.equal(wait.waitSeconds, 300);
  assert.equal(lib.parseArgs(['wait', 's1', 'https://example.com', '60'], {}).waitSeconds, 60);
  const tidy = lib.parseArgs(['tidy', 's1'], {});
  assert.equal(tidy.command, 'tidy');
  assert.equal(tidy.session, 's1');
});

test('parseArgs: usage errors exit 64', () => {
  assertUsage(() => lib.parseArgs([], {}), /missing/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com', '--cdp-port=9229'], {}), /9230/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com', '--cdp-port=9390'], {}), /rule 05/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com', '--cdp-port=abc'], {}));
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com', '--headless'], {}), /unknown option/);
  assertUsage(() => lib.parseArgs(['s1', 'javascript:alert(1)'], {}), /http or https/);
  assertUsage(() => lib.parseArgs(['s1', 'not a url'], {}), /invalid url/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com', 'big'], {}), /window size/);
  assertUsage(() => lib.parseArgs(['bad name!', 'https://example.com'], {}), /session name/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com'], { SSO_CHECK_URL: "https://x.example.com/'a" }), /SSO_CHECK_URL/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com'], { SSO_CHECK_URL: 'http://x.example.com' }), /SSO_CHECK_URL/);
  assertUsage(() => lib.parseArgs(['s1', 'https://example.com'], { SSO_WAIT_SECONDS: '0' }), /SSO_WAIT_SECONDS/);
  assertUsage(() => lib.parseArgs(['wait', 's1', 'https://example.com'], { SKIP_SSO: 'true' }), /SKIP_SSO/);
  assertUsage(() => lib.parseArgs(['wait', 's1', 'https://example.com', '--cdp-port=9231'], {}), /cdp-port/);
  assertUsage(() => lib.parseArgs(['wait', 's1'], {}), /wait needs/);
  assertUsage(() => lib.parseArgs(['tidy'], {}), /tidy needs/);
});

test('validateSessionName rejects reserved subcommand names', () => {
  assertUsage(() => lib.validateSessionName('wait'), /reserved/);
  assertUsage(() => lib.validateSessionName('tidy'), /reserved/);
  assertUsage(() => lib.validateSessionName('a'.repeat(33)));
  assert.equal(lib.validateSessionName('ok_name-1'), 'ok_name-1');
});

test('autoPortRange covers 9390-9399 and never overlaps skill ports', () => {
  const ports = lib.autoPortRange();
  assert.equal(ports.length, 10);
  assert.equal(ports[0], 9390);
  assert.equal(ports[9], 9399);
  assert.ok(ports.every((port) => port > lib.SKILL_PORT_MAX));
});

test('edgePaths: macOS', () => {
  const edge = lib.edgePaths({ platform: 'darwin', env: {}, homedir: '/Users/me', exists: () => true });
  assert.equal(edge.binary, '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge');
  assert.equal(edge.profileDir, '/Users/me/Library/Application Support/Microsoft Edge');
});

test('edgePaths: Windows picks the first existing install', () => {
  const env = { 'ProgramFiles(x86)': 'C:\\PF86', ProgramFiles: 'C:\\PF', LOCALAPPDATA: 'C:\\Users\\me\\AppData\\Local' };
  const edge = lib.edgePaths({ platform: 'win32', env, homedir: 'C:\\Users\\me', exists: (p) => p.startsWith('C:\\PF\\') });
  assert.equal(edge.binary, 'C:\\PF\\Microsoft\\Edge\\Application\\msedge.exe');
  assert.equal(edge.profileDir, 'C:\\Users\\me\\AppData\\Local\\Microsoft\\Edge\\User Data');
  const none = lib.edgePaths({ platform: 'win32', env: {}, homedir: 'C:\\', exists: () => false });
  assert.equal(none.binary, null);
  assert.equal(none.profileDir, null);
});

test('edgePaths: Linux searches PATH and honours overrides', () => {
  const edge = lib.edgePaths({
    platform: 'linux',
    env: { PATH: '/usr/local/bin:/usr/bin' },
    homedir: '/home/me',
    exists: (p) => p === '/usr/bin/microsoft-edge',
  });
  assert.equal(edge.binary, '/usr/bin/microsoft-edge');
  assert.equal(edge.profileDir, '/home/me/.config/microsoft-edge');
  const custom = lib.edgePaths({
    platform: 'linux',
    env: { EDGE_PATH: '/opt/edge', EDGE_PROFILE_DIR: '/data/edge' },
    homedir: '/home/me',
    exists: () => false,
  });
  assert.deepEqual(custom, { binary: '/opt/edge', profileDir: '/data/edge' });
});

test('isExcludedFromCopy skips caches, locks and session-restore files', () => {
  for (const name of ['Cache', 'Service Worker', 'SingletonLock', 'Sessions', 'Current Tabs']) {
    assert.equal(lib.isExcludedFromCopy(name), true, name);
  }
  for (const name of ['Cookies', 'Preferences', 'Local Storage']) {
    assert.equal(lib.isExcludedFromCopy(name), false, name);
  }
});

test('scratchPaths are per session', () => {
  const paths = lib.scratchPaths('/tmp', 's1');
  assert.equal(paths.profileDir, path.join('/tmp', 'playwright-browser-s1-profile'));
  assert.equal(paths.stateFile, path.join('/tmp', 'playwright-browser-s1.state'));
});

test('state round-trips and rejects bad input', () => {
  const state = { port: 9390, browserId: 'abc-1', user: 'me@example.com', tabId: 'T1', baseline: ['B1'] };
  assert.deepEqual(lib.parseState(lib.serializeState(state)), state);
  assert.deepEqual(lib.parseState(lib.serializeState({ port: 9231, browserId: 'x' })), {
    port: 9231, browserId: 'x', user: '', tabId: null, baseline: null,
  });
  assert.equal(lib.parseState('not json'), null);
  assert.equal(lib.parseState('null'), null);
  assert.equal(lib.parseState('{"port":"9390","browserId":"x"}'), null);
  assert.deepEqual(lib.parseState('{"port":1,"browserId":"x","user":5,"tabId":7,"baseline":["a",3]}'), {
    port: 1, browserId: 'x', user: '', tabId: null, baseline: ['a'],
  });
});

test('browserIdFromVersion reads the browser websocket id', () => {
  assert.equal(lib.browserIdFromVersion({ webSocketDebuggerUrl: 'ws://127.0.0.1:9390/devtools/browser/1a-2b' }), '1a-2b');
  assert.equal(lib.browserIdFromVersion({}), null);
  assert.equal(lib.browserIdFromVersion(null), null);
});

test('nonce start page is found only on page targets', () => {
  const url = lib.nonceStartUrl('n0nce');
  assert.match(url, /^data:/);
  const targets = [
    { type: 'other', url, targetId: 'O' },
    { type: 'page', url: 'edge://newtab/', targetId: 'A' },
    { type: 'page', url, targetId: 'B' },
  ];
  assert.equal(lib.findNonceTarget(targets, 'n0nce').targetId, 'B');
  assert.equal(lib.findNonceTarget(targets, 'other'), null);
  assert.deepEqual(lib.pageTargets(targets).map((t) => t.targetId), ['A', 'B']);
});

test('hostOf returns host with port, or empty', () => {
  assert.equal(lib.hostOf('https://a.example.com:8443/x'), 'a.example.com:8443');
  assert.equal(lib.hostOf('nope'), '');
});

test('isAuthenticatedPage rejects sign-in pages and identity providers', () => {
  assert.equal(lib.isAuthenticatedPage('Dashboard', 'https://app.example.com/'), true);
  assert.equal(lib.isAuthenticatedPage('', 'https://app.example.com/'), false);
  assert.equal(lib.isAuthenticatedPage('Sign in to your account', 'https://app.example.com/'), false);
  assert.equal(lib.isAuthenticatedPage('Loading...', 'https://app.example.com/'), false);
  assert.equal(lib.isAuthenticatedPage('Designing a signing flow', 'https://app.example.com/'), true);
  assert.equal(lib.isAuthenticatedPage('Welcome', 'https://login.microsoftonline.com/common'), false);
  assert.equal(lib.isAuthenticatedPage('Welcome', 'https://accounts.google.com/x'), false);
  assert.equal(lib.isAuthenticatedPage('Welcome', 'about:blank'), false);
});

test('userExpression only reports an email on the check host', () => {
  const run = (host, bodyText, checkHost) => {
    const expression = lib.userExpression(checkHost);
    // eslint-disable-next-line no-new-func
    return new Function('location', 'document', `return ${expression};`)({ host }, { body: { innerText: bodyText } });
  };
  assert.equal(run('myaccount.example.com', 'Signed in as me@example.com', 'myaccount.example.com'), 'me@example.com');
  assert.equal(run('login.example.com', 'me@example.com', 'myaccount.example.com'), '');
  assert.equal(run('myaccount.example.com', 'no email here', 'myaccount.example.com'), '');
  assert.match(lib.userExpression('a"b'), /"a\\"b"/);
});

test('selectTabsToClose keeps baseline tabs and the newest task tab', () => {
  const pages = [{ targetId: 'B1' }, { targetId: 'T1' }, { targetId: 'T2' }, { targetId: 'T3' }];
  const result = lib.selectTabsToClose(pages, ['B1'], { T1: 10, T2: 30, T3: 20 });
  assert.equal(result.keep.targetId, 'T2');
  assert.deepEqual(result.close, ['T1', 'T3']);
});

test('selectTabsToClose handles ties, unknown load times and no task tabs', () => {
  const pages = [{ targetId: 'T1' }, { targetId: 'T2' }];
  assert.equal(lib.selectTabsToClose(pages, null, { T1: 5, T2: 5 }).keep.targetId, 'T1');
  assert.equal(lib.selectTabsToClose(pages, [], { T2: 5 }).keep.targetId, 'T2');
  assert.equal(lib.selectTabsToClose(pages, [], {}).keep.targetId, 'T1');
  assert.deepEqual(lib.selectTabsToClose(pages, ['T1', 'T2'], {}), { keep: null, close: [] });
});

test('formatResult prints the documented lines', () => {
  const text = lib.formatResult({
    result: 'opened', user: 'skipped', session: 's1', page: { title: 'Example', url: 'https://example.com/' }, port: 9390,
  });
  assert.equal(text, [
    'RESULT: opened',
    'USER: skipped',
    'SESSION: s1',
    'PAGE: [Example](https://example.com/)',
    'CDP: http://127.0.0.1:9390',
  ].join('\n'));
  assert.match(lib.formatResult({ result: 'x', user: 'none', session: 's', page: null, port: 1 }), /PAGE: \[\]\(\)/);
});

test('runner exits 64 on usage errors without opening a browser', () => {
  for (const args of [[], ['s1', 'https://example.com', '--cdp-port=9229']]) {
    const run = spawnSync(process.execPath, [RUNNER, ...args], { encoding: 'utf8' });
    assert.equal(run.status, 64);
    assert.match(run.stderr, /^RESULT: error - /);
    assert.equal(run.stdout, '');
  }
});

test('runner tidy reports no-session for an unknown session', () => {
  const env = { ...process.env, TMPDIR: __dirname, TMP: __dirname, TEMP: __dirname };
  const run = spawnSync(process.execPath, [RUNNER, 'tidy', `no-such-${process.pid}`], { encoding: 'utf8', env });
  assert.equal(run.status, 0);
  assert.match(run.stdout, /^RESULT: no-session/);
});
