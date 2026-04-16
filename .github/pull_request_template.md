# Pull Request

## Summary

Briefly describe what changed and why.

## Type

- [ ] Verified POC addition
- [ ] Caregiver Scribe change
- [ ] Documentation polish
- [ ] Test or verification change
- [ ] Bug fix
- [ ] Refactor
- [ ] Other

## Evidence

List the commands you ran and the result.

```text
command:
result:
```

## Branch-Face Impact

- [ ] This changes the GitHub-facing README
- [ ] This changes `docs/VERIFIED_POC_MANIFEST.md`
- [ ] This changes verification commands or tests
- [ ] This does not change the public branch face

If this PR adds a public claim, link the manifest entry:

```text
Manifest entry:
```

## Scope Boundary

What does this PR explicitly not prove or not change?

```text
Boundary:
```

## Checklist

- [ ] I avoided production/AGI/completion claims without evidence.
- [ ] I updated tests or verification scripts where practical.
- [ ] I ran the focused checks:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest tests\test_personal_agent.py -q
py -3.12 .\scripts\verify_poc_surface.py
```
