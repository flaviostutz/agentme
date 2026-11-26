// ESLint flat config for the skill scripts (agentme-edr-101)
import baseConfig from '@stutzlab/eslint-config';

export default [
  ...baseConfig,
  {
    files: ['*.ts'],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // unicorn/no-null makes undefined the single "absent value", so banning it too is contradictory.
      'no-undefined': 'off',
      'unicorn/no-null': 'off',
    },
  },
  {
    // Test callbacks stay terse; production code keeps the explicit return type rule.
    files: ['*.test.ts'],
    rules: { '@typescript-eslint/explicit-function-return-type': 'off', 'no-process-env': 'off' },
  },
  {
    // Reusable mocks follow the <name>_mock.ts convention (agentme-edr-126 rule 10).
    files: ['*_mock.ts'],
    rules: { 'unicorn/filename-case': 'off' },
  },
  {
    // The CLI layer is the only place that reads process-level state (agentme-edr-126).
    files: ['review-gdpr.ts', 'cli.ts'],
    rules: { 'no-process-env': 'off' },
  },
];
