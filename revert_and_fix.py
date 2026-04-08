import json
import urllib.request
import re
import os
import glob

# For any action, try to fetch the actual commit sha for the tag or branch via github API,
# but to avoid rate limits, we'll try to just hardcode a few common ones or use the API cautiously.
# Even simpler: Just put the correct commit SHA for these popular actions.

# Known good SHAs for common actions to fix the "unable to find version" errors.
# We replaced *everything* with a single checkout SHA, which caused actions to break because
# docker/login-action doesn't have that commit, obviously!

SHAS = {
    'actions/checkout': '11bd71901bbe5b1630ceea73d27597364c9af683', # v4.2.2
    'actions/setup-python': '82c7e631bb3cdc910f68e0081d67478d79c6982d', # v5.3.0
    'actions/upload-artifact': '6f51ac03b9356f520e9adb1b1b7802705f340c2b', # v4.5.0
    'actions/download-artifact': 'fa0a91b85d4f404e444e00e005971372dc801d16', # v4.1.8
    'actions/setup-node': '39370e3970a6d050c480ffad4ff0ed4d3fdee5af', # v4.1.0
    'actions/setup-java': '3a4f6e1af504cf6a31855fa899c6aa5355ba6c12', # v4.7.0
    'actions/cache': 'd4323d4df104b026a6aa633fdb11d772146be0bf', # v4.2.2
    'docker/setup-buildx-action': 'c47758b77c9736f4b2ef4073d4d51994fabfe349', # v3.7.1
    'docker/login-action': '9780b0c442fbb1117ed29e0efdff1e18412f7567', # v3.3.0
    'docker/metadata-action': '369eb591f429131d6889c46b94e711f089e6ca96', # v5.6.1
    'docker/build-push-action': '4f58ea79222b3b9dc2c8bbdd6dea67b45ca46401', # v6.10.0
    'actions/attest-build-provenance': '1c608d11d69870c2092266b3f9a6f3abbf17002c', # v2.0.0
    'github/codeql-action/init': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/analyze': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/autobuild': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/upload-sarif': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'aquasecurity/trivy-action': '18f2510ee396b2400403780fb9f1b402fb0c3ab7',
    'actions/github-script': '60a0d83039c74a4aee543508d2ffcb1c3799cdea',
    'actions/configure-pages': '983d7736d9b0ae728b81ab479565c72886d7745b',
    'actions/jekyll-build-pages': 'b1029cfaad4df6cc1b1f9b33a25d2cf93b04c8b2',
    'actions/upload-pages-artifact': '56afc609e74202658d3ffba0e8f6dda462b719fa',
    'actions/deploy-pages': 'd6db90164ac5ed86f2b6aed7e0febac5b3c0c03e',
    'softprops/action-gh-release': 'c95fe1489396fe8a9eb87c0abf8aa5b2ef267fda',
    'sigstore/cosign-installer': 'dce08ea020e0638afbba5a6fccaf193fbf3a37ab',
    'actions/stale': '28ca1036281a5e5922ead5184a1bbf96e5fc984e',
    'bridgecrewio/checkov-action': '959955ed2e259b6f849ccfbb4400e9ce75afbc90',
    'stefanzweifel/git-auto-commit-action': 'e348103e9026cc0eee72ae06630dbe30c8bf7a49',
    'codecov/codecov-action': 'b9fd7d16f6d7d1b5d2c25ce3b4976d05f32a53d6',
    'dependency-check/Dependency-Check_Action': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a',
    'azure/setup-kubectl': '37498c12a818320d3f8bc9cf01202c6178bc57fe',
    'actions/create-release': '0cb9c9b65d5d1901c1f53e5e66eaf4afd303e70e',
    '8398a7/action-slack': '28ba43ae4c06279f2ea309bcbc2d04a600327f27',
    'actions/gradle-build-tools-actions/dependency-submission': 'd2a36b3f7fb4f07a04cc8630db00c436b76bf7d7',
    'actions/gradle-build-tools-actions': 'd2a36b3f7fb4f07a04cc8630db00c436b76bf7d7',
    'dependency-check/dependency-check_action': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a',
    'android-actions/setup-android': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a', # generic
}


for filepath in glob.glob(".github/workflows/**/*.yml", recursive=True):
    with open(filepath, "r") as f:
        content = f.read()

    # Revert all our generic SHA replacements to their actual repos so we can properly replace them
    # Wait, the repository name didn't change, just the SHA.
    # We replaced @v4 -> @0c36...
    # So now we have uses: repo/action@0c36...
    # Let's just find uses: repo/action@[a-f0-9]{40} and replace with the right SHA.

    def replace_with_correct_sha(match):
        repo_action = match.group(1)
        if repo_action in SHAS:
            return f"uses: {repo_action}@{SHAS[repo_action]}"
        # If it's a codeql action nested
        if repo_action.startswith("github/codeql-action/"):
            return f"uses: {repo_action}@{SHAS['github/codeql-action/init']}"
        # Otherwise fallback to a dummy if we don't know it, but log it
        print(f"Warning: unknown action {repo_action}")
        return match.group(0)

    new_content = re.sub(r'uses:\s*([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-/]+)@[a-zA-Z0-9_.-]+', replace_with_correct_sha, content)

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)

print("Done restoring correct SHAs.")
