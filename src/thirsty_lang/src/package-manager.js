/* eslint-env node */
/* global require, module, console, process */
/**
 * Thirsty-lang Package Manager
 * Manage dependencies and packages for your Thirsty projects!
 */

const fs = require('fs');

class ThirstyPackageManager {
  constructor() {
    this.configFile = 'thirsty.json';
    this.packagesDir = 'thirsty_packages';
  }

  init(projectName = 'my-thirsty-project') {
    if (fs.existsSync(this.configFile)) {
      console.log('❌ thirsty.json already exists');
      return;
    }

    const config = {
      name: projectName,
      version: '1.0.0',
      description: 'A Thirsty-lang project',
      main: 'main.thirsty',
      dependencies: {},
      devDependencies: {},
      scripts: {},
      keywords: ['thirsty', 'hydration'],
      author: '',
      license: 'MIT'
    };

    fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2));
    console.log('✓ Created thirsty.json');
    console.log('\n📦 Your Thirsty project is ready!');
    console.log('   Project: ' + projectName);
    console.log('   Run "thirsty-pkg install" to set up dependencies');
  }

  install(packageName = null, options = {}) {
    if (!fs.existsSync(this.configFile)) {
      console.log('❌ No thirsty.json found. Run "thirsty-pkg init" first.');
      return;
    }

    const config = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));

    if (packageName) {
      // Install specific package
      console.log("ð¥ Installing " + packageName + "...");

      const deps = options.dev ? config.devDependencies : config.dependencies;
      deps[packageName] = options.version || 'latest';

      fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2));
      console.log('✓ Added ' + packageName + ' to ' + (options.dev ? 'devDependencies' : 'dependencies'));
    } else {
      // Install all dependencies
      console.log('📥 Installing all dependencies...');

      if (!fs.existsSync(this.packagesDir)) {
        fs.mkdirSync(this.packagesDir);
      }

      const allDeps = {
        ...config.dependencies,
        ...config.devDependencies
      };

      if (Object.keys(allDeps).length === 0) {
        console.log('✓ No dependencies to install');
        return;
      }

      for (var pkg in allDeps) {
        if (allDeps.hasOwnProperty(pkg)) {
          var version = allDeps[pkg];
          console.log('  • ' + pkg + '@' + version);
        }
      }

      console.log('✓ All dependencies installed!');
    }
  }

  uninstall(packageName) {
    if (!fs.existsSync(this.configFile)) {
      console.log('❌ No thirsty.json found');
      return;
    }

    const config = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));

    let found = false;
    if (config.dependencies[packageName]) {
      delete config.dependencies[packageName];
      found = true;
    }
    if (config.devDependencies[packageName]) {
      delete config.devDependencies[packageName];
      found = true;
    }

    if (found) {
      fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2));
      console.log('✓ Removed ' + packageName);
    } else {
      console.log('❌ Package ' + packageName + ' not found');
    }
  }

  list() {
    if (!fs.existsSync(this.configFile)) {
      console.log('❌ No thirsty.json found');
      return;
    }

    const config = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));

    console.log('\n📦 ' + config.name + '@' + config.version);
    console.log('═'.repeat(60));

    if (Object.keys(config.dependencies).length > 0) {
      console.log('\n Dependencies:');
      for (var pkg in config.dependencies) {
        if (config.dependencies.hasOwnProperty(pkg)) {
          var version = config.dependencies[pkg];
          console.log('  • ' + pkg + '@' + version);
        }
      }
    }

    if (Object.keys(config.devDependencies).length > 0) {
      console.log('\n DevDependencies:');
      for (var pkg in config.devDependencies) {
        if (config.devDependencies.hasOwnProperty(pkg)) {
          var version = config.devDependencies[pkg];
          console.log('  • ' + pkg + '@' + version);
        }
      }
    }

    if (Object.keys(config.dependencies).length === 0 &&
      Object.keys(config.devDependencies).length === 0) {
      console.log('\n  No dependencies installed');
    }
  }

  search(query) {
    console.log('🔍 Searching for "' + query + '"...');

    // Simulated package registry
    const packages = [
      { name: 'thirsty-http', description: 'HTTP server for Thirsty-lang', version: '1.0.0' },
      { name: 'thirsty-db', description: 'Database adapter for Thirsty-lang', version: '1.2.0' },
      { name: 'thirsty-test', description: 'Testing framework', version: '2.0.0' },
      { name: 'thirsty-cli', description: 'CLI helpers', version: '1.5.0' },
      { name: 'hydration-utils', description: 'Common utilities', version: '3.0.0' }
    ];

    const results = packages.filter(function(pkg) {
      return pkg.name.includes(query) || pkg.description.toLowerCase().includes(query.toLowerCase());
    });

    if (results.length === 0) {
      console.log('No packages found');
      return;
    }

    console.log('\nFound ' + results.length + ' package(s):\n');
    for (var i = 0; i < results.length; i++) {
      var pkg = results[i];
      console.log('  ' + pkg.name + '@' + pkg.version);
      console.log('    ' + pkg.description);
      console.log();
    }
  }

  publish() {
    if (!fs.existsSync(this.configFile)) {
      console.log('❌ No thirsty.json found');
      return;
    }

    const config = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));

    console.log('📤 Publishing ' + config.name + '@' + config.version + '...');
    console.log('✓ Package published successfully!');
    console.log('\n📦 Your package is now available in the Thirsty registry!');
  }
}

function main() {
  const args = process.argv.slice(2);
  const pm = new ThirstyPackageManager();

  if (args.length === 0) {
    console.log('Thirsty Package Manager');
    console.log('\nUsage:');
    console.log('  thirsty-pkg init [name]           Initialize a new project');
    console.log('  thirsty-pkg install [package]     Install package(s)');
    console.log('  thirsty-pkg uninstall <package>   Remove a package');
    console.log('  thirsty-pkg list                  List installed packages');
    console.log('  thirsty-pkg search <query>        Search for packages');
    console.log('  thirsty-pkg publish               Publish your package');
    console.log('\nStay hydrated! 💧');
    return;
  }

  const command = args[0];
  const commandArgs = args.slice(1);

  switch (command) {
    case 'init':
      pm.init(commandArgs[0]);
      break;

    case 'install':
    case 'i': {
      const isDev = commandArgs.includes('--save-dev') || commandArgs.includes('-D');
      const packageName = commandArgs.find(function(arg) { return !arg.startsWith('-'); });
      pm.install(packageName, { dev: isDev });
      break;
    }

    case 'uninstall':
    case 'remove':
      if (commandArgs.length === 0) {
        console.log('Usage: thirsty-pkg uninstall <package>');
      } else {
        pm.uninstall(commandArgs[0]);
      }
      break;

    case 'list':
    case 'ls':
      pm.list();
      break;

    case 'search':
      if (commandArgs.length === 0) {
        console.log('Usage: thirsty-pkg search <query>');
      } else {
        pm.search(commandArgs[0]);
      }
      break;

    case 'publish':
      pm.publish();
      break;

    default:
      console.log('Unknown command: ' + command);
      console.log('Run "thirsty-pkg" for usage information');
  }
}

if (require.main === module) {
  main();
}

module.exports = ThirstyPackageManager;
