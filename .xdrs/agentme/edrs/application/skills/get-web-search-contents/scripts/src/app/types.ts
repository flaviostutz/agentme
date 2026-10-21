export type Engine = 'duckduckgo' | 'google';

export type Status =
  'ok' | 'no-results' | 'captcha' | 'blocked' | 'login-required' | 'cap-reached' | 'error';

export type SearchResult = {
  rank: number;
  title: string;
  url: string;
  snippet: string;
};

export type AiAnswer = {
  source: 'duckduckgo-search-assist' | 'google-ai-mode';
  text: string;
  citations: { title: string; url: string }[];
};

export type SearchBudget = { used: number; max: number };

// Shapes returned by the functions that run inside the page (see scripts.ts).
export type RawResult = { title: string; href: string; snippet: string };
export type RawLink = { text: string; href: string };
export type RawSearchPage = { results: RawResult[]; assistAvailable: boolean };
export type RawAnswer = { text: string; links: RawLink[] };
export type PageProbe = { url: string; title: string; text: string };

export type PageState = 'ready' | 'captcha' | 'blocked' | 'consent' | 'login-required';
