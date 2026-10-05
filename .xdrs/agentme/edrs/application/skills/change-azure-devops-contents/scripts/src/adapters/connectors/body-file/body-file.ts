import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import type { BodyFilePort } from '../../../app/ports';

export const bodyFileConnector: BodyFilePort = {
  withFile: (content, use) => {
    const dir = mkdtempSync(path.join(os.tmpdir(), 'change-ado-'));
    try {
      const file = path.join(dir, 'body.json');
      writeFileSync(file, content);
      return use(file);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  },
};
