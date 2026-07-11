# Core Module Documentation Index

**Directory:** `T:\Project-AI-vault\source-docs\core\`
**Purpose:** Comprehensive API reference and technical documentation for all 11 core Python modules in `src/app/core/`
**Status:** Production (1/11 modules complete, 10 in progress)
**Last Updated:** 2026-04-20
**Maintained By:** AGENT-032 (Source Code Documentation Specialist)

---

## Quick Navigation

### ✅ Complete Modules (1/11)

| Module | Document | Status | Word Count | API Coverage |
|--------|----------|--------|------------|--------------|
| **ai_systems.py** | [ai_systems.md](./ai_systems.md) | ✅ Complete | 9,100+ | 100% (6 classes, 50+ methods) |

### 🚧 In Progress Modules (10/11)

| Module | Document | Status | Est. Completion |
|--------|----------|--------|-----------------|
| **user_manager.py** | user_manager.md | 🔄 Pending | Next batch |
| **command_override.py** | command_override.md | 🔄 Pending | Next batch |
| **learning_paths.py** | learning_paths.md | 🔄 Pending | Next batch |
| **data_analysis.py** | data_analysis.md | 🔄 Pending | Next batch |
| **security_resources.py** | security_resources.md | 🔄 Pending | Next batch |
| **location_tracker.py** | location_tracker.md | 🔄 Pending | Next batch |
| **emergency_alert.py** | emergency_alert.md | 🔄 Pending | Next batch |
| **intelligence_engine.py** | intelligence_engine.md | 🔄 Pending | Next batch |
| **intent_detection.py** | intent_detection.md | 🔄 Pending | Next batch |
| **image_generator.py** | image_generator.md | 🔄 Pending | Next batch |

---

## Document Structure (Per Module)

Each module documentation follows this comprehensive template:

### 1. **YAML Frontmatter (Metadata Schema)**
- Complete metadata following `METADATA_SCHEMA.md` v2.0.0
- Universal fields: title, id, type, version, dates, status, author
- Domain-specific: category, tags, technologies, summary
- Relationships: dependencies, dependents, related_docs
- Extended: complexity, test_coverage, security_classification

### 2. **Overview Section**
- Purpose and responsibility
- Scope and boundaries
- Design philosophy
- Module location and import patterns

### 3. **Architecture Section**
- Design patterns used
- Data persistence architecture
- Dependency graph (ASCII diagrams)
- Integration points

### 4. **API Reference**
- All classes with complete docstrings
- All public methods with:
  - Signatures with type hints
  - Parameter descriptions
  - Return value specifications
  - Raises documentation
- 3+ runnable code examples per method
- Real-world usage patterns

### 5. **Data Flow Diagrams**
- ASCII art diagrams for complex flows
- State machine diagrams
- Request/response flows
- Integration sequences

### 6. **Integration Points**
- What depends on this module
- What this module depends on
- Integration patterns with code examples
- GUI integration points

### 7. **Testing Approach**
- Test file location
- Test class structure
- Running tests (commands)
- Example test patterns
- Coverage expectations

### 8. **Troubleshooting**
- 5+ common issues with solutions
- Performance tuning tips
- Debugging strategies
- Known limitations

### 9. **Security Considerations**
- Authentication/authorization details
- Encryption patterns
- Audit trails
- Threat model

### 10. **Additional Sections**
- Performance characteristics
- Scalability limits
- Changelog
- FAQ
- Contributing guidelines
- Appendices

---

## Module Summaries

### ✅ ai_systems.py (COMPLETE)

**Purpose:** Six core AI subsystems: FourLaws (ethics), AIPersona (personality), MemoryExpansionSystem (knowledge), LearningRequestManager (learning), PluginManager (extensions), CommandOverrideSystem (overrides)

**Key Features:**
- Asimov's Laws enforcement with Planetary Defense Core integration
- 8-dimensional personality tracking with mood history
- 6-category knowledge base with full-text search
- Human-in-the-loop learning with Black Vault content fingerprinting
- Plugin lifecycle management
- Privileged override system with bcrypt authentication

**Documentation Highlights:**
- Complete API reference for 6 classes
- 50+ method signatures with examples
- 3 ASCII data flow diagrams
- 8 troubleshooting scenarios
- 9 FAQ entries
- 4 appendices with reference tables

**Word Count:** ~9,100 words
**API Coverage:** 100%
**Example Count:** 40+ runnable code examples

---

### 🔄 user_manager.py (PENDING)

**Purpose:** User authentication and profile management with secure password hashing

**Key Features:**
- Bcrypt/PBKDF2 password hashing with auto-migration
- Account lockout protection (5 attempts, 15min lockout)
- Constant-time authentication (prevents timing attacks)
- Password strength validation
- Fernet encryption for sensitive data
- User role management

**Planned Documentation:**
- Complete API reference for `UserManager` class
- Authentication flow diagrams
- Password migration patterns
- Security best practices
- Integration with `gui/leather_book_interface.py`

**Estimated Word Count:** ~2,500 words

---

### 🔄 command_override.py (PENDING)

**Purpose:** Extended command override system with 10+ safety protocols

**Key Features:**
- 10 toggleable safety protocols
- Bcrypt/PBKDF2 password hashing with SHA-256 migration
- Account lockout with exponential backoff
- Comprehensive audit logging
- Emergency unlock mechanism
- Master override (disables all protocols)

**Planned Documentation:**
- Full protocol reference table
- Authentication flow diagrams
- Audit log format specification
- Security considerations
- Troubleshooting lockout scenarios

**Estimated Word Count:** ~3,000 words

---

### 🔄 learning_paths.py (PENDING)

**Purpose:** AI-powered learning path generation via OpenAI/Perplexity

**Key Features:**
- OpenAI GPT-3.5/GPT-4 integration
- Perplexity AI provider support
- Structured learning path generation
- Progress tracking
- User-specific path storage

**Planned Documentation:**
- AI orchestrator integration patterns
- Prompt engineering best practices
- Path storage format
- Error handling strategies

**Estimated Word Count:** ~1,500 words

---

### 🔄 data_analysis.py (PENDING)

**Purpose:** Tabular data analysis and visualization with pandas/scikit-learn

**Key Features:**
- CSV/XLSX/JSON file loading
- Summary statistics generation
- 4 visualization types (scatter, histogram, boxplot, correlation)
- K-means clustering with PCA
- Qt5/Qt6 canvas support

**Planned Documentation:**
- Visualization gallery with examples
- Clustering workflow
- Qt integration patterns
- Performance optimization tips

**Estimated Word Count:** ~2,000 words

---

### 🔄 security_resources.py (PENDING)

**Purpose:** Security repository management and GitHub API integration

**Key Features:**
- Curated security resource catalog
- GitHub API repository details fetching
- Category filtering
- User favorites system
- Rate limiting considerations

**Planned Documentation:**
- Resource catalog reference
- GitHub API integration patterns
- Favorite management workflows
- API rate limiting strategies

**Estimated Word Count:** ~1,500 words

---

### 🔄 location_tracker.py (PENDING)

**Purpose:** Location tracking with IP geolocation and GPS support

**Key Features:**
- IP-based geolocation (ipapi.co)
- GPS coordinate reverse geocoding (Nominatim)
- Fernet encryption for location history
- User privacy controls
- Configurable tracking modes

**Planned Documentation:**
- Location data encryption flow
- API integration patterns
- Privacy considerations
- GDPR compliance notes

**Estimated Word Count:** ~2,000 words

---

### 🔄 emergency_alert.py (PENDING)

**Purpose:** Emergency contact system with email alerts

**Key Features:**
- SMTP email integration
- Emergency contact registry
- Location-aware alerts
- Alert history logging
- Gmail/custom SMTP support

**Planned Documentation:**
- SMTP configuration guide
- Alert template customization
- Contact management workflow
- Email delivery troubleshooting

**Estimated Word Count:** ~1,800 words

---

### 🔄 intelligence_engine.py (PENDING)

**Purpose:** Unified intelligence engine with data analysis, intent detection, and learning paths

**Key Features:**
- Intelligence router for query handling
- Function registry integration
- Knowledge base queries
- Conversation search
- AGI Identity System integration (Bonding, Triumvirate, Memory)

**Planned Documentation:**
- Router architecture diagrams
- AGI Identity System integration
- Function registry patterns
- Comprehensive subsystem reference

**Estimated Word Count:** ~4,000 words (largest module)

---

### 🔄 intent_detection.py (PENDING)

**Purpose:** ML-based intent classification using scikit-learn

**Key Features:**
- TF-IDF vectorization
- SGD classifier (modified Huber loss)
- Model persistence (joblib)
- Training workflow
- Fallback to "general" intent

**Planned Documentation:**
- Training data format
- Model lifecycle management
- Intent classification examples
- Accuracy improvement strategies

**Estimated Word Count:** ~1,200 words

---

### 🔄 image_generator.py (PENDING)

**Purpose:** AI image generation with content filtering and style presets

**Key Features:**
- Dual backend (Hugging Face Stable Diffusion, OpenAI DALL-E 3)
- 15 blocked keyword content filter
- 10 style presets
- Generation history tracking
- Retry logic with exponential backoff
- Path traversal protection

**Planned Documentation:**
- Content filtering architecture
- Style preset reference
- Backend comparison table
- Retry logic flow diagram
- Security considerations

**Estimated Word Count:** ~3,000 words

---

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                  CORE MODULE DEPENDENCY GRAPH                    │
└─────────────────────────────────────────────────────────────────┘

[EXTERNAL DEPENDENCIES]
    │
    ├─ OpenAI API ──────────────┬───────────────────┐
    │                           │                   │
    │                           ▼                   ▼
    │                   learning_paths.py   image_generator.py
    │                           │                   │
    │                           └───────┬───────────┘
    │                                   │
    ├─ GitHub API ──────────► security_resources.py
    │
    ├─ ipapi.co ────────────► location_tracker.py
    │
    ├─ Nominatim ───────────► location_tracker.py
    │
    ├─ SMTP ────────────────► emergency_alert.py
    │
    ├─ passlib/bcrypt ──────┬───────────────────┐
    │                       │                   │
    │                       ▼                   ▼
    │                  user_manager.py   command_override.py
    │
    └─ scikit-learn ────────┬───────────────────┐
                            │                   │
                            ▼                   ▼
                    data_analysis.py   intent_detection.py


[CORE SYSTEMS]
    │
    ├─ ai_systems.py ─────────────┬─────────────────────┐
    │   (6 subsystems)             │                     │
    │                              ▼                     ▼
    │                      user_manager.py      command_override.py
    │                              │                     │
    │                              └──────────┬──────────┘
    │                                         │
    └────────────────────────────────────────┼──────────┐
                                              │          │
                                              ▼          ▼
                                    intelligence_engine.py
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
            data_analysis.py        intent_detection.py      learning_paths.py
                    │                         │                         │
                    │                         └─────────────┬───────────┘
                    │                                       │
                    └───────────────────────────────────────┤
                                                            │
                                                            ▼
                                                  [GUI Integration]
                                                            │
                                                ┌───────────┼───────────┐
                                                │           │           │
                                                ▼           ▼           ▼
                                    leather_book_interface.py
                                    persona_panel.py
                                    image_generation.py


[UTILITY MODULES]
    │
    ├─ location_tracker.py ────► emergency_alert.py
    │                                     │
    │                                     └─────► [Email Alerts]
    │
    └─ security_resources.py ──────────► [Knowledge Integration]
```

