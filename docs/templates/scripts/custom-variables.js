/**
 * Custom Variables for Templater
 * 
 * Provides Project-AI specific custom variables, context information,
 * user preferences, and dynamic calculations for use in templates.
 * 
 * @module custom-variables
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Project-AI context variables
 * 
 * Provides project-specific information and constants.
 */
const PROJECT_CONTEXT = {
    name: 'Project-AI',
    fullName: 'Project-AI: Self-Aware AI Assistant',
    version: '2.0.0',
    repository: 'https://github.com/yourusername/Project-AI',
    documentation: 'https://project-ai.docs.example.com',
    license: 'MIT',
    
    // Core technologies
    technologies: {
        backend: ['Python 3.11+', 'PyQt6', 'OpenAI API', 'scikit-learn'],
        frontend: ['React 18', 'Vite', 'Zustand'],
        deployment: ['Docker', 'Docker Compose'],
        testing: ['pytest', 'Jest']
    },
    
    // Module paths
    paths: {
        root: 'T:\\Project-AI-main',
        src: 'T:\\Project-AI-main\\src',
        core: 'T:\\Project-AI-main\\src\\app\\core',
        gui: 'T:\\Project-AI-main\\src\\app\\gui',
        agents: 'T:\\Project-AI-main\\src\\app\\agents',
        web: 'T:\\Project-AI-main\\web'
    },
    
    // Core systems
    coreSystems: [
        'FourLaws (Ethics)',
        'AIPersona (Personality)',
        'MemoryExpansionSystem',
        'LearningRequestManager',
        'CommandOverride',
        'PluginManager'
    ],
    
    // AI agents
    agents: [
        'Oversight',
        'Planner',
        'Validator',
        'Explainability'
    ]
};

/**
 * Gets current project context
 * 
 * @returns {Object} Project context object
 */
function getProjectContext() {
    return PROJECT_CONTEXT;
}

/**
 * Gets context variable by key
 * 
 * @param {string} key - Context key (dot notation supported)
 * @returns {*} Context value or null if not found
 * 
 * @example
 * getContextVariable('technologies.backend') // Returns array of backend technologies
 * getContextVariable('version') // Returns "2.0.0"
 */
function getContextVariable(key) {
    try {
        const keys = key.split('.');
        let value = PROJECT_CONTEXT;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return null;
            }
        }
        
        return value;
        
    } catch (error) {
        console.error('Error getting context variable:', error);
        return null;
    }
}

/**
 * User preferences (can be customized per installation)
 */
const USER_PREFERENCES = {
    // Author information
    author: {
        name: 'Documentation Team',
        email: 'docs@project-ai.example.com',
        organization: 'Project-AI'
    },
    
    // Documentation preferences
    documentation: {
        defaultLanguage: 'en',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: 'HH:mm:ss',
        timezone: 'UTC',
        includeTimestamps: true,
        includeAuthorInfo: true
    },
    
    // Template preferences
    templates: {
        autoGenerateTOC: true,
        autoGenerateAliases: true,
        autoSuggestTags: true,
        minWordCount: 500,
        defaultStatus: 'draft'
    },
    
    // Quality preferences
    quality: {
        enforceMetadataCompleteness: true,
        enforceLinkIntegrity: false,
        enforceReadability: false,
        minReadabilityScore: 50
    },
    
    // Git preferences
    git: {
        autoCommit: false,
        commitMessageStyle: 'conventional',
        branchNamingConvention: 'feature/scope/description'
    }
};

/**
 * Gets user preference by key
 * 
 * @param {string} key - Preference key (dot notation supported)
 * @param {*} defaultValue - Default value if preference not found
 * @returns {*} Preference value or default
 * 
 * @example
 * getUserPreference('author.name', 'Unknown') // Returns author name or 'Unknown'
 */
function getUserPreference(key, defaultValue = null) {
    try {
        const keys = key.split('.');
        let value = USER_PREFERENCES;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value;
        
    } catch (error) {
        console.error('Error getting user preference:', error);
        return defaultValue;
    }
}

/**
 * Sets user preference (runtime only - not persisted)
 * 
 * @param {string} key - Preference key (dot notation supported)
 * @param {*} value - Preference value
 * @returns {boolean} Success status
 */
function setUserPreference(key, value) {
    try {
        const keys = key.split('.');
        const lastKey = keys.pop();
        let obj = USER_PREFERENCES;
        
        for (const k of keys) {
            if (!(k in obj)) {
                obj[k] = {};
            }
            obj = obj[k];
        }
        
        obj[lastKey] = value;
        return true;
        
    } catch (error) {
        console.error('Error setting user preference:', error);
        return false;
    }
}

/**
 * Calculates documentation progress statistics
 * 
 * @param {Object} app - Obsidian app instance
 * @returns {Object} Progress statistics
 */
