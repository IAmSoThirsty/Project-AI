/**
 * Standard Library Module
 * Provides built-in Math, String, File, and Http utilities
 */

const fs = require('fs');
const http = require('http');
const https = require('https');

/**
 * Initialize and return standard library objects
 * @returns {Object} Object containing Math, String, File, and Http utilities
 */
function initializeStandardLibrary() {
  return {
    Math: {
      __builtin: true,
      PI: 3.14159265359,
      E: 2.71828182846,
      abs: (x) => Math.abs(x),
      sqrt: (x) => Math.sqrt(x),
      pow: (x, y) => Math.pow(x, y),
      floor: (x) => Math.floor(x),
      ceil: (x) => Math.ceil(x),
      round: (x) => Math.round(x),
      min: (...args) => Math.min(...args),
      max: (...args) => Math.max(...args),
      random: () => Math.random()
    },

    String: {
      __builtin: true,
      toUpperCase: (str) => String(str).toUpperCase(),
      toLowerCase: (str) => String(str).toLowerCase(),
      trim: (str) => String(str).trim(),
      split: (str, separator) => String(str).split(separator),
      replace: (str, search, replacement) => String(str).replace(search, replacement),
      charAt: (str, index) => String(str).charAt(index),
      substring: (str, start, end) => String(str).substring(start, end)
    },

    File: {
      __builtin: true,
      read: (filePath) => {
        try {
          return fs.readFileSync(filePath, 'utf8');
        } catch (err) {
          throw new Error(`Failed to read file: ${err.message}`);
        }
      },
      write: (filePath, content) => {
        try {
          fs.writeFileSync(filePath, String(content), 'utf8');
          return true;
        } catch (err) {
          throw new Error(`Failed to write file: ${err.message}`);
        }
      },
      exists: (filePath) => {
        return fs.existsSync(filePath);
      },
      delete: (filePath) => {
        try {
          fs.unlinkSync(filePath);
          return true;
        } catch (err) {
          throw new Error(`Failed to delete file: ${err.message}`);
        }
      },
      readAsync: async (filePath) => {
        return new Promise((resolve, reject) => {
          fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) reject(new Error(`Failed to read file: ${err.message}`));
            else resolve(data);
          });
        });
      },
      writeAsync: async (filePath, content) => {
        return new Promise((resolve, reject) => {
          fs.writeFile(filePath, String(content), 'utf8', (err) => {
            if (err) reject(new Error(`Failed to write file: ${err.message}`));
            else resolve(true);
          });
        });
      }
    },

    Http: {
      __builtin: true,
      get: (url) => {
        return new Promise((resolve, reject) => {
          const urlObj = new URL(url);
          const protocol = urlObj.protocol === 'https:' ? https : http;

          protocol.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
              resolve({
                status: res.statusCode,
                headers: res.headers,
                body: data
              });
            });
          }).on('error', (err) => {
            reject(new Error(`HTTP GET failed: ${err.message}`));
          });
        });
      },
      post: (url, postData) => {
        return new Promise((resolve, reject) => {
          const urlObj = new URL(url);
          const protocol = urlObj.protocol === 'https:' ? https : http;
          const data = typeof postData === 'string' ? postData : JSON.stringify(postData);

          const options = {
            hostname: urlObj.hostname,
            port: urlObj.port,
            path: urlObj.pathname + urlObj.search,
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Content-Length': Buffer.byteLength(data)
            }
          };

          const req = protocol.request(options, (res) => {
            let responseData = '';
            res.on('data', (chunk) => { responseData += chunk; });
            res.on('end', () => {
              resolve({
                status: res.statusCode,
                headers: res.headers,
                body: responseData
              });
            });
          });

          req.on('error', (err) => {
            reject(new Error(`HTTP POST failed: ${err.message}`));
          });

          req.write(data);
          req.end();
        });
      },
      // Note: fetch is added dynamically in the interpreter since it references this.variables
      _createFetch: function(httpObj) {
        return async (url, options = {}) => {
          const method = (options.method || 'GET').toUpperCase();
          if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
            return httpObj.post(url, options.body || '');
          } else {
            return httpObj.get(url);
          }
        };
      }
    },

    JSON: {
      __builtin: true,

      /**
       * Parse JSON string into Thirsty-lang value
       * Supports all JSON types: null, boolean, number, string, array, object
       * Handles nested structures and provides detailed error messages
       * @param {string} jsonString - JSON string to parse
       * @returns {*} Parsed value (null, boolean, number, string, array, or object)
       * @throws {Error} If JSON is malformed or invalid
       */
      parse: (jsonString) => {
        // Validate input type
        if (typeof jsonString !== 'string') {
          throw new Error(`JSON.parse expects a string, got ${typeof jsonString}`);
        }

        // Handle empty string
        if (jsonString.trim() === '') {
          throw new Error('JSON.parse cannot parse empty string');
        }

        try {
          // Use native JSON.parse for robust parsing
          const result = JSON.parse(jsonString);

          // Convert JavaScript null to Thirsty-lang null (undefined in variables)
          // Arrays and objects are already compatible with Thirsty-lang
          return result;
        } catch (error) {
          // Enhance error message with position information
          const match = error.message.match(/position (\d+)/);
          if (match) {
            const pos = parseInt(match[1], 10);
            const context = jsonString.substring(Math.max(0, pos - 20), Math.min(jsonString.length, pos + 20));
            throw new Error(`JSON.parse failed at position ${pos}: ${error.message}\nContext: ...${context}...`);
          }
          throw new Error(`JSON.parse failed: ${error.message}`);
        }
      },

      /**
       * Convert Thirsty-lang value to JSON string
       * Supports all Thirsty-lang types with configurable formatting
       * Detects circular references to prevent infinite loops
       * @param {*} value - Value to stringify (null, boolean, number, string, array, object, fountain)
       * @param {Function|Array|null} replacer - Optional replacer function or whitelist array
       * @param {string|number} space - Optional indentation (number of spaces or string)
       * @returns {string} JSON string representation
       * @throws {Error} If value contains circular references or unsupported types
       */
      stringify: (value, replacer = null, space = undefined) => {
        // Track visited objects for circular reference detection
        const seen = new WeakSet();

        /**
         * Custom replacer that handles Thirsty-lang types and circular references
         */
        const thirstyReplacer = (key, val) => {
          // Handle circular references
          if (val !== null && typeof val === 'object') {
            if (seen.has(val)) {
              throw new Error(`JSON.stringify cannot serialize circular references (found at key "${key}")`);
            }
            seen.add(val);
          }

          // Handle Thirsty-lang specific types

          // Handle functions (cannot be serialized to JSON)
          if (typeof val === 'function') {
            // Check if it's a Thirsty-lang function with metadata
            if (val.__thirstyFunction) {
              // Return function metadata instead of undefined
              return {
                __type: 'ThirstyFunction',
                name: val.__name || 'anonymous',
                params: val.__params || [],
                body: val.__body || ''
              };
            }
            // Regular functions become undefined in JSON
            return undefined;
          }

          // Handle Thirsty-lang classes
          if (val && val.__thirstyClass) {
            return {
              __type: 'ThirstyClass',
              name: val.__className || 'anonymous',
              properties: Object.keys(val).filter(k => !k.startsWith('__'))
            };
          }

          // Handle undefined (convert to null for JSON compatibility)
          if (val === undefined) {
            return null;
          }

          // Handle built-in markers
          if (val && val.__builtin) {
            return '[Built-in Object]';
          }

          // Apply user-provided replacer if exists
          if (typeof replacer === 'function') {
            return replacer(key, val);
          }

          return val;
        };

        // Handle whitelist array replacer
        if (Array.isArray(replacer)) {
          const whitelist = replacer;
          const whitelistReplacer = (key, val) => {
            if (key === '' || whitelist.includes(key)) {
              return thirstyReplacer(key, val);
            }
            return undefined;
          };

          try {
            return JSON.stringify(value, whitelistReplacer, space);
          } catch (error) {
            throw new Error(`JSON.stringify failed: ${error.message}`);
          }
        }

        // Combine user replacer with Thirsty-lang replacer
        const combinedReplacer = (key, val) => {
          const thirstyVal = thirstyReplacer(key, val);
          if (typeof replacer === 'function') {
            return replacer(key, thirstyVal);
          }
          return thirstyVal;
        };

        try {
          return JSON.stringify(value, combinedReplacer, space);
        } catch (error) {
          // Provide more helpful error messages
          if (error.message.includes('circular')) {
            throw error; // Already handled by our custom logic
          }
          throw new Error(`JSON.stringify failed: ${error.message}`);
        }
      },

      /**
       * Check if a string is valid JSON
       * Non-throwing validation method
       * @param {string} jsonString - String to validate
       * @returns {boolean} True if valid JSON, false otherwise
       */
      isValid: (jsonString) => {
        if (typeof jsonString !== 'string') {
          return false;
        }

        if (jsonString.trim() === '') {
          return false;
        }

        try {
          JSON.parse(jsonString);
          return true;
        } catch (error) {
          return false;
        }
      },

      /**
       * Deep clone a value using JSON serialization
       * Warning: Loses functions, symbols, and other non-JSON-serializable data
       * @param {*} value - Value to clone
       * @returns {*} Deep cloned value
       * @throws {Error} If value contains circular references
       */
      clone: (value) => {
        try {
          // Simple deep clone via JSON round-trip
          // Note: This loses functions and other non-serializable data
          const jsonStr = JSON.stringify(value);
          return JSON.parse(jsonStr);
        } catch (error) {
          throw new Error(`JSON.clone failed: ${error.message}`);
        }
      },

      /**
       * Compare two values for deep equality using JSON serialization
       * @param {*} a - First value
       * @param {*} b - Second value
       * @returns {boolean} True if values are deeply equal
       */
      equals: (a, b) => {
        try {
          // Use JSON serialization for deep comparison
          // Note: This may not work correctly for objects with different key orders
          return JSON.stringify(a) === JSON.stringify(b);
        } catch (error) {
          // If serialization fails, fall back to reference equality
          return a === b;
        }
      }
    }
  };
}

module.exports = { initializeStandardLibrary };
