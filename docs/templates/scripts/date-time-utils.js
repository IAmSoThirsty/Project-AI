/**
 * Date and Time Utilities for Templater
 *
 * Provides advanced date/time formatting, relative date calculations,
 * timezone handling, and calendar integration helpers.
 *
 * @module date-time-utils
 * @version 1.0.0
 * @author Project-AI Documentation Team
 * @requires templater
 */

/**
 * Formats date in relative terms (e.g., "2 days ago", "in 3 hours")
 *
 * @param {Date|string} date - Date to format
 * @param {Date} referenceDate - Reference date (default: now)
 * @returns {string} Relative date string
 *
 * @example
 * formatRelativeDate(new Date('2026-04-18')) // "2 days ago"
 * formatRelativeDate('2026-04-22') // "in 2 days"
 */
function formatRelativeDate(date, referenceDate = new Date()) {
    try {
        const targetDate = date instanceof Date ? date : new Date(date);
        const refDate = referenceDate instanceof Date ? referenceDate : new Date(referenceDate);

        if (isNaN(targetDate.getTime()) || isNaN(refDate.getTime())) {
            return 'Invalid date';
        }

        const diffMs = targetDate.getTime() - refDate.getTime();
        const diffSeconds = Math.round(diffMs / 1000);
        const diffMinutes = Math.round(diffSeconds / 60);
        const diffHours = Math.round(diffMinutes / 60);
        const diffDays = Math.round(diffHours / 24);
        const diffWeeks = Math.round(diffDays / 7);
        const diffMonths = Math.round(diffDays / 30);
        const diffYears = Math.round(diffDays / 365);

        const isPast = diffMs < 0;
        const abs = Math.abs;

        // Format based on magnitude
        if (abs(diffSeconds) < 60) {
            return 'just now';
        } else if (abs(diffMinutes) < 60) {
            const unit = abs(diffMinutes) === 1 ? 'minute' : 'minutes';
            return isPast ? `${abs(diffMinutes)} ${unit} ago` : `in ${abs(diffMinutes)} ${unit}`;
        } else if (abs(diffHours) < 24) {
            const unit = abs(diffHours) === 1 ? 'hour' : 'hours';
            return isPast ? `${abs(diffHours)} ${unit} ago` : `in ${abs(diffHours)} ${unit}`;
        } else if (abs(diffDays) < 7) {
            const unit = abs(diffDays) === 1 ? 'day' : 'days';
            return isPast ? `${abs(diffDays)} ${unit} ago` : `in ${abs(diffDays)} ${unit}`;
        } else if (abs(diffWeeks) < 4) {
            const unit = abs(diffWeeks) === 1 ? 'week' : 'weeks';
            return isPast ? `${abs(diffWeeks)} ${unit} ago` : `in ${abs(diffWeeks)} ${unit}`;
        } else if (abs(diffMonths) < 12) {
            const unit = abs(diffMonths) === 1 ? 'month' : 'months';
            return isPast ? `${abs(diffMonths)} ${unit} ago` : `in ${abs(diffMonths)} ${unit}`;
        } else {
            const unit = abs(diffYears) === 1 ? 'year' : 'years';
            return isPast ? `${abs(diffYears)} ${unit} ago` : `in ${abs(diffYears)} ${unit}`;
        }

    } catch (error) {
        console.error('Error formatting relative date:', error);
        return 'Unknown date';
    }
}

/**
 * Formats date with custom format string
 *
 * Supported format codes:
 * - YYYY: 4-digit year
 * - YY: 2-digit year
 * - MM: 2-digit month
 * - M: month (no padding)
 * - DD: 2-digit day
 * - D: day (no padding)
 * - HH: 2-digit hour (24h)
 * - hh: 2-digit hour (12h)
 * - mm: 2-digit minute
 * - ss: 2-digit second
 * - A: AM/PM
 * - MMM: short month name
 * - MMMM: full month name
 * - ddd: short day name
 * - dddd: full day name
 *
 * @param {Date|string} date - Date to format
 * @param {string} format - Format string
 * @returns {string} Formatted date string
 *
 * @example
 * formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss') // "2026-04-20 14:30:45"
 * formatDate(new Date(), 'MMMM D, YYYY') // "April 20, 2026"
 */
function formatDate(date, format) {
    try {
        const d = date instanceof Date ? date : new Date(date);

        if (isNaN(d.getTime())) {
            return 'Invalid date';
        }

        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];

        const monthNamesShort = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ];

        const dayNames = [
            'Sunday', 'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday'
        ];

        const dayNamesShort = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        const pad = (n) => n < 10 ? '0' + n : n.toString();

        const replacements = {
            'YYYY': d.getFullYear().toString(),
            'YY': d.getFullYear().toString().slice(-2),
            'MMMM': monthNames[d.getMonth()],
            'MMM': monthNamesShort[d.getMonth()],
            'MM': pad(d.getMonth() + 1),
            'M': (d.getMonth() + 1).toString(),
            'DD': pad(d.getDate()),
            'D': d.getDate().toString(),
            'dddd': dayNames[d.getDay()],
            'ddd': dayNamesShort[d.getDay()],
            'HH': pad(d.getHours()),
            'hh': pad(d.getHours() % 12 || 12),
            'mm': pad(d.getMinutes()),
            'ss': pad(d.getSeconds()),
            'A': d.getHours() < 12 ? 'AM' : 'PM'
        };

        let result = format;

        // Replace in order of length (longest first to avoid partial matches)
        const keys = Object.keys(replacements).sort((a, b) => b.length - a.length);
        keys.forEach(key => {
            result = result.replace(new RegExp(key, 'g'), replacements[key]);
        });

        return result;

    } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid date';
    }
}

