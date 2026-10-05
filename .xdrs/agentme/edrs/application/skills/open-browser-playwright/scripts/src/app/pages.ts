import type { PageInfo } from '../shared/types';

export const hostOf = (value: string): string => {
  try {
    return new URL(value).host;
  } catch {
    return '';
  }
};

const SIGN_IN_TITLE = /(^|[^a-z])sign[ -]?in([^a-z]|$)|^loading/i;
const IDP_URL =
  /login\.microsoftonline\.com|login\.live\.com|accounts\.google\.com|\/_signin|\/adfs\/|\/oauth2\/|msalredirect|^about:blank/i;

export const isAuthenticatedPage = (title: string, url: string): boolean => {
  if (!title) return false;
  return !SIGN_IN_TITLE.test(title) && !IDP_URL.test(url);
};

// Only counts an email found on the check page's own host, so login or account-picker pages never pass.
export const userExpression = (checkHost: string): string =>
  `(() => location.host === ${JSON.stringify(checkHost)} ? ` +
  '(((document.body && document.body.innerText) || "").match(/[\\w.+-]+@[\\w-]+(\\.[\\w-]+)+/) || [""])[0] : "")()';

export const isLoaded = (info: PageInfo): boolean =>
  info.ready && !/^(about:blank|data:)/.test(info.url);

export type TabCandidate = { targetId: string };

// Keeps baseline tabs and the task tab with the newest page load; closes the other task tabs.
export const selectTabsToClose = <T extends TabCandidate>(
  pages: T[],
  baseline: string[] | undefined,
  timeOrigins: Record<string, number | undefined>,
): { keep: T | undefined; close: string[] } => {
  const known = new Set(baseline ?? []);
  const taskTabs = pages.filter((page) => !known.has(page.targetId));
  const [first] = taskTabs;
  if (!first) return { keep: undefined, close: [] };
  let keep = first;
  for (const page of taskTabs) {
    const origin = timeOrigins[page.targetId];
    const best = timeOrigins[keep.targetId];
    if (
      Number.isFinite(origin) &&
      (!Number.isFinite(best) || (origin as number) > (best as number))
    ) {
      keep = page;
    }
  }
  return { keep, close: taskTabs.filter((page) => page !== keep).map((page) => page.targetId) };
};

export type ResultLines = {
  result: string;
  user: string;
  session: string;
  page?: { title?: string; url?: string };
  port: number;
};

export const formatResult = ({ result, user, session, page, port }: ResultLines): string =>
  [
    `RESULT: ${result}`,
    `USER: ${user}`,
    `SESSION: ${session}`,
    `PAGE: [${page?.title ?? ''}](${page?.url ?? ''})`,
    `CDP: http://127.0.0.1:${port}`,
  ].join('\n');
