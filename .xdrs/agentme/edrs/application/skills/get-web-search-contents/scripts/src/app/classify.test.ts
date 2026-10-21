import { classifyPage } from './classify';

const probe = (
  url: string,
  title = 'Page',
  text = '',
): { url: string; title: string; text: string } => ({
  url,
  title,
  text,
});

describe('classifyPage', () => {
  it('is ready for a normal results page', () => {
    expect(
      classifyPage('duckduckgo', probe('https://duckduckgo.com/?q=x', 'x at DuckDuckGo')),
    ).toBe('ready');
  });

  it('detects a DuckDuckGo challenge', () => {
    expect(
      classifyPage(
        'duckduckgo',
        probe('https://duckduckgo.com/', 'DuckDuckGo', 'Unfortunately, bots use DuckDuckGo too.'),
      ),
    ).toBe('captcha');
  });

  it('detects the Google sorry page and consent redirect', () => {
    expect(classifyPage('google', probe('https://www.google.com/sorry/index?continue=x'))).toBe(
      'captcha',
    );
    expect(classifyPage('google', probe('https://consent.google.com/m?continue=x'))).toBe(
      'consent',
    );
  });

  it('detects login and rate limit pages', () => {
    expect(classifyPage('google', probe('https://accounts.google.com/v3/signin/identifier'))).toBe(
      'login-required',
    );
    expect(classifyPage('google', probe('https://x.org', 'Page', 'Please sign in'))).toBe(
      'login-required',
    );
    expect(classifyPage('duckduckgo', probe('https://duckduckgo.com/', 'Too Many Requests'))).toBe(
      'blocked',
    );
  });
});
