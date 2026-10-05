import { mkdirSync, writeFileSync } from 'node:fs';

import type { FilesPort } from '../../../app/ports';

export const filesConnector: FilesPort = {
  mkdirp: (dir) => {
    mkdirSync(dir, { recursive: true });
  },
  write: (file, bytes) => {
    writeFileSync(file, bytes);
  },
};
