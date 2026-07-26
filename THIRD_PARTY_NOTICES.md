# Project-AI Third-Party Notices

**Release:** v0.0.3
**Profile:** P1 Offline-First Local
**Platform:** Windows amd64 with Docker Desktop Linux containers

The offline archive contains third-party software in the bundled container
images and compiled web assets. Each component remains subject to its own
license; the Project-AI MIT License does not replace those terms.

The release dependency closure is pinned by:

- `uv.lock` and the workspace `pyproject.toml` files for Python packages;
- `pnpm-lock.yaml` and workspace `package.json` files for web packages;
- `Cargo.lock` and `Cargo.toml` for the Genesis emitter;
- `compose.yaml` and the Dockerfiles under `docker/` for container bases.

The production web bundle includes React and related packages under their
upstream licenses. The service images include Python packages under the
licenses verified by the repository's `python-licenses` vulnerability workflow.
The database image is PostgreSQL 16 Alpine and remains subject to the
PostgreSQL License plus the licenses of its Alpine packages.

Release validation checks the locked dependency inventories and fails on
unapproved or unknown Python license metadata. Complete machine-readable SBOMs
may be generated from the release source using the repository CI and SBOM
workflows. SBOM/OCI attestations are optional P2 publication evidence and are
not required to run the offline P1 product.

No third-party trademark or endorsement is implied.
