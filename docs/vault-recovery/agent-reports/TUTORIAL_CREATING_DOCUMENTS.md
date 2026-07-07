# Tutorial: Creating Documents

**Step-by-Step Guide to Creating Quality Documentation** 📝

**Version:** 1.0.0  
**Last Updated:** 2026-04-20  
**Estimated Time:** 30 minutes  
**Skill Level:** Intermediate  
**Audience:** Documentation contributors

---

## Tutorial Overview

**What You'll Learn:**
- ✅ Choose the right template for your document
- ✅ Add proper metadata and frontmatter
- ✅ Structure content effectively
- ✅ Link to other documents
- ✅ Validate your documentation

**Prerequisites:**
- Completed [TUTORIAL_BASIC_NAVIGATION.md](TUTORIAL_BASIC_NAVIGATION.md)
- Templater plugin installed
- Read [METADATA_GUIDE.md](METADATA_GUIDE.md)

**By the End:**
You'll confidently create production-quality documentation!

---

## Step 1: Choose Your Template (5 minutes)

### Exercise 1.1: Understand Template Categories

**Templates Available:**

```
Module Documentation:
├─ module-doc-core-system.md    → Core Python modules
├─ module-doc-gui-component.md  → PyQt6 GUI components
└─ module-doc-agent.md          → AI agent systems

Architecture Documentation:
├─ architecture-doc-adr.md      → Architecture decisions
├─ architecture-doc-design-pattern.md → Design patterns
└─ architecture-doc-integration-api.md → API integrations

Guide Documentation:
├─ guide-quickstart-feature.md  → Quick start guides
├─ guide-developer-reference.md → Developer references
└─ guide-troubleshooting-production.md → Troubleshooting

Agent Documentation:
├─ agent-doc-task-report.md     → Agent completion reports
├─ agent-doc-security-audit.md  → Security audits
└─ agent-doc-convergence-summary.md → Phase summaries
```

**Decision Matrix:**

| You're Documenting... | Use Template... |
|----------------------|----------------|
| Python class/module | `module-doc-core-system` |
| GUI panel/window | `module-doc-gui-component` |
| AI agent behavior | `module-doc-agent` |
| Design decision | `architecture-doc-adr` |
| API endpoint | `architecture-doc-integration-api` |
| Feature tutorial | `guide-quickstart-feature` |
| API reference | `guide-developer-reference` |
| Troubleshooting steps | `guide-troubleshooting-production` |
| Your work summary | `agent-doc-task-report` |

**Your Task:**

- [ ] Review template categories
- [ ] Open `templates/TEMPLATE_LIBRARY.md` to see examples
- [ ] Choose a template for your first document

---

## Step 2: Create Your Document (10 minutes)

### Exercise 2.1: Use Templater to Insert Template

**Scenario:** You're documenting the `UserManager` class

**Template Choice:** `module-doc-core-system.md`

**Steps:**

1. **Create new note**
   ```
   Ctrl+N
   Name: USER_MANAGER_DOCUMENTATION.md
   ```

2. **Insert template**
   ```
   Ctrl+P → "Templater: Insert template"
   Choose: module-doc-core-system
   Press Enter
   ```

3. **Fill prompts** (Templater asks):
   ```
   Author: AGENT-048 (your ID)
   Component: core-system
   Priority: high
   ```

4. **Template generates** frontmatter automatically:

```yaml
---
type: code-documentation
area: [development, architecture]
component: core-system
status: draft
audience: [developer, architect]
priority: high
tags: [core-system, authentication, <cursor>]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
---

# USER_MANAGER_DOCUMENTATION

## Overview
<cursor>
```

**Your Task:**

- [ ] Create a new note named `TEST_DOCUMENT.md`
- [ ] Insert template: `module-doc-core-system`
- [ ] Fill in prompts when asked
- [ ] Observe auto-generated frontmatter

### Exercise 2.2: Complete Metadata

**Action:** Fill in frontmatter fields

**Required Fields:**

```yaml
✅ type: code-documentation     (auto-filled)
✅ area: [development]          (add your area)
✅ component: core-system       (auto-filled)
✅ status: draft               (start as draft)
✅ audience: [developer]       (who reads this?)
✅ tags: [list, of, tags]      (add 5-7 tags)
```

**Your Task:**

Edit frontmatter in your test document:

```yaml
---
type: code-documentation
area: [development, security]           ← Add areas
component: [core-system, authentication] ← Specify components
status: draft
audience: [developer, architect]         ← Add audiences
priority: high
tags: [core-system, authentication, user-management, bcrypt, security] ← Complete tags
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
---
```

