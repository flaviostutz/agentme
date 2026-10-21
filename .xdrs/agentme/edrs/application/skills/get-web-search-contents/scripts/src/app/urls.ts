import type { Engine } from './types';

const TRACKING_PARAMS = /^(?:utm_.+|srsltid|gclid|gclsrc|fbclid|msclkid|dclid|ved|ei|sa|usg)$/i;
const ENGINE_HOSTS =
  /^(?:(?:www|consent|accounts|support|policies|myaccount|myactivity)\.)?google\.[a-z.]+$|(?:^|\.)duckduckgo\.com$|^duck\.ai$|(?:^|\.)gstatic\.com$/i;

const parse = (value: string): URL | undefined => {
  try {
    return new URL(value);
  } catch {
    return undefined;
  }
};

const isWrapper = (url: URL): boolean =>
  /(?:^|\.)google\.[a-z.]+$/i.test(url.hostname) && url.pathname === '/url';

const stripTracking = (url: URL): URL => {
  const clean = new URL(url.toString());
  for (const key of [...clean.searchParams.keys()].filter((key) => TRACKING_PARAMS.test(key)))
    clean.searchParams.delete(key);
  clean.hash = '';
  return clean;
};

// Returns the destination of a result link: unwraps engine redirects, drops tracking parameters,
// and rejects anything that is not an external http(s) page.
export const cleanUrl = (href: string): string | undefined => {
  const first = parse(href);
  if (!first) return undefined;
  const wrapped = isWrapper(first)
    ? (first.searchParams.get('q') ?? first.searchParams.get('url') ?? undefined)
    : undefined;
  const target = wrapped ? parse(wrapped) : first;
  if (!target || !/^https?:$/.test(target.protocol)) return undefined;
  if (ENGINE_HOSTS.test(target.hostname)) return undefined;
  return stripTracking(target).toString();
};

export const searchUrl = (
  engine: Engine,
  query: string,
  options: { lang?: string; region?: string },
): string => {
  const encoded = encodeURIComponent(query);
  if (engine === 'duckduckgo') {
    const region = options.region ? `&kl=${options.region}-${options.lang ?? options.region}` : '';
    return `https://duckduckgo.com/?q=${encoded}${region}`;
  }
  const lang = options.lang ?? 'en';
  const region = options.region ? `&gl=${options.region}` : '';
  return `https://www.google.com/search?q=${encoded}&hl=${lang}${region}`;
};

export const aiModeUrl = (prompt: string, options: { lang?: string; region?: string }): string => {
  const region = options.region ? `&gl=${options.region}` : '';
  return `https://www.google.com/search?udm=50&q=${encodeURIComponent(prompt)}&hl=${options.lang ?? 'en'}${region}`;
};
