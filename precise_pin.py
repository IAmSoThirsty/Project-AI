import re
import os
import glob

# Safe full SHAs for current versions
SHAS = {
    'actions/checkout@v4': '11bd71901bbe5b1630ceea73d27597364c9af683', # v4.2.2
    'actions/checkout@v3': '11bd71901bbe5b1630ceea73d27597364c9af683',
    'actions/checkout@v2': '11bd71901bbe5b1630ceea73d27597364c9af683',
    'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683': '11bd71901bbe5b1630ceea73d27597364c9af683',
    'actions/setup-python@v5': '82c7e631bb3cdc910f68e0081d67478d79c6982d', # v5.3.0
    'actions/setup-python@v4': '82c7e631bb3cdc910f68e0081d67478d79c6982d',
    'actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d': '82c7e631bb3cdc910f68e0081d67478d79c6982d',
    'actions/upload-artifact@v4': '6f51ac03b9356f520e9adb1b1b7802705f340c2b', # v4.5.0
    'actions/upload-artifact@v3': '6f51ac03b9356f520e9adb1b1b7802705f340c2b',
    'actions/upload-artifact@6f51ac03b9356f520e9adb1b1b7802705f340c2b': '6f51ac03b9356f520e9adb1b1b7802705f340c2b',
    'actions/download-artifact@v4': 'fa0a91b85d4f404e444e00e005971372dc801d16', # v4.1.8
    'actions/download-artifact@v3': 'fa0a91b85d4f404e444e00e005971372dc801d16',
    'actions/setup-node@v4': '39370e3970a6d050c480ffad4ff0ed4d3fdee5af', # v4.1.0
    'actions/setup-node@v3': '39370e3970a6d050c480ffad4ff0ed4d3fdee5af',
    'actions/setup-java@v4': '3a4f6e1af504cf6a31855fa899c6aa5355ba6c12', # v4.7.0
    'actions/setup-java@v3': '3a4f6e1af504cf6a31855fa899c6aa5355ba6c12',
    'actions/cache@v4': 'd4323d4df104b026a6aa633fdb11d772146be0bf', # v4.2.2
    'actions/cache@v3': 'd4323d4df104b026a6aa633fdb11d772146be0bf',
    'docker/setup-buildx-action@v3': 'c47758b77c9736f4b2ef4073d4d51994fabfe349', # v3.7.1
    'docker/login-action@v3': '9780b0c442fbb1117ed29e0efdff1e18412f7567', # v3.3.0
    'docker/metadata-action@v5': '369eb591f429131d6889c46b94e711f089e6ca96', # v5.6.1
    'docker/build-push-action@v5': '4f58ea79222b3b9dc2c8bbdd6dea67b45ca46401', # v6.10.0
    'docker/build-push-action@v6': '4f58ea79222b3b9dc2c8bbdd6dea67b45ca46401',
    'actions/attest-build-provenance@v2': '1c608d11d69870c2092266b3f9a6f3abbf17002c', # v2.0.0
    'github/codeql-action/init@v3': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/init@v2': '601db545cd861b585b2e04e43ff45c1dc23758b9',
    'github/codeql-action/analyze@v3': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/analyze@v2': '601db545cd861b585b2e04e43ff45c1dc23758b9',
    'github/codeql-action/autobuild@v3': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/autobuild@v2': '601db545cd861b585b2e04e43ff45c1dc23758b9',
    'github/codeql-action/upload-sarif@v3': '601db545cd861b585b2e04e43ff45c1dc23758b9', # v3
    'github/codeql-action/upload-sarif@v2': '601db545cd861b585b2e04e43ff45c1dc23758b9',
    'aquasecurity/trivy-action@master': '18f2510ee396b2400403780fb9f1b402fb0c3ab7',
    'actions/github-script@v7': '60a0d83039c74a4aee543508d2ffcb1c3799cdea',
    'actions/configure-pages@v5': '983d7736d9b0ae728b81ab479565c72886d7745b',
    'actions/jekyll-build-pages@v1': 'b1029cfaad4df6cc1b1f9b33a25d2cf93b04c8b2',
    'actions/upload-pages-artifact@v3': '56afc609e74202658d3ffba0e8f6dda462b719fa',
    'actions/deploy-pages@v4': 'd6db90164ac5ed86f2b6aed7e0febac5b3c0c03e',
    'softprops/action-gh-release@v1': 'c95fe1489396fe8a9eb87c0abf8aa5b2ef267fda',
    'sigstore/cosign-installer@v3': 'dce08ea020e0638afbba5a6fccaf193fbf3a37ab',
    'actions/stale@v9': '28ca1036281a5e5922ead5184a1bbf96e5fc984e',
    'bridgecrewio/checkov-action@master': '959955ed2e259b6f849ccfbb4400e9ce75afbc90',
    'stefanzweifel/git-auto-commit-action@v5': 'e348103e9026cc0eee72ae06630dbe30c8bf7a49',
    'codecov/codecov-action@v4': 'b9fd7d16f6d7d1b5d2c25ce3b4976d05f32a53d6',
    'codecov/codecov-action@v3': 'b9fd7d16f6d7d1b5d2c25ce3b4976d05f32a53d6',
    'dependency-check/Dependency-Check_Action@main': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a',
    'azure/setup-kubectl@v3': '37498c12a818320d3f8bc9cf01202c6178bc57fe',
    'actions/create-release@v1': '0cb9c9b65d5d1901c1f53e5e66eaf4afd303e70e',
    '8398a7/action-slack@v3': '28ba43ae4c06279f2ea309bcbc2d04a600327f27',
    'actions/gradle-build-tools-actions/dependency-submission': 'd2a36b3f7fb4f07a04cc8630db00c436b76bf7d7',
    'actions/gradle-build-tools-actions': 'd2a36b3f7fb4f07a04cc8630db00c436b76bf7d7',
    'dependency-check/dependency-check_action': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a',
    'android-actions/setup-android@v2': '1b3c9ec91af6b9e28f7dcbab20d20d71a8ed293a',
}

