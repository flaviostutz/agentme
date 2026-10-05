import { normalizeComments, threadsFromGraphql } from './comments';

describe('threadsFromGraphql', () => {
  it('merges paginated pages', () => {
    const page = (id: number): unknown => ({
      data: {
        repository: {
          pullRequest: {
            reviewThreads: {
              nodes: [{ isResolved: false, comments: { nodes: [{ databaseId: id }] } }],
            },
          },
        },
      },
    });
    expect(threadsFromGraphql([page(1), page(2)])).toHaveLength(2);
  });
});

describe('normalizeComments', () => {
  it('maps every kind to the shared record shape', () => {
    const records = normalizeComments({
      issueComments: [{ id: 1, body: 'general', user: { login: 'ann' }, html_url: 'u1' }],
      reviewComments: [
        {
          id: 10,
          body: 'root',
          user: { login: 'bob' },
          path: 'a.js',
          line: 3,
          diff_hunk: '@@',
          html_url: 'u10',
        },
        { id: 11, body: 'reply', user: null, path: 'a.js', original_line: 3, in_reply_to_id: 10 },
        { id: 12, body: 'reply-to-reply', in_reply_to_id: 11 },
        { id: 13, in_reply_to_id: 99 },
      ],
      reviews: [
        { id: 20, body: 'summary', user: { login: 'cy' }, html_url: 'u20' },
        { id: 21, body: '' },
      ],
      threads: [
        {
          isResolved: true,
          comments: { nodes: [{ databaseId: 10 }, { databaseId: 11 }, { databaseId: 12 }] },
        },
      ],
    });
    const byId = Object.fromEntries(records.map((record) => [record.id, record]));
    expect(records).toHaveLength(6);
    expect(byId['issue-comment/1']).toEqual({
      id: 'issue-comment/1',
      kind: 'issue-comment',
      status: 'open',
      can_reply: true,
      can_resolve: false,
      path: null,
      line: null,
      content: 'general',
      author: 'ann',
      in_reply_to: null,
      diff_hunk: null,
      url: 'u1',
    });
    expect(byId['review-comment/10']).toMatchObject({
      status: 'resolved',
      can_resolve: true,
      in_reply_to: null,
    });
    expect(byId['review-comment/11']).toMatchObject({ in_reply_to: 10, author: null, line: 3 });
    expect(byId['review-comment/12']?.in_reply_to).toBe(10);
    expect(byId['review-comment/13']).toMatchObject({
      in_reply_to: 99,
      status: 'open',
      can_resolve: false,
    });
    expect(byId['review-summary/20']?.can_resolve).toBe(false);
    expect(byId['review-summary/21']).toBeUndefined();
  });

  it('accepts empty input', () => {
    expect(normalizeComments({})).toEqual([]);
  });
});
