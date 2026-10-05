import fs from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';

import { browserConnector, cdpVersion, portBusy } from './browser';
import { FakeWebSocket, installFakeWebSocket } from './websocket_mock';

type Listening = { server: http.Server; port: number };

const listen = async (handler: http.RequestListener): Promise<Listening> =>
  new Promise((resolve) => {
    const server = http.createServer(handler);
    server.listen(0, '127.0.0.1', () => {
      resolve({ server, port: (server.address() as net.AddressInfo).port });
    });
  });

const stop = async (server: http.Server): Promise<void> =>
  new Promise((resolve) => {
    server.closeAllConnections();
    server.close(() => {
      resolve();
    });
  });

const freePort = async (): Promise<number> => {
  const { server, port } = await listen((_request, response) => {
    response.end();
  });
  await stop(server);
  return port;
};

const versionServer = async (): Promise<Listening> =>
  listen((request, response) => {
    response.setHeader('content-type', 'application/json');
    response.end(
      JSON.stringify({
        webSocketDebuggerUrl: `ws://127.0.0.1:${request.socket.localPort}/devtools/browser/X1`,
      }),
    );
  });

describe('cdpVersion and portBusy', () => {
  it('reads the version endpoint and detects busy ports', async () => {
    const { server, port } = await versionServer();
    await expect(cdpVersion(port)).resolves.toEqual({
      webSocketDebuggerUrl: `ws://127.0.0.1:${port}/devtools/browser/X1`,
    });
    await expect(portBusy(port)).resolves.toBe(true);
    await stop(server);
    await expect(cdpVersion(port)).resolves.toBeUndefined();
    await expect(portBusy(port)).resolves.toBe(false);
  });

  it('returns null when the endpoint answers with an error status', async () => {
    const { server, port } = await listen((_request, response) => {
      response.statusCode = 500;
      response.end('nope');
    });
    await expect(cdpVersion(port)).resolves.toBeUndefined();
    await stop(server);
  });
});

describe('browserConnector.launch', () => {
  let restore: () => void;
  let dir: string;

  beforeEach(() => {
    restore = installFakeWebSocket();
    dir = fs.mkdtempSync(path.join(os.tmpdir(), 'open-browser-launch-'));
  });

  afterEach(() => {
    restore();
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const request = (
    binary: string,
    port: number,
  ): Parameters<typeof browserConnector.launch>[0] => ({
    binary,
    profileDir: path.join(dir, 'profile'),
    port,
    size: { width: 800, height: 600 },
  });

  it('reports exit code 3 when the binary does not exist', async () => {
    const result = await browserConnector.launch(
      request(path.join(dir, 'missing'), await freePort()),
    );
    expect(result).toMatchObject({ code: 3 });
    expect((result as { message: string }).message).toContain('browser failed to open');
  });

  it('reports exit code 3 when the browser exits right away', async () => {
    const result = await browserConnector.launch(request(process.execPath, await freePort()));
    expect(result).toMatchObject({ code: 3 });
  });

  it('launches the browser and finds its own start tab by nonce', async () => {
    const script = path.join(dir, 'fake-browser.sh');
    const argsFile = path.join(dir, 'args.txt');
    fs.writeFileSync(script, `#!/bin/sh\nprintf '%s\\n' "$@" > '${argsFile}'\nexec sleep 5\n`, {
      mode: 0o700,
    });
    const { server, port } = await versionServer();
    FakeWebSocket.handler = (method) => {
      if (method !== 'Target.getTargets') return {};
      const lines = fs.existsSync(argsFile) ? fs.readFileSync(argsFile, 'utf8').split('\n') : [];
      const url = lines.find((line) => line.startsWith('data:text/html,opening#')) ?? '';
      return { targetInfos: url ? [{ targetId: 'N1', type: 'page', url }] : [] };
    };

    const result = await browserConnector.launch(request(script, port));
    await stop(server);

    expect(result).toMatchObject({ targetId: 'N1' });
    const args = fs.readFileSync(argsFile, 'utf8');
    expect(args).toContain(`--remote-debugging-port=${port}`);
    expect(args).toContain('--window-size=800,600');
    expect(args).toContain(`--user-data-dir=${path.join(dir, 'profile')}`);
  });
});

describe('browserConnector.close', () => {
  let restore: () => void;

  beforeEach(() => {
    restore = installFakeWebSocket();
  });

  afterEach(() => {
    restore();
  });

  it('asks the browser to close and waits until the endpoint is gone', async () => {
    const { server, port } = await versionServer();
    FakeWebSocket.handler = (method) => {
      if (method === 'Browser.close') {
        void stop(server);
      }
      return {};
    };
    const version = await cdpVersion(port);
    await browserConnector.close(version ?? {}, port);
    await expect(cdpVersion(port)).resolves.toBeUndefined();
  });

  it('ignores browsers that are already gone', async () => {
    FakeWebSocket.failConnect = true;
    await expect(
      browserConnector.close({ webSocketDebuggerUrl: 'ws://127.0.0.1:1/x' }, await freePort()),
    ).resolves.toBeUndefined();
  });
});
