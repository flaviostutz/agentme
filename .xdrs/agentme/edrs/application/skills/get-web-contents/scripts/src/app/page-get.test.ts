import { createWorld, html, redirect } from './world_mock';
import { readPage, runPageGet } from './page-get';
import type { PageResult } from './page-get';

const LONG = `<html><head><title>Story</title></head><body><h1>Title</h1><p>${'word '.repeat(80)}</p><a href="/next">n</a></body></html>`;
const parse = (stdout: string[]): PageResult => JSON.parse(stdout.join('')) as PageResult;

describe('readPage', () => {
  it('reads an HTML page into text, title and links', async () => {
    const world = createWorld({ http: () => html(LONG) });
    const result = await readPage('https://example.com/a', false, world.deps);
    expect(result).toMatchObject({
      status: 'ok',
      httpStatus: 200,
      title: 'Story',
      finalUrl: 'https://example.com/a',
      links: ['https://example.com/next'],
      truncated: false,
    });
    expect(result.text).toMatch(/^# Title/);
  });

  it('follows redirects hop by hop and reports the final url', async () => {
    const world = createWorld({
      http: (url) => (url === 'https://example.com/a' ? redirect('/b') : html(LONG)),
    });
    const result = await readPage('https://example.com/a', false, world.deps);
    expect(result).toMatchObject({ status: 'ok', finalUrl: 'https://example.com/b' });
    expect(world.httpCalls).toEqual(['https://example.com/a', 'https://example.com/b']);
  });

  it('blocks a redirect to a private address without contacting it', async () => {
    const world = createWorld({ http: () => redirect('http://169.254.169.254/latest/meta-data') });
    const result = await readPage('https://example.com/a', false, world.deps);
    expect(result.status).toBe('blocked');
    expect(world.httpCalls).toEqual(['https://example.com/a']);
  });

  it('blocks a private start url unless the human typed it, and still blocks redirects away from it', async () => {
    const dns = (host: string): string[] =>
      host === 'wiki.corp' ? ['10.0.0.9'] : ['93.184.216.34'];
    const blocked = createWorld({ http: () => html(LONG), dns });
    expect((await readPage('https://wiki.corp/x', false, blocked.deps)).status).toBe('blocked');
    expect(blocked.httpCalls).toEqual([]);

    const allowed = createWorld({ http: () => html(LONG), dns });
    expect((await readPage('https://wiki.corp/x', true, allowed.deps)).status).toBe('ok');

    const pivot = createWorld({ http: () => redirect('http://127.0.0.1/admin'), dns });
    expect((await readPage('https://wiki.corp/x', true, pivot.deps)).status).toBe('blocked');
  });

  it('detects login redirects, 401/403 and password forms', async () => {
    const toLogin = createWorld({ http: () => redirect('https://login.microsoftonline.com/x') });
    expect((await readPage('https://example.com/a', false, toLogin.deps)).status).toBe(
      'login-required',
    );
    const toPath = createWorld({ http: () => redirect('https://example.com/login?next=/a') });
    expect((await readPage('https://example.com/a', false, toPath.deps)).status).toBe(
      'login-required',
    );
    const forbidden = createWorld({ http: () => html('no', 403) });
    expect((await readPage('https://example.com/a', false, forbidden.deps)).status).toBe(
      'login-required',
    );
    const form = createWorld({
      http: () => html('<body><input type="password"><p>Sign in</p></body>'),
    });
    expect((await readPage('https://example.com/a', false, form.deps)).status).toBe(
      'login-required',
    );
  });

  it('keeps a login page as ok when the requested page is itself a login path', async () => {
    const world = createWorld({
      http: (url) => (url.endsWith('/login') ? redirect('/login/') : html(LONG)),
    });
    expect((await readPage('https://example.com/login', false, world.deps)).status).toBe('ok');
  });

  it('flags JavaScript-rendered shells as needing a browser', async () => {
    const shell = createWorld({
      http: () =>
        html('<html><body><div id="root"></div><script src="app.js"></script></body></html>'),
    });
    expect((await readPage('https://example.com/a', false, shell.deps)).status).toBe(
      'needs-browser',
    );
    const noscript = createWorld({
      http: () => html('<body><noscript>You need to enable JavaScript.</noscript><p>Hi</p></body>'),
    });
    expect((await readPage('https://example.com/a', false, noscript.deps)).status).toBe(
      'needs-browser',
    );
    const blank = createWorld({ http: () => html('<html><body>hi</body></html>') });
    expect((await readPage('https://example.com/a', false, blank.deps)).status).toBe(
      'needs-browser',
    );
  });

  it('accepts short static pages that have no scripts', async () => {
    const world = createWorld({
      http: () => html(`<html><body><p>${'short but static text. '.repeat(3)}</p></body></html>`),
    });
    expect((await readPage('https://example.com/a', false, world.deps)).status).toBe('ok');
  });

  it('reports 404, other statuses and network failures', async () => {
    const missing = createWorld({ http: () => html('', 404) });
    expect((await readPage('https://example.com/a', false, missing.deps)).status).toBe('not-found');
    const broken = createWorld({ http: () => html('', 500) });
    expect(await readPage('https://example.com/a', false, broken.deps)).toMatchObject({
      status: 'error',
      note: expect.stringMatching(/500/),
    });
    const down = createWorld({
      http: () => {
        throw new Error('ECONNREFUSED');
      },
    });
    expect(await readPage('https://example.com/a', false, down.deps)).toMatchObject({
      status: 'error',
      note: 'ECONNREFUSED',
    });
  });

  it('reports redirect loops and unsupported redirect targets', async () => {
    const loop = createWorld({ http: () => redirect('/again') });
    expect((await readPage('https://example.com/a', false, loop.deps)).note).toMatch(/redirects/);
    const bad = createWorld({ http: () => redirect('ftp://example.com/x') });
    expect((await readPage('https://example.com/a', false, bad.deps)).status).toBe('error');
    const noLocation = createWorld({ http: () => html('', 302) });
    expect((await readPage('https://example.com/a', false, noLocation.deps)).status).toBe('error');
  });

  it('returns plain text and json as is and marks binary or oversized bodies unreadable', async () => {
    const json = createWorld({ http: () => html('{"a":1}', 200, 'application/json') });
    expect(await readPage('https://example.com/a', false, json.deps)).toMatchObject({
      status: 'ok',
      text: '{"a":1}',
      title: null,
    });
    const pdf = createWorld({ http: () => html('%PDF', 200, 'application/pdf') });
    expect(await readPage('https://example.com/a', false, pdf.deps)).toMatchObject({
      status: 'unreadable',
      contentType: 'application/pdf',
      text: null,
    });
    const big = createWorld({
      http: () => ({
        status: 200,
        location: undefined,
        contentType: 'text/html',
        bytes: undefined,
      }),
    });
    expect((await readPage('https://example.com/a', false, big.deps)).status).toBe('unreadable');
  });

  it('truncates very long text', async () => {
    const text = 'x'.repeat(250_000);
    const world = createWorld({ http: () => html(text, 200, 'text/plain') });
    const result = await readPage('https://example.com/a', false, world.deps);
    expect(result.truncated).toBe(true);
    expect(result.text).toHaveLength(200_000);
  });
});

describe('runPageGet', () => {
  it('prints the JSON result and passes --allow-private on', async () => {
    const world = createWorld({ http: () => html(LONG), dns: () => ['10.0.0.1'] });
    expect(await runPageGet(['--url', 'https://wiki.corp/a', '--allow-private'], world.deps)).toBe(
      0,
    );
    expect(parse(world.stdout).status).toBe('ok');
  });

  it('requires a valid url', async () => {
    const world = createWorld();
    await expect(runPageGet([], world.deps)).rejects.toThrow(/Usage: page-get/);
    await expect(runPageGet(['--url', 'ftp://x'], world.deps)).rejects.toThrow(/http and https/);
  });
});
