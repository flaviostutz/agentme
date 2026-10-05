import { ExitError } from '../shared/errors';
import type { WaitOptions } from '../shared/types';

import {
  attachPage,
  createBlankTab,
  getTargets,
  navigate,
  openTarget,
  pageInfo,
  waitForUser,
} from './page-ops';
import { hostOf, isAuthenticatedPage } from './pages';
import type { Deps } from './ports';
import { checkPageOf, connectLive, finish } from './session';
import { pageTargets } from './state';

// Continues a session after a manual sign-in: waits for the user, then opens the target page.
export const runWait = async (deps: Deps, opts: WaitOptions): Promise<number> => {
  const live = await connectLive(deps, opts.session);
  if (!live.state) {
    throw new ExitError(
      3,
      `no open browser for session ${opts.session}; run the open command first`,
    );
  }
  const { cdp, scratch } = live;
  let { state } = live;
  try {
    const targets = await getTargets(cdp);
    let tabId = pageTargets(targets).some((target) => target.targetId === state.tabId)
      ? state.tabId
      : undefined;
    if (!tabId) {
      tabId = await createBlankTab(cdp);
      state = { ...state, tabId };
    }
    const page = await attachPage(cdp, tabId);
    const check = checkPageOf(opts.ssoCheckUrl);
    const current = opts.ssoCheckUrl ? await pageInfo(cdp, page) : undefined;
    if (current && hostOf(current.url) !== check.host) {
      await navigate(cdp, page, check.url);
    }
    const user = await waitForUser(cdp, page, check.host, opts.waitSeconds, deps.clock);
    if (!user) {
      return finish(deps, scratch, state, {
        result: 'sign-in-required',
        code: 10,
        user: 'none',
        info: await pageInfo(cdp, page),
        skipped: 0,
      });
    }
    const info = await openTarget(
      cdp,
      page,
      opts.url,
      { checkHost: check.host, seconds: opts.ssoWaitSeconds, requireAuth: true },
      deps.clock,
    );
    const authenticated = !info.onCheckPage && isAuthenticatedPage(info.title, info.url);
    return finish(deps, scratch, state, {
      result: authenticated ? 'authenticated' : 'sign-in-required',
      code: authenticated ? 0 : 10,
      user,
      info,
      skipped: 0,
    });
  } finally {
    cdp.close();
  }
};
