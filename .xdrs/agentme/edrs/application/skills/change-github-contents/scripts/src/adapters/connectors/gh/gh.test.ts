import { createGh } from './gh';

describe('createGh', () => {
  it('invokes the configured binary with GH_PAGER=cat', () => {
    const gh = createGh({ ...process.env, GH_BIN: process.execPath });
    expect(gh.run(['-e', 'process.stdout.write(process.env.GH_PAGER)'])).toBe('cat');
  });

  it('keeps extra words of GH_BIN as leading arguments', () => {
    const gh = createGh({ ...process.env, GH_BIN: `${process.execPath} -p` });
    expect(gh.run(['1+1']).trim()).toBe('2');
  });
});
