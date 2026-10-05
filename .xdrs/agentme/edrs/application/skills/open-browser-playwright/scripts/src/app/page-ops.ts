import { RENAVIGATE_MS } from '../shared/constants';
import { swallow } from '../shared/errors';
import type { Cdp, CdpTarget, PageHandle, PageInfo } from '../shared/types';

import type { Clock } from './ports';
import { hostOf, isAuthenticatedPage, isLoaded, userExpression } from './pages';
import { pageTargets } from './state';

export const getTargets = async (cdp: Cdp): Promise<CdpTarget[]> => {
  const { targetInfos } = await cdp.send('Target.getTargets');
  return targetInfos as CdpTarget[];
};

export const createBlankTab = async (cdp: Cdp): Promise<string> => {
  const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
  return targetId as string;
};

export const attachPage = async (cdp: Cdp, targetId: string): Promise<PageHandle> => {
  const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
  return { targetId, sessionId: sessionId as string };
};

export const evaluate = async (
  cdp: Cdp,
  page: PageHandle,
  expression: string,
): Promise<unknown> => {
  try {
    const { result } = await cdp.send(
      'Runtime.evaluate',
      { expression, returnByValue: true },
      page.sessionId,
    );
    return result ? (result as { value?: unknown }).value : undefined;
  } catch {
    return undefined;
  }
};

export const pageInfo = async (cdp: Cdp, page: PageHandle): Promise<PageInfo> => {
  const value = await evaluate(cdp, page, '[document.title, location.href, document.readyState]');
  return Array.isArray(value)
    ? { title: String(value[0]), url: String(value[1]), ready: value[2] === 'complete' }
    : { title: '', url: '', ready: false };
};

export const navigate = async (cdp: Cdp, page: PageHandle, url: string): Promise<void> => {
  try {
    await cdp.send('Page.navigate', { url }, page.sessionId);
  } catch {
    // Retried by the caller's polling loop.
  }
};

export const closeOtherPages = async (cdp: Cdp, keepId: string): Promise<void> => {
  const targets = pageTargets(await getTargets(cdp));
  await Promise.all(
    targets
      .filter((target) => target.targetId !== keepId)
      .map(async (target) =>
        cdp.send('Target.closeTarget', { targetId: target.targetId }).catch(swallow),
      ),
  );
};

export const waitForUser = async (
  cdp: Cdp,
  page: PageHandle,
  checkHost: string,
  seconds: number,
  clock: Clock,
): Promise<string> => {
  const expression = userExpression(checkHost);
  const deadline = clock.now() + seconds * 1000;
  while (clock.now() < deadline) {
    // Sequential on purpose: each probe must finish before the next one starts.

    const user = await evaluate(cdp, page, expression);
    if (typeof user === 'string' && user) return user;

    await clock.sleep(1000);
  }
  return '';
};

export type OpenTargetOptions = {
  checkHost: string | undefined;
  seconds: number;
  requireAuth: boolean;
};

export type OpenedPage = PageInfo & { onCheckPage: boolean };

// A blocking navigation away from an SSO single-page app can be undone while it is still loading, so retry.
export const openTarget = async (
  cdp: Cdp,
  page: PageHandle,
  url: string,
  { checkHost, seconds, requireAuth }: OpenTargetOptions,
  clock: Clock,
): Promise<OpenedPage> => {
  await navigate(cdp, page, url);
  const targetHost = hostOf(url);
  const isCheckPage = (info: PageInfo): boolean =>
    Boolean(checkHost) && hostOf(info.url) === checkHost && targetHost !== checkHost;
  const deadline = clock.now() + seconds * 1000;
  let nextNavigation = clock.now() + RENAVIGATE_MS;
  await clock.sleep(1000);
  let info = await pageInfo(cdp, page);
  while (clock.now() < deadline) {
    if (isCheckPage(info)) {
      if (clock.now() >= nextNavigation) {
        await navigate(cdp, page, url);
        nextNavigation = clock.now() + RENAVIGATE_MS;
      }
    } else if (isLoaded(info) && (!requireAuth || isAuthenticatedPage(info.title, info.url))) {
      return { ...info, onCheckPage: false };
    }

    await clock.sleep(1000);

    info = await pageInfo(cdp, page);
  }
  return { ...info, onCheckPage: isCheckPage(info) };
};
