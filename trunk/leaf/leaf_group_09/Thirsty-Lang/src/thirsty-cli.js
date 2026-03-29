#!/usr/bin/env node

/**
 * Thirsty CLI - Unified command-line interface
 * One tool to rule them all!
 */

const fs = require('fs');
const path = require('path');

// Don't load command modules at top level to avoid auto-execution
// They will be lazy-loaded when needed

function showHelp() {
  const pkg = require('../package.json');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log(`║              💧 Thirsty-lang CLI v${pkg.version} 💧                ║`);
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
  console.log(`Thirsty-lang v${pkg.version}`);
  console.log(`Node.js ${process.version}`);
  console.log('Stay hydrated! 💧');
}

function initProject(name = 'my-thirsty-project') {
  const projectDir = path.join(process.cwd(), name);
  
  if (fs.existsSync(projectDir)) {
    console.error(`❌ Directory '${name}' already exists`);
    process.exit(1);
  }

  // Create project structure
  fs.mkdirSync(projectDir);
  fs.mkdirSync(path.join(projectDir, 'src'));
  fs.mkdirSync(path.join(projectDir, 'tests'));
  fs.mkdirSync(path.join(projectDir, 'docs'));

  // Create main file
  const mainContent = `// Welcome to ${name}!
// Start coding your Thirsty-lang application here

drink message = "Hello from ${name}!"
pour message

// Stay hydrated! 💧
`;
  fs.writeFileSync(path.join(projectDir, 'src', 'main.thirsty'), mainContent);

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
    path.join(projectDir, 'thirsty.json'),
    JSON.stringify(config, null, 2)
  );

  // Create README
  const readme = `# ${name}

A Thirsty-lang project.

## Getting Started

\`\`\`bash
# Run the program
thirsty run src/main.thirsty

# Start REPL
thirsty repl

# Run tests
thirsty test
\`\`\`

## Learn More

- [Thirsty-lang Documentation](https://github.com/IAmSoThirsty/Thirsty-lang)
- [Language Specification](https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/SPECIFICATION.md)
- [Expansions Guide](https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/EXPANSIONS.md)

Stay hydrated! 💧
`;
  fs.writeFileSync(path.join(projectDir, 'README.md'), readme);

  // Create .gitignore
  const gitignore = `thirsty_packages/
node_modules/
*.log
.DS_Store
`;
  fs.writeFileSync(path.join(projectDir, '.gitignore'), gitignore);

  console.log('✓ Project initialized successfully!');
  console.log(`\nNext steps:`);
  console.log(`  cd ${name}`);
  console.log(`  thirsty run src/main.thirsty`);
  console.log('\nStay hydrated! 💧');
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
      // Remove 'run' from argv so cli.js gets the correct arguments
      process.argv.splice(2, 1);
      const runMain = require('./cli');
      if (typeof runMain === 'function') {
        runMain();
      }
      break;

    case 'repl':
      const ThirstyREPL = require('./repl');
      const repl = new ThirstyREPL();
      await repl.start();
      break;

    case 'train':
      const TrainingProgram = require('./training');
      const trainer = new TrainingProgram();
      await trainer.start();
      break;

    case 'test':
      require('./test/runner');
      break;

    case 'debug':
      // Pass through to debugger module which has its own CLI
      process.argv.splice(2, 1); // Remove 'debug' command
      require('./debugger');
      break;

    case 'format':
      // Pass through to formatter module which has its own CLI
      process.argv.splice(2, 1); // Remove 'format' command
      require('./formatter');
      break;

    case 'lint':
      // Pass through to linter module which has its own CLI
      process.argv.splice(2, 1); // Remove 'lint' command
      require('./linter');
      break;

    case 'profile':
      // Pass through to profiler module which has its own CLI
      process.argv.splice(2, 1); // Remove 'profile' command
      require('./profiler');
      break;

    case 'doc':
      // Pass through to doc-generator module which has its own CLI
      process.argv.splice(2, 1); // Remove 'doc' command
      require('./doc-generator');
      break;

    case 'ast':
      // Pass through to ast module which has its own CLI
      process.argv.splice(2, 1); // Remove 'ast' command
      require('./ast');
      break;

    case 'transpile':
      // Pass through to transpiler module which has its own CLI
      process.argv.splice(2, 1); // Remove 'transpile' command
      require('./transpiler');
      break;

    case 'pkg':
      // Pass through to package-manager module which has its own CLI
      process.argv.splice(2, 1); // Remove 'pkg' command
      require('./package-manager');
      break;

    default:
      console.error(`Unknown command: ${command}`);
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

module.exports = { main, showHelp, showVersion, initProject };
