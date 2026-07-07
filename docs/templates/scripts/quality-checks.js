/**
 * Quality Checks for Templater
 * 
 * Provides validation functions for metadata completeness, tag validation,
 * link integrity checks, and document quality metrics.
 * 
 * @module quality-checks
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Checks metadata completeness against schema requirements
 * 
 * Validates that all required frontmatter fields are present and properly formatted
 * according to the Project-AI metadata schema.
 * 
 * @param {Object} frontmatter - Document frontmatter object
 * @param {string} category - Document category (module-doc, agent-doc, etc.)
 * @returns {Object} Validation result with score, errors, and warnings
 * 
 * @example
 * const result = checkMetadataCompleteness(frontmatter, 'module-doc');
 * // Returns: { score: 85, errors: [], warnings: [...], isComplete: true }
 */
function checkMetadataCompleteness(frontmatter, category) {
    try {
        const errors = [];
        const warnings = [];
        let score = 100;
        
        // Universal required fields
        const universalFields = {
            created: { weight: 15, type: 'date' },
            updated: { weight: 15, type: 'date' },
            type: { weight: 15, type: 'string' },
            status: { weight: 10, type: 'string' },
            tags: { weight: 10, type: 'array' },
            title: { weight: 10, type: 'string' }
        };
        
        // Category-specific required fields
        const categoryFields = {
            'module-doc': {
                module_name: { weight: 10, type: 'string' },
                module_path: { weight: 5, type: 'string' },
                dependencies: { weight: 5, type: 'array' }
            },
            'agent-doc': {
                agent_id: { weight: 10, type: 'string' },
                task_description: { weight: 5, type: 'string' },
                deliverables: { weight: 5, type: 'array' }
            },
            'architecture-doc': {
                decision_number: { weight: 10, type: 'string' },
                context: { weight: 5, type: 'string' },
                consequences: { weight: 5, type: 'string' }
            },
            'guide': {
                difficulty: { weight: 5, type: 'string' },
                prerequisites: { weight: 5, type: 'array' },
                estimated_time: { weight: 5, type: 'string' }
            }
        };
        
        // Check universal fields
        for (const [field, config] of Object.entries(universalFields)) {
            if (!frontmatter[field] || frontmatter[field] === '') {
                errors.push(`Missing required field: ${field}`);
                score -= config.weight;
            } else {
                // Type validation
                const isValid = validateFieldType(frontmatter[field], config.type);
                if (!isValid) {
                    warnings.push(`Field '${field}' has incorrect type (expected: ${config.type})`);
                    score -= config.weight / 2;
                }
            }
        }
        
        // Check category-specific fields
        if (categoryFields[category]) {
            for (const [field, config] of Object.entries(categoryFields[category])) {
                if (!frontmatter[field] || frontmatter[field] === '') {
                    warnings.push(`Recommended field missing: ${field}`);
                    score -= config.weight;
                } else {
                    const isValid = validateFieldType(frontmatter[field], config.type);
                    if (!isValid) {
                        warnings.push(`Field '${field}' has incorrect type (expected: ${config.type})`);
                        score -= config.weight / 2;
                    }
                }
            }
        }
        
        // Ensure score doesn't go negative
        score = Math.max(0, score);
        
        return {
            score: Math.round(score),
            errors: errors,
            warnings: warnings,
            isComplete: errors.length === 0,
            grade: getGrade(score)
        };
        
    } catch (error) {
        console.error('Error checking metadata completeness:', error);
        return {
            score: 0,
            errors: ['Validation failed: ' + error.message],
            warnings: [],
            isComplete: false,
            grade: 'F'
        };
    }
}

/**
 * Validates field type
 * 
 * @param {*} value - Field value
 * @param {string} expectedType - Expected type
 * @returns {boolean} True if type matches
 */
function validateFieldType(value, expectedType) {
    switch (expectedType) {
        case 'string':
            return typeof value === 'string';
        case 'array':
            return Array.isArray(value);
        case 'date':
            // Check if it's a valid date string or Date object
            if (typeof value === 'string') {
                return !isNaN(Date.parse(value));
            }
            return value instanceof Date;
        case 'number':
            return typeof value === 'number';
        case 'boolean':
            return typeof value === 'boolean';
        default:
            return true;
    }
}

/**
 * Converts score to letter grade
 * 
 * @param {number} score - Numeric score (0-100)
 * @returns {string} Letter grade
 */
function getGrade(score) {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
}

/**
 * Validates tags against approved tag taxonomy
 * 
 * @param {string[]} tags - Tags to validate
 * @param {string} category - Document category
 * @returns {Object} Validation result with approved, unknown, and suggestions
 */
