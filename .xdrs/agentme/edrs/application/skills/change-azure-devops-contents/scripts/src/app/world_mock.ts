import type { Deps } from './ports';

export type FakeThread = {
  id: number;
  status: string;
  isDeleted?: boolean;
  threadContext?: unknown;
  comments: { id: number; content: string; isDeleted?: boolean }[];
};
export type FakeWorkItem = { id: number; rev: number; fields: Record<string, unknown> };

type Options = {
  threads?: FakeThread[];
  workItems?: FakeWorkItem[];
  workItemComments?: { id: number; text: string }[];
  dropWrites?: boolean;
  failWrites?: boolean;
  markdown?: 'missing';
  input?: string;
};

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  calls: string[][];
  // Parsed JSON bodies sent with POST/PATCH, in call order.
  bodies: unknown[];
  headers: string[];
  threads: FakeThread[];
  workItems: FakeWorkItem[];
  workItemComments: { id: number; text: string }[];
};

const forbidden = (): Error => {
  const error = new Error('boom') as Error & { stderr: string };
  error.stderr = 'TF401027: You need the Contribute permission\n';
  return error;
};

const flag = (args: readonly string[], name: string): string => {
  const index = args.indexOf(name);
  return index === -1 ? '' : (args[index + 1] ?? '');
};

type Ctx = { world: World; options: Options; method: string; body: unknown; path: string };

const guard = ({ options }: Ctx): void => {
  if (options.failWrites) throw forbidden();
};

const handleThreads = (ctx: Ctx): string | undefined => {
  const { world, options, method, body, path } = ctx;
  const comments = /\/pullRequests\/\d+\/threads\/(\d+)\/comments$/.exec(path);
  const one = /\/pullRequests\/\d+\/threads\/(\d+)$/.exec(path);
  const all = /\/pullRequests\/\d+\/threads$/.test(path);
  if (!comments && !one && !all) return undefined;
  const thread = world.threads.find((t) => t.id === Number((comments ?? one)?.[1]));
  if (method === 'GET') return JSON.stringify(all ? { value: world.threads } : thread);
  guard(ctx);
  if (options.dropWrites) return '{}';
  if (comments && thread) {
    thread.comments.push({
      id: thread.comments.length + 1,
      content: (body as { content: string }).content,
    });
  } else if (one && thread) {
    thread.status = (body as { status: string }).status;
  } else if (all) {
    const first = (body as { comments: { content: string }[] }).comments[0];
    world.threads.push({
      id: world.threads.length + 1,
      status: 'active',
      comments: [{ id: 1, content: first?.content ?? '' }],
    });
  }
  return '{}';
};

type Patch = { op: string; path: string; value: unknown };
const fieldName = (patch: Patch): string => patch.path.replace('/fields/', '');

const handleWiql = ({ world, body }: Ctx): string => {
  const { query } = body as { query: string };
  const title = /\[System\.Title\] = '((?:[^']|'')*)'/.exec(query)?.[1]?.replaceAll("''", "'");
  const hits = world.workItems.filter((w) => w.fields['System.Title'] === title);
  return JSON.stringify({ workItems: hits.map((w) => ({ id: w.id })) });
};

const handleWorkItemComments = (ctx: Ctx): string => {
  const { world, options, method, body } = ctx;
  if (method === 'GET') return JSON.stringify({ comments: world.workItemComments });
  guard(ctx);
  if (!options.dropWrites) {
    world.workItemComments.push({
      id: world.workItemComments.length + 1,
      text: (body as { text: string }).text,
    });
  }
  return '{}';
};

const handleWorkItemCreate = (ctx: Ctx, type: string): string => {
  const { world, options, body } = ctx;
  guard(ctx);
  const fields: Record<string, unknown> = { 'System.WorkItemType': decodeURIComponent(type) };
  for (const patch of body as Patch[]) fields[fieldName(patch)] = patch.value;
  const item = { id: 900 + world.workItems.length, rev: 1, fields };
  if (!options.dropWrites) world.workItems.push(item);
  return JSON.stringify(item);
};

const handleWorkItemPatch = (ctx: Ctx, item: FakeWorkItem): string => {
  guard(ctx);
  if (!ctx.options.dropWrites) {
    for (const patch of ctx.body as Patch[]) {
      if (patch.op === 'add') item.fields[fieldName(patch)] = patch.value;
    }
    item.rev += 1;
  }
  return '{}';
};

const handleWorkItems = (ctx: Ctx): string | undefined => {
  const { world, method, path } = ctx;
  if (/\/wit\/wiql$/.test(path)) return handleWiql(ctx);
  if (/\/wit\/workitems\/(\d+)\/comments$/i.test(path)) return handleWorkItemComments(ctx);
  const created = /\/wit\/workitems\/\$(.+)$/i.exec(path);
  if (created) return handleWorkItemCreate(ctx, created[1] ?? '');
  const one = /\/wit\/workitems\/(\d+)$/i.exec(path);
  if (!one) return undefined;
  const item = world.workItems.find((w) => w.id === Number(one[1]));
  if (!item) throw new Error('TF401232: Work item does not exist');
  return method === 'PATCH' ? handleWorkItemPatch(ctx, item) : JSON.stringify(item);
};

export const createWorld = (options: Options = {}): World => {
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    calls: [],
    bodies: [],
    headers: [],
    threads: options.threads ?? [],
    workItems: options.workItems ?? [],
    workItemComments: options.workItemComments ?? [],
  };
  const files = new Map<string, string>();
  const run = (args: readonly string[]): string => {
    world.calls.push([...args]);
    const method = flag(args, '--method');
    const path = flag(args, '--uri').split('?')[0] ?? '';
    const bodyArg = flag(args, '--body');
    const body: unknown = bodyArg ? JSON.parse(files.get(bodyArg.slice(1)) ?? 'null') : undefined;
    if (body !== undefined) world.bodies.push(body);
    if (args.includes('--headers')) world.headers.push(flag(args, '--headers'));
    const ctx = { world, options, method, body, path };
    const result = handleThreads(ctx) ?? handleWorkItems(ctx);
    if (result === undefined) throw new Error(`unexpected az call: ${args.join(' ')}`);
    return result;
  };
  world.deps = {
    az: { run },
    input: { read: (): string => options.input ?? '[]' },
    bodyFile: {
      withFile: (content, use): ReturnType<typeof use> => {
        const file = `body-${files.size}.json`;
        files.set(file, content);
        return use(file);
      },
    },
    markdown: {
      toHtml: (markdown): string | undefined =>
        options.markdown === 'missing' ? undefined : `<p>${markdown}</p>`,
    },
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
