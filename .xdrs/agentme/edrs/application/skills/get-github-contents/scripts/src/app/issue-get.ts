import { usageError } from '../shared/errors';

import { parseArgs, requireString } from './args';
import { extractAssets, extractLinks } from './assets';
import { downloadAssets } from './attachments';
import { flattenPages } from './json-stream';
import type { Deps } from './ports';
import { parseIssueUrl } from './urls';

const USAGE = 'issue-get --issue-url <url> [--download-dir <dir>] [--no-download]';
const ACCEPT = ['-H', 'Accept: application/vnd.github.full+json'];

type RestUser = { login?: string } | null;

type RestIssue = {
  number: number;
  title: string;
  body: string | null;
  body_html?: string | null;
  state: string;
  state_reason?: string | null;
  locked?: boolean;
  html_url: string;
  created_at: string;
  updated_at: string;
  user: RestUser;
  labels: (string | { name?: string })[];
  assignees?: { login?: string }[];
  milestone?: { title?: string } | null;
  pull_request?: unknown;
};

type RestComment = {
  id: number;
  body: string | null;
  body_html?: string | null;
  user: RestUser;
  created_at: string;
  html_url: string;
};

type RestRepo = { private: boolean; archived: boolean; full_name: string };

// Reads one issue with its comments, repo visibility, downloaded attachments and linked URLs.
export const runIssueGet = async (argv: readonly string[], deps: Deps): Promise<number> => {
  const parsed = parseArgs(argv);
  const url = requireString(parsed, 'issue-url', USAGE);
  const { owner, repo, issue: number } = parseIssueUrl(url);
  const base = `repos/${owner}/${repo}`;
  const issue = JSON.parse(
    deps.gh.run(['api', ...ACCEPT, `${base}/issues/${number}`]),
  ) as RestIssue;
  if (issue.pull_request) throw usageError(`${url} is a pull request, an issue URL is required`);
  const repository = JSON.parse(deps.gh.run(['api', base])) as RestRepo;
  const comments = flattenPages<RestComment>(
    deps.gh.run(['api', '--paginate', ...ACCEPT, `${base}/issues/${number}/comments`]),
  );
  const html = [issue.body_html ?? '', ...comments.map((comment) => comment.body_html ?? '')].join(
    '\n',
  );
  const text = [issue.body ?? '', ...comments.map((comment) => comment.body ?? '')].join('\n');
  const assets = extractAssets(html);
  const dir =
    typeof parsed['download-dir'] === 'string'
      ? parsed['download-dir']
      : `.tmp/issue-attachments/${owner}-${repo}-${number}`;
  const attachments = parsed['no-download'] === true ? [] : await downloadAssets(assets, dir, deps);
  const record = {
    url: issue.html_url,
    owner,
    repo,
    number,
    title: issue.title,
    body: issue.body ?? '',
    state: issue.state,
    locked: issue.locked ?? false,
    author: issue.user?.login ?? null,
    labels: issue.labels.map((label) => (typeof label === 'string' ? label : (label.name ?? ''))),
    assignees: (issue.assignees ?? []).map((assignee) => assignee.login ?? ''),
    milestone: issue.milestone?.title ?? null,
    createdAt: issue.created_at,
    updatedAt: issue.updated_at,
    repository: {
      fullName: repository.full_name,
      private: repository.private,
      archived: repository.archived,
    },
    comments: comments.map((comment) => ({
      id: comment.id,
      author: comment.user?.login ?? null,
      body: comment.body ?? '',
      createdAt: comment.created_at,
      url: comment.html_url,
    })),
    attachments,
    links: extractLinks(text, issue.html_url),
  };
  deps.output.out(`${JSON.stringify(record, null, 2)}\n`);
  return 0;
};
