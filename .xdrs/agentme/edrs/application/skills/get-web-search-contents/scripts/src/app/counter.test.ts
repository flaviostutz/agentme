import { currentBudget, reserveSearch } from './counter';
import { createWorld } from './world_mock';

describe('reserveSearch', () => {
  it('counts searches per run and refuses past the cap', async () => {
    const world = createWorld();
    const first = await reserveSearch(world.deps, 'run-a', 2, 'search');
    const second = await reserveSearch(world.deps, 'run-a', 2, 'chat');
    const third = await reserveSearch(world.deps, 'run-a', 2, 'search');
    expect(first).toEqual({ allowed: true, budget: { used: 1, max: 2 } });
    expect(second.budget).toEqual({ used: 2, max: 2 });
    expect(third).toEqual({ allowed: false, budget: { used: 2, max: 2 } });
    expect(world.states.get('run-a')?.chatTurns).toBe(1);
    expect(await currentBudget(world.deps, 'run-b', 5)).toEqual({ used: 0, max: 5 });
  });

  it('spaces consecutive searches by the pacing delay and does not wait for the first', async () => {
    const world = createWorld();
    await reserveSearch(world.deps, 'run-a', 5, 'search');
    expect(world.sleeps).toEqual([]);
    await reserveSearch(world.deps, 'run-a', 5, 'search');
    expect(world.sleeps).toEqual([3000]);
  });
});
