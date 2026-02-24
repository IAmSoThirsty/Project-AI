# Thirsty-lang for VS Code 💧

**Syntax highlighting, code snippets, and language support for [Thirsty-lang](https://github.com/IAmSoThirsty/Thirsty-lang)** — the fun, water-themed programming language with built-in defensive security features.

## Features

- 🎨 **Syntax Highlighting** — Full TextMate grammar for all Thirsty-lang keywords
- ✂️ **Code Snippets** — Quick templates for common patterns
- 📝 **Language Configuration** — Auto-closing brackets, comment toggling, indentation rules

## Supported File Extensions

| Extension | Edition |
|---|---|
| `.thirsty` | Standard |
| `.thirstyplus` | Enhanced |
| `.thirstyplusplus` | Advanced |
| `.thirstofgods` | Master |

## Syntax Preview

```thirsty
// Hello World in Thirsty-lang
drink message = "Hello, Thirsty World!"
pour message

// Control flow
drink temperature = 30
thirsty temperature > 25 {
  pour "Stay hydrated!"
}
hydrated {
  pour "Drink up anyway!"
}

// Loops
drink glasses = 0
refill glasses < 8 {
  drink glasses = glasses + 1
  pour glasses
}
```

## Keywords

| Keyword | Purpose |
|---|---|
| `drink` | Variable declaration |
| `pour` | Output / print |
| `sip` | Input |
| `thirsty` | If statement |
| `hydrated` | Else statement |
| `refill` | Loop |
| `glass` | Function declaration |
| `fountain` | Class declaration |
| `cascade` | Async function |
| `shield` | Protected code block |
| `sanitize` | HTML encoding / input cleaning |
| `armor` | Memory protection |
| `morph` | Code obfuscation |
| `detect` | Threat monitoring |
| `defend` | Automated countermeasures |
| `reservoir` | Array declaration |

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search for **"Thirsty-lang"**
4. Click **Install**

### From VSIX

```bash
code --install-extension thirsty-lang-1.0.0.vsix
```

## Requirements

- VS Code ≥ 1.60.0

## Links

- [GitHub Repository](https://github.com/IAmSoThirsty/Thirsty-lang)
- [Language Specification](https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/SPECIFICATION.md)
- [npm Package](https://www.npmjs.com/package/thirsty-lang)
- [PyPI Package](https://pypi.org/project/thirsty-lang/)

## License

MIT — See [LICENSE](LICENSE)

---

**Stay hydrated and happy coding! 💧**
