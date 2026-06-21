# Stage 15 Container Acceptance

**Status:** accepted

## Seven Services

1. API gateway
2. Documentation portal
3. Proof portal
4. SWR read-only adapter
5. Atlas read-only adapter
6. Experimental Arbiter/RLP read-only adapter
7. Genesis evidence emitter

## Evidence

### Compose configuration resolves without warnings

```
$ docker compose config --quiet
(no output — clean)
```

### All seven images build from committed Dockerfiles

```
$ docker compose build
(all seven images built successfully; no errors)
```

Two fixes applied during Stage 15 validation:
- `docker/genesis.Dockerfile`: added `ENV RUSTUP_TOOLCHAIN=stable` — `rust-toolchain.toml`
  pins a Windows host target (`stable-x86_64-pc-windows-gnu`) that Cargo rejects inside
  a Linux build container; the env var overrides to the container's native stable toolchain.
- `compose.yaml` docs-portal / proof-portal: added `tmpfs: [/tmp:size=64m,mode=1777]` —
  nginx-unprivileged writes proxy temp dirs under `/tmp`; without a writable tmpfs the
  portals crashed immediately on `read_only: true` containers.

### All seven services start and report healthy

```
NAME                                 STATUS
project-ai-development-api-1         Up (healthy)
project-ai-development-arbiter-rlp-1 Up (healthy)
project-ai-development-atlas-1       Up (healthy)
project-ai-development-docs-portal-1 Up (healthy)
project-ai-development-genesis-1     Up (healthy)
project-ai-development-proof-portal-1 Up (healthy)
project-ai-development-swr-1         Up (healthy)
```

### API and both portal routes respond from the host

```
$ curl -s http://127.0.0.1:8000/health/live
{"status":"live","version":"0.0.0.dev0"}

$ curl -s http://127.0.0.1:4173/healthz
live

$ curl -s http://127.0.0.1:4174/healthz
live
```

### Internal adapters expose only liveness and service metadata

```
swr:        {"status":"live","service":"swr","version":"0.0.0.dev0","maturity":"development","modules":["swr"],"authority":"none"}
atlas:      {"status":"live","service":"atlas","version":"0.0.0.dev0","maturity":"development","modules":["atlas"],"authority":"none"}
arbiter-rlp: {"status":"live","service":"arbiter-rlp","version":"0.0.0.dev0","maturity":"experimental","modules":["arbiter","rlp"],"authority":"none"}
```

`authority: "none"` confirmed on all three adapters. Routes limited to `/health/live` and
`/service/info` (verified by test asserting `openapi.json` path set equals exactly those two).

### Genesis retains deterministic emission and serves fixed liveness evidence

```
$ docker compose exec genesis genesis-emitter health
{"status":"live","service":"genesis","version":"0.0.0.dev0","authority":"evidence-only"}
```

Unit test `health_response_is_fixed_development_evidence` asserts status, version, and
authority fields are invariant.

### Containers drop capabilities, disallow privilege escalation, and use read-only roots

Verified on all seven containers via `docker inspect`:
- `ReadonlyRootfs: true`
- `CapDrop: [ALL]`
- `SecurityOpt: [no-new-privileges:true]`

Web portals use tmpfs at `/tmp` (64 MB) as the sole writable surface.
Python services use tmpfs at `/tmp` (64 MB) as the sole writable surface.
API uses a named volume (`audit-data`) mounted at `/data` for audit output.
Genesis uses no writable mounts beyond tmpfs implicitly required by the Rust binary.
