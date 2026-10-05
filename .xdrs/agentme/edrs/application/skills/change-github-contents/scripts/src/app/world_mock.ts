import type { Deps } from './ports';

export type Thread = {
  id: string;
  isResolved: boolean;
  comments: { nodes: { databaseId: number }[] };
};
export type FakeIssue = {
  number: number;
  title: string;
  body: string | null;
  updated_at: string;
  html_url: string;
  pull_request?: unknown;
};
export type StoredComment = {
  id: number;
  body?: string;
  in_reply_to_id?: number;
  html_url?: string;
};

type Options = {
  issueComments?: StoredComment[];
  reviewComments?: StoredComment[];
  threads?: Thread[];
  issues?: FakeIssue[];
  dropWrites?: boolean;
  failWrites?: boolean;
  input?: string;
};

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  calls: string[][];
  issueComments: StoredComment[];
  reviewComments: StoredComment[];
  threads: Thread[];
  issues: FakeIssue[];
};

const arg = (args: readonly string[], prefix: string): string | undefined =>
  args.find((value) => value.startsWith(prefix))?.slice(prefix.length);

const forbidden = (): Error => {
  const error = new Error('boom') as Error & { stderr: string };
  error.stderr = 'HTTP 403: Resource not accessible\n';
  return error;
};

const handleGraphql = (world: World, args: readonly string[], options: Options): string => {
  const query = arg(args, 'query=') ?? '';
  if (query.includes('resolveReviewThread')) {
    const thread = world.threads.find((candidate) => candidate.id === arg(args, 'id='));
    if (thread && !options.dropWrites) thread.isResolved = true;
    return '{}';
  }
  const half = Math.ceil(world.threads.length / 2);
  const page = (nodes: Thread[]): string =>
    JSON.stringify({ data: { repository: { pullRequest: { reviewThreads: { nodes } } } } });
  return page(world.threads.slice(0, half)) + page(world.threads.slice(half));
};

const handleIssues = (
  world: World,
  args: readonly string[],
  options: Options,
): string | undefined => {
  const endpoint = args.find((value) => /^repos\/[^/]+\/[^/]+\/issues(\/\d+)?$/.test(value));
  if (!endpoint) return undefined;
  const number = Number(/\/issues\/(\d+)$/.exec(endpoint)?.[1] ?? 0);
  const method = args[args.indexOf('--method') + 1];
  if (method === 'POST') {
    if (options.failWrites) throw forbidden();
    const issue: FakeIssue = {
      number: 100 + world.issues.length,
      title: arg(args, 'title=') ?? '',
      body: arg(args, 'body=') ?? null,
      updated_at: '2026-01-02T00:00:00Z',
      html_url: `https://github.com/acme/widgets/issues/${100 + world.issues.length}`,
    };
    if (!options.dropWrites) world.issues.push(issue);
    return JSON.stringify(issue);
  }
  const issue = world.issues.find((candidate) => candidate.number === number);
  if (!issue) throw new Error('HTTP 404: Not Found');
  if (method === 'PATCH') {
    if (options.failWrites) throw forbidden();
    if (!options.dropWrites) {
      issue.title = arg(args, 'title=') ?? issue.title;
      issue.body = arg(args, 'body=') ?? issue.body;
      issue.updated_at = '2026-02-01T00:00:00Z';
    }
    return '{}';
  }
  return JSON.stringify(issue);
};

export const createWorld = (options: Options = {}): World => {
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    calls: [],
    issueComments: options.issueComments ?? [],
    reviewComments: options.reviewComments ?? [],
    threads: options.threads ?? [],
    issues: options.issues ?? [],
  };
  const run = (args: readonly string[]): string => {
    world.calls.push([...args]);
    if (args[1] === 'graphql') return handleGraphql(world, args, options);
    if (args.includes('search/issues')) {
      return JSON.stringify({ items: world.issues });
    }
    const issueResult = handleIssues(world, args, options);
    if (issueResult !== undefined) return issueResult;
    const endpoint = args.find((value) => value.startsWith('repos/')) ?? '';
    const store = endpoint.includes('/pulls/') ? world.reviewComments : world.issueComments;
    if (args[1] === '--paginate') return JSON.stringify(store);
    if (args[1] === '--method' && args[2] === 'POST') {
      if (options.failWrites) throw forbidden();
      const replyTo = arg(args, 'in_reply_to=');
      if (!options.dropWrites) {
        store.push({
          id: 1000 + store.length,
          body: arg(args, 'body='),
          in_reply_to_id: replyTo ? Number(replyTo) : undefined,
          html_url: `u-${endpoint}`,
        });
      }
      return '{}';
    }
    throw new Error(`unexpected gh call: ${args.join(' ')}`);
  };
  world.deps = {
    gh: { run },
    input: { read: (): string => options.input ?? '[]' },
    output: {
      out: (text): void => {
        world.stdout.push(text);
      },
      err: (text): void => {
        world.stderr.push(text);
      },
    },
  };
  return world;
};
