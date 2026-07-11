/**
 * Project-AI Utilities for Templater
 *
 * Provides Project-AI specific utilities for metadata generation,
 * tag suggestions, related document finding, and automatic wiki linking.
 *
 * @module project-ai-utils
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Extracts metadata from filename using Project-AI naming conventions
 *
 * Parses filenames like:
 * - module-doc-core-system.md → {category: 'module-doc', type: 'core-system'}
 * - agent-doc-task-report.md → {category: 'agent-doc', type: 'task-report'}
 * - architecture-doc-adr-003.md → {category: 'architecture-doc', type: 'adr', number: '003'}
 *
 * @param {string} filename - The filename to parse (without path)
 * @returns {Object} Extracted metadata object
 * @throws {Error} If filename doesn't match expected pattern
 *
 * @example
 * const metadata = generateMetadataFromFilename('module-doc-ai-systems.md');
 * // Returns: { category: 'module-doc', type: 'ai-systems', docType: 'module-doc', ... }
 */
function generateMetadataFromFilename(filename) {
    try {
        // Remove .md extension
        const baseName = filename.replace(/\.md$/i, '');

        // Define category patterns
        const categories = ['module-doc', 'agent-doc', 'architecture-doc', 'guide'];

        // Try to match category
        let category = null;
        let remainder = baseName;

        for (const cat of categories) {
            if (baseName.startsWith(cat + '-')) {
                category = cat;
                remainder = baseName.substring(cat.length + 1);
                break;
            }
        }

        // If no category matched, try to infer from content
        if (!category) {
            // Fallback: analyze filename components
            const parts = baseName.split('-');
            if (parts.length >= 2) {
                // Check for common patterns
                if (parts[0] === 'module' && parts[1] === 'doc') {
                    category = 'module-doc';
                    remainder = parts.slice(2).join('-');
                } else if (parts[0] === 'agent' && parts[1] === 'doc') {
                    category = 'agent-doc';
                    remainder = parts.slice(2).join('-');
                } else if (parts[0] === 'architecture' && parts[1] === 'doc') {
                    category = 'architecture-doc';
                    remainder = parts.slice(2).join('-');
                } else if (parts[0] === 'guide') {
                    category = 'guide';
                    remainder = parts.slice(1).join('-');
                } else {
                    // Default to guide for unknown patterns
                    category = 'guide';
                    remainder = baseName;
                }
            } else {
                category = 'guide';
                remainder = baseName;
            }
        }

        // Extract type and optional number/variant
        const parts = remainder.split('-');
        let type = parts[0] || 'general';
        let variant = parts.length > 1 ? parts.slice(1).join('-') : null;

        // Check if variant contains a number (e.g., adr-003)
        let number = null;
        if (variant) {
            const numberMatch = variant.match(/(\d+)/);
            if (numberMatch) {
                number = numberMatch[1];
            }
        }

        // Generate appropriate tags
        const tags = generateTagsForCategory(category, type, variant);

        // Determine status based on category
        const status = getDefaultStatus(category);

        return {
            category: category,
            type: type,
            variant: variant,
            number: number,
            docType: category,
            tags: tags,
            status: status,
            parsedFrom: filename
        };

    } catch (error) {
        console.error(`Error parsing filename ${filename}:`, error);
        throw new Error(`Failed to parse filename: ${error.message}`);
    }
}

/**
 * Generates appropriate tags based on document category and type
 *
 * @param {string} category - Document category
 * @param {string} type - Document type
 * @param {string|null} variant - Optional variant
 * @returns {string[]} Array of suggested tags
 */
function generateTagsForCategory(category, type, variant) {
    const baseTags = [];

    // Category-specific tags
    switch (category) {
        case 'module-doc':
            baseTags.push('module', 'code', 'api', 'implementation');
            if (type === 'core-system') baseTags.push('core', 'business-logic');
            if (type === 'gui-component') baseTags.push('ui', 'pyqt6', 'gui');
            if (type === 'agent') baseTags.push('ai-agent', 'autonomous');
            break;

        case 'agent-doc':
            baseTags.push('agent', 'task', 'execution', 'audit');
            if (type === 'task-report') baseTags.push('completion', 'deliverables');
            if (type === 'security-audit') baseTags.push('security', 'vulnerability', 'assessment');
            if (type === 'convergence-summary') baseTags.push('multi-agent', 'coordination');
            break;

        case 'architecture-doc':
            baseTags.push('architecture', 'design', 'system');
            if (type === 'adr') baseTags.push('decision', 'adr', 'architectural-decision');
            if (type === 'integration') baseTags.push('integration', 'api', 'external-service');
            if (type === 'design-pattern') baseTags.push('pattern', 'reusable', 'best-practice');
            break;

        case 'guide':
            baseTags.push('guide', 'documentation', 'reference');
            if (type === 'quickstart') baseTags.push('tutorial', 'onboarding', 'getting-started');
            if (type === 'troubleshooting') baseTags.push('runbook', 'problem-solving', 'diagnosis');
            if (type === 'developer-reference') baseTags.push('api', 'developer', 'technical');
            break;
    }

    // Add variant as tag if present
    if (variant && variant !== type) {
        baseTags.push(variant.replace(/\d+/g, '').replace(/-+$/, '').trim());
    }

    return [...new Set(baseTags)]; // Remove duplicates
}

