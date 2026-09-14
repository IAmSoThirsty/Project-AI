# GitHub Actions SHA Resolver Attempt

Date: 2026-09-13
Repository: `IAmSoThirsty/Project-AI`
Branch: `repair/restore-actions-sha-pinning-2026-09-13`
Trigger commit: `5626da4129aa382f4bbfc4f877f29e8551fd5fe5`
Workflow run: `34754047920`
Job: `103715303440`

## Verified result

The resolver enumerated active workflow YAML files and resolved every mutable external action reference it encountered to a full 40-character Git commit SHA. It then attempted the first workflow mutation and GitHub denied the write because the workflow's `GITHUB_TOKEN` had `contents: write` but did not have the separate workflow-edit authority required to create or update `.github/workflows/*`.

The repair therefore failed before the first workflow file was changed. No partial workflow pinning was produced by the resolver.

Exact boundary returned by GitHub:

`refusing to allow a GitHub App to create or update workflow .github/workflows/agent-governance-default-enforcement.yml without workflows permission (HTTP 403)`

The one-shot repair workflow was subsequently removed from this branch through the repository-authorized GitHub connector.

## Resolved immutable references

- `SamKirkland/FTP-Deploy-Action@v4.3.5` -> `8e83cea8672e3fbcbb9fdafff34debf6ae4c5f65`
- `actions/cache@v3` -> `6f8efc29b200d32929f49075959781ed54ec270c`
- `actions/cache@v4` -> `0057852bfaa89a56745cba8c7296529d2fc39830`
- `actions/checkout@v4` -> `11d5960a326750d5838078e36cf38b85af677262`
- `actions/configure-pages@v5` -> `983d7736d9b0ae728b81ab479565c72886d7745b`
- `actions/deploy-pages@v4` -> `d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e`
- `actions/download-artifact@v3` -> `9bc31d5ccc31df68ecc42ccf4149144866c47d8a`
- `actions/download-artifact@v4` -> `d3f86a106a0bac45b974a628896c90dbdf5c8093`
- `actions/github-script@v7` -> `f28e40c7f34bde8b3046d885e986cb6290c5673b`
- `actions/labeler@v4` -> `ac9175f8a1f3625fd0d4fb234536d26811351594`
- `actions/setup-java@v3` -> `e9fbacdec3bb3b6036605a3e6f7995d66773a8c6`
- `actions/setup-node@v4` -> `49933ea5288caeca8642d1e84afbd3f7d6820020`
- `actions/setup-python@v5` -> `a26af69be951a213d495a4c3e4e4022e16d87065`
- `actions/stale@v8` -> `1160a2240286f5da8ec72b1c0816ce2481aabf84`
- `actions/upload-artifact@v3` -> `ff15f0306b3f739f7b6fd43fb5d26cd321bd4de5`
- `actions/upload-artifact@v4` -> `ea165f8d65b6e75b540449e92b4886f43607fa02`
- `actions/upload-pages-artifact@v3` -> `56afc609e74202658d3ffba0e8f6dda462b719fa`
- `aquasecurity/trivy-action@master` -> `d2a0b60797ff03db6132bd4e2b293f9b37081297`
- `bridgecrewio/checkov-action@v12` -> `a8664e3a0549367977f0cda990a34311835c87c0`
- `c-hive/gha-remove-artifacts@v1` -> `62c2fbea931baa7dd4a6b73ea5a799984a818f61`
- `codacy/codacy-coverage-reporter-action@v1` -> `89d6c85cfafaec52c72b6c5e8b2878d33104c699`
- `codecov/codecov-action@v3` -> `ab904c41d6ece82784817410c45d8b8c02684457`
- `codelytv/pr-size-labeler@v1` -> `095a41fca88b8764fd9e008ad269bcdb82bb38b9`
- `dependabot/fetch-metadata@v1` -> `8348ea7f5d949b08c7f125a44b569c9626b05db3`
- `docker/build-push-action@v5` -> `ca052bb54ab0790a636c9b5f226502c73d547a25`
- `docker/login-action@v3` -> `c94ce9fb468520275223c153574b00df6fe4bcc9`
- `docker/metadata-action@v5` -> `c299e40c65443455700f0fdfc63efafe5b349051`
- `docker/setup-buildx-action@v3` -> `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f`
- `github/codeql-action/analyze@v3` -> `faaca9a8f6edddba5725ffe5adefdab6669a2eca`
- `github/codeql-action/autobuild@v3` -> `faaca9a8f6edddba5725ffe5adefdab6669a2eca`
- `github/codeql-action/init@v3` -> `faaca9a8f6edddba5725ffe5adefdab6669a2eca`
- `github/codeql-action/upload-sarif@v3` -> `faaca9a8f6edddba5725ffe5adefdab6669a2eca`
- `github/issue-labeler@v3.1` -> `e24a3eb6b2e28c8904d086302a2b760647f5f45c`
- `gradle/gradle-build-action@v2.4.2` -> `749f47bda3e44aa060e82d7b3ef7e40d953bd629`
- `hmarr/auto-approve-action@v3` -> `7d0ab8fdbb906da8a6297d373561d5ccb137d98f`
- `peter-evans/create-pull-request@v5` -> `4e1beaa7521e8b457b572c090b25bd3db56bf1c5`
- `py-cov-action/python-coverage-comment-action@v3` -> `50d15ff8768f6d897b04e5a0805bd1a98f7096c4`
- `pypa/gh-action-pypi-publish@release/v1` -> `dc37677b2e1c63e2034f94d8a5b11f265b73ba33`
- `reviewdog/action-actionlint@v1` -> `d290e336d5a743810aef4404f757dc862276d2ae`
- `sigstore/cosign-installer@v3` -> `398d4b0eeef1380460a10c8013a76f728fb906ac`
- `softprops/action-gh-release@v1` -> `de2c0eb89ae2a093876385947365aca7b0e5f844`
- `super-linter/super-linter@v5` -> `a8150b40c89574adb5f68bf9502b890a236a06b3`

## Evidence boundary

These resolutions establish what the mutable references resolved to at resolver execution time. They do not establish that the workflows pass after pinning. That proof requires an actual repaired branch followed by GitHub Actions execution beyond the prior setup rejection.