**Validation:**

- [ ] All required fields present
- [ ] Tags match official taxonomy (check TAG_TAXONOMY.md)
- [ ] Audience is an array: `[developer]` not `developer`
- [ ] Dates in YYYY-MM-DD format

---

## Step 3: Structure Your Content (10 minutes)

### Exercise 3.1: Write the Overview

**Template Provides:**

```markdown
## Overview

<cursor>
```

**What to Write:**

1. **Purpose** (1-2 sentences)
   - What does this component do?
   - Why does it exist?

2. **Key Features** (bullet list)
   - Main capabilities
   - Notable characteristics

3. **Context** (1-2 sentences)
   - How it fits in the system
   - What it depends on

**Example:**

```markdown
## Overview

The `UserManager` class handles user authentication and authorization for Project-AI. It provides secure password hashing, user profile management, and session handling.

**Key Features:**
- Bcrypt password hashing for security
- JSON-based user persistence
- Session token generation (SHA-256)
- User CRUD operations

**Context:**
UserManager is a core system component used by the LeatherBook GUI for login/logout functionality. It integrates with the CommandOverride system for elevated permissions.
```

**Your Task:**

- [ ] Write a 1-2 sentence purpose statement
- [ ] List 3-5 key features
- [ ] Explain context (how it fits in system)

### Exercise 3.2: Document the API/Interface

**Template Provides:**

```markdown
## API Reference

### Class: [ClassName]

### Methods
```

**What to Write:**

For each public method:

```markdown
#### `method_name(param1, param2)`

**Purpose:** One-line description

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:**
- (type): Description

**Raises:**
- `ExceptionType`: When this happens

**Example:**
\`\`\`python
result = obj.method_name("value", 42)
\`\`\`
```

**Real Example:**

```markdown
#### `authenticate_user(username, password)`

**Purpose:** Verify user credentials and return user object if valid

**Parameters:**
- `username` (str): User's login name
- `password` (str): Plaintext password to verify

**Returns:**
- `dict | None`: User profile dict if authenticated, None if invalid

**Raises:**
- `FileNotFoundError`: If users.json doesn't exist
- `ValueError`: If username/password are empty

**Example:**
\`\`\`python
user = user_manager.authenticate_user("admin", "password123")
if user:
    print(f"Welcome {user['name']}")
else:
    print("Invalid credentials")
\`\`\`
```

**Your Task:**

- [ ] Document at least 2 methods
- [ ] Include purpose, parameters, returns
- [ ] Add code example for each

---

## Step 4: Add Links and References (3 minutes)

### Exercise 4.1: Link to Related Documents

**Why Link?**
- Readers discover related content
- Builds the knowledge graph
- Prevents orphaned documents

**How to Link:**

```markdown
## See Also

- [[AUTHENTICATION_GUIDE]] - User authentication overview
- [[SECURITY_MODEL]] - Security architecture
- [[source-docs/core/user_manager]] - Source code documentation
- [[DEPLOYMENT_GUIDE]] - Deployment configuration
```

**Link Syntax:**

```markdown
[[Document Name]]                    → Auto-links to document
[[Document Name|Display Text]]       → Custom display text
[[folder/subfolder/Document]]        → Specific path
```

**Your Task:**

- [ ] Add "See Also" section
- [ ] Link to 3-5 related documents
- [ ] Use descriptive link text

### Exercise 4.2: Reference External Resources

**For external links:**

```markdown
## References

- [Bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [Python Password Hashing](https://docs.python.org/3/library/hashlib.html)
- [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
```

**Your Task:**

- [ ] Add "References" section
- [ ] Include 2-3 external links
- [ ] Use descriptive link text

---

## Step 5: Validate and Publish (2 minutes)

### Exercise 5.1: Run Quality Checks

**Checklist:**

```markdown
Content Quality:
- [ ] Overview explains purpose clearly
- [ ] API methods documented with examples
- [ ] Links to related documents added
- [ ] Code examples are accurate
- [ ] No TODO comments left

Metadata Quality:
- [ ] All required fields present
- [ ] Tags match official taxonomy
- [ ] Status set appropriately
- [ ] Dates are current
- [ ] Author field populated

Formatting:
- [ ] Headers follow hierarchy (H2 > H3 > H4)
- [ ] Code blocks have language specified
- [ ] Lists formatted consistently
- [ ] Tables render properly (preview mode)
```

**Your Task:**

- [ ] Run through checklist
- [ ] Fix any issues found
- [ ] Switch to preview mode (`Ctrl+E`) to verify formatting

### Exercise 5.2: Update Status

**Status Progression:**

