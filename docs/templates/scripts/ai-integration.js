/**
 * AI Integration for Templater
 *
 * Provides AI-powered features for content generation, summarization,
 * keyword extraction, and intelligent document enhancement.
 *
 * @module ai-integration
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 * @requires openai (optional - graceful degradation if not available)
 */

/**
 * Summarizes document content using AI
 *
 * Generates concise summaries of markdown content.
 * Falls back to extractive summary if AI is unavailable.
 *
 * @param {string} content - Document content to summarize
 * @param {number} maxLength - Maximum summary length in words (default: 100)
 * @param {Object} options - AI options
 * @param {string} options.apiKey - OpenAI API key (optional, uses env var if not provided)
 * @param {string} options.model - Model to use (default: 'gpt-4')
 * @returns {Promise<string>} Generated summary
 *
 * @example
 * const summary = await summarizeContent(documentContent, 100);
 */
async function summarizeContent(content, maxLength = 100, options = {}) {
    try {
        const { apiKey = null, model = 'gpt-4' } = options;

        // Remove frontmatter and code blocks for summarization
        let cleanContent = content.replace(/^---[\s\S]*?---\n/, '');
        cleanContent = cleanContent.replace(/```[\s\S]*?```/g, '[CODE BLOCK]');
        cleanContent = cleanContent.replace(/`[^`]+`/g, '[CODE]');

        // Truncate if too long (for API limits)
        const words = cleanContent.split(/\s+/);
        if (words.length > 2000) {
            cleanContent = words.slice(0, 2000).join(' ') + '...';
        }

        // Try AI summarization if API key available
        if (apiKey || process.env.OPENAI_API_KEY) {
            try {
                return await aiSummarize(cleanContent, maxLength, apiKey || process.env.OPENAI_API_KEY, model);
            } catch (aiError) {
                console.warn('AI summarization failed, falling back to extractive method:', aiError.message);
            }
        }

        // Fallback: extractive summarization
        return extractiveSummarize(cleanContent, maxLength);

    } catch (error) {
        console.error('Error summarizing content:', error);
        return 'Summary generation failed. Please check the content and try again.';
    }
}

/**
 * AI-powered summarization using OpenAI
 *
 * @param {string} content - Content to summarize
 * @param {number} maxLength - Max words
 * @param {string} apiKey - OpenAI API key
 * @param {string} model - Model name
 * @returns {Promise<string>} AI-generated summary
 */
async function aiSummarize(content, maxLength, apiKey, model) {
    // Note: This is a placeholder implementation
    // In a real environment, this would make an actual API call to OpenAI
    // For Templater in Obsidian, you'd need to use the fetch API

    const prompt = `Please provide a concise summary of the following technical documentation in approximately ${maxLength} words. Focus on the key concepts, purpose, and main takeaways:\n\n${content}`;

    // Placeholder - would normally call OpenAI API here
    // return await callOpenAI(prompt, apiKey, model);

    // For now, return extractive summary with AI note
    return '> AI summarization requires OpenAI API integration.\n\n' + extractiveSummarize(content, maxLength);
}

/**
 * Extractive summarization (fallback method)
 *
 * Extracts key sentences based on importance scoring.
 *
 * @param {string} content - Content to summarize
 * @param {number} maxLength - Maximum words in summary
 * @returns {string} Extractive summary
 */
function extractiveSummarize(content, maxLength) {
    try {
        // Split into sentences
        const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);

        if (sentences.length === 0) {
            return 'No content available for summarization.';
        }

        // Score sentences by importance
        const scored = sentences.map(sentence => ({
            text: sentence.trim(),
            score: scoreSentence(sentence, content)
        }));

        // Sort by score descending
        scored.sort((a, b) => b.score - a.score);

        // Build summary up to maxLength
        let summary = '';
        let wordCount = 0;

        for (const item of scored) {
            const words = item.text.split(/\s+/);
            if (wordCount + words.length <= maxLength) {
                summary += item.text + '. ';
                wordCount += words.length;
            } else {
                break;
            }
        }

        return summary.trim() || sentences[0].trim() + '.';

    } catch (error) {
        console.error('Error in extractive summarization:', error);
        return 'Summary generation failed.';
    }
}

/**
 * Scores a sentence for importance
 *
 * @param {string} sentence - Sentence to score
 * @param {string} fullContent - Full document content
 * @returns {number} Importance score
 */
function scoreSentence(sentence, fullContent) {
    let score = 0;

    // Position score (earlier sentences weighted higher)
    const position = fullContent.indexOf(sentence);
    const relativePosition = position / fullContent.length;
    if (relativePosition < 0.1) score += 3; // First 10% gets bonus

    // Length score (medium-length sentences preferred)
    const words = sentence.split(/\s+/);
    if (words.length >= 10 && words.length <= 30) score += 2;

    // Keyword score (important words)
    const importantWords = [
        'implement', 'provide', 'enable', 'system', 'module', 'feature',
        'important', 'critical', 'essential', 'key', 'main', 'primary',
        'purpose', 'function', 'responsible', 'manages', 'handles'
    ];

    const lowerSentence = sentence.toLowerCase();
    importantWords.forEach(word => {
        if (lowerSentence.includes(word)) score += 1;
    });

    // Technical term score (capitalized technical terms)
    const techTerms = sentence.match(/\b[A-Z][a-zA-Z]+(?:System|Manager|Service|Interface|Handler)\b/g);
    if (techTerms) score += techTerms.length;

    return score;
}

/**
 * Extracts keywords from document content
 *
 * Uses frequency analysis and TF-IDF-like scoring to identify important keywords.
 *
 * @param {string} content - Document content
 * @param {number} maxKeywords - Maximum keywords to return (default: 10)
 * @param {Object} options - Extraction options
 * @param {string[]} options.stopwords - Additional stopwords to filter
 * @returns {Object[]} Array of keywords with scores
 *
 * @example
 * const keywords = extractKeywords(content, 10);
 * // Returns: [{ keyword: 'ai-systems', score: 15 }, ...]
 */
function extractKeywords(content, maxKeywords = 10, options = {}) {
    try {
        const { stopwords = [] } = options;

        // Default stopwords
        const defaultStopwords = new Set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their'
        ]);

        // Combine stopwords
        stopwords.forEach(word => defaultStopwords.add(word.toLowerCase()));

        // Clean content
        let cleanContent = content.replace(/^---[\s\S]*?---\n/, '');
        cleanContent = cleanContent.replace(/```[\s\S]*?```/g, '');
        cleanContent = cleanContent.replace(/`[^`]+`/g, '');
        cleanContent = cleanContent.replace(/[#*_~\[\]()]/g, '');

        // Tokenize
        const words = cleanContent.toLowerCase().match(/\b\w+(?:-\w+)*\b/g) || [];

        // Count frequencies
        const frequencies = {};
        words.forEach(word => {
            if (!defaultStopwords.has(word) && word.length > 2) {
                frequencies[word] = (frequencies[word] || 0) + 1;
            }
        });

        // Score keywords (frequency + length bonus)
        const scored = Object.entries(frequencies).map(([word, freq]) => ({
            keyword: word,
            score: freq + (word.length > 6 ? 2 : 0)
        }));

        // Sort and return top keywords
        return scored
            .sort((a, b) => b.score - a.score)
            .slice(0, maxKeywords);

    } catch (error) {
        console.error('Error extracting keywords:', error);
        return [];
    }
}

/**
 * Suggests related content based on semantic similarity
 *
 * @param {string} content - Document content
 * @param {Object} app - Obsidian app instance
 * @param {number} maxSuggestions - Maximum suggestions (default: 5)
 * @returns {Object[]} Array of related documents
 */
function suggestRelatedContent(content, app, maxSuggestions = 5) {
    try {
        if (!app || !app.vault) {
            return [];
        }

        // Extract keywords from current content
        const keywords = extractKeywords(content, 20);
        const keywordSet = new Set(keywords.map(k => k.keyword));

        // Get all markdown files
        const allFiles = app.vault.getMarkdownFiles();
        const suggestions = [];

        for (const file of allFiles) {
            const cache = app.metadataCache.getFileCache(file);
            if (!cache) continue;

            // Calculate similarity score
            let score = 0;

            // Check frontmatter tags
            if (cache.frontmatter && cache.frontmatter.tags) {
                const tags = Array.isArray(cache.frontmatter.tags) ?
                    cache.frontmatter.tags : [cache.frontmatter.tags];

                tags.forEach(tag => {
                    if (keywordSet.has(tag.toLowerCase())) {
                        score += 3;
                    }
                });
            }

            // Check headings
            if (cache.headings) {
                cache.headings.forEach(heading => {
                    const headingWords = heading.heading.toLowerCase().split(/\s+/);
                    headingWords.forEach(word => {
                        if (keywordSet.has(word)) {
                            score += 2;
                        }
                    });
                });
            }

            if (score > 0) {
                suggestions.push({
                    file: file.path,
                    name: file.basename,
                    score: score
                });
            }
        }

        return suggestions
            .sort((a, b) => b.score - a.score)
            .slice(0, maxSuggestions);

    } catch (error) {
        console.error('Error suggesting related content:', error);
        return [];
    }
}

/**
 * Generates intelligent tags based on content analysis
 *
 * Combines keyword extraction with domain knowledge to suggest relevant tags.
 *
 * @param {string} content - Document content
 * @param {string} category - Document category
 * @param {number} maxTags - Maximum tags to suggest (default: 10)
 * @returns {string[]} Array of suggested tags
 */
function generateIntelligentTags(content, category, maxTags = 10) {
    try {
        const tags = new Set();

        // Extract keywords
        const keywords = extractKeywords(content, 15);
        keywords.slice(0, 5).forEach(k => tags.add(k.keyword));

        // Technology detection
        const technologies = {
            python: /\b(python|py|pyqt|flask|fastapi|django|pandas|numpy)\b/gi,
            javascript: /\b(javascript|js|node|react|vue|angular|typescript)\b/gi,
            ai: /\b(ai|ml|machine-learning|neural|gpt|llm|openai|model)\b/gi,
            database: /\b(sql|sqlite|postgres|mysql|mongodb|redis|database)\b/gi,
            cloud: /\b(aws|azure|gcp|docker|kubernetes|container|cloud)\b/gi,
            security: /\b(security|auth|encrypt|bcrypt|jwt|oauth|vulnerability)\b/gi
        };

        for (const [tech, pattern] of Object.entries(technologies)) {
            if (pattern.test(content)) {
                tags.add(tech);
            }
        }

        // Category-specific tags
        if (category === 'module-doc') {
            if (/\bclass\s+\w+/gi.test(content)) tags.add('class');
            if (/\bdef\s+\w+/gi.test(content)) tags.add('function');
            if (/\bQWidget|QPushButton|QLabel/gi.test(content)) tags.add('gui');
        } else if (category === 'architecture-doc') {
            if (/\b(pattern|design|architecture)\b/gi.test(content)) tags.add('design-pattern');
            if (/\b(api|endpoint|rest|graphql)\b/gi.test(content)) tags.add('api');
        }

        // Limit and return
        return Array.from(tags).slice(0, maxTags);

    } catch (error) {
        console.error('Error generating intelligent tags:', error);
        return [];
    }
}

/**
 * Generates a document outline using AI or heuristics
 *
 * @param {string} title - Document title
 * @param {string} type - Document type
 * @param {string} description - Brief description
 * @returns {string} Suggested outline in markdown
 */
function generateOutline(title, type, description) {
    try {
        let outline = `# ${title}\n\n`;

        // Type-specific outlines
        if (type === 'module-doc') {
            outline += '## Overview\n\n';
            outline += description + '\n\n';
            outline += '## Architecture\n\n';
            outline += '### Components\n\n';
            outline += '### Dependencies\n\n';
            outline += '## API Reference\n\n';
            outline += '### Classes\n\n';
            outline += '### Functions\n\n';
            outline += '### Constants\n\n';
            outline += '## Implementation Details\n\n';
            outline += '### Design Patterns\n\n';
            outline += '### State Management\n\n';
            outline += '## Usage Examples\n\n';
            outline += '### Basic Usage\n\n';
            outline += '### Advanced Usage\n\n';
            outline += '## Testing\n\n';
            outline += '### Unit Tests\n\n';
            outline += '### Integration Tests\n\n';
            outline += '## Related Documentation\n\n';
        } else if (type === 'architecture-doc') {
            outline += '## Context\n\n';
            outline += description + '\n\n';
            outline += '## Problem Statement\n\n';
            outline += '## Decision\n\n';
            outline += '## Rationale\n\n';
            outline += '## Alternatives Considered\n\n';
            outline += '## Consequences\n\n';
            outline += '### Positive\n\n';
            outline += '### Negative\n\n';
            outline += '## Implementation Notes\n\n';
            outline += '## Related Decisions\n\n';
        } else if (type === 'guide') {
            outline += '## Overview\n\n';
            outline += description + '\n\n';
            outline += '## Prerequisites\n\n';
            outline += '## Getting Started\n\n';
            outline += '### Installation\n\n';
            outline += '### Configuration\n\n';
            outline += '## Step-by-Step Guide\n\n';
            outline += '## Examples\n\n';
            outline += '## Troubleshooting\n\n';
            outline += '## Best Practices\n\n';
            outline += '## Advanced Topics\n\n';
            outline += '## Additional Resources\n\n';
        } else {
            outline += '## Overview\n\n';
            outline += description + '\n\n';
            outline += '## Details\n\n';
            outline += '## Examples\n\n';
            outline += '## References\n\n';
        }

        return outline;

    } catch (error) {
        console.error('Error generating outline:', error);
        return `# ${title}\n\n${description}`;
    }
}

/**
 * Enhances document with AI-generated improvements
 *
 * @param {string} content - Original content
 * @param {Object} options - Enhancement options
 * @returns {Object} Enhanced content with suggestions
 */
function enhanceDocument(content, options = {}) {
    try {
        const enhancements = {
            keywords: extractKeywords(content, 10),
            suggestedTags: generateIntelligentTags(content, options.category || 'guide', 10),
            readability: {
                wordCount: content.split(/\s+/).length,
                sentenceCount: content.split(/[.!?]+/).length,
                avgSentenceLength: Math.round(
                    content.split(/\s+/).length / content.split(/[.!?]+/).length
                )
            },
            improvements: []
        };

        // Check for improvement opportunities
        if (enhancements.readability.avgSentenceLength > 25) {
            enhancements.improvements.push('Consider breaking up long sentences for better readability');
        }

        if (content.split('##').length < 3) {
            enhancements.improvements.push('Add more section headings to improve document structure');
        }

        if (!content.includes('```')) {
            enhancements.improvements.push('Consider adding code examples if applicable');
        }

        return enhancements;

    } catch (error) {
        console.error('Error enhancing document:', error);
        return { error: error.message };
    }
}

// Export functions for use in Templater
module.exports = {
    summarizeContent,
    extractKeywords,
    suggestRelatedContent,
    generateIntelligentTags,
    generateOutline,
    enhanceDocument,
    extractiveSummarize
};
