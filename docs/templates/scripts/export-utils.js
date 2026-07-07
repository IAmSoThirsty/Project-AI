/**
 * Export Utilities for Templater
 * 
 * Provides helpers for preparing documents for export to various formats
 * including PDF, HTML, and clean markdown.
 * 
 * @module export-utils
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Prepares document for PDF export
 * 
 * Optimizes markdown for PDF conversion by:
 * - Removing Obsidian-specific syntax
 * - Converting wiki links to standard markdown
 * - Adding page breaks
 * - Formatting tables for print
 * 
 * @param {string} content - Original markdown content
 * @param {Object} options - Export options
 * @param {boolean} options.includeTableOfContents - Add TOC (default: true)
 * @param {boolean} options.pageBreaks - Add page breaks at headings (default: true)
 * @param {string} options.pageBreakLevel - Heading level for breaks: 'h1' | 'h2' (default: 'h1')
 * @param {boolean} options.removeComments - Remove HTML comments (default: true)
 * @returns {string} PDF-optimized markdown
 * 
 * @example
 * const pdfContent = preparePDFExport(content, {
 *   includeTableOfContents: true,
 *   pageBreaks: true,
 *   pageBreakLevel: 'h1'
 * });
 */
function preparePDFExport(content, options = {}) {
    try {
        const {
            includeTableOfContents = true,
            pageBreaks = true,
            pageBreakLevel = 'h1',
            removeComments = true
        } = options;
        
        let output = content;
        
        // Remove frontmatter
        output = output.replace(/^---[\s\S]*?---\n/m, '');
        
        // Convert wiki links to standard markdown
        // [[Page]] => [Page](Page.md)
        // [[Page|Alias]] => [Alias](Page.md)
        output = output.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, page, alias) => {
            const linkText = alias || page;
            return `[${linkText}](${page}.md)`;
        });
        
        // Remove Obsidian tags (convert #tag to **tag**)
        output = output.replace(/#([\w-]+)/g, '**$1**');
        
        // Remove Obsidian callouts and convert to blockquotes
        output = output.replace(/^>\s*\[!(\w+)\]\s*(.*)$/gm, (match, type, text) => {
            return `> **${type.toUpperCase()}:** ${text}`;
        });
        
        // Remove HTML comments if requested
        if (removeComments) {
            output = output.replace(/<!--[\s\S]*?-->/g, '');
        }
        
        // Remove embedded queries (Dataview, etc.)
        output = output.replace(/```dataview[\s\S]*?```/g, '');
        output = output.replace(/```query[\s\S]*?```/g, '');
        
        // Add page breaks at specified heading level
        if (pageBreaks) {
            const breakPattern = pageBreakLevel === 'h1' ? /^# /gm : /^## /gm;
            output = output.replace(breakPattern, '\n<div style="page-break-before: always;"></div>\n\n$&');
        }
        
        // Insert table of contents if requested
        if (includeTableOfContents) {
            const toc = generateSimpleTOC(output);
            output = toc + '\n\n' + output;
        }
        
        // Optimize tables for print (ensure they don't overflow)
        output = output.replace(/\|(.+)\|/g, (match) => {
            // Add word-wrap hints for long table cells
            return match.replace(/\s{2,}/g, ' ');
        });
        
        return output;
        
    } catch (error) {
        console.error('Error preparing PDF export:', error);
        return content;
    }
}

/**
 * Generates a simple table of contents
 * 
 * @param {string} content - Markdown content
 * @returns {string} TOC markdown
 */
