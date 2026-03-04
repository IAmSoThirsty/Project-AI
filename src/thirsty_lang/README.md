<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# Thirsty-lang 💧🔒

This is my Language for anyone and everyone who is Thirsty - now with **Defensive Programming** capabilities!

## About

Thirsty-lang is a unique, expressive programming language designed to be **defensive and combative** against all known code threats. It combines fun water-themed syntax with enterprise-grade security features.

## Features

- ✨ Simple and intuitive syntax
- 🔒 **Defensive Programming - Built-in security against all attack vectors**
- 🛡️ **Threat Detection - White/Grey/Black/Red box attack detection**
- 🔄 **Code Morphing - Dynamic obfuscation and anti-analysis**
- 🎯 **Security Keywords - shield, morph, detect, defend, sanitize, armor**
- 🚨 **Counter-Strike Mode - Automated attacker neutralization**
- 🎓 Interactive training program for all skill levels
- 🔍 Built-in REPL for experimenting
- 🐛 Full-featured debugger
- 📊 Performance profiler
- 🎨 Code formatter and linter
- 📚 Automatic documentation generator
- 🌐 Web playground
- 🔄 Transpiler to JavaScript, Python, Go, Rust, Java, and C
- 📦 Package manager
- 🌳 AST generator
- 🎯 Multiple language editions (Base, Plus, PlusPlus, ThirstOfGods)
- 🔌 VS Code extension support
- 🐍 **Python implementation included**
- 🐳 **Docker and Docker Compose support**
- 🔒 **Virtual environment setup**
- 🤖 **Project-AI Integration Ready**

## Getting Started

### Prerequisites

**Choose your runtime:**

- **Node.js** (Primary): 14 or higher
- **Python** (Alternative): 3.8 or higher
- **Docker** (Optional): For containerized execution

### Installation

#### Node.js Setup (Primary)

```bash
npm install
```

#### Python Setup (Alternative)

```bash

# Automated setup

./setup_venv.sh

# Manual setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Docker Setup (Optional)

```bash

# Build and run with Docker Compose

docker-compose up

# Or build Docker image directly

docker build -t thirsty-lang .
```

See [DOCKER.md](DOCKER.md) for detailed Docker instructions and [PYTHON_SETUP.md](PYTHON_SETUP.md) for Python setup guide.

### Quick Start

#### Using Node.js

```bash

# Run a program

npm start examples/hello.thirsty

# Or use the unified CLI

node src/thirsty-cli.js run examples/hello.thirsty
```

#### Using Python

```bash

# Activate virtual environment (if using)

source .venv/bin/activate

# Run a program

python3 src/thirsty_interpreter.py examples/hello.thirsty

# Start Python REPL

python3 src/thirsty_repl.py
```

#### Using Docker

```bash

# Run a program

docker-compose run --rm thirsty node src/cli.js examples/hello.thirsty

# Start Node.js REPL

docker-compose run --rm repl

# Start Python REPL

docker-compose run --rm python-repl
```

### Interactive Training Program 🎓

Learn Thirsty-lang interactively with our built-in training program:

```bash
npm run train
```

The training program includes:

- 💧 **Base Thirsty-lang**: Fundamentals for beginners
- 💧+ **Thirsty Plus**: Control flow and logic
- 💧++ **Thirsty Plus Plus**: Functions and loops
- ⚡ **ThirstOfGods**: Advanced OOP and async features

### Running Thirsty-lang Programs

```bash
npm start examples/hello.thirsty
```

### Running Tests

```bash
npm test

# Run security tests

