import { usageError } from '../shared/errors';

export type PrRef = {
  org: string;
  project: string;
  repo: string;
  pr: number;
  orgUrl: string;
  apiBase: string;
  webUrl: string;
};

export type WorkItemRef = {
  org: string;
  // Percent-encoded exactly as it appears in URLs.
  project: string;
  projectName: string;
  id: number;
  orgUrl: string;
  webUrl: string;
};

const PR_PATTERNS = [
  /^https:\/\/dev\.azure\.com\/([^/\s]+)\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i,
  /^https:\/\/([^./\s]+)\.visualstudio\.com\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i,
];

const WORK_ITEM_PATTERNS = [
  /^https:\/\/dev\.azure\.com\/([^/\s]+)\/([^/\s]+)\/_workitems\/edit\/(\d+)(?:[/?#].*)?$/i,
  /^https:\/\/([^./\s]+)\.visualstudio\.com\/([^/\s]+)\/_workitems\/edit\/(\d+)(?:[/?#].*)?$/i,
];

const firstMatch = (patterns: readonly RegExp[], url: string): RegExpExecArray | undefined => {
  for (const pattern of patterns) {
    const match = pattern.exec(url);
    if (match) return match;
  }
  return undefined;
};

export const parsePrUrl = (url: string): PrRef => {
  const match = firstMatch(PR_PATTERNS, String(url));
  if (!match) throw usageError(`unrecognized Azure DevOps PR URL: ${url}`);
  const [, org = '', project = '', repo = '', pr = ''] = match;
  const orgUrl = `https://dev.azure.com/${org}`;
  return {
    org,
    project,
    repo,
    pr: Number(pr),
    orgUrl,
    apiBase: `${orgUrl}/${project}/_apis/git/repositories/${repo}/pullRequests/${pr}`,
    webUrl: `${orgUrl}/${project}/_git/${repo}/pullrequest/${pr}`,
  };
};

// PR and board URLs are rejected on purpose: only one work item can be refined at a time.
export const parseWorkItemUrl = (url: string): WorkItemRef => {
  if (firstMatch(PR_PATTERNS, url)) {
    throw usageError(`pull request URL given, a work item URL is required: ${url}`);
  }
  const match = firstMatch(WORK_ITEM_PATTERNS, url);
  if (!match) throw usageError(`unrecognized Azure DevOps work item URL: ${url}`);
  const [, org = '', project = '', id = ''] = match;
  const orgUrl = `https://dev.azure.com/${org}`;
  return {
    org,
    project,
    projectName: decodeURIComponent(project),
    id: Number(id),
    orgUrl,
    webUrl: `${orgUrl}/${project}/_workitems/edit/${id}`,
  };
};
