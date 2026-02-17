# Google Antigravity IDE Integration

This directory contains configuration files and custom agents for integrating Google Antigravity IDE with Project-AI.

## 📁 Directory Structure

```
.antigravity/
├── config.json              # Main Antigravity configuration
├── security.yaml            # Security policies and restrictions
├── agents/                  # Custom AI agents
│   └── project_ai_agent.py  # Main Project-AI aware agent
├── workflows/               # Workflow definitions
│   ├── feature-development.yaml
│   └── security-fix.yaml
├── scripts/                 # Helper scripts
│   └── setup_antigravity.py # Setup and validation script
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Verify Integration

Run the setup script to check if everything is configured correctly:

```bash
python .antigravity/scripts/setup_antigravity.py
```

This will check:

- ✅ Prerequisites (Python version, dependencies)
- ✅ Configuration validity
- ✅ Custom agent files
- ✅ Workflow definitions

### 2. Install Antigravity IDE

Download and install Google Antigravity IDE:

- Visit: https://antigravity.google.com/download
- Or use package manager:

  ```bash

  # macOS

  brew install --cask google-antigravity

  # Windows

  winget install Google.Antigravity

  # Linux

  sudo snap install google-antigravity
  ```

### 3. Open Project in Antigravity

1. Launch Antigravity IDE
2. File > Open Folder
3. Select the Project-AI directory
4. Antigravity will automatically detect the configuration

## 🤖 Custom Agents

### ProjectAIAgent

The main custom agent that understands Project-AI's architecture:

**Features:**

- Knows about Four Laws ethical framework
- Integrates with Triumvirate review system
- Understands personhood-critical files
- Validates against security policies
- Coordinates with Temporal.io workflows

**Usage:**
Antigravity automatically loads this agent. It will:

- Analyze tasks for ethical implications
- Request Triumvirate review when needed
- Validate actions against Four Laws
- Generate context-aware recommendations

## 📊 Workflows

### Feature Development

Standard workflow for adding new features:

**Steps:**

1. Requirements Analysis
2. Ethical Review Check (if needed)
3. Triumvirate Review (if triggered)
4. Implementation
5. Unit Testing (80% coverage required)
6. Security Scan
7. Documentation
8. Code Quality Check
9. Temporal Workflow Validation (if applicable)
10. Integration Test

**Triggers:**

- Keywords: "add feature", "new feature", "implement"
- File patterns: `src/**/*.py`

### Security Fix

Expedited workflow for security vulnerabilities:

**Steps:**

1. Vulnerability Assessment
2. Immediate Mitigation (for high severity)
3. Triumvirate Emergency Review (for critical)
4. Fix Implementation
5. Security Testing
6. Regression Testing
7. Security Documentation
8. Verification Scan

**Triggers:**

- Keywords: "security", "vulnerability", "CVE"
- Security scan alerts

## ⚙️ Configuration

### config.json

Main configuration file with:

- Agent settings (coding, testing, security, ethical_review)
- Workflow definitions (pre_commit, pre_push, daily)
- Integration settings (temporal, openai, github)
- AI system mappings (four_laws, triumvirate, ai_persona)
- File patterns (personhood_critical, security_critical)

### security.yaml

Security policies including:

- Required approval operations
- Restricted paths
- Auto-approved operations
- Security scanning configuration
- Ethical review triggers
- Code execution restrictions

## 🔒 Security Features

### Restricted Paths

These paths require special approval:

- `data/ai_persona/` - Personhood-critical AI identity
- `.env` - Secrets and API keys
- `data/command_override_config.json` - Security config
- `data/black_vault_secure/` - Denied content
- `data/memory/` - AI memory (approval required)

### Auto-Approved Operations

These are safe and don't require approval:

- Adding tests
- Adding documentation
- Adding docstrings
- Adding type hints
- Fixing typos
- Formatting code

### Ethical Review Triggers

Automatically triggers Triumvirate review for:

- AI persona changes
- Four Laws modifications
- Memory system changes
- Learning system changes
- User data access
- Encryption changes

## 🔗 Integration Points

### Temporal.io Workflows

Antigravity integrates with existing Temporal workflows:

- **Triumvirate Review**: `temporal.workflows.triumvirate_workflow`
- **Security Scan**: `temporal.workflows.security_agent_workflows`
- **Learning Workflow**: `examples.temporal.learning_workflow_example`

### Four Laws Validation

All actions are validated against the immutable Four Laws:
```python
from src.app.core.ai_systems import FourLaws

