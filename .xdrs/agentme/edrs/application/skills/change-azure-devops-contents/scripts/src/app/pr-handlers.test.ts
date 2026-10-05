import { createWorld } from './world_mock';
import { prCommentCreate, prCommentReply, prThreadStatusSet } from './pr-handlers';

const prUrl = 'https://dev.azure.com/acme/proj/_git/repo/pullrequest/7';
const thread = (over: object = {}) => ({
  id: 3,
  status: 'active',
  comments: [{ id: 1, content: 'first' }],
  ...over,
});

describe('prCommentReply', () => {
  it('replies, reads back and returns the discussion url', () => {
    const world = createWorld({ threads: [thread()] });
    const result = prCommentReply(
      { prUrl, commentId: 'thread-comment/3.1', body: 'hi' },
      world.deps,
    );
    expect(result).toEqual({
      commentId: 'thread-comment/3.1',
      status: 'verified',
      url: 'https://dev.azure.com/acme/proj/_git/repo/pullrequest/7?discussionId=3',
    });
    expect(world.bodies).toEqual([{ content: 'hi', parentCommentId: 1, commentType: 1 }]);
  });

  it('is idempotent when the reply already exists', () => {
    const world = createWorld({ threads: [thread({ comments: [{ id: 2, content: 'hi' }] })] });
    const result = prCommentReply(
      { prUrl, commentId: 'thread-comment/3.1', body: 'hi' },
      world.deps,
    );
    expect(result.status).toBe('already-present');
    expect(world.bodies).toEqual([]);
  });

  it('reports a write that is missing on read-back', () => {
    const world = createWorld({ threads: [thread()], dropWrites: true });
    const result = prCommentReply(
      { prUrl, commentId: 'thread-comment/3.1', body: 'hi' },
      world.deps,
    );
    expect(result.status).toBe('error');
  });

  it('rejects a malformed comment id', () => {
    const world = createWorld();
    expect(() => prCommentReply({ prUrl, commentId: '12', body: 'hi' }, world.deps)).toThrow(
      /thread-comment/,
    );
  });
});

describe('prCommentCreate', () => {
  it('creates a general thread then reads it back', () => {
    const world = createWorld();
    const result = prCommentCreate({ prUrl, body: 'note' }, world.deps);
    expect(result.status).toBe('verified');
    expect(result['url']).toMatch(/discussionId=1$/);
  });

  it('is idempotent for an existing general thread and ignores code threads', () => {
    const world = createWorld({
      threads: [
        thread({ threadContext: {}, comments: [{ id: 1, content: 'note' }] }),
        thread({ id: 4, comments: [{ id: 1, content: 'note' }] }),
      ],
    });
    const result = prCommentCreate({ prUrl, body: 'note' }, world.deps);
    expect(result).toMatchObject({ status: 'already-present' });
    expect(result['url']).toMatch(/discussionId=4$/);
  });

  it('reports a dropped write', () => {
    const world = createWorld({ dropWrites: true });
    expect(prCommentCreate({ prUrl, body: 'note' }, world.deps).status).toBe('error');
  });
});

describe('prThreadStatusSet', () => {
  it('sets and verifies the status', () => {
    const world = createWorld({ threads: [thread()] });
    expect(
      prThreadStatusSet({ prUrl, commentId: 'thread-comment/3.1', status: 'fixed' }, world.deps)
        .status,
    ).toBe('verified');
  });

  it('is idempotent when the status already matches', () => {
    const world = createWorld({ threads: [thread({ status: 'fixed' })] });
    expect(
      prThreadStatusSet({ prUrl, commentId: 'thread-comment/3.1', status: 'fixed' }, world.deps)
        .status,
    ).toBe('already-present');
  });

  it('rejects unknown statuses and reports dropped writes', () => {
    const world = createWorld({ threads: [thread()], dropWrites: true });
    expect(() =>
      prThreadStatusSet({ prUrl, commentId: 'thread-comment/3.1', status: 'nope' }, world.deps),
    ).toThrow(/status must be/);
    expect(
      prThreadStatusSet({ prUrl, commentId: 'thread-comment/3.1', status: 'closed' }, world.deps)
        .status,
    ).toBe('error');
  });
});
