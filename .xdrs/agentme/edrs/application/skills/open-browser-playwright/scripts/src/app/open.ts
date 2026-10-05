import path from 'node:path';

import { AUTO_PORT_MAX, AUTO_PORT_MIN } from '../shared/constants';
import { ExitError } from '../shared/errors';
import type {
  Cdp,
  CdpVersion,
  EdgeLocation,
  OpenOptions,
  PageHandle,
  SessionState,
} from '../shared/types';

import { autoPortRange, edgePaths } from './edge-paths';
import {
  attachPage,
  closeOtherPages,
  createBlankTab,
  getTargets,
  navigate,
  openTarget,
  pageInfo,
  waitForUser,
} from './page-ops';
import { isAuthenticatedPage } from './pages';
import type { Deps, LaunchOk, LaunchResult } from './ports';
import { checkPageOf, finish, liveVersion, scratchFor } from './session';
import type { Finish, Scratch, CheckPage } from './session';
import { browserIdFromVersion, pageTargets } from './state';

type Session = {
  cdp: Cdp;
  version: CdpVersion;
  launched: boolean;
  fresh: boolean;
  skipped: number;
  page: PageHandle;
  state: SessionState;
};

const isLaunchOk = (launch: LaunchResult): launch is LaunchOk => 'cdp' in launch;

const pickAutoPort = async (deps: Deps): Promise<number> => {
  for (const port of autoPortRange()) {
    // Ports are probed in order so the lowest free one wins.

    if (!(await deps.browser.portBusy(port))) return port;
  }
  throw new ExitError(
    4,
    `no free port in ${AUTO_PORT_MIN}-${AUTO_PORT_MAX}; close browser windows opened by earlier tasks`,
  );
};

const locateEdge = (deps: Deps): { binary: string; profileDir: string } => {
  const edge: EdgeLocation = edgePaths({
    platform: deps.host.platform,
    env: deps.host.env,
    homedir: deps.host.homedir,
    exists: (file) => deps.files.exists(file),
  });
  if (!edge.binary || !deps.files.exists(edge.binary)) {
    throw new ExitError(2, 'Microsoft Edge not found (set EDGE_PATH)');
  }
  if (!edge.profileDir || !deps.files.exists(path.join(edge.profileDir, 'Default'))) {
    throw new ExitError(2, `Edge profile not found at ${edge.profileDir} (set EDGE_PROFILE_DIR)`);
  }
  return { binary: edge.binary, profileDir: edge.profileDir };
};

type Started = { launch: LaunchResult; fresh: boolean; skipped: number };

const startBrowser = async (
  deps: Deps,
  opts: OpenOptions,
  edge: { binary: string; profileDir: string },
  scratch: Scratch,
  port: number,
  reclone: boolean,
): Promise<Started> => {
  const fresh = reclone || !deps.files.exists(path.join(scratch.profileDir, 'Default'));
  const skippedNames = fresh ? deps.files.cloneProfile(edge.profileDir, scratch.profileDir) : [];
  if (skippedNames.length > 0) {
    deps.output.err(
      `WARNING: skipped ${skippedNames.length} locked profile file(s): ${skippedNames.join(', ')}\n`,
    );
  }
  deps.files.removeRestoreFiles(scratch.profileDir);
  const launch = await deps.browser.launch({
    binary: edge.binary,
    profileDir: scratch.profileDir,
    port,
    size: opts.size,
  });
  return { launch, fresh, skipped: skippedNames.length };
};

const launchSession = async (
  deps: Deps,
  opts: OpenOptions,
  edge: { binary: string; profileDir: string },
  scratch: Scratch,
  port: number,
  reclone: boolean,
): Promise<Session> => {
  let started = await startBrowser(deps, opts, edge, scratch, port, reclone);
  if (!isLaunchOk(started.launch) && started.launch.code === 3 && !started.fresh) {
    deps.output.err('Browser failed to open on the reused profile copy; re-creating it\n');
    started = await startBrowser(deps, opts, edge, scratch, port, true);
  }
  const { launch } = started;
  if (!isLaunchOk(launch)) throw new ExitError(launch.code, launch.message);
  const page = await attachPage(launch.cdp, launch.targetId);
  await closeOtherPages(launch.cdp, launch.targetId);
  const state: SessionState = {
    port,
    browserId: browserIdFromVersion(launch.version) ?? '',
    user: '',
    tabId: launch.targetId,
    baseline: [],
  };
  // Recorded before the SSO check so wait knows the port after a manual sign-in.
  deps.files.writeState(scratch.stateFile, state);
  return {
    cdp: launch.cdp,
    version: launch.version,
    launched: true,
    fresh: started.fresh,
    skipped: started.skipped,
    page,
    state,
  };
};

