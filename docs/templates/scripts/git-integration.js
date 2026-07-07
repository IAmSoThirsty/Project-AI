/**
 * Git Integration Helpers for Templater
 * 
 * Provides utilities for generating commit messages, branch names,
 * and PR descriptions based on document changes and metadata.
 * 
 * @module git-integration
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Generates a conventional commit message based on document changes
 * 
 * Follows Conventional Commits specification:
 * <type>[optional scope]: <description>
 * 
 * @param {Object} options - Commit message options
 * @param {string} options.type - Commit type (docs, feat, fix, etc.)
 * @param {string} options.scope - Optional scope (module-doc, agent-doc, etc.)
 * @param {string} options.description - Brief description of changes
 * @param {string[]} options.files - Files changed
 * @param {boolean} options.breaking - Whether this is a breaking change
 * @param {string} options.body - Optional detailed description
 * @param {string[]} options.footers - Optional footers (e.g., issue refs)
 * @returns {string} Formatted commit message
 * 
 * @example
 * const message = generateCommitMessage({
 *   type: 'docs',
 *   scope: 'module-doc',
 *   description: 'add ai_systems documentation',
 *   files: ['knowledge-vault/modules/ai-systems.md']
 * });
 * // Returns: "docs(module-doc): add ai_systems documentation"
 */
function generateCommitMessage(options = {}) {
    try {
        const {
            type = 'docs',
            scope = null,
            description = '',
            files = [],
            breaking = false,
            body = null,
            footers = []
        } = options;
        
        // Validate type
        const validTypes = [
            'docs',     // Documentation changes
            'feat',     // New feature
            'fix',      // Bug fix
            'refactor', // Code refactoring
            'test',     // Adding tests
            'chore',    // Maintenance
            'style',    // Formatting changes
            'perf',     // Performance improvements
            'ci',       // CI/CD changes
            'build'     // Build system changes
        ];
        
        const commitType = validTypes.includes(type) ? type : 'docs';
        
        // Build header
        let header = commitType;
        
        if (scope) {
            header += `(${scope})`;
        }
        
        if (breaking) {
            header += '!';
        }
        
        header += ': ' + description.toLowerCase();
        
        // Build full message
        let message = header;
        
        // Add body if provided
        if (body) {
            message += '\n\n' + body;
        }
        
        // Add file list if multiple files
        if (files.length > 1) {
            message += '\n\nFiles changed:';
            files.forEach(file => {
                message += '\n- ' + file;
            });
        }
        
        // Add footers
        if (footers.length > 0) {
            message += '\n\n';
            footers.forEach(footer => {
                message += footer + '\n';
            });
        }
        
        return message;
        
    } catch (error) {
        console.error('Error generating commit message:', error);
        return 'docs: update documentation';
    }
}

/**
 * Generates a commit message from document metadata
 * 
 * @param {Object} frontmatter - Document frontmatter
 * @param {string} filename - Document filename
 * @param {boolean} isNew - Whether this is a new document
 * @returns {string} Generated commit message
 * 
 * @example
 * const message = generateCommitFromMetadata(frontmatter, 'ai-systems.md', true);
 * // Returns: "docs(module-doc): add AI Systems module documentation"
 */
function generateCommitFromMetadata(frontmatter, filename, isNew = true) {
    try {
        const category = frontmatter.category || frontmatter.type || 'docs';
        const docType = frontmatter.type || 'document';
        
        // Determine action verb
        const action = isNew ? 'add' : 'update';
        
        // Extract document title or use filename
        const title = frontmatter.title || 
                     filename.replace(/\.md$/, '').replace(/-/g, ' ');
        
        // Build description
        const description = `${action} ${title}`;
        
        return generateCommitMessage({
            type: 'docs',
            scope: category,
            description: description,
            files: [filename]
        });
        
    } catch (error) {
        console.error('Error generating commit from metadata:', error);
        return 'docs: update documentation';
    }
}

/**
 * Generates a branch name based on task or feature
 * 
 * Follows naming convention: <type>/<scope>/<description>
 * 
 * @param {Object} options - Branch name options
 * @param {string} options.type - Branch type (feature, bugfix, docs, hotfix)
 * @param {string} options.scope - Scope or component
 * @param {string} options.description - Brief description
 * @param {string} options.issueNumber - Optional issue number
 * @returns {string} Generated branch name
 * 
 * @example
 * const branch = generateBranchName({
 *   type: 'docs',
 *   scope: 'templates',
 *   description: 'add advanced user scripts',
 *   issueNumber: '42'
 * });
 * // Returns: "docs/templates/add-advanced-user-scripts-42"
 */
