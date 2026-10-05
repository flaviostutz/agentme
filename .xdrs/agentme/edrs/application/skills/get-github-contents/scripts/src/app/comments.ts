export const THREADS_QUERY =
  'query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$pr){reviewThreads(first:100,after:$endCursor){pageInfo{hasNextPage endCursor}nodes{id isResolved comments(first:100){nodes{databaseId}}}}}}}';

type User = { login?: string } | null | undefined;

type RestComment = {
  id: number;
  body?: string | null;
  user?: User;
  html_url?: string | null;
  in_reply_to_id?: number | null;
  path?: string | null;
  line?: number | null;
  original_line?: number | null;
  diff_hunk?: string | null;
};

export type Thread = { isResolved: boolean; comments: { nodes: { databaseId: number }[] } };

type ThreadsPage = {
  data: { repository: { pullRequest: { reviewThreads: { nodes: Thread[] } } } };
};

export type CommentRecord = {
  id: string;
  kind: 'issue-comment' | 'review-comment' | 'review-summary';
  status: 'open' | 'resolved';
  can_reply: boolean;
  can_resolve: boolean;
  path: string | null;
  line: number | null;
  content: string;
  author: string | null;
  in_reply_to: number | null;
  diff_hunk: string | null;
  url: string | null;
};

export type CommentInputs = {
  issueComments?: RestComment[];
  reviewComments?: RestComment[];
  reviews?: RestComment[];
  threads?: Thread[];
};

export const threadsFromGraphql = (pages: unknown[]): Thread[] =>
  (pages as ThreadsPage[]).flatMap((page) => page.data.repository.pullRequest.reviewThreads.nodes);

const login = (user: User): string | null => user?.login ?? null;

const rootId = (comment: RestComment, byId: Map<number, RestComment>): number => {
  let current = comment;
  const seen = new Set<number>();
  while (current.in_reply_to_id && byId.has(current.in_reply_to_id) && !seen.has(current.id)) {
    seen.add(current.id);
    current = byId.get(current.in_reply_to_id) ?? current;
  }
  return current.in_reply_to_id ?? current.id;
};

const base = (comment: RestComment): Pick<CommentRecord, 'content' | 'author' | 'url'> => ({
  content: comment.body ?? '',
  author: login(comment.user),
  url: comment.html_url ?? null,
});

export const normalizeComments = (inputs: CommentInputs): CommentRecord[] => {
  const { issueComments = [], reviewComments = [], reviews = [], threads = [] } = inputs;
  const resolvedIds = new Set<number>();
  const threadIds = new Set<number>();
  for (const thread of threads) {
    for (const node of thread.comments.nodes) {
      threadIds.add(node.databaseId);
      if (thread.isResolved) resolvedIds.add(node.databaseId);
    }
  }
  const byId = new Map(reviewComments.map((comment) => [comment.id, comment]));
  const issueRecords = issueComments.map((comment): CommentRecord => ({
    id: `issue-comment/${comment.id}`,
    kind: 'issue-comment',
    status: 'open',
    can_reply: true,
    can_resolve: false,
    path: null,
    line: null,
    in_reply_to: null,
    diff_hunk: null,
    ...base(comment),
  }));
  const reviewRecords = reviewComments.map((comment): CommentRecord => {
    const root = rootId(comment, byId);
    return {
      id: `review-comment/${comment.id}`,
      kind: 'review-comment',
      status: resolvedIds.has(comment.id) ? 'resolved' : 'open',
      can_reply: true,
      can_resolve: threadIds.has(comment.id),
      path: comment.path ?? null,
      line: comment.line ?? comment.original_line ?? null,
      in_reply_to: root === comment.id ? null : root,
      diff_hunk: comment.diff_hunk ?? null,
      ...base(comment),
    };
  });
  const summaryRecords = reviews
    .filter((review) => Boolean(review.body))
    .map((review): CommentRecord => ({
      id: `review-summary/${review.id}`,
      kind: 'review-summary',
      status: 'open',
      can_reply: true,
      can_resolve: false,
      path: null,
      line: null,
      in_reply_to: null,
      diff_hunk: null,
      ...base(review),
    }));
  return [...issueRecords, ...reviewRecords, ...summaryRecords];
};
