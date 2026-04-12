import { hello } from './index';

describe('hello', () => {
  it('should return a greeting', () => {
    expect(hello('world')).toBe('Hello, world!');
  });
});
