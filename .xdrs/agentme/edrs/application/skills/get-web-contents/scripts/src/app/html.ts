import { MAX_LINKS } from '../shared/constants';

const NAMED_ENTITIES: Record<string, string> = {
  amp: '&',
  lt: '<',
  gt: '>',
  quot: '"',
  apos: "'",
  nbsp: ' ',
};

const decodeEntities = (text: string): string =>
  text.replaceAll(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (match, body: string) => {
    if (body.startsWith('#')) {
      const code =
        body[1]?.toLowerCase() === 'x' ? Number.parseInt(body.slice(2), 16) : Number(body.slice(1));
      return Number.isInteger(code) && code > 0 && code <= 1_114_111
        ? String.fromCodePoint(code)
        : match;
    }
    return NAMED_ENTITIES[body.toLowerCase()] ?? match;
  });

const dropHidden = (html: string): string =>
  html
    .replaceAll(/<!--[\s\S]*?-->/g, '')
    .replaceAll(/<(script|style|noscript|svg|template)\b[\s\S]*?<\/\1\s*>/gi, '');

export const extractTitle = (html: string): string | undefined => {
  const match = /<title\b[^>]*>([\s\S]*?)<\/title\s*>/i.exec(html);
  const title = match
    ? decodeEntities(match[1] ?? '')
        .replaceAll(/\s+/g, ' ')
        .trim()
    : '';
  return title || undefined;
};

export const extractLinks = (html: string, base: string): string[] => {
  const links = new Set<string>();
  const pattern = /<a\b[^>]*?\shref\s*=\s*(?:"([^"]*)"|'([^']*)')/gi;
  for (const match of dropHidden(html).matchAll(pattern)) {
    try {
      const url = new URL(decodeEntities(match[1] ?? match[2] ?? ''), base);
      if (url.protocol === 'http:' || url.protocol === 'https:') {
        url.hash = '';
        links.add(url.href);
      }
    } catch {
      // Unparseable hrefs are ignored.
    }
  }
  return [...links].slice(0, MAX_LINKS);
};

// Converts HTML to readable plain text: headings and list items keep a markdown marker.
export const htmlToText = (html: string): string => {
  const body =
    /<body\b[^>]*>([\s\S]*)<\/body\s*>/i.exec(html)?.[1] ??
    html.replace(/<head\b[\s\S]*?<\/head\s*>/i, '');
  const text = dropHidden(body)
    .replaceAll(
      /<h([1-6])\b[^>]*>/gi,
      (_match, level: string) => `\n\n${'#'.repeat(Number(level))} `,
    )
    .replaceAll(/<\/h[1-6]\s*>/gi, '\n\n')
    .replaceAll(/<li\b[^>]*>/gi, '\n- ')
    .replaceAll(
      /<br\s*\/?>|<\/?(p|div|section|article|header|footer|ul|ol|table|tr|blockquote|pre)\b[^>]*>/gi,
      '\n',
    )
    .replaceAll(/<\/t[dh]\s*>/gi, ' | ')
    .replaceAll(/<[^>]+>/g, '');
  return decodeEntities(text)
    .split('\n')
    .map((line) => line.replaceAll(/[ \t]+/g, ' ').trim())
    .join('\n')
    .replaceAll(/\n{3,}/g, '\n\n')
    .trim();
};
