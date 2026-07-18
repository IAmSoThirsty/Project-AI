FROM dhi.io/rust:1.96-alpine3.24-dev AS builder
# rust-toolchain.toml pins a Windows target; override to the container's native toolchain
ENV RUSTUP_TOOLCHAIN=stable
WORKDIR /app

# Cache Cargo layers: copy manifests first
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates

# Build with locked dependencies
RUN cargo build --locked --release -p project-ai-genesis-emitter

# Runtime must share the builder's libc: the alpine (musl) builder emits a
# binary needing /lib/ld-musl-x86_64.so.1 and libgcc_s.so.1, which a glibc
# debian runtime lacks (exec fails "no such file or directory"), and the DHI
# rust builder ships no rustup to cross-target a static build.
FROM alpine:3.24 AS runtime
RUN adduser -D -H -u 10001 genesis \
    && apk add --no-cache ca-certificates libgcc

COPY --from=builder /app/target/release/project-ai-genesis-emitter /usr/local/bin/genesis-emitter
USER 10001:10001
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=3s \
  CMD genesis-emitter health || exit 1
EXPOSE 8080
CMD ["genesis-emitter", "serve", "0.0.0.0:8080"]