function generateSimpleTOC(content) {
    try {
        const headingRegex = /^(#{1,3})\s+(.+)$/gm;
        const headings = [];
        let match;
        
        while ((match = headingRegex.exec(content)) !== null) {
            const level = match[1].length;
            const text = match[2].trim();
            
            headings.push({
                level: level,
                text: text,
                anchor: text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-')
            });
        }
        
        if (headings.length === 0) {
            return '';
        }
        
        let toc = '## Table of Contents\n\n';
        
        headings.forEach(heading => {
            const indent = '  '.repeat(heading.level - 1);
            toc += `${indent}- [${heading.text}](#${heading.anchor})\n`;
        });
        
        return toc;
        
    } catch (error) {
        console.error('Error generating TOC:', error);
        return '';
    }
}

/**
 * Prepares document for HTML export
 * 
 * @param {string} content - Original markdown content
 * @param {Object} options - Export options
 * @param {string} options.cssFramework - CSS framework: 'none' | 'bootstrap' | 'tailwind'
 * @param {boolean} options.syntaxHighlighting - Enable syntax highlighting (default: true)
 * @param {boolean} options.responsiveImages - Make images responsive (default: true)
 * @param {Object} options.metadata - Document metadata for HTML head
 * @returns {string} HTML-ready markdown
 */
function prepareHTMLExport(content, options = {}) {
    try {
        const {
            cssFramework = 'none',
            syntaxHighlighting = true,
            responsiveImages = true,
            metadata = {}
        } = options;
        
        let output = content;
        
        // Remove frontmatter but save metadata
        const frontmatterMatch = output.match(/^---\n([\s\S]*?)\n---\n/);
        if (frontmatterMatch) {
            output = output.replace(/^---[\s\S]*?---\n/, '');
        }
        
        // Convert wiki links to standard links
        output = output.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, page, alias) => {
            const linkText = alias || page;
            return `[${linkText}](${page}.html)`;
        });
        
        // Add classes to code blocks for syntax highlighting
        if (syntaxHighlighting) {
            output = output.replace(/```(\w+)/g, (match, lang) => {
                return `\`\`\`${lang} {.language-${lang}}`;
            });
        }
        
        // Make images responsive
        if (responsiveImages) {
            output = output.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
                if (cssFramework === 'bootstrap') {
                    return `<img src="${src}" alt="${alt}" class="img-fluid">`;
                } else if (cssFramework === 'tailwind') {
                    return `<img src="${src}" alt="${alt}" class="max-w-full h-auto">`;
                } else {
                    return `<img src="${src}" alt="${alt}" style="max-width: 100%; height: auto;">`;
                }
            });
        }
        
        // Add framework-specific classes to elements
        if (cssFramework === 'bootstrap') {
            // Add Bootstrap table classes
            output = output.replace(/<table>/g, '<table class="table table-striped table-bordered">');
            
            // Add Bootstrap button classes to links that look like buttons
            output = output.replace(/\[([^\]]+)\]\(([^)]+)\)\s*{\.btn}/g, 
                '<a href="$2" class="btn btn-primary">$1</a>');
        } else if (cssFramework === 'tailwind') {
            // Add Tailwind table classes
            output = output.replace(/<table>/g, '<table class="min-w-full divide-y divide-gray-200">');
        }
        
        // Remove Obsidian-specific syntax
        output = output.replace(/```dataview[\s\S]*?```/g, '');
        output = output.replace(/```query[\s\S]*?```/g, '');
        
        return output;
        
    } catch (error) {
        console.error('Error preparing HTML export:', error);
        return content;
    }
}

/**
 * Cleans markdown for universal compatibility
 * 
 * Removes all platform-specific syntax and normalizes formatting.
 * 
 * @param {string} content - Original markdown content
 * @param {Object} options - Cleanup options
 * @param {boolean} options.removeFrontmatter - Remove YAML frontmatter (default: true)
 * @param {boolean} options.convertWikiLinks - Convert to standard markdown links (default: true)
 * @param {boolean} options.removeComments - Remove HTML comments (default: true)
 * @param {boolean} options.normalizeWhitespace - Normalize line endings and spacing (default: true)
 * @returns {string} Clean markdown
 */
function cleanMarkdown(content, options = {}) {
    try {
        const {
            removeFrontmatter = true,
            convertWikiLinks = true,
            removeComments = true,
            normalizeWhitespace = true
        } = options;
        
        let output = content;
        
        // Remove frontmatter
        if (removeFrontmatter) {
            output = output.replace(/^---[\s\S]*?---\n/m, '');
        }
        
        // Convert wiki links
        if (convertWikiLinks) {
            output = output.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, page, alias) => {
                const linkText = alias || page;
                return `[${linkText}](${page})`;
            });
        }
        
        // Remove HTML comments
        if (removeComments) {
            output = output.replace(/<!--[\s\S]*?-->/g, '');
        }
        
        // Remove Obsidian callouts (convert to blockquotes)
        output = output.replace(/^>\s*\[!(\w+)\]\s*(.*)$/gm, '> $2');
        
        // Remove Obsidian tags
        output = output.replace(/#([\w-]+)(?=\s|$)/g, '');
        
        // Remove embedded queries
        output = output.replace(/```(?:dataview|query)[\s\S]*?```/g, '');
        
        // Remove empty links
        output = output.replace(/\[\]\([^)]*\)/g, '');
        
        // Normalize whitespace
        if (normalizeWhitespace) {
            // Normalize line endings to \n
            output = output.replace(/\r\n/g, '\n');
            output = output.replace(/\r/g, '\n');
            
            // Remove trailing whitespace from lines
            output = output.replace(/[ \t]+$/gm, '');
            
            // Collapse multiple blank lines to maximum 2
            output = output.replace(/\n{4,}/g, '\n\n\n');
            
            // Ensure single newline at end of file
            output = output.replace(/\n*$/, '\n');
        }
        
        return output;
        
    } catch (error) {
        console.error('Error cleaning markdown:', error);
        return content;
    }
}

