---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.file.last_modified_date("YYYY-MM-DD") %>
type: code-review
category: development
status: in-progress
pr_number: <% tp.system.prompt("PR number", "") %>
pr_title: <% tp.system.prompt("PR title", "") %>
author: <% tp.system.prompt("PR author", "") %>
reviewer: <% tp.system.prompt("Reviewer name", "") %>
language: <% tp.system.prompt("Primary language (Python/JavaScript/TypeScript/etc)", "Python") %>
component: <% tp.system.prompt("Component/module name", "") %>
review_date: <% tp.file.creation_date("YYYY-MM-DD") %>
tags: [code-review, quality, development]
aliases: []
---

# Code Review: <%* tR += tp.frontmatter.pr_title %>

## Review Information

| Field | Value |
|-------|-------|
| **PR Number** | #<% tp.frontmatter.pr_number %> |
| **Author** | <% tp.frontmatter.author %> |
| **Reviewer** | <% tp.frontmatter.reviewer %> |
| **Review Date** | <% tp.frontmatter.review_date %> |
| **Language** | <% tp.frontmatter.language %> |
| **Component** | <% tp.frontmatter.component %> |

**PR Link:** 

**Related Issues:**
- 

---

## Change Summary

### What Changed?



### Why Was This Change Made?



### Files Modified

| File | Lines Added | Lines Deleted | Impact |
|------|-------------|---------------|--------|
| | | | |
| | | | |
| | | | |

---

## Code Quality Checklist

### 1. Code Structure & Organization

- [ ] **Single Responsibility:** Each function/class has one clear purpose
- [ ] **DRY Principle:** No unnecessary code duplication
- [ ] **Separation of Concerns:** Logic properly separated
- [ ] **Modularity:** Code is well-organized into modules
- [ ] **Naming:** Clear, descriptive names for variables, functions, classes

**Notes:**


---

### 2. Functionality & Logic

- [ ] **Correctness:** Code does what it's supposed to do
- [ ] **Edge Cases:** All edge cases are handled
- [ ] **Error Handling:** Appropriate error handling implemented
- [ ] **Input Validation:** All inputs are validated
- [ ] **Business Logic:** Aligns with requirements

**Issues Found:**


**Recommendations:**


---

### 3. Code Readability

- [ ] **Clarity:** Code is easy to understand
- [ ] **Comments:** Complex logic is explained
- [ ] **No Over-commenting:** Code is self-documenting where possible
- [ ] **Formatting:** Consistent indentation and spacing
- [ ] **Line Length:** Lines are reasonably short (<120 chars)

**Readability Score:** ⭐⭐⭐⭐⭐ (1-5)

**Notes:**


---

### 4. Performance

- [ ] **Efficiency:** No unnecessary operations
- [ ] **Algorithm Choice:** Appropriate algorithms used
- [ ] **Database Queries:** Optimized (no N+1 queries)
- [ ] **Caching:** Appropriate use of caching
- [ ] **Resource Usage:** Memory and CPU usage considered

**Performance Concerns:**


**Optimization Suggestions:**


---

### 5. Security

- [ ] **Input Sanitization:** All user inputs are sanitized
- [ ] **SQL Injection:** Protected against SQL injection
- [ ] **XSS Prevention:** Protected against XSS attacks
- [ ] **CSRF Protection:** CSRF tokens used where needed
- [ ] **Authentication:** Proper authentication checks
- [ ] **Authorization:** Proper permission checks
- [ ] **Sensitive Data:** No hardcoded secrets or credentials
- [ ] **Encryption:** Sensitive data is encrypted
- [ ] **Logging:** No sensitive data in logs

**Security Issues (CRITICAL):**


**Security Recommendations:**


---

### 6. Testing

