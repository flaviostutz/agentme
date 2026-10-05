import type { WaitOptions } from '../shared/types';

import { runWait } from './wait';
import { SIGNED_IN_USER, makeWorld } from './world_mock';

const opts = (overrides: Partial<WaitOptions> = {}): WaitOptions => ({
  command: 'wait',
  session: 's1',
  url: 'https://app.example.com/',
  waitSeconds: 5,
  skipSso: false,
  ssoWaitSeconds: 5,
  ...overrides,
});

const tab = (
  targetId: string,
  url: string,
): { targetId: string; title: string; url: string; origin: number } => ({
  targetId,
  title: 'x',
  url,
  origin: 1,
});

describe('runWait', () => {
  it('fails with code 3 when the session has no open browser', async () => {
    const world = makeWorld();
    await expect(runWait(world.deps, opts())).rejects.toMatchObject({ code: 3 });
  });

  it('continues in the recorded tab once the user signed in', async () => {
    const world = makeWorld();
    world.seedSession('s1', { tabId: 'T1' }, [tab('T1', 'https://myaccount.microsoft.com/')]);
    const code = await runWait(world.deps, opts());
    expect(code).toBe(0);
    expect(world.stdout.join('')).toContain(`RESULT: authenticated\nUSER: ${SIGNED_IN_USER}`);
    expect(world.cdpClosed).toBe(1);
  });

  it('opens a new tab when the recorded one is gone and navigates to the check page', async () => {
    const world = makeWorld();
    world.seedSession('s1', { tabId: 'GONE' }, [tab('T1', 'https://home.example.com/')]);
    const code = await runWait(
      world.deps,
      opts({ ssoCheckUrl: 'https://myaccount.microsoft.com/me' }),
    );
    expect(code).toBe(0);
    expect(world.navigations[0]).toBe('https://myaccount.microsoft.com/me');
    expect(world.stateOf('s1')?.tabId).not.toBe('GONE');
  });

  it('exits 10 when nobody signs in before the deadline', async () => {
    const world = makeWorld({ signedInUser: '' });
    world.seedSession('s1', { tabId: 'T1' }, [tab('T1', 'https://myaccount.microsoft.com/')]);
    const code = await runWait(world.deps, opts({ waitSeconds: 3 }));
    expect(code).toBe(10);
    expect(world.stdout.join('')).toContain('RESULT: sign-in-required\nUSER: none');
  });

  it('exits 10 when the target page still asks for sign-in', async () => {
    const world = makeWorld({ targetRequiresLogin: true });
    world.seedSession('s1', { tabId: 'T1' }, [tab('T1', 'https://myaccount.microsoft.com/')]);
    expect(await runWait(world.deps, opts())).toBe(10);
  });
});
