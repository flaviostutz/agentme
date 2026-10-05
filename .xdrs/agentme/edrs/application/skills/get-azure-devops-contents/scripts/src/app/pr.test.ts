import { normalizeThreads, pickPrMetadata } from './pr';
import { restGet } from './rest';

describe('restGet', () => {
  it('always passes the ADO resource and api-version', () => {
    const calls: string[][] = [];
    const az = {
      run: (args: readonly string[]): string => {
        calls.push([...args]);
        return '{"value":[]}';
      },
    };
    expect(restGet(az, 'https://x/threads')).toEqual({ value: [] });
    expect(calls[0]?.slice(0, 5)).toEqual([
      'rest',
      '--resource',
      '499b84ac-1321-427f-aa17-267ca6975798',
      '--method',
      'GET',
    ]);
    expect(calls[0]?.at(-1)).toBe('https://x/threads?api-version=7.1');
    restGet(az, 'https://x/threads?top=1', '7.1-preview.4');
    expect(calls[1]?.at(-1)).toBe('https://x/threads?top=1&api-version=7.1-preview.4');
  });
});

describe('normalizeThreads', () => {
  it('maps threads to the shared record shape (regression of the JS port)', () => {
    const records = normalizeThreads(
      [
        {
          id: 12,
          status: 'fixed',
          threadContext: { filePath: '/src/a.ts', rightFileStart: { line: 4 } },
          comments: [
            { id: 1, content: 'root', author: { displayName: 'Ann' } },
            { id: 2, content: 'reply', author: null },
            { id: 3, content: 'gone', isDeleted: true },
          ],
        },
        {
          id: 13,
          status: 'active',
          threadContext: null,
          comments: [{ id: 1, content: 'general' }],
        },
        {
          id: 14,
          status: 'wontFix',
          threadContext: { filePath: '/b', leftFileStart: { line: 9 } },
          comments: [{ id: 1 }],
        },
        {
          id: 15,
          status: 'weird',
          threadContext: { filePath: '/c' },
          comments: [{ id: 1, content: 'x' }],
        },
        { id: 16, comments: [{ id: 1, commentType: 'system', content: 'voted' }] },
        { id: 17, isDeleted: true, comments: [{ id: 1 }] },
        { id: 18 },
      ],
      'https://w',
    ) as Record<string, unknown>[];
    expect(records).toHaveLength(5);
    expect(records[0]).toEqual({
      id: 'thread-comment/12.1',
      kind: 'thread-comment',
      status: 'resolved',
      can_reply: true,
      can_resolve: true,
      path: '/src/a.ts',
      line: 4,
      content: 'root',
      author: 'Ann',
      in_reply_to: null,
      diff_hunk: null,
      url: 'https://w?discussionId=12',
    });
    expect(records[1]).toMatchObject({ in_reply_to: 1, author: null });
    expect(records[2]).toMatchObject({ status: 'open', path: null, line: null });
    expect(records[3]).toMatchObject({ status: 'wontfix', line: 9, content: '' });
    expect(records[4]).toMatchObject({ status: 'open', line: null });
  });
});

describe('pickPrMetadata', () => {
  it('keeps the useful fields', () => {
    expect(
      pickPrMetadata(
        {
          pullRequestId: 5,
          title: 't',
          status: 'active',
          targetRefName: 'refs/heads/main',
          sourceRefName: 'refs/heads/feat/x',
          repository: { name: 'r' },
          createdBy: { displayName: 'Bo' },
        },
        'https://w',
      ),
    ).toEqual({
      number: 5,
      title: 't',
      body: '',
      state: 'active',
      isDraft: false,
      url: 'https://w',
      baseRefName: 'main',
      headRefName: 'feat/x',
      repository: 'r',
      author: 'Bo',
    });
    expect(pickPrMetadata({ description: 'd', isDraft: true }, 'u')).toMatchObject({
      body: 'd',
      isDraft: true,
      baseRefName: null,
      repository: null,
      author: null,
    });
  });
});
