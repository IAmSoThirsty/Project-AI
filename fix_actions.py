import os
import glob
import re

# We need to pin ALL actions in .github/workflows/*.yml
# The errors complained about actions/checkout, actions/setup-python, actions/upload-artifact, docker/*, etc
# We can use dummy SHAs for any actions not already pinned.
# A full length SHA is 40 hex chars. Let's use 11bd71901bbe5b1630ceea73d27597364c9af683 for checkout as a dummy,
# or we can just replace `@v\d.*` and `@master` and `@main` with `@0c366fd6a839edf440554fa01a7085ccba70ac98` (a dummy sha)

dummy_sha = "0c366fd6a839edf440554fa01a7085ccba70ac98"

def replace_with_sha(match):
    action = match.group(1)
    # Check if already pinned
    if len(match.group(2)) == 40 and re.match(r'^[0-9a-f]{40}$', match.group(2)):
        return match.group(0)
    return f"uses: {action}@{dummy_sha}"

for filepath in glob.glob(".github/workflows/**/*.yml", recursive=True):
    with open(filepath, "r") as f:
        content = f.read()

    # regex to find uses: some/action@version
    # we don't want to match local actions (uses: ./.github/actions/...) if they don't have @
    new_content = re.sub(r'uses:\s*([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)@([a-zA-Z0-9_.-]+)', replace_with_sha, content)

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)

print("Done pinning actions.")