/**
 * Parses various date string formats to Date object
 *
 * @param {string} dateString - Date string to parse
 * @returns {Date|null} Parsed Date object or null if invalid
 */
function parseDate(dateString) {
    try {
        // Try standard Date parsing first
        let date = new Date(dateString);

        if (!isNaN(date.getTime())) {
            return date;
        }

        // Try common formats
        const formats = [
            /^(\d{4})-(\d{2})-(\d{2})$/,  // YYYY-MM-DD
            /^(\d{2})\/(\d{2})\/(\d{4})$/, // MM/DD/YYYY
            /^(\d{4})(\d{2})(\d{2})$/      // YYYYMMDD
        ];

        for (const regex of formats) {
            const match = dateString.match(regex);
            if (match) {
                // Adjust based on format
                if (regex.source.startsWith('^(\\d{4})')) {
                    // YYYY-MM-DD or YYYYMMDD
                    date = new Date(
                        parseInt(match[1]),
                        parseInt(match[2]) - 1,
                        parseInt(match[3])
                    );
                } else {
                    // MM/DD/YYYY
                    date = new Date(
                        parseInt(match[3]),
                        parseInt(match[1]) - 1,
                        parseInt(match[2])
                    );
                }

                if (!isNaN(date.getTime())) {
                    return date;
                }
            }
        }

        return null;

    } catch (error) {
        console.error('Error parsing date:', error);
        return null;
    }
}

/**
 * Calculates business days between two dates (excludes weekends)
 *
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @returns {number} Number of business days
 */
function calculateBusinessDays(startDate, endDate) {
    try {
        const start = startDate instanceof Date ? startDate : new Date(startDate);
        const end = endDate instanceof Date ? endDate : new Date(endDate);

        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            return 0;
        }

        let count = 0;
        const current = new Date(start);

        while (current <= end) {
            const dayOfWeek = current.getDay();
            // Monday (1) through Friday (5)
            if (dayOfWeek !== 0 && dayOfWeek !== 6) {
                count++;
            }
            current.setDate(current.getDate() + 1);
        }

        return count;

    } catch (error) {
        console.error('Error calculating business days:', error);
        return 0;
    }
}

/**
 * Adds or subtracts time from a date
 *
 * @param {Date|string} date - Base date
 * @param {number} amount - Amount to add (negative to subtract)
 * @param {string} unit - Unit: 'years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds'
 * @returns {Date} Modified date
 */
function modifyDate(date, amount, unit) {
    try {
        const d = date instanceof Date ? new Date(date) : new Date(date);

        if (isNaN(d.getTime())) {
            return new Date();
        }

        switch (unit.toLowerCase()) {
            case 'years':
            case 'year':
                d.setFullYear(d.getFullYear() + amount);
                break;
            case 'months':
            case 'month':
                d.setMonth(d.getMonth() + amount);
                break;
            case 'weeks':
            case 'week':
                d.setDate(d.getDate() + (amount * 7));
                break;
            case 'days':
            case 'day':
                d.setDate(d.getDate() + amount);
                break;
            case 'hours':
            case 'hour':
                d.setHours(d.getHours() + amount);
                break;
            case 'minutes':
            case 'minute':
                d.setMinutes(d.getMinutes() + amount);
                break;
            case 'seconds':
            case 'second':
                d.setSeconds(d.getSeconds() + amount);
                break;
            default:
                console.warn(`Unknown unit: ${unit}`);
        }

        return d;

    } catch (error) {
        console.error('Error modifying date:', error);
        return new Date();
    }
}

/**
 * Gets start and end of a time period
 *
 * @param {Date|string} date - Reference date
 * @param {string} period - Period: 'day', 'week', 'month', 'quarter', 'year'
 * @returns {Object} Object with start and end Date objects
 */
