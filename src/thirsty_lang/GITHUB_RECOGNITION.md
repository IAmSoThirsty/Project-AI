# GitHub Language Recognition for Thirsty-lang

This directory contains all necessary files and configuration for GitHub to officially recognize Thirsty-lang as a programming language.

## Files Included

### Configuration Files

1. **`.gitattributes`** - Defines language detection rules
   - Maps `.thirsty*` extensions to Thirsty-lang
   - Configures vendoring for proper statistics
   - Ensures examples are counted in language metrics

2. **`linguist.yml`** - Language metadata for GitHub Linguist
   - Language name, type, and color
   - File extensions and aliases
   - Syntax highlighting configuration

3. **`languages.yml`** - Format for GitHub Linguist submission
   - Ready to be added to github/linguist repository
   - Contains all language definition metadata

4. **`GITHUB_LINGUIST.md`** - Complete documentation
   - Language overview and features
   - Example code
   - Integration instructions
   - Submission checklist

## How It Works

### Local Recognition

GitHub automatically recognizes languages based on:

1. **File extensions** - `.gitattributes` maps extensions to languages
2. **Linguist attributes** - Controls what's counted in statistics
3. **Vendor detection** - Excludes dependencies from stats

### Repository Statistics

With these configurations:

- `.thirsty` files are counted as Thirsty-lang
- Examples are included in language statistics
- Vendor directories (node_modules, .venv) are excluded
- Language bar shows Thirsty-lang percentage

## Current Status

✅ **Configured for Local Recognition**

- Repository-level gitattributes configured
- Thirsty-lang module gitattributes configured
- All `.thirsty` files properly attributed

⏳ **Pending Official Recognition**

- Requires pull request to github/linguist
- Needs 200+ lines of code in public repos (✅ Met)
- Requires TextMate grammar (✅ Available in VS Code extension)

## Verification

Test language detection locally:

```bash

# Check specific file

git check-attr linguist-language examples/hello.thirsty

# Expected output:

# examples/hello.thirsty: linguist-language: Thirsty-lang

# Check all attributes

git check-attr -a examples/hello.thirsty

# Show all Thirsty files

find . -name "*.thirsty" -o -name "*.thirstyplus"
```

## GitHub Language Statistics

After pushing to GitHub:

1. **Language Bar**: Repository page shows Thirsty-lang percentage
2. **Search**: Can search by `language:Thirsty-lang`
3. **Statistics**: `/graphs/languages` shows Thirsty-lang
4. **Code Navigation**: Syntax highlighting (if grammar included)

## For Official GitHub Linguist Recognition

To submit Thirsty-lang to GitHub Linguist:

### 1. Fork github/linguist

```bash
git clone https://github.com/github/linguist.git
cd linguist
```

### 2. Add Language Definition

Edit `lib/linguist/languages.yml`:
```yaml

# Copy contents from languages.yml in this directory

```

### 3. Add TextMate Grammar (Optional but Recommended)

Copy from `vscode-extension/syntaxes/thirsty.tmLanguage.json`:
```bash
cp path/to/thirsty.tmLanguage.json linguist/grammars/
```

### 4. Add Samples

Add example files to `samples/Thirsty-lang/`:
```bash
mkdir -p samples/Thirsty-lang
cp examples/*.thirsty samples/Thirsty-lang/
```

### 5. Test Locally

```bash

# Install dependencies

bundle install

# Test language detection

bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty

# Run tests

bundle exec rake test
```

### 6. Submit Pull Request

Create PR with:

- Language definition in `languages.yml`
- Sample code files
- TextMate grammar (optional)
- Brief description of language

## Integration with Project-AI

Thirsty-lang is integrated into Project-AI with:

- **76 files** - Complete implementation
- **9 examples** - Various complexity levels
- **14 documents** - Comprehensive guides
- **TARL integration** - Security runtime

Repository: https://github.com/IAmSoThirsty/Project-AI

## Benefits of Official Recognition

1. **Discoverability**
   - Searchable by language on GitHub
   - Appears in trending languages
   - Better project classification

2. **Statistics**
   - Accurate language percentage in repos
   - Language-specific graphs and insights
   - Contribution tracking by language

3. **Developer Experience**
   - Syntax highlighting on GitHub
   - Language-specific search and filtering
   - Proper file type detection

4. **Community**
   - Easier to find other Thirsty-lang projects
   - Language-based recommendations
   - Developer network effects

## Troubleshooting

### Language Not Showing in Stats

1. **Check gitattributes**: `git check-attr -a file.thirsty`
2. **Verify vendoring**: Ensure examples aren't marked as vendored
3. **Force refresh**: May take time for GitHub to update stats
4. **Check file size**: Very small files may be ignored

### Incorrect Language Detection

1. **Check extension**: Ensure file ends with `.thirsty`
2. **Verify attributes**: Use `git check-attr linguist-language file.thirsty`
3. **Check heuristics**: May need disambiguation rules
4. **Clear cache**: `git rm --cached -r .` then `git add .`

## Resources

- [GitHub Linguist](https://github.com/github/linguist)
- [Contributing Guide](https://github.com/github/linguist/blob/master/CONTRIBUTING.md)
- [Linguist Documentation](https://github.com/github/linguist/blob/master/docs/index.md)
- [Language Grammar Guide](https://github.com/github/linguist/blob/master/docs/grammars.md)

## Contact

- **Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **Issues**: https://github.com/IAmSoThirsty/Thirsty-lang/issues
- **Author**: Jeremy Karrick (IAmSoThirsty)

---

**Status**: ✅ Configured for GitHub Recognition
**Last Updated**: 2026-01-28
**Version**: 1.0.0
