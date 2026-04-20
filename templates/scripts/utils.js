// Templater User Script: Advanced Utilities
// Location: templates/scripts/utils.js
// 
// This script provides custom functions for Templater templates
// Enable in Templater settings: User Scripts Folder = "templates/scripts"

/**
 * Generate a unique ID based on timestamp and random string
 * Usage: <% tp.user.generate_id() %>
 */
function generate_id() {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `${timestamp}-${random}`;
}

/**
 * Format a date in a human-readable relative format
 * Usage: <% tp.user.relative_date("2024-01-01") %>
 */
function relative_date(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return date < now ? "Yesterday" : "Tomorrow";
    if (diffDays < 7) return `${diffDays} days ${date < now ? "ago" : "from now"}`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ${date < now ? "ago" : "from now"}`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ${date < now ? "ago" : "from now"}`;
    return `${Math.floor(diffDays / 365)} years ${date < now ? "ago" : "from now"}`;
}

/**
 * Get current git branch (requires git in PATH)
 * Usage: <% tp.user.git_branch() %>
 */
async function git_branch() {
    try {
        const { exec } = require('child_process');
        const util = require('util');
        const execPromise = util.promisify(exec);
        
        const { stdout } = await execPromise('git rev-parse --abbrev-ref HEAD');
        return stdout.trim();
    } catch (error) {
        return "Not a git repository";
    }
}

/**
 * Get random item from array
 * Usage: <% tp.user.random_from_array(["option1", "option2", "option3"]) %>
 */
function random_from_array(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Count words in text
 * Usage: <% tp.user.word_count(tp.file.content) %>
 */
function word_count(text) {
    return text.split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Generate a table of contents from headings
 * Usage: <%* tR += tp.user.generate_toc(tp.file.content) %>
 */
function generate_toc(content) {
    const headings = content.match(/^#{1,6} .+$/gm) || [];
    let toc = "## Table of Contents\n\n";
    
    headings.forEach(heading => {
        const level = heading.match(/^#+/)[0].length;
        const text = heading.replace(/^#+\s/, '');
        const link = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
        const indent = '  '.repeat(level - 1);
        toc += `${indent}- [${text}](#${link})\n`;
    });
    
    return toc;
}

/**
 * Format currency
 * Usage: <% tp.user.format_currency(1234.56, "USD") %>
 */
function format_currency(amount, currency = "USD") {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Calculate days between two dates
 * Usage: <% tp.user.days_between("2024-01-01", "2024-12-31") %>
 */
function days_between(date1, date2) {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    const diffTime = Math.abs(d2 - d1);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Get season based on date
 * Usage: <% tp.user.get_season() %>
 */
function get_season(date = new Date()) {
    const month = date.getMonth() + 1;
    if (month >= 3 && month <= 5) return "Spring";
    if (month >= 6 && month <= 8) return "Summer";
    if (month >= 9 && month <= 11) return "Fall";
    return "Winter";
}

/**
 * Generate a progress bar
 * Usage: <% tp.user.progress_bar(75, 20) %>
 */
function progress_bar(percentage, length = 20) {
    const filled = Math.round((percentage / 100) * length);
    const empty = length - filled;
    return `[${'█'.repeat(filled)}${'░'.repeat(empty)}] ${percentage}%`;
}

// Export all functions for Templater
module.exports = {
    generate_id,
    relative_date,
    git_branch,
    random_from_array,
    word_count,
    generate_toc,
    format_currency,
    days_between,
    get_season,
    progress_bar
};
