import type { Cdp, CdpVersion, SessionState, WindowSize } from '../shared/types';

export type Clock = {
  now: () => number;
  sleep: (ms: number) => Promise<void>;
};

export type LaunchRequest = {
  binary: string;
  profileDir: string;
  port: number;
  size: WindowSize;
};

export type LaunchOk = { cdp: Cdp; version: CdpVersion; targetId: string };

export type LaunchFailure = { code: number; message: string };

export type LaunchResult = LaunchOk | LaunchFailure;

// Outbound connector to a Chromium-based browser reachable over the DevTools protocol.
export type BrowserPort = {
  version: (port: number) => Promise<CdpVersion | undefined>;
  portBusy: (port: number) => Promise<boolean>;
  launch: (request: LaunchRequest) => Promise<LaunchResult>;
  close: (version: CdpVersion, port: number) => Promise<void>;
  connect: (wsUrl: string) => Promise<Cdp>;
};

// Outbound connector to the local filesystem: profile copies and session state files.
export type FilesPort = {
  exists: (file: string) => boolean;
  readState: (file: string) => SessionState | undefined;
  writeState: (file: string, state: SessionState) => void;
  cloneProfile: (realProfile: string, profileCopy: string) => string[];
  removeRestoreFiles: (profileCopy: string) => void;
};

export type Host = {
  platform: string;
  env: Record<string, string | undefined>;
  homedir: string;
  tmpdir: string;
};

export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

export type Deps = {
  browser: BrowserPort;
  files: FilesPort;
  clock: Clock;
  output: Output;
  host: Host;
};
