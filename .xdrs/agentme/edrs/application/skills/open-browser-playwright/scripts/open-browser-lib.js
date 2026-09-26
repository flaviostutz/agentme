#!/usr/bin/env node
'use strict';

// Pure helpers for open-browser.js: argument validation, ports, paths, page checks and tab selection.

const path = require('node:path');

const SKILL_PORT_MIN = 9230;
const SKILL_PORT_MAX = 9389;
const AUTO_PORT_MIN = 9390;
const AUTO_PORT_MAX = 9399;
const DEFAULT_SIZE = '1200x900';
const DEFAULT_CHECK_URL = 'https://myaccount.microsoft.com/?ref=MeControl';
const DEFAULT_SSO_WAIT_SECONDS = 45;
const DEFAULT_WAIT_SECONDS = 300;
const SUBCOMMANDS = ['wait', 'tidy'];

// Caches are large and session-restore files would reopen the user's own tabs (with live tokens).
const PROFILE_EXCLUDES = new Set([
  'Cache', 'Code Cache', 'GPUCache', 'GrShaderCache', 'ShaderCache', 'DawnGraphiteCache',
  'DawnWebGPUCache', 'component_crx_cache', 'Service Worker', 'WebStorage', 'Snapshots',
  'SingletonLock', 'SingletonCookie', 'SingletonSocket', 'Sessions', 'Current Session',
  'Current Tabs', 'Last Session', 'Last Tabs', 'EdgeSessions',
]);
const SESSION_RESTORE_FILES = ['Sessions', 'Current Session', 'Current Tabs', 'Last Session', 'Last Tabs', 'EdgeSessions'];
const SINGLETON_FILES = ['SingletonLock', 'SingletonCookie', 'SingletonSocket'];

const USAGE = [
  'Usage:',
  '  node open-browser.js <session> <url> [WIDTHxHEIGHT] [--cdp-port=N]',
  '  node open-browser.js wait <session> <url> [seconds]',
  '  node open-browser.js tidy <session>',
].join('\n');

class ExitError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

function usageError(message) {
  return new ExitError(64, `${message}\n${USAGE}`);
}

function validateSessionName(name) {
  if (!/^[A-Za-z0-9_-]{1,32}$/.test(name || '')) {
    throw usageError('session name must match [A-Za-z0-9_-]{1,32}');
  }
  if (SUBCOMMANDS.includes(name)) {
    throw usageError(`session name "${name}" is reserved`);
  }
  return name;
}

function validateTargetUrl(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw usageError(`invalid url: ${value}`);
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw usageError('url must use http or https');
  }
  return url.href;
}

