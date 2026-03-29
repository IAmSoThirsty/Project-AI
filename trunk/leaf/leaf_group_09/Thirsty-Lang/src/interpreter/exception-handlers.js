/**
 * Exception Handlers Module
 * Provides try/catch/finally/throw functionality for error handling
 *
 * MAXIMUM ALLOWED DESIGN:
 * - Complete exception handling with stack traces
 * - Support for typed exceptions
 * - Finally block with guaranteed execution
 * - Nested try/catch support
 * - Error propagation and bubbling
 * - Integration with existing error system
 */

/**
 * ThirstyError - Base error class for Thirsty-lang exceptions
 */
class ThirstyError extends Error {
  constructor(message, type = 'Error', context = {}) {
    super(message);
    this.name = `Thirsty${type}`;
    this.thirstyType = type;
    this.context = context;
    this.timestamp = new Date().toISOString();

    // Capture stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ThirstyError);
    }
  }

  /**
   * Convert to Thirsty-lang error object
   */
  toThirstyObject() {
    return {
      message: this.message,
      type: this.thirstyType,
      name: this.name,
      stack: this.stack,
      context: this.context,
      timestamp: this.timestamp
    };
  }

  /**
   * Create from JavaScript Error
   */
  static fromError(err, context = {}) {
    if (err instanceof ThirstyError) {
      return err;
    }
    const thirstyErr = new ThirstyError(err.message, 'Error', context);
    thirstyErr.stack = err.stack;
    return thirstyErr;
  }
}

/**
 * Exception Handlers class for try/catch/finally/throw
 */
class ExceptionHandlers {
  constructor(interpreter) {
    this.interpreter = interpreter;
    this.exceptionStack = []; // Track exception context
  }

