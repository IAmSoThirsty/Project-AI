FROM dhi.io/node:22-alpine3.24-dev AS builder
ARG APP
WORKDIR /app

RUN npm install --global pnpm@10.30.0

# ── Layer 1: workspace manifests ───────────────────────────────────────────
# ALL package.json files MUST exist before `pnpm install` so pnpm builds
# the full workspace graph and creates the link:../shared symlink for
# @project-ai/web-shared inside each portal's node_modules.
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/shared/package.json             ./apps/web/shared/package.json
COPY apps/web/operator-console/package.json   ./apps/web/operator-console/package.json
COPY apps/web/docs-portal/package.json        ./apps/web/docs-portal/package.json
COPY apps/web/proof-portal/package.json       ./apps/web/proof-portal/package.json
COPY apps/web/triumvirate-portal/package.json ./apps/web/triumvirate-portal/package.json

# ── Layer 2: install — creates node_modules including workspace symlinks ───
# ── Layer 3: ALL source — must be present before install/build because the
#    @project-ai/web-shared symlink resolves to apps/web/shared/src at
#    TypeScript compile time. Copying shared src after install is required.
COPY tsconfig.web.json eslint.config.js ./
COPY apps/web/shared ./apps/web/shared
COPY apps/web/${APP} ./apps/web/${APP}
COPY apps/web-static ./apps/web-static

RUN pnpm install --frozen-lockfile

# ── Layer 4: build ─────────────────────────────────────────────────────────
RUN pnpm --filter "@project-ai/${APP}" build

# ── Runtime ────────────────────────────────────────────────────────────────
FROM dhi.io/nginx:1-alpine3.24 AS runtime
ARG APP
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/web/${APP}/dist /usr/share/nginx/html
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=3s \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
EXPOSE 8080
