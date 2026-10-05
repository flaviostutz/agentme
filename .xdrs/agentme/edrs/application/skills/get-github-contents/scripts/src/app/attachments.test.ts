import { downloadAssets } from './attachments';
import { createWorld, okBytes } from './world_mock';

const asset = (name: string, url: string): { name: string; url: string } => ({ name, url });
const ASSET_URL = 'https://github.com/user-attachments/assets/abc';

describe('downloadAssets', () => {
  it('saves the file and adds an extension from the content type', async () => {
    const world = createWorld({ http: () => okBytes('png-bytes', 'image/png') });
    const results = await downloadAssets([asset('mock', ASSET_URL)], '.tmp/x', world.deps);
    expect(results).toEqual([{ name: 'mock', url: ASSET_URL, path: '.tmp/x/1-mock.png' }]);
    expect(world.files.has('.tmp/x/1-mock.png')).toBe(true);
  });

  it('follows redirects between allowed hosts without sending credentials', async () => {
    const world = createWorld({
      http: (url) =>
        url === ASSET_URL
          ? {
              status: 302,
              location: 'https://objects.githubusercontent.com/f/1',
              contentType: undefined,
              bytes: undefined,
            }
          : okBytes('ok', 'application/pdf'),
    });
    const results = await downloadAssets([asset('spec.pdf', ASSET_URL)], '.tmp/x', world.deps);
    expect(results[0]).toMatchObject({ path: '.tmp/x/1-spec.pdf' });
    expect(world.httpCalls).toEqual([ASSET_URL, 'https://objects.githubusercontent.com/f/1']);
  });

  it('refuses a redirect to a host outside the allowlist (security)', async () => {
    const world = createWorld({
      http: () => ({
        status: 302,
        location: 'http://169.254.169.254/latest',
        contentType: undefined,
        bytes: undefined,
      }),
    });
    const results = await downloadAssets([asset('a', ASSET_URL)], '.tmp/x', world.deps);
    expect(results[0]).toMatchObject({ error: expect.stringContaining('host not allowed') });
    expect(world.httpCalls).toEqual([ASSET_URL]);
  });

  it('reports HTTP failures, oversize files and redirect loops per file', async () => {
    const statuses: Record<string, ReturnType<typeof okBytes>> = {
      'https://github.com/user-attachments/assets/403': {
        status: 403,
        location: undefined,
        contentType: undefined,
        bytes: undefined,
      },
      'https://github.com/user-attachments/assets/big': {
        status: 200,
        location: undefined,
        contentType: undefined,
        bytes: undefined,
      },
      'https://github.com/user-attachments/assets/loop': {
        status: 302,
        location: 'https://github.com/user-attachments/assets/loop',
        contentType: undefined,
        bytes: undefined,
      },
    };
    const world = createWorld({ http: (url) => statuses[url] ?? okBytes('x') });
    const results = await downloadAssets(
      [
        asset('forbidden', 'https://github.com/user-attachments/assets/403'),
        asset('big', 'https://github.com/user-attachments/assets/big'),
        asset('loop', 'https://github.com/user-attachments/assets/loop'),
      ],
      '.tmp/x',
      world.deps,
    );
    expect(results.map((result) => ('error' in result ? result.error : ''))).toEqual([
      'download failed (HTTP 403)',
      'file is larger than 10 MB',
      'too many redirects',
    ]);
  });

  it('turns a thrown network error into a per-file error and caps the file count', async () => {
    const world = createWorld({
      http: () => {
        throw new Error('network down');
      },
    });
    const many = Array.from({ length: 21 }, (_, index) =>
      asset(`f${index}`, `https://github.com/user-attachments/assets/${index}`),
    );
    const results = await downloadAssets(many, '.tmp/x', world.deps);
    expect(results[0]).toMatchObject({ error: 'network down' });
    expect(results[20]).toMatchObject({ error: expect.stringContaining('more than 20') });
  });
});
