import { usageError } from '../shared/errors';

export type PrRef = { owner: string; repo: string; pr: number };
export type IssueRef = { owner: string; repo: string; issue: number };

const PR_URL = /^https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/pull\/(\d+)(?:[/?#].*)?$/;
const ISSUE_URL = /^https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/issues\/(\d+)(?:[/?#].*)?$/;

export const parsePrUrl = (url: string): PrRef => {
  const match = PR_URL.exec(url);
  if (!match) throw usageError(`unrecognized GitHub PR URL: ${url}`);
  return { owner: match[1] ?? '', repo: match[2] ?? '', pr: Number(match[3]) };
};

// Pull request URLs are rejected on purpose: a PR is not a story to refine.
export const parseIssueUrl = (url: string): IssueRef => {
  if (PR_URL.test(url))
    throw usageError(`pull request URL given, an issue URL is required: ${url}`);
  const match = ISSUE_URL.exec(url);
  if (!match) throw usageError(`unrecognized GitHub issue URL: ${url}`);
  return { owner: match[1] ?? '', repo: match[2] ?? '', issue: Number(match[3]) };
};
