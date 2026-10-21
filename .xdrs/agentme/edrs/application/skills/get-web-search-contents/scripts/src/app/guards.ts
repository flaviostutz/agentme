import { HARD_MAX_SEARCHES, DEFAULT_MAX_SEARCHES } from '../shared/constants';
import { usageError } from '../shared/errors';

const SECRET_PATTERNS: readonly (readonly [string, RegExp])[] = [
  ['an email address', /[\w.+-]+@[\w-]+\.[\w.-]+/],
  ['a private key block', /-----BEGIN [A-Z ]*PRIVATE KEY-----/],
  ['an authorization header', /\bauthorization\s*:\s*\S+|\bbearer\s+[\w.~+/=-]{10,}/i],
  [
    'a password or secret assignment',
    /\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S+/i,
  ],
  ['a token-like string', /\b(?:sk|pk|ghp|gho|ghs|ghu|xox[abprs]|AKIA|AIza)[-_A-Za-z0-9]{16,}/],
  ['a JSON web token', /\beyJ[\w-]{8,}\.[\w-]{8,}\.[\w-]*/],
  [
    'a long random-looking string',
    /\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{32,}\b/,
  ],
  [
    'a private IP address',
    /\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01])|127\.\d{1,3})\.\d{1,3}\.\d{1,3}\b/,
  ],
];

// Refuses text that looks like it holds credentials or personal data; the reason never echoes the text.
export const secretReason = (text: string): string | undefined => {
  const hit = SECRET_PATTERNS.find(([, pattern]) => pattern.test(text));
  return hit?.[0];
};

export const validateText = (raw: string, label: string, maxChars: number): string => {
  const text = raw.trim();
  if (text.length === 0) throw usageError(`${label} must not be empty`);
  if (text.length > maxChars) throw usageError(`${label} is longer than ${maxChars} characters`);
  const reason = secretReason(text);
  if (reason) {
    throw usageError(
      `${label} looks like it contains ${reason}; rephrase it without credentials, personal data or internal infrastructure`,
    );
  }
  return text;
};

const ID = /^[A-Za-z0-9_-]{1,64}$/;

export const validateId = (value: string, label: string): string => {
  if (!ID.test(value)) throw usageError(`${label} must match [A-Za-z0-9_-]{1,64}`);
  return value;
};

export const validateMaxSearches = (raw: string | undefined): number => {
  if (raw === undefined) return DEFAULT_MAX_SEARCHES;
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1 || value > HARD_MAX_SEARCHES) {
    throw usageError(`--max-searches must be an integer from 1 to ${HARD_MAX_SEARCHES}`);
  }
  return value;
};

export const validateLang = (raw: string | undefined): string | undefined => {
  if (raw === undefined) return undefined;
  if (!/^[a-z]{2}(?:-[A-Za-z]{2})?$/.test(raw))
    throw usageError('--lang must look like en or pt-BR');
  return raw;
};

export const validateRegion = (raw: string | undefined): string | undefined => {
  if (raw === undefined) return undefined;
  if (!/^[A-Za-z]{2}$/.test(raw)) throw usageError('--region must be a 2-letter country code');
  return raw.toLowerCase();
};
