import { createAz } from './az';

describe('createAz', () => {
  it('invokes the configured binary', () => {
    const az = createAz({ ...process.env, AZ_BIN: process.execPath });
    expect(az.run(['-e', 'process.stdout.write("ok")'])).toBe('ok');
  });

  it('keeps extra words of AZ_BIN as leading arguments and defaults to az', () => {
    const az = createAz({ ...process.env, AZ_BIN: `${process.execPath} -p` });
    expect(az.run(['1+1']).trim()).toBe('2');
    expect(() => createAz({ PATH: '' }).run(['--version'])).toThrow();
  });
});
