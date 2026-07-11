/**
 * Dataview Helper Functions for Templater
 *
 * Provides utilities for building Dataview queries, data aggregation,
 * and report generation for the Project-AI vault.
 *
 * @module dataview-helpers
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 * @requires dataview (Obsidian plugin)
 */

/**
 * Builds a Dataview query for filtering documents by category and tags
 *
 * @param {Object} filters - Query filters
 * @param {string} filters.category - Document category (module-doc, agent-doc, etc.)
 * @param {string[]} filters.tags - Tags to filter by
 * @param {string} filters.status - Document status (draft, published, etc.)
 * @param {string} filters.folder - Folder path to search in
 * @param {string} outputFormat - Output format: 'list', 'table', 'task'
 * @param {string[]} tableColumns - Columns for table output
 * @returns {string} Dataview query string
 *
 * @example
 * const query = buildQuery({
 *   category: 'module-doc',
 *   tags: ['ai', 'core'],
 *   status: 'published'
 * }, 'table', ['file.name', 'updated', 'status']);
 */
function buildQuery(filters = {}, outputFormat = 'list', tableColumns = []) {
    try {
        const {
            category = null,
            tags = [],
            status = null,
            folder = null,
            type = null,
            dateFrom = null,
            dateTo = null
        } = filters;

        let query = '';

        // Build output clause
        if (outputFormat === 'table' && tableColumns.length > 0) {
            query += `TABLE ${tableColumns.join(', ')}\n`;
        } else if (outputFormat === 'task') {
            query += 'TASK\n';
        } else {
            query += 'LIST\n';
        }

        // Build FROM clause
        if (folder) {
            query += `FROM "${folder}"\n`;
        } else {
            query += 'FROM ""\n';
        }

        // Build WHERE clauses
        const conditions = [];

        if (category) {
            conditions.push(`category = "${category}"`);
        }

        if (type) {
            conditions.push(`type = "${type}"`);
        }

        if (status) {
            conditions.push(`status = "${status}"`);
        }

        if (tags && tags.length > 0) {
            // Multiple tags = all must be present (AND logic)
            tags.forEach(tag => {
                conditions.push(`contains(tags, "${tag}")`);
            });
        }

        if (dateFrom) {
            conditions.push(`created >= date("${dateFrom}")`);
        }

        if (dateTo) {
            conditions.push(`created <= date("${dateTo}")`);
        }

        if (conditions.length > 0) {
            query += 'WHERE ' + conditions.join(' AND ') + '\n';
        }

        // Add default sorting
        query += 'SORT file.name ASC';

        return query;

    } catch (error) {
        console.error('Error building Dataview query:', error);
        return `\`\`\`dataview\nLIST\nFROM ""\n\`\`\``;
    }
}

/**
 * Generates a Dataview query to find recently updated documents
 *
 * @param {number} days - Number of days to look back (default: 7)
 * @param {string} category - Optional category filter
 * @param {number} limit - Maximum number of results (default: 10)
 * @returns {string} Dataview query string
 *
 * @example
 * const query = queryRecentlyUpdated(7, 'module-doc', 10);
 */
function queryRecentlyUpdated(days = 7, category = null, limit = 10) {
    try {
        let query = 'TABLE updated, status, tags\n';
        query += 'FROM ""\n';

        const conditions = [];

        // Calculate date threshold
        const daysAgo = new Date();
        daysAgo.setDate(daysAgo.getDate() - days);
        const threshold = daysAgo.toISOString().split('T')[0];

        conditions.push(`updated >= date("${threshold}")`);

        if (category) {
            conditions.push(`category = "${category}"`);
        }

        if (conditions.length > 0) {
            query += 'WHERE ' + conditions.join(' AND ') + '\n';
        }

        query += 'SORT updated DESC\n';
        query += `LIMIT ${limit}`;

        return query;

    } catch (error) {
        console.error('Error building recently updated query:', error);
        return 'LIST\nFROM ""';
    }
}

