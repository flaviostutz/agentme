import { runPrCommentsList } from './pr-comments-list';
import { runPrMetadataGet } from './pr-metadata-get';
import { createWorld } from './world_mock';
import { runWorkItemGet } from './work-item-get';

const ATT = 'https://dev.azure.com/contoso/guid/_apis/wit/attachments/abc';
const URL_ = 'https://dev.azure.com/contoso/My%20Project/_workitems/edit/321#comment';

const workItem = {
  id: 321,
  rev: 7,
  fields: {
    'System.WorkItemType': 'User Story',
    'System.Title': 'Export orders',
    'System.State': 'Active',
    'System.ChangedDate': '2026-05-01T10:00:00Z',
    'System.CreatedBy': { displayName: 'Ana' },
    'System.AssignedTo': 'bob@example.com',
    'System.Tags': 'export; csv',
    'System.AreaPath': 'Widgets',
    'System.IterationPath': 'Widgets\\Sprint 1',
    'System.Description': `<div>Need export. Spec: https://wiki.example.com/spec <img src="${ATT}?fileName=shot.png"></div>`,
    'Microsoft.VSTS.Common.AcceptanceCriteria': '<ul><li>csv</li></ul>',
  },
  relations: [
    { rel: 'AttachedFile', url: ATT, attributes: { name: 'shot.png', resourceSize: 100 } },
    { rel: 'Hyperlink', url: 'https://example.com/design' },
    {
      rel: 'System.LinkTypes.Hierarchy-Reverse',
      url: 'https://dev.azure.com/contoso/_apis/wit/workItems/99',
    },
  ],
};

type Handler = (uri: string) => unknown;

const azFor =
  (handler: Handler) =>
  (args: readonly string[]): string => {
    const uri = args[args.indexOf('--uri') + 1] ?? '';
    return JSON.stringify(handler(uri));
  };

const standard: Handler = (uri) => {
  if (uri.includes('/comments')) {
    return {
      comments: [
        {
          id: 1,
          text: '<p>see https://other.example.com/x</p>',
          createdBy: { displayName: 'Cy' },
          createdDate: 't',
        },
      ],
    };
  }
  if (uri.includes('/_apis/projects/')) return { visibility: 'private' };
  return workItem;
};

