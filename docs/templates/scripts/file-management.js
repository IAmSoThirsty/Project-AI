/**
 * File Management Utilities for Templater
 *
 * Provides helpers for bulk file operations, renaming, archival,
 * and folder organization within the Obsidian vault.
 *
 * @module file-management
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 * @requires obsidian
 */

/**
 * Generates a safe filename from a title string
 *
 * Removes unsafe characters and normalizes spacing/casing.
 *
 * @param {string} title - Original title
 * @param {Object} options - Naming options
 * @param {string} options.case - 'kebab' | 'snake' | 'camel' | 'pascal' | 'preserve'
 * @param {number} options.maxLength - Maximum length (default: 100)
 * @param {boolean} options.allowSpaces - Allow spaces in filename (default: false)
 * @returns {string} Safe filename (without extension)
 *
 * @example
 * generateSafeFilename('API Reference: Authentication & Auth', { case: 'kebab' })
 * // Returns: "api-reference-authentication-auth"
 */
function generateSafeFilename(title, options = {}) {
    try {
        const {
            case: nameCase = 'kebab',
            maxLength = 100,
            allowSpaces = false
        } = options;

        let filename = title;

        // Remove or replace unsafe characters
        const unsafeChars = /[<>:"/\\|?*\x00-\x1F]/g;
        filename = filename.replace(unsafeChars, '');

        // Replace special characters with spaces or hyphens
        filename = filename.replace(/[^\w\s-]/g, allowSpaces ? ' ' : '-');

        // Normalize whitespace
        filename = filename.replace(/\s+/g, allowSpaces ? ' ' : '-');
        filename = filename.replace(/-+/g, '-');

        // Apply case transformation
        switch (nameCase) {
            case 'kebab':
                filename = filename.toLowerCase();
                filename = filename.replace(/\s+/g, '-');
                break;

            case 'snake':
                filename = filename.toLowerCase();
                filename = filename.replace(/[\s-]+/g, '_');
                break;

            case 'camel':
                filename = filename
                    .toLowerCase()
                    .replace(/[\s-_]+(.)/g, (_, char) => char.toUpperCase());
                break;

            case 'pascal':
                filename = filename
                    .toLowerCase()
                    .replace(/[\s-_]+(.)/g, (_, char) => char.toUpperCase());
                filename = filename.charAt(0).toUpperCase() + filename.slice(1);
                break;

            case 'preserve':
                // Keep original casing
                break;

            default:
                filename = filename.toLowerCase().replace(/\s+/g, '-');
        }

        // Trim to max length
        if (filename.length > maxLength) {
            filename = filename.substring(0, maxLength);
        }

        // Remove leading/trailing separators
        filename = filename.replace(/^[-_\s]+|[-_\s]+$/g, '');

        // Ensure not empty
        if (filename.length === 0) {
            filename = 'untitled';
        }

        return filename;

    } catch (error) {
        console.error('Error generating safe filename:', error);
        return 'untitled';
    }
}

/**
 * Suggests a folder path based on document metadata
 *
 * @param {Object} metadata - Document frontmatter
 * @param {string} filename - Document filename
 * @returns {string} Suggested folder path
 *
 * @example
 * suggestFolderPath({ category: 'module-doc', type: 'core-system' }, 'ai-systems.md')
 * // Returns: "modules/core-systems"
 */
function suggestFolderPath(metadata, filename) {
    try {
        const category = metadata.category || metadata.type || 'general';

        // Define folder mapping
        const folderMap = {
            'module-doc': 'modules',
            'agent-doc': 'agents',
            'architecture-doc': 'architecture',
            'guide': 'guides'
        };

        const baseFolder = folderMap[category] || 'documents';

        // Add sub-folder based on type if available
        const docType = metadata.type;
        const subFolderMap = {
            'core-system': 'core-systems',
            'gui-component': 'gui-components',
            'agent': 'ai-agents',
            'task-report': 'task-reports',
            'security-audit': 'security',
            'adr': 'decisions',
            'integration': 'integrations',
            'design-pattern': 'patterns',
            'quickstart': 'quickstarts',
            'troubleshooting': 'troubleshooting',
            'developer-reference': 'references'
        };

        const subFolder = subFolderMap[docType] || '';

        return subFolder ? `${baseFolder}/${subFolder}` : baseFolder;

    } catch (error) {
        console.error('Error suggesting folder path:', error);
        return 'documents';
    }
}

/**
 * Generates a unique filename to avoid collisions
 *
 * @param {string} basename - Desired base filename (without extension)
 * @param {string} extension - File extension (default: 'md')
 * @param {Object} app - Obsidian app instance
 * @param {string} folder - Target folder path
 * @returns {string} Unique filename
 */
function generateUniqueFilename(basename, extension = 'md', app = null, folder = '') {
    try {
        if (!app || !app.vault) {
            // Fallback without collision detection
            return `${basename}.${extension}`;
        }

        let counter = 1;
        let filename = `${basename}.${extension}`;
        let fullPath = folder ? `${folder}/${filename}` : filename;

        // Check for existing file
        while (app.vault.getAbstractFileByPath(fullPath)) {
            filename = `${basename}-${counter}.${extension}`;
            fullPath = folder ? `${folder}/${filename}` : filename;
            counter++;

            // Safety limit
            if (counter > 1000) {
                console.warn('Reached maximum collision attempts');
                break;
            }
        }

        return filename;

    } catch (error) {
        console.error('Error generating unique filename:', error);
        return `${basename}.${extension}`;
    }
}

/**
 * Bulk rename files using a pattern
 *
 * @param {Object[]} files - Array of file objects
 * @param {Function} renameFn - Rename function (oldName) => newName
 * @param {Object} app - Obsidian app instance
 * @returns {Promise<Object>} Rename report
 *
 * @example
 * await bulkRename(files, (name) => name.replace('old', 'new'), app);
 */
async function bulkRename(files, renameFn, app) {
    try {
        if (!app || !app.vault) {
            throw new Error('Obsidian app instance required');
        }

        const results = {
            success: [],
            failed: [],
            skipped: []
        };

        for (const file of files) {
            try {
                const oldName = file.basename;
                const newName = renameFn(oldName);

                // Skip if name unchanged
                if (oldName === newName) {
                    results.skipped.push({
                        file: file.path,
                        reason: 'Name unchanged'
                    });
                    continue;
                }

                // Validate new name
                if (!newName || newName.trim() === '') {
                    results.failed.push({
                        file: file.path,
                        error: 'Invalid new name'
                    });
                    continue;
                }

                // Build new path
                const newPath = file.parent ?
                    `${file.parent.path}/${newName}.md` :
                    `${newName}.md`;

                // Check for collision
                if (app.vault.getAbstractFileByPath(newPath)) {
                    results.failed.push({
                        file: file.path,
                        error: 'File already exists at target path'
                    });
                    continue;
                }

                // Perform rename
                await app.fileManager.renameFile(file, newPath);

                results.success.push({
                    oldPath: file.path,
                    newPath: newPath
                });

            } catch (error) {
                results.failed.push({
                    file: file.path,
                    error: error.message
                });
            }
        }

        return results;

    } catch (error) {
        console.error('Error in bulk rename:', error);
        return {
            success: [],
            failed: [],
            skipped: [],
            error: error.message
        };
    }
}

/**
 * Archives old files by moving them to an archive folder
 *
 * @param {Object} options - Archive options
 * @param {number} options.olderThanDays - Archive files older than N days
 * @param {string} options.sourceFolder - Source folder to archive from
 * @param {string} options.archiveFolder - Archive destination folder
 * @param {string[]} options.excludeTags - Don't archive files with these tags
 * @param {Object} app - Obsidian app instance
 * @returns {Promise<Object>} Archive report
 */
async function archiveOldFiles(options, app) {
    try {
        if (!app || !app.vault) {
            throw new Error('Obsidian app instance required');
        }

        const {
            olderThanDays = 90,
            sourceFolder = '',
            archiveFolder = 'archive',
            excludeTags = ['important', 'active', 'wip']
        } = options;

        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

        const results = {
            archived: [],
            skipped: [],
            failed: []
        };

        // Get files from source folder
        const files = sourceFolder ?
            app.vault.getMarkdownFiles().filter(f => f.path.startsWith(sourceFolder)) :
            app.vault.getMarkdownFiles();

        for (const file of files) {
            try {
                // Check file age
                const metadata = app.metadataCache.getFileCache(file);
                const updated = metadata?.frontmatter?.updated;

                let fileDate;
                if (updated) {
                    fileDate = new Date(updated);
                } else {
                    fileDate = new Date(file.stat.mtime);
                }

                // Skip if too recent
                if (fileDate > cutoffDate) {
                    results.skipped.push({
                        file: file.path,
                        reason: 'Too recent'
                    });
                    continue;
                }

                // Check excluded tags
                const fileTags = metadata?.frontmatter?.tags || [];
                const hasExcludedTag = fileTags.some(tag => excludeTags.includes(tag));

                if (hasExcludedTag) {
                    results.skipped.push({
                        file: file.path,
                        reason: 'Has excluded tag'
                    });
                    continue;
                }

                // Build archive path
                const archivePath = `${archiveFolder}/${file.basename}.md`;

                // Create archive folder if needed
                const archiveFolderObj = app.vault.getAbstractFileByPath(archiveFolder);
                if (!archiveFolderObj) {
                    await app.vault.createFolder(archiveFolder);
                }

                // Move file
                await app.fileManager.renameFile(file, archivePath);

                results.archived.push({
                    from: file.path,
                    to: archivePath,
                    date: fileDate.toISOString()
                });

            } catch (error) {
                results.failed.push({
                    file: file.path,
                    error: error.message
                });
            }
        }

        return results;

    } catch (error) {
        console.error('Error archiving files:', error);
        return {
            archived: [],
            skipped: [],
            failed: [],
            error: error.message
        };
    }
}

/**
 * Organizes files into folders based on metadata
 *
 * @param {Object} app - Obsidian app instance
 * @param {boolean} dryRun - If true, only report changes without moving files
 * @returns {Promise<Object>} Organization report
 */
async function organizeFilesByMetadata(app, dryRun = false) {
    try {
        if (!app || !app.vault) {
            throw new Error('Obsidian app instance required');
        }

        const results = {
            moved: [],
            skipped: [],
            failed: []
        };

        const files = app.vault.getMarkdownFiles();

        for (const file of files) {
            try {
                const cache = app.metadataCache.getFileCache(file);
                if (!cache || !cache.frontmatter) {
                    results.skipped.push({
                        file: file.path,
                        reason: 'No frontmatter'
                    });
                    continue;
                }

                const metadata = cache.frontmatter;
                const suggestedFolder = suggestFolderPath(metadata, file.basename);

                // Skip if already in correct folder
                if (file.parent && file.parent.path === suggestedFolder) {
                    results.skipped.push({
                        file: file.path,
                        reason: 'Already in correct folder'
                    });
                    continue;
                }

                const newPath = `${suggestedFolder}/${file.basename}.md`;

                if (dryRun) {
                    results.moved.push({
                        from: file.path,
                        to: newPath,
                        dryRun: true
                    });
                } else {
                    // Create folder if needed
                    const folderExists = app.vault.getAbstractFileByPath(suggestedFolder);
                    if (!folderExists) {
                        await app.vault.createFolder(suggestedFolder);
                    }

                    // Move file
                    await app.fileManager.renameFile(file, newPath);

                    results.moved.push({
                        from: file.path,
                        to: newPath
                    });
                }

            } catch (error) {
                results.failed.push({
                    file: file.path,
                    error: error.message
                });
            }
        }

        return results;

    } catch (error) {
        console.error('Error organizing files:', error);
        return {
            moved: [],
            skipped: [],
            failed: [],
            error: error.message
        };
    }
}

/**
 * Finds duplicate files by content hash
 *
 * @param {Object} app - Obsidian app instance
 * @returns {Promise<Object>} Duplicate report
 */
async function findDuplicateFiles(app) {
    try {
        if (!app || !app.vault) {
            throw new Error('Obsidian app instance required');
        }

        const files = app.vault.getMarkdownFiles();
        const hashes = {};
        const duplicates = [];

        for (const file of files) {
            try {
                const content = await app.vault.read(file);

                // Simple hash (for demonstration - use better hash in production)
                const hash = simpleHash(content);

                if (hashes[hash]) {
                    duplicates.push({
                        file1: hashes[hash],
                        file2: file.path,
                        hash: hash
                    });
                } else {
                    hashes[hash] = file.path;
                }
            } catch (error) {
                console.error(`Error reading file ${file.path}:`, error);
            }
        }

        return {
            duplicates: duplicates,
            totalFiles: files.length,
            uniqueFiles: Object.keys(hashes).length
        };

    } catch (error) {
        console.error('Error finding duplicates:', error);
        return {
            duplicates: [],
            totalFiles: 0,
            uniqueFiles: 0,
            error: error.message
        };
    }
}

/**
 * Simple string hash function
 *
 * @param {string} str - String to hash
 * @returns {string} Hash string
 */
function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
}