- [ ] **Unit Tests:** Adequate unit test coverage
- [ ] **Integration Tests:** Integration points tested
- [ ] **Test Quality:** Tests are meaningful and comprehensive
- [ ] **Test Data:** Appropriate test data used
- [ ] **Mocking:** Dependencies properly mocked
- [ ] **Edge Cases:** Edge cases are tested
- [ ] **Error Cases:** Error scenarios are tested
- [ ] **All Tests Pass:** No failing tests

**Test Coverage:** ____%

**Testing Gaps:**


**Additional Tests Needed:**


---

### 7. Documentation

- [ ] **Code Comments:** Complex logic is documented
- [ ] **Docstrings:** Functions/classes have proper docstrings
- [ ] **API Documentation:** Public APIs are documented
- [ ] **README:** README updated if needed
- [ ] **CHANGELOG:** CHANGELOG updated
- [ ] **Migration Guide:** Breaking changes documented

**Documentation Quality:** ⭐⭐⭐⭐⭐ (1-5)

**Documentation Gaps:**


---

### 8. Best Practices (Language-Specific)

<%* if (tp.frontmatter.language === "Python") { %>
#### Python Specific

- [ ] **PEP 8:** Follows PEP 8 style guide
- [ ] **Type Hints:** Type hints used where appropriate
- [ ] **Context Managers:** Proper use of `with` statements
- [ ] **Exceptions:** Appropriate exception classes
- [ ] **List Comprehensions:** Used where appropriate
- [ ] **Generators:** Used for large datasets where appropriate

<%* } else if (tp.frontmatter.language === "JavaScript" || tp.frontmatter.language === "TypeScript") { %>
#### JavaScript/TypeScript Specific

- [ ] **ESLint:** No linting errors
- [ ] **Const/Let:** Proper use of `const`/`let` (no `var`)
- [ ] **Arrow Functions:** Appropriate use of arrow functions
- [ ] **Promises:** Async operations handled properly
- [ ] **TypeScript:** Proper typing (if TypeScript)
- [ ] **Modern Syntax:** ES6+ features used appropriately

<%* } %>

**Style Guide Compliance:**


---

### 9. Architecture & Design

- [ ] **Design Patterns:** Appropriate patterns used
- [ ] **SOLID Principles:** Code follows SOLID principles
- [ ] **Dependencies:** Minimal and appropriate dependencies
- [ ] **Coupling:** Low coupling between components
- [ ] **Cohesion:** High cohesion within components
- [ ] **Scalability:** Design supports future growth

**Architectural Concerns:**


**Design Recommendations:**


---

### 10. Integration & Compatibility

- [ ] **API Compatibility:** No breaking changes to public APIs
- [ ] **Backward Compatibility:** Maintains backward compatibility
- [ ] **Database Migrations:** Migrations are reversible
- [ ] **Third-Party Integration:** External services handled properly
- [ ] **Environment Configuration:** Works across environments

**Integration Issues:**


---

### 11. Error Handling & Logging

- [ ] **Try-Catch:** Appropriate use of exception handling
- [ ] **Error Messages:** Clear, actionable error messages
- [ ] **Logging Levels:** Appropriate log levels (DEBUG, INFO, WARN, ERROR)
- [ ] **Structured Logging:** Logs are structured and searchable
- [ ] **No Swallowed Errors:** Errors are not silently ignored
- [ ] **Graceful Degradation:** System fails gracefully

**Error Handling Quality:** ⭐⭐⭐⭐⭐ (1-5)

**Logging Issues:**


---

### 12. Code Smells & Anti-Patterns

**Identified Code Smells:**
- [ ] Long methods (>50 lines)
- [ ] Large classes (>500 lines)
- [ ] Too many parameters (>5)
- [ ] Deep nesting (>4 levels)
- [ ] Magic numbers
- [ ] God objects
- [ ] Other: _______________

**Refactoring Recommendations:**


---

## Language-Specific Deep Dive

