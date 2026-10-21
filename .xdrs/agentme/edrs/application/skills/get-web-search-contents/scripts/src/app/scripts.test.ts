/**
 * @jest-environment jsdom
 */
import {
  clickAiCitations,
  clickConsentReject,
  clickDuckAssist,
  extractAiMode,
  extractDuckAssist,
  extractDuckResults,
  extractGoogleResults,
  probePage,
} from './scripts';

// jsdom has no layout, so innerText is approximated with textContent.
beforeAll(() => {
  Object.defineProperty(HTMLElement.prototype, 'innerText', {
    configurable: true,
    get(this: HTMLElement) {
      return this.textContent ?? '';
    },
  });
});

const setBody = (html: string): void => {
  document.body.innerHTML = html;
};

describe('probePage', () => {
  it('returns the address, title and a bounded text sample', () => {
    setBody(`<p>${'x'.repeat(1000)}</p>`);
    document.title = 'Synthetic';
    const probe = probePage();
    expect(probe.title).toBe('Synthetic');
    expect(probe.text).toHaveLength(600);
    expect(probe.url).toContain('http');
  });
});

describe('DuckDuckGo page functions', () => {
  it('reads organic results and ignores the ad block', () => {
    setBody(`
      <div><span data-testid="ad-badge-1">Ads</span><a href="https://ad.example/">Ad link</a></div>
      <article data-testid="result">
        <a data-testid="result-title-a" href="https://one.example/a">One</a>
        <div data-testid="snippet">First snippet</div>
      </article>
      <article data-testid="result">
        <a data-testid="result-title-a" href="https://two.example/b">Two</a>
        <div data-testid="snippet">Second snippet</div>
      </article>
      <button data-testid="duckassist-action-button">Search Assist</button>`);
    const page = extractDuckResults();
    expect(page.results).toEqual([
      { title: 'One', href: 'https://one.example/a', snippet: 'First snippet' },
      { title: 'Two', href: 'https://two.example/b', snippet: 'Second snippet' },
    ]);
    expect(page.assistAvailable).toBe(true);
  });

  it('falls back to the leftover text when the layout has no snippet marker', () => {
    setBody(`
      <article data-testid="result">
        <span>one.example</span>
        <span>https://one.example</span>
        <a data-testid="result-title-a" href="https://one.example/a">One title</a>
        <p>A readable snippet about it.</p>
      </article>`);
    const text = document.querySelector('article')!;
    Object.defineProperty(text, 'innerText', {
      configurable: true,
      value: 'one.example\nhttps://one.example\nOne title\nA readable snippet about it.',
    });
    expect(extractDuckResults().results[0]?.snippet).toBe('A readable snippet about it.');
  });

  it('reports no Search Assist button and an empty page', () => {
    setBody('<p>nothing</p>');
    expect(extractDuckResults()).toEqual({ results: [], assistAvailable: false });
  });

  it('clicks Search Assist once and reads the answer with its sources', () => {
    setBody(`<button data-testid="duckassist-action-button">Search Assist</button>
      <div data-testid="duckassist-answer-content">Answer text <a href="https://src.example/p">Src</a></div>`);
    const clicks: number[] = [];
    document.querySelector('button')?.addEventListener('click', () => clicks.push(1));
    expect(clickDuckAssist()).toBe(true);
    expect(clicks).toEqual([1]);
    expect(extractDuckAssist()).toEqual({
      text: 'Answer text Src',
      links: [{ text: 'Src', href: 'https://src.example/p' }],
    });
  });

  it('returns false and an empty answer when Search Assist is absent', () => {
    setBody('<p>x</p>');
    expect(clickDuckAssist()).toBe(false);
    expect(extractDuckAssist()).toEqual({ text: '', links: [] });
  });
});

describe('Google page functions', () => {
  it('reads organic results and drops sponsored ones and duplicates', () => {
    setBody(`
      <div id="tads"><a href="https://ad.example/"><h3>Sponsored</h3></a></div>
      <div id="rso">
        <div class="tF2Cxc">
          <a href="https://one.example/a"><h3>One</h3></a>
          <div class="VwiC3b">Snippet one</div>
        </div>
        <div class="tF2Cxc"><a href="https://one.example/a"><h3>One again</h3></a></div>
        <div class="tF2Cxc"><a href="https://www.google.com/aclk?x=1"><h3>Ad by click</h3></a></div>
        <div class="tF2Cxc" data-text-ad="1"><a href="https://ad2.example/"><h3>Ad two</h3></a></div>
        <div class="tF2Cxc"><a href="https://two.example/b"><h3>Two</h3></a><span>Body of two</span></div>
      </div>`);
    const page = extractGoogleResults();
    expect(page.results.map((r) => r.href)).toEqual([
      'https://one.example/a',
      'https://two.example/b',
    ]);
    expect(page.results[0]?.snippet).toBe('Snippet one');
    expect(page.results[1]?.snippet).toContain('Body of two');
    expect(page.assistAvailable).toBe(false);
  });

  it('reads only the conversation region for AI Mode, never other page areas', () => {
    setBody(`
      <nav>Recent thread: my private plan <a href="https://private.example/t">t</a></nav>
      <div role="main">Prompt text Answer text
        <a href="https://www.google.com/url?q=https%3A%2F%2Fsrc.example%2Fp">Source</a>
      </div>`);
    const answer = extractAiMode();
    expect(answer.text).toContain('Answer text');
    expect(answer.text).not.toContain('private plan');
    expect(answer.links).toHaveLength(1);
  });

  it('clicks citation chips inside the main region only, never share controls', () => {
    setBody(`
      <button data-amic="true" id="outside">outside</button>
      <div role="main">
        <button data-amic="true" id="c1">Site (+2)</button>
        <button id="share">Share public link</button>
      </div>`);
    const clicked: string[] = [];
    document
      .querySelectorAll('button')
      .forEach((b) => b.addEventListener('click', () => clicked.push(b.id)));
    expect(clickAiCitations()).toBe(1);
    expect(clicked).toEqual(['c1']);
  });
});

describe('clickConsentReject', () => {
  it('clicks the reject choice and never the accept choice', () => {
    setBody('<button id="a">Accept all</button><button id="r">Reject all</button>');
    const clicked: string[] = [];
    document
      .querySelectorAll('button')
      .forEach((b) => b.addEventListener('click', () => clicked.push(b.id)));
    expect(clickConsentReject()).toBe('Reject all');
    expect(clicked).toEqual(['r']);
  });

  it('does nothing when only an accept choice exists', () => {
    setBody('<button id="a">Accept all</button>');
    expect(clickConsentReject()).toBe('');
  });
});
