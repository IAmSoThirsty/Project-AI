#!/usr/bin/env python3
"""
Parse a JUnit XML report (reports/junit.xml) and emit GitHub Actions workflow commands
to create annotations for failing tests.

This is a best-effort annotator: it extracts file and line information from Python-style
tracebacks when available. If no file/line can be determined, it emits a generic error
annotation containing the failure message.

Usage (from workflow):
  python .github/scripts/annotate_junit.py reports/junit.xml

The script prints lines like:
  ::error file=path/to/file.py,line=123::Failure message

GitHub Actions will convert those into annotations in the Checks view.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TRACE_RE = re.compile(r'File "(?P<file>.+?)", line (?P<line>\d+)', re.MULTILINE)


def short_msg(text, max_len=200):
    if not text:
        return "test failed"
    t = text.strip().splitlines()
    if not t:
        return "test failed"
    s = t[0]
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def annotate_failure(message):
    # attempt to find file/line from traceback
    m = TRACE_RE.search(message)
    if m:
        file = m.group("file")
        line = m.group("line")
        # ensure file path is repository-relative if possible
        p = Path(file)
        file_path = str(p) if p.exists() else file
        msg = short_msg(message)
        # GitHub workflow command for an error annotation
        print(f"::error file={file_path},line={line}::{msg}")
    else:
        msg = short_msg(message, max_len=1000)
        # emit a general error annotation without file/line
        print(f"::error ::{msg}")


def main():
    if len(sys.argv) < 2:
        print("Usage: annotate_junit.py <junit-xml-path>", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"JUnit report not found at: {path}", file=sys.stderr)
        sys.exit(0)

    try:
        tree = ET.parse(str(path))
    except ET.ParseError as e:
        print(f"Failed to parse JUnit XML: {e}", file=sys.stderr)
        sys.exit(0)

    root = tree.getroot()
    # Support both <testsuites> and single <testsuite>
    suites = []
    if root.tag == "testsuites":
        suites.extend(root.findall("testsuite"))
    elif root.tag == "testsuite":
        suites.append(root)
    else:
        suites.extend(root.findall(".//testsuite"))

    for suite in suites:
        for case in suite.findall("testcase"):
            failures = case.findall("failure") + case.findall("error")
            for f in failures:
                text = f.text or ""
                annotate_failure(text)


if __name__ == "__main__":
    main()
