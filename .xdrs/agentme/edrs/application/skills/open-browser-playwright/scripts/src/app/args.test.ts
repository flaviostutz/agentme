import { AUTO_PORT_MAX, SKILL_PORT_MAX } from '../shared/constants';
import { ExitError } from '../shared/errors';

import { parseArgs, validateSessionName } from './args';

const assertUsage = (fn: () => unknown, pattern?: RegExp): void => {
  let thrown: unknown;
  try {
    fn();
  } catch (error) {
    thrown = error;
  }
  expect(thrown).toBeInstanceOf(ExitError);
  expect((thrown as ExitError).code).toBe(64);
  if (pattern) expect((thrown as ExitError).message).toMatch(pattern);
};

describe('parseArgs', () => {
  it('parses open with defaults', () => {
    expect(parseArgs(['my-task', 'https://example.com'], {})).toEqual({
      command: 'open',
      session: 'my-task',
      url: 'https://example.com/',
      size: { width: 1300, height: 900 },
      skipSso: false,
      ssoWaitSeconds: 45,
    });
  });

  it('parses open with size, port and env', () => {
    const opts = parseArgs(['s1', 'http://example.com/a', '800x600', '--cdp-port=9231'], {
      SKIP_SSO: 'true',
      SSO_CHECK_URL: 'https://portal.example.com/me',
      SSO_WAIT_SECONDS: '10',
    });
    expect(opts).toMatchObject({
      cdpPort: 9231,
      size: { width: 800, height: 600 },
      skipSso: true,
      ssoCheckUrl: 'https://portal.example.com/me',
      ssoWaitSeconds: 10,
    });
  });

  it('accepts SKIP_SSO only as exactly "true"', () => {
    expect(parseArgs(['s1', 'https://example.com'], { SKIP_SSO: 'yes' })).toMatchObject({
      skipSso: false,
    });
    expect(parseArgs(['s1', 'https://example.com'], { SKIP_SSO: 'TRUE' })).toMatchObject({
      skipSso: false,
    });
  });

  it('parses wait and tidy', () => {
    expect(parseArgs(['wait', 's1', 'https://example.com'], {})).toMatchObject({
      command: 'wait',
      waitSeconds: 300,
    });
    expect(parseArgs(['wait', 's1', 'https://example.com', '60'], {})).toMatchObject({
      waitSeconds: 60,
    });
    expect(parseArgs(['tidy', 's1'], {})).toMatchObject({ command: 'tidy', session: 's1' });
  });

  it('rejects invalid usage with exit code 64', () => {
    assertUsage(() => parseArgs([], {}), /missing/);
    assertUsage(() => parseArgs(['s1', 'https://example.com', '--cdp-port=9229'], {}), /9230/);
    assertUsage(() => parseArgs(['s1', 'https://example.com', '--cdp-port=9390'], {}), /rule 05/);
    assertUsage(() => parseArgs(['s1', 'https://example.com', '--cdp-port=abc'], {}));
    assertUsage(() => parseArgs(['s1', 'https://example.com', '--headless'], {}), /unknown option/);
    assertUsage(() => parseArgs(['s1', 'javascript:alert(1)'], {}), /http or https/);
    assertUsage(() => parseArgs(['s1', 'not a url'], {}), /invalid url/);
    assertUsage(() => parseArgs(['s1', 'https://example.com', 'big'], {}), /window size/);
    assertUsage(() => parseArgs(['bad name!', 'https://example.com'], {}), /session name/);
    assertUsage(
      () => parseArgs(['s1', 'https://example.com'], { SSO_CHECK_URL: "https://x.example.com/'a" }),
      /SSO_CHECK_URL/,
    );
    assertUsage(
      () => parseArgs(['s1', 'https://example.com'], { SSO_CHECK_URL: 'http://x.example.com' }),
      /SSO_CHECK_URL/,
    );
    assertUsage(
      () => parseArgs(['s1', 'https://example.com'], { SSO_WAIT_SECONDS: '0' }),
      /SSO_WAIT_SECONDS/,
    );
    assertUsage(
      () => parseArgs(['wait', 's1', 'https://example.com'], { SKIP_SSO: 'true' }),
      /SKIP_SSO/,
    );
    assertUsage(
      () => parseArgs(['wait', 's1', 'https://example.com', '--cdp-port=9231'], {}),
      /cdp-port/,
    );
    assertUsage(() => parseArgs(['wait', 's1'], {}), /wait needs/);
    assertUsage(() => parseArgs(['tidy'], {}), /tidy needs/);
  });
});

describe('validateSessionName', () => {
  it('rejects reserved subcommand names and overlong names', () => {
    assertUsage(() => validateSessionName('wait'), /reserved/);
    assertUsage(() => validateSessionName('tidy'), /reserved/);
    assertUsage(() => validateSessionName('a'.repeat(33)));
    assertUsage(() => validateSessionName(''));
    expect(validateSessionName('ok_name-1')).toBe('ok_name-1');
  });

  it('keeps automatic ports above the skill-reserved range', () => {
    expect(SKILL_PORT_MAX).toBeLessThan(AUTO_PORT_MAX);
  });
});