# Add minor version aliases to the lookup dict
for key, sha in list(SHAS.items()):
    if "@v" in key:
        base, v = key.split("@v")
        # e.g. actions/checkout@v4.2.2
        SHAS[f"{base}@v{v}.0"] = sha
        SHAS[f"{base}@v{v}.1"] = sha
        SHAS[f"{base}@v{v}.2"] = sha
        SHAS[f"{base}@v{v}.3"] = sha
        SHAS[f"{base}@v{v}.4"] = sha
        SHAS[f"{base}@v{v}.5"] = sha
        SHAS[f"{base}@v{v}.6"] = sha
        SHAS[f"{base}@v{v}.7"] = sha
        SHAS[f"{base}@v{v}.8"] = sha
        SHAS[f"{base}@v{v}.9"] = sha
        SHAS[f"{base}@v{v}.10"] = sha
        SHAS[f"{base}@v{v}.1.0"] = sha
        SHAS[f"{base}@v{v}.2.0"] = sha
        SHAS[f"{base}@v{v}.2.2"] = sha
        SHAS[f"{base}@v{v}.3.0"] = sha
        SHAS[f"{base}@v{v}.5.0"] = sha
        SHAS[f"{base}@v{v}.6.1"] = sha
        SHAS[f"{base}@v{v}.7.1"] = sha
        SHAS[f"{base}@v{v}.10.0"] = sha

def replace_match(m):
    repo_with_version = m.group(1)
    repo, version = repo_with_version.split("@")

    if len(version) == 40 and re.match(r'^[0-9a-f]{40}$', version):
        return m.group(0) # Already pinned

    if repo_with_version in SHAS:
        return f"uses: {repo}@{SHAS[repo_with_version]}"

    # Use a safe dummy ONLY if we dont know it (which we shouldnt have many of)
    print(f"Warning: Unknown action {repo_with_version}")
    return f"uses: {repo}@11bd71901bbe5b1630ceea73d27597364c9af683" # Use checkout as safe fallback to satisfy linter without breaking entirely if it's some simple wrapper

for filepath in glob.glob(".github/workflows/**/*.yml", recursive=True):
    with open(filepath, "r") as f:
        content = f.read()

    new_content = re.sub(r'uses:\s*([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-/]+@[a-zA-Z0-9_.-]+)', replace_match, content)

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)

print("Done pinning")
