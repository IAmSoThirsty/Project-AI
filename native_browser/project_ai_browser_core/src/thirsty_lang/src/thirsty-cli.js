//                                           [2026-03-03 13:45]
//                                          Productivity: Active
#!/usr/bin/env node

/**
 * Thirsty CLI - Unified command-line interface
 * One tool to rule them all!
 * 
 * Date: 2026-03-03 15:15 UTC | Status: Active
 */

const fs = require('fs');
const path = require('path');
const { safeJoin } = require('./path-validator');

const commands = {
  run: require('./cli'),
  repl: require('./repl'),
  test: require('./test/runner'),
  debug: require('./debugger'),
  format: require('./formatter'),
  lint: require('./linter'),
  profile: require('./profiler'),
  doc: require('./doc-generator'),
  ast: require('./ast'),
  transpile: require('./transpiler'),
  train: require('./training'),
  pkg: require('./package-manager')
};

function showHelp() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║              💧 Thirsty-lang CLI v1.0.0 💧                ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('\nUsage: thirsty <command> [options]\n');
  console.log('Commands:\n');
  console.log('  run <file>              Run a Thirsty-lang program');
  console.log('  repl                    Start interactive REPL');
  console.log('  train                   Launch interactive training');
  console.log('  test [file]             Run tests');
  console.log('  debug <file>            Debug a program');
  console.log('  format <file>           Format code');
  console.log('  lint <file>             Lint code');
  console.log('  profile <file>          Profile performance');
  console.log('  doc <file>              Generate documentation');
  console.log('  ast <file>              Generate AST');
  console.log('  transpile <file>        Transpile to other languages');
  console.log('  pkg <command>           Package manager');
  console.log('  init [name]             Initialize new project');
  console.log('  version                 Show version');
  console.log('  help                    Show this help\n');
  console.log('Examples:\n');
  console.log('  thirsty run examples/hello.thirsty');
  console.log('  thirsty repl');
  console.log('  thirsty train');
  console.log('  thirsty format examples/hello.thirsty');
  console.log('  thirsty transpile program.thirsty --target python\n');
  console.log('For more information: https://github.com/IAmSoThirsty/Thirsty-lang');
  console.log('\nStay hydrated! 💧\n');
}

function showVersion() {
  const pkg = require('../package.json');
  console.log("Thirsty-lang v" + pkg.version);
  console.log('Node.js ' + process.version);
  console.log('Stay hydrated! 💧');
}

function initProject(name = 'my-thirsty-project') {
  // Validate project name to prevent path traversal
  try {
    // Only allow alphanumeric, hyphens, and underscores in project names
    if (!/^[a-zA-Z0-9_-]+$/.test(name)) {
      console.error("❌ Invalid project name. Use only letters, numbers, hyphens, and underscores");
      process.exit(1);
    }

    const projectDir = safeJoin(process.cwd(), name);

    if (fs.existsSync(projectDir)) {
      console.error("❌ Directory '" + name + "' already exists");
      process.exit(1);
    }

    // Create project structure
    fs.mkdirSync(projectDir);
    fs.mkdirSync(safeJoin(projectDir, 'src'));
    fs.mkdirSync(safeJoin(projectDir, 'tests'));
    fs.mkdirSync(safeJoin(projectDir, 'docs'));

    // Create main file
    const mainContent = '// Welcome to ' + name + '!\n' +
      '// Start coding your Thirsty-lang application here\n' +
      '\n' +
      'drink message = "Hello from ' + name + '!"\n' +
      'pour message\n' +
      '\n' +
      '// Stay hydrated! 💧\n';
    fs.writeFileSync(safeJoin(projectDir, 'src', 'main.thirsty'), mainContent);

    // Create thirsty.json
    const config = {
      name: name,
      version: '1.0.0',
      description: 'A Thirsty-lang project',
      main: 'src/main.thirsty',
      scripts: {
        start: 'thirsty run src/main.thirsty',
        test: 'thirsty test',
        format: 'thirsty format src/*.thirsty',
        lint: 'thirsty lint src/*.thirsty'
      },
      dependencies: {},
      devDependencies: {},
      author: '',
      license: 'MIT'
    };
    fs.writeFileSync(
      safeJoin(projectDir, 'thirsty.json'),
      JSON.stringify(config, null, 2)
    );

    // Create README
    const readme = '# ' + name + '\n' +
      '\n' +
      'A Thirsty-lang project.\n' +
      '\n' +
      '## Getting Started\n' +
      '\n' +
      '```bash\n' +
      '# Run the program\n' +
      'thirsty run src/main.thirsty\n' +
      '\n' +
      '# Start REPL\n' +
      'thirsty repl\n' +
      '\n' +
      '# Run tests\n' +
      'thirsty test\n' +
      '```\n' +
      '\n' +
      '## Learn More\n' +
      '\n' +
      '- [Thirsty-lang Documentation](https://github.com/IAmSoThirsty/Thirsty-lang)\n' +
      '- [Language Specification](https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/SPECIFICATION.md)\n' +
      '- [Expansions Guide](https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/EXPANSIONS.md)\n' +
      '\n' +
      'Stay hydrated! 💧\n';
    fs.writeFileSync(safeJoin(projectDir, 'README.md'), readme);

    // Create .gitignore
    const gitignore = `thirsty_packages/
node_modules/
*.log
.DS_Store
`;
    fs.writeFileSync(safeJoin(projectDir, '.gitignore'), gitignore);

    console.log('✓ Project initialized successfully!');
    console.log('\nNext steps:');
    console.log('  cd ' + name);
    console.log('  thirsty run src/main.thirsty');
    console.log('\nStay hydrated! 💧');
  } catch (error) {
    console.error('❌ Error initializing project: ' + error.message);
    process.exit(1);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    showHelp();
    process.exit(0);
  }

  const command = args[0];
  const commandArgs = args.slice(1);

  switch (command) {
    case 'help':
    case '--help':
    case '-h':
      showHelp();
      break;

    case 'version':
    case '--version':
    case '-v':
      showVersion();
      break;

    case 'init':
      initProject(commandArgs[0]);
      break;

    case 'run':
      if (commandArgs.length === 0) {
        console.error('Usage: thirsty run <file>');
        process.exit(1);
      }
      await commands.run(commandArgs);
      break;

    case 'repl':
      const repl = new commands.repl();
      await repl.start();
      break;

    case 'train':
      const trainer = new commands.train();
      await trainer.start();
      break;

    case 'test':
      commands.test.run();
      break;

    case 'debug':
      commands.debug(commandArgs);
      break;

    case 'format':
      commands.format(commandArgs);
      break;

    case 'lint':
      commands.lint(commandArgs);
      break;

    case 'profile':
      commands.profile(commandArgs);
      break;

    case 'doc':
      commands.doc(commandArgs);
      break;

    case 'ast':
      commands.ast(commandArgs);
      break;

    case 'transpile':
      commands.transpile(commandArgs);
      break;

    case 'pkg':
      commands.pkg(commandArgs);
      break;

    default:
      console.error('Unknown command: ' + command);
      console.log('Run "thirsty help" for usage information');
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}

module.exports = { main: main, showHelp: showHelp, showVersion: showVersion, initProject: initProject };
