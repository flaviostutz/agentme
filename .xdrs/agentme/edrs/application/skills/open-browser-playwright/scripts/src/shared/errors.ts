import { USAGE } from './constants';

// The exit code is part of the error contract, so the constructor takes it before the message.

export class ExitError extends Error {
  readonly code: number;

  // eslint-disable-next-line unicorn/custom-error-definition
  constructor(code: number, message: string) {
    super(message);
    this.name = 'ExitError';
    this.code = code;
  }
}

export const usageError = (message: string): ExitError => new ExitError(64, `${message}\n${USAGE}`);

// Passed to .catch() for best-effort CDP calls whose failure does not matter.
export const swallow = (): void => {
  // Intentionally ignored.
};
