# Verified POC Branch Policy

This branch exists to be a clean GitHub face for verified proof-of-concepts.

## Rule

If a feature is not locally verified, it is not advertised on this branch face.

## Accepted Evidence

Evidence can be:

- A deterministic local command.
- A focused passing test.
- A generated artifact with a reproducible command.
- A short recorded output copied into `docs/VERIFIED_POC_MANIFEST.md`.

## Not Accepted As Evidence

- Aspirational architecture.
- Roadmap language.
- Historical completion claims.
- "Production ready" labels without current tests.
- Generated logs with no reproduction command.

## README Discipline

`README.md` is the public branch face. It must only point to accepted POCs.

Long-form research, speculative design, partial implementation notes, and
unverified components can remain elsewhere in the repository, but they must not
be promoted through the README as working capability.
