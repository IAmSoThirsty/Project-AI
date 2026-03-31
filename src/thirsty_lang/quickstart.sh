#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env bash

# Thirsty-lang Quick Start Script
# Helps users get started with Thirsty-lang quickly!

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          💧 Welcome to Thirsty-lang! 💧                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "   Please install Node.js from https://nodejs.org"
    echo "   Required version: 14.0.0 or higher"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    echo "⚠️  Node.js version is too old (found v$(node --version))"
    echo "   Required: v14.0.0 or higher"
    echo "   Please upgrade from https://nodejs.org"
    exit 1
fi

echo "✓ Node.js $(node --version) detected"
echo ""

# Run tests
echo "Running tests..."
npm test
TEST_EXIT_CODE=$?
if [ "$TEST_EXIT_CODE" -ne 0 ]; then
    echo "❌ 'npm test' did not complete successfully (exit code $TEST_EXIT_CODE)."
    exit 1
fi
echo ""

# Run a demo program
echo "Running demo program..."
npm start examples/hello.thirsty
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 Setup Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "What would you like to do next?"
echo ""
echo "  1. 🎓 Start interactive training"
echo "     npm run train"
echo ""
echo "  2. 🔍 Launch the REPL"
echo "     npm run repl"
echo ""
echo "  3. 📝 Create a new project"
echo "     node src/thirsty-cli.js init my-project"
echo ""
echo "  4. 🎮 Try the web playground"
echo "     Open playground/index.html in your browser"
echo ""
echo "  5. 📚 Read the documentation"
echo "     Check out the docs/ directory"
echo ""
echo "  6. 🚀 Run more examples"
echo "     npm start examples/variables.thirsty"
echo "     npm start examples/hydration.thirsty"
echo ""
echo "Stay hydrated and happy coding! 💧✨"
echo ""
