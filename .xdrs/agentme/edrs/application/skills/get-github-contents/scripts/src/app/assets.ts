export type Asset = { name: string; url: string };

// Hosts a GitHub attachment may be served from; used for the first request and every redirect hop.
export const isAssetUrl = (value: string): boolean => {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    return false;
  }
  if (url.protocol !== 'https:') return false;
  const host = url.hostname.toLowerCase();
  if (host === 'github.com') {
    return /^\/(?:user-attachments\/|[^/]+\/[^/]+\/files\/)/.test(url.pathname);
  }
  return (
    host.endsWith('.githubusercontent.com') ||
    /^github-production-[\w-]+\.s3(?:\.[\w-]+)?\.amazonaws\.com$/.test(host)
  );
};

const decodeEntities = (text: string): string =>
  text
    .replaceAll('&amp;', '&')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>');

const attribute = (tag: string, name: string): string | undefined => {
  const match = new RegExp(`\\s${name}="([^"]*)"`).exec(tag);
  return match?.[1] === undefined ? undefined : decodeEntities(match[1]);
};

const nameFromUrl = (value: string): string => {
  const last = new URL(value).pathname.split('/').findLast(Boolean) ?? 'attachment';
  return decodeURIComponent(last);
};

// Reads image and file links out of the rendered HTML, which carries signed URLs for private repos.
export const extractAssets = (html: string): Asset[] => {
  const found = new Map<string, Asset>();
  for (const tag of html.match(/<img\s[^>]*>/g) ?? []) {
    const url = attribute(tag, 'src');
    if (url && isAssetUrl(url))
      found.set(url, { name: attribute(tag, 'alt') || nameFromUrl(url), url });
  }
  for (const match of html.matchAll(/<a\s[^>]*>([^<]*)<\/a>/g)) {
    const url = attribute(match[0], 'href');
    if (url && isAssetUrl(url) && !found.has(url)) {
      found.set(url, { name: decodeEntities(match[1] ?? '').trim() || nameFromUrl(url), url });
    }
  }
  return [...found.values()];
};

// Full http(s) URLs written in markdown text, without attachment links and trailing punctuation.
export const extractLinks = (markdown: string, ownUrl: string): string[] => {
  const urls = new Set<string>();
  for (const match of markdown.matchAll(/https?:\/\/[^\s)<>\]"'`]+/g)) {
    const url = match[0].replace(/[.,;:!?]+$/, '');
    if (!isAssetUrl(url) && url !== ownUrl && URL.canParse(url)) urls.add(url);
  }
  return [...urls];
};
