import { createServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { dnsConnector } from '../dns/dns';

import { httpConnector } from './http';

describe('httpConnector', () => {
  it('does not follow redirects, sends a user agent and limits the body', async () => {
    const server = createServer((request, response) => {
      if (request.url === '/redirect') response.writeHead(302, { location: '/ok' }).end();
      else if (request.url === '/big')
        response.writeHead(200, { 'content-type': 'text/html' }).end(Buffer.alloc(50));
      else
        response
          .writeHead(200, { 'content-type': 'text/plain' })
          .end(String(request.headers['user-agent']));
    });
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
    const base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
    try {
      const redirect = await httpConnector.get(`${base}/redirect`, 100);
      expect(redirect).toMatchObject({ status: 302, location: '/ok', bytes: undefined });
      const ok = await httpConnector.get(`${base}/ok`, 100);
      expect(Buffer.from(ok.bytes ?? []).toString()).toMatch(/agentme-get-web-contents/);
      expect(ok.contentType).toMatch(/text\/plain/);
      expect((await httpConnector.get(`${base}/big`, 10)).bytes).toBeUndefined();
    } finally {
      server.close();
    }
  });
});

describe('dnsConnector', () => {
  it('resolves localhost to loopback addresses', async () => {
    const addresses = await dnsConnector.lookup('localhost');
    expect(addresses.some((address) => address === '127.0.0.1' || address === '::1')).toBe(true);
  });
});