<%* if (tp.frontmatter.language === "Python") { %>
### Python-Specific Review

#### Imports
- [ ] All imports used
- [ ] No circular imports
- [ ] Grouped correctly (stdlib, third-party, local)

#### Memory Management
- [ ] Large objects properly released
- [ ] File handles closed
- [ ] Database connections managed

#### Pythonic Practices
- [ ] Uses Python idioms effectively
- [ ] Appropriate use of built-in functions
- [ ] List comprehensions over loops where clear

**Python-Specific Issues:**


<%* } else if (tp.frontmatter.language === "JavaScript") { %>
### JavaScript-Specific Review

#### Async Handling
- [ ] Promises handled correctly
- [ ] No callback hell
- [ ] Async/await used appropriately

#### Browser Compatibility
- [ ] Polyfills for older browsers if needed
- [ ] Feature detection used

#### Event Handling
- [ ] Event listeners removed when no longer needed
- [ ] No memory leaks from closures

**JavaScript-Specific Issues:**


<%* } %>

---

## Review Outcome

### Overall Assessment

**Quality Score:** ___/100

**Risk Level:**
- [ ] Low (approve immediately)
- [ ] Medium (approve with minor changes)
- [ ] High (requires significant changes)
- [ ] Critical (fundamental issues, do not merge)

### Decision

- [ ] ✅ **APPROVED** - Ready to merge
- [ ] ⚠️ **APPROVED WITH COMMENTS** - Can merge after addressing comments
- [ ] 🔄 **CHANGES REQUESTED** - Must address issues before merge
- [ ] ❌ **REJECTED** - Fundamental issues, complete rework needed

---

## Critical Issues (Must Fix Before Merge)

<%* const numCritical = parseInt(tp.system.prompt("Number of critical issues (0 if none)", "0")); %>
<%* if (numCritical > 0) { %>
<%* for (let i = 1; i <= numCritical; i++) { %>
### Critical Issue <%* tR += i %>

**Location:** `<% tp.system.prompt(`Issue ${i} file:line`, "") %>`
**Severity:** Critical
**Category:** Security | Bug | Performance | Other

**Issue:**


**Recommendation:**


**Status:**
- [ ] Acknowledged
- [ ] Fixed
- [ ] Verified

---
<%* } %>
<%* } else { %>
> ✅ No critical issues identified

<%* } %>

## Major Issues (Should Fix)

1. 
2. 
3. 

## Minor Issues (Nice to Have)

1. 
2. 
3. 

## Positive Observations

**What Was Done Well:**
- 
- 
- 

**Exemplary Practices:**
- 
- 

---

## Learning Opportunities

**For Author:**
- 
- 

**For Team:**
- 
- 

**Documentation to Create/Update:**
- 
- 

---

## Follow-up Actions

- [ ] Address critical issues
- [ ] Address major issues
- [ ] Consider minor improvements
- [ ] Update tests
- [ ] Update documentation
- [ ] Re-review after changes
- [ ] Merge approved changes

**Re-review Required:** Yes / No
**Re-reviewer:** _______________

---

## Metrics

| Metric | Value |
|--------|-------|
| Files Changed | |
| Lines Added | |
| Lines Deleted | |
| Net Change | |
| Cyclomatic Complexity | |
| Test Coverage | |
| Review Duration | <% tp.system.prompt("Review duration (minutes)", "") %> min |

---

## Additional Notes



---

## Reviewer Checklist (Final)

- [ ] All checklist items reviewed
- [ ] Code executed locally
- [ ] Tests run and passing
- [ ] Security implications considered
- [ ] Performance implications considered
- [ ] Documentation reviewed
- [ ] Breaking changes identified
- [ ] Feedback provided constructively
- [ ] Decision recorded

**Reviewer Signature:** <% tp.frontmatter.reviewer %>
**Review Completed:** <% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>

---

## Related Reviews

- 

## References

- 
- 

---

**Review Template Version:** 2.0
**Last Updated:** 2026-04-20

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