function validateTags(tags, category) {
    try {
        // Define approved tag taxonomy
        const approvedTags = {
            'module-doc': [
                'module', 'code', 'api', 'implementation', 'core', 'gui', 'pyqt6',
                'business-logic', 'ai-agent', 'autonomous', 'testing', 'integration'
            ],
            'agent-doc': [
                'agent', 'task', 'execution', 'audit', 'completion', 'deliverables',
                'security', 'vulnerability', 'assessment', 'multi-agent', 'coordination'
            ],
            'architecture-doc': [
                'architecture', 'design', 'system', 'decision', 'adr', 'integration',
                'api', 'external-service', 'pattern', 'reusable', 'best-practice'
            ],
            'guide': [
                'guide', 'documentation', 'reference', 'tutorial', 'onboarding',
                'getting-started', 'runbook', 'problem-solving', 'diagnosis',
                'api', 'developer', 'technical'
            ]
        };
        
        // Common tags across all categories
        const commonTags = [
            'python', 'javascript', 'typescript', 'ai', 'security', 'testing',
            'deployment', 'docker', 'database', 'performance', 'optimization',
            'deprecated', 'experimental', 'production-ready', 'wip'
        ];
        
        const categoryApproved = approvedTags[category] || [];
        const allApproved = [...categoryApproved, ...commonTags];
        
        const approved = [];
        const unknown = [];
        const suggestions = [];
        
        for (const tag of tags) {
            const normalizedTag = tag.toLowerCase().trim();
            
            if (allApproved.includes(normalizedTag)) {
                approved.push(tag);
            } else {
                unknown.push(tag);
                
                // Suggest similar tags
                const similar = findSimilarTags(normalizedTag, allApproved);
                if (similar.length > 0) {
                    suggestions.push({
                        tag: tag,
                        suggestions: similar
                    });
                }
            }
        }
        
        return {
            approved: approved,
            unknown: unknown,
            suggestions: suggestions,
            allValid: unknown.length === 0,
            coverage: tags.length > 0 ? (approved.length / tags.length * 100).toFixed(1) : 0
        };
        
    } catch (error) {
        console.error('Error validating tags:', error);
        return {
            approved: [],
            unknown: tags,
            suggestions: [],
            allValid: false,
            coverage: 0
        };
    }
}

/**
 * Finds similar tags using Levenshtein distance
 * 
 * @param {string} tag - Tag to match
 * @param {string[]} approvedTags - List of approved tags
 * @returns {string[]} Similar tags (max 3)
 */
function findSimilarTags(tag, approvedTags) {
    const similarities = approvedTags.map(approvedTag => ({
        tag: approvedTag,
        distance: levenshteinDistance(tag, approvedTag)
    }));
    
    return similarities
        .filter(s => s.distance <= 3) // Max 3 character difference
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 3)
        .map(s => s.tag);
}

/**
 * Calculates Levenshtein distance between two strings
 * 
 * @param {string} a - First string
 * @param {string} b - Second string
 * @returns {number} Edit distance
 */
function levenshteinDistance(a, b) {
    const matrix = [];
    
    for (let i = 0; i <= b.length; i++) {
        matrix[i] = [i];
    }
    
    for (let j = 0; j <= a.length; j++) {
        matrix[0][j] = j;
    }
    
    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // substitution
                    matrix[i][j - 1] + 1,     // insertion
                    matrix[i - 1][j] + 1      // deletion
                );
            }
        }
    }
    
    return matrix[b.length][a.length];
}

/**
 * Checks link integrity (broken links, missing files)
 * 
 * @param {string} content - Document content
 * @param {Object} app - Obsidian app instance
 * @returns {Object} Link integrity report
 */
