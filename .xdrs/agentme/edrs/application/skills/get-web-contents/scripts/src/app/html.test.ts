import { extractLinks, extractTitle, htmlToText } from './html';

const PAGE = `<!doctype html><html><head><title> My &amp; Page </title><style>.a{}</style></head>
<body><script>var x = "<p>no</p>";</script><!-- hidden -->
<h1>Story</h1><p>As a <b>user</b> I want&nbsp;this &#38; that &#x41; &unknown;.</p>
<ul><li>one</li><li>two</li></ul>
<table><tr><td>a</td><td>b</td></tr></table>
<a href="/rel#frag">rel</a><a href='https://other.example/x'>abs</a><a href="mailto:x@y.z">m</a>
<a href="https://other.example/x#again">dup</a><a href="http://[bad">bad</a>
</body></html>`;

describe('htmlToText', () => {
  it('keeps headings and list markers, drops scripts, styles and comments, decodes entities', () => {
    const text = htmlToText(PAGE);
    expect(text).toContain('# Story');
    expect(text).toContain('As a user I want this & that A &unknown;.');
    expect(text).toContain('- one\n- two');
    expect(text).toContain('a | b |');
    expect(text).not.toMatch(/var x|hidden|\.a\{/);
  });

  it('handles fragments without a body element', () => {
    expect(htmlToText('<head><title>t</title></head><p>hello</p>')).toBe('hello');
  });
});

describe('extractTitle', () => {
  it('decodes and trims the title', () => {
    expect(extractTitle(PAGE)).toBe('My & Page');
  });
  it('returns undefined without a title', () => {
    expect(extractTitle('<p>x</p>')).toBeUndefined();
  });
});

describe('extractLinks', () => {
  it('resolves, de-duplicates and keeps only http(s) links without fragments', () => {
    expect(extractLinks(PAGE, 'https://example.com/dir/')).toEqual([
      'https://example.com/rel',
      'https://other.example/x',
    ]);
  });

  it('caps the number of links', () => {
    const many = Array.from({ length: 80 }, (_v, index) => `<a href="/p${index}">x</a>`).join('');
    expect(extractLinks(many, 'https://example.com')).toHaveLength(50);
  });
});
