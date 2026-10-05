// The exit code is part of the error contract: 2 for invalid input, 1 for runtime failures.
export class ExitError extends Error {
  readonly code: number;

  // eslint-disable-next-line unicorn/custom-error-definition
  constructor(code: number, message: string) {
    super(message);
    this.name = 'ExitError';
    this.code = code;
  }
}

export const usageError = (message: string): ExitError => new ExitError(2, message);
