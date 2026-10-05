import crypto from 'node:crypto';
import net from 'node:net';
import { spawn } from 'node:child_process';

import { findNonceTarget, nonceStartUrl } from '../../../app/state';
import type { BrowserPort, LaunchRequest, LaunchResult } from '../../../app/ports';
import { CDP_STARTUP_MS } from '../../../shared/constants';
import { swallow } from '../../../shared/errors';
import type { Cdp, CdpTarget, CdpVersion } from '../../../shared/types';

import { connectCdp } from './client';

const sleep = async (ms: number): Promise<void> =>
  new Promise((resolve) => {
    setTimeout(resolve, ms);
  });

export const cdpVersion = async (port: number): Promise<CdpVersion | undefined> => {
  try {
    const response = await fetch(`http://127.0.0.1:${port}/json/version`, {
      signal: AbortSignal.timeout(2000),
    });
    return response.ok ? ((await response.json()) as CdpVersion) : undefined;
  } catch {
    return undefined;
  }
};

export const portBusy = async (port: number): Promise<boolean> =>
  new Promise((resolve) => {
    const socket = net.createConnection({ host: '127.0.0.1', port });
    socket.setTimeout(1000, () => {
      socket.destroy();
      resolve(false);
    });
    socket.once('connect', () => {
      socket.destroy();
      resolve(true);
    });
    socket.once('error', () => {
      resolve(false);
    });
  });

type Spawned = { kill: () => void; exited: () => string | undefined };

const spawnBrowser = (binary: string, args: string[]): Spawned => {
  let exited: string | undefined;
  const child = spawn(binary, args, { detached: true, stdio: 'ignore' });
  child.once('error', (error) => {
    exited = error.message;
  });
  child.once('exit', (code) => {
    exited ??= `browser exited with code ${code}`;
  });
  child.unref();
  return {
    kill: (): void => {
      child.kill();
    },
    exited: (): string | undefined => exited,
  };
};

const waitForVersion = async (port: number, child: Spawned): Promise<CdpVersion | undefined> => {
  const deadline = Date.now() + CDP_STARTUP_MS;
  let version: CdpVersion | undefined;
  while (!version && !child.exited() && Date.now() < deadline) {
    version = await cdpVersion(port);

    if (!version) await sleep(500);
  }
  return version;
};

// CDP can answer before the first tab exists.
const waitForNonceTab = async (cdp: Cdp, nonce: string): Promise<CdpTarget | undefined> => {
  const deadline = Date.now() + 5000;
  while (Date.now() < deadline) {
    const { targetInfos } = await cdp.send('Target.getTargets');
    const own = findNonceTarget(targetInfos as CdpTarget[], nonce);
    if (own) return own;

    await sleep(250);
  }
  return undefined;
};

const launch = async ({ binary, profileDir, port, size }: LaunchRequest): Promise<LaunchResult> => {
  const nonce = crypto.randomBytes(12).toString('hex');
  const child = spawnBrowser(binary, [
    `--user-data-dir=${profileDir}`,
    `--remote-debugging-port=${port}`,
    '--no-first-run',
    '--no-default-browser-check',
    `--window-size=${size.width},${size.height}`,
    '--window-position=100,100',
    nonceStartUrl(nonce),
  ]);

  const version = await waitForVersion(port, child);
  if (!version) {
    const reason = child.exited();
    if (reason) return { code: 3, message: `browser failed to open: ${reason}` };
    child.kill();
    return {
      code: 5,
      message: `CDP endpoint http://127.0.0.1:${port} did not respond after launch`,
    };
  }
  const cdp = await connectCdp(version.webSocketDebuggerUrl ?? '');
  const own = await waitForNonceTab(cdp, nonce);
  if (!own) {
    cdp.close();
    child.kill();
    return {
      code: 4,
      message: `port ${port} is held by another browser (agentme-edr-128 rule 05)`,
    };
  }
  return { cdp, version, targetId: own.targetId };
};

const closeBrowser = async (version: CdpVersion, port: number): Promise<void> => {
  try {
    const cdp = await connectCdp(version.webSocketDebuggerUrl ?? '');
    await cdp.send('Browser.close').catch(swallow);
    cdp.close();
  } catch {
    // Already gone.
  }
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline && (await cdpVersion(port))) {
    await sleep(500);
  }
};

export const browserConnector: BrowserPort = {
  version: cdpVersion,
  portBusy,
  launch,
  close: closeBrowser,
  connect: connectCdp,
};
