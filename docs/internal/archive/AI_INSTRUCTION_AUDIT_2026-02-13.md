# AI Assistant Instruction Audit Report

**Date:** February 13, 2026 **Issue:** Repetitive bash command execution causing malfunction **Status:** ✅ RESOLVED

______________________________________________________________________

## Executive Summary

An audit of the AI assistant instruction files revealed that overly prescriptive directives in `.github/instructions/codacy.instructions.md` were causing AI assistants to repeatedly execute the same bash commands, leading to apparent malfunctions and degraded user experience.

### Root Cause

The Codacy instructions file contained multiple **absolute mandates** requiring tool execution after every file edit:

1. **Line 13 (Original):** "YOU MUST IMMEDIATELY run the `codacy_cli_analyze` tool"
1. **Line 29 (Original):** "After every response - verify you ran `codacy_cli_analyze` tool"
1. **Line 51 (Original):** "You MUST run the `codacy_cli_analyze` tool" (for dependencies)
1. **Line 68 (Original):** "You MUST NOT wait for the user to ask for analysis"

These directives created a feedback loop where:

- AI assistants felt compelled to run the tool after every edit
- If the tool was unavailable, they would retry or check again
- The verification requirement in line 29 caused re-checking in subsequent responses
- This resulted in dozens of identical command attempts

______________________________________________________________________

## Changes Implemented

### 1. Modified `.github/instructions/codacy.instructions.md`

#### Before (Problematic)

```markdown

## CRITICAL: After ANY successful `edit_file` or `reapply` operation

- YOU MUST IMMEDIATELY run the `codacy_cli_analyze` tool...
- > NOTE: Failure to follow this rule is considered a critical error.

## After every response

- If you made any file edits, verify you ran `codacy_cli_analyze` tool

## CRITICAL: Dependencies and Security Checks

- IMMEDIATELY after ANY of these actions...
- You MUST run the `codacy_cli_analyze` tool...

```

#### After (Fixed)

```markdown

## Code Quality Checks (When Applicable)

**When to run `codacy_cli_analyze`:**

- After making code changes to Python, JavaScript, or other source files
- When the Codacy MCP Server tools are available
- If the tool has not already been run for the current file in this session

**Circuit Breaker Rules:**

- Do NOT run the tool more than once per file per editing session
- Do NOT retry if the tool fails due to unavailability
- Do NOT run for non-code files

## Session Management

- Track which files have been analyzed in the current session
- Avoid redundant analysis of the same file
- If analysis was already performed, skip it and continue

## OPTIONAL: Dependencies and Security Checks

- You MAY optionally run the tool (not mandatory)
- **Do NOT block progress** if the tool is unavailable

## Anti-Repetition Safeguards

**IMPORTANT: Prevent infinite loops**

- Maximum 1 analysis per file per session
- If a tool call fails, log it and move on (do NOT retry automatically)
- Prioritize task completion over perfect analysis

```

### 2. Modified `.github/copilot-instructions.md`

Changed line 293 from:

```markdown
**Codacy integration**: After file edits, MUST run `codacy_cli_analyze`
```

To:

```markdown
**Codacy integration** (OPTIONAL): After file edits, may run `codacy_cli_analyze` if available

- Not mandatory - prioritize task completion over perfect analysis

```

______________________________________________________________________

## Key Improvements

### 1. Conditional vs. Mandatory Execution

- **Before:** Absolute mandates ("MUST", "IMMEDIATELY", "CRITICAL")
- **After:** Conditional guidelines ("When applicable", "If available", "MAY optionally")

### 2. Circuit Breaker Pattern

Added explicit safeguards:

- Maximum 1 analysis per file per session
- No automatic retries on failure
- Skip analysis if tool unavailable

### 3. Session State Tracking

- Introduced concept of tracking analyzed files
- Prevents redundant analysis
- Reduces command repetition

### 4. Priority Clarity

- Explicitly prioritize task completion over perfect analysis
- Don't block progress if tools unavailable
- Balance quality checks with workflow efficiency

### 5. Scope Limitations

Clarified when NOT to run tools:

- Non-code files (markdown, configs, etc.)
- Complexity metrics (unless requested)
- Code coverage (use dedicated tools)
- Duplicated code detection (low priority)

______________________________________________________________________

## Impact Assessment

### Before Fix

- **Symptom:** Dozens of identical bash command calls
- **User Experience:** Appears as malfunction/infinite loop
- **Workflow:** Blocked or severely degraded
- **Root Cause:** Overly prescriptive mandatory directives

### After Fix

- **Behavior:** Conditional, single-pass analysis
- **User Experience:** Smooth, efficient workflow
- **Workflow:** Task completion prioritized
- **Design:** Balanced quality with pragmatism

______________________________________________________________________

## Testing Recommendations

To verify the fix is effective:

1. **Edit a Python file** - Tool should run once (if available), then skip on subsequent edits
1. **Edit a markdown file** - Tool should NOT run (non-code file)
1. **Tool unavailable scenario** - AI should skip analysis and continue task
1. **Multiple file edits** - Each file analyzed at most once
1. **Dependency changes** - Optional security check, not blocking

______________________________________________________________________

## Lessons Learned

### Anti-Patterns to Avoid

1. **Absolute Mandates**

   - ❌ "YOU MUST IMMEDIATELY"
   - ✅ "You may optionally"

1. **Verification Loops**

   - ❌ "After every response, verify you ran..."
   - ✅ "Track which files have been analyzed"

1. **Blocking on External Tools**

   - ❌ "Stop all operations until..."
   - ✅ "If unavailable, skip and continue"

1. **Lack of Circuit Breakers**

   - ❌ No retry limits or failure handling
   - ✅ "Maximum 1 analysis per file per session"

### Best Practices for AI Instructions

1. **Use conditional language** for non-critical operations
1. **Implement circuit breakers** to prevent loops
1. **Track state** to avoid redundant operations
1. **Prioritize workflows** over perfect execution
1. **Fail gracefully** when tools unavailable
1. **Limit scope** with explicit exclusions

______________________________________________________________________

## Related Files Modified

- `.github/instructions/codacy.instructions.md` - Major revision
- `.github/copilot-instructions.md` - Minor clarification
- `docs/internal/archive/AI_INSTRUCTION_AUDIT_2026-02-13.md` - This report

______________________________________________________________________

## Recommendations for Future Instruction Design

1. **Review all instruction files** for similar absolute mandate patterns
1. **Add circuit breakers** to any tool-calling instructions
1. **Use state tracking** to prevent redundant operations
1. **Test instructions** with simulated tool failures
1. **Monitor for repetitive behavior** in AI assistant logs
1. **Balance quality vs. efficiency** - don't let perfect be the enemy of good

______________________________________________________________________

## Approval

**Auditor:** Claude (AI Assistant) **Date:** 2026-02-13 **Status:** Changes implemented and documented **Next Review:** When similar issues reported or during quarterly instruction audit

______________________________________________________________________

## Appendix: Command Patterns to Monitor

Watch for these patterns in AI assistant behavior:

```bash

# Warning sign: Same command repeated many times

codacy_cli_analyze --file src/app/main.py
codacy_cli_analyze --file src/app/main.py
codacy_cli_analyze --file src/app/main.py

# ... (dozens of times)

# Expected: Single execution per file

codacy_cli_analyze --file src/app/main.py

# (analysis complete, move on)

```

If repetitive patterns emerge again, review for:

- New absolute mandates in instruction files
- Missing circuit breakers
- Lack of state tracking
- Verification loops
