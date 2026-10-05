import { issueCommentCreate, issueCreate, issueUpdate } from './issue-handlers';
import type { FakeIssue } from './world_mock';
import { createWorld } from './world_mock';

const ISSUE = 'https://github.com/acme/widgets/issues/5';
const REPO = 'https://github.com/acme/widgets';
const issue = (extra: Partial<FakeIssue> = {}): FakeIssue => ({
  number: 5,
  title: 'Old title',
  body: 'Old body',
  updated_at: '2026-01-01T00:00:00Z',
  html_url: ISSUE,
  ...extra,
});

describe('issueCommentCreate', () => {
  it('posts the comment once and is idempotent', () => {
    const world = createWorld();
    expect(issueCommentCreate({ issueUrl: ISSUE, body: 'Original text' }, world.deps).status).toBe(
      'verified',
    );
    expect(issueCommentCreate({ issueUrl: ISSUE, body: 'Original text' }, world.deps).status).toBe(
      'already-present',
    );
    expect(world.issueComments).toHaveLength(1);
    expect(world.calls.some((call) => call.includes('repos/acme/widgets/issues/5/comments'))).toBe(
      true,
    );
  });

  it('rejects PR urls and missing fields', () => {
    const world = createWorld();
    expect(() =>
      issueCommentCreate(
        { issueUrl: 'https://github.com/acme/widgets/pull/5', body: 'x' },
        world.deps,
      ),
    ).toThrow(/pull request/);
    expect(() => issueCommentCreate({ issueUrl: ISSUE }, world.deps)).toThrow(/body/);
  });
});

describe('issueUpdate', () => {
  const item = {
    issueUrl: ISSUE,
    expectedUpdatedAt: '2026-01-01T00:00:00Z',
    title: 'New title',
    body: 'New body',
  };

  it('updates title and body and verifies by read-back', () => {
    const world = createWorld({ issues: [issue()] });
    expect(issueUpdate(item, world.deps)).toEqual({
      status: 'verified',
      url: ISSUE,
      updatedAt: '2026-02-01T00:00:00Z',
    });
    expect(world.issues[0]).toMatchObject({ title: 'New title', body: 'New body' });
  });

  it('updates only the given field', () => {
    const world = createWorld({ issues: [issue()] });
    expect(issueUpdate({ ...item, title: undefined }, world.deps).status).toBe('verified');
    expect(world.issues[0]).toMatchObject({ title: 'Old title', body: 'New body' });
    expect(world.calls.flat().some((value) => value.startsWith('title='))).toBe(false);
  });

  it('refuses a stale issue without writing', () => {
    const world = createWorld({ issues: [issue({ updated_at: '2026-01-05T00:00:00Z' })] });
    const result = issueUpdate(item, world.deps);
    expect(result.status).toBe('error');
    expect(result['error']).toMatch(/stale/);
    expect(world.calls.some((call) => call.includes('PATCH'))).toBe(false);
  });

  it('returns already-present when the content is identical (line endings ignored)', () => {
    const world = createWorld({ issues: [issue({ title: 'New title', body: 'New\r\nbody' })] });
    expect(issueUpdate({ ...item, body: 'New\nbody' }, world.deps).status).toBe('already-present');
    expect(world.calls.some((call) => call.includes('PATCH'))).toBe(false);
  });

  it('reports a failed read-back and write errors', () => {
    expect(
      issueUpdate(item, createWorld({ issues: [issue()], dropWrites: true }).deps).status,
    ).toBe('error');
    expect(() =>
      issueUpdate(item, createWorld({ issues: [issue()], failWrites: true }).deps),
    ).toThrow(/boom/);
  });

  it('validates the item', () => {
    const world = createWorld({ issues: [issue()] });
    expect(() => issueUpdate({ issueUrl: ISSUE, expectedUpdatedAt: 'x' }, world.deps)).toThrow(
      /title or body/,
    );
    expect(() => issueUpdate({ ...item, title: 3 }, world.deps)).toThrow(/title must be/);
    expect(() => issueUpdate({ issueUrl: ISSUE, title: 'x' }, world.deps)).toThrow(
      /expectedUpdatedAt/,
    );
  });
});

describe('issueCreate', () => {
  const item = { repoUrl: REPO, title: '[NEEDS REFINING] Export "csv"', body: 'Context' };

  it('creates the issue and verifies it by read-back', () => {
    const world = createWorld();
    const result = issueCreate(item, world.deps);
    expect(result).toMatchObject({ status: 'verified', number: 100 });
    expect(world.issues[0]).toMatchObject({ title: item.title, body: 'Context' });
    const search = world.calls.flat().find((value) => value.startsWith('q=')) ?? '';
    expect(search).toContain('repo:acme/widgets is:issue in:title');
    expect(search).not.toContain('"');
  });

  it('skips creation when an issue with the same title exists', () => {
    const world = createWorld({
      issues: [issue({ title: item.title }), issue({ number: 6, title: 'PR', pull_request: {} })],
    });
    expect(issueCreate(item, world.deps)).toMatchObject({ status: 'already-present', number: 5 });
    expect(world.calls.some((call) => call.includes('POST'))).toBe(false);
  });

  it('ignores pull requests with the same title', () => {
    const world = createWorld({ issues: [issue({ title: item.title, pull_request: {} })] });
    expect(issueCreate(item, world.deps).status).toBe('verified');
  });

  it('reports a failed read-back', () => {
    const world = createWorld({ dropWrites: true });
    const result = issueCreate(item, world.deps);
    expect(result.status).toBe('error');
  });
});
