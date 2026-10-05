import { flattenPages, parseJsonStream } from './json-stream';

describe('parseJsonStream', () => {
  it('parses concatenated pages including brackets in strings', () => {
    const text = '[{"body":"a ] tricky \\" [ one"}]\n[{"body":"b"}]';
    expect(flattenPages(text)).toEqual([{ body: 'a ] tricky " [ one' }, { body: 'b' }]);
    expect(flattenPages('{"a":1}')).toEqual([{ a: 1 }]);
  });

  it('fails on truncated output', () => {
    expect(() => parseJsonStream('[{"a":1}')).toThrow(/truncated/);
  });
});
