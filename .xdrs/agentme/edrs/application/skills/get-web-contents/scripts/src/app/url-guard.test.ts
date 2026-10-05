import { blockedReason, isPrivateAddress, parseWebUrl } from './url-guard';

describe('isPrivateAddress', () => {
  it.each([
    '127.0.0.1',
    '10.1.2.3',
    '172.16.0.1',
    '172.31.255.255',
    '192.168.1.1',
    '169.254.169.254',
    '100.64.0.1',
    '0.0.0.0',
    '224.0.0.1',
    '::1',
    '::',
    'fc00::1',
    'fd12::1',
    'fe80::1',
    'ff02::1',
    '::ffff:127.0.0.1',
    '::ffff:7f00:1',
    '[::1]',
  ])('treats %s as private', (address) => {
    expect(isPrivateAddress(address)).toBe(true);
  });

  it.each([
    '93.184.216.34',
    '172.32.0.1',
    '8.8.8.8',
    '100.63.0.1',
    '2606:4700::1111',
    '::ffff:808:808',
  ])('treats %s as public', (address) => {
    expect(isPrivateAddress(address)).toBe(false);
  });
});

describe('parseWebUrl', () => {
  it('accepts http and https', () => {
    expect(parseWebUrl('https://example.com/a').hostname).toBe('example.com');
  });

  it.each(['not a url', 'ftp://example.com', 'file:///etc/passwd', 'https://user:pw@example.com'])(
    'rejects %s',
    (raw) => {
      expect(() => parseWebUrl(raw)).toThrow();
    },
  );
});

describe('blockedReason', () => {
  const dns = {
    lookup: async (host: string): Promise<string[]> =>
      host === 'intranet.example' ? ['10.0.0.5'] : ['93.184.216.34'],
  };

  it('blocks local names, private literals and names resolving to private addresses', async () => {
    expect(await blockedReason('localhost', dns, undefined)).toMatch(/local host name/);
    expect(await blockedReason('printer.local', dns, undefined)).toMatch(/local host name/);
    expect(await blockedReason('[::1]', dns, undefined)).toMatch(/private address/);
    expect(await blockedReason('169.254.169.254', dns, undefined)).toMatch(/private address/);
    expect(await blockedReason('intranet.example', dns, undefined)).toMatch(/10\.0\.0\.5/);
  });

  it('allows public hosts and the one private host typed by the human', async () => {
    expect(await blockedReason('example.com', dns, undefined)).toBeUndefined();
    expect(await blockedReason('intranet.example', dns, 'intranet.example')).toBeUndefined();
    expect(await blockedReason('localhost', dns, 'other.example')).toMatch(/local/);
  });
});
