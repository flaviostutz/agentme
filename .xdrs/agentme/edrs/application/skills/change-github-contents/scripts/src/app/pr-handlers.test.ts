import { findRootId } from './comments';
import { parseIssueUrl, parsePrUrl, parseRepoUrl } from './urls';
import { prCommentCreate, prCommentReply, prThreadResolve } from './pr-handlers';
import { createWorld } from './world_mock';

const PR = 'https://github.com/acme/widgets/pull/7';

describe('urls', () => {
  it('parses PR, issue and repository URLs', () => {
    expect(parsePrUrl(PR)).toEqual({ owner: 'acme', repo: 'widgets', pr: 7 });
    expect(parseIssueUrl('https://github.com/acme/widgets/issues/5#x')).toEqual({
      owner: 'acme',
      repo: 'widgets',
      issue: 5,
    });
    expect(parseRepoUrl('https://github.com/acme/widgets')).toEqual({
      owner: 'acme',
      repo: 'widgets',
    });
    expect(parseRepoUrl('https://github.com/acme/widgets.git/')).toEqual({
      owner: 'acme',
      repo: 'widgets',
    });
  });

  it('rejects unrelated and mixed-up URLs', () => {
    expect(() => parsePrUrl('https://example.com/x')).toThrow(/unrecognized/);
    expect(() => parseIssueUrl(PR)).toThrow(/pull request URL/);
    expect(() => parseIssueUrl('https://github.com/acme/widgets')).toThrow(/unrecognized/);
    expect(() => parseRepoUrl('https://github.com/acme/widgets/issues/1')).toThrow(/unrecognized/);
  });
});

describe('findRootId', () => {
  const comments = [
    { id: 1 },
    { id: 2, in_reply_to_id: 1 },
    { id: 3, in_reply_to_id: 2 },
    { id: 4, in_reply_to_id: 99 },
  ];
  it('walks reply chains to the thread root', () => {
    expect(findRootId(comments, 3)).toBe(1);
    expect(findRootId(comments, 1)).toBe(1);
    expect(findRootId(comments, 4)).toBe(99);
    expect(() => findRootId(comments, 5)).toThrow(/not found/);
  });

  it('does not loop forever on cyclic replies', () => {
    expect(
      findRootId(
        [
          { id: 1, in_reply_to_id: 2 },
          { id: 2, in_reply_to_id: 1 },
        ],
        1,
      ),
    ).toBeDefined();
  });
});

describe('prCommentReply', () => {
  it('posts a review reply to the root and verifies it', () => {
    const world = createWorld({ reviewComments: [{ id: 1 }, { id: 2, in_reply_to_id: 1 }] });
    const result = prCommentReply(
      { prUrl: PR, commentId: 'review-comment/2', body: 'Done' },
      world.deps,
    );
    expect(result.status).toBe('verified');
    expect(world.calls.some((call) => call.includes('in_reply_to=1'))).toBe(true);
    expect(world.reviewComments.at(-1)?.in_reply_to_id).toBe(1);
  });

  it('skips an identical existing reply', () => {
    const world = createWorld({
      reviewComments: [{ id: 1 }, { id: 2, in_reply_to_id: 1, body: 'Done', html_url: 'u2' }],
    });
    expect(
      prCommentReply({ prUrl: PR, commentId: 'review-comment/1', body: 'Done' }, world.deps),
    ).toEqual({
      commentId: 'review-comment/1',
      status: 'already-present',
      url: 'u2',
    });
    expect(world.calls.some((call) => call.includes('POST'))).toBe(false);
  });

  it('routes issue comments and review summaries to issue comments', () => {
    const world = createWorld();
    expect(
      prCommentReply({ prUrl: PR, commentId: 'review-summary/9', body: 'Thanks' }, world.deps)
        .status,
    ).toBe('verified');
    expect(world.issueComments).toHaveLength(1);
  });

  it('validates the comment id and fields', () => {
    const world = createWorld();
    expect(() =>
      prCommentReply({ prUrl: PR, commentId: 'thread-comment/1', body: 'x' }, world.deps),
    ).toThrow(/kind/);
    expect(() => prCommentReply({ prUrl: PR, commentId: 'issue-comment/1' }, world.deps)).toThrow(
      /body/,
    );
  });
});

describe('prCommentCreate', () => {
  it('posts once and reports error when read-back misses the write', () => {
    const world = createWorld({ dropWrites: true });
    const result = prCommentCreate({ prUrl: PR, body: 'hello' }, world.deps);
    expect(result.status).toBe('error');
    expect(result['error']).toMatch(/read-back/);
  });
});

describe('prThreadResolve', () => {
  const threads = (): Parameters<typeof createWorld>[0] => ({
    threads: [
      { id: 'T0', isResolved: false, comments: { nodes: [{ databaseId: 1 }] } },
      { id: 'T1', isResolved: false, comments: { nodes: [{ databaseId: 5 }, { databaseId: 6 }] } },
    ],
  });

  it('resolves, skips resolved and rejects non-review kinds', () => {
    const world = createWorld(threads());
    expect(prThreadResolve({ prUrl: PR, commentId: 'review-comment/6' }, world.deps).status).toBe(
      'verified',
    );
    expect(world.threads[1]?.isResolved).toBe(true);
    expect(prThreadResolve({ prUrl: PR, commentId: 'review-comment/5' }, world.deps).status).toBe(
      'already-present',
    );
    expect(() => prThreadResolve({ prUrl: PR, commentId: 'issue-comment/5' }, world.deps)).toThrow(
      /only review-comment/,
    );
    expect(() =>
      prThreadResolve({ prUrl: PR, commentId: 'review-comment/77' }, world.deps),
    ).toThrow(/no review thread/);
  });

  it('reports error when the thread stays unresolved', () => {
    const world = createWorld({ ...threads(), dropWrites: true });
    expect(prThreadResolve({ prUrl: PR, commentId: 'review-comment/1' }, world.deps).status).toBe(
      'error',
    );
  });
});
