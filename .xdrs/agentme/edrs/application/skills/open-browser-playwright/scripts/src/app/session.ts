import { DEFAULT_CHECK_URL } from '../shared/constants';
import type { Cdp, CdpVersion, PageInfo, ScratchPaths, SessionState } from '../shared/types';

import { scratchPaths } from './edge-paths';
import { formatResult, hostOf } from './pages';
import type { Deps } from './ports';
import { browserIdFromVersion } from './state';

export type Scratch = ScratchPaths & { session: string };

export type CheckPage = { url: string; host: string };

export type Finish = {
  result: string;
  code: number;
  user: string;
  info: Pick<PageInfo, 'title' | 'url'>;
  skipped: number;
};

export const scratchFor = (deps: Deps, session: string): Scratch => ({
  ...scratchPaths(deps.host.tmpdir, session),
  session,
});

export const checkPageOf = (ssoCheckUrl: string | undefined): CheckPage => {
  const url = ssoCheckUrl ?? DEFAULT_CHECK_URL;
  return { url, host: hostOf(url) };
};

// Writes the session state, prints the result lines and returns the exit code.
export const finish = (
  deps: Deps,
  scratch: Scratch,
  state: SessionState,
  outcome: Finish,
): number => {
  deps.files.writeState(scratch.stateFile, { ...state, user: outcome.user || state.user });
  deps.output.out(
    `${formatResult({
      result: outcome.result,
      user: outcome.user,
      session: scratch.session,
      page: outcome.info,
      port: state.port,
    })}\n`,
  );
  if ((outcome.code === 10 || outcome.code === 11) && outcome.skipped > 0) {
    deps.output.err('HINT: some locked profile files were not copied; close Edge and rerun\n');
  }
  return outcome.code;
};

// The recorded browser only counts as live when it answers with the same browser id.
export const liveVersion = async (
  deps: Deps,
  state: SessionState | undefined,
): Promise<CdpVersion | undefined> => {
  if (!state) return undefined;
  const version = await deps.browser.version(state.port);
  return version && browserIdFromVersion(version) === state.browserId ? version : undefined;
};

export type LiveConnection =
  | { scratch: Scratch; state?: undefined }
  | { scratch: Scratch; state: SessionState; version: CdpVersion; cdp: Cdp };

export const connectLive = async (deps: Deps, session: string): Promise<LiveConnection> => {
  const scratch = scratchFor(deps, session);
  const state = deps.files.readState(scratch.stateFile);
  const version = await liveVersion(deps, state);
  if (!state || !version) return { scratch, state: undefined };
  return {
    scratch,
    state,
    version,
    cdp: await deps.browser.connect(version.webSocketDebuggerUrl ?? ''),
  };
};
