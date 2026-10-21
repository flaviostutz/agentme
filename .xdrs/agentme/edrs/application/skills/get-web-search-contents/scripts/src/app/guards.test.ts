import {
  secretReason,
  validateId,
  validateLang,
  validateMaxSearches,
  validateRegion,
  validateText,
} from './guards';

describe('validateText', () => {
  it('passes a normal query through trimmed, including operators and non-ASCII', () => {
    expect(validateText('  site:example.org "água potável" filetype:pdf ', '--query', 300)).toBe(
      'site:example.org "água potável" filetype:pdf',
    );
  });

  it('rejects empty and over-long text with exit code 2', () => {
    expect(() => validateText('   ', '--query', 300)).toThrow(/must not be empty/);
    expect(() => validateText('x'.repeat(301), '--query', 300)).toThrow(/longer than 300/);
    try {
      validateText('', '--query', 300);
    } catch (error) {
      expect((error as { code: number }).code).toBe(2);
    }
  });

  it.each([
    ['an email', 'contact jane.doe@example.com about it', 'email'],
    ['a bearer header', 'Authorization: Bearer abcdef1234567890', 'authorization'],
    ['a private key', '-----BEGIN RSA PRIVATE KEY-----', 'private key'],
    ['a password', 'password=hunter2 login', 'password'],
    ['a token', 'ghp_abcdefghijklmnopqrstuvwxyz0123456789', 'token'],
    ['a jwt', 'eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0.SflKxwRJSMeKKF2QT4', 'web token'],
    ['a private ip', 'server at 192.168.1.20 is down', 'private IP'],
    ['a random string', 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6', 'random-looking'],
  ])('refuses %s without echoing it', (_name, text, reason) => {
    expect(() => validateText(text, '--query', 300)).toThrow(new RegExp(reason, 'i'));
    try {
      validateText(text, '--query', 300);
    } catch (error) {
      expect((error as Error).message).not.toContain(text);
    }
  });

  it('allows ordinary public text', () => {
    expect(secretReason('how to build a first aid kit 2025')).toBeUndefined();
    expect(secretReason('node 22.1.0 release notes')).toBeUndefined();
  });
});

describe('option validators', () => {
  it('validateId accepts safe ids and rejects path-like ones', () => {
    expect(validateId('digital-prepper_1', '--run-id')).toBe('digital-prepper_1');
    expect(() => validateId('../etc', '--run-id')).toThrow(/must match/);
    expect(() => validateId('', '--run-id')).toThrow(/must match/);
  });

  it('validateMaxSearches defaults to 10 and caps at 30', () => {
    expect(validateMaxSearches(undefined)).toBe(10);
    expect(validateMaxSearches('30')).toBe(30);
    expect(() => validateMaxSearches('31')).toThrow(/1 to 30/);
    expect(() => validateMaxSearches('0')).toThrow(/1 to 30/);
    expect(() => validateMaxSearches('x')).toThrow(/1 to 30/);
  });

  it('validateLang and validateRegion check their shape', () => {
    expect(validateLang(undefined)).toBeUndefined();
    expect(validateLang('pt-BR')).toBe('pt-BR');
    expect(() => validateLang('english')).toThrow(/--lang/);
    expect(validateRegion(undefined)).toBeUndefined();
    expect(validateRegion('NL')).toBe('nl');
    expect(() => validateRegion('nld')).toThrow(/--region/);
  });
});
