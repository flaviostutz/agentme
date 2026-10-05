import { COMMENTS_API_VERSION, DEFAULT_BODY_FIELD } from '../shared/constants';

import type { Handler, Item } from './batch';
import { requireFields } from './batch';
import type { Deps } from './ports';
import { plainText, rest } from './rest';
import { parseWorkItemUrl } from './urls';

type WorkItem = { id: number; rev: number; fields: Record<string, unknown> };
type WorkItemComment = { id: number; text?: string };

const JSON_PATCH = 'application/json-patch+json';
const MAX_COMMENT_PAGES = 20;

const toHtml = (deps: Deps, markdown: string): string => {
  const html = deps.markdown.toHtml(markdown);
  if (html === undefined) {
    throw new Error(
      'pandoc is required to convert markdown to the HTML Azure DevOps stores; install it (brew install pandoc)',
    );
  }
  return html;
};

const field = (workItem: WorkItem, name: string): string => {
  const value = workItem.fields[name];
  return typeof value === 'string' ? value : '';
};

const optionalString = (item: Item, name: string): string | undefined => {
  const value = item[name];
  if (value === undefined) return undefined;
  if (typeof value !== 'string' || value === '')
    throw new Error(`item field ${name} must be a non-empty string`);
  return value;
};

const workItemApi = (ref: { orgUrl: string; project: string }, id?: number): string =>
  `${ref.orgUrl}/${ref.project}/_apis/wit/workitems${id === undefined ? '' : `/${id}`}`;

const getWorkItem = (deps: Deps, uri: string): WorkItem =>
  rest<WorkItem>(deps, { method: 'GET', uri });

// A work item that cannot be read back counts as a failed write instead of aborting the batch item.
const readBack = (deps: Deps, uri: string): WorkItem | undefined => {
  try {
    return getWorkItem(deps, uri);
  } catch {
    return undefined;
  }
};

const listComments = (deps: Deps, uri: string): WorkItemComment[] => {
  const comments: WorkItemComment[] = [];
  let token: string | undefined;
  for (let page = 0; page < MAX_COMMENT_PAGES; page += 1) {
    const suffix = token === undefined ? '' : `&continuationToken=${encodeURIComponent(token)}`;
    const response = rest<{ comments?: WorkItemComment[]; continuationToken?: string }>(deps, {
      method: 'GET',
      uri: `${uri}?$top=200${suffix}`,
      version: COMMENTS_API_VERSION,
    });
    comments.push(...(response.comments ?? []));
    token = response.continuationToken;
    if (!token) break;
  }
  return comments;
};

export const workItemCommentCreate: Handler = (item, deps) => {
  const { workItemUrl, body } = requireFields(item, ['workItemUrl', 'body']);
  const ref = parseWorkItemUrl(workItemUrl as string);
  const uri = `${workItemApi(ref, ref.id)}/comments`;
  const html = toHtml(deps, body as string);
  const has = (): boolean =>
    listComments(deps, uri).some((comment) => plainText(comment.text) === plainText(html));
  if (has()) return { status: 'already-present', url: ref.webUrl };
  rest(deps, { method: 'POST', uri, version: COMMENTS_API_VERSION, body: { text: html } });
  // A zero exit from `az rest` is not proof the write persisted; always read back.
  if (!has())
    return { status: 'error', error: 'write exited 0 but the comment is missing on read-back' };
  return { status: 'verified', url: ref.webUrl };
};