/**
 * Gets default status for document category
 *
 * @param {string} category - Document category
 * @returns {string} Default status value
 */
function getDefaultStatus(category) {
    const statusMap = {
        'module-doc': 'draft',
        'agent-doc': 'completed',
        'architecture-doc': 'proposed',
        'guide': 'published'
    };

    return statusMap[category] || 'draft';
}

/**
 * Suggests tags based on document content analysis
 *
 * Analyzes content for keywords, code blocks, and structural elements
 * to suggest relevant tags.
 *
 * @param {string} content - Document content to analyze
 * @param {number} maxTags - Maximum number of tags to suggest (default: 10)
 * @returns {string[]} Array of suggested tags
 *
 * @example
 * const content = "This module implements the FourLaws ethics system...";
 * const tags = suggestTagsFromContent(content, 5);
 * // Returns: ['ethics', 'four-laws', 'validation', 'ai-safety', 'core']
 */
function suggestTagsFromContent(content, maxTags = 10) {
    try {
        const tags = new Set();

        // Keyword extraction patterns
        const patterns = {
            // Technical keywords
            python: /\b(python|py|pyqt6|flask|fastapi)\b/gi,
            javascript: /\b(javascript|js|react|node|npm)\b/gi,
            ai: /\b(ai|machine-learning|openai|gpt|llm|neural|model)\b/gi,
            security: /\b(security|auth|encrypt|bcrypt|vulnerability|cve)\b/gi,
            database: /\b(database|sql|sqlite|postgres|redis|cache)\b/gi,
            testing: /\b(test|testing|pytest|unittest|coverage|qa)\b/gi,
            deployment: /\b(deploy|docker|container|kubernetes|ci-cd)\b/gi,
            api: /\b(api|rest|graphql|endpoint|http|request)\b/gi,

            // Project-AI specific
            fourLaws: /\b(four-?laws|asimov|ethics|safety-protocol)\b/gi,
            persona: /\b(persona|personality|mood|ai-state)\b/gi,
            memory: /\b(memory|knowledge-base|learning|context)\b/gi,
            plugin: /\b(plugin|extension|addon|module)\b/gi,

            // Document structure
            hasCodeBlocks: /```/g,
            hasTables: /\|.*\|.*\|/g,
            hasDiagrams: /\bmermaid\b|\bdiagram\b/gi
        };

        // Check for code blocks
        const codeBlockMatches = content.match(/```(\w+)/g);
        if (codeBlockMatches) {
            codeBlockMatches.forEach(block => {
                const lang = block.replace(/```/g, '').toLowerCase();
                if (lang && lang !== 'text' && lang !== 'plaintext') {
                    tags.add(lang);
                }
            });
        }

        // Check for technical keywords
        for (const [tag, pattern] of Object.entries(patterns)) {
            if (pattern.test(content)) {
                if (tag === 'hasCodeBlocks') tags.add('code-examples');
                else if (tag === 'hasTables') tags.add('tabular-data');
                else if (tag === 'hasDiagrams') tags.add('diagrams');
                else tags.add(tag);
            }
        }

        // Extract capitalized technical terms (likely to be component/class names)
        const capitalizedTerms = content.match(/\b[A-Z][a-zA-Z0-9]*(?:System|Manager|Service|Handler|Controller|Interface|Panel|Widget|Agent)\b/g);
        if (capitalizedTerms) {
            capitalizedTerms.slice(0, 3).forEach(term => {
                // Convert to kebab-case and add
                const kebab = term.replace(/([A-Z])/g, '-$1').toLowerCase().replace(/^-/, '');
                tags.add(kebab);
            });
        }

        // Check for workflow/lifecycle keywords
        if (/\b(deprecated|legacy|obsolete)\b/gi.test(content)) tags.add('deprecated');
        if (/\b(experimental|beta|preview)\b/gi.test(content)) tags.add('experimental');
        if (/\b(production|stable|release)\b/gi.test(content)) tags.add('production-ready');

        // Convert Set to Array and limit
        return Array.from(tags).slice(0, maxTags);

    } catch (error) {
        console.error('Error analyzing content for tags:', error);
        return [];
    }
}

/**
 * Finds related documents based on tags, type, and content similarity
 *
 * @param {Object} currentDoc - Current document metadata
 * @param {string} currentDoc.tags - Tags array
 * @param {string} currentDoc.type - Document type
 * @param {string} currentDoc.category - Document category
 * @param {Object} app - Obsidian app instance
 * @returns {Object[]} Array of related documents with similarity scores
 *
 * @example
 * const related = findRelatedDocuments({
 *   tags: ['ai', 'ethics', 'four-laws'],
 *   type: 'module-doc',
 *   category: 'module-doc'
 * }, app);
 */
function findRelatedDocuments(currentDoc, app) {
    try {
        if (!app || !app.vault) {
            console.warn('App instance not available, cannot find related documents');
            return [];
        }

        const allFiles = app.vault.getMarkdownFiles();
        const related = [];

        // Get current document's tags as Set for faster lookup
        const currentTags = new Set(currentDoc.tags || []);

        for (const file of allFiles) {
            // Skip current file
            if (file.path === currentDoc.path) continue;

            // Get file's frontmatter
            const cache = app.metadataCache.getFileCache(file);
            if (!cache || !cache.frontmatter) continue;

            const fileTags = new Set(cache.frontmatter.tags || []);
            const fileType = cache.frontmatter.type || '';
            const fileCategory = cache.frontmatter.category || '';

            // Calculate similarity score
            let score = 0;

            // Tag overlap (weighted heavily)
            const tagOverlap = new Set([...currentTags].filter(tag => fileTags.has(tag)));
            score += tagOverlap.size * 3;

            // Same category
            if (fileCategory === currentDoc.category) score += 2;

            // Same type
            if (fileType === currentDoc.type) score += 2;

            // Related categories (e.g., module-doc relates to architecture-doc)
            const relatedCategories = {
                'module-doc': ['architecture-doc', 'guide'],
                'agent-doc': ['module-doc'],
                'architecture-doc': ['module-doc', 'guide'],
                'guide': ['module-doc', 'architecture-doc']
            };

            if (relatedCategories[currentDoc.category]?.includes(fileCategory)) {
                score += 1;
            }

            // Only include if there's some relation
            if (score > 0) {
                related.push({
                    path: file.path,
                    name: file.basename,
                    score: score,
                    tags: Array.from(fileTags),
                    type: fileType,
                    category: fileCategory
                });
            }
        }

        // Sort by score descending and return top 10
        return related
            .sort((a, b) => b.score - a.score)
            .slice(0, 10);

    } catch (error) {
        console.error('Error finding related documents:', error);
        return [];
    }
}

/**
 * Generates wiki links for related documents
 *
 * @param {Object[]} relatedDocs - Array of related documents from findRelatedDocuments
 * @param {boolean} includeDescription - Whether to include descriptions (default: false)
 * @returns {string} Markdown formatted wiki links
 *
 * @example
 * const links = generateWikiLinks(relatedDocs, true);
 * // Returns:
 * // - [[module-doc-ai-systems]] - AI Systems Documentation (score: 12)
 * // - [[architecture-doc-state-persistence]] - State Persistence Pattern (score: 8)
 */
function generateWikiLinks(relatedDocs, includeDescription = false) {
    try {
        if (!relatedDocs || relatedDocs.length === 0) {
            return '> No related documents found';
        }

        const links = relatedDocs.map(doc => {
            const link = `[[${doc.name}]]`;

            if (includeDescription) {
                const description = doc.type ? ` - ${doc.type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}` : '';
                const scoreInfo = ` (similarity: ${doc.score})`;
                return `- ${link}${description}${scoreInfo}`;
            } else {
                return `- ${link}`;
            }
        });

        return links.join('\n');

    } catch (error) {
        console.error('Error generating wiki links:', error);
        return '> Error generating links';
    }
}

/**
 * Extracts module path from filename or content
 *
 * Attempts to find Python module paths like:
 * - src/app/core/ai_systems.py
 * - src/app/gui/leather_book_interface.py
 *
 * @param {string} filename - Filename to analyze
 * @param {string} content - Document content to search
 * @returns {string|null} Extracted module path or null
 */
function extractModulePath(filename, content) {
    try {
        // Try to find path in content first
        const pathPattern = /src\/app\/(?:core|gui|agents)\/[a-z_]+\.py/g;
        const matches = content.match(pathPattern);

        if (matches && matches.length > 0) {
            return matches[0];
        }

        // Try to infer from filename
        // e.g., "module-doc-ai-systems.md" -> "src/app/core/ai_systems.py"
        const nameMatch = filename.match(/module-doc-([a-z-]+)\.md/);
        if (nameMatch) {
            const moduleName = nameMatch[1].replace(/-/g, '_');

            // Try to determine if it's core, gui, or agent
            if (content.includes('PyQt') || content.includes('QWidget') || content.includes('gui')) {
                return `src/app/gui/${moduleName}.py`;
            } else if (content.includes('agent') || content.includes('Agent')) {
                return `src/app/agents/${moduleName}.py`;
            } else {
                return `src/app/core/${moduleName}.py`;
            }
        }

        return null;

    } catch (error) {
        console.error('Error extracting module path:', error);
        return null;
    }
}

/**
 * Generates a suggested alias list based on document type and content
 *
 * @param {Object} metadata - Document metadata
 * @param {string} content - Document content
 * @returns {string[]} Array of suggested aliases
 */
function generateAliases(metadata, content) {
    try {
        const aliases = new Set();

        // Add category-specific aliases
        if (metadata.category === 'module-doc') {
            if (metadata.variant) {
                // Convert variant to different formats
                const camelCase = metadata.variant.replace(/-([a-z])/g, g => g[1].toUpperCase());
                const snake_case = metadata.variant.replace(/-/g, '_');
                const PascalCase = camelCase.charAt(0).toUpperCase() + camelCase.slice(1);

                aliases.add(camelCase);
                aliases.add(snake_case);
                aliases.add(PascalCase);
            }
        } else if (metadata.category === 'architecture-doc' && metadata.type === 'adr') {
            // ADR number aliases
            if (metadata.number) {
                aliases.add(`ADR-${metadata.number}`);
                aliases.add(`adr${metadata.number}`);
            }
        } else if (metadata.category === 'agent-doc') {
            // Agent ID aliases
            const agentMatch = content.match(/AGENT-(\d+)/);
            if (agentMatch) {
                aliases.add(`AGENT-${agentMatch[1]}`);
                aliases.add(`agent${agentMatch[1]}`);
            }
        }

        return Array.from(aliases).slice(0, 5); // Limit to 5 aliases

    } catch (error) {
        console.error('Error generating aliases:', error);
        return [];
    }
}

/**
 * Validates document completeness based on metadata schema requirements
 *
 * @param {Object} frontmatter - Document frontmatter
 * @param {string} content - Document content
 * @param {string} category - Document category
 * @returns {Object} Validation result with isValid, errors, warnings
 */
function validateDocumentCompleteness(frontmatter, content, category) {
    const errors = [];
    const warnings = [];

    // Required universal fields
    const requiredFields = ['created', 'type', 'status', 'tags'];
    for (const field of requiredFields) {
        if (!frontmatter[field]) {
            errors.push(`Missing required field: ${field}`);
        }
    }

    // Category-specific validations
    const minWordCounts = {
        'module-doc': 1000,
        'agent-doc': 500,
        'architecture-doc': 1500,
        'guide': 800
    };

    const wordCount = content.split(/\s+/).length;
    const minWords = minWordCounts[category] || 500;

    if (wordCount < minWords) {
        warnings.push(`Document may be incomplete: ${wordCount} words (recommended: ${minWords}+)`);
    }

    // Check for required sections
    if (!content.includes('## ') && !content.includes('# ')) {
        errors.push('Document has no headings/sections');
    }

    // Check for empty tags
    if (frontmatter.tags && frontmatter.tags.length === 0) {
        warnings.push('No tags specified - document may be hard to discover');
    }

    return {
        isValid: errors.length === 0,
        errors: errors,
        warnings: warnings,
        wordCount: wordCount,
        completeness: Math.min(100, Math.round((wordCount / minWords) * 100))
    };
}

// Export functions for use in Templater
module.exports = {
    generateMetadataFromFilename,
    suggestTagsFromContent,
    findRelatedDocuments,
    generateWikiLinks,
    extractModulePath,
    generateAliases,
    validateDocumentCompleteness,
    generateTagsForCategory,
    getDefaultStatus
};
