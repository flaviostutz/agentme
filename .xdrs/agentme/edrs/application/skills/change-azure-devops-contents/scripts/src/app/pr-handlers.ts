import { THREAD_STATUSES } from '../shared/constants';

import type { Handler } from './batch';
import { requireFields } from './batch';
import { rest } from './rest';
import { parsePrUrl } from './urls';

type Thread = {
  id?: number;
  status?: string;
  isDeleted?: boolean;
  threadContext?: unknown;
  comments?: { content?: string; isDeleted?: boolean }[];
};

const parseCommentId = (id: string): { threadId: number; commentId: number } => {
  const match = /^thread-comment\/(\d+)\.(\d+)$/.exec(id);
  if (!match)
    throw new Error(`commentId is not a thread-comment/<threadId>.<commentId> value: ${id}`);
  return { threadId: Number(match[1]), commentId: Number(match[2]) };
};

const hasContent = (thread: Thread | null, body: string): boolean =>
  (thread?.comments ?? []).some((comment) => !comment.isDeleted && comment.content === body);

const findGeneralThread = (threads: readonly Thread[], body: string): Thread | undefined =>
  threads.find(
    (thread) =>
      !thread.isDeleted && !thread.threadContext && thread.comments?.[0]?.content === body,
  );

export const prCommentReply: Handler = (item, deps) => {
  const { prUrl, commentId, body } = requireFields(item, ['prUrl', 'commentId', 'body']);
  const { apiBase, webUrl } = parsePrUrl(prUrl as string);
  const ids = parseCommentId(commentId as string);
  const threadUri = `${apiBase}/threads/${ids.threadId}`;
  const url = `${webUrl}?discussionId=${ids.threadId}`;
  const read = (): Thread | null => rest<Thread | null>(deps, { method: 'GET', uri: threadUri });
  if (hasContent(read(), body as string)) return { commentId, status: 'already-present', url };
  rest(deps, {
    method: 'POST',
    uri: `${threadUri}/comments`,
    body: { content: body, parentCommentId: ids.commentId, commentType: 1 },
  });
  // A zero exit from `az rest` is not proof the write persisted; always read back.
  if (!hasContent(read(), body as string)) {
    return {
      commentId,
      status: 'error',
      error: 'write exited 0 but the reply is missing on read-back',
    };
  }
  return { commentId, status: 'verified', url };
};

export const prCommentCreate: Handler = (item, deps) => {
  const { prUrl, body } = requireFields(item, ['prUrl', 'body']);
  const { apiBase, webUrl } = parsePrUrl(prUrl as string);
  const list = (): Thread[] =>
    rest<{ value?: Thread[] }>(deps, { method: 'GET', uri: `${apiBase}/threads` }).value ?? [];
  const existing = findGeneralThread(list(), body as string);
  if (existing) return { status: 'already-present', url: `${webUrl}?discussionId=${existing.id}` };
  rest(deps, {
    method: 'POST',
    uri: `${apiBase}/threads`,
    body: { comments: [{ parentCommentId: 0, content: body, commentType: 1 }], status: 'active' },
  });
  const created = findGeneralThread(list(), body as string);
  if (!created)
    return { status: 'error', error: 'write exited 0 but the thread is missing on read-back' };
  return { status: 'verified', url: `${webUrl}?discussionId=${created.id}` };
};

export const prThreadStatusSet: Handler = (item, deps) => {
  const { prUrl, commentId, status } = requireFields(item, ['prUrl', 'commentId', 'status']);
  if (!THREAD_STATUSES.includes(status as string))
    throw new Error(`status must be one of ${THREAD_STATUSES.join(', ')}`);
  const { apiBase } = parsePrUrl(prUrl as string);
  const { threadId } = parseCommentId(commentId as string);
  const threadUri = `${apiBase}/threads/${threadId}`;
  const read = (): Thread => rest<Thread>(deps, { method: 'GET', uri: threadUri });
  if (read().status === status) return { commentId, status: 'already-present' };
  rest(deps, { method: 'PATCH', uri: threadUri, body: { status } });
  if (read().status !== status) {
    return {
      commentId,
      status: 'error',
      error: `write exited 0 but the thread status is not "${status}" on read-back`,
    };
  }
  return { commentId, status: 'verified' };
};