**Dependency Layers:**
1. **External APIs:** OpenAI, GitHub, IP geolocation, SMTP
2. **Core Systems:** ai_systems.py, user_manager.py, command_override.py
3. **Intelligence Layer:** intelligence_engine.py (orchestrates all subsystems)
4. **Specialized Systems:** data_analysis, intent_detection, learning_paths, image_generator
5. **Utility Systems:** location_tracker, emergency_alert, security_resources
6. **GUI Layer:** PyQt6 interfaces consuming all core systems

---

## Implementation Status

### Phase 1: Foundation (COMPLETE)
- ✅ Created `source-docs/core/` directory structure
- ✅ Reviewed all 11 source modules
- ✅ Established documentation template
- ✅ Created comprehensive metadata schema
- ✅ Documented first module (ai_systems.py) to full specification

### Phase 2: Core Systems (NEXT)
- 🔄 user_manager.py documentation
- 🔄 command_override.py documentation
- 🔄 intelligence_engine.py documentation

### Phase 3: Specialized Systems
- 🔄 data_analysis.py documentation
- 🔄 intent_detection.py documentation
- 🔄 learning_paths.py documentation
- 🔄 image_generator.py documentation

### Phase 4: Utility Systems
- 🔄 location_tracker.py documentation
- 🔄 emergency_alert.py documentation
- 🔄 security_resources.py documentation

