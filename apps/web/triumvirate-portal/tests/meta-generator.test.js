/* eslint-env node, jest */
/* global require, __dirname, describe, test, expect, beforeEach, afterEach */

const path = require('node:path');

const modulePath = path.resolve(__dirname, '..', 'js', 'meta-generator.js');

describe('Meta Generator - helper and CLI coverage', () => {
  let metaGenerator;

  beforeEach(() => {
    jest.resetModules();
    metaGenerator = require(modulePath);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('listPageKeys exposes expected canonical keys', () => {
    const keys = metaGenerator.listPageKeys();

    expect(keys).toEqual(
      expect.arrayContaining([
        'home',
        'manifesto',
        'trinity',
        'projectAI',
        'cerberus',
        'codex',
        'research',
        'founder'
      ])
    );
  });

  test('generateMetaTags escapes unsafe attribute characters', () => {
    const originalTitle = metaGenerator.metaTagsConfig.home.title;
    metaGenerator.metaTagsConfig.home.title = 'A "Quote" & <Tag>';

    try {
      const tags = metaGenerator.generateMetaTags('home');
      expect(tags).toContain('<title>A &quot;Quote&quot; &amp; &lt;Tag&gt;</title>');
    } finally {
      metaGenerator.metaTagsConfig.home.title = originalTitle;
    }
  });

  test('generateMetaTags returns empty string and logs for unknown key', () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const tags = metaGenerator.generateMetaTags('does-not-exist');

    expect(tags).toBe('');
    expect(errorSpy).toHaveBeenCalledWith('No configuration found for page: does-not-exist');
  });

  test('runCli supports --list and prints keys', () => {
    const logSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    const exitCode = metaGenerator.runCli(['--list']);

    expect(exitCode).toBe(0);
    expect(logSpy).toHaveBeenCalledWith('Available page keys:');

    const output = logSpy.mock.calls.map((call) => String(call[0])).join('\n');
    expect(output).toContain('- home');
    expect(output).toContain('- founder');
  });

  test('runCli supports -l alias', () => {
    const logSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    const exitCode = metaGenerator.runCli(['-l']);

    expect(exitCode).toBe(0);
    expect(logSpy).toHaveBeenCalledWith('Available page keys:');
  });

  test('runCli returns 1 when page argument is missing', () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const exitCode = metaGenerator.runCli([]);

    expect(exitCode).toBe(1);
    const output = errorSpy.mock.calls.map((call) => String(call[0])).join('\n');
    expect(output).toContain('Usage: node js/meta-generator.js --page <key>');
    expect(output).toContain('node js/meta-generator.js --list');
  });

  test('runCli supports -p alias and returns generated tags', () => {
    const logSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

    const exitCode = metaGenerator.runCli(['-p', 'home']);

    expect(exitCode).toBe(0);
    const output = logSpy.mock.calls.map((call) => String(call[0])).join('\n');
    expect(output).toContain('<meta name="description"');
    expect(output).toContain('<link rel="canonical" href="https://iamsothirsty.github.io/the_triumvirate/">');
  });

  test('runCli returns 1 for unknown page key', () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const exitCode = metaGenerator.runCli(['--page', 'unknown']);

    expect(exitCode).toBe(1);
    const output = errorSpy.mock.calls.map((call) => String(call[0])).join('\n');
    expect(output).toContain('No configuration found for page: unknown');
    expect(output).toContain('Unknown page key: unknown');
  });
});
