import { flag, optionalString, parseArgs, requireString } from './args';

describe('parseArgs', () => {
  it('reads values and flags', () => {
    expect(parseArgs(['--query', 'a b', '--google-confirmed'])).toEqual({
      query: 'a b',
      'google-confirmed': true,
    });
  });

  it('rejects stray arguments', () => {
    expect(() => parseArgs(['stray'])).toThrow(/unexpected argument/);
  });

  it('requireString fails with the usage text when the flag is missing', () => {
    expect(() => requireString({ x: true }, 'x', 'cmd --x <v>')).toThrow(/Usage: cmd --x <v>/);
    expect(requireString({ x: 'v' }, 'x', 'u')).toBe('v');
  });

  it('optionalString and flag enforce their shape', () => {
    expect(optionalString({}, 'a')).toBeUndefined();
    expect(optionalString({ a: 'v' }, 'a')).toBe('v');
    expect(() => optionalString({ a: true }, 'a')).toThrow(/needs a value/);
    expect(flag({}, 'f')).toBe(false);
    expect(flag({ f: true }, 'f')).toBe(true);
    expect(() => flag({ f: 'x' }, 'f')).toThrow(/takes no value/);
  });
});