describe('runWorkItemGet', () => {
  it('prints the work item with comments, visibility, attachments and links (happy flow)', () => {
    const world = createWorld({ az: azFor(standard) });
    expect(runWorkItemGet(['--work-item-url', URL_], world.deps)).toBe(0);
    const record = JSON.parse(world.stdout.join('')) as Record<string, unknown>;
    expect(record).toMatchObject({
      url: 'https://dev.azure.com/contoso/My%20Project/_workitems/edit/321',
      project: 'My Project',
      id: 321,
      type: 'User Story',
      title: 'Export orders',
      rev: 7,
      changedDate: '2026-05-01T10:00:00Z',
      createdBy: 'Ana',
      assignedTo: 'bob@example.com',
      tags: ['export', 'csv'],
      parentId: 99,
      projectVisibility: 'private',
      acceptanceCriteria: { markdown: 'md:<ul><li>csv</li></ul>' },
      reproSteps: null,
      comments: [{ id: 1, author: 'Cy', markdown: 'md:<p>see https://other.example.com/x</p>' }],
      attachments: [
        { name: 'shot.png', url: ATT, path: '.tmp/work-item-attachments/contoso-321/1-shot.png' },
      ],
      links: [
        'https://example.com/design',
        'https://wiki.example.com/spec',
        'https://other.example.com/x',
      ],
    });
    const uris = world.azCalls.map((call) => call[call.indexOf('--uri') + 1]);
    expect(uris[0]).toBe(
      'https://dev.azure.com/contoso/My%20Project/_apis/wit/workitems/321?$expand=all&api-version=7.1',
    );
    expect(uris[1]).toContain('/comments?$top=200&api-version=7.1-preview.4');
  });

  it('follows comment continuation tokens, honors --no-download and falls back when pandoc is missing', () => {
    let page = 0;
    const world = createWorld({
      markdown: 'missing',
      az: azFor((uri) => {
        if (uri.includes('/comments')) {
          page += 1;
          return page === 1
            ? { comments: [{ id: 1 }], continuationToken: 'a b' }
            : { comments: [{ id: 2, text: 'x' }] };
        }
        if (uri.includes('/_apis/projects/')) throw new Error('403');
        return { id: 5, rev: 1, fields: { 'System.Description': '<p>x</p>' } };
      }),
    });
    runWorkItemGet(['--work-item-url', URL_, '--no-download'], world.deps);
    const record = JSON.parse(world.stdout.join('')) as Record<string, unknown>;
    expect(record).toMatchObject({
      projectVisibility: 'unknown',
      description: { html: '<p>x</p>', markdown: null },
      comments: [
        { id: 1, author: null, markdown: null },
        { id: 2, markdown: null },
      ],
      attachments: [],
      tags: [],
      parentId: null,
      assignedTo: null,
    });
    expect(
      world.azCalls.some((call) => call.some((arg) => arg.includes('continuationToken=a%20b'))),
    ).toBe(true);
  });

  it('honors --download-dir and treats a missing visibility as unknown', () => {
    const world = createWorld({
      az: azFor((uri) => {
        if (uri.includes('/comments')) return {};
        if (uri.includes('/_apis/projects/')) return {};
        return { ...workItem, relations: [workItem.relations[0]] };
      }),
    });
    runWorkItemGet(['--work-item-url', URL_, '--download-dir', '.tmp/z'], world.deps);
    expect([...world.files.keys()]).toEqual(['.tmp/z/1-shot.png']);
    expect(JSON.parse(world.stdout.join(''))).toMatchObject({
      projectVisibility: 'unknown',
      parentId: null,
    });
  });

  it('rejects pull request, board and missing URLs', () => {
    const world = createWorld();
    expect(() =>
      runWorkItemGet(
        ['--work-item-url', 'https://dev.azure.com/contoso/p/_git/r/pullrequest/1'],
        world.deps,
      ),
    ).toThrow(/pull request URL/);
    expect(() => runWorkItemGet([], world.deps)).toThrow(/Usage: work-item-get/);
  });
});

describe('runPrMetadataGet', () => {
  it('prints metadata read through az repos pr show', () => {
    const world = createWorld({ az: () => '{"pullRequestId":5,"title":"t","status":"active"}' });
    expect(
      runPrMetadataGet(
        ['--pr-url', 'https://contoso.visualstudio.com/Widgets/_git/r/pullrequest/5'],
        world.deps,
      ),
    ).toBe(0);
    expect(JSON.parse(world.stdout.join(''))).toMatchObject({ number: 5, state: 'active' });
    expect(world.azCalls[0]).toEqual([
      'repos',
      'pr',
      'show',
      '--id',
      '5',
      '--organization',
      'https://dev.azure.com/contoso',
      '--output',
      'json',
    ]);
  });

  it('fails without --pr-url', () => {
    expect(() => runPrMetadataGet([], createWorld().deps)).toThrow(/Usage/);
  });
});

describe('runPrCommentsList', () => {
  it('prints normalized records from the threads endpoint', () => {
    const world = createWorld({
      az: azFor(() => ({
        value: [{ id: 1, status: 'active', comments: [{ id: 1, content: 'hi' }] }],
      })),
    });
    expect(
      runPrCommentsList(
        ['--pr-url', 'https://dev.azure.com/contoso/Widgets/_git/r/pullrequest/5'],
        world.deps,
      ),
    ).toBe(0);
    expect(JSON.parse(world.stdout.join(''))).toMatchObject([
      { id: 'thread-comment/1.1', content: 'hi' },
    ]);
  });

  it('tolerates a response without value', () => {
    const world = createWorld({ az: azFor(() => ({})) });
    runPrCommentsList(
      ['--pr-url', 'https://dev.azure.com/contoso/Widgets/_git/r/pullrequest/5'],
      world.deps,
    );
    expect(JSON.parse(world.stdout.join(''))).toEqual([]);
  });
});
