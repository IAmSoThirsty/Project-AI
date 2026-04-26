# Getting Started Tutorial

Welcome to Thirsty-lang! This tutorial will guide you through your first steps.

## Lesson 1: Your First Program

Let's write the classic "Hello, World!" program:

```thirsty
drink message = "Hello, World!"
pour message
```

**Explanation:**

- `drink message = "Hello, World!"` creates a variable called `message` and assigns it the text "Hello, World!"
- `pour message` outputs the value of `message` to the console

Save this as `hello.thirsty` and run:
```bash
npm start hello.thirsty
```

Output:
```
Hello, World!
```

## Lesson 2: Working with Numbers

Thirsty-lang can work with numbers too:

```thirsty
drink glasses_per_day = 8
drink liters_per_glass = 0.25
drink total_liters = 2.0

pour "Daily hydration goal:"
pour glasses_per_day
pour "glasses"

pour "Total liters:"
pour total_liters
```

**Key Points:**

- Numbers don't need quotes
- You can use integers (8) or decimals (0.25)
- Each variable stores one value

## Lesson 3: Using the REPL

The REPL (Read-Eval-Pour-Loop) lets you experiment interactively:

```bash
npm run repl
```

Try typing:
```thirsty
💧> drink water = "H2O"
💧> pour water
H2O
💧> drink temp = 25
💧> pour temp
25
💧> .vars
```

**REPL Commands:**

- `.help` - Show available commands
- `.vars` - List all variables
- `.clear` - Clear all variables
- `.exit` - Exit REPL

## Lesson 4: Comments

Add comments to explain your code:

```thirsty
// This is a comment - it's ignored by the interpreter
drink username = "ThirstyCoder"

// Comments help explain what your code does
pour username  // You can also comment at the end of lines
```

## Lesson 5: Using the Debugger

Debug your code step-by-step:

1. Create `debug_example.thirsty`:

```thirsty
drink a = 10
drink b = 20
drink c = 30
pour a
pour b
pour c
```

1. Run the debugger:

```bash
npm run debug debug_example.thirsty
```

1. Try these debugger commands:
- `s` or `step` - Execute next line
- `c` or `continue` - Run until breakpoint
- `vars` - Show all variables
- `watch a` - Watch variable 'a'
- `help` - Show all commands

## Lesson 6: Code Quality Tools

### Format Your Code

```bash
node src/formatter.js myfile.thirsty
```

This ensures consistent styling.

### Lint Your Code

```bash
node src/linter.js myfile.thirsty
```

This checks for common issues and best practices.

### Profile Performance

```bash
node src/profiler.js myfile.thirsty
```

This shows execution time and helps optimize your code.

## Lesson 7: Transpiling

Convert your Thirsty-lang code to other languages:

```bash
# To Python
node src/transpiler.js hello.thirsty --target python

# To JavaScript
node src/transpiler.js hello.thirsty --target javascript

# To Go
node src/transpiler.js hello.thirsty --target go --wrap

# Save to file
node src/transpiler.js hello.thirsty --target python --output hello.py
```

## Lesson 8: Generate Documentation

Create beautiful docs from your code:

```bash
node src/doc-generator.js myfile.thirsty docs/output
```

Then open `docs/output/index.html` in your browser!

## Lesson 9: Web Playground

Try Thirsty-lang in your browser:

1. Open `playground/index.html`
1. Write or edit code in the editor
1. Click "Run" to execute
1. Use keyboard shortcut: Ctrl/Cmd + Enter

Features:

- Live code editing
- Instant execution
- Example programs
- Shareable links
- Download your code

## Lesson 10: Interactive Training

For a comprehensive learning experience:

```bash
npm run train
```

This interactive program guides you through:

1. Base Thirsty-lang fundamentals
1. Thirsty+ control flow
1. Thirsty++ functions and loops
1. ThirstOfGods advanced features

## Practice Exercises

Try these exercises to practice:

### Exercise 1: Personal Info

Create variables for your name, age, and favorite drink, then output them.

### Exercise 2: Math

Create three number variables and output each one.

### Exercise 3: Comments

Write a program with at least 3 comments explaining what it does.

### Exercise 4: Hydration Tracker

Create variables for:

- Target glasses per day (8)
- Glasses consumed (5)
- Then output both values

### Exercise 5: Use All Tools

For your hydration tracker:

1. Format it
1. Lint it
1. Profile it
1. Generate docs
1. Transpile it to Python

## Next Steps

- 📚 Read the [Language Specification](SPECIFICATION.md)
- 🚀 Explore [Expansions](EXPANSIONS.md) (Thirsty+, Thirsty++, ThirstOfGods)
- 💡 Check [Advanced Examples](../examples/advanced/)
- 🤝 Read [Contributing Guidelines](../CONTRIBUTING.md)

## Tips for Success

1. **Start simple** - Master basics before advanced features
1. **Experiment** - Use the REPL to try things quickly
1. **Read examples** - Learn from code in `examples/` directory
1. **Use tools** - Debugger, linter, formatter help you learn
1. **Have fun** - Programming should be refreshing!

## Common Mistakes

❌ **Forgetting quotes around strings**
```thirsty
drink name = ThirstyCoder  // Wrong!
drink name = "ThirstyCoder"  // Correct!
```

❌ **Misspelling keywords**
```thirsty
drank water = "H2O"  // Wrong! It's 'drink'
drink water = "H2O"  // Correct!
```

❌ **Missing equals sign**
```thirsty
drink water "H2O"  // Wrong!
drink water = "H2O"  // Correct!
```

## Getting Help

- Run `thirsty help` for command info
- Check [FAQ](FAQ.md) for common questions
- Read [Quick Reference](QUICK_REFERENCE.md) for syntax
- Open issues on GitHub for bugs

Congratulations! You've completed the tutorial. Now go build something awesome and stay hydrated! 💧✨
