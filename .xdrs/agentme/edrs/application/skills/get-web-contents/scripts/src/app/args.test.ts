import { parseArgs, requireString } from './args';

describe('parseArgs', () => {
  it('reads values and flags', () => {
    expect(parseArgs(['--pr-url', 'u', '--dry-run'])).toEqual({ 'pr-url': 'u', 'dry-run': true });
  });

  it('rejects stray arguments', () => {
    expect(() => parseArgs(['stray'])).toThrow(/unexpected argument/);
  });

  it('requireString fails with the usage text when the flag is missing', () => {
    expect(() => requireString({ x: true }, 'x', 'cmd --x <v>')).toThrow(/Usage: cmd --x <v>/);
    expect(requireString({ x: 'v' }, 'x', 'u')).toBe('v');
  });
});
