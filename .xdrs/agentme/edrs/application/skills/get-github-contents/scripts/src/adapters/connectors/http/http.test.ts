import { createServer } from 'node:http';
import type { AddressInfo } from 'node:net';
import { mkdtempSync, readFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { filesConnector } from '../local-fs/files';

import { httpConnector } from './http';

describe('httpConnector', () => {
  it('does not follow redirects and returns the body only for 200 within the limit', async () => {
    const server = createServer((request, response) => {
      if (request.url === '/redirect') response.writeHead(302, { location: '/ok' }).end();
      else if (request.url === '/big')
        response.writeHead(200, { 'content-type': 'image/png' }).end(Buffer.alloc(50));
      else response.writeHead(200, { 'content-type': 'image/png' }).end('hello');
    });
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
    const base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
    try {
      const redirect = await httpConnector.get(`${base}/redirect`, 10);
      expect(redirect).toMatchObject({ status: 302, location: '/ok', bytes: undefined });
      const ok = await httpConnector.get(`${base}/ok`, 10);
      expect(ok.status).toBe(200);
      expect(Buffer.from(ok.bytes ?? []).toString()).toBe('hello');
      const big = await httpConnector.get(`${base}/big`, 10);
      expect(big.bytes).toBeUndefined();
    } finally {
      server.close();
    }
  });
});

describe('filesConnector', () => {
  it('creates folders and writes files', () => {
    const dir = path.join(mkdtempSync(path.join(os.tmpdir(), 'ghc-')), 'a', 'b');
    filesConnector.mkdirp(dir);
    filesConnector.write(path.join(dir, 'f.txt'), new TextEncoder().encode('x'));
    expect(readFileSync(path.join(dir, 'f.txt'), 'utf8')).toBe('x');
  });
});
