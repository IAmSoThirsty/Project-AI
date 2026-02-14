module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'airbnb-base',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // Adjust rules based on project needs
    'no-console': 'off', // Allow console for debugging
    'import/prefer-default-export': 'off',
    'max-len': ['error', { code: 100 }],
    'no-underscore-dangle': 'off',
    'no-param-reassign': ['error', { props: false }],
  },
  ignorePatterns: [
    'node_modules/',
    'dist/',
    'build/',
    'coverage/',
    '*.min.js',
  ],
};
