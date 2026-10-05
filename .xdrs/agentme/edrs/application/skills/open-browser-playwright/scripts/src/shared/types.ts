export type CdpVersion = { webSocketDebuggerUrl?: string };

export type CdpTarget = { targetId: string; type: string; url: string; title?: string };

export type CdpResult = Record<string, unknown>;

export type Cdp = {
  send: (method: string, params?: object, sessionId?: string) => Promise<CdpResult>;
  close: () => void;
};

export type PageHandle = { targetId: string; sessionId: string };

export type PageInfo = { title: string; url: string; ready: boolean };

export type SessionState = {
  port: number;
  browserId: string;
  user: string;
  tabId?: string;
  baseline?: string[];
};

export type WindowSize = { width: number; height: number };

export type CommonOptions = {
  skipSso: boolean;
  ssoCheckUrl?: string;
  ssoWaitSeconds: number;
  cdpPort?: number;
};

export type OpenOptions = CommonOptions & {
  command: 'open';
  session: string;
  url: string;
  size: WindowSize;
};

export type WaitOptions = CommonOptions & {
  command: 'wait';
  session: string;
  url: string;
  waitSeconds: number;
};

export type TidyOptions = CommonOptions & { command: 'tidy'; session: string };

export type Options = OpenOptions | WaitOptions | TidyOptions;

export type EdgeLocation = { binary?: string; profileDir?: string };

export type ScratchPaths = { profileDir: string; stateFile: string };
