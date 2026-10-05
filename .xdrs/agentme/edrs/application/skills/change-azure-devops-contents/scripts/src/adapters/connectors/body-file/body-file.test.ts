import { existsSync, readFileSync } from 'node:fs';

import { bodyFileConnector } from './body-file';

describe('bodyFileConnector', () => {
  it('exposes the content as a file and removes it afterwards, even on failure', () => {
    let seen = '';
    const content = bodyFileConnector.withFile('{"a":1}', (file) => {
      seen = file;
      return readFileSync(file, 'utf8');
    });
    expect(content).toBe('{"a":1}');
    expect(existsSync(seen)).toBe(false);
    expect(() =>
      bodyFileConnector.withFile('x', (file) => {
        seen = file;
        throw new Error('boom');
      }),
    ).toThrow('boom');
    expect(existsSync(seen)).toBe(false);
  });
});