```
draft → review → approved → active
```

**When to Update:**

| Status | When to Use |
|--------|-------------|
| `draft` | Initial creation, work in progress |
| `review` | Ready for peer review |
| `approved` | Reviewed and accepted |
| `active` | Published, in production |

**Your Task:**

- [ ] If document is complete, change status to `review` or `active`
- [ ] Update `updated_date` to today
- [ ] Save (`Ctrl+S`)

---

## Advanced: Document Patterns

### Pattern 1: Quickstart Guide

**Structure:**

```markdown
# Quickstart: [Feature Name]

## Prerequisites
- Requirement 1
- Requirement 2

## Quick Steps (5 minutes)

1. Step 1
2. Step 2
3. Step 3

## Verification
How to verify it worked

## Troubleshooting
Common issues and fixes

## Next Steps
Links to detailed documentation
```

### Pattern 2: API Reference

**Structure:**

```markdown
# API Reference: [Module Name]

## Endpoints / Classes

### Endpoint 1 / Class 1
- Method signatures
- Parameters
- Returns
- Examples

## Error Codes
Possible errors and meanings

## Authentication
How to authenticate

## Rate Limits
Usage limits if applicable
```

### Pattern 3: Troubleshooting Guide

**Structure:**

```markdown
# Troubleshooting: [Problem Area]

## Common Issues

### Issue 1: [Problem Description]

**Symptoms:**
- What users see

**Cause:**
Why it happens

**Solution:**
Step-by-step fix

**Prevention:**
How to avoid in future
```

---

## Real-World Example: Full Document

**Let's create a complete document together!**

**Scenario:** Document the `ImageGenerator` class

**File:** `IMAGE_GENERATOR_DOCUMENTATION.md`

**Content:**

````markdown
---
type: code-documentation
area: [ai-systems, development]
component: [core-system, api]
status: active
audience: [developer]
priority: medium
tags: [image-generation, ai, openai, huggingface, dall-e, stable-diffusion]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
---

# Image Generator Documentation

## Overview

The `ImageGenerator` class provides dual-backend image generation using either Hugging Face Stable Diffusion or OpenAI DALL-E 3. It includes content filtering, style presets, and generation history tracking.

**Key Features:**
- Dual backend support (HuggingFace SD 2.1 + OpenAI DALL-E 3)
- 15-keyword content safety filter
- 10 style presets (photorealistic, anime, watercolor, etc.)
- Generation history with JSON persistence
- Async generation for UI responsiveness

**Context:**
Used by `ImageGenerationRightPanel` GUI component. Requires API keys for both backends. Generates images based on user prompts with safety constraints.

## Architecture

```
┌─────────────────────────────────────┐
│  ImageGenerator                      │
├─────────────────────────────────────┤
│ + generate(prompt, style, size)     │
│ + check_content_filter(prompt)      │
│ + generate_with_huggingface()       │
│ + generate_with_openai()            │
│ + get_generation_history()          │
└─────────────────────────────────────┘
         ↓                    ↓
    ┌────────┐          ┌──────────┐
    │ HF API │          │ OpenAI   │
    │ SD 2.1 │          │ DALL-E 3 │
    └────────┘          └──────────┘
```

## API Reference

### Class: `ImageGenerator`

#### `generate(prompt, style='photorealistic', size='1024x1024', backend='huggingface')`

**Purpose:** Generate image from text prompt with specified style and size

**Parameters:**
- `prompt` (str): Text description of desired image
- `style` (str): Style preset (default: 'photorealistic')
- `size` (str): Image dimensions (default: '1024x1024')
- `backend` (str): 'huggingface' or 'openai' (default: 'huggingface')

**Returns:**
- `tuple[str|None, str]`: (image_path, status_message)
  - Success: ("path/to/image.png", "Generated successfully")
  - Failure: (None, "Error: reason")

**Raises:**
- `ValueError`: If style or size invalid
- `EnvironmentError`: If API keys missing

