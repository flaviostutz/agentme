import { createWorld } from './world_mock';
import { workItemCommentCreate, workItemCreate, workItemUpdate } from './work-item-handlers';

const workItemUrl = 'https://dev.azure.com/acme/My%20Proj/_workitems/edit/5';
const existing = (over: Record<string, unknown> = {}) => ({
  id: 5,
  rev: 4,
  fields: { 'System.Title': 'Old', 'System.Description': '<p>old</p>', ...over },
});

describe('workItemCommentCreate', () => {
  it('adds the comment as HTML on the preview API and reads it back', () => {
    const world = createWorld();
    const result = workItemCommentCreate({ workItemUrl, body: 'hello' }, world.deps);
    expect(result).toEqual({
      status: 'verified',
      url: 'https://dev.azure.com/acme/My%20Proj/_workitems/edit/5',
    });
    expect(world.bodies).toEqual([{ text: '<p>hello</p>' }]);
    expect(world.calls[0]?.join(' ')).toContain('api-version=7.1-preview.4');
  });

  it('is idempotent and tolerant of HTML re-formatting', () => {
    const world = createWorld({ workItemComments: [{ id: 1, text: '<div>hello</div>' }] });
    expect(workItemCommentCreate({ workItemUrl, body: 'hello' }, world.deps).status).toBe(
      'already-present',
    );
    expect(world.bodies).toEqual([]);
  });

  it('reports a dropped write and a missing converter', () => {
    expect(
      workItemCommentCreate({ workItemUrl, body: 'x' }, createWorld({ dropWrites: true }).deps)
        .status,
    ).toBe('error');
    expect(() =>
      workItemCommentCreate({ workItemUrl, body: 'x' }, createWorld({ markdown: 'missing' }).deps),
    ).toThrow(/pandoc/);
  });
});

describe('workItemUpdate', () => {
  it('patches with a rev test operation and the json-patch content type', () => {
    const world = createWorld({ workItems: [existing()] });
    const result = workItemUpdate(
      { workItemUrl, expectedRev: 4, title: 'New', body: 'new' },
      world.deps,
    );
    expect(result).toMatchObject({ status: 'verified', rev: 5 });
    expect(world.bodies[0]).toEqual([
      { op: 'test', path: '/rev', value: 4 },
      { op: 'add', path: '/fields/System.Title', value: 'New' },
      { op: 'add', path: '/fields/System.Description', value: '<p>new</p>' },
    ]);
    expect(world.headers).toEqual(['Content-Type=application/json-patch+json']);
  });

  it('supports another body field and title only', () => {
    const world = createWorld({ workItems: [existing()] });
    workItemUpdate(
      { workItemUrl, expectedRev: '4', body: 'steps', bodyField: 'Microsoft.VSTS.TCM.ReproSteps' },
      world.deps,
    );
    expect(world.workItems[0]?.fields['Microsoft.VSTS.TCM.ReproSteps']).toBe('<p>steps</p>');
    workItemUpdate({ workItemUrl, expectedRev: 5, title: 'T' }, world.deps);
    expect(world.workItems[0]?.fields['System.Title']).toBe('T');
  });

  it('refuses stale writes without patching', () => {
    const world = createWorld({ workItems: [existing()] });
    const result = workItemUpdate({ workItemUrl, expectedRev: 3, title: 'New' }, world.deps);
    expect(result.status).toBe('error');
    expect(String(result['error'])).toMatch(/^stale:/);
    expect(world.bodies).toEqual([]);
  });

  it('is idempotent when content already matches', () => {
    const world = createWorld({ workItems: [existing()] });
    expect(
      workItemUpdate({ workItemUrl, expectedRev: 4, title: 'Old', body: 'old' }, world.deps).status,
    ).toBe('already-present');
  });

  it('reports dropped writes and validates input', () => {
    const world = createWorld({ workItems: [existing()], dropWrites: true });
    expect(workItemUpdate({ workItemUrl, expectedRev: 4, title: 'New' }, world.deps).status).toBe(
      'error',
    );
    expect(() => workItemUpdate({ workItemUrl, expectedRev: 'x', title: 'a' }, world.deps)).toThrow(
      /expectedRev/,
    );
    expect(() => workItemUpdate({ workItemUrl, expectedRev: 4 }, world.deps)).toThrow(
      /title or body/,
    );
    expect(() => workItemUpdate({ workItemUrl, expectedRev: 4, title: '' }, world.deps)).toThrow(
      /non-empty/,
    );
    expect(() =>
      workItemUpdate({ workItemUrl, expectedRev: 4, title: 'a' }, createWorld().deps),
    ).toThrow(/does not exist/);
  });
});

describe('workItemCreate', () => {
  const item = {
    workItemUrl,
    type: 'User Story',
    title: "It's new",
    body: 'b',
    areaPath: 'P\\A',
    iterationPath: 'P\\I',
  };

  it('creates the item with type, paths and json-patch, then reads it back', () => {
    const world = createWorld();
    const result = workItemCreate(item, world.deps);
    expect(result).toMatchObject({
      status: 'verified',
      id: 900,
      url: 'https://dev.azure.com/acme/My%20Proj/_workitems/edit/900',
    });
    expect(world.calls.some((call) => call.join(' ').includes('/workitems/$User%20Story'))).toBe(
      true,
    );
    expect(world.workItems[0]?.fields).toMatchObject({
      'System.AreaPath': 'P\\A',
      'System.IterationPath': 'P\\I',
    });
  });

  it('dedupes by exact title through WIQL with escaped quotes', () => {
    const world = createWorld({ workItems: [existing({ 'System.Title': "It's new" })] });
    expect(workItemCreate(item, world.deps)).toMatchObject({ status: 'already-present', id: 5 });
    const { query } = world.bodies[0] as { query: string };
    expect(query).toContain("'It''s new'");
  });

  it('works without paths and reports dropped writes', () => {
    const world = createWorld();
    workItemCreate({ workItemUrl, type: 'Task', title: 'x', body: 'b' }, world.deps);
    expect(Object.keys(world.workItems[0]?.fields ?? {})).not.toContain('System.AreaPath');
    expect(workItemCreate(item, createWorld({ dropWrites: true }).deps).status).toBe('error');
  });
});
