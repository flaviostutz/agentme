import type { TidyOptions } from '../shared/types';

import { runTidy } from './tidy';
import { makeWorld } from './world_mock';

const opts: TidyOptions = {
  command: 'tidy',
  session: 's1',
  skipSso: false,
  ssoWaitSeconds: 5,
};

describe('runTidy', () => {
  it('reports no-session for an unknown session', async () => {
    const world = makeWorld();
    expect(await runTidy(world.deps, opts)).toBe(0);
    expect(world.stdout.join('')).toBe('RESULT: no-session\nSESSION: s1\n');
  });

  it('closes older task tabs and keeps baseline tabs and the newest task tab', async () => {
    const world = makeWorld();
    world.seedSession('s1', { tabId: 'T1', baseline: ['B1'] }, [
      { targetId: 'B1', title: 'Home', url: 'https://home.example.com/', origin: 1 },
      { targetId: 'T1', title: 'Old', url: 'https://old.example.com/', origin: 10 },
      { targetId: 'T2', title: 'New', url: 'https://new.example.com/', origin: 30 },
    ]);
    expect(await runTidy(world.deps, opts)).toBe(0);
    expect(world.closedTabs).toEqual(['T1']);
    expect(world.stdout.join('')).toBe(
      [
        'RESULT: tidied',
        'SESSION: s1',
        'PAGE: [New](https://new.example.com/)',
        'CLOSED: 1',
        'CDP: http://127.0.0.1:9390',
      ].join('\n') + '\n',
    );
    expect(world.stateOf('s1')).toMatchObject({ tabId: 'T2' });
    expect(world.stateOf('s1')?.baseline).toBeUndefined();
    expect(world.cdpClosed).toBe(1);
  });

  it('keeps the recorded tab when there are no task tabs', async () => {
    const world = makeWorld();
    world.seedSession('s1', { tabId: 'B1', baseline: ['B1'] }, [
      { targetId: 'B1', title: 'Home', url: 'https://home.example.com/', origin: 1 },
    ]);
    expect(await runTidy(world.deps, opts)).toBe(0);
    expect(world.stdout.join('')).toContain('PAGE: [](');
    expect(world.stdout.join('')).toContain('CLOSED: 0');
    expect(world.stateOf('s1')?.tabId).toBe('B1');
  });
});
