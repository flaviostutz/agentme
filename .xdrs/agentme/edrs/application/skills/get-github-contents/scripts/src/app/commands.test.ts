import { runIssueGet } from './issue-get';
import { runPrCommentsList } from './pr-comments-list';
import { runPrMetadataGet } from './pr-metadata-get';
import { createWorld, okBytes } from './world_mock';

const issue = {
  number: 42,
  title: 'Export orders',
  body: 'Need export. Spec: https://wiki.example.com/spec',
  body_html:
    '<p><img src="https://private-user-images.githubusercontent.com/1/m.png?jwt=a" alt="mock"></p>',
  state: 'open',
  locked: false,
  html_url: 'https://github.com/acme/widgets/issues/42',
  created_at: '2026-05-01T09:00:00Z',
  updated_at: '2026-05-01T10:00:00Z',
  user: { login: 'ana' },
  labels: [{ name: 'feature' }, 'bug'],
  assignees: [{ login: 'bob' }],
  milestone: { title: 'v1' },
};

const ghFor =
  (overrides: Record<string, unknown> = {}) =>
  (args: readonly string[]): string => {
    const path = args.at(-1) ?? '';
    if (path.endsWith('/issues/42')) return JSON.stringify({ ...issue, ...overrides });
    if (path.endsWith('/issues/42/comments')) {
      return JSON.stringify([
        {
          id: 7,
          body: 'see https://other.example.com/x',
          body_html: '',
          user: null,
          created_at: 't',
          html_url: 'u7',
        },
      ]);
    }
    if (path === 'repos/acme/widgets')
      return JSON.stringify({ private: true, archived: false, full_name: 'acme/widgets' });
    throw new Error(`unexpected ${args.join(' ')}`);
  };

describe('runIssueGet', () => {
  it('prints the issue with comments, visibility, attachments and links (happy flow)', async () => {
    const world = createWorld({ gh: ghFor(), http: () => okBytes('png') });
    const code = await runIssueGet(
      ['--issue-url', 'https://github.com/acme/widgets/issues/42#issuecomment-7'],
      world.deps,
    );
    expect(code).toBe(0);
    const record = JSON.parse(world.stdout.join('')) as Record<string, unknown>;
    expect(record).toMatchObject({
      title: 'Export orders',
      labels: ['feature', 'bug'],
      assignees: ['bob'],
      milestone: 'v1',
      updatedAt: '2026-05-01T10:00:00Z',
      repository: { private: true, archived: false },
      comments: [{ id: 7, author: null, body: 'see https://other.example.com/x' }],
      attachments: [{ name: 'mock', path: '.tmp/get-github-contents/acme-widgets-42/1-mock.png' }],
      links: ['https://wiki.example.com/spec', 'https://other.example.com/x'],
    });
    expect(world.ghCalls[0]).toEqual([
      'api',
      '-H',
      'Accept: application/vnd.github.full+json',
      'repos/acme/widgets/issues/42',
    ]);
  });

  it('skips downloads with --no-download and honors --download-dir', async () => {
    const world = createWorld({ gh: ghFor(), http: () => okBytes('png') });
    await runIssueGet(
      ['--issue-url', 'https://github.com/acme/widgets/issues/42', '--no-download'],
      world.deps,
    );
    expect(world.httpCalls).toEqual([]);
    const second = createWorld({ gh: ghFor(), http: () => okBytes('png') });
    await runIssueGet(
      ['--issue-url', 'https://github.com/acme/widgets/issues/42', '--download-dir', '.tmp/z'],
      second.deps,
    );
    expect([...second.files.keys()]).toEqual(['.tmp/z/1-mock.png']);
  });

  it('rejects a pull request returned by the issues endpoint and pull request URLs (adversarial/invalid)', async () => {
    const world = createWorld({ gh: ghFor({ pull_request: {} }) });
    await expect(
      runIssueGet(['--issue-url', 'https://github.com/acme/widgets/issues/42'], world.deps),
    ).rejects.toThrow(/pull request/);
    await expect(
      runIssueGet(['--issue-url', 'https://github.com/acme/widgets/pull/42'], world.deps),
    ).rejects.toThrow(/pull request URL/);
    await expect(runIssueGet([], world.deps)).rejects.toThrow(/Usage: issue-get/);
  });

  it('handles an issue without body, labels as strings and no comments', async () => {
    const world = createWorld({
      gh: (args) =>
        (args.at(-1) ?? '').endsWith('/comments')
          ? '[]'
          : ghFor({
              body: null,
              body_html: null,
              user: null,
              assignees: undefined,
              milestone: null,
              locked: true,
            })(args),
    });
    await runIssueGet(['--issue-url', 'https://github.com/acme/widgets/issues/42'], world.deps);
    expect(JSON.parse(world.stdout.join(''))).toMatchObject({
      body: '',
      author: null,
      locked: true,
      assignees: [],
      milestone: null,
      attachments: [],
      links: [],
    });
  });
});

describe('runPrMetadataGet', () => {
  it('prints the gh pr view JSON', () => {
    const world = createWorld({ gh: () => '{"number":482,"title":"t"}' });
    expect(
      runPrMetadataGet(['--pr-url', 'https://github.com/acme/widgets/pull/482'], world.deps),
    ).toBe(0);
    expect(JSON.parse(world.stdout.join(''))).toEqual({ number: 482, title: 't' });
    expect(world.ghCalls[0]?.slice(0, 5)).toEqual(['pr', 'view', '482', '--repo', 'acme/widgets']);
  });

  it('fails without --pr-url', () => {
    expect(() => runPrMetadataGet([], createWorld().deps)).toThrow(/Usage/);
  });
});

describe('runPrCommentsList', () => {
  it('prints normalized records from the REST and GraphQL calls (regression)', () => {
    const world = createWorld({
      gh: (args) => {
        if (args.includes('graphql')) {
          return JSON.stringify({
            data: {
              repository: {
                pullRequest: {
                  reviewThreads: {
                    nodes: [{ isResolved: true, comments: { nodes: [{ databaseId: 10 }] } }],
                  },
                },
              },
            },
          });
        }
        const path = args.at(-1) ?? '';
        if (path.endsWith('/issues/482/comments'))
          return '[{"id":1,"body":"hi","user":{"login":"ann"},"html_url":"u1"}]';
        if (path.endsWith('/pulls/482/comments'))
          return '[{"id":10,"body":"root","path":"a.js","line":3}]';
        return '[]';
      },
    });
    expect(
      runPrCommentsList(['--pr-url', 'https://github.com/acme/widgets/pull/482'], world.deps),
    ).toBe(0);
    const records = JSON.parse(world.stdout.join('')) as { id: string; status: string }[];
    expect(records.map((record) => `${record.id}:${record.status}`)).toEqual([
      'issue-comment/1:open',
      'review-comment/10:resolved',
    ]);
  });
});