// Updates title and/or body unless the work item changed since it was read (stale guard on rev).
export const workItemUpdate: Handler = (item, deps) => {
  const { workItemUrl } = requireFields(item, ['workItemUrl']);
  const expectedRev = Number(item['expectedRev']);
  if (!Number.isInteger(expectedRev))
    throw new Error('item field expectedRev must be the integer rev read earlier');
  const title = optionalString(item, 'title');
  const markdown = optionalString(item, 'body');
  const bodyField = optionalString(item, 'bodyField') ?? DEFAULT_BODY_FIELD;
  if (title === undefined && markdown === undefined)
    throw new Error('item needs at least one of title or body');
  const ref = parseWorkItemUrl(workItemUrl as string);
  const uri = workItemApi(ref, ref.id);
  const html = markdown === undefined ? undefined : toHtml(deps, markdown);
  const matches = (workItem: WorkItem): boolean =>
    (title === undefined || title === field(workItem, 'System.Title')) &&
    (html === undefined || plainText(html) === plainText(field(workItem, bodyField)));
  const current = getWorkItem(deps, uri);
  if (matches(current)) return { status: 'already-present', url: ref.webUrl, rev: current.rev };
  if (current.rev !== expectedRev) {
    return {
      status: 'error',
      error: `stale: the work item changed after it was read (rev is ${current.rev}, expected ${expectedRev}); read it again and review the changes before writing`,
    };
  }
  const operations: Record<string, unknown>[] = [{ op: 'test', path: '/rev', value: expectedRev }];
  if (title !== undefined)
    operations.push({ op: 'add', path: '/fields/System.Title', value: title });
  if (html !== undefined) operations.push({ op: 'add', path: `/fields/${bodyField}`, value: html });
  rest(deps, { method: 'PATCH', uri, body: operations, contentType: JSON_PATCH });
  const after = getWorkItem(deps, uri);
  if (!matches(after))
    return { status: 'error', error: 'write exited 0 but the work item differs on read-back' };
  return { status: 'verified', url: ref.webUrl, rev: after.rev };
};

const escapeWiql = (text: string): string => text.replaceAll("'", "''");

// Creates a work item unless one with the same type and title exists in the project, then reads it back.
export const workItemCreate: Handler = (item, deps) => {
  const { workItemUrl, type, title, body } = requireFields(item, [
    'workItemUrl',
    'type',
    'title',
    'body',
  ]);
  const areaPath = optionalString(item, 'areaPath');
  const iterationPath = optionalString(item, 'iterationPath');
  const ref = parseWorkItemUrl(workItemUrl as string);
  const project = `${ref.orgUrl}/${ref.project}`;
  const html = toHtml(deps, body as string);
  const query = `SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = @project AND [System.WorkItemType] = '${escapeWiql(type as string)}' AND [System.Title] = '${escapeWiql(title as string)}'`;
  const found = rest<{ workItems?: { id: number }[] }>(deps, {
    method: 'POST',
    uri: `${project}/_apis/wit/wiql`,
    body: { query },
  }).workItems?.[0];
  const webUrl = (id: number): string => `${project}/_workitems/edit/${id}`;
  if (found) return { status: 'already-present', id: found.id, url: webUrl(found.id) };
  const operations: Record<string, unknown>[] = [
    { op: 'add', path: '/fields/System.Title', value: title },
    { op: 'add', path: '/fields/System.Description', value: html },
  ];
  if (areaPath !== undefined)
    operations.push({ op: 'add', path: '/fields/System.AreaPath', value: areaPath });
  if (iterationPath !== undefined)
    operations.push({ op: 'add', path: '/fields/System.IterationPath', value: iterationPath });
  const created = rest<WorkItem>(deps, {
    method: 'POST',
    uri: `${project}/_apis/wit/workitems/$${encodeURIComponent(type as string)}`,
    body: operations,
    contentType: JSON_PATCH,
  });
  const after = readBack(deps, workItemApi(ref, created.id));
  if (
    !after ||
    field(after, 'System.Title') !== title ||
    plainText(field(after, 'System.Description')) !== plainText(html)
  ) {
    return {
      status: 'error',
      error: 'write exited 0 but the work item is missing or differs on read-back',
      id: created.id,
    };
  }
  return { status: 'verified', id: after.id, url: webUrl(after.id), rev: after.rev };
};
