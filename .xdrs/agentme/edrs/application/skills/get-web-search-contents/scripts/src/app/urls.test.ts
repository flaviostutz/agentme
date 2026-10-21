import { aiModeUrl, cleanUrl, searchUrl } from './urls';

describe('cleanUrl', () => {
  it('keeps a direct URL and strips tracking parameters and the fragment', () => {
    expect(cleanUrl('https://example.org/a?id=1&utm_source=x&srsltid=abc#top')).toBe(
      'https://example.org/a?id=1',
    );
  });

  it('unwraps a Google redirect to its destination', () => {
    expect(cleanUrl('https://www.google.com/url?q=https%3A%2F%2Fexample.org%2Fpage&sa=U')).toBe(
      'https://example.org/page',
    );
    expect(cleanUrl('https://www.google.nl/url?url=https%3A%2F%2Fexample.org%2F&ved=1')).toBe(
      'https://example.org/',
    );
  });

  it('rejects non-http schemes, engine-owned hosts and garbage', () => {
    expect(cleanUrl('javascript:alert(1)')).toBeUndefined();
    expect(cleanUrl('mailto:a@b.c')).toBeUndefined();
    expect(cleanUrl('https://www.google.com/search?q=x')).toBeUndefined();
    expect(cleanUrl('https://duckduckgo.com/?q=x')).toBeUndefined();
    expect(cleanUrl('/relative/path')).toBeUndefined();
    expect(cleanUrl('https://www.google.com/url?q=javascript:alert(1)')).toBeUndefined();
  });

  it('keeps pages hosted on other Google subdomains', () => {
    expect(cleanUrl('https://play.google.com/store/apps/details?id=x&hl=en')).toBe(
      'https://play.google.com/store/apps/details?id=x&hl=en',
    );
  });
});

describe('search URLs', () => {
  it('encodes non-ASCII text and operators', () => {
    expect(searchUrl('duckduckgo', 'água site:a.org', {})).toBe(
      'https://duckduckgo.com/?q=%C3%A1gua%20site%3Aa.org',
    );
  });

  it('adds language and region', () => {
    expect(searchUrl('google', 'x', { lang: 'pt-BR', region: 'br' })).toBe(
      'https://www.google.com/search?q=x&hl=pt-BR&gl=br',
    );
    expect(searchUrl('duckduckgo', 'x', { region: 'nl' })).toBe(
      'https://duckduckgo.com/?q=x&kl=nl-nl',
    );
    expect(aiModeUrl('why?', {})).toBe('https://www.google.com/search?udm=50&q=why%3F&hl=en');
    expect(aiModeUrl('a', { lang: 'de', region: 'de' })).toBe(
      'https://www.google.com/search?udm=50&q=a&hl=de&gl=de',
    );
  });
});