/**
 * Generates a file tree structure
 *
 * @param {string} rootPath - Root folder path
 * @param {Object} app - Obsidian app instance
 * @param {number} maxDepth - Maximum depth (default: 3)
 * @returns {string} File tree in markdown
 */
function generateFileTree(rootPath, app, maxDepth = 3) {
    try {
        if (!app || !app.vault) {
            return '> Obsidian app instance required';
        }

        const root = app.vault.getAbstractFileByPath(rootPath);
        if (!root) {
            return `> Path not found: ${rootPath}`;
        }

        let tree = `\`\`\`\n${rootPath}/\n`;
        tree += buildTreeRecursive(root, '', 0, maxDepth, app);
        tree += '\`\`\`';

        return tree;

    } catch (error) {
        console.error('Error generating file tree:', error);
        return '> Error generating tree';
    }
}

/**
 * Recursively builds file tree
 *
 * @param {Object} folder - Folder object
 * @param {string} prefix - Line prefix
 * @param {number} depth - Current depth
 * @param {number} maxDepth - Maximum depth
 * @param {Object} app - App instance
 * @returns {string} Tree string
 */
function buildTreeRecursive(folder, prefix, depth, maxDepth, app) {
    if (depth >= maxDepth) {
        return '';
    }

    let result = '';

    if (folder.children) {
        const children = folder.children.sort((a, b) => {
            // Folders first, then files alphabetically
            if (a.children && !b.children) return -1;
            if (!a.children && b.children) return 1;
            return a.name.localeCompare(b.name);
        });

        children.forEach((child, index) => {
            const isLast = index === children.length - 1;
            const marker = isLast ? '└── ' : '├── ';
            const newPrefix = prefix + (isLast ? '    ' : '│   ');

            result += `${prefix}${marker}${child.name}${child.children ? '/' : ''}\n`;

            if (child.children) {
                result += buildTreeRecursive(child, newPrefix, depth + 1, maxDepth, app);
            }
        });
    }

    return result;
}

// Export functions for use in Templater
module.exports = {
    generateSafeFilename,
    suggestFolderPath,
    generateUniqueFilename,
    bulkRename,
    archiveOldFiles,
    organizeFilesByMetadata,
    findDuplicateFiles,
    generateFileTree,
    simpleHash
};
