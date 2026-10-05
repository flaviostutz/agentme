import type { OpenOptions } from '../shared/types';

import { scratchPaths } from './edge-paths';
import { runOpen } from './open';
import { EDGE_BINARY, SIGNED_IN_USER, TMPDIR, makeWorld } from './world_mock';
import type { World } from './world_mock';

const opts = (overrides: Partial<OpenOptions> = {}): OpenOptions => ({
  command: 'open',
  session: 's1',
  url: 'https://app.example.com/',
  size: { width: 1300, height: 900 },
  skipSso: false,
  ssoWaitSeconds: 5,
  ...overrides,
});

const stdoutOf = (world: World): string => world.stdout.join('');
const stderrOf = (world: World): string => world.stderr.join('');

describe('runOpen', () => {
  it('opens the page without SSO check when SKIP_SSO is set', async () => {
    const world = makeWorld();
    const code = await runOpen(world.deps, opts({ skipSso: true }));
    expect(code).toBe(0);
    expect(stdoutOf(world)).toContain('RESULT: opened\nUSER: skipped\nSESSION: s1\n');
    expect(stdoutOf(world)).toContain('PAGE: [Target page](https://app.example.com/)');
    expect(stdoutOf(world)).toContain('CDP: http://127.0.0.1:9390');
    expect(world.launches[0]).toMatchObject({ binary: EDGE_BINARY, port: 9390 });
    expect(world.cloned).toHaveLength(1);
    expect(world.cdpClosed).toBe(1);
    expect(world.stateOf('s1')).toMatchObject({ port: 9390, user: 'skipped' });
  });

  it('authenticates through the SSO check page', async () => {
    const world = makeWorld();
    const code = await runOpen(world.deps, opts());
    expect(code).toBe(0);
    expect(stdoutOf(world)).toContain('RESULT: authenticated');
    expect(stdoutOf(world)).toContain(`USER: ${SIGNED_IN_USER}`);
    expect(world.stateOf('s1')?.user).toBe(SIGNED_IN_USER);
    expect(world.closedTabs).toContain('T2');
  });

  it('exits 10 when the check page shows nobody signed in', async () => {
    const world = makeWorld({ signedInUser: '', lockedFiles: ['Cookies'] });
    const code = await runOpen(
      world.deps,
      opts({ ssoCheckUrl: 'https://myaccount.microsoft.com/me' }),
    );
    expect(code).toBe(10);
    expect(stdoutOf(world)).toContain('RESULT: sign-in-required\nUSER: none');
    expect(stderrOf(world)).toContain('WARNING: skipped 1 locked profile file(s): Cookies');
    expect(stderrOf(world)).toContain('HINT: some locked profile files were not copied');
  });

  it('exits 11 when nobody is signed in and no SSO_CHECK_URL was given', async () => {
    const world = makeWorld({ signedInUser: '' });
    const code = await runOpen(world.deps, opts());
    expect(code).toBe(11);
    expect(stdoutOf(world)).toContain('RESULT: sso-check-url-required');
  });

  it('exits 10 when the target page redirects to a login page', async () => {
    const world = makeWorld({ targetRequiresLogin: true });
    const code = await runOpen(world.deps, opts());
    expect(code).toBe(10);
    expect(stdoutOf(world)).toContain(`RESULT: sign-in-required\nUSER: ${SIGNED_IN_USER}`);
  });

  it('retries the SSO check on a fresh profile copy when the reused copy is signed out', async () => {
    let world!: World;
    world = makeWorld({
      signedInUser: '',
      onLaunch: (attempt) => {
        if (attempt === 2) world.signedInUser = SIGNED_IN_USER;
      },
    });
    world.paths.add(`${scratchPaths(TMPDIR, 's1').profileDir}/Default`);
    const code = await runOpen(world.deps, opts());
    expect(code).toBe(0);
    expect(world.launches).toHaveLength(2);
    expect(world.closedBrowsers).toEqual([9390]);
    expect(world.cloned).toHaveLength(1);
    expect(stderrOf(world)).toContain('SSO check failed on the reused profile copy');
  });

  it('re-creates the profile copy when the browser fails to open on a reused copy', async () => {
    const world = makeWorld({
      launchResults: [{ code: 3, message: 'browser failed to open' }],
    });
    world.paths.add(`${scratchPaths(TMPDIR, 's1').profileDir}/Default`);
    const code = await runOpen(world.deps, opts({ skipSso: true }));
    expect(code).toBe(0);
    expect(world.launches).toHaveLength(2);
    expect(stderrOf(world)).toContain('re-creating it');
  });

  it('reuses a live session and opens a new tab', async () => {
    const world = makeWorld();
    world.seedSession('s1', { port: 9392, browserId: 'BID', baseline: ['B1'] }, [
      { targetId: 'B1', title: 'Home', url: 'https://home.example.com/', origin: 1 },
    ]);
    const code = await runOpen(world.deps, opts({ skipSso: true }));
    expect(code).toBe(0);
    expect(world.launches).toHaveLength(0);
    expect(stdoutOf(world)).toContain('CDP: http://127.0.0.1:9392');
    expect(world.stateOf('s1')?.baseline).toEqual(['B1']);
  });

  it('relaunches on the requested port when the live session uses another one', async () => {
    const world = makeWorld();
    world.seedSession('s1', { port: 9390 });
    const code = await runOpen(world.deps, opts({ skipSso: true, cdpPort: 9250 }));
    expect(code).toBe(0);
    expect(world.closedBrowsers).toEqual([9390]);
    expect(world.launches[0]?.port).toBe(9250);
    expect(stderrOf(world)).toContain('relaunching it on 9250');
  });

  it('picks the next free automatic port', async () => {
    const world = makeWorld({ busyPorts: [9390, 9391] });
    await runOpen(world.deps, opts({ skipSso: true }));
    expect(world.launches[0]?.port).toBe(9392);
  });

  it('fails with code 4 when every automatic port is busy', async () => {
    const world = makeWorld({
      busyPorts: Array.from({ length: 10 }, (_item, index) => 9390 + index),
    });
    await expect(runOpen(world.deps, opts())).rejects.toMatchObject({ code: 4 });
  });

  it('fails with code 4 when the requested port is busy', async () => {
    const world = makeWorld({ busyPorts: [9250] });
    await expect(runOpen(world.deps, opts({ cdpPort: 9250 }))).rejects.toMatchObject({ code: 4 });
  });

  it('fails with code 2 when Edge or its profile is missing', async () => {
    await expect(runOpen(makeWorld({ edgeInstalled: false }).deps, opts())).rejects.toMatchObject({
      code: 2,
      message: expect.stringContaining('Microsoft Edge not found'),
    });
    await expect(runOpen(makeWorld({ profileExists: false }).deps, opts())).rejects.toMatchObject({
      code: 2,
      message: expect.stringContaining('Edge profile not found'),
    });
  });

  it('propagates launch failures with their exit code', async () => {
    const world = makeWorld({
      launchResults: [{ code: 5, message: 'CDP endpoint did not respond' }],
    });
    await expect(runOpen(world.deps, opts())).rejects.toMatchObject({ code: 5 });
  });
});
