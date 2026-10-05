import { COMMENTS_API_VERSION } from '../shared/constants';

import { parseArgs, requireString } from './args';
import { type Asset, downloadAssets, mergeAssets } from './attachments';
import { extractLinks, inlineAttachmentUrls } from './links';
import type { Deps } from './ports';
import { restGet } from './rest';
import { parseWorkItemUrl } from './urls';

const USAGE = 'work-item-get --work-item-url <url> [--download-dir <dir>] [--no-download]';
const MAX_COMMENT_PAGES = 20;

type Person = { displayName?: string } | string | undefined;

type Relation = {
  rel: string;
  url: string;
  attributes?: { name?: string; resourceSize?: number };
};

type WorkItem = {
  id: number;
  rev: number;
  fields: Record<string, unknown>;
  relations?: Relation[];
};

type CommentsPage = {
  comments?: { id: number; text?: string; createdBy?: Person; createdDate?: string }[];
  continuationToken?: string;
};

const text = (fields: Record<string, unknown>, key: string): string => {
  const value = fields[key];
  return typeof value === 'string' ? value : '';
};

const person = (value: unknown): string | null => {
  const found = value as Person;
  if (typeof found === 'string') return found;
  return found?.displayName ?? null;
};

const lastNumber = (url: string): number | null => {
  const match = /(\d+)\/?$/.exec(url);
  return match ? Number(match[1]) : null;
};

const projectVisibility = (deps: Deps, orgUrl: string, project: string): string => {
  try {
    return (
      restGet<{ visibility?: string }>(deps.az, `${orgUrl}/_apis/projects/${project}`).visibility ??
      'unknown'
    );
  } catch {
    return 'unknown';
  }
};

const readComments = (deps: Deps, base: string): NonNullable<CommentsPage['comments']> => {
  const all: NonNullable<CommentsPage['comments']> = [];
  let token: string | undefined;
  for (let page = 0; page < MAX_COMMENT_PAGES; page += 1) {
    const suffix = token ? `&continuationToken=${encodeURIComponent(token)}` : '';
    const result = restGet<CommentsPage>(
      deps.az,
      `${base}/comments?$top=200${suffix}`,
      COMMENTS_API_VERSION,
    );
    all.push(...(result.comments ?? []));
    token = result.continuationToken;
    if (!token) break;
  }
  return all;
};

// Reads one work item with comments, project visibility, downloaded attachments and linked URLs.
export const runWorkItemGet = (argv: readonly string[], deps: Deps): number => {
  const parsed = parseArgs(argv);
  const ref = parseWorkItemUrl(requireString(parsed, 'work-item-url', USAGE));
  const base = `${ref.orgUrl}/${ref.project}/_apis/wit/workitems/${ref.id}`;
  const item = restGet<WorkItem>(deps.az, `${base}?$expand=all`);
  const comments = readComments(deps, base);
  const { fields } = item;
  const rich = (key: string): { html: string; markdown: string | null } | null => {
    const html = text(fields, key);
    return html.trim() ? { html, markdown: deps.markdown.fromHtml(html) ?? null } : null;
  };
  const relations = item.relations ?? [];
  const htmlBlocks = [
    text(fields, 'System.Description'),
    text(fields, 'Microsoft.VSTS.Common.AcceptanceCriteria'),
    text(fields, 'Microsoft.VSTS.TCM.ReproSteps'),
    ...comments.map((comment) => comment.text ?? ''),
  ];
  const related: Asset[] = relations
    .filter((relation) => relation.rel === 'AttachedFile')
    .map((relation) => ({
      name: relation.attributes?.name ?? 'attachment',
      url: relation.url,
      ...(relation.attributes?.resourceSize === undefined
        ? {}
        : { size: relation.attributes.resourceSize }),
    }));
  const inline: Asset[] = htmlBlocks
    .flatMap((html) => inlineAttachmentUrls(html, ref.org))
    .map((url) => ({
      name: decodeURIComponent(new URL(url).searchParams.get('fileName') ?? 'image'),
      url,
    }));
  const dir =
    typeof parsed['download-dir'] === 'string'
      ? parsed['download-dir']
      : `.tmp/work-item-attachments/${ref.org}-${ref.id}`;
  const assets = mergeAssets([...related, ...inline]);
  const attachments =
    parsed['no-download'] === true ? [] : downloadAssets(assets, { dir, org: ref.org }, deps);
  const hyperlinks = relations
    .filter((relation) => relation.rel === 'Hyperlink')
    .map((relation) => relation.url);
  const parent = relations.find(
    (relation) => relation.rel === 'System.LinkTypes.Hierarchy-Reverse',
  );
  const tags = text(fields, 'System.Tags');
  const record = {
    url: ref.webUrl,
    org: ref.org,
    project: ref.projectName,
    id: item.id,
    type: text(fields, 'System.WorkItemType'),
    title: text(fields, 'System.Title'),
    state: text(fields, 'System.State'),
    rev: item.rev,
    changedDate: text(fields, 'System.ChangedDate'),
    createdBy: person(fields['System.CreatedBy']),
    assignedTo: person(fields['System.AssignedTo']),
    tags: tags ? tags.split(';').map((tag) => tag.trim()) : [],
    areaPath: text(fields, 'System.AreaPath'),
    iterationPath: text(fields, 'System.IterationPath'),
    parentId: parent ? lastNumber(parent.url) : null,
    projectVisibility: projectVisibility(deps, ref.orgUrl, ref.project),
    description: rich('System.Description'),
    acceptanceCriteria: rich('Microsoft.VSTS.Common.AcceptanceCriteria'),
    reproSteps: rich('Microsoft.VSTS.TCM.ReproSteps'),
    comments: comments.map((comment) => ({
      id: comment.id,
      author: person(comment.createdBy),
      createdAt: comment.createdDate ?? '',
      html: comment.text ?? '',
      markdown: deps.markdown.fromHtml(comment.text ?? '') ?? null,
    })),
    attachments,
    links: [
      ...new Set([...hyperlinks, ...extractLinks(htmlBlocks.join('\n'), ref.webUrl, ref.org)]),
    ],
  };
  deps.output.out(`${JSON.stringify(record, null, 2)}\n`);
  return 0;
};
