import { spawnSync } from 'node:child_process';

import type { MarkdownPort } from '../../../app/ports';

// Pandoc is optional: without it the caller still gets the original HTML.
export const createPandoc = (env: Record<string, string | undefined>): MarkdownPort => ({
  fromHtml: (html): string | undefined => {
    const bin = env['PANDOC_BIN'] ?? 'pandoc';
    const result = spawnSync(bin, ['-f', 'html', '-t', 'gfm-raw_html', '--wrap=none'], {
      input: html,
      encoding: 'utf8',
      env,
      maxBuffer: 16 * 1024 * 1024,
    });
    if (result.error || result.status !== 0) return;
    return result.stdout.trim();
  },
});
