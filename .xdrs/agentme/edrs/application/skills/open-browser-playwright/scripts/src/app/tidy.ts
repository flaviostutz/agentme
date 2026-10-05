import { swallow } from '../shared/errors';
import type { CdpTarget, TidyOptions } from '../shared/types';

import { attachPage, evaluate, getTargets } from './page-ops';
import { selectTabsToClose } from './pages';
import type { Deps } from './ports';
import { connectLive } from './session';
import { pageTargets } from './state';

// Closes leftover task tabs of a session, keeping baseline tabs and the newest task tab.
export const runTidy = async (deps: Deps, opts: TidyOptions): Promise<number> => {
  const live = await connectLive(deps, opts.session);
  if (!live.state) {
    deps.output.out(`RESULT: no-session\nSESSION: ${opts.session}\n`);
    return 0;
  }
  const { cdp, scratch, state } = live;
  try {
    const pages: CdpTarget[] = pageTargets(await getTargets(cdp));
    const known = new Set(state.baseline ?? []);
    const timeOrigins: Record<string, number | undefined> = {};
    for (const target of pages.filter((candidate) => !known.has(candidate.targetId))) {
      // Sequential: one attach and detach per tab keeps the CDP session count low.
      const page = await attachPage(cdp, target.targetId);
      const origin = await evaluate(cdp, page, 'performance.timeOrigin');
      timeOrigins[target.targetId] = typeof origin === 'number' ? origin : undefined;
      await cdp.send('Target.detachFromTarget', { sessionId: page.sessionId }).catch(swallow);
    }
    const { keep, close } = selectTabsToClose(pages, state.baseline, timeOrigins);
    await Promise.all(
      close.map(async (targetId) => cdp.send('Target.closeTarget', { targetId }).catch(swallow)),
    );
    deps.files.writeState(scratch.stateFile, {
      ...state,
      tabId: keep ? keep.targetId : state.tabId,
      baseline: undefined,
    });
    deps.output.out(
      `${[
        'RESULT: tidied',
        `SESSION: ${opts.session}`,
        `PAGE: [${keep?.title ?? ''}](${keep?.url ?? ''})`,
        `CLOSED: ${close.length}`,
        `CDP: http://127.0.0.1:${state.port}`,
      ].join('\n')}\n`,
    );
    return 0;
  } finally {
    cdp.close();
  }
};
