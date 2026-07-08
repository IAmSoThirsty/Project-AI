/**
 * Jest Configuration for The Triumvirate
 */

/* eslint-env node */
/* global module */

module.exports = {
  // Test environment
  testEnvironment: 'node',
  
  // Test match patterns
  testMatch: [
    '**/tests/**/*.test.js'
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'js/**/*.js',
    '!js/analytics.js', // Exclude analytics from coverage
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.git/'
  ],
  
  // Verbose output
  verbose: true,
  
  // Automatically clear mock calls between tests
  clearMocks: true,
  
  // Collect coverage
  collectCoverage: false, // Set to true when running coverage
  
  // Coverage directory
  coverageDirectory: 'coverage',
  
  // Coverage reporters
  coverageReporters: ['text', 'lcov', 'html'],
  
  // Maximum workers
  maxWorkers: '50%',
  
  // Timeout
  testTimeout: 10000
};
