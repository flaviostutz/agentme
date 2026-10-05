import { readFileSync } from 'node:fs';

import type { InputPort } from '../../../app/ports';

export const inputConnector: InputPort = {
  read: (file) => readFileSync(file ?? 0, 'utf8'),
};