/**
 * Generates a Dataview query to find documents by status
 *
 * @param {string} status - Status to filter by (draft, published, deprecated, etc.)
 * @param {string} category - Optional category filter
 * @returns {string} Dataview query string
 */
function queryByStatus(status, category = null) {
    try {
        let query = 'TABLE file.folder as Folder, updated as "Last Updated", tags\n';
        query += 'FROM ""\n';

        const conditions = [`status = "${status}"`];

        if (category) {
            conditions.push(`category = "${category}"`);
        }

        query += 'WHERE ' + conditions.join(' AND ') + '\n';
        query += 'SORT file.name ASC';

        return query;

    } catch (error) {
        console.error('Error building status query:', error);
        return 'LIST\nFROM ""';
    }
}

/**
 * Aggregates statistics about documents in the vault
 *
 * @param {Object} dv - Dataview API instance
 * @returns {Object} Statistics object
 *
 * @example
 * const stats = await aggregateVaultStats(dv);
 * // Returns: { totalDocs: 150, byCategory: {...}, byStatus: {...}, ... }
 */
async function aggregateVaultStats(dv) {
    try {
        if (!dv) {
            throw new Error('Dataview API not available');
        }

        const pages = dv.pages('""');

        const stats = {
            totalDocs: pages.length,
            byCategory: {},
            byStatus: {},
            byType: {},
            tagCloud: {},
            recentlyUpdated: 0,
            stale: 0
        };

        const now = new Date();
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

        for (const page of pages) {
            // Count by category
            if (page.category) {
                stats.byCategory[page.category] = (stats.byCategory[page.category] || 0) + 1;
            }

            // Count by status
            if (page.status) {
                stats.byStatus[page.status] = (stats.byStatus[page.status] || 0) + 1;
            }

            // Count by type
            if (page.type) {
                stats.byType[page.type] = (stats.byType[page.type] || 0) + 1;
            }

            // Aggregate tags
            if (page.tags) {
                const tags = Array.isArray(page.tags) ? page.tags : [page.tags];
                tags.forEach(tag => {
                    stats.tagCloud[tag] = (stats.tagCloud[tag] || 0) + 1;
                });
            }

            // Check update recency
            if (page.updated) {
                const updateDate = new Date(page.updated);
                if (updateDate >= sevenDaysAgo) {
                    stats.recentlyUpdated++;
                } else if (updateDate < thirtyDaysAgo) {
                    stats.stale++;
                }
            }
        }

        // Sort tag cloud by frequency
        stats.topTags = Object.entries(stats.tagCloud)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .map(([tag, count]) => ({ tag, count }));

        return stats;

    } catch (error) {
        console.error('Error aggregating vault stats:', error);
        return null;
    }
}

/**
 * Generates a progress report for agent tasks
 *
 * @param {Object} dv - Dataview API instance
 * @returns {string} Markdown formatted report
 */
async function generateAgentProgressReport(dv) {
    try {
        if (!dv) {
            throw new Error('Dataview API not available');
        }

        const agentDocs = dv.pages('"" WHERE category = "agent-doc"');

        let report = '## Agent Task Progress Report\n\n';
        report += `**Total Agent Tasks:** ${agentDocs.length}\n\n`;

        // Count by status
        const statusCounts = {};
        for (const doc of agentDocs) {
            const status = doc.status || 'unknown';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
        }

        report += '### By Status\n\n';
        for (const [status, count] of Object.entries(statusCounts)) {
            const percentage = ((count / agentDocs.length) * 100).toFixed(1);
            report += `- **${status}:** ${count} (${percentage}%)\n`;
        }

        // Recent completions (last 7 days)
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

        const recentCompletions = agentDocs.filter(doc => {
            if (!doc.updated) return false;
            const updateDate = new Date(doc.updated);
            return updateDate >= sevenDaysAgo && doc.status === 'completed';
        });

        report += `\n### Recent Completions (Last 7 Days)\n\n`;
        report += `**Count:** ${recentCompletions.length}\n\n`;

        if (recentCompletions.length > 0) {
            report += '```dataview\n';
            report += 'TABLE updated as "Completed", type as "Task Type"\n';
            report += 'FROM ""\n';
            report += 'WHERE category = "agent-doc" AND status = "completed"\n';
            const threshold = sevenDaysAgo.toISOString().split('T')[0];
            report += `WHERE updated >= date("${threshold}")\n`;
            report += 'SORT updated DESC\n';
            report += 'LIMIT 10\n';
            report += '```\n';
        }

        return report;

    } catch (error) {
        console.error('Error generating agent progress report:', error);
        return '> Error generating report';
    }
}

