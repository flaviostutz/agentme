import { MAX_ATTACHMENTS, MAX_ATTACHMENT_BYTES } from '../shared/constants';

import { attachmentKey, isAttachmentUrl } from './links';
import type { Deps } from './ports';
import { restArgs } from './rest';

export type Asset = { name: string; url: string; size?: number };

export type AttachmentResult =
  { name: string; url: string; path: string } | { name: string; url: string; error: string };

const safeName = (name: string): string => name.replaceAll(/[^\w.-]+/g, '_').slice(0, 80) || 'file';

// Keeps the first asset per file; relations come first because they carry the real name and size.
export const mergeAssets = (assets: readonly Asset[]): Asset[] => {
  const found = new Map<string, Asset>();
  for (const asset of assets) {
    if (URL.canParse(asset.url) && !found.has(attachmentKey(asset.url))) {
      found.set(attachmentKey(asset.url), asset);
    }
  }
  return [...found.values()];
};

// Downloads through `az rest` (which sends the Azure DevOps token), so only same-organization attachment URLs qualify.
export const downloadAssets = (
  assets: readonly Asset[],
  options: { dir: string; org: string },
  deps: Pick<Deps, 'az' | 'files'>,
): AttachmentResult[] =>
  assets.map((asset, index): AttachmentResult => {
    const { name, url } = asset;
    if (index >= MAX_ATTACHMENTS) {
      return { name, url, error: `skipped: more than ${MAX_ATTACHMENTS} attachments` };
    }
    if (!isAttachmentUrl(url, options.org)) return { name, url, error: 'host not allowed' };
    if ((asset.size ?? 0) > MAX_ATTACHMENT_BYTES)
      return { name, url, error: 'file is larger than 10 MB' };
    const path = `${options.dir}/${index + 1}-${safeName(name)}`;
    try {
      deps.files.mkdirp(options.dir);
      deps.az.run([...restArgs('GET', url, '7.1'), '--output-file', path]);
      const size = deps.files.size(path);
      if (size === undefined) return { name, url, error: 'download produced no file' };
      if (size > MAX_ATTACHMENT_BYTES) {
        deps.files.remove(path);
        return { name, url, error: 'file is larger than 10 MB' };
      }
      return { name, url, path };
    } catch (error) {
      const { stderr } = error as { stderr?: string };
      return {
        name,
        url,
        error: String(stderr ?? (error as Error).message)
          .trim()
          .slice(0, 200),
      };
    }
  });
