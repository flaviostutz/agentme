import {
  MAX_BODY_BYTES,
  MAX_REDIRECTS,
  MAX_TEXT_CHARS,
  MIN_READABLE_CHARS,
} from '../shared/constants';

import { parseArgs, requireString } from './args';
import { extractLinks, extractTitle, htmlToText } from './html';
import type { Deps, HttpResult } from './ports';
import { blockedReason, parseWebUrl } from './url-guard';

const USAGE = 'page-get --url <url> [--allow-private]';

export type PageStatus =
  'ok' | 'needs-browser' | 'login-required' | 'not-found' | 'unreadable' | 'blocked' | 'error';

export type PageResult = {
  url: string;
  finalUrl: string;
  status: PageStatus;
  httpStatus: number | null;
  contentType: string | null;
  title: string | null;
  text: string | null;
  truncated: boolean;
  links: string[];
  note: string | null;
};

const LOGIN_HOSTS = [
  'login.microsoftonline.com',
  'login.live.com',
  'accounts.google.com',
  'okta.com',
  'auth0.com',
  'onelogin.com',
];
const LOGIN_PATH = /\/(login|signin|sign-in|sso|oauth2?\/authorize)(\/|$)/i;

const isLoginUrl = (url: URL, origin: URL): boolean => {
  if (LOGIN_HOSTS.some((host) => url.hostname === host || url.hostname.endsWith(`.${host}`)))
    return true;
  return LOGIN_PATH.test(url.pathname) && !LOGIN_PATH.test(origin.pathname);
};

const isHtml = (contentType: string): boolean => /html/i.test(contentType);
const isText = (contentType: string): boolean => /^text\/|json|xml|markdown/i.test(contentType);

const base = (url: string, finalUrl: string, httpStatus: number | null): PageResult => ({
  url,
  finalUrl,
  status: 'error',
  httpStatus,
  contentType: null,
  title: null,
  text: null,
  truncated: false,
  links: [],
  note: null,
});

const withNote = (result: PageResult, status: PageStatus, note: string): PageResult => ({
  ...result,
  status,
  note,
});

// A mount point for a client-side app, or a noscript hint that JavaScript is required.
const looksClientRendered = (html: string): boolean =>
  /<div\b[^>]*\bid\s*=\s*["']?(root|app|__next|__nuxt|svelte)\b/i.test(html) ||
  /<noscript\b[^>]*>[^<]*javascript/i.test(html);

const hasPasswordField = (html: string): boolean =>
  /<input\b[^>]*\btype\s*=\s*["']?password/i.test(html);

const classifyHtml = (result: PageResult, html: string, finalUrl: string): PageResult => {
  const text = htmlToText(html);
  const links = extractLinks(html, finalUrl);
  const title = extractTitle(html) ?? null;
  const filled = { ...result, title, links };
  if (hasPasswordField(html) && text.length < MIN_READABLE_CHARS * 5) {
    return withNote(
      filled,
      'login-required',
      'The page shows a sign-in form instead of the content.',
    );
  }
  if (text.length < MIN_READABLE_CHARS && (looksClientRendered(html) || text.length < 40)) {
    return withNote(
      filled,
      'needs-browser',
      'The page has almost no readable text; it probably renders its content with JavaScript.',
    );
  }
  const truncated = text.length > MAX_TEXT_CHARS;
  return { ...filled, status: 'ok', text: text.slice(0, MAX_TEXT_CHARS), truncated };
};

const classifyBody = (result: PageResult, response: HttpResult, finalUrl: string): PageResult => {
  const contentType = response.contentType ?? '';
  const typed = { ...result, contentType: contentType || null };
  if (!response.bytes) {
    return withNote(
      typed,
      'unreadable',
      `The response is larger than ${MAX_BODY_BYTES} bytes and was not read.`,
    );
  }
  if (contentType && !isHtml(contentType) && !isText(contentType)) {
    return withNote(
      typed,
      'unreadable',
      `The content type ${contentType} cannot be read as text (PDF, image or binary).`,
    );
  }
  const decoded = new TextDecoder('utf-8').decode(response.bytes);
  if (contentType && !isHtml(contentType)) {
    const truncated = decoded.length > MAX_TEXT_CHARS;
    return { ...typed, status: 'ok', text: decoded.slice(0, MAX_TEXT_CHARS), truncated };
  }
  return classifyHtml(typed, decoded, finalUrl);
};

const message = (error: unknown): string =>
  error instanceof Error ? error.message : String(error);

// Reads one web page with redirects checked hop by hop, never contacting private hosts.
export const readPage = async (
  rawUrl: string,
  allowPrivate: boolean,
  deps: Deps,
): Promise<PageResult> => {
  const origin = parseWebUrl(rawUrl);
  const allowedPrivateHost = allowPrivate ? origin.hostname.toLowerCase() : undefined;
  let current = origin;
  for (let hop = 0; hop <= MAX_REDIRECTS; hop += 1) {
    const result = base(origin.href, current.href, null);
    let response: HttpResult;
    try {
      const reason = await blockedReason(current.hostname, deps.dns, allowedPrivateHost);
      if (reason) {
        return withNote(
          result,
          'blocked',
          `${reason}. Local and private addresses are never contacted unless the human typed the URL.`,
        );
      }
      response = await deps.http.get(current.href, MAX_BODY_BYTES);
    } catch (error) {
      return withNote(result, 'error', message(error));
    }
    const withStatus = { ...result, httpStatus: response.status };
    if (response.status >= 300 && response.status < 400 && response.location) {
      try {
        current = parseWebUrl(new URL(response.location, current).href);
      } catch {
        return withNote(
          withStatus,
          'error',
          `Redirect to an unsupported location: ${response.location}`,
        );
      }
      if (isLoginUrl(current, origin)) {
        return withNote(
          { ...withStatus, finalUrl: current.href },
          'login-required',
          'The page redirects to a sign-in page.',
        );
      }
      continue;
    }
    if (response.status === 401 || response.status === 403) {
      return withNote(
        withStatus,
        'login-required',
        `The server answered HTTP ${response.status}; sign-in is probably required or automated reads are blocked.`,
      );
    }
    if (response.status === 404 || response.status === 410) {
      return withNote(withStatus, 'not-found', `The server answered HTTP ${response.status}.`);
    }
    if (response.status !== 200) {
      return withNote(withStatus, 'error', `The server answered HTTP ${response.status}.`);
    }
    return classifyBody(withStatus, response, current.href);
  }
  return withNote(
    base(origin.href, current.href, null),
    'error',
    `More than ${MAX_REDIRECTS} redirects.`,
  );
};

export const runPageGet = async (argv: readonly string[], deps: Deps): Promise<number> => {
  const args = parseArgs(argv);
  const url = requireString(args, 'url', USAGE);
  const result = await readPage(url, args['allow-private'] === true, deps);
  deps.output.out(`${JSON.stringify(result, undefined, 2)}\n`);
  return 0;
};