### Phase 5: Integration & Finalization
- ⏳ Create module dependency graph (visual)
- ⏳ Generate comprehensive summary report
- ⏳ Cross-reference validation
- ⏳ Metadata consistency check
- ⏳ Final review and quality gates

---

## Quality Gates

Each module documentation must meet these criteria before marking as complete:

### Content Requirements
- ✅ **Metadata:** Complete YAML frontmatter with all required fields
- ✅ **Word Count:** Minimum 1,000 words (average 2,000-3,000)
- ✅ **API Coverage:** 100% of public methods documented
- ✅ **Examples:** 3+ runnable code examples per major method
- ✅ **Diagrams:** ASCII art for complex flows
- ✅ **Troubleshooting:** Minimum 5 common issues with solutions
- ✅ **Security:** Dedicated security considerations section
- ✅ **Testing:** Test approach with example patterns

### Technical Requirements
- ✅ **Accuracy:** All code examples tested and verified
- ✅ **Completeness:** No TODOs or placeholders
- ✅ **Consistency:** Follows AGENT_IMPLEMENTATION_STANDARD.md
- ✅ **Cross-References:** Links to related documentation
- ✅ **Metadata:** Valid according to METADATA_SCHEMA.md

### Review Checklist
- [ ] Metadata validates against schema
- [ ] All public APIs documented
- [ ] Code examples are runnable
- [ ] Diagrams are clear and accurate
- [ ] Troubleshooting covers common issues
- [ ] Security considerations comprehensive
- [ ] No spelling/grammar errors
- [ ] Cross-references valid