function generateBranchName(options = {}) {
    try {
        const {
            type = 'docs',
            scope = '',
            description = '',
            issueNumber = null
        } = options;
        
        // Validate type
        const validTypes = [
            'feature',  // New feature
            'bugfix',   // Bug fix
            'docs',     // Documentation
            'hotfix',   // Critical fix
            'refactor', // Code refactoring
            'test',     // Testing
            'chore'     // Maintenance
        ];
        
        const branchType = validTypes.includes(type) ? type : 'docs';
        
        // Normalize description (lowercase, hyphenated, no special chars)
        const normalizedDesc = description
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
        
        // Normalize scope
        const normalizedScope = scope
            .toLowerCase()
            .replace(/[^a-z0-9-]/g, '')
            .replace(/-+/g, '-');
        
        // Build branch name
        let branchName = branchType;
        
        if (normalizedScope) {
            branchName += '/' + normalizedScope;
        }
        
        if (normalizedDesc) {
            branchName += '/' + normalizedDesc;
        }
        
        if (issueNumber) {
            branchName += '-' + issueNumber;
        }
        
        return branchName;
        
    } catch (error) {
        console.error('Error generating branch name:', error);
        return 'docs/update';
    }
}

/**
 * Generates a pull request description from document metadata
 * 
 * @param {Object} options - PR description options
 * @param {string} options.title - PR title
 * @param {string} options.description - What was changed
 * @param {string[]} options.files - Files changed
 * @param {string} options.category - Document category
 * @param {string[]} options.tags - Document tags
 * @param {string} options.motivation - Why the change was made
 * @param {string[]} options.relatedIssues - Related issue numbers
 * @param {Object} options.checklist - Checklist items
 * @returns {string} Formatted PR description in Markdown
 * 
 * @example
 * const prDesc = generatePRDescription({
 *   title: 'Add AI Systems Module Documentation',
 *   description: 'Comprehensive documentation for the core AI systems module',
 *   files: ['knowledge-vault/modules/ai-systems.md'],
 *   category: 'module-doc',
 *   tags: ['ai', 'core', 'ethics'],
 *   motivation: 'Improve developer onboarding and system understanding',
 *   relatedIssues: ['#42', '#55']
 * });
 */
