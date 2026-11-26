// Jest configuration for the skill scripts (agentme-edr-101, agentme-edr-122)
module.exports = {
  testEnvironment: 'node',
  testMatch: ['<rootDir>/*.test.ts'],
  cacheDirectory: '<rootDir>/.cache/jest',
  coverageDirectory: '<rootDir>/.cache/coverage',
  // review-gdpr.ts is the three-line process entry point, exercised by the skill Makefile bundle test.
  collectCoverageFrom: ['*.ts', '!*.test.ts', '!*_mock.ts', '!review-gdpr.ts'],
  coverageThreshold: {
    global: { lines: 80, branches: 80, functions: 80, statements: 80 },
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { tsconfig: { module: 'commonjs' } }],
  },
};
