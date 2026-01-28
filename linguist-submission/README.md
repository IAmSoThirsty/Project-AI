# GitHub Linguist Submission Package for Thirsty-lang

This directory contains everything needed to submit Thirsty-lang to the [github/linguist](https://github.com/github/linguist) repository for official language recognition.

## Package Contents

### 1. Language Definition (`languages.yml`)
Contains the language metadata required by GitHub Linguist:
- Language name, type, and color
- File extensions (`.thirsty`, `.thirstyplus`, `.thirstyplusplus`, `.thirstofgods`)
- TextMate scope and language ID
- Supported interpreters

### 2. TextMate Grammar (`grammars/thirsty.tmLanguage.json`)
Syntax highlighting grammar for Thirsty-lang:
- Keyword definitions (drink, pour, sip, thirsty, hydrated, etc.)
- Comment patterns
- String and number matching
- Operator definitions
- Scope: `source.thirsty`

### 3. Sample Files (`samples/*.thirsty*`)
Representative code examples showcasing Thirsty-lang features:
- `hello.thirsty` - Basic "Hello, World!" example
- `variables.thirsty` - Variable declarations and types
- `hydration.thirsty` - Simple program with output
- `control-flow.thirstyplus` - Conditional statements and logic
- `basic-protection.thirsty` - Security features (shield, sanitize, armor)

## Language Features

**Thirsty-lang** is a unique programming language with:

### Water-Themed Syntax
- `drink` - Variable declaration
- `pour` - Output statement
- `sip` - Input statement
- `thirsty` - If statement
- `hydrated` - Else statement
- `refill` - Loop statement
- `glass` - Function declaration

### Defensive Programming
- `shield` - Protection blocks
- `morph` - Code obfuscation
- `detect` - Threat monitoring
- `defend` - Countermeasures
- `sanitize` - Input/output cleaning
- `armor` - Memory protection

### Multiple Editions
- **Base** (`.thirsty`) - Core features
- **Plus** (`.thirstyplus`) - Enhanced features
- **PlusPlus** (`.thirstyplusplus`) - Advanced features
- **ThirstOfGods** (`.thirstofgods`) - Master edition

## Submission Instructions

### Prerequisites
1. Fork the [github/linguist](https://github.com/github/linguist) repository
2. Clone your fork locally
3. Install Ruby and dependencies: `bundle install`

### Step 1: Add Language Definition

Edit `lib/linguist/languages.yml` in the linguist repository:

```yaml
# Add the contents of languages.yml from this directory
# Place alphabetically under "T" section
```

Or simply append the contents of `languages.yml` to linguist's `languages.yml` file.

### Step 2: Add TextMate Grammar

Copy the grammar file to linguist's grammars directory:

```bash
cp grammars/thirsty.tmLanguage.json /path/to/linguist/vendor/grammars/thirsty.tmLanguage.json
```

Then update `grammars.yml` in linguist repository:

```yaml
vendor/grammars/thirsty.tmLanguage.json:
  - source.thirsty
```

### Step 3: Add Sample Files

Copy sample files to linguist's samples directory:

```bash
mkdir -p /path/to/linguist/samples/Thirsty-lang
cp samples/*.thirsty* /path/to/linguist/samples/Thirsty-lang/
```

Linguist requires at least 3 sample files. This package includes 5 samples.

### Step 4: Update Vendor Directory (if needed)

If TextMate grammar is hosted elsewhere, add to `vendor.yml`:

```yaml
# Add to vendor.yml if grammar is from external source
- vendor/grammars/thirsty.tmLanguage.json
```

### Step 5: Run Tests

Test language detection locally:

```bash
cd /path/to/linguist

# Test detection on sample file
bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty

# Run full test suite
bundle exec rake test

# Generate language data
bundle exec rake samples
```

Expected output for hello.thirsty:
```
samples/Thirsty-lang/hello.thirsty: 100.00% (3 lines) Thirsty-lang
```

### Step 6: Create Pull Request

1. Commit your changes:
```bash
git add lib/linguist/languages.yml
git add vendor/grammars/thirsty.tmLanguage.json
git add grammars.yml
git add samples/Thirsty-lang/
git commit -m "Add support for Thirsty-lang"
```

2. Push to your fork:
```bash
git push origin add-thirsty-lang
```

3. Create PR with this description:

```markdown
## Add support for Thirsty-lang

This PR adds support for Thirsty-lang, a unique programming language with water-themed syntax and defensive programming capabilities.

### Language Overview
- **Type**: Programming
- **Extensions**: `.thirsty`, `.thirstyplus`, `.thirstyplusplus`, `.thirstofgods`
- **Color**: #00BFFF (Deep Sky Blue)
- **Scope**: source.thirsty

### Features
- Water-themed keywords (drink, pour, sip, thirsty, hydrated)
- Built-in security features (shield, sanitize, armor)
- Multiple language editions
- Active development and community

### Checklist
- [x] Language definition added to `languages.yml`
- [x] TextMate grammar included
- [x] At least 3 sample files provided (5 included)
- [x] Tests pass locally
- [x] Samples demonstrate language features

### Repository
- Main: https://github.com/IAmSoThirsty/Thirsty-lang
- Integration: https://github.com/IAmSoThirsty/Project-AI

### Author
Jeremy Karrick (@IAmSoThirsty)
```

## Validation Checklist

Before submitting, ensure:

- [ ] `languages.yml` contains valid YAML
- [ ] TextMate grammar is valid JSON
- [ ] At least 3 sample files included (✓ 5 provided)
- [ ] Sample files demonstrate key language features
- [ ] Grammar scope matches `tm_scope` in languages.yml
- [ ] Language ID is unique (472923847)
- [ ] All file extensions listed
- [ ] Tests pass in linguist repository
- [ ] PR description is complete

## Post-Submission

After your PR is merged:

1. **Language Recognition**: GitHub will recognize `.thirsty` files
2. **Statistics**: Language appears in repository stats
3. **Search**: Can search by `language:Thirsty-lang`
4. **Syntax Highlighting**: Code displays with proper colors
5. **Community**: Language becomes discoverable

## Testing Locally (Before Submission)

You can test the language definition without submitting:

```bash
# In linguist repository
bundle exec linguist samples/Thirsty-lang/hello.thirsty

# Should output:
# samples/Thirsty-lang/hello.thirsty: 100.00% (3 lines) Thirsty-lang
```

## Common Issues

### Issue: "Language not detected"
- Check that file extension matches `extensions` in languages.yml
- Verify scope in grammar matches `tm_scope` in languages.yml

### Issue: "Grammar not working"
- Validate JSON syntax in tmLanguage file
- Ensure `scopeName` in grammar matches `tm_scope`

### Issue: "Tests failing"
- Run `bundle exec rake test` to see specific errors
- Check that language ID is unique
- Verify sample files have proper extensions

## Additional Resources

- [Linguist Documentation](https://github.com/github/linguist/blob/master/docs/README.md)
- [Contributing Guide](https://github.com/github/linguist/blob/master/CONTRIBUTING.md)
- [Language Grammar Guide](https://github.com/github/linguist/blob/master/docs/grammars.md)
- [Testing Guide](https://github.com/github/linguist/blob/master/docs/testing.md)

## Contact

- **Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **Issues**: https://github.com/IAmSoThirsty/Thirsty-lang/issues
- **Author**: Jeremy Karrick (@IAmSoThirsty)

---

**Status**: Ready for submission  
**Last Updated**: 2026-01-28  
**Version**: 1.0.0

For questions or issues with this submission package, please open an issue in the Thirsty-lang repository.
