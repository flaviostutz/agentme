import type { PageCall } from './page-call';

export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

// Outbound connector for the browser opened by open-browser-playwright; it never launches or closes the browser.
export type BrowserPort = {
  // Attaches to the CDP endpoint when the session is not attached yet.
  ensureSession: () => Promise<void>;
  // Opens a new tab on the URL and returns its index.
  openTab: (url: string) => Promise<number>;
  // Returns the index of the first tab whose URL contains the text.
  findTab: (urlPart: string) => Promise<number | undefined>;
  selectTab: (index: number) => Promise<void>;
  closeTab: (index: number) => Promise<void>;
  // Runs a page function in the current tab and returns its JSON value.
  evalJson: (call: PageCall) => Promise<unknown>;
  // Types the text into the element and presses Enter.
  fillAndSubmit: (selector: string, text: string) => Promise<void>;
};

export type RunState = {
  searches: number;
  chatTurns: number;
  lastAt: number;
};

// Outbound connector for the per-run counter under .tmp/get-web-search-contents/<run-id>/.
export type StatePort = {
  read: (runId: string) => Promise<RunState | undefined>;
  write: (runId: string, state: RunState) => Promise<void>;
};

export type ClockPort = {
  now: () => number;
  sleep: (ms: number) => Promise<void>;
};

export type Deps = {
  browser: BrowserPort;
  state: StatePort;
  clock: ClockPort;
  output: Output;
};

// What a command needs from the outside; the browser is created after the arguments are parsed.
export type Wiring = {
  connect: (session: string, cdpPort: number) => BrowserPort;
  state: StatePort;
  clock: ClockPort;
  output: Output;
};