  /**
   * Handle try block
   *
   * Syntax:
   *   try {
   *     // code that may throw
   *   } catch (error) {
   *     // error handling
   *   } finally {
   *     // cleanup (optional)
   *   }
   */
  handleTry(lines, startIndex) {
    const line = lines[startIndex].trim();

    if (!line.match(/^try\s*{$/)) {
      throw new Error(`Invalid try statement: ${line}`);
    }

    // Find try block boundaries
    const tryBlockEnd = this.interpreter.findMatchingBrace(lines, startIndex);
    if (tryBlockEnd === -1) {
      throw new Error(`Unmatched opening brace for try block at line ${startIndex + 1}`);
    }

    // Look for catch block
    let catchStart = -1;
    let catchEnd = -1;
    let catchVar = null;
    let finallyStart = -1;
    let finallyEnd = -1;

    let nextIdx = tryBlockEnd;

    // Check for catch block - could be on same line as closing brace or next line
    let catchLine = lines[nextIdx].trim();

    // Check if catch is on the closing brace line (e.g., "} catch (e) {")
    const inlineCatchMatch = catchLine.match(/}\s*catch\s*\((\w+)\)\s*{$/);
    if (inlineCatchMatch) {
      catchVar = inlineCatchMatch[1];
      catchStart = nextIdx + 1;
      // Find the catch block's closing brace using a custom search
      catchEnd = this.findNextMatchingBrace(lines, nextIdx);

      if (catchEnd === -1) {
        throw new Error(`Unmatched opening brace for catch block at line ${nextIdx + 1}`);
      }

      nextIdx = catchEnd;
    } else {
      // Check next line for catch
      nextIdx = tryBlockEnd + 1;
      if (nextIdx < lines.length) {
        catchLine = lines[nextIdx].trim();
        const catchMatch = catchLine.match(/^catch\s*\((\w+)\)\s*{$/);

        if (catchMatch) {
          catchVar = catchMatch[1];
          catchStart = nextIdx + 1;
          catchEnd = this.interpreter.findMatchingBrace(lines, nextIdx);

          if (catchEnd === -1) {
            throw new Error(`Unmatched opening brace for catch block at line ${nextIdx + 1}`);
          }

          nextIdx = catchEnd;
        }
      }
    }

    // Check for finally block - could be on same line as closing brace or next line
    let finallyLine = lines[nextIdx].trim();

    // Check if finally is on the closing brace line (e.g., "} finally {")
    const inlineFinallyMatch = finallyLine.match(/}\s*finally\s*{$/);
    if (inlineFinallyMatch) {
      finallyStart = nextIdx + 1;
      finallyEnd = this.findNextMatchingBrace(lines, nextIdx);

      if (finallyEnd === -1) {
        throw new Error(`Unmatched opening brace for finally block at line ${nextIdx + 1}`);
      }

      nextIdx = finallyEnd;
    } else {
      // Check next line for finally
      nextIdx = nextIdx + 1;
      if (nextIdx < lines.length) {
        finallyLine = lines[nextIdx].trim();

        if (finallyLine === 'finally {') {
          finallyStart = nextIdx + 1;
          finallyEnd = this.interpreter.findMatchingBrace(lines, nextIdx);

          if (finallyEnd === -1) {
            throw new Error(`Unmatched opening brace for finally block at line ${nextIdx + 1}`);
          }

          nextIdx = finallyEnd;
        }
      }
    }

    // Must have at least catch or finally
    if (catchStart === -1 && finallyStart === -1) {
      throw new Error('try block must have at least a catch or finally block');
    }

    // Execute try block with exception handling
    let caughtError = null;
    let tryResult = null;

    try {
      // Push exception context
      this.exceptionStack.push({
        type: 'try',
        lineStart: startIndex,
        lineEnd: tryBlockEnd
      });

      // Execute try block
      const tryLines = lines.slice(startIndex + 1, tryBlockEnd);
      tryResult = this.interpreter.executeBlock(tryLines, 0);

    } catch (err) {
      // Catch any error (including returns)
      if (err && err.type === 'return') {
        // Return statements propagate through
        caughtError = err;
      } else {
        // Regular error - convert to ThirstyError
        caughtError = ThirstyError.fromError(err, {
          tryBlock: true,
          lineStart: startIndex,
          lineEnd: tryBlockEnd
        });
      }
    } finally {
      this.exceptionStack.pop();
    }

    // Execute catch block if error was caught and catch exists
    if (caughtError && caughtError.type !== 'return' && catchStart !== -1) {
      try {
        // Push exception context
        this.exceptionStack.push({
          type: 'catch',
          lineStart: catchStart - 1,
          lineEnd: catchEnd,
          error: caughtError
        });

        // Set catch variable to error object
        if (caughtError instanceof ThirstyError) {
          this.interpreter.variables[catchVar] = caughtError.toThirstyObject();
        } else {
          this.interpreter.variables[catchVar] = {
            message: String(caughtError),
            type: 'Error',
            stack: null
          };
        }

        // Execute catch block
        const catchLines = lines.slice(catchStart, catchEnd);
        this.interpreter.executeBlock(catchLines, 0);

        // Error was handled
        caughtError = null;

      } catch (catchErr) {
        // Error in catch block becomes new error
        if (catchErr && catchErr.type === 'return') {
          caughtError = catchErr;
        } else {
          caughtError = ThirstyError.fromError(catchErr, {
            catchBlock: true,
            originalError: caughtError
          });
        }
      } finally {
        this.exceptionStack.pop();
      }
    }

    // Execute finally block (guaranteed)
    if (finallyStart !== -1) {
      try {
        this.exceptionStack.push({
          type: 'finally',
          lineStart: finallyStart - 1,
          lineEnd: finallyEnd
        });

        const finallyLines = lines.slice(finallyStart, finallyEnd);
        this.interpreter.executeBlock(finallyLines, 0);

      } catch (finallyErr) {
        // Error in finally block overrides previous error
        if (finallyErr && finallyErr.type === 'return') {
          caughtError = finallyErr;
        } else {
          caughtError = ThirstyError.fromError(finallyErr, {
            finallyBlock: true,
            originalError: caughtError
          });
        }
      } finally {
        this.exceptionStack.pop();
      }
    }

    // Re-throw uncaught error
    if (caughtError) {
      throw caughtError;
    }

    // Return index after all blocks
    return nextIdx;
  }

  /**
   * Handle throw statement
   *
   * Syntax:
   *   throw "error message"
   *   throw expression
   *   throw { message: "...", type: "..." }
   */
  handleThrow(line) {
    const throwMatch = line.match(/^throw\s+(.+)$/);

    if (!throwMatch) {
      throw new Error(`Invalid throw statement: ${line}`);
    }

    const expression = throwMatch[1].trim();

    // Evaluate the expression to throw
    let value;
    try {
      value = this.interpreter.evaluateExpression(expression);
    } catch (err) {
      throw new ThirstyError('Error evaluating throw expression', 'EvaluationError', {
        expression,
        cause: err.message
      });
    }

    // Create ThirstyError from thrown value
    let error;

    if (typeof value === 'string') {
      error = new ThirstyError(value, 'ThrownError');
    } else if (typeof value === 'object' && value !== null) {
      const message = value.message || String(value);
      const type = value.type || 'ThrownError';
      error = new ThirstyError(message, type, value);
    } else {
      error = new ThirstyError(String(value), 'ThrownError');
    }

    throw error;
  }

  /**
   * Get current exception context
   */
  getExceptionContext() {
    return this.exceptionStack[this.exceptionStack.length - 1] || null;
  }

  /**
   * Get full exception stack
   */
  getExceptionStack() {
    return [...this.exceptionStack];
  }

  /**
   * Find matching brace for inline catch/finally blocks
   * Starts from a line that contains both } and { (e.g., "} catch (e) {")
   */
  findNextMatchingBrace(lines, startIndex) {
    let braceCount = 1;
    let i = startIndex + 1;

    while (i < lines.length && braceCount > 0) {
      const currentLine = lines[i].trim();

      // Count all opening braces
      const openCount = (currentLine.match(/{/g) || []).length;
      const closeCount = (currentLine.match(/}/g) || []).length;

      braceCount += openCount - closeCount;

      if (braceCount === 0) {
        return i;
      }

      i++;
    }

    return -1; // No matching brace found
  }
}

module.exports = { ExceptionHandlers, ThirstyError };
