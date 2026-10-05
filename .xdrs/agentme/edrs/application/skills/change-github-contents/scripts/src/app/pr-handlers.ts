import {
  postIdempotent,
  findRootId,
  listComments,
  lookupThread,
  RESOLVE_MUTATION,
} from './comments';
import type { Handler } from './batch';
import { requireFields } from './batch';
import { parsePrUrl } from './urls';

const parseCommentId = (id: string): { kind: string; numericId: number } => {
  const match = /^(issue-comment|review-comment|review-summary)\/(\d+)$/.exec(id);
  if (!match) throw new Error(`commentId is not a <kind>/<numeric-id> value: ${id}`);
  return { kind: match[1] ?? '', numericId: Number(match[2]) };
};

export const prCommentReply: Handler = (item, deps) => {
  const { prUrl, commentId, body } = requireFields(item, ['prUrl', 'commentId', 'body']);
  const { owner, repo, pr } = parsePrUrl(prUrl as string);
  const { kind, numericId } = parseCommentId(commentId as string);
  const { gh } = deps;
  if (kind !== 'review-comment') {
    // Issue comments and review summaries have no threads; a reply is a new PR comment.
    const outcome = postIdempotent({
      gh,
      endpoint: `repos/${owner}/${repo}/issues/${pr}/comments`,
      body: body as string,
    });
    return { commentId, ...outcome };
  }
  const endpoint = `repos/${owner}/${repo}/pulls/${pr}/comments`;
  const rootId = findRootId(listComments(gh, endpoint), numericId);
  return { commentId, ...postIdempotent({ gh, endpoint, body: body as string, rootId }) };
};

export const prCommentCreate: Handler = (item, deps) => {
  const { prUrl, body } = requireFields(item, ['prUrl', 'body']);
  const { owner, repo, pr } = parsePrUrl(prUrl as string);
  return postIdempotent({
    gh: deps.gh,
    endpoint: `repos/${owner}/${repo}/issues/${pr}/comments`,
    body: body as string,
  });
};

export const prThreadResolve: Handler = (item, deps) => {
  const { prUrl, commentId } = requireFields(item, ['prUrl', 'commentId']);
  const ref = parsePrUrl(prUrl as string);
  const { kind, numericId } = parseCommentId(commentId as string);
  if (kind !== 'review-comment')
    throw new Error(`only review-comment threads can be resolved, got ${kind}`);
  const thread = lookupThread(deps.gh, ref, numericId);
  if (!thread) throw new Error(`no review thread contains comment ${numericId}`);
  if (thread.isResolved) return { commentId, status: 'already-present' };
  deps.gh.run(['api', 'graphql', '-f', `query=${RESOLVE_MUTATION}`, '-f', `id=${thread.id}`]);
  const after = lookupThread(deps.gh, ref, numericId);
  if (!after?.isResolved) {
    return {
      commentId,
      status: 'error',
      error: 'mutation exited 0 but the thread is still unresolved on read-back',
    };
  }
  return { commentId, status: 'verified' };
};
