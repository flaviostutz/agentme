import type { PageCall } from './page-call';
import type { BrowserPort, Deps, RunState } from './ports';

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  calls: string[];
  sleeps: number[];
  states: Map<string, RunState>;
  clockMs: { value: number };
};

type Options = {
  // Returns the JSON value for a page function by its name; called once per evalJson.
  page?: (call: PageCall) => unknown;
  openTab?: (url: string) => number;
  findTab?: (urlPart: string) => number | undefined;
  state?: Map<string, RunState>;
  startMs?: number;
};

export const createWorld = (options: Options = {}): World => {
  const clockMs = { value: options.startMs ?? 1_000_000 };
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    calls: [],
    sleeps: [],
    states: options.state ?? new Map(),
    clockMs,
  };
  const browser: BrowserPort = {
    ensureSession: async (): Promise<void> => {
      world.calls.push('ensureSession');
    },
    openTab: async (url): Promise<number> => {
      world.calls.push(`openTab ${url}`);
      return options.openTab ? options.openTab(url) : 1;
    },
    findTab: async (part): Promise<number | undefined> => {
      world.calls.push(`findTab ${part}`);
      return options.findTab ? options.findTab(part) : undefined;
    },
    selectTab: async (index): Promise<void> => {
      world.calls.push(`selectTab ${index}`);
    },
    closeTab: async (index): Promise<void> => {
      world.calls.push(`closeTab ${index}`);
    },
    evalJson: async (call): Promise<unknown> => {
      world.calls.push(`eval ${call.name}`);
      if (!options.page) throw new Error('unexpected page call');
      return options.page(call);
    },
    fillAndSubmit: async (selector, text): Promise<void> => {
      world.calls.push(`fill ${selector} ${text}`);
    },
  };
  world.deps = {
    browser,
    state: {
      read: async (runId): Promise<RunState | undefined> => world.states.get(runId),
      write: async (runId, state): Promise<void> => {
        world.states.set(runId, state);
      },
    },
    clock: {
      now: (): number => clockMs.value,
      sleep: async (ms): Promise<void> => {
        world.sleeps.push(ms);
        clockMs.value += ms;
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
  };
  return world;
};
