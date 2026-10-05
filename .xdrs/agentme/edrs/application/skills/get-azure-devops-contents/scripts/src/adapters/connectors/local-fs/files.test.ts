import { mkdtempSync, writeFileSync, existsSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { filesConnector } from './files';

describe('filesConnector', () => {
  it('creates folders, reports sizes and removes files', () => {
    const dir = path.join(mkdtempSync(path.join(os.tmpdir(), 'ado-')), 'a', 'b');
    filesConnector.mkdirp(dir);
    const file = path.join(dir, 'f.txt');
    expect(filesConnector.size(file)).toBeUndefined();
    writeFileSync(file, 'xyz');
    expect(filesConnector.size(file)).toBe(3);
    filesConnector.remove(file);
    expect(existsSync(file)).toBe(false);
  });
});
