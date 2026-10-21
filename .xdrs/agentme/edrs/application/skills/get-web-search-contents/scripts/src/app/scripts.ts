/* eslint-disable complexity, unicorn/prefer-dom-node-text-content */
// Page-side code cannot be split into shared helpers, so a few style rules are off for this file.
import type { PageProbe, RawAnswer, RawSearchPage } from './types';

// Every function below runs inside the page through `playwright-cli eval`: it is serialized with
// toString(), so it must not use imports, closures over module scope, or other helpers.
// Selectors come from the live spike notes; they break when the engines change markup.

export const probePage = (): PageProbe => ({
  url: location.href,
  title: document.title,
  text: (document.body?.innerText ?? '').slice(0, 600),
});

export const extractDuckResults = (): RawSearchPage => {
  const results = Array.from(document.querySelectorAll('article[data-testid="result"]')).map(
    (article) => {
      const link = article.querySelector('a[data-testid="result-title-a"]');
      const title = link?.textContent ?? '';
      const marked = article.querySelector('[data-testid="snippet"]')?.textContent;
      // Some layouts have no snippet marker: the snippet is what is left after the host, URL and title lines.
      const leftover = ((article as HTMLElement).innerText ?? '')
        .split('\n')
        .map((line) => line.trim())
        .filter(
          (line) =>
            line.length > 0 && line !== title && !/^https?:\/\//.test(line) && /\s/.test(line),
        )
        .join(' ');
      return { title, href: link?.getAttribute('href') ?? '', snippet: marked ?? leftover };
    },
  );
  return {
    results,
    assistAvailable: document.querySelector('[data-testid="duckassist-action-button"]') !== null,
  };
};

export const clickDuckAssist = (): boolean => {
  const button = document.querySelector<HTMLElement>('[data-testid="duckassist-action-button"]');
  button?.click();
  return button !== null;
};

export const extractDuckAssist = (): RawAnswer => {
  const answer = document.querySelector('[data-testid="duckassist-answer-content"]');
  return {
    text: answer?.textContent ?? '',
    links: Array.from(answer?.querySelectorAll('a[href]') ?? []).map((a) => ({
      text: a.textContent ?? '',
      href: a.getAttribute('href') ?? '',
    })),
  };
};

export const extractGoogleResults = (): RawSearchPage => {
  const root = document.querySelector('#rso') ?? document.querySelector('#search');
  const seen = new Set<string>();
  const results: { title: string; href: string; snippet: string }[] = [];
  for (const anchor of Array.from(root?.querySelectorAll('a') ?? [])) {
    const heading = anchor.querySelector('h3');
    const href = anchor.getAttribute('href') ?? '';
    if (!heading || !href || seen.has(href)) continue;
    if (anchor.closest('[data-text-ad], [data-ad-slot], #tads, #tadsb, #bottomads')) continue;
    if (/\/aclk\?|googleadservices\./.test(href)) continue;
    seen.add(href);
    const title = heading.textContent ?? '';
    const container = anchor.closest('.tF2Cxc, .MjjYud, [data-hveid]') ?? anchor.parentElement;
    const snippetNode = container?.querySelector(
      '[data-sncf], .VwiC3b, [style*="-webkit-line-clamp"]',
    );
    const snippet = (snippetNode?.textContent ?? container?.textContent ?? '').replace(title, '');
    results.push({ title, href, snippet });
  }
  return { results, assistAvailable: false };
};

// Reads only the conversation region: the page also lists the person's earlier AI Mode threads.
export const extractAiMode = (): RawAnswer => {
  const region = document.querySelector('[role="main"]');
  // a.href resolves the relative /url?...url= wrappers that carry the source addresses.
  const links = Array.from(region?.querySelectorAll<HTMLAnchorElement>('a[href]') ?? []).map(
    (a) => ({ text: a.textContent ?? '', href: a.href || (a.getAttribute('href') ?? '') }),
  );
  return { text: (region as HTMLElement | null)?.innerText ?? '', links };
};

// Opens the citation chips so the source links render; never touches share or save controls.
export const clickAiCitations = (): number => {
  const chips = Array.from(
    document.querySelectorAll<HTMLElement>('[role="main"] button[data-amic="true"]'),
  );
  for (const chip of chips.slice(0, 5)) chip.click();
  return chips.length;
};

// Clicks only the least invasive choice of a consent dialog; returns its label or an empty string.
export const clickConsentReject = (): string => {
  const wanted = /^(?:reject all|decline all|only necessary|necessary only|refuse all|reject)$/i;
  const button = Array.from(
    document.querySelectorAll<HTMLElement>('button, [role="button"], input[type="submit"]'),
  ).find((node) =>
    wanted.test((node.textContent ?? (node as HTMLInputElement).value ?? '').trim()),
  );
  button?.click();
  return button ? (button.textContent ?? '').trim() : '';
};