function checkLinkIntegrity(content, app) {
    try {
        const broken = [];
        const valid = [];
        const external = [];
        
        if (!app || !app.vault) {
            return {
                broken: [],
                valid: [],
                external: [],
                totalLinks: 0,
                integrityScore: 0,
                checked: false
            };
        }
        
        // Check wiki links [[link]]
        const wikiLinkRegex = /\[\[([^\]]+)\]\]/g;
        let match;
        
        while ((match = wikiLinkRegex.exec(content)) !== null) {
            const linkText = match[1];
            const linkPath = linkText.split('|')[0].split('#')[0].trim();
            
            const file = app.metadataCache.getFirstLinkpathDest(linkPath, '');
            
            if (file) {
                valid.push({
                    type: 'wiki',
                    link: linkText,
                    path: file.path
                });
            } else {
                broken.push({
                    type: 'wiki',
                    link: linkText,
                    reason: 'File not found'
                });
            }
        }
        
        // Check markdown links [text](url)
        const mdLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        
        while ((match = mdLinkRegex.exec(content)) !== null) {
            const text = match[1];
            const url = match[2];
            
            if (url.startsWith('http://') || url.startsWith('https://')) {
                external.push({
                    type: 'external',
                    text: text,
                    url: url
                });
            } else {
                const file = app.vault.getAbstractFileByPath(url);
                
                if (file) {
                    valid.push({
                        type: 'markdown',
                        text: text,
                        path: url
                    });
                } else {
                    broken.push({
                        type: 'markdown',
                        text: text,
                        path: url,
                        reason: 'File not found'
                    });
                }
            }
        }
        
        const totalInternal = valid.length + broken.length;
        const integrityScore = totalInternal > 0 ? 
            Math.round((valid.length / totalInternal) * 100) : 100;
        
        return {
            broken: broken,
            valid: valid,
            external: external,
            totalLinks: totalInternal + external.length,
            integrityScore: integrityScore,
            checked: true
        };
        
    } catch (error) {
        console.error('Error checking link integrity:', error);
        return {
            broken: [],
            valid: [],
            external: [],
            totalLinks: 0,
            integrityScore: 0,
            checked: false
        };
    }
}

/**
 * Calculates readability metrics for document content
 * 
 * Uses Flesch Reading Ease and other readability formulas.
 * 
 * @param {string} content - Document content (without frontmatter)
 * @returns {Object} Readability metrics
 */
