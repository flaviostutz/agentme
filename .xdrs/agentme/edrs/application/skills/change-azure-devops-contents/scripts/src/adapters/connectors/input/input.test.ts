import { mkdtempSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { inputConnector } from './input';

describe('inputConnector', () => {
  it('reads the given file', () => {
    const file = path.join(mkdtempSync(path.join(os.tmpdir(), 'input-')), 'items.json');
    writeFileSync(file, '[1]');
    expect(inputConnector.read(file)).toBe('[1]');
  });
});
