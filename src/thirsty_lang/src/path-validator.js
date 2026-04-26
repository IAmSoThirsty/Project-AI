/**
 * Path Validation Utility
 * Provides security functions to prevent path traversal attacks
 */

const path = require('path');
const fs = require('fs');

/**
 * Validates and sanitizes a file path to prevent path traversal attacks
 * @param {string} userPath - The user-provided path
 * @param {string} baseDir - The base directory that should contain the file (optional)
 * @returns {string} - The validated and normalized path
 * @throws {Error} - If the path is invalid or attempts traversal
 */
function validatePath(userPath, baseDir = null) {
  if (!userPath || typeof userPath !== 'string') {
    throw new Error('Invalid path: path must be a non-empty string');
  }

  // Remove null bytes
  if (userPath.indexOf('\0') !== -1) {
    throw new Error('Invalid path: contains null bytes');
  }

  // Normalize the path to resolve '..' and '.' sequences
  const normalizedPath = path.normalize(userPath);

  // Check for suspicious patterns
  const suspiciousPatterns = [
    /\.\.[\/\\]/,  // Parent directory traversal
    /^[\/\\]/,     // Absolute path (unless baseDir is not set)
    /[<>:"|?*]/    // Invalid filename characters on Windows
  ];

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(userPath) && baseDir) {
      throw new Error('Invalid path: contains suspicious patterns');
    }
  }

  // If baseDir is provided, ensure the path stays within it
  if (baseDir) {
    const resolvedBase = path.resolve(baseDir);
    const resolvedPath = path.resolve(baseDir, normalizedPath);

    // Verify the resolved path is within the base directory
    if (!resolvedPath.startsWith(resolvedBase + path.sep) && resolvedPath !== resolvedBase) {
      throw new Error('Invalid path: attempts to access files outside allowed directory');
    }

    return resolvedPath;
  }

  return normalizedPath;
}

/**
 * Validates that a file path uses only allowed extensions
 * @param {string} filePath - The file path to validate
 * @param {Array<string>} allowedExtensions - Array of allowed extensions (e.g., ['.thirsty', '.js'])
 * @returns {boolean} - True if extension is allowed
 */
function validateExtension(filePath, allowedExtensions) {
  const ext = path.extname(filePath).toLowerCase();
  return allowedExtensions.some(allowed => allowed.toLowerCase() === ext);
}

/**
 * Safely joins paths and validates the result
 * @param {string} basePath - The base directory
 * @param {...string} segments - Path segments to join
 * @returns {string} - The safely joined and validated path
 */
function safeJoin(basePath, ...segments) {
  const joined = path.join(basePath, ...segments);
  return validatePath(joined, basePath);
}

/**
 * Validates that a path exists and is a file
 * @param {string} filePath - The file path to check
 * @returns {boolean} - True if path exists and is a file
 */
function isValidFile(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return stats.isFile();
  } catch (error) {
    return false;
  }
}

/**
 * Validates that a path exists and is a directory
 * @param {string} dirPath - The directory path to check
 * @returns {boolean} - True if path exists and is a directory
 */
function isValidDirectory(dirPath) {
  try {
    const stats = fs.statSync(dirPath);
    return stats.isDirectory();
  } catch (error) {
    return false;
  }
}

module.exports = {
  validatePath,
  validateExtension,
  safeJoin,
  isValidFile,
  isValidDirectory
};
