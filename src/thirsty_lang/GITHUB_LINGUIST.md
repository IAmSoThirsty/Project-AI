# Thirsty-lang - GitHub Linguist Language Definition
# For submission to: https://github.com/github/linguist

## Language Overview

**Name:** Thirsty-lang  
**Type:** Programming Language  
**Category:** Defensive Programming / Systems Programming  
**First Appeared:** 2025  
**Designer:** Jeremy Karrick (IAmSoThirsty)

## Language Characteristics

### Extensions
- `.thirsty` (primary)
- `.thirstyplus` (enhanced edition)
- `.thirstyplusplus` (advanced edition)
- `.thirstofgods` (master edition)

### Syntax Highlighting
- **TextMate Scope:** source.thirsty
- **Color Scheme:** #00BFFF (Deep Sky Blue - water themed)
- **Line Comment:** `//`
- **Block Comment:** None (uses line comments)

### Language Type
- **Type:** Programming
- **Paradigm:** Multi-paradigm (imperative, defensive)
- **Typing:** Dynamic

## Distinguishing Features

1. **Water-Themed Syntax**: Uses intuitive water-related keywords
   - `drink` - Variable declaration
   - `pour` - Output/print statement
   - `sip` - Input statement
   - `thirsty` - If statement
   - `hydrated` - Else statement
   - `refill` - Loop statement
   - `glass` - Function declaration

2. **Defensive Programming Keywords**: Built-in security features
   - `shield` - Protection blocks
   - `morph` - Code obfuscation
   - `detect` - Threat monitoring
   - `defend` - Countermeasures
   - `sanitize` - Input/output cleaning
   - `armor` - Memory protection

3. **Security-First Design**
   - Threat detection (white/grey/black/red box)
   - Dynamic code morphing
   - Automated attack mitigation
   - Counter-strike capabilities

## Implementation

### Runtimes
- **Primary:** Node.js (JavaScript interpreter)
- **Alternative:** Python 3.8+
- **Container:** Docker support

### Tools & Ecosystem
- REPL (interactive shell)
- Debugger (source-level debugging)
- Profiler (performance analysis)
- Linter & Formatter (code quality)
- Transpiler (to JS, Python, Go, Rust, Java, C)
- Package Manager
- VS Code Extension
- Web Playground

## Example Code

```thirsty
// Hello World in Thirsty-lang
drink message = "Hello, World!"
pour message
```

```thirsty
// Secure program with defensive features
shield mySecureApp {
  detect attacks {
    morph on: ["injection", "overflow"]
    defend with: "aggressive"
  }
  
  drink userData = sip "Enter name"
  sanitize userData
  armor userData
  
  pour "Hello, " + userData
}
```

## Repository Information

- **Main Repository:** https://github.com/IAmSoThirsty/Thirsty-lang
- **Project-AI Integration:** https://github.com/IAmSoThirsty/Project-AI
- **License:** MIT
- **Author:** Jeremy Karrick
- **Contributors:** See AUTHORS.txt

## Language Statistics

- **File Count:** 76+ implementation files
- **Example Programs:** 9+ in various complexity levels
- **Documentation:** 14+ comprehensive guides
- **Lines of Code:** 10,000+ (implementation)

## Integration with GitHub

### Linguist Configuration

Add to `.gitattributes`:
```gitattributes
*.thirsty linguist-language=Thirsty-lang linguist-detectable
*.thirstyplus linguist-language=Thirsty-lang linguist-detectable
*.thirstyplusplus linguist-language=Thirsty-lang linguist-detectable
*.thirstofgods linguist-language=Thirsty-lang linguist-detectable
```

### Language Recognition

For GitHub to officially recognize Thirsty-lang:

1. **Add to `languages.yml`:**
```yaml
Thirsty-lang:
  type: programming
  color: "#00BFFF"
  extensions:
  - ".thirsty"
  - ".thirstyplus"
  - ".thirstyplusplus"
  - ".thirstofgods"
  tm_scope: source.thirsty
  ace_mode: text
  language_id: 472923847
```

2. **Add to `heuristics.yml`** (if needed for disambiguation)

3. **Add TextMate Grammar** (already exists in VS Code extension)

4. **Submit Pull Request** to github/linguist repository

## Verification

To verify language detection:

```bash
# Check gitattributes
git check-attr linguist-language src/thirsty_lang/examples/hello.thirsty

# Expected output:
# src/thirsty_lang/examples/hello.thirsty: linguist-language: Thirsty-lang
```

## Submission Checklist

For official GitHub Linguist recognition:

- [x] Language has unique file extensions
- [x] Language has at least 200 lines of code in public repos
- [x] Language has clear syntax definition (TextMate grammar)
- [x] Language has documentation
- [x] Language has example code
- [x] gitattributes configured
- [x] linguist.yml created
- [ ] Pull request to github/linguist (pending)

## Contact

- **Issue Tracker:** https://github.com/IAmSoThirsty/Thirsty-lang/issues
- **Documentation:** https://github.com/IAmSoThirsty/Thirsty-lang#readme
- **Community:** GitHub Discussions

## References

- GitHub Linguist: https://github.com/github/linguist
- Contributing Guide: https://github.com/github/linguist/blob/master/CONTRIBUTING.md
- Language Grammar Guide: https://github.com/github/linguist/blob/master/docs/grammars.md

---

**Status:** Ready for GitHub recognition  
**Last Updated:** 2026-01-28  
**Version:** 1.0.0
