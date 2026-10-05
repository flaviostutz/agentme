import { isOrgUrl } from './urls';

const ATTACHMENT_PATH = '/_apis/wit/attachments/';

const decodeEntities = (text: string): string =>
  text
    .replaceAll('&amp;', '&')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>');

export const isAttachmentUrl = (value: string, org: string): boolean =>
  isOrgUrl(value, org) && new URL(value).pathname.includes(ATTACHMENT_PATH);

// Stable key so the relation URL and the inline image URL of the same file count once.
export const attachmentKey = (value: string): string => {
  const url = new URL(value);
  return `${url.hostname.toLowerCase()}${url.pathname.toLowerCase()}`;
};

// Image sources inside rich text fields that point at attachments of the same organization.
export const inlineAttachmentUrls = (html: string, org: string): string[] => {
  const urls: string[] = [];
  for (const match of html.matchAll(/<img\s[^>]*?src="([^"]*)"/g)) {
    const url = decodeEntities(match[1] ?? '');
    if (isAttachmentUrl(url, org)) urls.push(url);
  }
  return urls;
};

// Full http(s) URLs in HTML or text, without attachment links, the item itself and trailing punctuation.
export const extractLinks = (text: string, ownUrl: string, org: string): string[] => {
  const urls = new Set<string>();
  for (const match of decodeEntities(text).matchAll(/https?:\/\/[^\s)<>\]"'`]+/g)) {
    const url = match[0].replace(/[.,;:!?]+$/, '');
    if (URL.canParse(url) && url !== ownUrl && !isAttachmentUrl(url, org)) urls.add(url);
  }
  return [...urls];
};
