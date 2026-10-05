import type { Cdp, CdpResult, CdpVersion, SessionState } from '../shared/types';

import { scratchPaths } from './edge-paths';
import type { Deps, LaunchRequest, LaunchResult } from './ports';

// Reusable in-memory world (browser tabs, files, clock, output) for the open, wait and tidy flows.

export const CHECK_HOST = 'myaccount.microsoft.com';
export const SIGNED_IN_USER = 'me@example.com';
export const EDGE_BINARY = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge';
export const EDGE_PROFILE = '/Users/me/Library/Application Support/Microsoft Edge';
export const TMPDIR = '/tmp';

export type FakeTab = { targetId: string; title: string; url: string; origin: number };

export type WorldOptions = {
  edgeInstalled?: boolean;
  profileExists?: boolean;
  signedInUser?: string;
  targetRequiresLogin?: boolean;
  lockedFiles?: string[];
  busyPorts?: number[];
  // Consumed in order by launch calls; later launches use the default fake browser.
  launchResults?: LaunchResult[];
  onLaunch?: (attempt: number) => void;
};

export type World = {
  deps: Deps;
  tabs: FakeTab[];
  paths: Set<string>;
  states: Map<string, SessionState>;
  versions: Map<number, CdpVersion>;
  busyPorts: Set<number>;
  signedInUser: string;
  stdout: string[];
  stderr: string[];
  launches: LaunchRequest[];
  closedBrowsers: number[];
  navigations: string[];
  closedTabs: string[];
  cdpClosed: number;
  cloned: string[];
  seedSession: (session: string, state: Partial<SessionState>, tabs?: FakeTab[]) => void;
  stateOf: (session: string) => SessionState | undefined;
};

const versionFor = (port: number, browserId: string): CdpVersion => ({
  webSocketDebuggerUrl: `ws://127.0.0.1:${port}/devtools/browser/${browserId}`,
});

const hostOfUrl = (url: string): string => {
  try {
    return new URL(url).host;
  } catch {
    return '';
  }
};

export const makeWorld = (options: WorldOptions = {}): World => {
  const tabs: FakeTab[] = [];
  const paths = new Set<string>();
  if (options.edgeInstalled !== false) paths.add(EDGE_BINARY);
  if (options.profileExists !== false) paths.add(`${EDGE_PROFILE}/Default`);
  const queuedLaunches = [...(options.launchResults ?? [])];
  let counter = 0;
  let now = 1_000_000;
  let launchAttempt = 0;

  const world: World = {
    deps: {} as Deps,
    tabs,
    paths,
    states: new Map(),
    versions: new Map(),
    busyPorts: new Set(options.busyPorts ?? []),
    signedInUser: options.signedInUser ?? SIGNED_IN_USER,
    stdout: [],
    stderr: [],
    launches: [],
    closedBrowsers: [],
    navigations: [],
    closedTabs: [],
    cdpClosed: 0,
    cloned: [],
    seedSession: (session, state, seededTabs = []): void => {
      const scratch = scratchPaths(TMPDIR, session);
      const full = { port: 9390, browserId: 'BID', user: '', ...state };
      world.states.set(scratch.stateFile, full);
      world.versions.set(full.port, versionFor(full.port, full.browserId));
      tabs.push(...seededTabs);
      paths.add(`${scratch.profileDir}/Default`);
    },
    stateOf: (session): SessionState | undefined =>
      world.states.get(scratchPaths(TMPDIR, session).stateFile),
  };

  const createTab = (url: string): FakeTab => {
    counter += 1;
    const tab = { targetId: `T${counter}`, title: '', url, origin: counter * 10 };
    tabs.push(tab);
    return tab;
  };

  const land = (tab: FakeTab, url: string): void => {
    if (hostOfUrl(url) === CHECK_HOST) {
      Object.assign(tab, {
        url,
        title: world.signedInUser ? 'My Account' : 'Sign in to your account',
      });
    } else if (options.targetRequiresLogin) {
      Object.assign(tab, { url: 'https://login.microsoftonline.com/common', title: 'Sign in' });
    } else {
      Object.assign(tab, { url, title: 'Target page' });
    }
  };

  const evaluate = (tab: FakeTab | undefined, expression: string): unknown => {
    if (expression.startsWith('[document.title')) return tab && [tab.title, tab.url, 'complete'];
    if (expression === 'performance.timeOrigin') return tab?.origin;
    return tab && hostOfUrl(tab.url) === CHECK_HOST ? world.signedInUser : '';
  };

  const send = (method: string, params: Record<string, unknown>, sessionId?: string): CdpResult => {
    const tab = tabs.find((candidate) => `S-${candidate.targetId}` === sessionId);
    switch (method) {
      case 'Target.getTargets': {
        return { targetInfos: tabs.map((item) => ({ ...item, type: 'page' })) };
      }
      case 'Target.createTarget': {
        return { targetId: createTab(String(params.url)).targetId };
      }
      case 'Target.attachToTarget': {
        return { sessionId: `S-${String(params.targetId)}` };
      }
      case 'Target.closeTarget': {
        world.closedTabs.push(String(params.targetId));
        tabs.splice(0, tabs.length, ...tabs.filter((item) => item.targetId !== params.targetId));
        return {};
      }
      case 'Page.navigate': {
        world.navigations.push(String(params.url));
        if (tab) land(tab, String(params.url));
        return {};
      }
      case 'Runtime.evaluate': {
        return { result: { value: evaluate(tab, String(params.expression)) } };
      }
      default: {
        return {};
      }
    }
  };

  const createCdp = (): Cdp => ({
    send: async (method, params = {}, sessionId = ''): Promise<CdpResult> =>
      send(method, params as Record<string, unknown>, sessionId),
    close: (): void => {
      world.cdpClosed += 1;
    },
  });

  world.deps = {
    browser: {
      version: async (port): Promise<CdpVersion | undefined> => world.versions.get(port),
      portBusy: async (port): Promise<boolean> =>
        world.busyPorts.has(port) || world.versions.has(port),
      launch: async (request): Promise<LaunchResult> => {
        launchAttempt += 1;
        world.launches.push(request);
        options.onLaunch?.(launchAttempt);
        const queued = queuedLaunches.shift();
        if (queued) return queued;
        tabs.splice(0, tabs.length);
        const own = createTab('data:text/html,opening');
        createTab('edge://newtab/');
        const version = versionFor(request.port, `BID${launchAttempt}`);
        world.versions.set(request.port, version);
        return { cdp: createCdp(), version, targetId: own.targetId };
      },
      close: async (_version, port): Promise<void> => {
        world.closedBrowsers.push(port);
        world.versions.delete(port);
      },
      connect: async (): Promise<Cdp> => createCdp(),
    },
    files: {
      exists: (file): boolean => paths.has(file),
      readState: (file): SessionState | undefined => world.states.get(file),
      writeState: (file, state): void => {
        world.states.set(file, state);
      },
      cloneProfile: (_real, copy): string[] => {
        world.cloned.push(copy);
        paths.add(`${copy}/Default`);
        return options.lockedFiles ?? [];
      },
      removeRestoreFiles: (): void => {
        // Nothing to remove in memory.
      },
    },
    clock: {
      now: (): number => now,
      sleep: async (ms): Promise<void> => {
        now += ms;
      },
    },
    output: {
      out: (text): void => {
        world.stdout.push(text);
      },
      err: (text): void => {
        world.stderr.push(text);
      },
    },
    host: { platform: 'darwin', env: {}, homedir: '/Users/me', tmpdir: TMPDIR },
  };
  return world;
};
