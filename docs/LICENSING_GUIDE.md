# Licensing Guide for Project-AI

**Status**: ✅ MIT License Implemented  
**Date**: December 4, 2025

---

## 📋 Current Licensing

### Project License: MIT

The Project-AI codebase is licensed under the **MIT License**, one of the most permissive open-source licenses available.

**File Location**: `LICENSE` (root directory)

**Key Points**:

- ✅ **Permissive**: Anyone can use, modify, and distribute the code
- ✅ **Commercial**: Commercial use is explicitly permitted
- ✅ **Attribution**: Requires keeping copyright notice
- ✅ **No Warranty**: Provided "as-is" with no warranty or liability
- ✅ **Sublicensing**: Allowed (derivative works can use different licenses)

---

## 📦 Dependency Licensing

All dependencies in `pyproject.toml` are compatible with MIT licensing:

### Core Dependencies

| Package | License | Compatible | Purpose |
|---------|---------|-----------|---------|
| PyQt6 | GPL v3 / Commercial | ✅ Yes | GUI Framework |
| scikit-learn | BSD 3-Clause | ✅ Yes | Machine Learning |
| numpy | BSD 3-Clause | ✅ Yes | Numerical Computing |
| pandas | BSD 3-Clause | ✅ Yes | Data Analysis |
| matplotlib | PSF | ✅ Yes | Data Visualization |
| cryptography | Apache 2.0 / BSD 3-Clause | ✅ Yes | Encryption |
| openai | Apache 2.0 | ✅ Yes | AI API Client |
| requests | Apache 2.0 | ✅ Yes | HTTP Client |
| geopy | MIT | ✅ Yes | Geolocation |
| python-dotenv | BSD 3-Clause | ✅ Yes | Environment Config |
| passlib | BSD | ✅ Yes | Password Hashing |
| bcrypt | Apache 2.0 | ✅ Yes | Bcrypt Hashing |
| PyPDF2 | BSD | ✅ Yes | PDF Processing |
| httpx | BSD | ✅ Yes | Async HTTP |

### Development Dependencies

| Package | License | Purpose |
|---------|---------|---------|
| ruff | MIT | Code Linting |
| pytest | MIT | Testing Framework |
| pytest-cov | MIT | Coverage Reporting |
| black | MIT | Code Formatter |
| flake8 | MIT | Style Guide |

All dependencies are compatible with MIT licensing

---

## 🔐 License Compliance

### Your Obligations (What You MUST Do)

1. **Include License Notice**
   - ✅ Include full MIT license text with distributions
   - ✅ Keep copyright notice in LICENSE file
   - ✅ Include license in source code archives

2. **Provide Attribution**
   - Recommended: Add notice to README.md or source files:

   ```python
   # Project-AI
   # Copyright (c) 2025 Project AI Team
   # Licensed under MIT License - See LICENSE file for details
   ```

3. **Document Dependencies**
   - ✅ Already configured in pyproject.toml
   - ✅ Maintain accurate version constraints

### Your Rights (What You CAN Do)

✅ Use commercially without royalties
✅ Distribute modified versions
✅ Include in proprietary software
✅ Change the license in derivative works
✅ Sublicense under different terms

### What You CANNOT Do

❌ Hold the authors liable
❌ Use trademark/name for endorsement
❌ Claim original authorship of others' work

---

## 🎯 Licensing Scenarios

### Scenario 1: Commercial Use

**Question**: Can I use Project-AI in a commercial product?

**Answer**: ✅ **Yes**. MIT allows commercial use without limitation or royalty.

**Requirements**:

- Include LICENSE file with product
- Retain copyright notice
- Cannot claim you wrote it

---

### Scenario 2: Closed-Source Distribution

**Question**: Can I use Project-AI in a closed-source/proprietary application?

**Answer**: ✅ **Yes**. MIT is compatible with closed-source distribution.

**Requirements**:

- Include LICENSE file with binaries/source
- Provide copy of original source upon request
- Acknowledge Project-AI in documentation

**Example**:

```text
This software includes Project-AI components
(c) 2025 Project AI Team, Licensed under MIT License.
For details, see: https://github.com/IAmSoThirsty/Project-AI
```

---

### Scenario 3: Derivative Works

**Question**: Can I modify Project-AI and release it under a different license?

**Answer**: ✅ **Yes**. MIT allows this (permissive).

**Requirements**:

- Include original MIT license text
- Acknowledge Project-AI as original source
- Your modifications can use different license

