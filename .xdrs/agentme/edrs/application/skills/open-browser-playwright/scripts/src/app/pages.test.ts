import {
  formatResult,
  hostOf,
  isAuthenticatedPage,
  isLoaded,
  selectTabsToClose,
  userExpression,
} from './pages';

describe('hostOf', () => {
  it('returns host with port, or empty', () => {
    expect(hostOf('https://a.example.com:8443/x')).toBe('a.example.com:8443');
    expect(hostOf('nope')).toBe('');
  });
});

describe('isAuthenticatedPage', () => {
  it('rejects sign-in pages and identity providers', () => {
    expect(isAuthenticatedPage('Dashboard', 'https://app.example.com/')).toBe(true);
    expect(isAuthenticatedPage('', 'https://app.example.com/')).toBe(false);
    expect(isAuthenticatedPage('Sign in to your account', 'https://app.example.com/')).toBe(false);
    expect(isAuthenticatedPage('Loading...', 'https://app.example.com/')).toBe(false);
    expect(isAuthenticatedPage('Designing a signing flow', 'https://app.example.com/')).toBe(true);
    expect(isAuthenticatedPage('Welcome', 'https://login.microsoftonline.com/common')).toBe(false);
    expect(isAuthenticatedPage('Welcome', 'https://accounts.google.com/x')).toBe(false);
    expect(isAuthenticatedPage('Welcome', 'about:blank')).toBe(false);
  });
});

describe('isLoaded', () => {
  it('requires a complete, non-blank page', () => {
    expect(isLoaded({ title: 't', url: 'https://a.example.com', ready: true })).toBe(true);
    expect(isLoaded({ title: 't', url: 'about:blank', ready: true })).toBe(false);
    expect(isLoaded({ title: 't', url: 'https://a.example.com', ready: false })).toBe(false);
  });
});

describe('userExpression', () => {
  const run = (host: string, bodyText: string, checkHost: string): unknown =>
    new Function('location', 'document', `return ${userExpression(checkHost)};`)(
      { host },
      { body: { innerText: bodyText } },
    );

  it('only reports an email on the check host', () => {
    expect(
      run('myaccount.example.com', 'Signed in as me@example.com', 'myaccount.example.com'),
    ).toBe('me@example.com');
    expect(run('login.example.com', 'me@example.com', 'myaccount.example.com')).toBe('');
    expect(run('myaccount.example.com', 'no email here', 'myaccount.example.com')).toBe('');
    expect(userExpression('a"b')).toMatch(/"a\\"b"/);
  });
});

describe('selectTabsToClose', () => {
  it('keeps baseline tabs and the newest task tab', () => {
    const pages = [{ targetId: 'B1' }, { targetId: 'T1' }, { targetId: 'T2' }, { targetId: 'T3' }];
    const result = selectTabsToClose(pages, ['B1'], { T1: 10, T2: 30, T3: 20 });
    expect(result.keep?.targetId).toBe('T2');
    expect(result.close).toEqual(['T1', 'T3']);
  });

  it('handles ties, unknown load times and no task tabs', () => {
    const pages = [{ targetId: 'T1' }, { targetId: 'T2' }];
    expect(selectTabsToClose(pages, [], { T1: 5, T2: 5 }).keep?.targetId).toBe('T1');
    expect(selectTabsToClose(pages, [], { T2: 5 }).keep?.targetId).toBe('T2');
    expect(selectTabsToClose(pages, [], {}).keep?.targetId).toBe('T1');
    expect(selectTabsToClose(pages, ['T1', 'T2'], {})).toEqual({ close: [] });
  });
});

describe('formatResult', () => {
  it('prints the documented lines', () => {
    expect(
      formatResult({
        result: 'opened',
        user: 'skipped',
        session: 's1',
        page: { title: 'Example', url: 'https://example.com/' },
        port: 9390,
      }),
    ).toBe(
      [
        'RESULT: opened',
        'USER: skipped',
        'SESSION: s1',
        'PAGE: [Example](https://example.com/)',
        'CDP: http://127.0.0.1:9390',
      ].join('\n'),
    );
    expect(formatResult({ result: 'x', user: 'none', session: 's', port: 1 })).toMatch(
      /PAGE: \[\]\(\)/,
    );
  });
});