function calculateDocProgress(app) {
    try {
        if (!app || !app.vault) {
            return {
                total: 0,
                byStatus: {},
                byCategory: {},
                completionRate: 0
            };
        }
        
        const files = app.vault.getMarkdownFiles();
        const stats = {
            total: files.length,
            byStatus: {},
            byCategory: {},
            completionRate: 0
        };
        
        let completed = 0;
        
        files.forEach(file => {
            const cache = app.metadataCache.getFileCache(file);
            if (!cache || !cache.frontmatter) return;
            
            const status = cache.frontmatter.status || 'unknown';
            const category = cache.frontmatter.category || 'uncategorized';
            
            stats.byStatus[status] = (stats.byStatus[status] || 0) + 1;
            stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
            
            if (status === 'published' || status === 'completed') {
                completed++;
            }
        });
        
        stats.completionRate = stats.total > 0 ? 
            Math.round((completed / stats.total) * 100) : 0;
        
        return stats;
        
    } catch (error) {
        console.error('Error calculating documentation progress:', error);
        return {
            total: 0,
            byStatus: {},
            byCategory: {},
            completionRate: 0
        };
    }
}

/**
 * Generates a unique document ID
 * 
 * @param {string} prefix - ID prefix (default: 'doc')
 * @param {boolean} includeTimestamp - Include timestamp in ID (default: true)
 * @returns {string} Unique document ID
 * 
 * @example
 * generateDocumentID('module') // Returns: "module-1713628800000-a1b2"
 */
function generateDocumentID(prefix = 'doc', includeTimestamp = true) {
    try {
        const timestamp = includeTimestamp ? Date.now() : '';
        const random = Math.random().toString(36).substring(2, 6);
        
        return `${prefix}-${timestamp}${timestamp ? '-' : ''}${random}`;
        
    } catch (error) {
        console.error('Error generating document ID:', error);
        return `${prefix}-${Date.now()}`;
    }
}

/**
 * Calculates estimated reading time
 * 
 * @param {string} content - Document content
 * @param {number} wordsPerMinute - Reading speed (default: 200)
 * @returns {Object} Reading time information
 * 
 * @example
 * const readingTime = calculateReadingTime(content);
 * // Returns: { minutes: 5, formatted: "5 minute read" }
 */
function calculateReadingTime(content, wordsPerMinute = 200) {
    try {
        // Remove frontmatter and code blocks
        let cleanContent = content.replace(/^---[\s\S]*?---\n/, '');
        cleanContent = cleanContent.replace(/```[\s\S]*?```/g, '');
        
        // Count words
        const words = cleanContent.split(/\s+/).filter(w => w.length > 0);
        const wordCount = words.length;
        
        // Calculate time
        const minutes = Math.ceil(wordCount / wordsPerMinute);
        
        let formatted;
        if (minutes < 1) {
            formatted = 'Less than 1 minute read';
        } else if (minutes === 1) {
            formatted = '1 minute read';
        } else {
            formatted = `${minutes} minute read`;
        }
        
        return {
            words: wordCount,
            minutes: minutes,
            formatted: formatted
        };
        
    } catch (error) {
        console.error('Error calculating reading time:', error);
        return {
            words: 0,
            minutes: 0,
            formatted: 'Unknown reading time'
        };
    }
}

/**
 * Gets system information
 * 
 * @returns {Object} System information
 */
