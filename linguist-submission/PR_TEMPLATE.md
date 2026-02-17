## Add support for Thirsty-lang

This PR adds support for Thirsty-lang, a unique programming language with water-themed syntax and defensive programming capabilities.

### Language Overview

**Thirsty-lang** is a modern programming language featuring:

- Water-themed syntax for intuitive programming
- Built-in defensive programming and security features
- Multiple language editions (Base, Plus, PlusPlus, ThirstOfGods)
- Active development and growing community

### Language Details

- **Type**: Programming
- **Extensions**: `.thirsty`, `.thirstyplus`, `.thirstyplusplus`, `.thirstofgods`
- **Color**: #00BFFF (Deep Sky Blue - water themed)
- **TextMate Scope**: source.thirsty
- **Language ID**: 472923847
- **Interpreters**: node, python3

### Syntax Highlights

```thirsty
// Hello World
drink message = "Hello, World!"
pour message

// Conditional logic
thirsty temperature > 30
  pour "It's hot! Stay hydrated!"
hydrated
  pour "Normal temperature"

// Security features
shield myApp {
  drink userData = sip "Enter name"
  sanitize userData
  armor userData
  pour "Hello, " + userData
}
```

### Key Features

**Water-Themed Keywords:**

- `drink` - Variable declaration
- `pour` - Output statement
- `sip` - Input statement
- `thirsty` - If statement
- `hydrated` - Else statement
- `refill` - Loop statement
- `glass` - Function declaration

**Defensive Programming:**

- `shield` - Protection blocks
- `morph` - Code obfuscation
- `detect` - Threat monitoring
- `defend` - Countermeasures
- `sanitize` - Input/output cleaning
- `armor` - Memory protection

### Checklist

- [x] Language definition added to `lib/linguist/languages.yml`
- [x] TextMate grammar included in `vendor/grammars/thirsty.tmLanguage.json`
- [x] Grammar reference added to `grammars.yml`
- [x] At least 3 sample files provided in `samples/Thirsty-lang/` (5 included)
- [x] Samples demonstrate key language features
- [x] Tests pass locally (`bundle exec rake test`)
- [x] Language detection verified (`bundle exec bin/linguist samples/Thirsty-lang/*.thirsty`)

### Sample Files Included

1. **hello.thirsty** - Basic "Hello, World!" example
2. **variables.thirsty** - Variable declarations and types
3. **hydration.thirsty** - Simple program with output
4. **control-flow.thirstyplus** - Conditional statements (Thirsty+ edition)
5. **basic-protection.thirsty** - Security features demonstration

### Testing

Local tests confirm proper language detection:

```bash
$ bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty
samples/Thirsty-lang/hello.thirsty: 100.00% (3 lines) Thirsty-lang

$ bundle exec rake test

# All tests pass

```

### Repository Information

- **Main Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **Integration Repository**: https://github.com/IAmSoThirsty/Project-AI
- **License**: MIT
- **Author**: Jeremy Karrick (@IAmSoThirsty)
- **Documentation**: Available in repository

### Implementation Details

The language has:

- Full JavaScript and Python implementations
- REPL, debugger, and profiler
- VS Code extension with syntax highlighting
- Comprehensive documentation
- Active development since 2025
- 1,000+ lines of code in active use

### Community

- Growing user base
- Educational focus
- Security-first design
- Multiple example projects

### Related Projects

- [Project-AI](https://github.com/IAmSoThirsty/Project-AI) - Integration with AI systems
- [TARL](https://github.com/IAmSoThirsty/Project-AI/tree/main/tarl) - Security runtime layer

### Additional Notes

This language brings a unique approach to programming education with its water-themed metaphors while maintaining practical security features. The defensive programming capabilities make it suitable for teaching secure coding practices.

---

Thank you for considering this submission! Please let me know if any adjustments are needed.

cc: @IAmSoThirsty