/**
 * Generates a standalone HTML document
 * 
 * @param {string} markdownContent - Markdown content
 * @param {Object} options - HTML generation options
 * @param {string} options.title - Document title
 * @param {string} options.cssUrl - URL to CSS stylesheet
 * @param {string} options.inlineCSS - Inline CSS to include
 * @param {boolean} options.includeMarkdownConverter - Include markdown-to-HTML script (default: false)
 * @returns {string} Complete HTML document
 */
function generateStandaloneHTML(markdownContent, options = {}) {
    try {
        const {
            title = 'Document',
            cssUrl = null,
            inlineCSS = null,
            includeMarkdownConverter = false
        } = options;
        
        // Prepare markdown
        const cleanedMarkdown = prepareHTMLExport(markdownContent, options);
        
        // Build HTML
        let html = '<!DOCTYPE html>\n';
        html += '<html lang="en">\n';
        html += '<head>\n';
        html += '  <meta charset="UTF-8">\n';
        html += '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
        html += `  <title>${escapeHTML(title)}</title>\n`;
        
        // Add CSS
        if (cssUrl) {
            html += `  <link rel="stylesheet" href="${cssUrl}">\n`;
        }
        
        if (inlineCSS) {
            html += '  <style>\n';
            html += inlineCSS;
            html += '\n  </style>\n';
        } else {
            // Default minimal styling
            html += '  <style>\n';
            html += '    body { max-width: 800px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; }\n';
            html += '    code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }\n';
            html += '    pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }\n';
            html += '    table { border-collapse: collapse; width: 100%; margin: 20px 0; }\n';
            html += '    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n';
            html += '    th { background: #f4f4f4; }\n';
            html += '    blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 16px; color: #666; }\n';
            html += '  </style>\n';
        }
        
        html += '</head>\n';
        html += '<body>\n';
        html += '  <article>\n';
        
        if (includeMarkdownConverter) {
            html += '  <div id="content">';
            html += escapeHTML(cleanedMarkdown);
            html += '</div>\n';
            
            // Note: In a real implementation, you'd include a markdown-to-HTML converter
            html += '  <script>\n';
            html += '    // Markdown converter would go here (e.g., marked.js)\n';
            html += '    console.log("Markdown converter not included in this build");\n';
            html += '  </script>\n';
        } else {
            html += '  <!-- Markdown content (convert to HTML before use) -->\n';
            html += '  <pre><code>';
            html += escapeHTML(cleanedMarkdown);
            html += '</code></pre>\n';
        }
        
        html += '  </article>\n';
        html += '</body>\n';
        html += '</html>';
        
        return html;
        
    } catch (error) {
        console.error('Error generating standalone HTML:', error);
        return '<html><body><h1>Error generating HTML</h1></body></html>';
    }
}

/**
 * Escapes HTML special characters
 * 
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHTML(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    
    return text.replace(/[&<>"']/g, char => map[char]);
}

/**
 * Exports document as plain text with optional formatting
 * 
 * @param {string} content - Markdown content
 * @param {Object} options - Export options
 * @param {number} options.lineWidth - Maximum line width (default: 80)
 * @param {boolean} options.preserveHeadings - Keep heading markers (default: true)
 * @param {boolean} options.preserveLists - Keep list markers (default: true)
 * @returns {string} Plain text content
 */