**Example**:

```python
# Based on Project-AI (c) 2025 Project AI Team (MIT License)
# Modified by: Your Company Name
# Licensed under: Apache 2.0
```

---

### Scenario 4: GPL Compatibility

**Question**: Can I combine Project-AI with GPL-licensed code?

**Answer**: ✅ **Technically yes, but proceed carefully**

**Note**:

- MIT → GPL: ✅ Permitted (subset of GPL permissions)
- GPL → MIT: ❌ NOT permitted (GPL requires copy-left)
- If combining: The combined work becomes GPL

---

## 📝 Adding License Headers (Optional)

For professional projects, add license headers to source files:

### Python Files

```python
# src/app/main.py
# Project-AI - Comprehensive AI Assistant
# Copyright (c) 2025 Project AI Team
# Licensed under the MIT License
# See LICENSE file in the root directory for full details
```

### Configuration Files

```yaml
# .github/workflows/deploy.yml
# Project-AI - CI/CD Configuration
# Copyright (c) 2025 Project AI Team
# Licensed under the MIT License
```

---

## 🚀 Using Your Licensed Code

### For End Users

Users can:

1. Download and use freely
2. Modify for their own use
3. Include in commercial projects
4. Redistribute with modifications

### For Contributors

Contributors:

1. Automatically agree to MIT licensing for contributions
2. Can create pull requests (contributions inherit MIT)
3. May be listed in contributors/authors

### For Forks

Forked repositories:

1. Must maintain MIT licensing
2. Must include original copyright
3. Can be modified freely
4. GitHub automatically inherits your license in forks

---

## 📊 License Compatibility Matrix

```text
Project-AI (MIT) is compatible with:
✅ Apache 2.0
✅ BSD (2-Clause, 3-Clause, 4-Clause)
✅ GPL v2 (code can be used, result becomes GPL)
✅ GPL v3 (code can be used, result becomes GPL)
✅ LGPL
✅ ISC
✅ MPL 2.0
✅ CDDL
✅ Other permissive licenses
❌ SSPL (Server Side Public License - may have restrictions)
```

---

## 🛡️ What the MIT License Protects

1. **Your Attribution**: Maintains copyright ownership
2. **Warranty Disclaimer**: Protects you from liability
3. **Freedom of Use**: Allows any use by others
4. **Patent Rights**: Doesn't grant patent licenses (but minimal patent risk with MIT)

---

## 📋 Recommended Actions

### Done ✅

1. ✅ Created LICENSE file
2. ✅ Declared in pyproject.toml
3. ✅ All dependencies compatible

### Recommended (Optional)

#### Documentation & Compliance

1. Add license headers to key source files
2. Add SECURITY.md with vulnerability disclosure
3. Add CODE_OF_CONDUCT.md for contributors
4. Add THIRD_PARTY_LICENSES.md for dependency details
5. Create license FAQ for users
6. Document contributor licensing agreements (CLA)
7. Document export control compliance (if applicable)

#### Supply Chain & Automation

1. Generate SBOM (Software Bill of Materials) for supply chain security
2. Set up license scanning in CI/CD (pip-licenses, FOSSA)
3. Set up automated dependency license audits
4. Add REUSE compliance badge (REUSE Software specification)

#### Distribution & Operations

1. Create license compliance checklist for distributions
2. Add license headers to all Python source files
3. Create internal license compliance training materials

### For Commercial Distribution

1. Include LICENSE file in binary releases
2. Add license notice to About dialog/splash screen
3. Provide source upon request if using binaries

---

## 🔗 References

- **MIT License Full Text**: See `LICENSE` file in repository
- **OpenSource.org**: [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)
- **GitHub License Detection**: [https://github.com/IAmSoThirsty/Project-AI](https://github.com/IAmSoThirsty/Project-AI)
- **Dependency License Checker**: `pip install pip-licenses && pip-licenses`

---

## 💡 Key Takeaway

**You're good to go!**

✅ Project-AI is properly licensed under MIT
✅ All dependencies are compatible
✅ Commercial use is permitted
✅ You're protected from liability

The MIT license is one of the most permissive and widely adopted in open-source software, making Project-AI accessible to the broadest audience while protecting your rights.

---

**Questions?** See:

- Official MIT License: [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)
- GitHub Licensing Guide: [https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- Choose a License: [https://choosealicense.com/](https://choosealicense.com/)

---

**Generated**: December 4, 2025  
**Status**: ✅ Licensing Complete
