import type { Engine, PageProbe, PageState } from './types';

const CAPTCHA_TEXT =
  /bots use duckduckgo too|select all squares|unusual traffic from your computer|not a robot|are you a robot|confirm this search was made by a human|before you continue to google|our systems have detected unusual traffic/i;
const BLOCKED_TEXT =
  /too many requests|rate limit|access denied|temporarily blocked|error 403|429/i;
const LOGIN_TEXT = /sign in to continue|log in to continue|please sign in/i;

// Decides what a page is from its address, title and the first characters of its text.
export const classifyPage = (engine: Engine, probe: PageProbe): PageState => {
  const url = probe.url.toLowerCase();
  const haystack = `${probe.title}\n${probe.text}`;
  if (url.includes('consent.google.') || url.includes('/consent')) return 'consent';
  if (url.includes('/sorry/') || CAPTCHA_TEXT.test(haystack)) return 'captcha';
  if (engine === 'google' && /accounts\.google\.com\/(?:v3\/)?signin/.test(url))
    return 'login-required';
  if (LOGIN_TEXT.test(haystack)) return 'login-required';
  if (BLOCKED_TEXT.test(probe.title)) return 'blocked';
  return 'ready';
};
