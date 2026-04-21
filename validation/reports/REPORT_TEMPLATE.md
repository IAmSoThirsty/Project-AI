# Validation Report Template

## Metadata Validation Summary

**Date:** {{TIMESTAMP}}  
**Validator:** {{VALIDATOR_NAME}}  
**Version:** {{VERSION}}

---

## Executive Summary

This report provides a comprehensive analysis of metadata validation across {{TOTAL_FILES}} documentation files.

### Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total Files Analyzed | {{TOTAL_FILES}} | - |
| Valid Files | {{VALID_FILES}} | {{VALID_STATUS}} |
| Invalid Files | {{INVALID_FILES}} | {{INVALID_STATUS}} |
| Files Skipped | {{SKIPPED_FILES}} | {{SKIPPED_STATUS}} |
| **Total Errors** | {{TOTAL_ERRORS}} | {{ERROR_STATUS}} |
| **Total Warnings** | {{TOTAL_WARNINGS}} | {{WARNING_STATUS}} |

### Performance Metrics

| Metric | Value |
|--------|-------|
| Total Validation Time | {{TOTAL_TIME}}ms |
| Average Time per File | {{AVG_TIME}}ms |
| Minimum Time | {{MIN_TIME}}ms |
| Maximum Time | {{MAX_TIME}}ms |
| **Performance Rating** | {{PERFORMANCE_RATING}} |

---

## Validation Results

### ✅ Valid Files ({{VALID_COUNT}})

{{VALID_FILES_LIST}}

### ❌ Invalid Files ({{INVALID_COUNT}})

{{INVALID_FILES_DETAILS}}

### ⚠ Skipped Files ({{SKIPPED_COUNT}})

{{SKIPPED_FILES_LIST}}

---

## Error Analysis

### Error Distribution by Category

| Category | Count | Percentage |
|----------|-------|------------|
{{ERROR_CATEGORY_TABLE}}

### Error Distribution by Type

| Error Code | Description | Count |
|------------|-------------|-------|
{{ERROR_TYPE_TABLE}}

### Top 5 Most Common Errors

1. {{ERROR_1}}
2. {{ERROR_2}}
3. {{ERROR_3}}
4. {{ERROR_4}}
5. {{ERROR_5}}

---

## Recommendations

### Immediate Actions Required

{{IMMEDIATE_ACTIONS}}

### Medium-Term Improvements

{{MEDIUM_TERM_ACTIONS}}

### Long-Term Enhancements

{{LONG_TERM_ACTIONS}}

---

## Compliance Status

| Standard | Status | Notes |
|----------|--------|-------|
| Required Fields | {{REQUIRED_COMPLIANCE}} | {{REQUIRED_NOTES}} |
| Type Constraints | {{TYPE_COMPLIANCE}} | {{TYPE_NOTES}} |
| Pattern Validation | {{PATTERN_COMPLIANCE}} | {{PATTERN_NOTES}} |
| Array Constraints | {{ARRAY_COMPLIANCE}} | {{ARRAY_NOTES}} |

---

## Quality Metrics

### Documentation Health Score

**Overall Score:** {{HEALTH_SCORE}}/100

- **Completeness:** {{COMPLETENESS_SCORE}}/25
- **Correctness:** {{CORRECTNESS_SCORE}}/25
- **Consistency:** {{CONSISTENCY_SCORE}}/25
- **Compliance:** {{COMPLIANCE_SCORE}}/25

### Trend Analysis

{{TREND_CHART}}

---

## Appendices

### A. Detailed Error Log

```
{{DETAILED_ERROR_LOG}}
```

### B. Validation Configuration

```json
{{VALIDATION_CONFIG}}
```

### C. Schema Version

**Schema Version:** {{SCHEMA_VERSION}}  
**Schema Last Updated:** {{SCHEMA_UPDATED}}

---

## Sign-Off

**Validated By:** {{VALIDATOR}}  
**Reviewed By:** {{REVIEWER}}  
**Approved By:** {{APPROVER}}  
**Date:** {{APPROVAL_DATE}}

---

**Next Review:** {{NEXT_REVIEW_DATE}}  
**Report Generated:** {{REPORT_TIMESTAMP}}
