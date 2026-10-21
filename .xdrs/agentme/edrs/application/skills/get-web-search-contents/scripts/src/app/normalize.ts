import {
  MAX_AI_TEXT_CHARS,
  MAX_CITATIONS,
  MAX_RESULTS,
  MAX_SNIPPET_CHARS,
  MAX_TITLE_CHARS,
} from '../shared/constants';

import type { AiAnswer, RawAnswer, RawResult, SearchResult } from './types';
import { cleanUrl } from './urls';

const squash = (text: string): string => text.replaceAll(/\s+/g, ' ').trim();

export const truncate = (text: string, max: number): string => {
  const clean = squash(text);
  return clean.length <= max ? clean : `${clean.slice(0, max - 1).trimEnd()}…`;
};

// Cleans URLs, drops entries that are not external pages, removes duplicates and caps the list.
export const normalizeResults = (raw: readonly RawResult[]): SearchResult[] => {
  const seen = new Set<string>();
  return raw
    .flatMap((item) => {
      const url = cleanUrl(item.href);
      if (!url || seen.has(url)) return [];
      seen.add(url);
      return [
        {
          title: truncate(item.title, MAX_TITLE_CHARS),
          url,
          snippet: truncate(item.snippet, MAX_SNIPPET_CHARS),
        },
      ];
    })
    .filter((item) => item.title.length > 0)
    .slice(0, MAX_RESULTS)
    .map((item, index) => ({ rank: index + 1, ...item }));
};

export const normalizeAnswer = (
  source: AiAnswer['source'],
  raw: RawAnswer,
  text: string = raw.text,
  maxChars: number = MAX_AI_TEXT_CHARS,
): AiAnswer => {
  const seen = new Set<string>();
  const citations = raw.links
    .flatMap((link) => {
      const url = cleanUrl(link.href);
      if (!url || seen.has(url)) return [];
      seen.add(url);
      return [
        { title: truncate(squash(link.text) || new URL(url).hostname, MAX_TITLE_CHARS), url },
      ];
    })
    .slice(0, MAX_CITATIONS);
  return { source, text: truncate(text, maxChars), citations };
};

// Keeps only the answer: the conversation region repeats the prompt, so cut after its last echo.
export const cutAfterPrompt = (text: string, prompt: string): string => {
  const at = text.lastIndexOf(prompt);
  return at === -1 ? text : text.slice(at + prompt.length).trim();
};
