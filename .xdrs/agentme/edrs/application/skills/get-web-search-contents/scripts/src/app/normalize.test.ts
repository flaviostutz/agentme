import { cutAfterPrompt, normalizeAnswer, normalizeResults, truncate } from './normalize';

describe('normalizeResults', () => {
  it('cleans URLs, drops sponsored or internal links, removes duplicates and numbers the rest', () => {
    const results = normalizeResults([
      { title: ' First ', href: 'https://a.org/x?utm_source=z', snippet: ' s1 ' },
      { title: 'Duplicate', href: 'https://a.org/x', snippet: 's' },
      { title: 'Ad', href: 'https://www.google.com/aclk?x=1', snippet: '' },
      {
        title: 'Wrapped',
        href: 'https://www.google.com/url?q=https%3A%2F%2Fb.org%2F',
        snippet: 's2',
      },
      { title: '', href: 'https://c.org/', snippet: 'no title' },
    ]);
    expect(results).toEqual([
      { rank: 1, title: 'First', url: 'https://a.org/x', snippet: 's1' },
      { rank: 2, title: 'Wrapped', url: 'https://b.org/', snippet: 's2' },
    ]);
  });

  it('caps the list at 10 and snippets at 300 characters', () => {
    const raw = Array.from({ length: 15 }, (_, i) => ({
      title: `T${i}`,
      href: `https://e.org/${i}`,
      snippet: 'x'.repeat(500),
    }));
    const results = normalizeResults(raw);
    expect(results).toHaveLength(10);
    expect(results[0]?.snippet).toHaveLength(300);
    expect(results[9]?.rank).toBe(10);
  });
});

describe('normalizeAnswer and helpers', () => {
  it('keeps unique external citations and truncates the text', () => {
    const answer = normalizeAnswer('duckduckgo-search-assist', {
      text: 'a'.repeat(3000),
      links: [
        { text: 'Src', href: 'https://s.org/a?utm_x=1' },
        { text: 'Src again', href: 'https://s.org/a' },
        { text: 'Self', href: 'https://duckduckgo.com/x' },
      ],
    });
    expect(answer.text).toHaveLength(2000);
    expect(answer.citations).toEqual([{ title: 'Src', url: 'https://s.org/a' }]);
  });

  it('uses the host as title, unwraps google redirects and drops google account or policy links', () => {
    const answer = normalizeAnswer('google-ai-mode', {
      text: 't',
      links: [
        { text: '', href: 'https://www.google.com/url?sa=i&url=https://www.redcross.org/&ved=1' },
        { text: 'Privacy', href: 'https://policies.google.com/privacy' },
        { text: 'Help', href: 'https://support.google.com/websearch/answer/1' },
        { text: 'History', href: 'https://myactivity.google.com/x' },
      ],
    });
    expect(answer.citations).toEqual([
      { title: 'www.redcross.org', url: 'https://www.redcross.org/' },
    ]);
  });

  it('uses an explicit text and limit when given', () => {
    const answer = normalizeAnswer(
      'google-ai-mode',
      { text: 'ignored', links: [] },
      'b'.repeat(50),
      10,
    );
    expect(answer.text).toBe(`${'b'.repeat(9)}…`);
  });

  it('truncate squashes whitespace', () => {
    expect(truncate('a \n  b', 10)).toBe('a b');
  });

  it('cutAfterPrompt removes the echoed prompt and anything before it', () => {
    expect(cutAfterPrompt('head\nhow to x\nanswer one\nhow to x\nanswer two', 'how to x')).toBe(
      'answer two',
    );
    expect(cutAfterPrompt('no echo here', 'prompt')).toBe('no echo here');
  });
});