---

## Usage Examples

### Finding Documentation

**By Module Name:**
```bash
# Navigate to core documentation
cd T:\Project-AI-vault\source-docs\core

# View ai_systems documentation
cat ai_systems.md
```

**By Feature:**
- **User Authentication:** See `user_manager.md`
- **Ethical Validation:** See `ai_systems.md` → FourLaws section
- **AI Personality:** See `ai_systems.md` → AIPersona section
- **Learning Paths:** See `learning_paths.md`
- **Image Generation:** See `image_generator.md`
- **Data Analysis:** See `data_analysis.md`

**By Integration Point:**
- **GUI Integration:** See each module's "Integration Points" section
- **Testing Patterns:** See each module's "Testing Approach" section
- **Security:** See each module's "Security Considerations" section

### Searching Across Documentation

```powershell
# Search for specific API method
Get-ChildItem -Path "T:\Project-AI-vault\source-docs\core\" -Filter "*.md" | Select-String -Pattern "validate_action"

# Search for security topics
Get-ChildItem -Path "T:\Project-AI-vault\source-docs\core\" -Filter "*.md" | Select-String -Pattern "security"

# Search for code examples
Get-ChildItem -Path "T:\Project-AI-vault\source-docs\core\" -Filter "*.md" | Select-String -Pattern "```python"
```

---

## Contributing to Documentation

### Adding New Module Documentation

1. **Create File:** `T:\Project-AI-vault\source-docs\core\{module_name}.md`
2. **Add Metadata:** Follow YAML frontmatter template in METADATA_SCHEMA.md
3. **Follow Template:** Use ai_systems.md as reference template
4. **Quality Check:** Verify against quality gates
5. **Update Index:** Add entry to this index file

### Updating Existing Documentation

1. **Version Bump:** Update `version` field in YAML frontmatter
2. **Update `updated_date`:** Set to current date
3. **Add Changelog Entry:** Document changes in Changelog section
4. **Cross-Reference Check:** Verify links still valid
5. **Test Examples:** Re-run all code examples

### Review Process

1. Self-review against quality gates
2. Peer review by another developer
3. Technical accuracy review by module owner
4. Final approval by Architecture Team

---

## Roadmap

### Immediate (Next 2 Days)
- Complete user_manager.py documentation
- Complete command_override.py documentation
- Complete intelligence_engine.py documentation

### Short-Term (Next Week)
- Complete all specialized system docs (data_analysis, intent_detection, learning_paths, image_generator)
- Complete all utility system docs (location_tracker, emergency_alert, security_resources)

### Medium-Term (Next 2 Weeks)
- Create visual dependency graph
- Generate PDF exports of all documentation
- Create quick reference cards (1-page summaries)
- Add interactive API explorer

### Long-Term (Next Month)
- Integrate documentation into IDE (VS Code extension)
- Create video tutorials for complex modules
- Build searchable documentation website
- Add automated documentation testing

---

## Metrics

### Current Progress
- **Modules Documented:** 1/11 (9%)
- **Total Word Count:** 9,100+ words
- **API Methods Documented:** 50+ methods (ai_systems.py)
- **Code Examples:** 40+ examples
- **Diagrams:** 3 ASCII diagrams

### Target Metrics
- **Total Word Count:** 25,000+ words (all modules)
- **API Methods Documented:** 150+ methods
- **Code Examples:** 120+ examples
- **Diagrams:** 20+ diagrams
- **Estimated Completion:** 2-3 days (continuous work)

---

## Contact

**Documentation Maintainer:** AGENT-032 (Source Code Documentation Specialist)
**Architecture Team:** architecture@project-ai.dev
**Questions/Feedback:** Create issue in T:\Project-AI-vault\issues\
**Last Review:** 2026-04-20
**Next Review:** 2026-04-27 (Weekly)

---

**Document ID:** SOURCE-DOCS-INDEX
**Version:** 1.0.0
**Status:** Living Document (Updated Continuously)
**License:** Internal Use Only (Project-AI Development Team)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
