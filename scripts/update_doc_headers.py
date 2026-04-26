#                                           [2026-03-04 10:02]
#                                          Productivity: Active
# Project-AI Document Header Synchronizer
# Usage: python update_docs.py

import os
import re

CURRENT_TIME = "2026-03-04 09:48"
DOCS_DIR = "docs"

HEADER_PATTERN = re.compile(
    r"<!--\s*\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]\s*-->\n<!--\s*Productivity: \w+\s*-->"
)
NEW_HEADER = f"<!--                                         [{CURRENT_TIME}] -->\n<!--                                        Productivity: Active -->"


def update_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if content.startswith("<!--"):
        # Replace existing header
        new_content = HEADER_PATTERN.sub(NEW_HEADER, content, count=1)
        if new_content == content:
            # Pattern didn't match exactly, maybe different spacing, let's just prepend if not matched and it looks like a header
            # Or more aggressively replace the first two lines if they are comments
            lines = content.splitlines()
            if (
                len(lines) >= 2
                and lines[0].strip().startswith("<!--")
                and lines[1].strip().startswith("<!--")
            ):
                lines[0] = (
                    f"<!--                                         [{CURRENT_TIME}] -->"
                )
                lines[1] = (
                    "<!--                                        Productivity: Active -->"
                )
                new_content = "\n".join(lines)
    else:
        new_content = NEW_HEADER + "\n" + content

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {filepath}")


def main():
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                update_file(os.path.join(root, file))


if __name__ == "__main__":
    main()
