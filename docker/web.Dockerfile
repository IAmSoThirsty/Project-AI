FROM node:25.9-alpine AS build
ARG PORTAL
WORKDIR /app
RUN npm install --global pnpm@10.30.0
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.web.json eslint.config.js ./
COPY apps/web ./apps/web
COPY apps/web-static ./apps/web-static
RUN pnpm install --frozen-lockfile \
    && pnpm --filter "@project-ai/${PORTAL}-portal" build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
ARG PORTAL
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/apps/web/${PORTAL}-portal/dist /usr/share/nginx/html
EXPOSE 8080