function getSystemInfo() {
    return {
        platform: process.platform || 'unknown',
        nodeVersion: process.version || 'unknown',
        timestamp: new Date().toISOString(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
}

/**
 * Generates metadata for a new document
 * 
 * @param {Object} options - Document options
 * @param {string} options.title - Document title
 * @param {string} options.type - Document type
 * @param {string} options.category - Document category
 * @param {string[]} options.tags - Document tags
 * @param {string} options.status - Document status
 * @returns {Object} Complete frontmatter object
 */
function generateDocumentMetadata(options = {}) {
    try {
        const {
            title = 'Untitled Document',
            type = 'document',
            category = 'general',
            tags = [],
            status = getUserPreference('templates.defaultStatus', 'draft')
        } = options;
        
        const now = new Date();
        const dateFormat = getUserPreference('documentation.dateFormat', 'YYYY-MM-DD');
        
        // Format date (simple implementation)
        const formattedDate = now.toISOString().split('T')[0];
        
        const metadata = {
            id: generateDocumentID(type),
            title: title,
            created: formattedDate,
            updated: formattedDate,
            type: type,
            category: category,
            status: status,
            tags: tags,
            version: '1.0.0',
            aliases: []
        };
        
        // Add author if preference set
        if (getUserPreference('documentation.includeAuthorInfo', true)) {
            metadata.author = getUserPreference('author.name', 'Unknown');
        }
        
        return metadata;
        
    } catch (error) {
        console.error('Error generating document metadata:', error);
        return {
            created: new Date().toISOString().split('T')[0],
            type: 'document',
            status: 'draft'
        };
    }
}

/**
 * Formats frontmatter object as YAML
 * 
 * @param {Object} metadata - Metadata object
 * @returns {string} YAML formatted frontmatter
 */
function formatFrontmatter(metadata) {
    try {
        let yaml = '---\n';
        
        for (const [key, value] of Object.entries(metadata)) {
            if (Array.isArray(value)) {
                if (value.length === 0) {
                    yaml += `${key}: []\n`;
                } else {
                    yaml += `${key}:\n`;
                    value.forEach(item => {
                        yaml += `  - ${item}\n`;
                    });
                }
            } else if (typeof value === 'object' && value !== null) {
                yaml += `${key}:\n`;
                for (const [subKey, subValue] of Object.entries(value)) {
                    yaml += `  ${subKey}: ${subValue}\n`;
                }
            } else {
                yaml += `${key}: ${value}\n`;
            }
        }
        
        yaml += '---\n';
        
        return yaml;
        
    } catch (error) {
        console.error('Error formatting frontmatter:', error);
        return '---\n---\n';
    }
}

/**
 * Gets template-specific variables
 * 
 * @param {string} templateType - Type of template
 * @returns {Object} Template-specific variables
 */
function getTemplateVariables(templateType) {
    try {
        const templateVars = {
            'module-doc': {
                defaultSections: [
                    'Overview',
                    'Architecture',
                    'API Reference',
                    'Implementation Details',
                    'Usage Examples',
                    'Testing',
                    'Related Documentation'
                ],
                requiredFields: ['module_name', 'module_path', 'dependencies'],
                suggestedTags: ['module', 'code', 'api', 'implementation']
            },
            
            'agent-doc': {
                defaultSections: [
                    'Agent Identification',
                    'Task Charter',
                    'Execution Summary',
                    'Deliverables',
                    'Quality Gates',
                    'Next Steps'
                ],
                requiredFields: ['agent_id', 'task_description', 'deliverables'],
                suggestedTags: ['agent', 'task', 'execution', 'audit']
            },
            
            'architecture-doc': {
                defaultSections: [
                    'Context',
                    'Problem Statement',
                    'Decision',
                    'Rationale',
                    'Alternatives Considered',
                    'Consequences',
                    'Implementation Notes',
                    'Related Decisions'
                ],
                requiredFields: ['decision_number', 'context', 'consequences'],
                suggestedTags: ['architecture', 'design', 'adr', 'decision']
            },
            
            'guide': {
                defaultSections: [
                    'Overview',
                    'Prerequisites',
                    'Getting Started',
                    'Step-by-Step Guide',
                    'Examples',
                    'Troubleshooting',
                    'Best Practices',
                    'Additional Resources'
                ],
                requiredFields: ['difficulty', 'prerequisites', 'estimated_time'],
                suggestedTags: ['guide', 'tutorial', 'reference', 'documentation']
            }
        };
        
        return templateVars[templateType] || {
            defaultSections: [],
            requiredFields: [],
            suggestedTags: []
        };
        
    } catch (error) {
        console.error('Error getting template variables:', error);
        return {
            defaultSections: [],
            requiredFields: [],
            suggestedTags: []
        };
    }
}

/**
 * Validates required fields for template type
 * 
 * @param {Object} metadata - Document metadata
 * @param {string} templateType - Template type
 * @returns {Object} Validation result
 */
function validateTemplateRequirements(metadata, templateType) {
    try {
        const templateVars = getTemplateVariables(templateType);
        const requiredFields = templateVars.requiredFields || [];
        
        const missing = [];
        const present = [];
        
        requiredFields.forEach(field => {
            if (!metadata[field] || metadata[field] === '') {
                missing.push(field);
            } else {
                present.push(field);
            }
        });
        
        return {
            isValid: missing.length === 0,
            missing: missing,
            present: present,
            completeness: requiredFields.length > 0 ? 
                Math.round((present.length / requiredFields.length) * 100) : 100
        };
        
    } catch (error) {
        console.error('Error validating template requirements:', error);
        return {
            isValid: true,
            missing: [],
            present: [],
            completeness: 100
        };
    }
}

// Export functions and constants for use in Templater
module.exports = {
    PROJECT_CONTEXT,
    USER_PREFERENCES,
    getProjectContext,
    getContextVariable,
    getUserPreference,
    setUserPreference,
    calculateDocProgress,
    generateDocumentID,
    calculateReadingTime,
    getSystemInfo,
    generateDocumentMetadata,
    formatFrontmatter,
    getTemplateVariables,
    validateTemplateRequirements
};