/**
 * Generates a documentation health report
 *
 * @param {Object} dv - Dataview API instance
 * @returns {string} Markdown formatted report
 */
async function generateHealthReport(dv) {
    try {
        if (!dv) {
            throw new Error('Dataview API not available');
        }

        const pages = dv.pages('""');

        let report = '## Documentation Health Report\n\n';
        report += `**Generated:** ${new Date().toISOString().split('T')[0]}\n\n`;

        // Calculate metrics
        const total = pages.length;
        let complete = 0;
        let incomplete = 0;
        let deprecated = 0;
        let needsReview = 0;
        let stale = 0;

        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        for (const page of pages) {
            // Status checks
            if (page.status === 'published') complete++;
            if (page.status === 'draft') incomplete++;
            if (page.status === 'deprecated') deprecated++;
            if (page.status === 'in-review') needsReview++;

            // Staleness check
            if (page.updated) {
                const updateDate = new Date(page.updated);
                if (updateDate < thirtyDaysAgo && page.status !== 'deprecated') {
                    stale++;
                }
            }
        }

        report += '### Overall Health\n\n';
        report += `- **Total Documents:** ${total}\n`;
        report += `- **Published:** ${complete} (${((complete/total)*100).toFixed(1)}%)\n`;
        report += `- **Draft:** ${incomplete} (${((incomplete/total)*100).toFixed(1)}%)\n`;
        report += `- **In Review:** ${needsReview}\n`;
        report += `- **Deprecated:** ${deprecated}\n`;
        report += `- **Stale (>30 days):** ${stale}\n\n`;

        // Health score (0-100)
        const healthScore = Math.round(
            (complete / total) * 50 +           // 50% weight on published docs
            ((total - stale) / total) * 30 +    // 30% weight on freshness
            ((total - incomplete) / total) * 20 // 20% weight on completeness
        );

        report += `### Health Score: ${healthScore}/100\n\n`;

        if (healthScore >= 80) {
            report += '✅ **Status:** Excellent\n\n';
        } else if (healthScore >= 60) {
            report += '⚠️ **Status:** Good (needs attention)\n\n';
        } else {
            report += '🔴 **Status:** Needs improvement\n\n';
        }

        // Action items
        report += '### Action Items\n\n';

        if (incomplete > 0) {
            report += `- Complete ${incomplete} draft documents\n`;
        }

        if (stale > 0) {
            report += `- Review and update ${stale} stale documents\n`;
        }

        if (needsReview > 0) {
            report += `- Process ${needsReview} documents pending review\n`;
        }

        return report;

    } catch (error) {
        console.error('Error generating health report:', error);
        return '> Error generating report';
    }
}

/**
 * Creates a tag usage report
 *
 * @param {Object} dv - Dataview API instance
 * @param {number} topN - Number of top tags to show (default: 20)
 * @returns {string} Markdown formatted report
 */