function calculateReadability(content) {
    try {
        // Remove code blocks and inline code
        let text = content.replace(/```[\s\S]*?```/g, '');
        text = text.replace(/`[^`]+`/g, '');
        
        // Remove markdown formatting
        text = text.replace(/#{1,6}\s/g, '');
        text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
        text = text.replace(/\[\[([^\]]+)\]\]/g, '$1');
        text = text.replace(/[*_~]/g, '');
        
        // Count sentences
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        const sentenceCount = sentences.length;
        
        // Count words
        const words = text.split(/\s+/).filter(w => w.length > 0);
        const wordCount = words.length;
        
        // Count syllables (approximate)
        let syllableCount = 0;
        words.forEach(word => {
            syllableCount += countSyllables(word);
        });
        
        // Calculate Flesch Reading Ease
        // Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        let fleschScore = 0;
        if (sentenceCount > 0 && wordCount > 0) {
            fleschScore = 206.835 - 
                1.015 * (wordCount / sentenceCount) - 
                84.6 * (syllableCount / wordCount);
            fleschScore = Math.max(0, Math.min(100, fleschScore)); // Clamp to 0-100
        }
        
        // Interpret Flesch score
        let readingLevel;
        if (fleschScore >= 90) readingLevel = 'Very Easy (5th grade)';
        else if (fleschScore >= 80) readingLevel = 'Easy (6th grade)';
        else if (fleschScore >= 70) readingLevel = 'Fairly Easy (7th grade)';
        else if (fleschScore >= 60) readingLevel = 'Standard (8th-9th grade)';
        else if (fleschScore >= 50) readingLevel = 'Fairly Difficult (10th-12th grade)';
        else if (fleschScore >= 30) readingLevel = 'Difficult (College)';
        else readingLevel = 'Very Difficult (Professional)';
        
        // Calculate average sentence length
        const avgSentenceLength = sentenceCount > 0 ? 
            Math.round(wordCount / sentenceCount) : 0;
        
        // Calculate average word length
        const totalChars = words.join('').length;
        const avgWordLength = wordCount > 0 ? 
            (totalChars / wordCount).toFixed(1) : 0;
        
        return {
            wordCount: wordCount,
            sentenceCount: sentenceCount,
            syllableCount: syllableCount,
            avgSentenceLength: avgSentenceLength,
            avgWordLength: avgWordLength,
            fleschScore: Math.round(fleschScore),
            readingLevel: readingLevel,
            estimatedReadingTime: Math.ceil(wordCount / 200) // 200 wpm
        };
        
    } catch (error) {
        console.error('Error calculating readability:', error);
        return {
            wordCount: 0,
            sentenceCount: 0,
            syllableCount: 0,
            avgSentenceLength: 0,
            avgWordLength: 0,
            fleschScore: 0,
            readingLevel: 'Unknown',
            estimatedReadingTime: 0
        };
    }
}

/**
 * Counts syllables in a word (approximate)
 * 
 * @param {string} word - Word to analyze
 * @returns {number} Syllable count
 */
function countSyllables(word) {
    word = word.toLowerCase().replace(/[^a-z]/g, '');
    if (word.length <= 3) return 1;
    
    // Count vowel groups
    const vowelGroups = word.match(/[aeiouy]+/g);
    let count = vowelGroups ? vowelGroups.length : 1;
    
    // Adjust for silent e
    if (word.endsWith('e')) count--;
    
    // Ensure at least one syllable
    return Math.max(1, count);
}

/**
 * Performs comprehensive document quality check
 * 
 * Combines all quality metrics into a single overall score.
 * 
 * @param {Object} frontmatter - Document frontmatter
 * @param {string} content - Document content
 * @param {string} category - Document category
 * @param {Object} app - Obsidian app instance
 * @returns {Object} Comprehensive quality report
 */
function comprehensiveQualityCheck(frontmatter, content, category, app) {
    try {
        // Run all checks
        const metadata = checkMetadataCompleteness(frontmatter, category);
        const tags = validateTags(frontmatter.tags || [], category);
        const links = checkLinkIntegrity(content, app);
        const readability = calculateReadability(content);
        
        // Calculate overall quality score (weighted average)
        const weights = {
            metadata: 0.30,      // 30% weight
            tags: 0.15,          // 15% weight
            links: 0.20,         // 20% weight
            content: 0.20,       // 20% weight (word count)
            readability: 0.15    // 15% weight
        };
        
        // Minimum word counts by category
        const minWords = {
            'module-doc': 1000,
            'agent-doc': 500,
            'architecture-doc': 1500,
            'guide': 800
        };
        
        const requiredWords = minWords[category] || 500;
        const contentScore = Math.min(100, (readability.wordCount / requiredWords) * 100);
        
        const readabilityScore = readability.fleschScore;
        
        const overallScore = Math.round(
            metadata.score * weights.metadata +
            parseFloat(tags.coverage) * weights.tags +
            links.integrityScore * weights.links +
            contentScore * weights.content +
            readabilityScore * weights.readability
        );
        
        return {
            overallScore: overallScore,
            grade: getGrade(overallScore),
            metadata: metadata,
            tags: tags,
            links: links,
            readability: readability,
            recommendations: generateRecommendations(
                metadata, tags, links, readability, category
            )
        };
        
    } catch (error) {
        console.error('Error in comprehensive quality check:', error);
        return {
            overallScore: 0,
            grade: 'F',
            error: error.message
        };
    }
}

/**
 * Generates actionable recommendations based on quality check results
 * 
 * @param {Object} metadata - Metadata check results
 * @param {Object} tags - Tag validation results
 * @param {Object} links - Link integrity results
 * @param {Object} readability - Readability metrics
 * @param {string} category - Document category
 * @returns {string[]} Array of recommendations
 */
function generateRecommendations(metadata, tags, links, readability, category) {
    const recommendations = [];
    
    // Metadata recommendations
    if (metadata.errors.length > 0) {
        recommendations.push(`🔴 CRITICAL: Fix ${metadata.errors.length} metadata errors`);
    }
    if (metadata.warnings.length > 0) {
        recommendations.push(`⚠️ Add ${metadata.warnings.length} recommended metadata fields`);
    }
    
    // Tag recommendations
    if (tags.unknown.length > 0) {
        recommendations.push(`🏷️ Review ${tags.unknown.length} non-standard tags`);
    }
    if (tags.suggestions.length > 0) {
        recommendations.push(`💡 Consider suggested tag alternatives`);
    }
    
    // Link recommendations
    if (links.broken.length > 0) {
        recommendations.push(`🔗 Fix ${links.broken.length} broken links`);
    }
    
    // Content recommendations
    const minWords = {
        'module-doc': 1000,
        'agent-doc': 500,
        'architecture-doc': 1500,
        'guide': 800
    };
    
    const required = minWords[category] || 500;
    if (readability.wordCount < required) {
        const needed = required - readability.wordCount;
        recommendations.push(`📝 Add ~${needed} more words to meet minimum (${required})`);
    }
    
    // Readability recommendations
    if (readability.avgSentenceLength > 25) {
        recommendations.push(`✂️ Consider breaking up long sentences (avg: ${readability.avgSentenceLength} words)`);
    }
    
    if (readability.fleschScore < 30) {
        recommendations.push(`📖 Content may be too complex - consider simplifying`);
    }
    
    if (recommendations.length === 0) {
        recommendations.push('✅ Document meets all quality standards!');
    }
    
    return recommendations;
}

// Export functions for use in Templater
module.exports = {
    checkMetadataCompleteness,
    validateTags,
    checkLinkIntegrity,
    calculateReadability,
    comprehensiveQualityCheck,
    generateRecommendations,
    getGrade,
    countSyllables
};
