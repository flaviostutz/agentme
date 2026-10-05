import { chmodSync, mkdtempSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { createPandoc } from './pandoc';

const fakeConverter = (body: string): string => {
  const file = path.join(mkdtempSync(path.join(os.tmpdir(), 'pandoc-')), 'pandoc');
  writeFileSync(file, `#!/bin/sh\n${body}\n`);
  chmodSync(file, 0o755);
  return file;
};

describe('createPandoc', () => {
  it('returns the trimmed converter output', () => {
    const converter = createPandoc({ ...process.env, PANDOC_BIN: fakeConverter('cat') });
    expect(converter.fromHtml('hello\n')).toBe('hello');
  });

  it('returns undefined when the converter is missing or fails', () => {
    expect(
      createPandoc({ ...process.env, PANDOC_BIN: '/nonexistent/pandoc' }).fromHtml('x'),
    ).toBeUndefined();
    expect(
      createPandoc({ ...process.env, PANDOC_BIN: fakeConverter('exit 3') }).fromHtml('x'),
    ).toBeUndefined();
  });

  it('defaults to the pandoc binary from PATH', () => {
    expect(createPandoc({ PATH: '' }).fromHtml('x')).toBeUndefined();
  });
});