node src/test/security-tests.js
```

## Language Syntax

### Core Keywords (Water-Themed)

- `drink` - Variable declaration
- `pour` - Output/print statement
- `sip` - Input statement
- `thirsty` - If statement
- `hydrated` - Else statement
- `refill` - Loop statement
- `glass` - Function declaration

### Security Keywords (Defensive Programming)

- `shield` - Mark code blocks for protection
- `morph` - Enable dynamic code mutation
- `detect` - Set up threat monitoring
- `defend` - Automatic countermeasures
- `sanitize` - Input/output cleaning
- `armor` - Memory protection

### Example Programs

#### Basic Program

```thirsty
drink water = "Hello, World!"
pour water
```

#### Secure Program with Defensive Features

```thirsty
shield mySecureApp {
  detect attacks {
    morph on: ["injection", "overflow", "timing"]
    defend with: "aggressive"
  }

  drink userData = sip "Enter your name"
  sanitize userData
  armor userData

  pour "Hello, " + userData
}
```

See more examples in the `examples/` and `examples/security/` directories.

## Defensive Programming Features

Thirsty-lang is designed to be **combative against all known code threats**:

### Attack Detection

- **White Box** - SQL injection, XSS, command injection, path traversal
- **Grey Box** - Timing attacks, brute force, enumeration
- **Black Box** - Buffer overflows, DoS, type confusion
- **Red Team** - Reverse engineering, memory dumps, VM detection

### Code Protection

- **Code Morphing** - Dynamic obfuscation and polymorphism
- **Anti-Debugging** - Debugger detection and prevention
- **Memory Safety** - Automatic bounds checking and type safety
- **Input Sanitization** - Comprehensive input validation

### Security Modes

- `passive` - Log threats only
- `moderate` - Warn and sanitize (default)
- `aggressive` - Block threats
- `paranoid` - Counter-strike with honeypots and deception

See [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) for comprehensive security documentation.

## Project-AI Integration

For superior AI-powered security measures, Thirsty-lang integrates with [Project-AI](https://github.com/IAmSoThirsty/Project-AI).

See [PROJECT_AI_INTEGRATION.md](PROJECT_AI_INTEGRATION.md) for integration details.

## Available Tools

### REPL (Read-Eval-Pour-Loop)

```bash
npm run repl
```
Interactive console with history, variables inspection, and session saving.

### Debugger

```bash
npm run debug examples/hello.thirsty
```
Step through code, set breakpoints, watch variables, and inspect state.

### Code Formatter

```bash
npm run format examples/hello.thirsty
```
Automatically format your code with consistent style.

### Linter

```bash
npm run lint examples/hello.thirsty
```
Check for code quality issues and style violations.

### Performance Profiler

```bash
npm run profile examples/hello.thirsty
```
Measure execution time and identify performance bottlenecks.

### Documentation Generator

```bash
npm run doc examples/hello.thirsty
```
Generate beautiful HTML and Markdown documentation.

### AST Generator

```bash
npm run ast examples/hello.thirsty
```
Visualize the Abstract Syntax Tree of your code.

### Transpiler

```bash
node src/transpiler.js examples/hello.thirsty --target python
```
Convert Thirsty-lang to JavaScript, Python, Go, Rust, Java, or C.

### Package Manager

```bash
node src/package-manager.js init my-project
node src/package-manager.js install
```
Manage dependencies and packages for your projects.

### Web Playground

Open `playground/index.html` in your browser for an interactive web-based editor!

### Docker Services

```bash

# See all available services

docker-compose ps

# Run specific services (see DOCKER.md for details)

