import { mkdirSync, rmSync, statSync } from 'node:fs';

import type { FilesPort } from '../../../app/ports';

export const filesConnector: FilesPort = {
  mkdirp: (dir) => {
    mkdirSync(dir, { recursive: true });
  },
  size: (file) => {
    try {
      return statSync(file).size;
    } catch {
      return;
    }
  },
  remove: (file) => {
    rmSync(file, { force: true });
  },
};
