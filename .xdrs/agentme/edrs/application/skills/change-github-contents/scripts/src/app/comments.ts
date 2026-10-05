import { flattenPages, parseJsonStream } from './json-stream';
import type { GhPort } from './ports';

export type RestComment = {
  id: number;
  body?: string;
  in_reply_to_id?: number;
  html_url?: string;
};

export type CommentOutcome = {
  status: 'verified' | 'already-present' | 'error';
  url?: string | null;
  error?: string;
};

const findComment = (
  comments: readonly RestComment[],
  body: string,
  rootId: number | undefined,
): RestComment | undefined =>
  comments.find(
    (comment) =>
      comment.body === body && (rootId === undefined || comment.in_reply_to_id === rootId),
  );

// GitHub only accepts review-comment replies anchored to the thread root.
export const findRootId = (reviewComments: readonly RestComment[], id: number): number => {
  const byId = new Map(reviewComments.map((comment) => [comment.id, comment]));
  let current = byId.get(id);
  if (!current) throw new Error(`review comment ${id} not found on this PR`);
  const seen = new Set<number>();
  while (current.in_reply_to_id && byId.has(current.in_reply_to_id) && !seen.has(current.id)) {
    seen.add(current.id);
    current = byId.get(current.in_reply_to_id) as RestComment;
  }
  return current.in_reply_to_id ?? current.id;
};

export const listComments = (gh: GhPort, endpoint: string): RestComment[] =>
  flattenPages<RestComment>(gh.run(['api', '--paginate', endpoint]));

// Posts `body` to a comments endpoint unless identical content exists, then reads it back.
export const postIdempotent = (options: {
  gh: GhPort;
  endpoint: string;
  body: string;
  rootId?: number;
}): CommentOutcome => {
  const { gh, endpoint, body, rootId } = options;
  const existing = findComment(listComments(gh, endpoint), body, rootId);
  if (existing) return { status: 'already-present', url: existing.html_url ?? null };
  const args = ['api', '--method', 'POST', endpoint, '-f', `body=${body}`];
  if (rootId !== undefined) args.push('-F', `in_reply_to=${rootId}`);
  gh.run(args);
  const posted = findComment(listComments(gh, endpoint), body, rootId);
  if (!posted)
    return { status: 'error', error: 'write exited 0 but the comment is missing on read-back' };
  return { status: 'verified', url: posted.html_url ?? null };
};

type ThreadsPage = {
  data: {
    repository: {
      pullRequest: {
        reviewThreads: {
          nodes: {
            id: string;
            isResolved: boolean;
            comments: { nodes: { databaseId: number }[] };
          }[];
        };
      };
    };
  };
};

export const THREADS_QUERY =
  'query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$pr){reviewThreads(first:100,after:$endCursor){pageInfo{hasNextPage endCursor}nodes{id isResolved comments(first:100){nodes{databaseId}}}}}}}';

export const RESOLVE_MUTATION =
  'mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{id isResolved}}}';

export const findThread = (
  pages: readonly unknown[],
  numericId: number,
): { id: string; isResolved: boolean } | undefined =>
  (pages as ThreadsPage[])
    .flatMap((page) => page.data.repository.pullRequest.reviewThreads.nodes)
    .find((thread) => thread.comments.nodes.some((comment) => comment.databaseId === numericId));

export const lookupThread = (
  gh: GhPort,
  ref: { owner: string; repo: string; pr: number },
  numericId: number,
): { id: string; isResolved: boolean } | undefined =>
  findThread(
    parseJsonStream(
      gh.run([
        'api',
        'graphql',
        '--paginate',
        '-f',
        `query=${THREADS_QUERY}`,
        '-f',
        `owner=${ref.owner}`,
        '-f',
        `repo=${ref.repo}`,
        '-F',
        `pr=${ref.pr}`,
      ]),
    ),
    numericId,
  );
