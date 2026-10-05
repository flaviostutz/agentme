import { isOrgUrl, parsePrUrl, parseWorkItemUrl } from './urls';

describe('parsePrUrl', () => {
  it('accepts modern and legacy URLs', () => {
    const modern = parsePrUrl(
      'https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029',
    );
    expect(modern.apiBase).toBe(
      'https://dev.azure.com/contoso/Widgets/_apis/git/repositories/widgets-api/pullRequests/1029',
    );
    expect(modern.webUrl).toBe(
      'https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029',
    );
    const legacy = parsePrUrl(
      'https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/7?_a=files',
    );
    expect([legacy.org, legacy.project, legacy.repo, legacy.pr, legacy.orgUrl]).toEqual([
      'contoso',
      'Widgets',
      'widgets-api',
      7,
      'https://dev.azure.com/contoso',
    ]);
  });

  it('rejects other URLs with a usage error', () => {
    expect(() => parsePrUrl('https://github.com/a/b/pull/1')).toThrow(/unrecognized/);
    expect(() => parsePrUrl(undefined as unknown as string)).toThrow(/unrecognized/);
  });
});

describe('parseWorkItemUrl', () => {
  it('parses the modern form and keeps encoded project names', () => {
    const ref = parseWorkItemUrl(
      'https://dev.azure.com/contoso/My%20Project/_workitems/edit/321?x=1#y',
    );
    expect(ref).toMatchObject({
      org: 'contoso',
      project: 'My%20Project',
      projectName: 'My Project',
      id: 321,
      orgUrl: 'https://dev.azure.com/contoso',
      webUrl: 'https://dev.azure.com/contoso/My%20Project/_workitems/edit/321',
    });
  });

  it('parses the legacy visualstudio.com form', () => {
    expect(parseWorkItemUrl('https://contoso.visualstudio.com/Widgets/_workitems/edit/9/').id).toBe(
      9,
    );
  });

  it.each([
    'https://dev.azure.com/contoso/Widgets/_boards/board/t/Team/Stories?workitem=9',
    'https://dev.azure.com/contoso/Widgets/_queries/query/abc',
    'https://github.com/acme/widgets/issues/1',
    'not a url',
  ])('rejects %s', (url) => {
    expect(() => parseWorkItemUrl(url)).toThrow(/unrecognized Azure DevOps work item URL/);
  });

  it('rejects pull request URLs with a specific message (adversarial/invalid)', () => {
    expect(() =>
      parseWorkItemUrl('https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1'),
    ).toThrow(/pull request URL/);
  });
});

describe('isOrgUrl', () => {
  it.each([
    ['https://dev.azure.com/contoso/p/_apis/wit/attachments/1', true],
    ['https://dev.azure.com/Contoso/p/_apis/wit/attachments/1', true],
    ['https://contoso.visualstudio.com/p/_apis/wit/attachments/1', true],
    ['https://dev.azure.com/other/p/_apis/wit/attachments/1', false],
    ['https://dev.azure.com.evil.com/contoso/p', false],
    ['http://dev.azure.com/contoso/p', false],
    ['https://evil.com/dev.azure.com/contoso/', false],
    ['nonsense', false],
  ])('%s -> %s', (url, expected) => {
    expect(isOrgUrl(url, 'contoso')).toBe(expected);
  });
});
