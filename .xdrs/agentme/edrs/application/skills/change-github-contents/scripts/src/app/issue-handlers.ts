import type { Handler, Item } from './batch';
import { requireFields } from './batch';
import { postIdempotent } from './comments';
import { parseJsonStream } from './json-stream';
import type { GhPort } from './ports';
import { parseIssueUrl, parseRepoUrl } from './urls';

type RestIssue = {
  number: number;
  title: string;
  body: string | null;
  updated_at: string;
  html_url: string;
  pull_request?: unknown;
};

const normalize = (text: string | null | undefined): string =>
  (text ?? '').replaceAll('\r\n', '\n').trim();

const getIssue = (gh: GhPort, endpoint: string): RestIssue =>
  JSON.parse(gh.run(['api', endpoint])) as RestIssue;

const readBack = (gh: GhPort, endpoint: string): RestIssue | undefined => {
  try {
    return getIssue(gh, endpoint);
  } catch {
    return undefined;
  }
};

const optionalString = (item: Item, field: string): string | undefined => {
  const value = item[field];
  if (value === undefined) return undefined;
  if (typeof value !== 'string' || value === '')
    throw new Error(`item field ${field} must be a non-empty string`);
  return value;
};

export const issueCommentCreate: Handler = (item, deps) => {
  const { issueUrl, body } = requireFields(item, ['issueUrl', 'body']);
  const { owner, repo, issue } = parseIssueUrl(issueUrl as string);
  return postIdempotent({
    gh: deps.gh,
    endpoint: `repos/${owner}/${repo}/issues/${issue}/comments`,
    body: body as string,
  });
};

// Updates title and/or body unless the issue changed since it was read (stale guard on updated_at).
export const issueUpdate: Handler = (item, deps) => {
  const { issueUrl, expectedUpdatedAt } = requireFields(item, ['issueUrl', 'expectedUpdatedAt']);
  const title = optionalString(item, 'title');
  const body = optionalString(item, 'body');
  if (title === undefined && body === undefined)
    throw new Error('item needs at least one of title or body');
  const { owner, repo, issue } = parseIssueUrl(issueUrl as string);
  const endpoint = `repos/${owner}/${repo}/issues/${issue}`;
  const current = getIssue(deps.gh, endpoint);
  const sameTitle = title === undefined || normalize(title) === normalize(current.title);
  const sameBody = body === undefined || normalize(body) === normalize(current.body);
  if (sameTitle && sameBody)
    return { status: 'already-present', url: current.html_url, updatedAt: current.updated_at };
  if (current.updated_at !== expectedUpdatedAt) {
    return {
      status: 'error',
      error: `stale: the issue changed after it was read (updated_at is ${current.updated_at}, expected ${expectedUpdatedAt}); read it again and review the changes before writing`,
    };
  }
  const args = ['api', '--method', 'PATCH', endpoint];
  if (title !== undefined) args.push('-f', `title=${title}`);
  if (body !== undefined) args.push('-f', `body=${body}`);
  deps.gh.run(args);
  const after = getIssue(deps.gh, endpoint);
  const confirmed =
    (title === undefined || normalize(title) === normalize(after.title)) &&
    (body === undefined || normalize(body) === normalize(after.body));
  if (!confirmed)
    return { status: 'error', error: 'write exited 0 but the issue differs on read-back' };
  return { status: 'verified', url: after.html_url, updatedAt: after.updated_at };
};

// Creates an issue unless one with the same title exists in the repository, then reads it back.
export const issueCreate: Handler = (item, deps) => {
  const { repoUrl, title, body } = requireFields(item, ['repoUrl', 'title', 'body']);
  const { owner, repo } = parseRepoUrl(repoUrl as string);
  const query = `repo:${owner}/${repo} is:issue in:title ${(title as string).replaceAll(/["\\]/g, ' ')}`;
  const found = parseJsonStream(
    deps.gh.run([
      'api',
      '--method',
      'GET',
      'search/issues',
      '-f',
      `q=${query}`,
      '-F',
      'per_page=100',
    ]),
  ).flatMap((page) => (page as { items: RestIssue[] }).items);
  const existing = found.find(
    (issue) => !issue.pull_request && normalize(issue.title) === normalize(title),
  );
  if (existing)
    return { status: 'already-present', url: existing.html_url, number: existing.number };
  const created = JSON.parse(
    deps.gh.run([
      'api',
      '--method',
      'POST',
      `repos/${owner}/${repo}/issues`,
      '-f',
      `title=${title}`,
      '-f',
      `body=${body}`,
    ]),
  ) as RestIssue;
  const after = readBack(deps.gh, `repos/${owner}/${repo}/issues/${created.number}`);
  if (
    !after ||
    normalize(after.title) !== normalize(title) ||
    normalize(after.body) !== normalize(body)
  ) {
    return {
      status: 'error',
      error: 'write exited 0 but the issue differs on read-back',
      number: created.number,
    };
  }
  return {
    status: 'verified',
    url: after.html_url,
    number: after.number,
    updatedAt: after.updated_at,
  };
};
