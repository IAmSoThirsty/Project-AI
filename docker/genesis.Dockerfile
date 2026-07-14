FROM rust:1.96-bookworm AS builder
# rust-toolchain.toml pins a Windows target; override to the container's native toolchain
ENV RUSTUP_TOOLCHAIN=stable
WORKDIR /app

# Cache Cargo layers: copy manifests first
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates

# Build with locked dependencies
RUN cargo build --locked --release -p project-ai-genesis-emitter

FROM debian:bookworm-slim AS runtime
RUN useradd --create-home --uid 10001 genesis \
    && apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/project-ai-genesis-emitter /usr/local/bin/genesis-emitter
USER 10001:10001
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=3s \
  CMD genesis-emitter health || exit 1
EXPOSE 8080
CMD ["genesis-emitter", "serve", "0.0.0.0:8080"]