docker-compose up playground     # Web playground on port 8888
docker-compose up training       # Interactive training
```

## Implementation Support

Thirsty-lang includes two complete implementations:

### Node.js Implementation (Primary)

- **Fast and feature-complete**
- All tools and utilities included
- Production-ready
- Run: `node src/cli.js <file.thirsty>`

### Python Implementation (Alternative)

- **Pure Python with standard library**
- Educational and portable
- Cross-platform compatible
- Run: `python3 src/thirsty_interpreter.py <file.thirsty>`

See [PYTHON_SETUP.md](PYTHON_SETUP.md) for detailed Python setup and usage.

### Docker Support

- **Multi-service architecture**
- Development and production images
- Pre-configured services for all tools
- See [DOCKER.md](DOCKER.md) for complete Docker guide

## Language Editions

Thirsty-lang comes in four flavors:

| Edition | Level | Description |
|---------|-------|-------------|
| 💧 **Base** | Beginner | Core features: variables, output |
| 💧+ **Thirsty+** | Intermediate | Adds control flow, conditionals |
| 💧++ **Thirsty++** | Advanced | Functions, loops, arrays |
| ⚡ **ThirstOfGods** | Master | Classes, async/await, modules |

See [docs/EXPANSIONS.md](docs/EXPANSIONS.md) for detailed information.

## Documentation

Full language specification and documentation can be found in the `docs/` directory and root:

### Core Documentation

- [README.md](README.md) - Main documentation (this file)
- [Language Specification](docs/SPECIFICATION.md) - Complete syntax and semantics
- [Expansions Guide](docs/EXPANSIONS.md) - Multi-tier language editions
- [Tutorial](docs/TUTORIAL.md) - Step-by-step learning guide
- [Quick Reference](docs/QUICK_REFERENCE.md) - Syntax cheat sheet
- [FAQ](docs/FAQ.md) - Frequently asked questions
- [Installation Guide](docs/INSTALLATION.md) - Setup instructions

### Setup Guides

- [PYTHON_SETUP.md](PYTHON_SETUP.md) - Python implementation setup
- [DOCKER.md](DOCKER.md) - Docker and containerization guide

### Project Information

- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes
- [AUTHORS.txt](AUTHORS.txt) - Contributors and authors
- [DEPENDENCIES.txt](DEPENDENCIES.txt) - Dependency information
- [VERSION.txt](VERSION.txt) - Current version
- [LICENSE](LICENSE) - License terms

## VS Code Extension

Syntax highlighting and code snippets are available in `vscode-extension/`.

To install:

1. Copy the `vscode-extension` folder to your VS Code extensions directory
1. Reload VS Code
1. Enjoy syntax highlighting for `.thirsty` files!

See [vscode-extension/README.md](vscode-extension/README.md) for detailed installation instructions.

## Project Structure

```
Thirsty-lang/
├── src/
│   ├── index.js                # Main Node.js interpreter
│   ├── cli.js                  # CLI runner
│   ├── thirsty-cli.js          # Unified CLI
│   ├── repl.js                 # Interactive REPL
│   ├── training.js             # Interactive training program
│   ├── debugger.js             # Debugger
│   ├── formatter.js            # Code formatter
│   ├── linter.js               # Code linter
│   ├── profiler.js             # Performance profiler
│   ├── doc-generator.js        # Documentation generator
│   ├── ast.js                  # AST generator
│   ├── transpiler.js           # Multi-language transpiler
│   ├── package-manager.js      # Package manager
│   ├── thirsty_interpreter.py  # Python interpreter
│   ├── thirsty_repl.py         # Python REPL
│   ├── thirsty_utils.py        # Python utilities
│   └── test/                   # Test suite
├── examples/                   # Example programs
│   ├── hello.thirsty
│   ├── variables.thirsty
│   ├── hydration.thirsty
│   └── advanced/               # Advanced examples
├── docs/                       # Documentation
├── playground/                 # Web playground
├── vscode-extension/           # VS Code extension
├── tools/                      # Benchmark tools
├── requirements.txt            # Python core dependencies
├── requirements-dev.txt        # Python dev dependencies
├── setup_venv.sh               # Python venv setup script
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker multi-service setup
├── .dockerignore               # Docker ignore file
├── CHANGELOG.md                # Version history
├── AUTHORS.txt                 # Contributors
├── DEPENDENCIES.txt            # Dependency information
├── VERSION.txt                 # Current version
└── .github/workflows/          # CI/CD
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the terms in the LICENSE file.

## Author

Created by someone who believes coding should be refreshing! 💧

## Stay Connected

- 🐛 [Report Issues](https://github.com/IAmSoThirsty/Thirsty-lang/issues)
- 💡 [Request Features](https://github.com/IAmSoThirsty/Thirsty-lang/issues/new)
- ⭐ [Star on GitHub](https://github.com/IAmSoThirsty/Thirsty-lang)

Stay hydrated and happy coding! 💧✨
