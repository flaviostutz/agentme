import { spawnSync } from 'node:child_process';

import type { MarkdownPort } from '../../../app/ports';

// Pandoc is needed only for writes that carry text; without it the caller gets a clear error.
export const createPandoc = (env: Record<string, string | undefined>): MarkdownPort => ({
  toHtml: (markdown): string | undefined => {
    const bin = env['PANDOC_BIN'] ?? 'pandoc';
    const result = spawnSync(bin, ['-f', 'gfm', '-t', 'html', '--wrap=none'], {
      input: markdown,
      encoding: 'utf8',
      env,
      maxBuffer: 16 * 1024 * 1024,
    });
    if (result.error || result.status !== 0) return;
    return result.stdout.trim();
  },
});
