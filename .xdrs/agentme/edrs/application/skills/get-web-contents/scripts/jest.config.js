// Jest configuration for the skill scripts (agentme-edr-101, agentme-edr-122)
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  cacheDirectory: '<rootDir>/.cache/jest',
  coverageDirectory: '<rootDir>/.cache/coverage',
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.test.ts', '!src/**/*_mock.ts'],
  coverageThreshold: {
    global: { lines: 80, branches: 80, functions: 80, statements: 80 },
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { tsconfig: { module: 'commonjs' } }],
  },
};
