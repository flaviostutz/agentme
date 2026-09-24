#!/usr/bin/env node
'use strict';

// Opens a visible Edge window on a per-session copy of the user's profile, checks SSO over CDP and
// opens the target page. See ../SKILL.md for commands, output lines and exit codes.

const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const lib = require('./open-browser-lib');

const CDP_STARTUP_MS = 15000;
const COMMAND_TIMEOUT_MS = 15000;
const RENAVIGATE_MS = 5000;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class Cdp {
  static connect(wsUrl) {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(wsUrl);
      ws.onopen = () => resolve(new Cdp(ws));
      ws.onerror = () => reject(new Error(`cannot connect to ${wsUrl}`));
    });
  }

  constructor(ws) {
    this.ws = ws;
    this.nextId = 1;
    this.pending = new Map();
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const call = this.pending.get(message.id);
      if (!call) return;
      this.pending.delete(message.id);
      clearTimeout(call.timer);
      if (message.error) call.reject(new Error(message.error.message));
      else call.resolve(message.result);
    };
    ws.onclose = () => {
      for (const call of this.pending.values()) {
        clearTimeout(call.timer);
        call.reject(new Error('CDP connection closed'));
      }
      this.pending.clear();
    };
  }

  send(method, params = {}, sessionId = undefined) {
    const id = this.nextId;
    this.nextId += 1;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP ${method} timed out`));
      }, COMMAND_TIMEOUT_MS);
      this.pending.set(id, { resolve, reject, timer });
      this.ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }));
    });
  }

  close() {
    this.ws.close();
  }
}

async function cdpVersion(port) {
  try {
    const response = await fetch(`http://127.0.0.1:${port}/json/version`, { signal: AbortSignal.timeout(2000) });
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
}

function portBusy(port) {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: '127.0.0.1', port });
    socket.setTimeout(1000, () => {
      socket.destroy();
      resolve(false);
    });
    socket.once('connect', () => {
      socket.destroy();
      resolve(true);
    });
    socket.once('error', () => resolve(false));
  });
}

async function pickAutoPort() {
  for (const port of lib.autoPortRange()) {
    if (!(await portBusy(port))) return port;
  }
  throw new lib.ExitError(4, `no free port in ${lib.AUTO_PORT_MIN}-${lib.AUTO_PORT_MAX}; close browser windows opened by earlier tasks`);
}