const reuseSession = async (
  deps: Deps,
  version: CdpVersion,
  previous: SessionState,
): Promise<Session> => {
  const cdp = await deps.browser.connect(version.webSocketDebuggerUrl ?? '');
  const targets = await getTargets(cdp);
  const baseline = previous.baseline ?? pageTargets(targets).map((target) => target.targetId);
  const targetId = await createBlankTab(cdp);
  return {
    cdp,
    version,
    launched: false,
    fresh: false,
    skipped: 0,
    page: await attachPage(cdp, targetId),
    state: { ...previous, tabId: targetId, baseline },
  };
};

const startSession = async (
  deps: Deps,
  opts: OpenOptions,
  edge: { binary: string; profileDir: string },
  scratch: Scratch,
): Promise<Session> => {
  const previous = deps.files.readState(scratch.stateFile);
  let version = await liveVersion(deps, previous);
  if (previous && version && opts.cdpPort !== undefined && opts.cdpPort !== previous.port) {
    deps.output.err(
      `Session ${opts.session} is open on port ${previous.port}; relaunching it on ${opts.cdpPort}\n`,
    );
    await deps.browser.close(version, previous.port);
    version = undefined;
  }
  if (previous && version) return reuseSession(deps, version, previous);

  const port = opts.cdpPort ?? (await pickAutoPort(deps));
  if (await deps.browser.portBusy(port)) {
    throw new ExitError(
      4,
      `port ${port} is already in use; use the skill's own metadata.cdp-port (agentme-edr-128 rule 05) or close the process holding it`,
    );
  }
  return launchSession(deps, opts, edge, scratch, port, false);
};

const signInOutcome = async (session: Session, hasCheckUrl: boolean): Promise<Finish> => ({
  result: hasCheckUrl ? 'sign-in-required' : 'sso-check-url-required',
  code: hasCheckUrl ? 10 : 11,
  user: 'none',
  info: await pageInfo(session.cdp, session.page),
  skipped: session.skipped,
});

// Retries the SSO check once on a fresh profile copy when the reused copy has no signed-in user.
const checkSso = async (
  deps: Deps,
  opts: OpenOptions,
  edge: { binary: string; profileDir: string },
  scratch: Scratch,
  session: Session,
  check: CheckPage,
): Promise<{ session: Session; user: string }> => {
  await navigate(session.cdp, session.page, check.url);
  let user = await waitForUser(
    session.cdp,
    session.page,
    check.host,
    opts.ssoWaitSeconds,
    deps.clock,
  );
  if (user || !session.launched || session.fresh) return { session, user };

  deps.output.err('SSO check failed on the reused profile copy; re-creating it\n');
  session.cdp.close();
  await deps.browser.close(session.version, session.state.port);
  const retried = await launchSession(deps, opts, edge, scratch, session.state.port, true);
  await navigate(retried.cdp, retried.page, check.url);
  user = await waitForUser(retried.cdp, retried.page, check.host, opts.ssoWaitSeconds, deps.clock);
  return { session: retried, user };
};

export const runOpen = async (deps: Deps, opts: OpenOptions): Promise<number> => {
  const edge = locateEdge(deps);
  const scratch = scratchFor(deps, opts.session);
  let session = await startSession(deps, opts, edge, scratch);
  const check = checkPageOf(opts.ssoCheckUrl);

  try {
    let user = '';
    if (!opts.skipSso) {
      ({ session, user } = await checkSso(deps, opts, edge, scratch, session, check));
      if (!user) {
        return finish(
          deps,
          scratch,
          session.state,
          await signInOutcome(session, Boolean(opts.ssoCheckUrl)),
        );
      }
    }

    const info = await openTarget(
      session.cdp,
      session.page,
      opts.url,
      {
        checkHost: opts.skipSso ? undefined : check.host,
        seconds: opts.ssoWaitSeconds,
        requireAuth: !opts.skipSso,
      },
      deps.clock,
    );
    if (session.launched) await closeOtherPages(session.cdp, session.page.targetId);
    if (opts.skipSso) {
      return finish(deps, scratch, session.state, {
        result: 'opened',
        code: 0,
        user: 'skipped',
        info,
        skipped: session.skipped,
      });
    }
    const authenticated = !info.onCheckPage && isAuthenticatedPage(info.title, info.url);
    return finish(deps, scratch, session.state, {
      result: authenticated ? 'authenticated' : 'sign-in-required',
      code: authenticated ? 0 : 10,
      user,
      info,
      skipped: session.skipped,
    });
  } finally {
    session.cdp.close();
  }
};
