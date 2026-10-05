import { MAX_ATTACHMENTS, MAX_ATTACHMENT_BYTES, MAX_REDIRECTS } from '../shared/constants';

import { type Asset, isAssetUrl } from './assets';
import type { FilesPort, HttpPort } from './ports';

export type AttachmentResult =
  { name: string; url: string; path: string } | { name: string; url: string; error: string };

const EXTENSIONS: Record<string, string> = {
  'image/png': '.png',
  'image/jpeg': '.jpg',
  'image/gif': '.gif',
  'image/webp': '.webp',
  'image/svg+xml': '.svg',
  'application/pdf': '.pdf',
  'text/plain': '.txt',
};

const safeName = (name: string): string => name.replaceAll(/[^\w.-]+/g, '_').slice(0, 80) || 'file';

const withExtension = (name: string, contentType: string | undefined): string => {
  if (/\.\w{1,5}$/.test(name)) return name;
  return `${name}${EXTENSIONS[(contentType ?? '').split(';')[0]?.trim() ?? ''] ?? ''}`;
};

type Fetched =
  { ok: true; bytes: Uint8Array; contentType: string | undefined } | { ok: false; error: string };

// Follows redirects by hand so that every hop is checked against the GitHub asset hosts.
const fetchAsset = async (start: string, http: HttpPort): Promise<Fetched> => {
  let url = start;
  for (let hop = 0; hop <= MAX_REDIRECTS; hop += 1) {
    if (!isAssetUrl(url)) return { ok: false, error: `host not allowed: ${new URL(url).hostname}` };

    const response = await http.get(url, MAX_ATTACHMENT_BYTES);
    if (response.status >= 300 && response.status < 400 && response.location) {
      url = new URL(response.location, url).href;
    } else if (response.status !== 200) {
      return { ok: false, error: `download failed (HTTP ${response.status})` };
    } else if (!response.bytes) {
      return { ok: false, error: 'file is larger than 10 MB' };
    } else {
      return { ok: true, bytes: response.bytes, contentType: response.contentType };
    }
  }
  return { ok: false, error: 'too many redirects' };
};

// Downloads without credentials; a failure never aborts the read, it is reported per file.
export const downloadAssets = async (
  assets: readonly Asset[],
  dir: string,
  deps: { http: HttpPort; files: FilesPort },
): Promise<AttachmentResult[]> => {
  const results: AttachmentResult[] = [];
  for (const [index, asset] of assets.entries()) {
    if (index >= MAX_ATTACHMENTS) {
      results.push({ ...asset, error: `skipped: more than ${MAX_ATTACHMENTS} attachments` });
    } else {
      let result: AttachmentResult;
      try {
        const fetched = await fetchAsset(asset.url, deps.http);
        if (fetched.ok) {
          const path = `${dir}/${index + 1}-${withExtension(safeName(asset.name), fetched.contentType)}`;
          deps.files.mkdirp(dir);
          deps.files.write(path, fetched.bytes);
          result = { ...asset, path };
        } else {
          result = { ...asset, error: fetched.error };
        }
      } catch (error) {
        result = { ...asset, error: (error as Error).message };
      }
      results.push(result);
    }
  }
  return results;
};
