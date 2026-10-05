const STATUS_MAP: Record<string, string> = {
  active: 'open',
  pending: 'open',
  fixed: 'resolved',
  closed: 'resolved',
  wontFix: 'wontfix',
  byDesign: 'wontfix',
};

type Position = { line?: number } | undefined;

type ThreadComment = {
  id: number;
  content?: string;
  isDeleted?: boolean;
  commentType?: string;
  author?: { displayName?: string } | null;
};

export type Thread = {
  id: number;
  status?: string;
  isDeleted?: boolean;
  threadContext?: { filePath?: string; rightFileStart?: Position; leftFileStart?: Position } | null;
  comments?: ThreadComment[];
};

export type PrDetails = {
  pullRequestId?: number;
  title?: string;
  description?: string;
  status?: string;
  isDraft?: boolean;
  targetRefName?: string;
  sourceRefName?: string;
  repository?: { name?: string };
  createdBy?: { displayName?: string };
};

const isHumanComment = (comment: ThreadComment): boolean =>
  !comment.isDeleted && comment.commentType !== 'system';

// Maps Azure DevOps threads to the record shape shared with GitHub; deleted and system comments are omitted.
export const normalizeThreads = (threads: readonly Thread[], webUrl: string): object[] =>
  threads.flatMap((thread) => {
    const comments = (thread.comments ?? []).filter((comment) => isHumanComment(comment));
    const root = comments[0];
    if (thread.isDeleted || !root) return [];
    const context = thread.threadContext;
    const start = context?.rightFileStart ?? context?.leftFileStart;
    return comments.map((comment) => ({
      id: `thread-comment/${thread.id}.${comment.id}`,
      kind: 'thread-comment',
      status: STATUS_MAP[thread.status ?? ''] ?? 'open',
      can_reply: true,
      can_resolve: true,
      path: context?.filePath ?? null,
      line: start?.line ?? null,
      content: comment.content ?? '',
      author: comment.author?.displayName ?? null,
      in_reply_to: comment.id === root.id ? null : root.id,
      diff_hunk: null,
      url: `${webUrl}?discussionId=${thread.id}`,
    }));
  });

const branch = (ref: string | undefined): string | null =>
  ref?.replace(/^refs\/heads\//, '') ?? null;

export const pickPrMetadata = (pr: PrDetails, webUrl: string): object => ({
  number: pr.pullRequestId,
  title: pr.title,
  body: pr.description ?? '',
  state: pr.status,
  isDraft: Boolean(pr.isDraft),
  url: webUrl,
  baseRefName: branch(pr.targetRefName),
  headRefName: branch(pr.sourceRefName),
  repository: pr.repository?.name ?? null,
  author: pr.createdBy?.displayName ?? null,
});