function exportPlainText(content, options = {}) {
    try {
        const {
            lineWidth = 80,
            preserveHeadings = true,
            preserveLists = true
        } = options;
        
        let output = content;
        
        // Remove frontmatter
        output = output.replace(/^---[\s\S]*?---\n/m, '');
        
        // Remove code blocks (or extract just the content)
        output = output.replace(/```[\s\S]*?```/g, '');
        
        // Remove inline code markers
        output = output.replace(/`([^`]+)`/g, '$1');
        
        // Convert wiki links to plain text
        output = output.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, page, alias) => {
            return alias || page;
        });
        
        // Convert markdown links to plain text
        output = output.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
        
        // Remove images
        output = output.replace(/!\[([^\]]*)\]\([^)]+\)/g, '[Image: $1]');
        
        // Handle headings
        if (preserveHeadings) {
            output = output.replace(/^(#{1,6})\s+(.+)$/gm, (match, hashes, text) => {
                const level = hashes.length;
                const underline = '='.repeat(text.length);
                return `\n${text}\n${underline}\n`;
            });
        } else {
            output = output.replace(/^#{1,6}\s+/gm, '');
        }
        
        // Remove emphasis markers if not preserving
        output = output.replace(/\*\*([^*]+)\*\*/g, '$1'); // bold
        output = output.replace(/\*([^*]+)\*/g, '$1');     // italic
        output = output.replace(/__([^_]+)__/g, '$1');     // bold
        output = output.replace(/_([^_]+)_/g, '$1');       // italic
        
        // Handle lists
        if (!preserveLists) {
            output = output.replace(/^[\s]*[-*+]\s+/gm, '');
            output = output.replace(/^[\s]*\d+\.\s+/gm, '');
        }
        
        // Wrap lines to specified width
        if (lineWidth > 0) {
            output = wrapText(output, lineWidth);
        }
        
        return output;
        
    } catch (error) {
        console.error('Error exporting plain text:', error);
        return content;
    }
}

/**
 * Wraps text to specified line width
 * 
 * @param {string} text - Text to wrap
 * @param {number} width - Maximum line width
 * @returns {string} Wrapped text
 */
function wrapText(text, width) {
    const lines = text.split('\n');
    const wrapped = [];
    
    lines.forEach(line => {
        if (line.length <= width || line.trim() === '') {
            wrapped.push(line);
            return;
        }
        
        const words = line.split(' ');
        let currentLine = '';
        
        words.forEach(word => {
            if ((currentLine + word).length <= width) {
                currentLine += (currentLine ? ' ' : '') + word;
            } else {
                if (currentLine) wrapped.push(currentLine);
                currentLine = word;
            }
        });
        
        if (currentLine) wrapped.push(currentLine);
    });
    
    return wrapped.join('\n');
}

/**
 * Generates export metadata summary
 * 
 * @param {Object} frontmatter - Document frontmatter
 * @returns {string} Metadata summary in markdown
 */
function generateExportMetadata(frontmatter) {
    try {
        let metadata = '---\n\n';
        metadata += '**Document Information**\n\n';
        
        if (frontmatter.title) {
            metadata += `- **Title:** ${frontmatter.title}\n`;
        }
        
        if (frontmatter.author || frontmatter.created_by) {
            metadata += `- **Author:** ${frontmatter.author || frontmatter.created_by}\n`;
        }
        
        if (frontmatter.created) {
            metadata += `- **Created:** ${frontmatter.created}\n`;
        }
        
        if (frontmatter.updated) {
            metadata += `- **Last Updated:** ${frontmatter.updated}\n`;
        }
        
        if (frontmatter.version) {
            metadata += `- **Version:** ${frontmatter.version}\n`;
        }
        
        if (frontmatter.status) {
            metadata += `- **Status:** ${frontmatter.status}\n`;
        }
        
        if (frontmatter.tags && frontmatter.tags.length > 0) {
            metadata += `- **Tags:** ${frontmatter.tags.join(', ')}\n`;
        }
        
        metadata += '\n---\n\n';
        
        return metadata;
        
    } catch (error) {
        console.error('Error generating export metadata:', error);
        return '';
    }
}

// Export functions for use in Templater
module.exports = {
    preparePDFExport,
    prepareHTMLExport,
    cleanMarkdown,
    generateStandaloneHTML,
    exportPlainText,
    generateExportMetadata,
    escapeHTML,
    wrapText
};