async function generateTagReport(dv, topN = 20) {
    try {
        if (!dv) {
            throw new Error('Dataview API not available');
        }

        const pages = dv.pages('""');
        const tagCounts = {};

        for (const page of pages) {
            if (page.tags) {
                const tags = Array.isArray(page.tags) ? page.tags : [page.tags];
                tags.forEach(tag => {
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                });
            }
        }

        const sortedTags = Object.entries(tagCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, topN);

        let report = `## Tag Usage Report (Top ${topN})\n\n`;
        report += '| Rank | Tag | Count | Percentage |\n';
        report += '|------|-----|-------|------------|\n';

        sortedTags.forEach(([tag, count], index) => {
            const percentage = ((count / pages.length) * 100).toFixed(1);
            report += `| ${index + 1} | #${tag} | ${count} | ${percentage}% |\n`;
        });

        // Orphaned tags (used only once)
        const orphanedTags = Object.entries(tagCounts)
            .filter(([, count]) => count === 1)
            .map(([tag]) => tag);

        if (orphanedTags.length > 0) {
            report += `\n### Orphaned Tags (Used Once)\n\n`;
            report += `**Count:** ${orphanedTags.length}\n\n`;
            report += orphanedTags.slice(0, 10).map(tag => `- #${tag}`).join('\n');

            if (orphanedTags.length > 10) {
                report += `\n- *(and ${orphanedTags.length - 10} more...)*`;
            }
        }

        return report;

    } catch (error) {
        console.error('Error generating tag report:', error);
        return '> Error generating report';
    }
}

/**
 * Generates a dependency matrix showing document relationships
 *
 * @param {Object} dv - Dataview API instance
 * @param {string} category - Category to analyze
 * @returns {string} Markdown formatted dependency matrix
 */
async function generateDependencyMatrix(dv, category = 'module-doc') {
    try {
        if (!dv) {
            throw new Error('Dataview API not available');
        }

        const pages = dv.pages(`"" WHERE category = "${category}"`);

        let matrix = `## Dependency Matrix: ${category}\n\n`;

        // Build link graph
        const linkGraph = {};

        for (const page of pages) {
            const outbound = page.file.outlinks || [];
            linkGraph[page.file.name] = {
                outbound: outbound.map(link => link.path),
                inbound: []
            };
        }

        // Calculate inbound links
        for (const [source, links] of Object.entries(linkGraph)) {
            links.outbound.forEach(target => {
                const targetName = target.replace(/\.md$/, '');
                if (linkGraph[targetName]) {
                    linkGraph[targetName].inbound.push(source);
                }
            });
        }

        // Find highly connected documents
        const connectivity = Object.entries(linkGraph).map(([name, links]) => ({
            name: name,
            totalLinks: links.outbound.length + links.inbound.length,
            outbound: links.outbound.length,
            inbound: links.inbound.length
        })).sort((a, b) => b.totalLinks - a.totalLinks);

        matrix += '### Most Connected Documents\n\n';
        matrix += '| Document | Outbound Links | Inbound Links | Total |\n';
        matrix += '|----------|----------------|---------------|-------|\n';

        connectivity.slice(0, 10).forEach(doc => {
            matrix += `| [[${doc.name}]] | ${doc.outbound} | ${doc.inbound} | ${doc.totalLinks} |\n`;
        });

        // Find isolated documents (no links)
        const isolated = connectivity.filter(doc => doc.totalLinks === 0);

        if (isolated.length > 0) {
            matrix += `\n### Isolated Documents (No Links)\n\n`;
            matrix += `**Count:** ${isolated.length}\n\n`;
            isolated.forEach(doc => {
                matrix += `- [[${doc.name}]]\n`;
            });
        }

        return matrix;

    } catch (error) {
        console.error('Error generating dependency matrix:', error);
        return '> Error generating matrix';
    }
}

/**
 * Generates a calendar heatmap query for document activity
 *
 * @param {string} year - Year to analyze (e.g., '2026')
 * @returns {string} Dataview query for calendar view
 */
function generateCalendarHeatmap(year = new Date().getFullYear().toString()) {
    return `\`\`\`dataview
CALENDAR updated
FROM ""
WHERE updated >= date("${year}-01-01") AND updated <= date("${year}-12-31")
\`\`\``;
}

// Export functions for use in Templater
module.exports = {
    buildQuery,
    queryRecentlyUpdated,
    queryByStatus,
    aggregateVaultStats,
    generateAgentProgressReport,
    generateHealthReport,
    generateTagReport,
    generateDependencyMatrix,
    generateCalendarHeatmap
};
