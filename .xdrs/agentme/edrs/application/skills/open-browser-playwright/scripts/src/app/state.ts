import type { CdpTarget, CdpVersion, SessionState } from '../shared/types';

export const parseState = (text: string): SessionState | undefined => {
  try {
    const state: unknown = JSON.parse(text);
    if (!state || typeof state !== 'object') return undefined;
    const { port, browserId, user, tabId, baseline } = state as Record<string, unknown>;
    if (!Number.isInteger(port) || typeof browserId !== 'string') return undefined;
    return {
      port: port as number,
      browserId,
      user: typeof user === 'string' ? user : '',
      tabId: typeof tabId === 'string' ? tabId : undefined,
      baseline: Array.isArray(baseline)
        ? baseline.filter((id): id is string => typeof id === 'string')
        : undefined,
    };
  } catch {
    return undefined;
  }
};

export const serializeState = (
  state: Partial<SessionState> & { port: number; browserId: string },
): string =>
  `${JSON.stringify({
    port: state.port,
    browserId: state.browserId,
    user: state.user ?? '',
    tabId: state.tabId,
    baseline: state.baseline,
  })}\n`;

export const browserIdFromVersion = (version: CdpVersion | undefined): string | undefined => {
  const wsUrl = version?.webSocketDebuggerUrl;
  const match =
    typeof wsUrl === 'string' ? /\/devtools\/browser\/([\dA-Za-z-]+)$/.exec(wsUrl) : undefined;
  return match?.[1];
};

// Edge swaps an about:blank start URL for its new tab page, so the nonce rides on a data: URL.
export const nonceStartUrl = (nonce: string): string => `data:text/html,opening#${nonce}`;

// The first page carries a random nonce, so a browser answering on the port proves it is ours.
export const findNonceTarget = (targets: CdpTarget[], nonce: string): CdpTarget | undefined =>
  targets.find((target) => target.type === 'page' && String(target.url).endsWith(`#${nonce}`));

export const pageTargets = (targets: CdpTarget[]): CdpTarget[] =>
  targets.filter((target) => target.type === 'page');
