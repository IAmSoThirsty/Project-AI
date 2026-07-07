/**
 * Markdown Utilities for Templater
 * 
 * Provides markdown manipulation helpers including TOC generation,
 * heading formatting, link validation, and code block formatting.
 * 
 * @module markdown-utils
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Generates a table of contents from markdown content
 * 
 * Creates a hierarchical TOC with proper indentation and anchor links.
 * Supports customization of heading levels to include and TOC style.
 * 
 * @param {string} content - Markdown content to analyze
 * @param {Object} options - TOC generation options
 * @param {number} options.minLevel - Minimum heading level to include (default: 2)
 * @param {number} options.maxLevel - Maximum heading level to include (default: 4)
 * @param {boolean} options.numbered - Whether to add numbering (default: false)
 * @param {string} options.title - TOC title (default: "Table of Contents")
 * @returns {string} Generated table of contents in markdown
 * 
 * @example
 * const toc = generateTableOfContents(content, {
 *   minLevel: 2,
 *   maxLevel: 3,
 *   numbered: true,
 *   title: "Contents"
 * });
 */
function generateTableOfContents(content, options = {}) {
    try {
        const {
            minLevel = 2,
            maxLevel = 4,
            numbered = false,
            title = "Table of Contents"
        } = options;
        
        // Extract headings
        const headingRegex = /^(#{1,6})\s+(.+)$/gm;
        const headings = [];
        let match;
        
        while ((match = headingRegex.exec(content)) !== null) {
            const level = match[1].length;
            const text = match[2].trim();
            
            // Skip headings outside specified range
            if (level < minLevel || level > maxLevel) continue;
            
            // Skip metadata headings
            if (text.toLowerCase().includes('table of contents')) continue;
            
            headings.push({
                level: level,
                text: text,
                anchor: createAnchorLink(text)
            });
        }
        
        if (headings.length === 0) {
            return `> No headings found in document (levels ${minLevel}-${maxLevel})`;
        }
        
        // Build TOC
        let toc = `## ${title}\n\n`;
        
        // Track numbering at each level
        const counters = new Array(maxLevel + 1).fill(0);
        
        headings.forEach(heading => {
            const indent = '  '.repeat(heading.level - minLevel);
            const bullet = numbered ? '1.' : '-';
            
            if (numbered) {
                // Increment current level counter
                counters[heading.level]++;
                
                // Reset deeper level counters
                for (let i = heading.level + 1; i <= maxLevel; i++) {
                    counters[i] = 0;
                }
                
                // Build number string (e.g., 1.2.3)
                const numberParts = [];
                for (let i = minLevel; i <= heading.level; i++) {
                    numberParts.push(counters[i]);
                }
                const number = numberParts.join('.');
                
                toc += `${indent}${bullet} ${number} [${heading.text}](#${heading.anchor})\n`;
            } else {
                toc += `${indent}${bullet} [${heading.text}](#${heading.anchor})\n`;
            }
        });
        
        return toc;
        
    } catch (error) {
        console.error('Error generating table of contents:', error);
        return `> Error generating TOC: ${error.message}`;
    }
}

/**
 * Creates an anchor link from heading text
 * 
 * Converts heading text to valid GitHub-style anchor links.
 * 
 * @param {string} text - Heading text
 * @returns {string} Anchor link slug
 * 
 * @example
 * createAnchorLink("API Reference Guide") // Returns: "api-reference-guide"
 */
function createAnchorLink(text) {
    return text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-')      // Replace spaces with hyphens
        .replace(/-+/g, '-')       // Replace multiple hyphens with single
        .replace(/^-|-$/g, '');    // Remove leading/trailing hyphens
}

/**
 * Formats headings to ensure consistent styling
 * 
 * Ensures:
 * - Proper spacing after # symbols
 * - No trailing # symbols
 * - Consistent capitalization style
 * - Proper blank lines before/after headings
 * 
 * @param {string} content - Markdown content
 * @param {Object} options - Formatting options
 * @param {string} options.capitalization - 'title-case' | 'sentence-case' | 'preserve' (default: 'preserve')
 * @param {boolean} options.blankLines - Add blank lines around headings (default: true)
 * @returns {string} Formatted markdown content
 */
function formatHeadings(content, options = {}) {
    try {
        const {
            capitalization = 'preserve',
            blankLines = true
        } = options;
        
        let formatted = content;
        
        // Fix spacing after # symbols
        formatted = formatted.replace(/^(#{1,6})([^\s#])/gm, '$1 $2');
        
        // Remove trailing # symbols
        formatted = formatted.replace(/^(#{1,6}\s+.+?)\s*#+\s*$/gm, '$1');
        
        // Apply capitalization
        if (capitalization !== 'preserve') {
            formatted = formatted.replace(/^(#{1,6}\s+)(.+)$/gm, (match, prefix, text) => {
                if (capitalization === 'title-case') {
                    return prefix + toTitleCase(text);
                } else if (capitalization === 'sentence-case') {
                    return prefix + text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
                }
                return match;
            });
        }
        
        // Add blank lines around headings
        if (blankLines) {
            // Add line before headings (if not already present)
            formatted = formatted.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2');
            
            // Add line after headings (if not already present)
            formatted = formatted.replace(/(#{1,6}\s.+)\n([^\n])/g, '$1\n\n$2');
        }
        
        return formatted;
        
    } catch (error) {
        console.error('Error formatting headings:', error);
        return content;
    }
}

/**
 * Converts text to Title Case
 * 
 * @param {string} text - Text to convert
 * @returns {string} Title-cased text
 */
function toTitleCase(text) {
    const smallWords = /^(a|an|and|as|at|but|by|for|from|if|in|into|near|nor|of|on|onto|or|the|to|with)$/i;
    
    return text.replace(/\w\S*/g, (word, index) => {
        if (index > 0 && smallWords.test(word)) {
            return word.toLowerCase();
        }
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    });
}

/**
 * Validates internal wiki links in markdown content
 * 
 * Checks if linked documents exist in the vault and identifies broken links.
 * 
 * @param {string} content - Markdown content to validate
 * @param {Object} app - Obsidian app instance
 * @returns {Object} Validation result with valid, broken, and external links
 * 
 * @example
 * const result = validateLinks(content, app);
 * // Returns: { valid: [...], broken: [...], external: [...], totalLinks: 15 }
 */
function validateLinks(content, app) {
    try {
        const valid = [];
        const broken = [];
        const external = [];
        
        if (!app || !app.vault) {
            console.warn('App instance not available for link validation');
            return { valid, broken, external, totalLinks: 0, validated: false };
        }
        
        // Extract wiki links [[link]]
        const wikiLinkRegex = /\[\[([^\]]+)\]\]/g;
        let match;
        
        while ((match = wikiLinkRegex.exec(content)) !== null) {
            const linkText = match[1];
            
            // Parse link (handle aliases and anchors)
            const parts = linkText.split('|');
            const linkPath = parts[0].split('#')[0].trim();
            
            // Check if file exists
            const file = app.metadataCache.getFirstLinkpathDest(linkPath, '');
            
            if (file) {
                valid.push({
                    link: linkText,
                    path: file.path,
                    type: 'wiki'
                });
            } else {
                broken.push({
                    link: linkText,
                    type: 'wiki'
                });
            }
        }
        
        // Extract markdown links [text](url)
        const mdLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        
        while ((match = mdLinkRegex.exec(content)) !== null) {
            const text = match[1];
            const url = match[2];
            
            // Check if external or internal
            if (url.startsWith('http://') || url.startsWith('https://')) {
                external.push({
                    text: text,
                    url: url,
                    type: 'external'
                });
            } else {
                // Internal file link
                const file = app.vault.getAbstractFileByPath(url);
                
                if (file) {
                    valid.push({
                        text: text,
                        path: url,
                        type: 'markdown'
                    });
                } else {
                    broken.push({
                        text: text,
                        path: url,
                        type: 'markdown'
                    });
                }
            }
        }
        
        return {
            valid: valid,
            broken: broken,
            external: external,
            totalLinks: valid.length + broken.length + external.length,
            validated: true
        };
        
    } catch (error) {
        console.error('Error validating links:', error);
        return { valid: [], broken: [], external: [], totalLinks: 0, validated: false };
    }
}

/**
 * Formats code blocks for consistency
 * 
 * Ensures:
 * - Language specifiers are present
 * - Consistent indentation
 * - Proper blank lines around code blocks
 * - Optional syntax highlighting hints
 * 
 * @param {string} content - Markdown content
 * @param {Object} options - Formatting options
 * @param {boolean} options.addLanguage - Auto-detect and add language (default: true)
 * @param {boolean} options.blankLines - Add blank lines around blocks (default: true)
 * @returns {string} Formatted markdown content
 */
function formatCodeBlocks(content, options = {}) {
    try {
        const {
            addLanguage = true,
            blankLines = true
        } = options;
        
        let formatted = content;
        
        // Add blank lines around code blocks
        if (blankLines) {
            // Before code blocks
            formatted = formatted.replace(/([^\n])\n(```)/g, '$1\n\n$2');
            
            // After code blocks
            formatted = formatted.replace(/(```)\n([^\n])/g, '$1\n\n$2');
        }
        
        // Auto-detect and add language specifiers
        if (addLanguage) {
            formatted = formatted.replace(/```\n([\s\S]*?)```/g, (match, code) => {
                // Detect language from code content
                const language = detectCodeLanguage(code);
                if (language) {
                    return '```' + language + '\n' + code + '```';
                }
                return match;
            });
        }
        
        return formatted;
        
    } catch (error) {
        console.error('Error formatting code blocks:', error);
        return content;
    }
}

/**
 * Detects programming language from code content
 * 
 * @param {string} code - Code content to analyze
 * @returns {string|null} Detected language or null
 */
function detectCodeLanguage(code) {
    // Python indicators
    if (/\b(def|class|import|from|if __name__|print\()\b/.test(code)) {
        return 'python';
    }
    
    // JavaScript indicators
    if (/\b(function|const|let|var|=>|console\.log)\b/.test(code)) {
        return 'javascript';
    }
    
    // TypeScript indicators
    if (/\b(interface|type|enum|implements|extends)\s+\w+/.test(code) && 
        /:\s*(string|number|boolean)/.test(code)) {
        return 'typescript';
    }
    
    // JSON indicator
    if (/^\s*[\{\[]/.test(code) && /[\}\]]\s*$/.test(code) && /"[^"]+"\s*:/.test(code)) {
        return 'json';
    }
    
    // YAML indicators
    if (/^[a-zA-Z_][\w-]*:\s*[^\s]/.test(code) || /^-\s+/.test(code)) {
        return 'yaml';
    }
    
    // Shell/Bash indicators
    if (/^(#!\/bin\/|export |source |npm |pip |docker )/.test(code) || /[\$#]\s/.test(code)) {
        return 'bash';
    }
    
    // SQL indicators
    if (/\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|FROM|WHERE|JOIN)\b/i.test(code)) {
        return 'sql';
    }
    
    return null;
}

/**
 * Generates a markdown table from data
 * 
 * @param {Array<Object>} data - Array of objects representing table rows
 * @param {string[]} columns - Column names (uses object keys if not provided)
 * @param {Object} options - Table formatting options
 * @param {string} options.alignment - 'left' | 'center' | 'right' (default: 'left')
 * @returns {string} Formatted markdown table
 * 
 * @example
 * const data = [
 *   { name: 'John', age: 30, role: 'Developer' },
 *   { name: 'Jane', age: 28, role: 'Designer' }
 * ];
 * const table = generateTable(data, ['name', 'age', 'role']);
 */
function generateTable(data, columns = null, options = {}) {
    try {
        if (!data || data.length === 0) {
            return '> No data to display';
        }
        
        const { alignment = 'left' } = options;
        
        // Determine columns
        const cols = columns || Object.keys(data[0]);
        
        // Calculate column widths
        const widths = cols.map(col => {
            const headerWidth = col.length;
            const dataWidths = data.map(row => {
                const value = row[col]?.toString() || '';
                return value.length;
            });
            return Math.max(headerWidth, ...dataWidths);
        });
        
        // Create alignment markers
        const alignMarker = {
            'left': ':---',
            'center': ':---:',
            'right': '---:'
        }[alignment] || ':---';
        
        // Build header row
        const header = '| ' + cols.map((col, i) => 
            col.padEnd(widths[i])
        ).join(' | ') + ' |';
        
        // Build separator row
        const separator = '| ' + widths.map(width => 
            alignMarker.padEnd(width, '-')
        ).join(' | ') + ' |';
        
        // Build data rows
        const rows = data.map(row => {
            return '| ' + cols.map((col, i) => {
                const value = row[col]?.toString() || '';
                return value.padEnd(widths[i]);
            }).join(' | ') + ' |';
        });
        
        return [header, separator, ...rows].join('\n');
        
    } catch (error) {
        console.error('Error generating table:', error);
        return `> Error generating table: ${error.message}`;
    }
}

/**
 * Cleans up markdown formatting issues
 * 
 * Fixes common markdown issues:
 * - Multiple blank lines
 * - Trailing whitespace
 * - Inconsistent list formatting
 * - Missing blank lines around elements
 * 
 * @param {string} content - Markdown content to clean
 * @returns {string} Cleaned markdown content
 */
function cleanupMarkdown(content) {
    try {
        let cleaned = content;
        
        // Remove trailing whitespace from lines
        cleaned = cleaned.replace(/[ \t]+$/gm, '');
        
        // Collapse multiple blank lines to max 2
        cleaned = cleaned.replace(/\n{4,}/g, '\n\n\n');
        
        // Ensure blank line before lists
        cleaned = cleaned.replace(/([^\n])\n([*\-+]\s)/g, '$1\n\n$2');
        
        // Ensure blank line after lists
        cleaned = cleaned.replace(/([*\-+]\s.+)\n([^\n*\-+])/g, '$1\n\n$2');
        
        // Fix list item spacing (consistent spacing after bullet)
        cleaned = cleaned.replace(/^([*\-+])([^\s])/gm, '$1 $2');
        
        // Ensure single blank line at end of file
        cleaned = cleaned.replace(/\n*$/, '\n');
        
        return cleaned;
        
    } catch (error) {
        console.error('Error cleaning markdown:', error);
        return content;
    }
}

/**
 * Extracts frontmatter from markdown content
 * 
 * @param {string} content - Markdown content with frontmatter
 * @returns {Object} Object with frontmatter and content properties
 */
function extractFrontmatter(content) {
    try {
        const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
        const match = content.match(frontmatterRegex);
        
        if (match) {
            return {
                frontmatter: match[1],
                content: match[2],
                hasFrontmatter: true
            };
        }
        
        return {
            frontmatter: '',
            content: content,
            hasFrontmatter: false
        };
        
    } catch (error) {
        console.error('Error extracting frontmatter:', error);
        return {
            frontmatter: '',
            content: content,
            hasFrontmatter: false
        };
    }
}

/**
 * Counts words in markdown content (excluding frontmatter and code blocks)
 * 
 * @param {string} content - Markdown content
 * @returns {Object} Word count statistics
 */
function countWords(content) {
    try {
        // Remove frontmatter
        const { content: bodyContent } = extractFrontmatter(content);
        
        // Remove code blocks
        const withoutCode = bodyContent.replace(/```[\s\S]*?```/g, '');
        
        // Remove inline code
        const withoutInlineCode = withoutCode.replace(/`[^`]+`/g, '');
        
        // Remove markdown formatting
        const plainText = withoutInlineCode
            .replace(/#{1,6}\s/g, '')        // Remove heading markers
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Extract link text
            .replace(/\[\[([^\]]+)\]\]/g, '$1')      // Extract wiki link text
            .replace(/[*_~]/g, '');          // Remove emphasis markers
        
        // Count words
        const words = plainText.trim().split(/\s+/).filter(word => word.length > 0);
        
        // Estimate reading time (average 200 words per minute)
        const readingTimeMinutes = Math.ceil(words.length / 200);
        
        return {
            words: words.length,
            characters: plainText.length,
            charactersNoSpaces: plainText.replace(/\s/g, '').length,
            readingTime: readingTimeMinutes,
            readingTimeFormatted: readingTimeMinutes === 1 ? '1 minute' : `${readingTimeMinutes} minutes`
        };
        
    } catch (error) {
        console.error('Error counting words:', error);
        return { words: 0, characters: 0, charactersNoSpaces: 0, readingTime: 0 };
    }
}

// Export functions for use in Templater
module.exports = {
    generateTableOfContents,
    createAnchorLink,
    formatHeadings,
    toTitleCase,
    validateLinks,
    formatCodeBlocks,
    detectCodeLanguage,
    generateTable,
    cleanupMarkdown,
    extractFrontmatter,
    countWords
};