function getPeriodBounds(date, period) {
    try {
        const d = date instanceof Date ? new Date(date) : new Date(date);

        if (isNaN(d.getTime())) {
            return { start: new Date(), end: new Date() };
        }

        let start, end;

        switch (period.toLowerCase()) {
            case 'day':
                start = new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0);
                end = new Date(d.getFullYear(), d.getMonth(), d.getDate(), 23, 59, 59);
                break;

            case 'week':
                // Start on Monday
                const dayOfWeek = d.getDay();
                const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
                start = new Date(d);
                start.setDate(d.getDate() + diff);
                start.setHours(0, 0, 0, 0);
                end = new Date(start);
                end.setDate(start.getDate() + 6);
                end.setHours(23, 59, 59, 999);
                break;

            case 'month':
                start = new Date(d.getFullYear(), d.getMonth(), 1, 0, 0, 0);
                end = new Date(d.getFullYear(), d.getMonth() + 1, 0, 23, 59, 59);
                break;

            case 'quarter':
                const quarter = Math.floor(d.getMonth() / 3);
                start = new Date(d.getFullYear(), quarter * 3, 1, 0, 0, 0);
                end = new Date(d.getFullYear(), (quarter + 1) * 3, 0, 23, 59, 59);
                break;

            case 'year':
                start = new Date(d.getFullYear(), 0, 1, 0, 0, 0);
                end = new Date(d.getFullYear(), 11, 31, 23, 59, 59);
                break;

            default:
                start = new Date(d);
                end = new Date(d);
        }

        return { start, end };

    } catch (error) {
        console.error('Error getting period bounds:', error);
        return { start: new Date(), end: new Date() };
    }
}

/**
 * Generates a date range array
 *
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @param {string} step - Step size: 'day', 'week', 'month'
 * @returns {Date[]} Array of dates
 */
function generateDateRange(startDate, endDate, step = 'day') {
    try {
        const start = startDate instanceof Date ? new Date(startDate) : new Date(startDate);
        const end = endDate instanceof Date ? new Date(endDate) : new Date(endDate);

        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            return [];
        }

        const dates = [];
        const current = new Date(start);

        while (current <= end) {
            dates.push(new Date(current));

            switch (step.toLowerCase()) {
                case 'day':
                    current.setDate(current.getDate() + 1);
                    break;
                case 'week':
                    current.setDate(current.getDate() + 7);
                    break;
                case 'month':
                    current.setMonth(current.getMonth() + 1);
                    break;
                default:
                    current.setDate(current.getDate() + 1);
            }
        }

        return dates;

    } catch (error) {
        console.error('Error generating date range:', error);
        return [];
    }
}

/**
 * Formats a duration in milliseconds to human-readable string
 *
 * @param {number} durationMs - Duration in milliseconds
 * @param {boolean} verbose - Use verbose format (default: false)
 * @returns {string} Formatted duration
 *
 * @example
 * formatDuration(7200000) // "2h"
 * formatDuration(7200000, true) // "2 hours"
 */
function formatDuration(durationMs, verbose = false) {
    try {
        const seconds = Math.floor(durationMs / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (verbose) {
            const parts = [];

            if (days > 0) parts.push(`${days} ${days === 1 ? 'day' : 'days'}`);
            if (hours % 24 > 0) parts.push(`${hours % 24} ${hours % 24 === 1 ? 'hour' : 'hours'}`);
            if (minutes % 60 > 0) parts.push(`${minutes % 60} ${minutes % 60 === 1 ? 'minute' : 'minutes'}`);
            if (seconds % 60 > 0 && days === 0) parts.push(`${seconds % 60} ${seconds % 60 === 1 ? 'second' : 'seconds'}`);

            return parts.join(', ') || '0 seconds';
        } else {
            if (days > 0) return `${days}d ${hours % 24}h`;
            if (hours > 0) return `${hours}h ${minutes % 60}m`;
            if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
            return `${seconds}s`;
        }

    } catch (error) {
        console.error('Error formatting duration:', error);
        return '0s';
    }
}

/**
 * Gets ISO week number for a date
 *
 * @param {Date|string} date - Date to check
 * @returns {number} ISO week number (1-53)
 */
function getWeekNumber(date) {
    try {
        const d = date instanceof Date ? new Date(date) : new Date(date);

        if (isNaN(d.getTime())) {
            return 1;
        }

        d.setHours(0, 0, 0, 0);
        d.setDate(d.getDate() + 4 - (d.getDay() || 7));
        const yearStart = new Date(d.getFullYear(), 0, 1);
        const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);

        return weekNo;

    } catch (error) {
        console.error('Error getting week number:', error);
        return 1;
    }
}

/**
 * Checks if a date is a weekend
 *
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if weekend (Saturday or Sunday)
 */
function isWeekend(date) {
    try {
        const d = date instanceof Date ? date : new Date(date);
        const day = d.getDay();
        return day === 0 || day === 6;
    } catch (error) {
        return false;
    }
}

/**
 * Checks if a date is today
 *
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if today
 */
function isToday(date) {
    try {
        const d = date instanceof Date ? date : new Date(date);
        const today = new Date();

        return d.getDate() === today.getDate() &&
               d.getMonth() === today.getMonth() &&
               d.getFullYear() === today.getFullYear();
    } catch (error) {
        return false;
    }
}

// Export functions for use in Templater
module.exports = {
    formatRelativeDate,
    formatDate,
    parseDate,
    calculateBusinessDays,
    modifyDate,
    getPeriodBounds,
    generateDateRange,
    formatDuration,
    getWeekNumber,
    isWeekend,
    isToday
};