four_laws = FourLaws()
is_allowed, reason = four_laws.validate_action(action, context)
```

### AI Persona System

Antigravity respects the AI Persona system:

- Tracks interactions
- Respects mood states
- Logs to memory system
- Maintains personality consistency

## 📚 Usage Examples

### Example 1: Adding a New Feature

**User input in Antigravity:**
```
"Add a new timezone detection feature to the location tracker"
```

**Antigravity workflow:**

1. ✅ Requirements analyzed
2. ⚠️ Ethical review triggered (user data access)
3. 🔄 Triumvirate review requested
4. ✅ Approved by Galahad, Cerberus, Codex
5. 📝 Code generated in `src/app/core/location_tracker.py`
6. ✅ Tests written in `tests/test_location_tracker.py`
7. 🔒 Security scan passed
8. 📚 Documentation updated
9. ✅ Ready for review!

### Example 2: Fixing a Security Issue

**User input:**
```
"Fix SQL injection in user_manager.py line 234"
```

**Antigravity workflow:**

1. 🔒 Vulnerability assessed: HIGH severity
2. ⚡ Immediate mitigation applied
3. 🔄 Emergency Triumvirate review
4. ✅ Fix implemented with parameterized queries
5. ✅ Security tests added
6. ✅ Regression tests passed
7. 📋 Security advisory created
8. ✅ Verified - vulnerability resolved!

## 🎯 Best Practices

### When to Use Antigravity

✅ **Good for:**

- Adding new features
- Fixing bugs
- Writing tests
- Updating documentation
- Security fixes
- Code refactoring

❌ **Not recommended for:**

- First-time codebase exploration
- Learning Project-AI architecture
- Debugging complex issues (use traditional IDE first)
- Personhood-critical changes (requires deep understanding)

### Working with Ethical Reviews

When Antigravity triggers an ethical review:

1. **Review the analysis** - Understand why it was triggered
2. **Provide context** - Explain the purpose and impact
3. **Wait for approval** - Don't bypass the Triumvirate
4. **Document the decision** - Add to commit message

### Security Considerations

- Always review security scan results
- Don't auto-approve security fixes without understanding them
- Verify that fixes don't introduce new vulnerabilities
- Test exploit scenarios before and after fixes

## 🐛 Troubleshooting

### "Configuration not found"

**Solution:** Run setup script to verify:
```bash
python .antigravity/scripts/setup_antigravity.py
```

### "Temporal.io connection failed"

**Solution:** Start Temporal server:
```bash
cd temporal-server && docker-compose up -d
```

### "Four Laws validation unavailable"

**Solution:** Ensure you're in the Project-AI root and dependencies are installed:
```bash
pip install -e .
```

### "Triumvirate review timeout"

**Solution:** Check that Temporal workers are running:
```bash
python -m src.app.temporal.worker
```

## 📞 Support

For issues specific to:

- **Antigravity IDE**: https://antigravity.google.com/support
- **Project-AI integration**: Open an issue on GitHub
- **Temporal.io**: https://docs.temporal.io/

## 🔄 Updates

To update the Antigravity configuration:

1. Edit `.antigravity/config.json` or `.antigravity/security.yaml`
2. Run validation: `python .antigravity/scripts/setup_antigravity.py`
3. Restart Antigravity IDE to load new configuration

## 📝 Contributing

When modifying Antigravity integration:

1. Test configuration changes locally
2. Verify custom agents still work
3. Update this README if needed
4. Run full validation before committing

---

**Integration Status:** ✅ Ready for use
**Last Updated:** January 28, 2026
**Maintainer:** @IAmSoThirsty