function readState(file) {
  try {
    return lib.parseState(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

function writeState(file, state) {
  fs.writeFileSync(file, lib.serializeState(state), { mode: 0o600 });
}

async function liveSession(state) {
  if (!state) return null;
  const version = await cdpVersion(state.port);
  return version && lib.browserIdFromVersion(version) === state.browserId ? version : null;
}

function copyTree(src, dst, skipped) {
  fs.mkdirSync(dst, { recursive: true, mode: 0o700 });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (lib.isExcludedFromCopy(entry.name)) continue;
    const from = path.join(src, entry.name);
    const to = path.join(dst, entry.name);
    try {
      if (entry.isDirectory()) copyTree(from, to, skipped);
      else if (entry.isFile()) fs.copyFileSync(from, to);
    } catch (err) {
      // Windows locks some files (e.g. cookies) while the user's Edge runs.
      if (!['EBUSY', 'EPERM', 'EACCES'].includes(err.code)) throw err;
      skipped.push(entry.name);
    }
  }
}

function cloneProfile(realProfile, profileCopy) {
  fs.rmSync(profileCopy, { recursive: true, force: true });
  const skipped = [];
  copyTree(path.join(realProfile, 'Default'), path.join(profileCopy, 'Default'), skipped);
  try {
    fs.copyFileSync(path.join(realProfile, 'Local State'), path.join(profileCopy, 'Local State'));
  } catch (err) {
    if (err.code !== 'ENOENT') skipped.push('Local State');
  }
  if (skipped.length > 0) {
    process.stderr.write(`WARNING: skipped ${skipped.length} locked profile file(s): ${skipped.join(', ')}\n`);
  }
  return skipped.length;
}

function removeRestoreFiles(profileCopy) {
  for (const name of lib.SINGLETON_FILES) fs.rmSync(path.join(profileCopy, name), { force: true });
  for (const name of lib.SESSION_RESTORE_FILES) {
    fs.rmSync(path.join(profileCopy, 'Default', name), { recursive: true, force: true });
  }
}

async function launchBrowser(binary, profileCopy, port, size) {
  removeRestoreFiles(profileCopy);
  const nonce = crypto.randomBytes(12).toString('hex');
  const args = [
    `--user-data-dir=${profileCopy}`,
    `--remote-debugging-port=${port}`,
    '--no-first-run',
    '--no-default-browser-check',
    `--window-size=${size.width},${size.height}`,
    '--window-position=100,100',
    lib.nonceStartUrl(nonce),
  ];
  let exited = null;
  const child = spawn(binary, args, { detached: true, stdio: 'ignore' });
  child.once('error', (err) => { exited = err.message; });
  child.once('exit', (code) => { exited = exited || `browser exited with code ${code}`; });
  child.unref();

  const deadline = Date.now() + CDP_STARTUP_MS;
  let version = null;
  while (!version && !exited && Date.now() < deadline) {
    version = await cdpVersion(port);
    if (!version) await sleep(500);
  }
  if (!version) {
    if (exited) return { code: 3, message: `browser failed to open: ${exited}` };
    child.kill();
    return { code: 5, message: `CDP endpoint http://127.0.0.1:${port} did not respond after launch` };
  }
  const cdp = await Cdp.connect(version.webSocketDebuggerUrl);
  // CDP can answer before the first tab exists.
  let own = null;
  const nonceDeadline = Date.now() + 5000;
  while (!own && Date.now() < nonceDeadline) {
    const { targetInfos } = await cdp.send('Target.getTargets');
    own = lib.findNonceTarget(targetInfos, nonce);
    if (!own) await sleep(250);
  }
  if (!own) {
    cdp.close();
    child.kill();
    return { code: 4, message: `port ${port} is held by another browser (agentme-edr-128 rule 05)` };
  }
  return { code: 0, cdp, version, targetId: own.targetId };
}

async function closeBrowser(version, port) {
  try {
    const cdp = await Cdp.connect(version.webSocketDebuggerUrl);
    await cdp.send('Browser.close').catch(() => {});
    cdp.close();
  } catch {
    // Already gone.
  }
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline && (await cdpVersion(port))) await sleep(500);
}

async function attachPage(cdp, targetId) {
  const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
  return { targetId, sessionId };
}

async function evaluate(cdp, page, expression) {
  try {
    const { result } = await cdp.send('Runtime.evaluate', { expression, returnByValue: true }, page.sessionId);
    return result ? result.value : undefined;
  } catch {
    return undefined;
  }
}

async function pageInfo(cdp, page) {
  const value = await evaluate(cdp, page, '[document.title, location.href, document.readyState]');
  return Array.isArray(value)
    ? { title: value[0], url: value[1], ready: value[2] === 'complete' }
    : { title: '', url: '', ready: false };
}

async function navigate(cdp, page, url) {
  try {
    await cdp.send('Page.navigate', { url }, page.sessionId);
  } catch {
    // Retried by the caller's polling loop.
  }
}

async function closeOtherPages(cdp, keepId) {
  const { targetInfos } = await cdp.send('Target.getTargets');
  for (const target of lib.pageTargets(targetInfos)) {
    if (target.targetId !== keepId) await cdp.send('Target.closeTarget', { targetId: target.targetId }).catch(() => {});
  }
}

async function waitForUser(cdp, page, checkHost, seconds) {
  const expression = lib.userExpression(checkHost);
  const deadline = Date.now() + seconds * 1000;
  while (Date.now() < deadline) {
    const user = await evaluate(cdp, page, expression);
    if (typeof user === 'string' && user) return user;
    await sleep(1000);
  }
  return '';
}

// A blocking navigation away from an SSO single-page app can be undone while it is still loading, so retry.
async function openTarget(cdp, page, url, { checkHost, seconds, requireAuth }) {
  await navigate(cdp, page, url);
  const targetHost = lib.hostOf(url);
  const deadline = Date.now() + seconds * 1000;
  let nextNavigation = Date.now() + RENAVIGATE_MS;
  await sleep(1000);
  let info = await pageInfo(cdp, page);
  while (Date.now() < deadline) {
    const onCheckPage = Boolean(checkHost) && lib.hostOf(info.url) === checkHost && targetHost !== checkHost;
    const loaded = info.ready && !/^(about:blank|data:)/.test(info.url);
    if (onCheckPage) {
      if (Date.now() >= nextNavigation) {
        await navigate(cdp, page, url);
        nextNavigation = Date.now() + RENAVIGATE_MS;
      }
    } else if (loaded && (!requireAuth || lib.isAuthenticatedPage(info.title, info.url))) {
      return { ...info, onCheckPage: false };
    }
    await sleep(1000);
    info = await pageInfo(cdp, page);
  }
  return { ...info, onCheckPage: Boolean(checkHost) && lib.hostOf(info.url) === checkHost && targetHost !== checkHost };
}

function finish(scratch, state, { result, code, user, info, skipped }) {
  writeState(scratch.stateFile, { ...state, user: user || state.user });
  process.stdout.write(`${lib.formatResult({ result, user, session: scratch.session, page: info, port: state.port })}\n`);
  if ((code === 10 || code === 11) && skipped > 0) {
    process.stderr.write('HINT: some locked profile files were not copied; close Edge and rerun\n');
  }
  return code;
}

function checkPageOf(opts) {
  const url = opts.ssoCheckUrl || lib.DEFAULT_CHECK_URL;
  return { url, host: lib.hostOf(url) };
}

async function startBrowser(opts, edge, scratch, port, reclone) {
  const fresh = reclone || !fs.existsSync(path.join(scratch.profileDir, 'Default'));
  const skipped = fresh ? cloneProfile(edge.profileDir, scratch.profileDir) : 0;
  const launch = await launchBrowser(edge.binary, scratch.profileDir, port, opts.size);
  return { ...launch, fresh, skipped };
}

async function launchSession(opts, edge, scratch, port, reclone) {
  let started = await startBrowser(opts, edge, scratch, port, reclone);
  if (started.code === 3 && !started.fresh) {
    process.stderr.write('Browser failed to open on the reused profile copy; re-creating it\n');
    started = await startBrowser(opts, edge, scratch, port, true);
  }
  if (started.code !== 0) throw new lib.ExitError(started.code, started.message);
  const page = await attachPage(started.cdp, started.targetId);
  await closeOtherPages(started.cdp, started.targetId);
  const state = {
    port,
    browserId: lib.browserIdFromVersion(started.version),
    user: '',
    tabId: started.targetId,
    baseline: [],
  };
  // Recorded before the SSO check so wait knows the port after a manual sign-in.
  writeState(scratch.stateFile, state);
  return { ...started, page, state };
}

async function runOpen(opts) {
  const edge = lib.edgePaths({ platform: process.platform, env: process.env, homedir: os.homedir(), exists: fs.existsSync });
  if (!edge.binary || !fs.existsSync(edge.binary)) {
    throw new lib.ExitError(2, 'Microsoft Edge not found (set EDGE_PATH)');
  }
  if (!edge.profileDir || !fs.existsSync(path.join(edge.profileDir, 'Default'))) {
    throw new lib.ExitError(2, `Edge profile not found at ${edge.profileDir} (set EDGE_PROFILE_DIR)`);
  }
  const scratch = { ...lib.scratchPaths(os.tmpdir(), opts.session), session: opts.session };
  const previous = readState(scratch.stateFile);
  let version = await liveSession(previous);
  if (version && opts.cdpPort !== null && opts.cdpPort !== previous.port) {
    process.stderr.write(`Session ${opts.session} is open on port ${previous.port}; relaunching it on ${opts.cdpPort}\n`);
    await closeBrowser(version, previous.port);
    version = null;
  }

  let session;
  if (version) {
    const cdp = await Cdp.connect(version.webSocketDebuggerUrl);
    const { targetInfos } = await cdp.send('Target.getTargets');
    const baseline = previous.baseline || lib.pageTargets(targetInfos).map((target) => target.targetId);
    const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
    session = {
      cdp,
      version,
      launched: false,
      fresh: false,
      skipped: 0,
      page: await attachPage(cdp, targetId),
      state: { ...previous, tabId: targetId, baseline },
    };
  } else {
    const port = opts.cdpPort === null ? await pickAutoPort() : opts.cdpPort;
    if (await portBusy(port)) {
      throw new lib.ExitError(4, `port ${port} is already in use; use the skill's own metadata.cdp-port (agentme-edr-128 rule 05) or close the process holding it`);
    }
    session = { ...(await launchSession(opts, edge, scratch, port, false)), launched: true };
  }

  try {
    let user = '';
    const check = checkPageOf(opts);
    if (!opts.skipSso) {
      await navigate(session.cdp, session.page, check.url);
      user = await waitForUser(session.cdp, session.page, check.host, opts.ssoWaitSeconds);
      if (!user && session.launched && !session.fresh) {
        process.stderr.write('SSO check failed on the reused profile copy; re-creating it\n');
        session.cdp.close();
        await closeBrowser(session.version, session.state.port);
        session = { ...(await launchSession(opts, edge, scratch, session.state.port, true)), launched: true };
        await navigate(session.cdp, session.page, check.url);
        user = await waitForUser(session.cdp, session.page, check.host, opts.ssoWaitSeconds);
      }
      if (!user) {
        const info = await pageInfo(session.cdp, session.page);
        return opts.ssoCheckUrl
          ? finish(scratch, session.state, { result: 'sign-in-required', code: 10, user: 'none', info, skipped: session.skipped })
          : finish(scratch, session.state, { result: 'sso-check-url-required', code: 11, user: 'none', info, skipped: session.skipped });
      }
    }

    const info = await openTarget(session.cdp, session.page, opts.url, {
      checkHost: opts.skipSso ? null : check.host,
      seconds: opts.ssoWaitSeconds,
      requireAuth: !opts.skipSso,
    });
    if (session.launched) await closeOtherPages(session.cdp, session.page.targetId);
    if (opts.skipSso) {
      return finish(scratch, session.state, { result: 'opened', code: 0, user: 'skipped', info, skipped: session.skipped });
    }
    const authenticated = !info.onCheckPage && lib.isAuthenticatedPage(info.title, info.url);
    return finish(scratch, session.state, {
      result: authenticated ? 'authenticated' : 'sign-in-required',
      code: authenticated ? 0 : 10,
      user,
      info,
      skipped: session.skipped,
    });
  } finally {
    session.cdp.close();
  }
}

async function connectLive(opts) {
  const scratch = { ...lib.scratchPaths(os.tmpdir(), opts.session), session: opts.session };
  const state = readState(scratch.stateFile);
  const version = await liveSession(state);
  if (!version) return { scratch, state: null };
  return { scratch, state, version, cdp: await Cdp.connect(version.webSocketDebuggerUrl) };
}

async function runWait(opts) {
  const live = await connectLive(opts);
  if (!live.state) {
    throw new lib.ExitError(3, `no open browser for session ${opts.session}; run the open command first`);
  }
  const { cdp, scratch } = live;
  let { state } = live;
  try {
    const { targetInfos } = await cdp.send('Target.getTargets');
    let tabId = lib.pageTargets(targetInfos).some((target) => target.targetId === state.tabId) ? state.tabId : null;
    if (!tabId) {
      ({ targetId: tabId } = await cdp.send('Target.createTarget', { url: 'about:blank' }));
      state = { ...state, tabId };
    }
    const page = await attachPage(cdp, tabId);
    const check = checkPageOf(opts);
    if (opts.ssoCheckUrl && lib.hostOf((await pageInfo(cdp, page)).url) !== check.host) {
      await navigate(cdp, page, check.url);
    }
    const user = await waitForUser(cdp, page, check.host, opts.waitSeconds);
    if (!user) {
      return finish(scratch, state, { result: 'sign-in-required', code: 10, user: 'none', info: await pageInfo(cdp, page), skipped: 0 });
    }
    const info = await openTarget(cdp, page, opts.url, { checkHost: check.host, seconds: opts.ssoWaitSeconds, requireAuth: true });
    const authenticated = !info.onCheckPage && lib.isAuthenticatedPage(info.title, info.url);
    return finish(scratch, state, {
      result: authenticated ? 'authenticated' : 'sign-in-required',
      code: authenticated ? 0 : 10,
      user,
      info,
      skipped: 0,
    });
  } finally {
    cdp.close();
  }
}

async function runTidy(opts) {
  const live = await connectLive(opts);
  if (!live.state) {
    process.stdout.write(`RESULT: no-session\nSESSION: ${opts.session}\n`);
    return 0;
  }
  const { cdp, scratch, state } = live;
  try {
    const { targetInfos } = await cdp.send('Target.getTargets');
    const pages = lib.pageTargets(targetInfos);
    const known = new Set(state.baseline || []);
    const timeOrigins = {};
    for (const target of pages.filter((candidate) => !known.has(candidate.targetId))) {
      const page = await attachPage(cdp, target.targetId);
      timeOrigins[target.targetId] = await evaluate(cdp, page, 'performance.timeOrigin');
      await cdp.send('Target.detachFromTarget', { sessionId: page.sessionId }).catch(() => {});
    }
    const { keep, close } = lib.selectTabsToClose(pages, state.baseline, timeOrigins);
    for (const targetId of close) await cdp.send('Target.closeTarget', { targetId }).catch(() => {});
    writeState(scratch.stateFile, { ...state, tabId: keep ? keep.targetId : state.tabId, baseline: null });
    process.stdout.write([
      'RESULT: tidied',
      `SESSION: ${opts.session}`,
      `PAGE: [${keep ? keep.title : ''}](${keep ? keep.url : ''})`,
      `CLOSED: ${close.length}`,
      `CDP: http://127.0.0.1:${state.port}`,
    ].join('\n') + '\n');
    return 0;
  } finally {
    cdp.close();
  }
}

async function main(argv) {
  if (typeof WebSocket === 'undefined' || typeof fetch === 'undefined') {
    throw new lib.ExitError(64, 'Node.js 22+ required');
  }
  const opts = lib.parseArgs(argv, process.env);
  process.umask(0o077);
  if (opts.command === 'wait') return runWait(opts);
  if (opts.command === 'tidy') return runTidy(opts);
  return runOpen(opts);
}

if (require.main === module) {
  main(process.argv.slice(2))
    .then((code) => { process.exitCode = code; })
    .catch((err) => {
      process.stderr.write(`RESULT: error - ${err.message}\n`);
      process.exitCode = err instanceof lib.ExitError ? err.code : 3;
    });
}