function validateSsoCheckUrl(value) {
  if (!/^https:\/\/[A-Za-z0-9.-]+(:\d{1,5})?(\/[^\s'"`\\<>]*)?$/.test(value)) {
    throw usageError('SSO_CHECK_URL must be an https URL with a plain host name');
  }
  return new URL(value).href;
}

function parsePositiveInt(value, name) {
  if (!/^[0-9]{1,6}$/.test(String(value)) || Number(value) < 1) {
    throw usageError(`${name} must be a positive whole number`);
  }
  return Number(value);
}

function parseSize(value) {
  const match = /^([0-9]{2,5})x([0-9]{2,5})$/.exec(value);
  if (!match) throw usageError('window size must look like 1200x900');
  return { width: Number(match[1]), height: Number(match[2]) };
}

function parseCdpPort(value) {
  if (!/^[0-9]{4}$/.test(value) || Number(value) < SKILL_PORT_MIN || Number(value) > SKILL_PORT_MAX) {
    throw usageError(`--cdp-port must be between ${SKILL_PORT_MIN} and ${SKILL_PORT_MAX} (agentme-edr-128 rule 05)`);
  }
  return Number(value);
}

function parseArgs(argv, env) {
  let cdpPort = null;
  const positional = [];
  for (const arg of argv) {
    if (arg.startsWith('--cdp-port=')) cdpPort = parseCdpPort(arg.slice('--cdp-port='.length));
    else if (arg.startsWith('--')) throw usageError(`unknown option ${arg}`);
    else positional.push(arg);
  }

  const skipSso = env.SKIP_SSO === 'true';
  const ssoCheckUrl = env.SSO_CHECK_URL ? validateSsoCheckUrl(env.SSO_CHECK_URL) : null;
  const ssoWaitSeconds = env.SSO_WAIT_SECONDS
    ? parsePositiveInt(env.SSO_WAIT_SECONDS, 'SSO_WAIT_SECONDS')
    : DEFAULT_SSO_WAIT_SECONDS;
  const common = { skipSso, ssoCheckUrl, ssoWaitSeconds, cdpPort };

  const [first] = positional;
  if (first === 'wait') {
    if (skipSso) throw usageError('SKIP_SSO=true cannot be combined with wait');
    if (cdpPort !== null) throw usageError('wait keeps the port the session was opened with; drop --cdp-port');
    if (positional.length < 3 || positional.length > 4) throw usageError('wait needs <session> <url> [seconds]');
    return {
      ...common,
      command: 'wait',
      session: validateSessionName(positional[1]),
      url: validateTargetUrl(positional[2]),
      waitSeconds: positional[3] ? parsePositiveInt(positional[3], 'seconds') : DEFAULT_WAIT_SECONDS,
    };
  }
  if (first === 'tidy') {
    if (positional.length !== 2) throw usageError('tidy needs <session>');
    return { ...common, command: 'tidy', session: validateSessionName(positional[1]) };
  }
  if (positional.length < 2 || positional.length > 3) throw usageError('missing <session> or <url>');
  return {
    ...common,
    command: 'open',
    session: validateSessionName(positional[0]),
    url: validateTargetUrl(positional[1]),
    size: parseSize(positional[2] || DEFAULT_SIZE),
  };
}

function autoPortRange() {
  const ports = [];
  for (let port = AUTO_PORT_MIN; port <= AUTO_PORT_MAX; port += 1) ports.push(port);
  return ports;
}

// exists is injected so each platform can be tested from any OS.
function edgePaths({ platform, env, homedir, exists }) {
  let binaries;
  let profileDir;
  if (platform === 'darwin') {
    binaries = ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'];
    profileDir = path.posix.join(homedir, 'Library/Application Support/Microsoft Edge');
  } else if (platform === 'win32') {
    const roots = [env['ProgramFiles(x86)'], env.ProgramFiles, env.LOCALAPPDATA].filter(Boolean);
    binaries = roots.map((root) => path.win32.join(root, 'Microsoft', 'Edge', 'Application', 'msedge.exe'));
    profileDir = env.LOCALAPPDATA ? path.win32.join(env.LOCALAPPDATA, 'Microsoft', 'Edge', 'User Data') : null;
  } else {
    const dirs = (env.PATH || '').split(':').filter(Boolean);
    binaries = [];
    for (const name of ['microsoft-edge-stable', 'microsoft-edge']) {
      for (const dir of dirs) binaries.push(path.posix.join(dir, name));
    }
    profileDir = path.posix.join(homedir, '.config/microsoft-edge');
  }
  const binary = env.EDGE_PATH || binaries.find((candidate) => exists(candidate)) || null;
  return { binary, profileDir: env.EDGE_PROFILE_DIR || profileDir };
}

function isExcludedFromCopy(name) {
  return PROFILE_EXCLUDES.has(name);
}

function scratchPaths(tmpdir, session) {
  return {
    profileDir: path.join(tmpdir, `playwright-browser-${session}-profile`),
    stateFile: path.join(tmpdir, `playwright-browser-${session}.state`),
  };
}

function parseState(text) {
  try {
    const state = JSON.parse(text);
    if (!state || typeof state !== 'object' || !Number.isInteger(state.port) || typeof state.browserId !== 'string') {
      return null;
    }
    return {
      port: state.port,
      browserId: state.browserId,
      user: typeof state.user === 'string' ? state.user : '',
      tabId: typeof state.tabId === 'string' ? state.tabId : null,
      baseline: Array.isArray(state.baseline) ? state.baseline.filter((id) => typeof id === 'string') : null,
    };
  } catch {
    return null;
  }
}

function serializeState(state) {
  return `${JSON.stringify({
    port: state.port,
    browserId: state.browserId,
    user: state.user || '',
    tabId: state.tabId || null,
    baseline: state.baseline || null,
  })}\n`;
}

function browserIdFromVersion(version) {
  const wsUrl = version && version.webSocketDebuggerUrl;
  const match = typeof wsUrl === 'string' ? /\/devtools\/browser\/([A-Za-z0-9-]+)$/.exec(wsUrl) : null;
  return match ? match[1] : null;
}

// Edge swaps an about:blank start URL for its new tab page, so the nonce rides on a data: URL.
function nonceStartUrl(nonce) {
  return `data:text/html,opening#${nonce}`;
}

// The first page carries a random nonce, so a browser answering on the port proves it is ours.
function findNonceTarget(targets, nonce) {
  return targets.find((target) => target.type === 'page' && String(target.url).endsWith(`#${nonce}`)) || null;
}

function pageTargets(targets) {
  return targets.filter((target) => target.type === 'page');
}

function hostOf(value) {
  try {
    return new URL(value).host;
  } catch {
    return '';
  }
}

const SIGN_IN_TITLE = /(^|[^a-z])sign[ -]?in([^a-z]|$)|^loading/i;
const IDP_URL = /login\.microsoftonline\.com|login\.live\.com|accounts\.google\.com|\/_signin|\/adfs\/|\/oauth2\/|msalredirect|^about:blank/i;

function isAuthenticatedPage(title, url) {
  if (!title) return false;
  return !SIGN_IN_TITLE.test(title) && !IDP_URL.test(url || '');
}

// Only counts an email found on the check page's own host, so login or account-picker pages never pass.
function userExpression(checkHost) {
  return `(() => location.host === ${JSON.stringify(checkHost)} ? `
    + '(((document.body && document.body.innerText) || "").match(/[\\w.+-]+@[\\w-]+(\\.[\\w-]+)+/) || [""])[0] : "")()';
}

// Keeps baseline tabs and the task tab with the newest page load; closes the other task tabs.
function selectTabsToClose(pages, baseline, timeOrigins) {
  const known = new Set(baseline || []);
  const taskTabs = pages.filter((page) => !known.has(page.targetId));
  if (taskTabs.length === 0) return { keep: null, close: [] };
  let keep = taskTabs[0];
  for (const page of taskTabs) {
    const origin = timeOrigins[page.targetId];
    const best = timeOrigins[keep.targetId];
    if (Number.isFinite(origin) && (!Number.isFinite(best) || origin > best)) keep = page;
  }
  return { keep, close: taskTabs.filter((page) => page !== keep).map((page) => page.targetId) };
}

function formatResult({ result, user, session, page, port }) {
  const title = (page && page.title) || '';
  const url = (page && page.url) || '';
  return [
    `RESULT: ${result}`,
    `USER: ${user}`,
    `SESSION: ${session}`,
    `PAGE: [${title}](${url})`,
    `CDP: http://127.0.0.1:${port}`,
  ].join('\n');
}

module.exports = {
  SKILL_PORT_MIN,
  SKILL_PORT_MAX,
  AUTO_PORT_MIN,
  AUTO_PORT_MAX,
  DEFAULT_CHECK_URL,
  SESSION_RESTORE_FILES,
  SINGLETON_FILES,
  USAGE,
  ExitError,
  validateSessionName,
  validateTargetUrl,
  validateSsoCheckUrl,
  parsePositiveInt,
  parseSize,
  parseCdpPort,
  parseArgs,
  autoPortRange,
  edgePaths,
  isExcludedFromCopy,
  scratchPaths,
  parseState,
  serializeState,
  browserIdFromVersion,
  nonceStartUrl,
  findNonceTarget,
  pageTargets,
  hostOf,
  isAuthenticatedPage,
  userExpression,
  selectTabsToClose,
  formatResult,
};
