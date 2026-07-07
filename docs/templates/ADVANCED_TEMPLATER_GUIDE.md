# Advanced Templater Guide for Project-AI Vault

**Version:** 2.0.0  
**Last Updated:** 2026-04-20  
**Author:** Project-AI Documentation Team  
**Audience:** Advanced template developers and power users

---

## Table of Contents

1. [Introduction](#introduction)
2. [Advanced Templater Syntax](#advanced-templater-syntax)
3. [User Script Development](#user-script-development)
4. [Dynamic Content Generation](#dynamic-content-generation)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Integration Patterns](#integration-patterns)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Examples](#advanced-examples)

---

## Introduction

This guide covers advanced Templater usage for the Project-AI vault, including user script development, dynamic content generation, and optimization techniques.

### Prerequisites

- Obsidian with Templater plugin installed (v1.16.0+)
- Basic understanding of JavaScript
- Familiarity with Obsidian's markdown format
- Knowledge of Project-AI metadata schema

### What You'll Learn

- How to create custom Templater user scripts
- Advanced template syntax and patterns
- Integration with Dataview and other plugins
- Performance optimization for large vaults
- Error handling and debugging techniques

---

## Advanced Templater Syntax

### 1. Template Variables

**Basic Syntax:**
```javascript
<% tp.file.creation_date("YYYY-MM-DD") %>
<% tp.file.title %>
<% tp.frontmatter.status %>
```

**Dynamic Prompts:**
```javascript
<%* const title = tp.system.prompt("Enter title", "Default"); %>
<%* const category = tp.system.suggester(
    ["Module Doc", "Agent Doc", "Architecture", "Guide"],
    ["module-doc", "agent-doc", "architecture-doc", "guide"]
); %>
```

**Conditional Rendering:**
```javascript
<%* if (tp.frontmatter.category === "module-doc") { %>
## Module-Specific Section
<%* } else { %>
## General Section
<%* } %>
```

### 2. Loops and Iteration

**Basic Loop:**
```javascript
<%* for (let i = 1; i <= 5; i++) { %>
- Item <%= i %>
<%* } %>
```

**Dynamic Loop with Prompts:**
```javascript
<%* const numItems = parseInt(tp.system.prompt("How many items?", "3")); %>
<%* for (let i = 1; i <= numItems; i++) { %>
### Item <%* tR += i %>: <% tp.system.prompt(`Item ${i} name`, "") %>

**Description:** <% tp.system.prompt(`Item ${i} description`, "") %>

---
<%* } %>
```

**Array Iteration:**
```javascript
<%* const tags = tp.frontmatter.tags || []; %>
<%* tags.forEach(tag => { %>
- #<%= tag %>
<%* }); %>
```

### 3. User Script Integration

**Loading User Scripts:**
```javascript
<%* const utils = tp.user["project-ai-utils"]; %>
<%* const metadata = utils.generateMetadataFromFilename(tp.file.title); %>

**Category:** <% metadata.category %>
**Tags:** <% metadata.tags.join(", ") %>
```

**Calling Script Functions:**
```javascript
<%* const markdownUtils = tp.user["markdown-utils"]; %>
<%* const toc = markdownUtils.generateTableOfContents(
    tp.file.content,
    { minLevel: 2, maxLevel: 4, numbered: true }
); %>

<% toc %>
```

### 4. Asynchronous Operations

**Using Async/Await:**
```javascript
<%*
const aiIntegration = tp.user["ai-integration"];
const summary = await aiIntegration.summarizeContent(
    tp.file.content,
    100
);
tR += summary;
%>
```

**Handling Promises:**
```javascript
<%*
const dataviewHelpers = tp.user["dataview-helpers"];
const stats = await dataviewHelpers.aggregateVaultStats(dv);
%>

**Total Documents:** <% stats.totalDocs %>
**Completion Rate:** <% stats.completionRate %>%
```

### 5. Template Return (`tR`)

**Direct Assignment:**
```javascript
<%* tR = "This replaces the template call entirely"; %>
```

**String Concatenation:**
```javascript
<%* tR += "Append to output"; %>
<%* tR += "\nAnother line"; %>
```

**Building Complex Output:**
```javascript
<%*
let output = "# Dynamic Title\n\n";
output += "**Created:** " + tp.file.creation_date() + "\n";
output += "**Status:** draft\n";
tR = output;
%>
```

---

## User Script Development

### Script Structure

**Basic Template:**
```javascript
/**
 * Module description
 * 
 * @module module-name
 * @version 1.0.0
 */

/**
 * Function description
 * 
 * @param {Type} paramName - Parameter description
 * @returns {Type} Return description
 */
function functionName(paramName) {
    try {
        // Implementation
        return result;
    } catch (error) {
        console.error('Error:', error);
        return defaultValue;
    }
}

// Export for Templater
module.exports = {
    functionName
};
```

### Accessing Obsidian API

**App Instance:**
```javascript
function getVaultFiles(app) {
    if (!app || !app.vault) {
        return [];
    }
    
    const files = app.vault.getMarkdownFiles();
    return files.map(f => ({
        path: f.path,
        name: f.basename,
        size: f.stat.size
    }));
}
```

**Metadata Cache:**
```javascript
function getFileFrontmatter(app, filePath) {
    const file = app.vault.getAbstractFileByPath(filePath);
    if (!file) return null;
    
    const cache = app.metadataCache.getFileCache(file);
    return cache?.frontmatter || null;
}
```

### Error Handling Patterns

**Graceful Degradation:**
```javascript
function safeFunctionCall(callback, fallback = null) {
    try {
        return callback();
    } catch (error) {
        console.error('Function call failed:', error);
        return fallback;
    }
}
```

**Input Validation:**
```javascript
function validateInput(value, type, required = true) {
    if (required && (!value || value === '')) {
        throw new Error(`Required value missing`);
    }
    
    if (type === 'number' && isNaN(Number(value))) {
        throw new Error(`Expected number, got ${typeof value}`);
    }
    
    return true;
}
```

### Testing User Scripts

**Manual Testing:**
```javascript
// Test in browser console
const utils = require('./project-ai-utils.js');
const result = utils.generateMetadataFromFilename('test-file.md');
console.log(result);
```

**Unit Testing Pattern:**
```javascript
function testFunction() {
    const testCases = [
        { input: 'test', expected: 'TEST' },
        { input: 'hello', expected: 'HELLO' }
    ];
    
    testCases.forEach(test => {
        const result = yourFunction(test.input);
        console.assert(
            result === test.expected,
            `Expected ${test.expected}, got ${result}`
        );
    });
}
```

---

## Dynamic Content Generation

### 1. Generating Table of Contents

**Implementation:**
```javascript
<%*
const markdownUtils = tp.user["markdown-utils"];

// Generate TOC for current file
const toc = markdownUtils.generateTableOfContents(
    tp.file.content,
    {
        minLevel: 2,
        maxLevel: 3,
        numbered: true,
        title: "Contents"
    }
);

tR += toc;
%>
```

### 2. Auto-generating Metadata

**Smart Metadata Generation:**
```javascript
<%*
const projectAIUtils = tp.user["project-ai-utils"];
const customVars = tp.user["custom-variables"];

// Generate metadata from filename
const meta = projectAIUtils.generateMetadataFromFilename(tp.file.title);

// Enrich with additional fields
const fullMetadata = customVars.generateDocumentMetadata({
    title: meta.variant || tp.file.title,
    type: meta.type,
    category: meta.category,
    tags: meta.tags,
    status: customVars.getUserPreference('templates.defaultStatus', 'draft')
});

// Format as frontmatter
const frontmatter = customVars.formatFrontmatter(fullMetadata);
tR += frontmatter;
%>
```

### 3. Related Documents Discovery

**Finding Related Content:**
```javascript
<%*
const projectAIUtils = tp.user["project-ai-utils"];

const relatedDocs = projectAIUtils.findRelatedDocuments(
    {
        tags: tp.frontmatter.tags || [],
        type: tp.frontmatter.type,
        category: tp.frontmatter.category,
        path: tp.file.path(true)
    },
    app
);

const wikiLinks = projectAIUtils.generateWikiLinks(relatedDocs, true);
%>

## Related Documentation

<% wikiLinks %>
```

### 4. Quality Checks Integration

**Document Quality Report:**
```javascript
<%*
const qualityChecks = tp.user["quality-checks"];

const report = qualityChecks.comprehensiveQualityCheck(
    tp.frontmatter,
    tp.file.content,
    tp.frontmatter.category,
    app
);
%>

## Quality Report

**Overall Score:** <% report.overallScore %>/100 (Grade: <% report.grade %>)

### Metadata Quality
- **Score:** <% report.metadata.score %>%
- **Errors:** <% report.metadata.errors.length %>
- **Warnings:** <% report.metadata.warnings.length %>

### Recommendations
<%* report.recommendations.forEach(rec => { %>
- <% rec %>
<%* }); %>
```

---

## Error Handling

### Template-Level Error Handling

**Try-Catch Wrapper:**
```javascript
<%*
try {
    // Template logic here
    const result = tp.user["some-script"].someFunction();
    tR += result;
} catch (error) {
    tR += `> ⚠️ Error generating content: ${error.message}\n`;
    tR += `> Please check the template configuration.\n`;
}
%>
```

**Fallback Values:**
```javascript
<%*
const utils = tp.user["project-ai-utils"];
const metadata = utils ? 
    utils.generateMetadataFromFilename(tp.file.title) :
    { category: 'unknown', tags: [] };
%>
```

### Script-Level Error Handling

**Defensive Programming:**
```javascript
function safeOperation(app, param) {
    // Check prerequisites
    if (!app || !app.vault) {
        console.warn('App instance not available');
        return null;
    }
    
    if (!param) {
        console.warn('Required parameter missing');
        return null;
    }
    
    try {
        // Main logic
        return performOperation(param);
    } catch (error) {
        console.error('Operation failed:', error);
        // Log error for debugging
        logError(error);
        return null;
    }
}
```

**Error Logging:**
```javascript
function logError(error) {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] Error:`, {
        message: error.message,
        stack: error.stack
    });
}
```

---

## Performance Optimization

### 1. Lazy Loading

**Load Scripts Only When Needed:**
```javascript
<%*
// Only load if condition met
if (tp.frontmatter.category === 'module-doc') {
    const utils = tp.user["project-ai-utils"];
    // Use utils...
}
%>
```

### 2. Caching Results

**Cache Expensive Operations:**
```javascript
<%*
// Cache in frontmatter for reuse
if (!tp.frontmatter.cached_summary) {
    const aiIntegration = tp.user["ai-integration"];
    const summary = await aiIntegration.summarizeContent(tp.file.content);
    
    // Update frontmatter (requires manual save)
    tR += `cached_summary: "${summary}"\n`;
} else {
    tR += tp.frontmatter.cached_summary;
}
%>
```

### 3. Batch Operations

**Process Multiple Items Together:**
```javascript
<%*
const projectAIUtils = tp.user["project-ai-utils"];

// Batch tag generation
const tags = projectAIUtils.generateTagsForCategory(
    tp.frontmatter.category,
    tp.frontmatter.type,
    tp.frontmatter.variant
);

// Single write operation
tR += `tags: [${tags.join(', ')}]\n`;
%>
```

### 4. Limiting Iterations

**Set Reasonable Limits:**
```javascript
<%*
const maxItems = 50; // Prevent infinite loops
const numItems = Math.min(
    parseInt(tp.system.prompt("How many?", "10")),
    maxItems
);

for (let i = 1; i <= numItems; i++) {
    tR += `Item ${i}\n`;
}
%>
```

---

## Integration Patterns

### 1. Dataview Integration

**Query Builder:**
```javascript
<%*
const dataviewHelpers = tp.user["dataview-helpers"];

const query = dataviewHelpers.buildQuery(
    {
        category: 'module-doc',
        tags: ['ai', 'core'],
        status: 'published'
    },
    'table',
    ['file.name', 'updated', 'status']
);
%>

```dataview
<% query %>
```

### 2. Git Integration

**Auto-generate Commit Message:**
```javascript
<%*
const gitIntegration = tp.user["git-integration"];

const commitMsg = gitIntegration.generateCommitFromMetadata(
    tp.frontmatter,
    tp.file.title,
    true // isNew
);
%>

<!-- Git Commit Message:
<% commitMsg %>
-->
```

### 3. Export Preparation

**PDF Export:**
```javascript
<%*
const exportUtils = tp.user["export-utils"];

const pdfContent = exportUtils.preparePDFExport(
    tp.file.content,
    {
        includeTableOfContents: true,
        pageBreaks: true,
        pageBreakLevel: 'h1'
    }
);

// Could write to export file
%>
```

---

## Best Practices

### 1. Template Organization

**Use Consistent Naming:**
- `{category}-{type}-{variant}.md`
- Example: `module-doc-core-system.md`

**Group Related Templates:**
- Development: `templates/development/`
- Documentation: `templates/documentation/`
- Operations: `templates/operations/`

### 2. Code Quality

**Write Readable Templates:**
```javascript
// GOOD: Clear, well-structured
<%*
const utils = tp.user["project-ai-utils"];
const metadata = utils.generateMetadataFromFilename(tp.file.title);
const tags = metadata.tags.join(", ");
%>
Tags: <% tags %>

// BAD: Unclear, condensed
<%* tR += tp.user["project-ai-utils"].generateMetadataFromFilename(tp.file.title).tags.join(", ") %>
```

**Add Comments:**
```javascript
<%*
// Generate metadata from filename
const metadata = utils.generateMetadataFromFilename(tp.file.title);

// Validate required fields
if (!metadata.category) {
    tR += "Warning: Category not determined\n";
}
%>
```

### 3. Maintainability

**Version Your Templates:**
```yaml
---
template_version: 2.0.0
last_updated: 2026-04-20
---
```

**Document Breaking Changes:**
```markdown
<!-- Template Changelog
v2.0.0 (2026-04-20):
- Changed metadata structure
- Removed deprecated fields
- Added quality checks integration
-->
```

### 4. Security

**Sanitize User Input:**
```javascript
<%*
const userInput = tp.system.prompt("Enter value", "");
const sanitized = userInput.replace(/[<>]/g, ''); // Remove HTML chars
%>
```

**Don't Hardcode Secrets:**
```javascript
// NEVER do this
const apiKey = "sk-1234567890";

// Instead
const apiKey = process.env.OPENAI_API_KEY;
```

---

## Troubleshooting

### Common Issues

**1. Script Not Found**

**Error:** `Cannot read property of undefined`

**Solution:**
```javascript
// Check script exists
<%*
if (tp.user["script-name"]) {
    // Use script
} else {
    tR += "> Script not loaded. Check Templater settings.\n";
}
%>
```

**2. Async Operation Not Waiting**

**Error:** `[object Promise]` in output

**Solution:**
```javascript
// Always await promises
<%*
const result = await asyncFunction(); // ✅ Correct
const wrong = asyncFunction();        // ❌ Wrong
%>
```

**3. Template Variables Not Updating**

**Solution:**
- Check Templater is enabled for file location
- Verify template folder location in settings
- Try reloading Obsidian

### Debugging Techniques

**Console Logging:**
```javascript
<%*
console.log("Debug: template executing");
console.log("Value:", tp.frontmatter.status);
%>
```

**Conditional Output:**
```javascript
<%*
if (DEBUG_MODE) {
    tR += `\n<!-- DEBUG: ${JSON.stringify(metadata)} -->\n`;
}
%>
```

---

## Advanced Examples

### Example 1: Intelligent Document Creation

```javascript
<%*
// Load all required utilities
const projectAIUtils = tp.user["project-ai-utils"];
const customVars = tp.user["custom-variables"];
const qualityChecks = tp.user["quality-checks"];

// Auto-detect document type from filename
const filenameMetadata = projectAIUtils.generateMetadataFromFilename(tp.file.title);

// Generate complete metadata
const fullMetadata = customVars.generateDocumentMetadata({
    title: tp.file.title,
    type: filenameMetadata.type,
    category: filenameMetadata.category,
    tags: filenameMetadata.tags
});

// Format frontmatter
const frontmatter = customVars.formatFrontmatter(fullMetadata);
%>

<% frontmatter %>

# <% fullMetadata.title %>

## Overview

<%* 
// Generate outline based on type
const aiIntegration = tp.user["ai-integration"];
const outline = aiIntegration.generateOutline(
    fullMetadata.title,
    fullMetadata.type,
    ""
);
%>

<% outline %>

## Quality Checklist

<%*
// Embed quality checks
const templateVars = customVars.getTemplateVariables(fullMetadata.type);
%>

**Required Fields:**
<%* templateVars.requiredFields.forEach(field => { %>
- [ ] <% field %>
<%* }); %>

**Suggested Tags:** <% templateVars.suggestedTags.join(", ") %>
```

### Example 2: Multi-Source Data Integration

```javascript
<%*
// Aggregate data from multiple sources
const dataviewHelpers = tp.user["dataview-helpers"];
const projectAIUtils = tp.user["project-ai-utils"];

// Get vault statistics
const stats = await dataviewHelpers.aggregateVaultStats(dv);

// Find related documents
const related = projectAIUtils.findRelatedDocuments(
    {
        tags: tp.frontmatter.tags,
        category: tp.frontmatter.category
    },
    app
);

// Calculate reading time
const customVars = tp.user["custom-variables"];
const readingTime = customVars.calculateReadingTime(tp.file.content);
%>

## Document Statistics

**Vault Total:** <% stats.totalDocs %> documents
**Completion Rate:** <% stats.completionRate %>%
**Reading Time:** <% readingTime.formatted %>

## Related Documents (<% related.length %> found)

<%* 
const wikiLinks = projectAIUtils.generateWikiLinks(related, true);
%>
<% wikiLinks %>
```

---

## Conclusion

This guide covers advanced Templater usage for the Project-AI vault. For additional examples and patterns, see:

- [[USER_SCRIPTS_REFERENCE.md]] - Complete API reference
- [[TEMPLATE_DEVELOPMENT_GUIDE.md]] - Template creation guide
- [[TEMPLATER_EXAMPLES.md]] - Real-world examples

**Support:**
- GitHub Issues: [project-ai/issues](https://github.com/...)
- Documentation: [[VAULT_STRUCTURE.md]]

---

**Version History:**
- 2.0.0 (2026-04-20): Initial advanced guide
- Future: Added async patterns, error handling deep dive

**Next Review:** 2026-07-20

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

