import { ExitError } from '../shared/errors';

import { parseIssueUrl, parsePrUrl } from './urls';

describe('parsePrUrl', () => {
  it('extracts owner, repo and number', () => {
    expect(parsePrUrl('https://github.com/acme/widgets/pull/482')).toEqual({
      owner: 'acme',
      repo: 'widgets',
      pr: 482,
    });
    expect(parsePrUrl('https://github.com/acme/widgets/pull/482/files?x=1').pr).toBe(482);
  });

  it('rejects non-GitHub URLs with exit code 2', () => {
    expect(() => parsePrUrl('https://gitlab.com/a/b/pull/1')).toThrow(/unrecognized/);
    expect(() => parsePrUrl('')).toThrow(ExitError);
  });
});

describe('parseIssueUrl', () => {
  it('extracts owner, repo and number, ignoring fragments and queries', () => {
    expect(parseIssueUrl('https://github.com/acme/widgets/issues/42')).toEqual({
      owner: 'acme',
      repo: 'widgets',
      issue: 42,
    });
    expect(parseIssueUrl('https://github.com/acme/widgets/issues/42#issuecomment-9').issue).toBe(
      42,
    );
    expect(parseIssueUrl('https://github.com/acme/widgets/issues/42/?a=b').issue).toBe(42);
  });

  it('rejects pull request URLs (adversarial/invalid)', () => {
    expect(() => parseIssueUrl('https://github.com/acme/widgets/pull/42')).toThrow(
      /pull request URL/,
    );
  });

  it('rejects other hosts, discussions and non-numeric ids', () => {
    expect(() => parseIssueUrl('https://github.com/acme/widgets/discussions/4')).toThrow(
      /unrecognized/,
    );
    expect(() => parseIssueUrl('https://github.com/acme/widgets/issues/abc')).toThrow(
      /unrecognized/,
    );
    expect(() => parseIssueUrl('https://example.com/acme/widgets/issues/4')).toThrow(
      /unrecognized/,
    );
  });
});
