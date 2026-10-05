// ESLint flat config for the skill scripts (agentme-edr-101)
import baseConfig from '@stutzlab/eslint-config';

export default [
  ...baseConfig,
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // unicorn/no-null makes undefined the single "absent value", so banning it too is contradictory.
      'no-undefined': 'off',
      // GitHub payloads and the CLI JSON contract use snake_case keys and null values.
      camelcase: 'off',
      'unicorn/no-null': 'off',
    },
  },
  {
    // Test callbacks stay terse; production code keeps the explicit return type rule.
    files: ['src/**/*.test.ts'],
    rules: { '@typescript-eslint/explicit-function-return-type': 'off', 'no-process-env': 'off', 'unicorn/no-await-expression-member': 'off' },
  },
  {
    // Reusable mocks follow the <name>_mock.ts convention (agentme-edr-126 rule 10).
    files: ['src/**/*_mock.ts'],
    rules: { 'unicorn/filename-case': 'off' },
  },
  {
    // CLI adapters are the only place that read process-level state (agentme-edr-126).
    files: ['src/adapters/cli/*.ts'],
    rules: { 'no-process-env': 'off' },
  },
];
