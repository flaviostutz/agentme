import { readItems, requireFields, runBatch, runBatchCommand } from './batch';
import { createWorld } from './world_mock';

describe('readItems', () => {
  it('reads the items array from the input connector', () => {
    expect(readItems([], createWorld({ input: '[{"a":1}]' }).deps)).toEqual([{ a: 1 }]);
  });

  it('passes --input to the connector and rejects invalid input with exit 2', () => {
    const world = createWorld();
    const read = jest.spyOn(world.deps.input, 'read').mockReturnValue('[]');
    readItems(['--input', 'f.json'], world.deps);
    expect(read).toHaveBeenCalledWith('f.json');
    expect(() => readItems([], createWorld({ input: '{' }).deps)).toThrow(/not valid JSON/);
    expect(() => readItems([], createWorld({ input: '{}' }).deps)).toThrow(/JSON array/);
  });
});

describe('requireFields', () => {
  it('returns the fields and names the missing ones', () => {
    expect(requireFields({ a: 'x', b: 'y' }, ['a', 'b'])).toEqual({ a: 'x', b: 'y' });
    expect(() => requireFields({ a: 'x', b: '' }, ['a', 'b', 'c'])).toThrow(/b, c/);
    expect(() => requireFields(null as never, ['a'])).toThrow(/a/);
  });
});

describe('runBatch', () => {
  it('isolates failures, keeps the index and surfaces the gh stderr', () => {
    const world = createWorld();
    const results = runBatch(
      [{ commentId: 'c/1' }, { ok: true }, {}],
      (item) => {
        if (item['commentId']) throw Object.assign(new Error('x'), { stderr: 'HTTP 403\n' });
        if (item['ok']) return { status: 'verified' };
        throw new Error('plain');
      },
      world.deps,
    );
    expect(results).toEqual([
      { index: 0, commentId: 'c/1', status: 'error', error: 'HTTP 403' },
      { index: 1, status: 'verified' },
      { index: 2, status: 'error', error: 'plain' },
    ]);
  });
});

describe('runBatchCommand', () => {
  it('returns 0 for success and an empty batch, and 1 when any item failed', () => {
    const empty = createWorld({ input: '[]' });
    expect(runBatchCommand([], () => ({ status: 'verified' }), empty.deps)).toBe(0);
    expect(empty.stdout.join('').trim()).toBe('[]');
    const failing = createWorld({ input: '[{}]' });
    expect(runBatchCommand([], () => ({ status: 'error', error: 'e' }), failing.deps)).toBe(1);
  });
});