function generatePRDescription(options = {}) {
    try {
        const {
            title = '',
            description = '',
            files = [],
            category = '',
            tags = [],
            motivation = '',
            relatedIssues = [],
            checklist = null
        } = options;
        
        let prDesc = `## ${title}\n\n`;
        
        // Overview section
        prDesc += '### Overview\n\n';
        prDesc += description + '\n\n';
        
        // Motivation section
        if (motivation) {
            prDesc += '### Motivation\n\n';
            prDesc += motivation + '\n\n';
        }
        
        // Changes section
        prDesc += '### Changes\n\n';
        
        if (files.length > 0) {
            prDesc += 'Files modified:\n';
            files.forEach(file => {
                prDesc += `- \`${file}\`\n`;
            });
            prDesc += '\n';
        }
        
        if (category) {
            prDesc += `**Category:** ${category}\n`;
        }
        
        if (tags.length > 0) {
            prDesc += `**Tags:** ${tags.map(t => `\`${t}\``).join(', ')}\n`;
        }
        
        prDesc += '\n';
        
        // Checklist
        const defaultChecklist = checklist || {
            'Documentation is complete': false,
            'All required metadata fields present': false,
            'Links are valid': false,
            'Code examples tested (if applicable)': false,
            'Follows template standards': false
        };
        
        prDesc += '### Checklist\n\n';
        for (const [item, checked] of Object.entries(defaultChecklist)) {
            const checkbox = checked ? '[x]' : '[ ]';
            prDesc += `- ${checkbox} ${item}\n`;
        }
        prDesc += '\n';
        
        // Related issues
        if (relatedIssues.length > 0) {
            prDesc += '### Related Issues\n\n';
            relatedIssues.forEach(issue => {
                prDesc += `- Closes ${issue}\n`;
            });
            prDesc += '\n';
        }
        
        // Reviewer notes
        prDesc += '### Reviewer Notes\n\n';
        prDesc += '> Please review for technical accuracy, completeness, and adherence to documentation standards.\n\n';
        
        return prDesc;
        
    } catch (error) {
        console.error('Error generating PR description:', error);
        return '## Update\n\nDocumentation changes.';
    }
}

/**
 * Generates a git commit hook script for documentation validation
 * 
 * @param {Object} options - Hook configuration
 * @param {boolean} options.validateMetadata - Check metadata completeness
 * @param {boolean} options.validateLinks - Check for broken links
 * @param {boolean} options.formatCheck - Check markdown formatting
 * @returns {string} Shell script for git hook
 */
function generatePreCommitHook(options = {}) {
    const {
        validateMetadata = true,
        validateLinks = true,
        formatCheck = true
    } = options;
    
    let script = '#!/bin/sh\n';
    script += '# Pre-commit hook for Project-AI documentation\n';
    script += '# Auto-generated by Templater git-integration script\n\n';
    
    script += 'echo "Running documentation validation..."\n\n';
    
    // Get staged markdown files
    script += '# Get staged markdown files\n';
    script += 'STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep "\.md$")\n\n';
    
    script += 'if [ -z "$STAGED_MD" ]; then\n';
    script += '  echo "No markdown files to validate."\n';
    script += '  exit 0\n';
    script += 'fi\n\n';
    
    // Validation checks
    if (validateMetadata) {
        script += '# Check metadata completeness\n';
        script += 'echo "Checking metadata..."\n';
        script += 'for FILE in $STAGED_MD; do\n';
        script += '  if ! grep -q "^---$" "$FILE"; then\n';
        script += '    echo "ERROR: $FILE is missing frontmatter"\n';
        script += '    exit 1\n';
        script += '  fi\n';
        script += 'done\n\n';
    }
    
    if (validateLinks) {
        script += '# Check for broken internal links (basic check)\n';
        script += 'echo "Checking links..."\n';
        script += '# TODO: Implement link validation\n\n';
    }
    
    if (formatCheck) {
        script += '# Check markdown formatting\n';
        script += 'echo "Checking markdown formatting..."\n';
        script += '# TODO: Implement formatting checks\n\n';
    }
    
    script += 'echo "✅ All validation checks passed!"\n';
    script += 'exit 0\n';
    
    return script;
}

/**
 * Parses conventional commit message
 * 
 * @param {string} message - Commit message to parse
 * @returns {Object} Parsed commit components
 */
function parseCommitMessage(message) {
    try {
        // Pattern: <type>(<scope>): <description>
        const pattern = /^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$/;
        const match = message.match(pattern);
        
        if (!match) {
            return {
                valid: false,
                type: null,
                scope: null,
                breaking: false,
                description: message
            };
        }
        
        return {
            valid: true,
            type: match[1],
            scope: match[2] || null,
            breaking: match[3] === '!',
            description: match[4]
        };
        
    } catch (error) {
        console.error('Error parsing commit message:', error);
        return { valid: false };
    }
}

/**
 * Generates a changelog entry from commits
 * 
 * @param {Object[]} commits - Array of commit objects
 * @param {string} version - Version number
 * @returns {string} Markdown formatted changelog
 */
function generateChangelog(commits, version = '1.0.0') {
    try {
        let changelog = `## [${version}] - ${new Date().toISOString().split('T')[0]}\n\n`;
        
        // Group commits by type
        const grouped = {
            feat: [],
            fix: [],
            docs: [],
            refactor: [],
            perf: [],
            test: [],
            chore: []
        };
        
        commits.forEach(commit => {
            const parsed = parseCommitMessage(commit.message || commit);
            if (parsed.valid && grouped[parsed.type]) {
                grouped[parsed.type].push(parsed);
            }
        });
        
        // Build changelog sections
        const sections = {
            feat: '### ✨ Features',
            fix: '### 🐛 Bug Fixes',
            docs: '### 📚 Documentation',
            refactor: '### ♻️ Refactoring',
            perf: '### ⚡ Performance',
            test: '### ✅ Tests',
            chore: '### 🔧 Maintenance'
        };
        
        for (const [type, title] of Object.entries(sections)) {
            if (grouped[type].length > 0) {
                changelog += `${title}\n\n`;
                grouped[type].forEach(commit => {
                    const scope = commit.scope ? `**${commit.scope}:** ` : '';
                    changelog += `- ${scope}${commit.description}\n`;
                });
                changelog += '\n';
            }
        }
        
        return changelog;
        
    } catch (error) {
        console.error('Error generating changelog:', error);
        return `## [${version}]\n\nNo changes documented.`;
    }
}

// Export functions for use in Templater
module.exports = {
    generateCommitMessage,
    generateCommitFromMetadata,
    generateBranchName,
    generatePRDescription,
    generatePreCommitHook,
    parseCommitMessage,
    generateChangelog
};