**Example:**
\`\`\`python
generator = ImageGenerator()
image_path, message = generator.generate(
    prompt="A sunset over mountains",
    style="photorealistic",
    size="1024x1024",
    backend="huggingface"
)

if image_path:
    print(f"Image saved: {image_path}")
else:
    print(f"Error: {message}")
\`\`\`

#### `check_content_filter(prompt)`

**Purpose:** Validate prompt against blocked keywords and safety rules

**Parameters:**
- `prompt` (str): Text prompt to validate

**Returns:**
- `tuple[bool, str]`: (is_safe, reason)
  - Safe: (True, "")
  - Unsafe: (False, "Content filter: [reason]")

**Example:**
\`\`\`python
is_safe, reason = generator.check_content_filter(
    "Generate image of a sunset"
)
if not is_safe:
    print(f"Prompt rejected: {reason}")
\`\`\`

## Configuration

**Environment Variables:**

```bash
HUGGINGFACE_API_KEY=hf_...
OPENAI_API_KEY=sk-...
```

**Style Presets:**

- `photorealistic` - Photorealistic rendering
- `digital_art` - Digital art style
- `oil_painting` - Oil painting texture
- `watercolor` - Watercolor effect
- `anime` - Anime/manga style
- `sketch` - Pencil sketch
- `abstract` - Abstract art
- `cyberpunk` - Cyberpunk aesthetic
- `fantasy` - Fantasy art
- `minimalist` - Minimalist design

**Supported Sizes:**

- `1024x1024` (square)
- `1792x1024` (landscape)
- `1024x1792` (portrait)

## Usage Examples

**Basic Generation:**

\`\`\`python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()
image_path, msg = generator.generate(
    "A cat wearing a top hat",
    style="photorealistic"
)
\`\`\`

**With Style and Backend:**

\`\`\`python
image_path, msg = generator.generate(
    prompt="Futuristic city at night",
    style="cyberpunk",
    size="1792x1024",
    backend="openai"
)
\`\`\`

**Content Filtering:**

\`\`\`python
is_safe, reason = generator.check_content_filter(prompt)
if not is_safe:
    return None, f"Rejected: {reason}"
```

## Troubleshooting

### Issue: "API key not found"

**Cause:** Missing environment variables

**Solution:**
1. Create `.env` file in project root
2. Add: `HUGGINGFACE_API_KEY=your_key`
3. Add: `OPENAI_API_KEY=your_key`
4. Restart application

### Issue: "Generation takes too long"

**Cause:** Synchronous generation blocking UI

**Solution:**
Use `ImageGenerationWorker` (QThread) for async generation:

\`\`\`python
worker = ImageGenerationWorker(prompt, style, size, backend)
worker.image_generated.connect(self.on_image_ready)
worker.start()
\`\`\`

## See Also

- [[IMAGE_GENERATION_GUI]] - GUI component documentation
- [[OPENAI_INTEGRATION]] - OpenAI API integration
- [[source-docs/core/image_generator]] - Source code
- [[DEPLOYMENT_GUIDE]] - API key setup

## References

- [Stable Diffusion 2.1](https://huggingface.co/stabilityai/stable-diffusion-2-1)
- [OpenAI DALL-E 3](https://platform.openai.com/docs/guides/images)
- [Hugging Face API](https://huggingface.co/docs/api-inference/index)

---

**Last Updated:** 2026-04-20  
**Maintainer:** AGENT-048  
**Status:** Active
````

**Analysis:**

✅ Complete frontmatter with all required fields  
✅ Clear overview with purpose, features, context  
✅ Architecture diagram for visual understanding  
✅ Detailed API reference with examples  
✅ Configuration section for setup  
✅ Multiple usage examples  
✅ Troubleshooting for common issues  
✅ Links to related documentation  
✅ External references

---

## Summary: Document Creation Checklist

**Before You Start:**
- [ ] Choose appropriate template
- [ ] Understand what you're documenting
- [ ] Review similar existing documents

**During Creation:**
- [ ] Insert template via Templater
- [ ] Complete all frontmatter fields
- [ ] Write clear overview (purpose + features + context)
- [ ] Document API/interface with examples
- [ ] Add links to related documents
- [ ] Include configuration instructions
- [ ] Provide troubleshooting guidance

**Before Publishing:**
- [ ] Run quality checklist
- [ ] Validate metadata against schema
- [ ] Test all code examples
- [ ] Preview in reading mode
- [ ] Update status appropriately
- [ ] Save and commit

---

## Next Steps

**You've completed Creating Documents!**

1. ✅ **Practice:** Create 3 documents using different templates
2. 📖 **Next Tutorial:** [TUTORIAL_ADVANCED_QUERIES.md](TUTORIAL_ADVANCED_QUERIES.md)
3. 🔍 **Reference:** [METADATA_GUIDE.md](METADATA_GUIDE.md)
4. 🎯 **Contribute:** Add documentation for a feature you understand

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [developer, contributor]
priority: high
tags: [tutorial, documentation, templates, metadata, intermediate]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
estimated_time: 30 minutes
difficulty: intermediate
word_count: 2600
dependencies:
  - METADATA_GUIDE.md
  - TEMPLATE_GUIDE.md
  - TUTORIAL_BASIC_NAVIGATION.md
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

